from flask import Response, render_template
import cv2

class API:

    def __init__(self, flask, flask_socket, dog, cam):
        # Init variables
        self.flask = flask 
        self.socket = flask_socket
        self.cam = cam
        self.dog = dog

        #TODO: Register flask with add_url_rule
        self.flask.add_url_rule('/rc', 'rc', self.rc)
        self.flask.add_url_rule('/video', 'video', self.video_feed)
        #TODO: Register socketio with on_event 
        self.socket.on_event('connect', self.socket_on_connect)
        self.socket.on_event('command', self.socket_on_command)

    def rc(self):
        """Renders the RC view that lets users drive Blu-E"""
        return render_template('control.html')
    
    def generate_video(self):
        """Helper function to generate usable video stream"""
        while True:
            frame = self.cam.capture_array()
            encode_success, jpeg = cv2.imencode('.jpg', frame)
            img = jpeg.tobytes()
            yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
    
    def video_feed(self):
        """Returns the video stream to an endpoint"""
        return Response(self.generate_video(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    
    def socket_on_connect(self):
        """Called whenever a new socket connection is made"""
        self.dog.reset()
        self.socket.emit('status', {
            "battery": self.dog.read_battery(),
            "motors": self.dog.read_motor(),
            "pitch": self.dog.read_pitch(),
            "roll": self.dog.read_roll(),
            "yaw": self.dog.read_yaw()
        })
    
    def socket_on_command(self, json):
        """Called whenever a new socket commmand event is sent, process and exectutes the command."""
        try :
            if json['cmd'] == 'move':
                self.dog.move(json['direction'], int(json['step']))
            elif json['cmd'] == 'turn':
                self.dog.turn(json['step'])
            elif json['cmd'] == 'attitude':
                self.dog.attitude(json['direction'], int(json['step']))
            elif json['cmd'] == 'translate':
                self.dog.translation(json['direction'], int(json['step']))
            elif json['cmd'] == 'motor':
                self.dog.motor(json['id'], int(json['step']))
            elif json['cmd'] == 'gait':
                self.dog.gait_type(json['mode'])
            elif json['cmd'] == 'pace':
                self.dog.pace(json(['mode']))
            elif json['cmd'] == 'imu':
                self.dog.imu(int(json['mode']))
        except Exception as err:
            print(err)