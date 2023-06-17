from xgolib import XGO 
from flask import Flask, Response 
from flask import request
import random
import string 
from flask_socketio import SocketIO
import sys
import cv2

# Global variables 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
video = cv2.VideoCapture(0)
io = SocketIO(app, cors_allowed_origins="*")
state = {
    "controled": False,
    "access_key": '',
    "action": ''
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
        success, image = video.read()
        frame_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        frame_gray = cv2.equalizeHist(frame_gray)

        faces = face_cascade.detectMultiScale(frame_gray)

        for (x, y, w, h) in faces:
            center = (x + w//2, y + h//2)
            cv2.putText(image, "X: " + str(center[0]) + " Y: " + str(center[1]), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
            image = cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)

            faceROI = frame_gray[y:y+h, x:x+w]
        ret, jpeg = cv2.imencode('.jpg', image)

        frame = jpeg.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video')
def video():
    global video 
    return Response(gen(video),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
@app.route('/action', methods=['POST'])
def action():
    data = request.json
    if check_auth(data.get('key')):
        id = data.get('id')
        print('action, id', id)
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
    print('JSON ', json)

# Main functions 
if __name__ == '__main__':
    print(sys.argv)
    app.run(host='0.0.0.0', port=5000)
    io.run(app)