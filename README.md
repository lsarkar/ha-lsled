## LS LEDS

## Folder structure
### custom_components/ls_leds

Home Assistant Custom Component for integrating WS2812 LED Strips with custom firmware that receives UDP commands

### kitchenleds
Raspberry Pi Pico W python code

## Installation
- Install ls_leds custom component through HACS (Home Assistant Community Store)
- Update Home Assistant YAML configuration

```
light:
  - platform: ls_leds
    host: <ip address>
    port: <port>
```

ip address - static IP address of the WS2812B light strip
port - The default port is **2522**
