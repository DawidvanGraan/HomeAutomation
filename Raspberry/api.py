#!/bin/sh

from flask import Flask, jsonify
import smbus
import time
import RPi.GPIO as io
import requests

# Plex Call
plexUrl = 'http://192.168.1.100/jsonrpc?request={"jsonrpc": "2.0", "method": "Player.GetItem", "params": { "properties": ["title", "album", "duration", "showtitle"], "playerid": 1 }, "id": "VideoGetItem"}';

I2C_ADDRESS = 0x4a

app = Flask(__name__)

gpioBigGate = 18        # Big Gate
gpioSmallGate = 23      # Small Gate
gpioGarageRight = 24    # Garage Right
gpioGarageLeft = 25     # Garage Left

mag_switch1 = 22        # Garage Door Right
mag_switch2 = 17        # Garage Door Left

# I2C BUS
bus = smbus.SMBus(0)

# GPIO
io.setmode(io.BCM)
io.setup(mag_switch1, io.IN, pull_up_down=io.PUD_UP)
io.setup(mag_switch2, io.IN, pull_up_down=io.PUD_UP)

io.setup(gpioBigGate, io.OUT)
io.setup(gpioSmallGate, io.OUT)
io.setup(gpioGarageRight, io.OUT)
io.setup(gpioGarageLeft, io.OUT)


@app.route('/api/v1/hello', methods=['GET'])
def get_hello():
    return jsonify({
        "status": 200,
        "message": "Hello API. I'm Alive and waiting for your Commands!"
    })


@app.route('/api/v1/plex', methods=['GET'])
def plex():
    r = requests.get(plexUrl)
    if r.status_code != 200:
        return jsonify({
            "status": 500,
            "message": "Oops, could not make call to Plex!"
        })

    return jsonify(r.content)


@app.route('/api/v1/biggate', methods=['GET'])
def get_biggate():
    io.output(gpioBigGate, io.HIGH)
    time.sleep(2)
    io.output(gpioBigGate, io.LOW)

    return jsonify({
        "status": 200,
        "message": "Big Gate Busy..."
    })


@app.route('/api/v1/smallgate', methods=['GET'])
def get_smallgate():
    io.output(gpioSmallGate, io.HIGH)
    time.sleep(2)
    io.output(gpioSmallGate, io.LOW)

    return jsonify({
        "status": 200,
        "message": "Small Gate Busy..."
    })


@app.route('/api/v1/garageright', methods=['GET'])
def get_garage_right():
    io.output(gpioGarageRight, io.HIGH)
    time.sleep(2)
    io.output(gpioGarageRight, io.LOW)

    rightSensor = io.input(mag_switch1)

    return jsonify({
        "status": 200,
        "message": "Garage Door Right",
        "garageRight": rightSensor
    })


@app.route('/api/v1/garageleft', methods=['GET'])
def get_garage_left():
    io.output(gpioGarageLeft, io.HIGH)
    time.sleep(2)
    io.output(gpioGarageLeft, io.LOW)

    leftSensor = io.input(mag_switch2)

    return jsonify({
        "status": 200,
        "message": "Garage Door Left",
        "garageLeft": leftSensor
    })


@app.route('/api/v1/garagedoors', methods=['GET'])
def get_garage_doors():
    rightSensor = io.input(mag_switch1)
    leftSensor = io.input(mag_switch2)

    return jsonify({
        "status": 200,
        "message": "States of the Garage Doors",
        "garageRight": rightSensor,
        "garageLeft": leftSensor
    })


@app.route('/api/v1/temp1', methods=['GET'])
def temp1():
    values = bus.read_i2c_block_data(I2C_ADDRESS, 0x00, 2)
    tempMSB = values[0]
    tempLSB = values[1]
    temp = (((tempMSB << 8) | tempLSB) >> 7) * 0.5
    if temp > 125:
        temp = (((((tempMSB << 8) | tempLSB) >> 7) * 0.5) - 256)

    return jsonify({
        "status": 200,
        "message": "Temperature 1 Sensor Value",
        "temp": temp
    })


@app.route('/')
def index():
    return "Hello, Home Remote!!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
