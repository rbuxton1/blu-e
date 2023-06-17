from xgolib import XGO 
from flask import Flask
from flask import request
import random
import string 
from flask_socketio import SocketIO

# Global variables 
app = Flask(__name__)
app.config['SECRET_KEY'] = 'test'
io = SocketIO(app, cors_allowed_origins="*")
state = {
    "controled": False,
    "access_key": ''
}
error_no_key = "You must provide a valid access key!"
#TODO: Add the XGO instance 

# Global functions 

if __name__ == '__main__':
    io.run(app)

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
    
@app.route('/action', methods=['POST'])
def action():
    data = request.json
    if check_auth(data.get('key')):
        id = data.get('id')
        #TODO: add the call to XGO class 
        return { "ok": True }
    else:
        return { "error": error_no_key }

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    if check_auth(data.get('key')):
        dir = data.get('direction')
        step = data.get('step')
        #TODO: add the call to XGO class 
        return { "ok": True }
    else:
        return { "error": error_no_key }
    
@app.route('/turn', methods=['POST'])
def turn():
    data = request.json
    if check_auth(data.get('key')):
        step = data.get('step')
        #TODO: add the call to XGO class 
    else: 
        return { "error": error_no_key }

@app.route('/translate', methods=['POST'])
def translate():
    data = request.json
    if check_auth(data.get('key')):
        dir = data.get('direction')
        step = data.get('step')
        #TODO: add the call to XGO class 
    else: 
        return { "error": error_no_key }
    
@app.route('/attitude', methods=['POST'])
def attitude():
    data = request.json
    if check_auth(data.get('key')):
        dir = data.get('direction')
        step = data.get('step')
        #TODO: add the call to XGO class 
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
        #TODO: add the call to XGO class 
    else: 
        return { "error": error_no_key }
    
@app.route('/motor', methods=['POST'])
def motor():
    data = request.json
    if check_auth(data.get('key')):
        id = data.get('id')
        step = data.get('step')
        #TODO: add the call to XGO class 
    else: 
        return { "error": error_no_key }
    
@io.on('connect')
def on_connect():
    print('New client connected!')

@io.on('command')
def on_command(json):
    print('JSON ', json)