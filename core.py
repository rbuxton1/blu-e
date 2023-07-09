from xgolib import XGO 
from picamera2 import Picamera2
from api import API 
from flask import Flask
from flask_socketio import SocketIO
import xgoscreen.LCD_2inch as LCD_2inch
from PIL import Image,ImageDraw
from libcamera import ColorSpace

class Core:

    def __init__(self, live=False):
        # Bring up the dog
        if live == True:
            # If the dog parameter was provided then initialize dog 
            self.dog = XGO(port='/dev/serial0',version="xgolite")
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
        else: 
            self.dog = None

        # Bring up camera 
        self.camera = Picamera2()
        self.init_and_start_cam()

        # Bring up flask and flask_socket 
        self.flask = Flask(__name__)
        self.flask.config['SECRET_KEY'] = 'test' #TODO: Expose this to an environment variable 
        self.socket = SocketIO(self.flask, cors_allowed_origins="*")

        #TODO: Implement a display manager class and bring that up here 
        display = LCD_2inch.LCD_2inch()
        display.Init()
        display.clear()
        eye_size = 40
        splash = Image.new("RGB", (display.height, display.width), (0, 0, 255))
        splash_draw = ImageDraw.Draw(splash)
        splash_draw.ellipse([(30 - (eye_size/2), (display.width/2) -(eye_size/2)), (30 + eye_size, (display.width/2) + eye_size)], (255, 255, 255), (255, 255, 255))
        splash_draw.ellipse([(display.height - 50 - (eye_size/2), (display.width/2) -(eye_size/2)), (display.height - 50 + eye_size, (display.width/2) + eye_size)], (255, 255, 255), (255, 255, 255))
        display.ShowImage(splash)

        # Start the API
        self.api = API(self.flask, self.socket, self.dog, self.camera)
        

    def init_and_start_cam(self, height=480, width=640):
        """Initializes the camera for the RC view"""
        config = self.camera.create_preview_configuration({"format": 'RGB888', "size": (width, height)}, colour_space=ColorSpace.Srgb(), raw={"format": "SGBRG10_CSI2P", "size": (width, height)})
        self.camera.configure(config)
        self.camera.start()
    
    def start(self):
        print('Starting Blu-E Core!')
        self.flask.run(host='0.0.0.0', port=5000)
        self.socket.run(self.flask)