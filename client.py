from socketIO_client import SocketIO, LoggingNamespace
from threading import Thread, Event
import logging
from time import sleep
logging.getLogger('socketIO-client').setLevel(logging.CRITICAL)
logging.basicConfig()

last_reading = {}
orientation = -1
compass = -1

WS_URL = 'http://localhost:5000'

def handle_sensor_data(*args):
    global last_reading
    last_reading = args[0]


def on_connect():
    print('socketIO connected')


def on_disconnect():
    print('socketIO disconnected')


def on_reconnect():
    print('socketIO reconnected')


def start_socket(running):
    print("starting socketIO connection")

    with SocketIO(WS_URL, verify=False) as socketIO:
        sleep(0.25)

        socketIO.emit('log', {'message': 'Python client connected'})

        # Test color command
        data = {'g': 255}
        socketIO.emit('command', {'color': data})
        print ("Sent color command")
        sleep(1)
        # socketIO.wait(2) # this pauses the socket
        socketIO.emit('command', {'low_light': True})
        sleep(1)


        # Test message command
        data = {
            'text': 'Hello world!',
            'speed': 0.05,
            'r': 200,
            'g': 100,
            'b': 0,
            'n': 3
        }
        socketIO.emit('command', {'message': data})
        print ("Sent message command")

        socketIO.on('connect', on_connect)
        socketIO.on('disconnect', on_disconnect)
        socketIO.on('reconnect', on_reconnect)

        socketIO.on('imu', handle_sensor_data)

        while running.is_set():
            socketIO.wait(1)


running = Event()
running.set()
t = Thread(target=start_socket, args=(running,))


# used as a module
def start():
    global t
    t.start()


def stop():
    global running, t
    running.clear()
    t.join(1)
    print("socket.io thread closed")


# used for testing
def main():
    global last_reading
    print("Hit Ctrl-C to exit.")

    try:
        t.start()

        while True:
            sleep(0.5)
            print(last_reading)
    except KeyboardInterrupt:
        print("exiting...")
        stop()


if __name__ == '__main__':
    main()