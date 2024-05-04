from machine import Pin
import time
from secrets import secrets
#from neopixel import Neopixel

from leds.pico_led import PicoLedStrip
from led_config import LedConfig
import network
import socket


"""
 *  LED STRIP INFO
 *
 *  BOTTOM SECTION
 *  - 23 LEDS on the kitchen short strip
 *  - 55 LEDS on the kitchen long strip
 *  - 88 TOTAL
 *  
 *  TOP SECTION
 *  95 (top right and top center)
 *  approx 70 top left
 *  approx 165 total (old)
 
 *  update added 80 LEDS
 *  TOTAL = 165 + 80
 
"""

PORT = 2522

led_upper = LedConfig()
led_upper.name = "upper strip"
led_upper.strip_id = 0x01
led_upper.num_leds = 245
led_upper.state_machine = 0
led_upper.pin = 28

led_lower = LedConfig()
led_upper.name = "lower strip"
led_lower.strip_id = 0x02
led_lower.num_leds = 88
led_lower.state_machine = 1
led_lower.pin = 27

def create_led_strip(config: LedConfig):
    return PicoLedStrip(config.pin, config.num_leds, state_machine=config.state_machine)

upper_strip = create_led_strip(led_upper)
lower_strip = create_led_strip(led_lower)


ALL_STRIP_ID = 0x00
UPPER_STRIP_ID = 0x01
LOWER_STRIP_ID = 0x02

led = Pin('LED', Pin.OUT)
led.off()


def led_strips_off():
    upper_strip.brightness(90)
    lower_strip.brightness(90)
    upper_strip.off()
    lower_strip.off()
    time.sleep(1)
    
def led_start_up():
    upper_strip.write_all(0, 0, 255)
    lower_strip.write_all(0, 255, 0)
    time.sleep(0.3)
    upper_strip.write_all(255, 0, 255)
    lower_strip.write_all(255, 255, 0)
    time.sleep(0.3)
    upper_strip.write_all(255, 0, 0)
    lower_strip.write_all(0, 255, 255)
    time.sleep(0.3)
    

led_strips_off()
led_start_up()
led_strips_off()

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

accesspoints = wlan.scan()

for ap in accesspoints:
    print("Found: " + ap[0].decode('ASCII'))

SSID = secrets['ssid']
PWD = secrets['password']

wlan.connect(SSID, PWD)

signal_strength = None

# static IP address
# ref: https://diyprojectslab.com/raspberry-pi-pico-w-with-a-static-ip-address/
wlan.ifconfig((secrets['static_ip'], '255.255.255.0', secrets['gateway'], '8.8.8.8'))


wait = 10
while wait > 0:
    if wlan.status() < 0 or wlan.status() >= 3:
        break
    wait -=1
    print('waiting for connection')
    led.on()
    time.sleep(0.3)
    led.off()
    time.sleep(0.3)
    
if wlan.status() != 3:
    raise RuntimeError('wifi connection failed')
    led.off()
else:
    print('connected')
    ip = wlan.ifconfig()[0]
    print('IP: ', ip)
    print('Subnet Mask', wlan.ifconfig()[1])
    led.on()
    

ip = None

def get_ip():
    if wlan is not None:
        wlan.ifconfig()[0]
   
# Function to load in html page    
def get_html(html_name):
    with open(html_name, 'r') as file:
        html = file.read()
        
    return html

# HTTP server with socket
#addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(("", PORT))


class DataPacket:
    
    """
    payload:
        header:
            version: 4 bits
            command type: 2 bits
                - 0: reserved
                - 1: reserved
                - 2: reserved
                - 3: reserved
        packet:
            8 bits red
            8 bits green
            8 bits blue
            8 bits strip id (TODO: change to less bytes)
                0x00 strip id 0
                0x01 strip id 1
                0xFF strip id all
    """
    
    def __init__(self, raw_input):
        self.raw_input = raw_input
        self.r = self.raw_input[0] & 0xFF
        self.g = self.raw_input[1] & 0xFF
        self.b = self.raw_input[2] & 0xFF
        self.led_strip_id = self.raw_input[3]
    
    def strip_id(self):
        return self.led_strip_id
    
    def red(self):
        return self.r
    
    def green(self):
        return self.g
    
    def blue(self):
        return self.b
    
    def color(self):
        return (self.r, self.g, self.b)
    
    def invert_color(self):
        return (255 - self.r, 255 - self.g, 255 - self.b)


def send(socket, udp_ip, udp_port):
    MSG_TO_SEND = 'ACK'
    socket.sendto(MSG_TO_SEND, (udp_ip, udp_port))

while True:

    print('Server listening..')
    print("Send and a command to control leds")

    data, addr = s.recvfrom(4096)
    
    color = None
    invert_color = None
    
    if data is not None:
        p = DataPacket(data)
        print(f'red: {p.red()} green: {p.green()} blue: {p.blue()} strip id: {p.strip_id()}')
        print(f'received: {data} from {addr[0]}:{addr[1]}')
        send(s, addr[0], addr[1])
        color = p.color()
        #invert_color = p.invert_color()
        invert_color = p.color()
    
    if p.strip_id() == LOWER_STRIP_ID:
        lower_strip.write_all(invert_color[0], invert_color[1], invert_color[2])
    elif p.strip_id() == UPPER_STRIP_ID:
        upper_strip.write_all(color[0], color[1], color[2])
    elif p.strip_id() == ALL_STRIP_ID:
        upper_strip.write_all(color[0], color[1], color[2])
        lower_strip.write_all(invert_color[0], invert_color[1], invert_color[2])
    else:
        # unrecognized ID, log error
        print("Did not recognize valid strip id")
    

    time.sleep(0.001)