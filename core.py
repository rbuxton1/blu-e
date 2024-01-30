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
            fm = self.dog.read_firmware()
            if fm[0] == 'M':
                print('XGO-MINI')
                self.dog = XGO(port='/dev/ttyAMA0',version="xgomini")
            else:
                print('XGO-LITE')
            self.dog.reset()
            print('Connected to XGO. Battery: ', self.dog.read_battery())
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
        self.display = LCD_2inch.LCD_2inch()
        self.display.Init()
        self.display.clear()
        eye_size = 40
        

        # Start the API
        self.api = API(self.flask, self.socket, self.dog, self.camera, self.display)
        

    def init_and_start_cam(self, height=480, width=640):
        """Initializes the camera for the RC view"""
        config = self.camera.create_preview_configuration({"format": 'RGB888', "size": (width, height)}, colour_space=ColorSpace.Srgb(), raw={"format": "SGBRG10_CSI2P", "size": (width, height)})
        self.camera.configure(config)
        self.camera.start()
    
    def init_display_with_eyes(self, size=40):
        splash = Image.new("RGB", (self.display.height, self.display.width), (0, 0, 255))
        splash_draw = ImageDraw.Draw(splash)
        splash_draw.ellipse([
            (30 - (size/2), (self.display.width/2) -(size/2)),
            (30 + size, (self.display.width/2) + size)
        ], 
            (255, 255, 255), 
            (255, 255, 255)
        )
        splash_draw.ellipse([
            (self.display.height - 50 - (size/2),
            (self.display.width/2) -(size/2)), 
            (self.display.height - 50 + size, (self.display.width/2) + size)
        ], 
            (255, 255, 255), 
            (255, 255, 255)
        )
        self.display.ShowImage(splash)
    
    def start(self):
        print('Starting Blu-E Core!')
        self.flask.run(host='0.0.0.0', port=5000)
        self.socket.run(self.flask)