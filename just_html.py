from flask import Flask, render_template

app = Flask(__name__)

@app.route('/rc')
def rc():
    return render_template('control.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)