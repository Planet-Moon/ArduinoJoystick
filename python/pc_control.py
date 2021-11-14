import win32api
from serial import Serial
import json
import copy


class Input_device:
    def __init__(self,serial:Serial):
        self.serial:Serial = serial
        self.connections = []
        self._running = False

    @property
    def running(self):
        self._running = False

    def add_connection(self,function):
        self.connections.append(function)

    def run(self):
        if not self._running:
            with self.serial as ser:
                self._running = True
                while True:
                    line = ser.readline()
                    mouse_move = Mouse_move().parse_from_json(line)
                    for connection in self.connections:
                        connection(mouse_move)
                    pass


class Mouse_move:
    def __init__(self,x:int=0,y:int=0,sw:bool=False):
        self.x:int = x
        self.y:int = y
        self.sw:bool = sw

    def __str__(self):
        retval = "{\"x\":"+str(self.x)+",\"y\":"+str(self.y)+",\"sw\":"+str(self.sw)+"}"
        return retval

    @staticmethod
    def parse_from_json(input:str):
        try:
            input_parsed = json.loads(input)
            mouse_move = Mouse_move(
                input_parsed['x'],
                input_parsed['y'],
                input_parsed['sw'] != 0)
            return mouse_move
        except UnicodeDecodeError:
            return Mouse_move()
        except json.JSONDecodeError:
            return Mouse_move()


class Mouse_controller:
    def __init__(self,input_device:Input_device):
        self.input_device:Input_device = input_device
        self._running:bool = False
        self._calibrated:bool = False
        self._calibration:Mouse_move = Mouse_move()
        self._sw_old:bool = None
        self._cursor_position_old:tuple[int,int] = win32api.GetCursorPos()
        self.input_device.add_connection(self.update)
        pass

    @property
    def calibrated(self):
        return self._calibrated

    @property
    def running(self):
        return self._running

    def run(self):
        if not self._running:
            self.input_device.run()
            self._running = True

    def diff_to_calibration(self,mouse_move:Mouse_move) -> Mouse_move:
        retval = Mouse_move()
        retval.x = mouse_move.x - self._calibration.x
        retval.y = mouse_move.y - self._calibration.y
        return retval

    def update(self, mouse_move:Mouse_move):
        if not self._calibrated:
            self._calibration = copy.copy(mouse_move)
            self._calibrated = True
            print("calibration: " + str(self._calibration))
        else:
            if mouse_move.sw == True and self._sw_old == False:
                # left mouse down
                win32api.mouse_event(int("8002",16),
                    self._cursor_position_old[0],
                    self._cursor_position_old[1],
                    0,0)
            elif mouse_move.sw == False and self._sw_old == True:
                # left mouse up
                win32api.mouse_event(int("8004",16),
                    self._cursor_position_old[0],
                    self._cursor_position_old[1],
                    0,0)
            else:
                diff_move = self.diff_to_calibration(mouse_move)
                self._cursor_position_old = self.move(self._cursor_position_old, diff_move.x, diff_move.y)
            self._sw_old = mouse_move.sw

    @staticmethod
    def move(last_position:tuple[int,int],x:int,y:int) -> tuple[int,int]:
        if x < 5 and x > -5:
            x = 0
        if y < 5 and y > -5:
            y = 0
        if x == 0 and y == 0:
            return last_position
        else:
            # print("x: "+str(x)+", y: "+str(y))
            x = int(x / 15)
            y = int(y / 15)
            add_value = (y*-1,x)
            x, y = y*-1,x
            new_position = (last_position[0]+x,last_position[1]+y)
            win32api.SetCursorPos(new_position) # swap x and y and invert x
            return new_position

    @staticmethod
    def update_cursor(command:Mouse_move):
        pass

    def calibrate(self,input:Mouse_move):
        self.calibrate_move = input


def main():
    ser = Serial(port='COM3',baudrate=115200, timeout=1)
    input_device = Input_device(ser)
    mouse_controller = Mouse_controller(input_device)
    mouse_controller.run()



if __name__ == '__main__':
    main()
