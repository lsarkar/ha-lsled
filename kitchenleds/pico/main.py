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
    
def led_start_up_sequence():
    upper_strip.write_all(255, 0, 0)
    lower_strip.write_all(255, 0, 0)
    time.sleep(0.5)
    upper_strip.write_all(0, 0, 255)
    lower_strip.write_all(0, 255, 0)
    time.sleep(0.5)
    upper_strip.write_all(0, 0, 255)
    lower_strip.write_all(0, 0, 255)
    time.sleep(0.5)
    

led_strips_off()
led_start_up_sequence()
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

# static IP address ref: https://diyprojectslab.com/raspberry-pi-pico-w-with-a-static-ip-address/
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
    raise RuntimeError('WiFi connection failed')
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

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

s.bind(("", PORT))


class DataPacket:
    
    """
    payload:
        packet:
            8 bits red
            8 bits green
            8 bits blue
            4 bits command id
                0x0 WRITE Command
                0x1 READ Command
                0x2 ID Command - TBD
            4 bits strip id
                0x0 strip id 0
                0x1 strip id 1
                0xF strip id 2 (ALL) (deprecated)
    """
    
    def __init__(self, raw_input):
        self.raw_input = raw_input
        self._r = self.raw_input[0] & 0xFF
        self._g = self.raw_input[1] & 0xFF
        self._b = self.raw_input[2] & 0xFF
        self._command = (self.raw_input[3] >> 4) & 0xF
        self._led_strip_id = self.raw_input[3] & 0xF
    
    def strip_id(self):
        return self._led_strip_id
    
    def red(self):
        return self._r
    
    def green(self):
        return self._g
    
    def blue(self):
        return self._b
    
    def command(self):
        return self._command
    
    def color(self):
        return (self._r, self._g, self._b)
    
    def invert_color(self):
        return (255 - self._r, 255 - self._g, 255 - self._b)


MSG_TO_SEND = 'ACK'

def send(socket, udp_ip, udp_port, msg_to_send=MSG_TO_SEND):
    socket.sendto(msg_to_send, (udp_ip, udp_port))

def write_to_strip(strip: PicoLedStrip, color: tuple):
    strip.write_all(color[0], color[1], color[2])


state_manager = {}
state_manager[LOWER_STRIP_ID] = (0, 0, 0)
state_manager[UPPER_STRIP_ID] = (0, 0, 0)

def write_command(packet: DataPacket, strip: PicoLedStrip):
    color = packet.color()

    if packet.strip_id() == LOWER_STRIP_ID:
        state_manager[LOWER_STRIP_ID] = color
        write_to_strip(lower_strip, color)
        print(state_manager[LOWER_STRIP_ID])
    elif packet.strip_id() == UPPER_STRIP_ID:
        write_to_strip(upper_strip, color)
        state_manager[UPPER_STRIP_ID] = color
        print(state_manager[UPPER_STRIP_ID])
    elif packet.strip_id() == ALL_STRIP_ID:
        write_to_strip(lower_strip, color)
        write_to_strip(upper_strip, color)
    else:
        # unrecognized ID, log error
        print("Did not recognize valid strip id")

def read_command(packet: DataPacket):
    if packet.strip_id() not in state_manager.keys():
        print("Couldn't recognize valid strip id")
        return
    
    return state_manager[packet.strip_id()]

WRITE_COMMAND = 0
READ_COMMAND = 1

while True:
    print('Server listening..')
    print("Send a command to control leds")

    data, addr = s.recvfrom(4096)

    if data is not None:
  
        if len(data) != 4:
            print(f"Couldn't recognise data packet: {data}, expected 4 bytes")
            break

        ip_address = addr[0]
        port = addr[1]

        packet = DataPacket(data)

        print(f'red: {packet.red()} green: {packet.green()} blue: {packet.blue()} command: {packet.command()} strip id: {packet.strip_id()}')
        print(f'received: {data} from {addr[0]}:{addr[1]}')

        # handle write command
        if packet.command() == WRITE_COMMAND:
            write_command(packet, packet.strip_id())
            print("WRITE COMMAND")
            send(s, ip_address, port)
        # handle read command
        elif packet.command() == READ_COMMAND:
            state = read_command(packet)
            print(f"READ COMMAND {state}")
            send(s, ip_address, port, msg_to_send=bytearray(state))
        else:
            print("Unrecognized command")

    

    time.sleep(0.001)