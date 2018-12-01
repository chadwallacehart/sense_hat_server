from threading import Lock, Event

from flask import Flask, Response
from flask_socketio import SocketIO, emit
from imu_data import get_imu


app = Flask(__name__)
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


thread_lock = Lock()


def background_thread(run_event):
    print("starting background thread")
    t = 0

    try:
        while run_event.is_set():
            t += 1
            socketio.sleep(0.5)
            data = get_imu(orientation=True)
            if data is not None:
                socketio.emit('imu', {'data': data})
                print("Sent message ", data)
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


@socketio.on('start')
def test_message(message):
    print('start: ', message)


@socketio.on('connect')
def test_connect():
    print("socket connected")
    get_data()


@socketio.on('disconnect')
def test_disconnect():
    global thread, run_event
    print('Client disconnected')
    run_event.clear()
    thread.join(1)
    print("thread closed")


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')