from flask import Flask, Response, render_template, request, redirect, url_for
import cv2
import serial
import time

ser = serial.Serial(
    port='/dev/ttyACM0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

ser.write(b'\x03')
ser.write(b'\x03')
ser.write(b'\x03')
ser.write(b'\x03')
ser.readlines()
ser.write('import hub\r\n'.encode())
ser.write('import utime\r\n'.encode())
ser.write('speed = 0\r\n'.encode())
ser.write('bias = 0\r\n'.encode())
ser.write('motorL = hub.port.E.motor\r\n'.encode())
ser.write('motorR = hub.port.F.motor\r\n'.encode())
ser.write('pair = motorL.pair(motorR)\r\n'.encode())
ser.write('pair.pwm(0,0)\r\n'.encode())

cam = cv2.VideoCapture(0)

def gen_frames():
    while True:
        success, frame = cam.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            frame = buffer.tobytes()
            yield (
                b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
            )

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    return Response(gen_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

@app.route("/controller")
def controller():
    return render_template("controller.html")

@app.route("/go")
def go():
    ser.write('speed = 60\r\n'.encode())
    ser.write('bias = 0\r\n'.encode())
    ser.write('pair.pwm(speed + bias, -speed + bias)\r\n'.encode())
    return redirect(url_for('controller'))

@app.route("/accelerate")
def accelerate():
    ser.write('speed = speed + 10\r\n'.encode())
    ser.write('pair.pwm(speed + bias, -speed + bias)\r\n'.encode())
    return redirect(url_for('controller'))

@app.route("/decelerate")
def decelerate():
    ser.write('speed = speed - 10\r\n'.encode())
    ser.write('pair.pwm(speed + bias, -speed + bias)\r\n'.encode())
    return redirect(url_for('controller'))

@app.route("/left")
def left():
    ser.write('bias = bias + 5\r\n'.encode())
    ser.write('pair.pwm(speed + bias, -speed + bias)\r\n'.encode())
    return redirect(url_for('controller'))

@app.route("/right")
def right():
    ser.write('bias = bias - 5\r\n'.encode())
    ser.write('pair.pwm(speed + bias, -speed + bias)\r\n'.encode())
    return redirect(url_for('controller'))

@app.route("/stop")
def stop():
    ser.write('speed = 0\r\n'.encode())
    ser.write('bias = 0\r\n'.encode())
    ser.write('pair.pwm(0,0)\r\n'.encode())
    return redirect(url_for('controller'))
 
if __name__ == "__main__":
    app.run(debug=True)