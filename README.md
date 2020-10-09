![license](https://img.shields.io/github/license/bbqkees/ems-esp-domoticz-plugin.svg) ![last-commit](https://img.shields.io/github/last-commit/bbqkees/ems-esp-domoticz-plugin?label=last%20commit%20in%20Master)
![last-commit-dev](https://img.shields.io/github/last-commit/bbqkees/ems-esp-domoticz-plugin/dev?label=last%20commit%20in%20DEV%20branch)
![last-commit-dev-2](https://img.shields.io/github/last-commit/bbqkees/ems-esp-domoticz-plugin/dev-2?label=last%20commit%20in%20DEV-2%20branch)

# ems-esp-domoticz-plugin
Domoticz plugin for the EMS Wi-Fi Gateway with Proddy's EMS-ESP firmware. 

## When do you need this?
If you are using the [EMS Wi-Fi Gateway](https://bbqkees-electronics.nl/) (or another setup with) with [Proddy's EMS-ESP firmware](https://github.com/proddy/EMS-ESP) in combination with Domoticz.<br><br>
<img src="https://raw.githubusercontent.com/bbqkees/Nefit-Buderus-EMS-bus-Arduino-Domoticz/master/Documentation/nefit-ems-bus-interface-PCB.jpg" height="150">
<img src="https://shop.hotgoodies.nl/ems/ems-kit/on-boiler.jpg" height="150">
<img src="https://hotgoodies.nl/shop/ems/ems-kit/ems-kit-2.jpg" height="150">
<br><br>
The EMS-ESP firmware communicates via MQTT. Although MQTT is an open format, the required message contents is specific to each home automation system.<br>
The EMS-ESP firmware was intented for integration with Home Assistant (HA).<br>
To communicate with Domoticz you need this plugin that will listen to the topics the Gateway publishes and listens to.<br>
The plugin will basically translate the Home Assistant format to Domoticz format.<br>

## New version compatible with EMS-ESP V2 almost ready for release!
A new version of the plugin (already available in the dev-2 branch) will be released soon (mid-October 2020). This version will be compatible with EMS-ESP V2 and V2.1.
I removed all specific support for 1.9.5 in the new plugin so you need to update the firmware of your Gateway (which you should do anyway because the V2 firmware is awesome!).

## Compatibility
The plugin works with all versions of EMS-ESP. So the old versions with the Telnet interface are supported but also the new versions with the web interface (1.9.0 and onwards).<br>
However in firmware 1.9.2/1.9.3/1.9.4 the MQTT topics have changed though, you need to upgrade to 1.9.4 for full support.<br>
If you are on older firmware versions than 1.9.4  and are unable to upgrade, do not update the plugin as it will break compatibility with the thermostat.
<br>
In the [dev branch](https://github.com/bbqkees/ems-esp-domoticz-plugin/tree/dev) a test version is also available with more additions and fixes.<br><br>
If you have a Gateway with old Telnet-only firmware or you are otherwise unable to upgrade the firmware of the Gateway, I can send you a new Wemos with soldered headers loaded with the latest firmware with web interface, so you can do future firmware updates yourself. This is a drop-in replacement. Send me an email for more information if you need this.<br><br>

## Compatibility with EMS-ESP 2.0
The current plugin works fine with at least 2.0b3. In 2.0 the MQTT topic base is now just 'ems-esp' so you have to change this in the plugin settings as well. By default this is 'home/ems-esp' in 1.9.5.<br>
In 2.0.1 the MQTT command structure has changed significantly. I did not have time yet to make all the appropriate changes.
Reading values will still work, however changing the setpoint on the thermostat will not work.
So hang on for a while until I have this ready.

## Known issues

### ! Issue with latest Domoticz beta versions !
In some cases, for the latest Domoticz beta versions (2020 versions) while on Debian Buster, when activating the plugin the entire device list in Domoticz gets empty.
Or it becomes empty after adding more than 8 devices from the plugin. I have not found out yet why this happens.
If you are running a stable version the problem does not occur, so please use the latest stable release.

### Thermostats are not updated with firmware version 1.9.5

In the latest firmware version 1.9.5 the MQTT topics are not 'nested' by default.
If you have updated from an older firmware version you will be fine but if you got a new Gateway with 1.9.5 you need to login via Telnet to the Gateway and execute the fommowing command:
`set mqtt_nestedjson on` 

# Installation and configuration

## Check if you have a MQTT broker/server
The Gateway communicates via MQTT. For this you need a MQTT broker/server installed on your machine. Usually this is [Mosquitto](http://mosquitto.org/).<br>
You can check if your machine has it installed by typing f.i. `mosquitto_pub` in a terminal.<br>
If it says 'command not found' you need to [install Mosquitto](https://www.sigmdel.ca/michel/ha/rpi/add_mqtt_en.html) first. If you get a list of option Mosquitto is installed and you can continue installing the plugin directly.<br>

## Installing the plugin
Stop the Domoticz service (by typing `sudo systemctl stop domoticz` in the shell). Actually stopping the service is not really necessary but it doesn't hurt.<br><br>
Now do one of the following actions:<br>
If you have Git installed (preferred method):<br>
Go to the domoticz/plugins directory and run `git clone https://github.com/bbqkees/ems-esp-domoticz-plugin.git`.<br>
<br>
Or as an alternative you can do the following:<br>
Create a new directory 'ems-gateway' in the folder domoticz/plugins.<br>
Copy the files mqtt.py and plugin.py to this new domoticz/plugins/ems-gateway directory.<br>
<br>
Make sure that 'Accept new Hardware Devices' is enabled in settings/system. <br>
Now start the domoticz service (by typing `sudo systemctl start domoticz` in the shell).<br>
Create a new hardware of the type "EMS bus Wi-Fi Gateway" (Do not create a hardware of the type 'MQTT Client Gateway', this is something different). See the image below.<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/master/images/domoticz-plugin-selection.jpg" height="200"><br><br>
Set the MQTT server and port. Usually the MQTT server is running on the same machine as Domoticz. If so, you can leave the IP and port to its default setting.<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/master/images/domoticz-plugin-parameters.jpg" height="350"><br>

### Setting the correct topics
The plugin listens to the topics preceded by "home/ems-esp/". In the latest EMS-ESP firmware versions the default topic is just "ems-esp". To change this go to the Gateway web interface and to the MQTT settings. Now set the Base parameter to "home".<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/master/images/ems-esp-web-mqtt-base-setting.jpg" height="300">
<br>
Also make sure you don't change the host name of the Gateway otherwise the topic will change as well!<br>
In the latest plugin version you can change the topic string to your own preference.

### Set the right MQTT update frequency
By default the Gateway will publish the set of MQTT messages every 120 seconds.<br>
For temperature and general logging this is a good update frequency. However, this is too slow if you also want to capture short events like turning on the warm water for 30 seconds.<br>
If needed you can change the frequency in the web interface in 'Custom Settings' -> 'Publish Time'. Don't set it too low as it will bombard Domoticz with messages.

## Using the plugin
On the first run the plugin will create several devices and sensors in Domoticz.<br>
The plugin then subscribes and publishes to the default MQTT topics of the Gateway.<br>
The plugin captures the messages and updates the Domoticz devices and sensors automatically.<br>
Go to the 'Devices' tab in Domoticz and search for the devices that are created. You can now add each device to Domoticz by clicking on the small green arrow with 'Add Device'.<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/master/images/domoticz-plugin-devices.jpg" height="300">
<br>

## Updating the plugin
To update the plugin, stop the Domoticz service (by typing `sudo systemctl stop domoticz` in the shell).<br>
Then copy the new plugin.py file to the plugin folder and overwrite the existing file.<br>
Or if you used the `git clone` command to initially install the plugin just type `git pull` when in the plugin folder.<br>
Now start the domoticz service (by typing `sudo systemctl start domoticz` in the shell).<br>
On first run of the plugin (takes a minute maybe) additional devices will be created automatically if they were not defined before. Existing devices will not change.<br>

## Issues
If you find a problem with the plugin, just open an issue here.<br>
As I do not have an EMS thermostat myself, I would like to know if this works as intended.

## To Do List

- Add the additional topics for controlling thermostat night/day settings.
- Shower stats
- Heartbeat check (MQTT availability as a sensor)
- Add commands for setting boiler comfort parameters and ww temperature and setting.

## Credits
This plugin was based on the beta version version created by [Gert05](https://github.com/Gert05)
