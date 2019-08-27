# ems-esp-domoticz-plugin
Domoticz plugin for the EMS Wi-Fi Gateway with Proddy's EMS-ESP firmware. 

## When do you need this?
If you are using the [EMS Wi-Fi Gateway](https://shop.hotgoodies.nl/ems/) (or another setup with) with [Proddy's EMS-ESP firmware](https://github.com/proddy/EMS-ESP) in combination with Domoticz.<br>
The EMS-ESP firmware communicates via MQTT. Although MQTT is an open format, the required message contents is specific to each home automation system.<br>
The EMS-ESP firmware was intented for integration with Home Assistant.<br>
To communicate with Domoticz you need this plugin that will listen to the topics the Gateway publishes and listens to.<br>
The plugin will translate the Home Assistant format to Domoticz format.<br>

## Installing the plugin
Stop the Domoticz service (by typing `sudo systemctl stop domoticz` in the shell).<br>
Copy the directory ems-gateway to the domoticz/plugins directory. Make sure that 'Accept new Hardware Devices' is enabled in settings/system. <br>
Now start the domoticz service (by typing `sudo systemctl start domoticz` in the shell).<br>
Create a new hardware of the type "EMS bus Wi-Fi Gateway".<br>
Set the MQTT server and port. Usually the MQTT server is running on the same machine as Domoticz. If so, you can leave the IP and port to its default setting.

### Setting the correct topics
The plugin listens to the topics preceded by "home/ems-esp/". In the latest EMS-ESP firmware versions the default topic is "ems-esp". To change this go to the Gateway web interface and to the MQTT settings. Now set the Base parameter to "home".

## Using the plugin
On the first run the plugin will create several devices and sensors in Domoticz.
The plugin then subscribes and publishes to the default MQTT topics of the Gateway.
The plugin captures the messages and updates the Domoticz devices and sensors automatically.

## Updating the plugin
To update the plugin, stop the Domoticz service (by typing `sudo systemctl stop domoticz` in the shell).
Then copy the plugin.py file to the plugin folder and overwrite the existing file.
Now start the domoticz service (by typing `sudo systemctl start domoticz` in the shell).
On first run of the plugin additional devices will be created automatically. Existing devices will not change.

## Issues
If you find a problem with the plugin, just open an issue here.<br>
As I do not have an EMS thermostat myself, I would like to know if this works as intended.

## To Do List
- Add the solar/mixer module devices.
- Add support for the DS18B20 temperature sensors.

## Credits
This plugin was based on the beta version version created by [Gert05](https://github.com/Gert05)
