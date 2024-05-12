Kitchen LED project with button switch to change colors of the LED strip. Communication to done over UDP

###  Hardware
Code runs on the Pi Pico W with MicroPython

The Pi Pico W listens for UDP messages on port 2252

--------
### BOM
| Item | Quantity |
| -- | -- |
| [Raspberry Pi Pico W](https://www.adafruit.com/product/5526?gclid=CjwKCAiA3KefBhByEiwAi2LDHHrzBphUm--6PniyvxpFsNIY99liun2cfvlbB1_9122XP3Poi4Q0pxoCPsEQAvD_BwE) | 1 |
| [74AHC125 Level Converter](https://cdn-shop.adafruit.com/product-files/1787/1787AHC125.pdf) | 1 |
| [WS2812B LED Strip](https://www.amazon.com/ALITOVE-Individual-Addressable-Programmable-Non-Waterproof/dp/B086B8Z6BK/ref=sr_1_10?crid=X51V29C4HMQV&keywords=ws2812b&qid=1676341262&sprefix=ws2812b%2Caps%2C194&sr=8-10&th=1) | 2 |

---

### Wiring
LED Strips are connected to GP27 and GP28 on the Pi Pico

The Level Converter is required as the GPIOs from the Pico output 3.3V and the WS2812 LED strips require 5V

<b>Indexes</b>
<p>
0 - both strips
1 - upper strip
2 - lower strip
</p>

---

### Useful Links
- [Pico W Pin Out Diagram](https://datasheets.raspberrypi.com/picow/PicoW-A4-Pinout.pdf)
- [Level Converter Wiring Example](https://www.adafruit.com/product/1787)
- [WLAN reference](https://docs.micropython.org/en/latest/library/network.WLAN.html)


- https://how2electronics.com/iot-rgb-led-strip-control-with-raspberry-pi-pico-w/
- https://how2electronics.com/raspberry-pi-pico-w-web-server-tutorial-with-micropython/

- https://github.com/pi3g/pico-w/blob/main/MicroPython/I%20Pico%20W%20LED%20web%20server/main.py

- [Async Webserver](https://gist.github.com/aallan/3d45a062f26bc425b22a17ec9c81e3b6)

- https://datasheets.raspberrypi.com/picow/connecting-to-the-internet-with-pico-w.pdf




### TODOs
- Add config flow using reference thread: https://community.home-assistant.io/t/custom-integration-error-creating-device-with-entities/635842/8
- Add custom read commands with UDP packet payload





