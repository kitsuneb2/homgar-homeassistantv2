# HomGar Home Assistant Integration v2

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

Home Assistant integration for Homgar / RainPoint 

This project is forked from Remboooo/homgarapi and adapted for Home Assistant usage.

## ✨ What’s New in This Fork
    
### ✅ Supported devices:
    Hub HWG023WBRF-V2
    Soil Sensors: HCS026FRF
    Air Sensors: HCS014ARF 
    Rain Sensors: HCS012ARF 
    4 Zone valve timer: HTV405FRF
### ✅ Added a debug logs including when a new device or not recognised device is detected
### ✅ 90% of the HEX received from the API is decoded
    The remaing 10% not very important like battery status, RSSI etc. to be decoded
### ✅ Fixed MQTT connection 
    

TODO:

Confirm that the MQTT is only for configuration changes.
I could not obtain a version to be able to receive the device / sensor update status from MQTT. This is done via 30 seconds HTTP POLL, but at least MQTT is stable.

As usual you need to create a second homgar user in the homgar app and add it as a memeber. Then use it for the HA integration as the API does not allow 2 connections from the single username at the sane time
