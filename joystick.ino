class Joystick{
public:
    Joystick(const uint8_t& axisX, const uint8_t& axisY, const uint8_t& sw):
        axisX(axisX), axisY(axisY), sw(sw)
    {
        ;
    }

    uint16_t get_axisX() { return analogRead(axisX); }
    uint16_t get_axisY() { return analogRead(axisY); }
    bool get_sw() { return analogRead(sw) == 0; }
    String get_string()
    {
        String str = "{\"x\":" + String(get_axisX(),DEC) + ",\"y\":" + String(get_axisY(),DEC) + ",\"sw\":" + String(get_sw(),DEC) + "}";
        return str;
    }

private:
    const uint8_t axisX;
    const uint8_t axisY;
    const uint8_t sw;
};

Joystick joystick(A0,A1,A2);

// the setup routine runs once when you press reset:
void setup() {
    // initialize serial communication at 9600 bits per second:
    Serial.begin(115200);
}

// the loop routine runs over and over again forever:
void loop() {
    String str = joystick.get_string();
    Serial.println(str);
    delay(50);        // delay in between reads for stability
}
