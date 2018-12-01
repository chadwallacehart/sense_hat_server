from socketIO_client import SocketIO, LoggingNamespace
from threading import Thread, Event
import logging
from time import sleep
logging.getLogger('socketIO-client').setLevel(logging.CRITICAL)
logging.basicConfig()

last_reading = {}
orientation = -1
compass = -1


def on_connect():
    print('socketIO connected')


def on_disconnect():
    print('socketIO disconnected')


def on_reconnect():
    print('socketIO reconnected')


def handle_sensor_data(*args):
    global last_reading
    last_reading = args[0]

    '''
    if 'orientation' in data:
        last_reading.orientation = data['orientation']
    if 'compass' in data:
        last_reading.compass = data['compass']
    if 'compass' in data:
        last_reading = data['compass']
    '''

def start_socket(running):
    print("starting socketIO connection")

    with SocketIO('http://n5r8-sense.local:5000', verify=False) as socketIO:
        sleep(0.25)

        socketIO.on('connect', on_connect)
        socketIO.on('disconnect', on_disconnect)
        socketIO.on('reconnect', on_reconnect)

        socketIO.on('imu', handle_sensor_data)

        socketIO.emit('log', {'message':'Python client connected'})
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
    t.join()
    print("socket.io thread closed")


# return an average over a given number of readings
def avg_heading(num_readings=5):
    n = 0
    headings = []
    while n <= num_readings:
        sleep(0.2)
        this_heading = int(heading)
        if this_heading != -1:
            # print(n, ":", this_heading)
            headings.append(this_heading)
            n += 1

    avg = int(sum(headings) / float(len(headings)))
    return avg


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