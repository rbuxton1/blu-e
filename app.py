from xgolib import XGO 
from flask import Flask, Response, render_template
from flask import request
import random
import string 
from flask_socketio import SocketIO
import sys
import cv2
from picamera2 import Picamera2

# Global variables 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'

# Using picamera2 avoids the issues with openCV and the new libcamera stack.
picam2 = Picamera2()
config = picam2.create_preview_configuration()
picam2.configure(config)
picam2.start()

io = SocketIO(app, cors_allowed_origins="*")
state = {
    "controled": False,
    "access_key": '',
    "cmd": ''
}
error_no_key = "You must provide a valid access key!"
dog = None 

if len(sys.argv) >= 2 and sys.argv[1] == 'dog':
    # If the dog parameter was provided then initialize dog 
    dog = XGO(port='/dev/serial0',version="xgolite")
    fm=dog.read_firmware()
    if fm[0]=='M':
        print('XGO-MINI')
        dog = XGO(port='/dev/ttyAMA0',version="xgomini")
        dog_type='M'
    else:
        print('XGO-LITE')
        dog_type='L'
    dog.reset()
    print('Connected to XGO. Battery: ', dog.read_battery())

# Global functions 

def check_auth(key):
    if state['controled']:
        if key == state['access_key']:
            return True
    return False

# HTTP Routes 

@app.route('/rc')
def rc():
    return render_template('control.html')

@app.route('/control', methods=['GET', 'POST'])
def control():
    if request.method == 'POST':
        if state['controled'] == True:
            return {
                "error": "Blu-E is currently being controlled. Please wait."
            }
        else:
            key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            state['controled'] = True
            state['access_key'] = key 
            return state
    else: 
        return { "controled": state['controled'] }
    
@app.route('/release', methods=['POST'])
def release():
    data = request.json
    if check_auth(data.get('key')):
        state['controled'] = False
        state['access_key'] = ''
        return state
    else:
        return { "error": error_no_key }

# Helper function to generate video from cv2 video capture 
def gen(video):
    while True:
        frame = picam2.capture_array()
        encode_success, jpeg = cv2.imencode('.jpg', frame)

        img = jpeg.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')

@app.route('/video')
def video_feed():
    return Response(gen(picam2),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/action', methods=['POST'])
def action():
    data = request.json
    if check_auth(data.get('key')):
        id = data.get('id')
        try:
            dog.action(id)
        except Exception as err:
            return { "ok": False, "error": err }
        return { "ok": True }
    else:
        return { "error": error_no_key }

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    print(data)
    if check_auth(data.get('key')):
        dir = data.get('direction')
        step = data.get('step')
        try:
            dog.move(dir, step)
        except Exception as err:
            return { "ok": False, "error": str(err) }
        return { "ok": True }
    else:
        return { "error": error_no_key }
    
@app.route('/turn', methods=['POST'])
def turn():
    data = request.json
    if check_auth(data.get('key')):
        step = data.get('step')
        try:
            dog.turn(step)
        except Exception as err:
            return { "ok": False, "error": str(err) }
        return { "ok": True }
    else: 
        return { "error": error_no_key }

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    if check_auth(data.get('key')):
        dir = data.get('direction')
        step = data.get('step')
        try:
            dog.translation(dir, step)
        except Exception as err:
            return { "ok": False, "error": err }
        return { "ok": True }
    else: 
        return { "error": error_no_key }
    
@app.route('/attitude', methods=['POST'])
def attitude():
    data = request.json
    if check_auth(data.get('key')):
        dir = data.get('direction')
        step = data.get('step')
        try:
            dog.attitude(dir, step)
        except Exception as err:
            return { "ok": False, "error": err }
        return { "ok": True }
    else: 
        return { "error": error_no_key }
    
@app.route('/leg', methods=['POST'])
def leg():
    data = request.json
    if check_auth(data.get('key')):
        id = data.get('id')
        x = data.get('x')
        y = data.get('y')
        z = data.get('z')
        try:
            #NOTE: This is nonstandard...
            dog.leg(id, {x, y, z})
        except Exception as err:
            return { "ok": False, "error": err }
        return { "ok": True }
    else: 
        return { "error": error_no_key }
    
@app.route('/motor', methods=['POST'])
def motor():
    data = request.json
    if check_auth(data.get('key')):
        id = data.get('id')
        step = data.get('step')
        try:
            dog.motor(id, step)
        except Exception as err:
            return { "ok": False, "error": err }
        return { "ok": True }
    else: 
        return { "error": error_no_key }
    
@io.on('connect')
def on_connect():
    print('New client connected!')

@io.on('command')
def on_command(json):
    try :
        if json['cmd'] == 'move':
            dog.move(json['direction'], json['step'])
        elif json['cmd'] == 'turn':
            dog.turn(json['step'])
        elif json['cmd'] == 'attitude':
            dog.attitude(json['direction'], json['step'])
    except Exception as err:
        print(err)

# Main functions 
if __name__ == '__main__':
    print(sys.argv)
    app.run(host='0.0.0.0', port=5000)
    io.run(app)