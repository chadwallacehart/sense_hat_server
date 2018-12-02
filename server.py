from threading import Lock, Event

from sense_hat import SenseHat
sense = SenseHat()
sense.set_rotation(270)


from flask import Flask, Response, jsonify, request
from flask_socketio import SocketIO, emit
app = Flask(__name__)
socketio = SocketIO(app)

thread_lock = Lock()

IMU_UPDATE_INTERVAL = 0.5   # How often to provide IMU updates over the socket


# IMU sensor data
# Some of these can only be used one at a time??
def get_imu(orientation=True, compass=False, gyroscope=False, accelerometer=False):
    data = {}
    if orientation: data["orientation"] = sense.get_orientation()
    if compass: data["compass"] = 360 - sense.get_compass()
    if gyroscope: data["gyroscope"] = sense.get_gyroscope()
    if accelerometer: data["accelerometer"] = sense.get_accelerometer()
    return data


def background_thread(run_event, imu=True, enviro=False):
    print("starting background thread")
    t = 0

    try:
        while run_event.is_set():
            t += 1
            socketio.sleep(IMU_UPDATE_INTERVAL)
            if imu:
                data = get_imu(orientation=True, compass=False, gyroscope=False, accelerometer=False)
                if data is not None:
                    socketio.emit('imu', {'data': data})
                    print("Sent message ", data)

            if enviro:
                socketio.emit('temperature', {'data': temperature()})
                socketio.emit('humidity', {'data': humidity()})
                socketio.emit('pressure', {'data': pressure()})
    finally:
        run_event.clear()


def get_data():
    global thread
    global run_event
    run_event = Event()
    run_event.set()

    with thread_lock:
        thread = socketio.start_background_task(background_thread, run_event)


@app.route('/')
def index():
    return Response(open('socket.html').read(), mimetype="text/html")


@app.route('/orientation')
def orientation():
    data = get_imu(orientation=True, compass=False, gyroscope=False, accelerometer=False)
    return jsonify(data)


@app.route('/compass')
def compass():
    data = get_imu(orientation=False, compass=True, gyroscope=False, accelerometer=False)
    return jsonify(data)


@app.route('/gyroscope')
def gyroscope():
    data = get_imu(orientation=False, compass=False, gyroscope=True, accelerometer=False)
    return jsonify(data)


@app.route('/accelerometer')
def accelerometer():
    data = get_imu(orientation=False, compass=False, gyroscope=True, accelerometer=False)
    return jsonify(data)


@app.route('/humidity')
def humidity():
    return jsonify(sense.humidity)


@app.route('/temp')
@app.route('/temperature')
def temperature(fahrenheit=False):
    fahrenheit = request.args.get('f', default = False, type=bool)

    if fahrenheit:
        return jsonify(9.0/5.0 * sense.temp + 32)
    else:
        return jsonify(sense.temp)


@app.route('/pressure')
def pressure():
    return jsonify(sense.pressure)


@app.route('/clear')
@app.route('/color')
def color():

    r = request.args.get('r', default = 0, type=int)
    g = request.args.get('g', default = 0, type=int)
    b = request.args.get('b', default=0, type=int)

    sense.clear(r, g, b)
    return Response("Set color to (%s, %s, %s)" % (r,g,b) )


@app.route('/message')
def message():
    if request.args.get('text'):
        text = request.args.get('text')
    else:
        return Response("No 'text' parameter provided")

    r = request.args.get('r', default = 0, type=int)
    g = request.args.get('g', default = 0, type=int)
    b = request.args.get('b', default=0, type=int)
    # if no color params then set to white
    if r + g + b is 0:
        r = g = b = 255
    speed = request.args.get('speed', default=0.1, type=float)
    n = request.args.get('n', default=1, type=int)

    for i in range(n):
        sense.show_message(text, text_colour=[r,g,b], scroll_speed=speed)
    return Response(text)


@app.route('/low_light')
def low_light():
    sense.low_light = not sense.low_light
    return Response("Low light set to %s" % sense.low_light)

### Socket IO


@socketio.on('start')
def socket_message(message):
    print('start: ', message)


@socketio.on('connect')
def socket_connect():
    print("socket connected")
    get_data()


@socketio.on('log')
def socket_log(message):
    print(message)

@socketio.on('command')
def socket_command(command):
    print("Got message ", command)
    if 'color' in command:
        r = command['color'].get('r', 0)
        g = command['color'].get('g', 0)
        b = command['color'].get('b', 0)
        print("Set color to (%s, %s, %s)" % (r,g,b))
        sense.clear(r, g, b)

    if 'message' in command:
        text = command['message'].get('text', "*")
        r = command['message'].get('r', 255)
        g = command['message'].get('g', 255)
        b = command['message'].get('b', 255)
        # if no color params then set to white
        if r + g + b is 0:
            r = g = b = 255
        speed = command['message'].get('speed', 0.1)
        n = command['message'].get('n', 1)
        for i in range(n):
            # Note: this is blocking to the sensor data
            sense.show_message(text, text_colour=[r,g,b], scroll_speed=speed)
        print("Displayed message: %s" % text)

    if 'low_light' in command:
        sense.low_light = command['low_light']
        print("Low light set to %s" % sense.low_light)

@socketio.on('disconnect')
def test_disconnect():
    global thread, run_event
    print('Client disconnected')
    run_event.clear()
    thread.join(1)
    print("thread closed")




if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
