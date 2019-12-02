# ems-esp-domoticz-plugin dev branch Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),

## [0.7b11] 2019-12-02

Firmware of the Gateway needs to be at least 1.9.2
  
### Fixed

- Thermostat settings for hc1 to hc4 gave an error, this is now solved.
  (Setting the thermostat mode does not work yet.)
- Creation of Device ID 2 (sys pressure) was mistakenly commented out.

## [0.7b07] 2019-11-27

In ESM_ESP firmware 1.9.2 the MQTT topics have changed.
This version of the plugin adds support for the new structure.
Firmware of the Gateway needs to be at least 1.9.2

### Added

- Support for 5 Dallas (DS18B20) temperature sensors
- Initial support for all 4 heating circuits hc1 to hc4
- Added MQTT topics "sensors", "mixing_data", "sm_data" and "hp_data"

### Changed

- Boiler wwComfort device ID 17 is now a selector switch ID 30 instead of a text sensor

### Deprecated

- Thermostat settings for the 'old' non-hc thermostat with device ID 1 and 3.
