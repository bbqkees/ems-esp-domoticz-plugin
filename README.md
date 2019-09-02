# ems-esp-domoticz-plugin
Domoticz plugin for the EMS Wi-Fi Gateway with Proddy's EMS-ESP firmware. 

## When do you need this?
If you are using the [EMS Wi-Fi Gateway](https://shop.hotgoodies.nl/ems/) (or another setup with) with [Proddy's EMS-ESP firmware](https://github.com/proddy/EMS-ESP) in combination with Domoticz.<br>
The EMS-ESP firmware communicates via MQTT. Although MQTT is an open format, the required message contents is specific to each home automation system.<br>
The EMS-ESP firmware was intented for integration with Home Assistant.<br>
To communicate with Domoticz you need this plugin that will listen to the topics the Gateway publishes and listens to.<br>
The plugin will translate the Home Assistant format to Domoticz format.<br>

## Check if you have a MQTT broker/server
The Gateway communicates via MQTT. For this you need a MQTT broker installed on your machine. Usually this is [Mosquitto](http://mosquitto.org/).<br>
You can check if your machine has it installed by typing f.i. `mosquitto_pub` in a terminal.<br>
If it says 'command not found' you need to [install Mosquitto](https://www.sigmdel.ca/michel/ha/rpi/add_mqtt_en.html) first. If you get a list of option Mosquitto is installed and you can continue installing the plugin directly.<br>

## Installing the plugin
Stop the Domoticz service (by typing `sudo systemctl stop domoticz` in the shell).<br>
Now do one of the following actions:<br>
Create a new directory 'ems-gateway' in the folder domoticz/plugins.<br>
Copy the files mqtt.py and plugin.py to this new domoticz/plugins/ems-gateway directory.<br>
Or:<br>
Go to the domoticz/plugins directory and run `git clone https://github.com/bbqkees/ems-esp-domoticz-plugin.git`.<br>
<br>
Make sure that 'Accept new Hardware Devices' is enabled in settings/system. <br>
Now start the domoticz service (by typing `sudo systemctl start domoticz` in the shell).<br>
Create a new hardware of the type "EMS bus Wi-Fi Gateway" (Do not create a hardware of the type 'MQTT Client Gateway', this is something different).<br>
Set the MQTT server and port. Usually the MQTT server is running on the same machine as Domoticz. If so, you can leave the IP and port to its default setting.

### Setting the correct topics
The plugin listens to the topics preceded by "home/ems-esp/". In the latest EMS-ESP firmware versions the default topic is "ems-esp". To change this go to the Gateway web interface and to the MQTT settings. Now set the Base parameter to "home".<br>
<img src="https://raw.githubusercontent.com/bbqkees/ems-esp-domoticz-plugin/master/images/ems-esp-web-mqtt-base-setting.jpg" height="300">
<br>
Also make sure you don't change the host name of the Gateway otherwise the topic will change as well!

### Set the right MQTT update frequency
By default the Gateway will publish the set of MQTT messages every 120 seconds.<br>
For temperature and general logging this is a good update frequency. However, this is too slow if you also want to capture short events like turning on the warm water for 30 seconds.<br>
If needed you can change the frequency in the web interface in 'Custom Settings' -> 'Publish Time'. Don't set it too low as it will bombard Domoticz with messages.

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
- Add the solar/mixer module devices.
- Add support for the DS18B20 temperature sensors.

## Credits
This plugin was based on the beta version version created by [Gert05](https://github.com/Gert05)
