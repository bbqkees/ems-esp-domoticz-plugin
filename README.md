# ems-esp-domoticz-plugin
Domoticz plugin for the EMS Wi-Fi Gateway with Proddy's EMS-ESP firmware. 

--You are now viewing the development branch.--<br>

Make sure the firmware of the Gateway is V3 or higher.
You can find the latest beta software bin file here:
https://github.com/proddy/EMS-ESP32/blob/firmware/firmware/

And make sure MQTT format is set to 'nested' in the web interface!


## Installing the plugin (development version)
Go to the domoticz/plugins directory and run `git clone -b dev-multi https://github.com/bbqkees/ems-esp-domoticz-plugin.git`.<br>
<br>
Make sure that 'Accept new Hardware Devices' is enabled in settings/system. <br>
Now restart the domoticz service (by typing `sudo systemctl restart domoticz` in the shell).<br>
Create a new hardware of the type "EMS bus Wi-Fi Gateway DEV".<br>

## Switching from main to dev branch
Several ways to do this. easiest is from the Domoticz plugin folder `sudo rm -r ems-esp-domoticz-plugin` and then
`git clone -b dev-multi https://github.com/bbqkees/ems-esp-domoticz-plugin.git`.
