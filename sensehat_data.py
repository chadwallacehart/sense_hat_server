# from sense_hat import SenseHat
from sense_hat import SenseHat

sense = SenseHat()

sense.clear()

def get_imu(orientation=True, compass=False, gyroscope=False, accelerometer=False):
    data = {}
    if orientation: data["orientation"] = sense.get_orientation()
    if compass: data["compass"] = 360 - sense.get_compass()
    if gyroscope: data["gyroscope"] = sense.get_gyroscope()
    if accelerometer: data["accelerometer"] = sense.get_accelerometer()
    return data


def get_humidity():
    return sense.humidity


def get_temperature(fahrenheit=False):
    if fahrenheit:
        return 9.0/5.0 * sense.temp + 32
    else:
        return sense.temp


def get_pressure():
    return sense.pressure


# ToDo: get LED status
# ToDo: get joystick