from sense_hat import SenseHat
sense = SenseHat()

sense.clear()


def get_imu(orientation=True, compass=False, gyroscope=False, accelerometer=False):
    data = {}
    if orientation: data["orientation"] = sense.get_orientation()
    if compass: data["compass"] = sense.get_compass()
    if gyroscope: data["gyroscope"] = sense.get_gyroscope()
    if accelerometer: data["acceleromater"] = sense.get_accelerometer()
    return data