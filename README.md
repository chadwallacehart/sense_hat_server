# Raspberry Pi Sense Hat Web and Socket Server

Python-based web and socket.IO server for the Raspberry Pi Sense Hat. 
Servers a web-page with a updated graphs of the data using [chart.js](https://www.chartjs.org/).

## Requirements
 * A Sense Hat or the emulator
 * [Setup and calibrate](https://www.raspberrypi.org/documentation/hardware/sense-hat/) the Sense Hat
 
 ## Usage
 
 ### Installation
 * `git clone https://github.com/chadwallacehart/sense_hat_server.git`
 * `cd sense_hat_server`
 * `pip3 install flask flask_socketio eventlet socketIO_client`

### Start the server
 * `python3 server.py`
 
 
### Web-client

Point your browser to `http://raspberrypi.local:5000` and watch the graph.
Replace 'raspberrypi.local' with your Pi's hostname or IP address or use 'localhost'
if you are using the Pi's built-in browser.

### REST API

These all return a JSON object.

Command | Parameters | Example | Notes
------- | ---------- | ------- | -----
orientation | none | `http://pisensehat.local:5000/orientation` | 
compass | none | `http://pisensehat.local:5000/compass` | 
gyroscope | none | `http://pisensehat.local:5000/gyroscope` | 
accelerometer | none | `http://pisensehat.local:5000/accelerometer` | 
humidity | none | `http://pisensehat.local:5000/humidity` | 
temp or temperature | `f` : use fahrenheit | `http://pisensehat.local:5000/temp?f=True` | include any value with parameter to show the temp in Fahrenheit
pressure | none | `http://pisensehat.local:5000/pressure` | 
color | `r`, `g`, `b` :  color values `0-255` | `http://pisensehat.local:5000/color?r=200&g=100` | Sets or clears the LED matrix. Leave blank or set all values to 0 to clear the display
message | `text`: what message to display; r`, `g`, `b` : same as above; `speed`: speed (default 0.1); `n`: # of times to repeat | `http://pisensehat.local:5000/message?text=Hello%20world!&speed=0.05&b=150&n=3` | Scrolls a message on the LED matrix. Color will default to white if no color params provided
low_light | none | `http://pisensehat.local:5000/low_light` | turns on/off low light mode on the LED matrix

### Socket IO

`color`, `message`, and `low_light` commands available from above.

Example code:
```python
        data = {
            'text': 'Hello world!',
            'speed': 0.05,
            'r': 200,
            'g': 100,
            'b': 0,
            'n': 3
        }
        socketIO.emit('command', {'message': data})
```

Once the socket client is connected, IMU (magnometer, compass, acceleratometer, gyro) and environment sensor data is 
automatically broadcasted at regular intervals as specified by `IMU_UPDATE_INTERVAL`

See `client.py` for full usage examples from a Python client.
The `socket.html` file shows how the data is read to a web page.


## Notes & To Do

* This can be expanded to work with more commands
* Command line arguments to set options
* By default, only the orientation set turned on