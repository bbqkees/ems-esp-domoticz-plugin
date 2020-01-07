# ems-esp-domoticz-plugin dev branch Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.7b18] 2020-01-07

Firmware of the Gateway needs to be at least 1.9.3.

### Fixed

- Counters were of the wrong type. Used incremental counters at first.
  Remove the devices 32:wWStarts, 33:wWWorkM, 34:UBAuptime, 35:burnStarts, 36:burnWorkMin, 37:heatWorkMin.
  Then update the plugin and restart Domoticz.

## [0.7b17] 2020-01-07

Firmware of the Gateway needs to be at least 1.9.3.

### Added

- Added a number of boiler parameters:
31:wWComfort,
25:wWSelTemp,
26:wWDesiredTemp,
27:heating_temp,
28:wWCircPump,
29:flameCurr,
38:pump_mod_max,
39:pump_mod_min,
32:wWStarts,
33:wWWorkM,
34:UBAuptime,
35:burnStarts,
36:burnWorkMin,
37:heatWorkMin.


## [0.7b16] 2019-12-13

Firmware of the Gateway needs to be at least 1.9.3.

### Fixed

- Reverted thermostat temp and mode topics.

## [0.7b15] 2019-12-10

Firmware of the Gateway needs to be at least 1.9.3.

### Changed

- Changed the thermostat topics.

### Fixed

- Thermostat mode names set to be lower case for EMS-ESP.

## [0.7b14] 2019-12-05

Firmware of the Gateway needs to be at least 1.9.2.

### Added

- Support for mixing modules on hc1 to hc4 (topic mixing_data).
  Domoticz devices for the mixing module are only generated if a first message in topic mixing_data is received,
  this only happens if a mixing module is detected on the EMS bus by the Gateway.
  (This check is done for each heating zone separately.)
  
## [0.7b13] 2019-12-04

Firmware of the Gateway needs to be at least 1.9.2

### Added

- Support for solar modules (topic sm_data).
  Domoticz devices for the solar module are only generated if a first message in topic sm_data is received,
  this only happens if a solar module is detected on the EMS bus by the Gateway.
  (Only pump, modulation and temperature sensors are supported now)

### Changed

- Domoticz devices for the optional Dallas sensors (1 to 5) are now only generated if a first message in topic sensors is received,
  this only happens if such a sensor is detected on the EMS bus by the Gateway.

## [0.7b12] 2019-12-03

Firmware of the Gateway needs to be at least 1.9.2

### Added

- Support for heat pump (topic hp_data)

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
