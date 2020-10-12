![license](https://img.shields.io/github/license/bbqkees/ems-esp-domoticz-plugin.svg) ![last-commit](https://img.shields.io/github/last-commit/bbqkees/ems-esp-domoticz-plugin?label=last%20commit%20in%20Master)
![last-commit-dev](https://img.shields.io/github/last-commit/bbqkees/ems-esp-domoticz-plugin/dev?label=last%20commit%20in%20DEV%20branch)
![last-commit-dev-2](https://img.shields.io/github/last-commit/bbqkees/ems-esp-domoticz-plugin/dev-2?label=last%20commit%20in%20DEV-2%20branch)

# ems-esp-domoticz-plugin
Domoticz plugin for the EMS Wi-Fi Gateway with Proddy's EMS-ESP firmware. 

## When do you need this?
If you are using the [EMS Wi-Fi Gateway](https://bbqkees-electronics.nl/) (or another setup with) with [Proddy's EMS-ESP firmware](https://github.com/proddy/EMS-ESP) in combination with Domoticz.<br><br>
<img src="https://bbqkees-electronics.nl/wp-content/uploads/2019/12/on-boiler.jpg" height="200">
<img src="https://bbqkees-electronics.nl/wp-content/uploads/2019/12/gateway-p2-kit.jpg" height="200">
<br><br>
The EMS-ESP firmware communicates via MQTT. Although MQTT is an open format, the required message contents is specific to each home automation system.<br>
The EMS-ESP firmware was intented for integration with Home Assistant (HA).<br>
To communicate with Domoticz you need this plugin that will listen to the topics the Gateway publishes and listens to.<br>
The plugin will basically translate the Home Assistant format to Domoticz format.<br>

## Compatibility
This version is compatible with EMS-ESP V2 and V2.1. I removed all specific support for 1.9.5 in the new plugin so you need to update the firmware of your Gateway (which you should do anyway because the V2 firmware is awesome!).<br>
If you are still on 1.9.5 see [the wiki](https://bbqkees-electronics.nl/wiki/gateway/firmware-update-to-v2.html) on how to safely update from 1.9.5 to 2.1.

# Installation and configuration

## Check if you have a MQTT broker/server
The Gateway communicates via MQTT. For this you need a MQTT broker/server installed on your machine. Usually this is [Mosquitto](http://mosquitto.org/).<br>
You can check if your machine has it installed by typing f.i. `mosquitto_pub` in a terminal.<br>
If it says 'command not found' you need to [install Mosquitto](https://www.sigmdel.ca/michel/ha/rpi/add_mqtt_en.html) first. If you get a list of option Mosquitto is installed and you can continue installing the plugin directly.<br>

## Installing the plugin
If you have Git installed (preferred method):<br>
Go to the domoticz/plugins directory and run `git clone https://github.com/bbqkees/ems-esp-domoticz-plugin.git`.<br>
<br>
Make sure that 'Accept new Hardware Devices' is enabled in settings/system. <br>
Now restart the domoticz service (by typing `sudo systemctl restart domoticz` in the shell).<br>
Create a new hardware of the type "EMS bus Wi-Fi Gateway" (Do not create a hardware of the type 'MQTT Client Gateway', this is something different). See the image below.<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/main/images/domoticz-plugin-selection.jpg" height="200"><br><br>
Set the MQTT server and port. Usually the MQTT server is running on the same machine as Domoticz. If so, you can leave the IP and port to its default setting.<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/main/images/domoticz-plugin-parameters.jpg" height="350"><br>

### Setting the correct topics
The plugin listens to the topics preceded by "ems-esp/".<br>
Also make sure you don't change the host name of the Gateway otherwise the topic will change as well!<br>
In the latest plugin version you can change the topic string to your own preference if needed.

### Set the right MQTT format
In the MQTT setting of the web interface set the MQTT format to 'nested'.
Otherwise the plugin won't work as intended.

## Using the plugin
The plugin subscribes and publishes to the default MQTT topics of the Gateway.<br>
The plugin captures the messages and updates the Domoticz devices and sensors automatically.<br>
On the first run the plugin will create several devices and sensors in Domoticz.<br>
Go to the 'Devices' tab in Domoticz and search for the devices that are created. You can now add each device to Domoticz by clicking on the small green arrow with 'Add Device'.<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/main/images/domoticz-plugin-devices.jpg" height="300">
<br>

## Updating the plugin
If you used the `git clone` command to initially install the plugin just type `git pull` when in the plugin folder.<br>
Now restart the domoticz service (by typing `sudo systemctl restart domoticz` in the shell).<br>
On first run of the plugin (takes a minute maybe) additional devices will be created automatically if they were not defined before. Existing devices will not change.<br>

## Issues
If you find a problem with the plugin, just open an issue here.<br>

## Credits
This plugin was based on the beta version version created by [Gert05](https://github.com/Gert05)
