# ems-esp-domoticz-plugin
Domoticz plugin for the EMS Wi-Fi Gateway with Proddy's EMS-ESP firmware. 

--You are now viewing the development branch 2.--<br>
Do not use this branch until further notice.



On first run the plugin will add a new thermostat device for all heating circuits hc1 to hc4. If you previously used the thermostat you now need to control it via the new Thermostat hc1. In some cases your thermostat is coupled to another heating circuit than hc1, in those cases you need to use the other hc.<br>
<br>
This version also supports 5 Dallas temperature sensors and several other new parameters.<br>
<br>
You need to run firmware 1.9.3 or later.<br>
<br>
See the [Changelog](https://github.com/bbqkees/ems-esp-domoticz-plugin/blob/dev/CHANGELOG.md) for more details.<br>
<br>
<br>
The easiest way to try out the dev branch when you already have the plugin installed is to view the plugin.py file here in raw mode, and copy and paste all contents into the existing plugin.py file on your home automation system. After that restart domoticz.
<br>

## When do you need this?
If you are using the [EMS Wi-Fi Gateway](https://bbqkees-electronics.nl/) (or another setup with) with [Proddy's EMS-ESP firmware](https://github.com/proddy/EMS-ESP) in combination with Domoticz.<br>
The EMS-ESP firmware communicates via MQTT. Although MQTT is an open format, the required message contents is specific to each home automation system.<br>
The EMS-ESP firmware was intented for integration with Home Assistant.<br>
To communicate with Domoticz you need this plugin that will listen to the topics the Gateway publishes and listens to.<br>
The plugin will translate the Home Assistant format to Domoticz format.<br>

## Installing the plugin (development version)
Stop the Domoticz service (by typing `sudo systemctl stop domoticz` in the shell).<br>
Now do one of the following actions:<br>
Create a new directory 'ems-gateway' in the folder domoticz/plugins.<br>
Copy the files mqtt.py and plugin.py to this new domoticz/plugins/ems-gateway directory.<br>
Or:<br>
Go to the domoticz/plugins directory and run `git clone -b dev https://github.com/bbqkees/ems-esp-domoticz-plugin.git`.<br>
<br>
Make sure that 'Accept new Hardware Devices' is enabled in settings/system. <br>
Now start the domoticz service (by typing `sudo systemctl start domoticz` in the shell).<br>
Create a new hardware of the type "EMS bus Wi-Fi Gateway".<br>
Set the MQTT server and port. Usually the MQTT server is running on the same machine as Domoticz. If so, you can leave the IP and port to its default setting.

## Switching from master to dev branch
Several ways to do this. easiest is from the Domoticz plugin folder `sudo rm -r ems-esp-domoticz-plugin` and then
`git clone -b dev https://github.com/bbqkees/ems-esp-domoticz-plugin.git`.

### Setting the correct topics
The plugin listens to the topics preceded by "home/ems-esp/". In the latest EMS-ESP firmware versions the default topic is "ems-esp". To change this go to the Gateway web interface and to the MQTT settings. Now set the Base parameter to "home".
You can also change it in the plugin.

## Using the plugin
On the first run the plugin will create several devices and sensors in Domoticz.<br>
The plugin then subscribes and publishes to the default MQTT topics of the Gateway.<br>
The plugin captures the messages and updates the Domoticz devices and sensors automatically.<br>

## Updating the plugin
To update the plugin, stop the Domoticz service (by typing `sudo systemctl stop domoticz` in the shell).<br>
Then copy the new plugin.py file to the plugin folder and overwrite the existing file.<br>
Or if you used the `git clone` command to initially install the plugin just run `git pull`<br>
Now start the domoticz service (by typing `sudo systemctl start domoticz` in the shell).<br>
On first run of the plugin additional devices will be created automatically. Existing devices will not change.<br>

## Issues
If you find a problem with the plugin, just open an issue here.<br>
As I do not have an EMS thermostat myself, I would like to know if this works as intended.

## To Do List
- See the readme on the master branch.

## Credits
This plugin was based on the beta version version created by [Gert05](https://github.com/Gert05)
