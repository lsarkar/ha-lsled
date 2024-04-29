## LS LEDS
Home Assistant Custom Component for integrating WS2812 LED Strips

### Installation
- Install through HACS (Home Assistant Community Store)
- Update YAML configuration

```
light:
  - platform: ls_leds
    host: <ip address>
    port: <port>
```

ip address - static IP address of the WS2812B light strip
port - The default port is **2522**
