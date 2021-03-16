# ems-esp-domoticz-plugin Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## [1.4] 2021-03-16

### Fixed

Some solar parameters had the wrong ID.

## [1.3] 2020-11-25

Firmware of the Gateway needs to be at least 2.1<br>
This release is based on dev V1.3b6.

### Added

- Shower duration.
- New MQTT topic names for boiler_ww etc are added.
- Additional Solar parameters.
- Lots of other fixes and additions.

### Changed

- Thermostat devices are only created if they are actually in the payload.
- Thermostat modes were not updated because of the names with a capital letter.

## [1.2] 2020-10-12

Firmware of the Gateway needs to be at least 2.1<br>
This release is based on dev-2 V1.2b8.

### Added

- Added compatibility for firmware V2.1
- Lots of other fixes and additions.


## [1.0] 2020-02-12

Firmware of the Gateway needs to be at least 1.9.4. (1.9.5 is even better)<br>

### Changed

- Sensors are now only updated when the value has changed.

## [0.9] 2020-02-06

Firmware of the Gateway needs to be at least 1.9.4. (1.9.5 is even better)<br>

### Fixed

- The thermostat command topics were changed in EMS-ESP 1.9.4, this has now been fixed here as well.

## [0.8] 2020-01-27

Firmware of the Gateway needs to be at least 1.9.4.<br>

### Added

- Added a number of boiler parameters: 31:wWComfort, 25:wWSelTemp, 26:wWDesiredTemp, 27:heating_temp, 28:wWCircPump, 29:flameCurr, 38:pump_mod_max, 39:pump_mod_min, 32:wWStarts, 33:wWWorkM, 34:UBAuptime, 35:burnStarts, 36:burnWorkMin, 37:heatWorkMin.
- tapwater_active and heating_active parameters now work.
- Added mqtt authentication with user/pw (thanks @hlugt for pointing it out).

## [0.7] 2019-12-16

Firmware of the Gateway needs to be at least 1.9.4.<br>
Thermostat command topics have changed in EMS-ESP, the plugin is now compatible with those in 1.9.4.

### Added

- Support for all 4 heating circuits hc1 to hc4.
- Support for mixing modules on hc1 to hc4 (topic mixing_data).
  Domoticz devices for the mixing module are only generated if a first message in topic mixing_data is received,
  this only happens if a mixing module is detected on the EMS bus by the Gateway.
  (This check is done for each heating circuit).
- Support for solar modules (topic sm_data).
  Domoticz devices for the solar module are only generated if a first message in topic sm_data is received,
  this only happens if a solar module is detected on the EMS bus by the Gateway.
  (Only pump, modulation and temperature sensors are supported now).
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
