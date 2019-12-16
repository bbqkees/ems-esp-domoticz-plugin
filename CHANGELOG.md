# ems-esp-domoticz-plugin Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [0.7] 2019-12-16

Firmware of the Gateway needs to be at least 1.9.4.
Thermostat command topics have changed in EMS-ESP, the plugin is now compatible with those in 1.9.4.

### Added

- Support for all 4 heating circuits hc1 to hc4.
- Support for mixing modules on hc1 to hc4 (topic mixing_data).
  Domoticz devices for the mixing module are only generated if a first message in topic mixing_data is received,
  this only happens if a mixing module is detected on the EMS bus by the Gateway.
  (This check is done for each heating zone
- Support for solar modules (topic sm_data).
  Domoticz devices for the solar module are only generated if a first message in topic sm_data is received,
  this only happens if a solar module is detected on the EMS bus by the Gateway.
  (Only pump, modulation and temperature sensors are supported now)
- Domoticz devices for the optional Dallas sensors (1 to 5) are now only generated if a first message in topic sensors is received,
  this only happens if such a sensor is detected on the EMS bus by the Gateway.
  
### Changed

- Boiler wwComfort device ID 17 is now a selector switch ID 30 instead of a text sensor

### Deprecated

- Thermostat settings for the 'old' non-hc thermostat with device ID 1 and 3.


## [0.6.1] 2019-11-17

In EMS-ESP firmware 1.9.2 the MQTT topics have changed.
This version of the plugin adds support for the new structure.
Firmware of the Gateway needs to be at least 1.9.2

### Added

- Initial support for heating circuit hc1


## [0.6] 2019-08-27

Initial plugin version for EMS-ESP firmware up to 1.9.1.
