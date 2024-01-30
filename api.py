from flask import Response, render_template
import cv2

class API:
    IDLE_STATUS = "IDLE"
    CONTROLLED_STATUS = "RC"

    def __init__(self, flask, flask_socket, dog, cam, display):
        # Init variables
        self.flask = flask 
        self.socket = flask_socket
        self.cam = cam
        self.dog = dog
        self.display = display

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
    
    def emit_status(self):
        """Basic status object to be emited all the time"""
        self.socket.emit('status',{
            "battery": self.dog.read_battery(),
            "motors": self.dog.read_motor(),
            "pitch": self.dog.read_pitch(),
            "roll": self.dog.read_roll(),
            "yaw": self.dog.read_yaw()
        })

    def socket_on_connect(self):
        """Called whenever a new socket connection is made"""
        self.dog.reset()
        self.emit_status()
    
    def socket_on_command(self, json):
        """Called whenever a new socket commmand event is sent, process and exectutes the command."""
        try :
            if json['cmd'] == 'move':
                self.dog.move(json['direction'], int(json['step']))
            elif json['cmd'] == 'turn':
                self.dog.turn(int(json['step']))
            elif json['cmd'] == 'pace':
                self.dog.pace(json['mode'])
            elif json['cmd'] == 'stop':
                self.dog.stop()
            elif json['cmd'] == 'translation':
                self.dog.translation(json['direction'], int(json['data']))
            elif json['cmd'] == 'attitude':
                self.dog.attitude(json['direction'], int(json['data']))
            elif json['cmd'] == 'periodic_tran':
                self.dog.periodic_tran(json['direction'], int(json['data']))
            elif json['cmd'] == 'periodic_rot':
                self.dog.periodic_rot(json['direction'], int(json['data']))
            elif json['cmd'] == 'arm':
                self.dog.arm(int(json['arm_x']), int(json['arm_z']))
            elif json['cmd'] == 'claw':
                self.dog.claw(int(json['pos']))
            elif json['cmd'] == 'arm_mode':
                self.dog.arm_mode(int(json['mode']))
            elif json['cmd'] == 'reset':
                self.dog.reset()
            elif json['cmd'] == 'imu':
                self.dog.imu(int(json['mode']))
            elif json['cmd'] == 'action':
                self.dog.actions(int(json['action_id']))

            self.emit_status()
        except Exception as err:
            print(err)
            self.socket.emit('error', { "error": err })