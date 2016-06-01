# The MIT License (MIT)
#
# GrovePi for the Raspberry Pi: an open source platform for connecting Grove Sensors to the Raspberry Pi.
# Copyright (C) 2015  Dexter Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import math
import struct
import time

import RPi.GPIO as GPIO
from smbus import SMBus


GPIO_REV = GPIO.RPI_REVISION
# I2C Address of Arduino
I2C_ADDRESS = 0x04

# Command Format
# digitalRead() command format header
dRead_cmd = [1]
# digitalWrite() command format header
dWrite_cmd = [2]
# analogRead() command format header
aRead_cmd = [3]
# analogWrite() command format header
aWrite_cmd = [4]
# pinMode() command format header
pMode_cmd = [5]
# Ultrasonic read
uRead_cmd = [7]
# Get firmware version
version_cmd = [8]
# Accelerometer (+/- 1.5g) read
acc_xyz_cmd = [20]
# RTC get time
rtc_getTime_cmd = [30]
# DHT Pro sensor temperature
dht_temp_cmd = [40]

# Grove LED Bar commands
# Initialise
ledbar_init_cmd = [50]
# Set orientation
ledbar_orient_cmd = [51]
# Set level
ledbar_level_cmd = [52]
# Set single LED
ledbar_set_one_cmd = [53]
# Toggle single LED
ledbar_toggle_one_cmd = [54]
# Set all LEDs
ledbar_set_cmd = [55]
# Get current state
ledbar_get_cmd = [56]

# Grove 4 Digit Display commands
# Initialise
fourDigitInit_cmd = [70]
# Set brightness, not visible until next cmd
fourDigitBrightness_cmd = [71]
# Set numeric value without leading zeros
fourDigitValue_cmd = [72]
# Set numeric value with leading zeros
fourDigitValueZeros_cmd = [73]
# Set individual digit
fourDigitIndividualDigit_cmd = [74]
# Set individual leds of a segment
fourDigitIndividualLeds_cmd = [75]
# Set left and right values with colon
fourDigitScore_cmd = [76]
# Analog read for n seconds
fourDigitAnalogRead_cmd = [77]
# Entire display on
fourDigitAllOn_cmd = [78]
# Entire display off
fourDigitAllOff_cmd = [79]

# Grove chainable RGB LED commands
# Store color for later use
storeColor_cmd = [90]
# Initialise
chainableRgbLedInit_cmd = [91]
# Initialise and test with a simple color
chainableRgbLedTest_cmd = [92]
# Set one or more leds to the stored color by pattern
chainableRgbLedSetPattern_cmd = [93]
# set one or more leds to the stored color by modulo
chainableRgbLedSetModulo_cmd = [94]
# sets leds similar to a bar graph, reversible
chainableRgbLedSetLevel_cmd = [95]

# Read the button from IR sensor
ir_read_cmd = [21]
# Set pin for the IR reciever
ir_recv_pin_cmd = [22]

dus_sensor_read_cmd = [10]
dust_sensor_en_cmd = [14]
dust_sensor_dis_cmd = [15]
encoder_read_cmd = [11]
encoder_en_cmd = [16]
encoder_dis_cmd = [17]
flow_read_cmd = [12]
flow_disable_cmd = [13]
flow_en_cmd = [18]
# This allows us to be more specific about which commands contain unused bytes
unused = 0


if GPIO_REV == 2 or GPIO_REV == 3:
    bus = SMBus(1)
else:
    bus = SMBus(0)


class GrovePiException(Exception):
    pass

# Function declarations of the various functions used for encoding and sending
# data from RPi to Arduino


def write_i2c_block(block):
    try:
        bus.write_i2c_block_data(I2C_ADDRESS, 1, block)
    except IOError as e:
        raise GrovePiException(e)


def read_i2c_byte(address=I2C_ADDRESS):
    try:
        return bus.read_byte(address)
    except IOError as e:
        raise GrovePiException(e)


def read_i2c_block(address=I2C_ADDRESS):
    try:
        return bus.read_i2c_block_data(address, 1)
    except IOError as e:
        raise GrovePiException(e)


# Arduino Digital Read
def digital_read(pin):
    write_i2c_block(dRead_cmd + [pin, unused, unused])
    time.sleep(.1)
    n = read_i2c_byte()
    return n


# Arduino Digital Write
def digital_write(pin, value):
    write_i2c_block(dWrite_cmd + [pin, value, unused])


# Setting up Pin mode on Arduino
def pin_mode(pin, mode):
    if mode == "OUTPUT":
        write_i2c_block(pMode_cmd + [pin, 1, unused])
    elif mode == "INPUT":
        write_i2c_block(pMode_cmd + [pin, 0, unused])


# Read analog value from Pin
def analog_read(pin):
    write_i2c_block(aRead_cmd + [pin, unused, unused])
    time.sleep(.1)
    read_i2c_byte()
    number = read_i2c_block()
    time.sleep(.1)
    return number[1] * 256 + number[2]


# Write PWM
def analog_write(pin, value):
    write_i2c_block(aWrite_cmd + [pin, value, unused])


# Read temp in Celsius from Grove Temperature Sensor
def temp(pin, model='1.0'):
    # Each of the sensor revisions use different thermistors, each with their own B value constant
    if model == '1.2':
        b_value = 4250  # sensor v1.2 uses thermistor ??? (assuming NCP18WF104F03RC until SeeedStudio clarifies)
    elif model == '1.1':
        b_value = 4250  # sensor v1.1 uses thermistor NCP18WF104F03RC
    else:
        b_value = 3975  # sensor v1.0 uses thermistor TTC3A103*39H
    a = analog_read(pin)
    resistance = float(1023 - a) * 10000 / a
    t = float(1 / (math.log(resistance / 10000) / b_value + 1 / 298.15) - 273.15)

    if math.isnan(t):
        raise GrovePiException("NaN")

    return t


# Read value from Grove Ultrasonic
def ultrasonic_read(pin):
    write_i2c_block(uRead_cmd + [pin, unused, unused])
    time.sleep(.2)
    read_i2c_byte()
    number = read_i2c_block()
    return number[1] * 256 + number[2]


# Read the firmware version
def version():
    write_i2c_block(version_cmd + [unused, unused, unused])
    time.sleep(.1)
    read_i2c_byte()
    number = read_i2c_block()
    return "%s.%s.%s" % (number[1], number[2], number[3])


# Read Grove Accelerometer (+/- 1.5g) XYZ value
def acc_xyz():
    write_i2c_block(acc_xyz_cmd + [unused, unused, unused])
    time.sleep(.1)
    read_i2c_byte()
    number = read_i2c_block()
    if number[1] > 32:
        number[1] = - (number[1] - 224)
    if number[2] > 32:
        number[2] = - (number[2] - 224)
    if number[3] > 32:
        number[3] = - (number[3] - 224)
    return number[1], number[2], number[3]


# Read from Grove RTC
def rtc_get_time():
    write_i2c_block(rtc_getTime_cmd + [unused, unused, unused])
    time.sleep(.1)
    read_i2c_byte()
    number = read_i2c_block()
    return number


# Read and return temperature and humidity from Grove DHT Pro
def dht(pin, module_type):
    write_i2c_block(dht_temp_cmd + [pin, module_type, unused])

    # Delay necessary for proper reading from DHT sensor
    time.sleep(.6)
    try:
        read_i2c_byte()
        number = read_i2c_block()
        time.sleep(.1)
        if number == -1:
            raise GrovePiException
    except (TypeError, IndexError) as e:
        raise GrovePiException(e)

    # Data returned in IEEE format as a float in 4 bytes
    t_val = bytearray(number[1:5])
    h_val = bytearray(number[5:9])
    t = round(struct.unpack('f', t_val)[0], 2)
    hum = round(struct.unpack('f', h_val)[0], 2)

    if math.isnan(t) or math.isnan(hum):
        raise GrovePiException("NaN")

    try:
        result = [float(t), float(hum)]
    except ValueError as e:
        raise GrovePiException(e)

    return result


# Grove LED Bar - initialise
# orientation: (0 = red to green, 1 = green to red)
def ledbar_init(pin, orientation):
    write_i2c_block(ledbar_init_cmd + [pin, orientation, unused])


# Grove LED Bar - set orientation
# orientation: (0 = red to green,  1 = green to red)
def ledbar_orientation(pin, orientation):
    write_i2c_block(ledbar_orient_cmd + [pin, orientation, unused])


# Grove LED Bar - set level
# level: (0-10)
def ledbar_set_level(pin, level):
    write_i2c_block(ledbar_level_cmd + [pin, level, unused])


# Grove LED Bar - set single led
# led: which led (1-10)
# state: off or on (0-1)
def ledbar_set_led(pin, led, state):
    write_i2c_block(ledbar_set_one_cmd + [pin, led, state])


# Grove LED Bar - toggle single led
# led: which led (1-10)
def ledbar_toggle_led(pin, led):
    write_i2c_block(ledbar_toggle_one_cmd + [pin, led, unused])


# Grove LED Bar - set all leds
# state: (0-1023) or (0x00-0x3FF) or (0b0000000000-0b1111111111) or (int('0000000000',2)-int('1111111111',2))
def ledbar_set_bits(pin, state):
    byte1 = state & 255
    byte2 = state >> 8
    write_i2c_block(ledbar_set_cmd + [pin, byte1, byte2])


# Grove LED Bar - get current state
# state: (0-1023) a bit for each of the 10 LEDs
def ledbar_get_bits(pin):
    write_i2c_block(ledbar_get_cmd + [pin, unused, unused])
    time.sleep(.2)
    read_i2c_byte(0x04)
    block = read_i2c_block(0x04)
    return block[1] ^ (block[2] << 8)


# Grove 4 Digit Display - initialise
def four_digit_init(pin):
    write_i2c_block(fourDigitInit_cmd + [pin, unused, unused])


# Grove 4 Digit Display - set numeric value with or without leading zeros
# value: (0-65535) or (0000-FFFF)
def four_digit_number(pin, value, leading_zero):
    # split the value into two bytes so we can render 0000-FFFF on the display
    byte1 = value & 255
    byte2 = value >> 8
    # separate commands to overcome current 4 bytes per command limitation
    if leading_zero:
        write_i2c_block(fourDigitValue_cmd + [pin, byte1, byte2])
    else:
        write_i2c_block(fourDigitValueZeros_cmd + [pin, byte1, byte2])
    time.sleep(.05)


# Grove 4 Digit Display - set brightness
# brightness: (0-7)
def four_digit_brightness(pin, brightness):
    # not actually visible until next command is executed
    write_i2c_block(fourDigitBrightness_cmd + [pin, brightness, unused])
    time.sleep(.05)


# Grove 4 Digit Display - set individual segment (0-9,A-F)
# segment: (0-3)
# value: (0-15) or (0-F)
def four_digit_digit(pin, segment, value):
    write_i2c_block(fourDigitIndividualDigit_cmd + [pin, segment, value])
    time.sleep(.05)


# Grove 4 Digit Display - set 7 individual leds of a segment
# segment: (0-3)
# leds: (0-255) or (0-0xFF) one bit per led, segment 2 is special, 8th bit is the colon
def four_digit_segment(pin, segment, leds):
    write_i2c_block(fourDigitIndividualLeds_cmd + [pin, segment, leds])
    time.sleep(.05)


# Grove 4 Digit Display - set left and right values (0-99), with leading zeros and a colon
# left: (0-255) or (0-FF)
# right: (0-255) or (0-FF)
# colon will be lit
def four_digit_score(pin, left, right):
    write_i2c_block(fourDigitScore_cmd + [pin, left, right])
    time.sleep(.05)


# Grove 4 Digit Display - display analogRead value for n seconds, 4 samples per second
# analog: analog pin to read
# duration: analog read for this many seconds
def four_digit_monitor(pin, analog, duration):
    write_i2c_block(fourDigitAnalogRead_cmd + [pin, analog, duration])
    time.sleep(duration + .05)


# Grove 4 Digit Display - turn entire display on (88:88)
def four_digit_on(pin):
    write_i2c_block(fourDigitAllOn_cmd + [pin, unused, unused])
    time.sleep(.05)


# Grove 4 Digit Display - turn entire display off
def four_digit_off(pin):
    write_i2c_block(fourDigitAllOff_cmd + [pin, unused, unused])
    time.sleep(.05)


# Grove Chainable RGB LED - store a color for later use
# red: 0-255
# green: 0-255
# blue: 0-255
def store_color(red, green, blue):
    write_i2c_block(storeColor_cmd + [red, green, blue])
    time.sleep(.05)


# Grove Chainable RGB LED - initialise
# numLeds: how many leds do you have in the chain
def chainable_rgb_led_init(pin, num_leds):
    write_i2c_block(chainableRgbLedInit_cmd + [pin, num_leds, unused])
    time.sleep(.05)


# Grove Chainable RGB LED - initialise and test with a simple color
# numLeds: how many leds do you have in the chain
# testColor: (0-7) 3 bits in total - a bit for red, green and blue, eg. 0x04 == 0b100 (0bRGB) == rgb(255, 0, 0) == #FF0000 == red
#            ie. 0 black, 1 blue, 2 green, 3 cyan, 4 red, 5 magenta, 6 yellow, 7 white
def chainable_rgb_led_test(pin, num_leds, test_color):
    write_i2c_block(chainableRgbLedTest_cmd + [pin, num_leds, test_color])
    time.sleep(.05)


# Grove Chainable RGB LED - set one or more leds to the stored color by pattern
# pattern: (0-3) 0 = this led only, 1 all leds except this led, 2 this led and all leds inwards, 3 this led and all leds outwards
# whichLed: index of led you wish to set counting outwards from the GrovePi, 0 = led closest to the GrovePi
def chainable_rgb_led_pattern(pin, pattern, which_led):
    write_i2c_block(chainableRgbLedSetPattern_cmd + [pin, pattern, which_led])
    time.sleep(.05)


# Grove Chainable RGB LED - set one or more leds to the stored color by modulo
# offset: index of led you wish to start at, 0 = led closest to the GrovePi, counting outwards
# divisor: when 1 (default) sets stored color on all leds >= offset, when 2 sets every 2nd led >= offset and so on
def chainable_rgb_led_modulo(pin, offset, divisor):
    write_i2c_block(chainableRgbLedSetModulo_cmd + [pin, offset, divisor])
    time.sleep(.05)


# Grove Chainable RGB LED - sets leds similar to a bar graph, reversible
# level: (0-10) the number of leds you wish to set to the stored color
# reversible (0-1) when 0 counting outwards from GrovePi, 0 = led closest to the GrovePi, otherwise counting inwards
def chainable_rgb_led_set_level(pin, level, reverse):
    write_i2c_block(chainableRgbLedSetLevel_cmd + [pin, level, reverse])
    time.sleep(.05)


# Grove - Infrared Receiver- get the commands received from the Grove IR sensor
def ir_read_signal():
    try:
        write_i2c_block(ir_read_cmd + [unused, unused, unused])
        time.sleep(.1)
        data_back = read_i2c_block()[0:21]
        if data_back[1] != 255:
            return data_back
        return [-1] * 21
    except IOError as e:
        raise GrovePiException(e)


# Grove - Infrared Receiver- set the pin on which the Grove IR sensor is connected
def ir_recv_pin(pin):
    write_i2c_block(ir_recv_pin_cmd + [pin, unused, unused])


def dust_sensor_en():
    write_i2c_block(dust_sensor_en_cmd + [unused, unused, unused])
    time.sleep(.2)


def dust_sensor_dis():
    write_i2c_block(dust_sensor_dis_cmd + [unused, unused, unused])
    time.sleep(.2)


def dust_sensor_read():
    write_i2c_block(dus_sensor_read_cmd + [unused, unused, unused])
    time.sleep(.2)
    data_back = read_i2c_block()[0:4]

    if data_back[0] != 255:
        lowpulseoccupancy = (data_back[3] * 256 * 256 + data_back[2] * 256 + data_back[1])
        return [data_back[0], lowpulseoccupancy]
    else:
        raise GrovePiException


def encoder_en():
    write_i2c_block(encoder_en_cmd + [unused, unused, unused])
    time.sleep(.2)


def encoder_dis():
    write_i2c_block(encoder_dis_cmd + [unused, unused, unused])
    time.sleep(.2)


def encoder_read():
    write_i2c_block(encoder_read_cmd + [unused, unused, unused])
    time.sleep(.2)
    data_back = read_i2c_block()[0:2]

    if data_back[0] != 255:
        return [data_back[0], data_back[1]]
    else:
        raise GrovePiException


def flow_disable():
    write_i2c_block(flow_disable_cmd + [unused, unused, unused])
    time.sleep(.2)


def flow_enable():
    write_i2c_block(flow_en_cmd + [unused, unused, unused])
    time.sleep(.2)


def flow_read():
    write_i2c_block(flow_read_cmd + [unused, unused, unused])
    time.sleep(.2)
    data_back = read_i2c_block()[0:3]

    if data_back[0] != 255:
        return [data_back[0], data_back[2] * 256 + data_back[1]]
    else:
        raise GrovePiException
