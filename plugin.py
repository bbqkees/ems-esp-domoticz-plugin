# Domoticz Python Plugin for EMS bus Wi-Fi Gateway with Proddy's EMS-ESP firmware
# last update: 18 February 2020
# Author: bbqkees @www.bbqkees-electronics.nl
# Credits to @Gert05 for creating the first version of this plugin
# https://github.com/bbqkees/ems-esp-domoticz-plugin
# Proddy's EMS-ESP repository: https://github.com/proddy/EMS-ESP
# Product Wiki: https://bbqkees-electronics.nl/wiki/
#
# This is the development and debug version. Use the master version for production.
#
"""
<plugin key="ems-gateway" name="EMS bus Wi-Fi Gateway" version="1.0b2">
    <description>
      Plugin to interface with EMS bus equipped Bosch brands boilers together with the EMS-ESP firmware '<a href="https://github.com/proddy/EMS-ESP"> from Proddy</a>'<br/>
      <br/>
      Please look at the <a href="https://bbqkees-electronics.nl/wiki/">Product Wiki</a> for all instructions.<br/>
      <i>Please update the firmware of the Gateway to 1.9.4 or higher for best functionality.</i><br/>
      As of firmware 1.9.2 the plugin supports 4 heating zones (HC1 to HC4). If you only have one thermostat/zone, the Gateway usually listens to zone 1.<br/>
      Automatically creates Domoticz devices for connected EMS devices.<br/> Do not forget to "Accept new Hardware Devices" on first run<br/>
    <br/>
    Parameters:<br/>
    <b>MQTT server and port</b><br/>
    MQTT Server address is usually, but not always, at the same address as the machine where Domoticz is running. So the 'local' machine at 127.0.0.1.<br/>
    The default port is 1883 and no user or password.<br/>
    <b>MQTT topic</b><br/>
    The default MQTT topic folder this plugin will look in is 'home/ems-esp/'.<br/>
    Make sure that this is set accordingly in the EMS-ESP firmware settings. In the latest versions the default topic is just ems-esp.<br/>
    You can change it here or in the Gateway web interface if its set differently.<br/>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="Username" width="300px"/>
        <param field="Password" label="Password" width="300px" default="" password="true"/>
        <param field="Mode1" label="Topic base" width="300px" required="true" default="home/ems-esp/"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Extra verbose" value="Verbose+"/>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

# Plugin Device ID numbering scheme:
# Bit inconvenient but Domoticz limts the ID's to max 255 for Python plugins.
#
# Boiler data (topic boiler_data):
# ID 1 to 39
#
# Shower data (topic shower_data):
# ID 60 to 69
#
# Tapwater/heating,Gateway etc on/off (topics tapwater_active and heating_active):
# ID 70 to 79
# 
# Solar module data (topic sm_data):
# ID 80 to 99
#
# Thermostats for heating zones (topic thermostat_data):
# ID 110 to 119 : heating zone 1
# ID 120 to 129 : heating zone 2
# ID 130 to 139 : heating zone 3
# ID 140 to 149 : heating zone 4
#
# Mixer modules for heating zones (topic mixing_data):
# ID 150 to 159 : heating zone 1
# ID 160 to 169 : heating zone 2
# ID 170 to 179 : heating zone 3
# ID 180 to 189 : heating zone 4 
#
# Heat pump parameters (topic hp_data):
# ID 200 to 209
#
# Dallas temperature sensors (topic sensors):
# ID 220 to 239
# 
# Other parameters:
# ID 240 to 249
# 
# 


import Domoticz
import json
import time
from mqtt import MqttClient


class EmsDevices:

    def checkDevices(self):
        # These are some old parameters from the old plugin
        # if 1 not in Devices:
            # Domoticz.Debug("Create Temperature Device")
            # Domoticz.Device(Name="EMS thermostat current temp", Unit=1, Type=80, Subtype=5).Create()
        if 2 not in Devices:
            Domoticz.Debug("Create System Pressure Device")
            Domoticz.Device(Name="Boiler system pressure", Unit=2, Type=243, Subtype=9).Create()
        # if 3 not in Devices:
            # Domoticz.Debug("Create Thermostat Setpoint Device")
            # Domoticz.Device(Name="EMS thermostat setpoint", Unit=3, Type=242, Subtype=1).Create()

        if 4 not in Devices:
            Domoticz.Debug("Create on/off switch (burnGas)")
            Domoticz.Device(Name="Boiler gas", Unit=4, Type=244, Subtype=73, Switchtype=0).Create()
        if 5 not in Devices:
            Domoticz.Debug("Create on/off switch (fanWork)")
            Domoticz.Device(Name="Boiler fan", Unit=5, Type=244, Subtype=73, Switchtype=0).Create()
        if 6 not in Devices:
            Domoticz.Debug("Create on/off switch (ignWork)")
            Domoticz.Device(Name="Boiler ingnition", Unit=6, Type=244, Subtype=73, Switchtype=0).Create()
        if 7 not in Devices:
            Domoticz.Debug("Create on/off switch (heatPmp)")
            Domoticz.Device(Name="Boiler heating pump", Unit=7, Type=244, Subtype=73, Switchtype=0).Create()
        if 8 not in Devices:
            Domoticz.Debug("Create on/off switch (wWActivated)")
            Domoticz.Device(Name="Boiler warm water", Unit=8, Type=244, Subtype=73, Switchtype=0).Create()
        if 9 not in Devices:
            Domoticz.Debug("Create on/off switch (wWHeat)")
            Domoticz.Device(Name="Boiler warm water heating", Unit=9, Type=244, Subtype=73, Switchtype=0).Create()
        if 10 not in Devices:
            Domoticz.Debug("Create on/off switch (wWCirc)")
            Domoticz.Device(Name="Boiler warm water circulation", Unit=10, Type=244, Subtype=73, Switchtype=0).Create()
        if 11 not in Devices:
            Domoticz.Debug("Create temperature device (selFlowTemp)")
            Domoticz.Device(Name="Boiler selected flow temperature", Unit=11, Type=80, Subtype=5).Create()
        if 12 not in Devices:
            Domoticz.Debug("Create temperature device (outdoorTemp)")
            Domoticz.Device(Name="Boiler connected outdoor temperature", Unit=12, Type=80, Subtype=5).Create()
        if 13 not in Devices:
            Domoticz.Debug("Create temperature device (wWCurTmp)")
            Domoticz.Device(Name="Boiler warm water current temperature", Unit=13, Type=80, Subtype=5).Create()
        if 14 not in Devices:
            Domoticz.Debug("Create temperature device (curFlowTemp)")
            Domoticz.Device(Name="Boiler current flow temperature", Unit=14, Type=80, Subtype=5).Create()
        if 15 not in Devices:
            Domoticz.Debug("Create temperature device (retTemp)")
            Domoticz.Device(Name="Boiler return temperature", Unit=15, Type=80, Subtype=5).Create()
        if 16 not in Devices:
            Domoticz.Debug("Create temperature device (boilTemp)")
            Domoticz.Device(Name="Boiler temperature", Unit=16, Type=80, Subtype=5).Create()
        if 25 not in Devices:
            Domoticz.Debug("Create temperature device (wWSelTemp)")
            Domoticz.Device(Name="ww selected temperature", Unit=25, Type=80, Subtype=5).Create()
        if 26 not in Devices:
            Domoticz.Debug("Create temperature device (wWDesiredTemp)")
            Domoticz.Device(Name="ww desired temperature", Unit=26, Type=80, Subtype=5).Create()
        if 27 not in Devices:
            Domoticz.Debug("Create temperature device (heating_temp)")
            Domoticz.Device(Name="Heating temperature", Unit=27, Type=80, Subtype=5).Create()
        # Old parameter
        # if 17 not in Devices:
            # Domoticz.Debug("Create text device (wWComfort)")
            # Domoticz.Device(Name="Boiler warm water comfort setting", Unit=17, Type=243, Subtype=19).Create()
        if 18 not in Devices:
            Domoticz.Debug("Create text device (ServiceCode)")
            Domoticz.Device(Name="Boiler Service code", Unit=18, Type=243, Subtype=19).Create()
        if 19 not in Devices:
            Domoticz.Debug("Create text device (ServiceCodeNumber)")
            Domoticz.Device(Name="Boiler Service code number", Unit=19, Type=243, Subtype=19).Create()
        # Old parameter
        # if 20 not in Devices:
            # Domoticz.Debug("Create text device (THERMOSTAT_MODE)")
            # Domoticz.Device(Name="EMS thermostat mode", Unit=20, Type=243, Subtype=19).Create()
        if 21 not in Devices:
            Domoticz.Debug("Create percentage device (selBurnPow)")
            Domoticz.Device(Name="Boiler selected power", Unit=21, Type=243, Subtype=6).Create()
        if 22 not in Devices:
            Domoticz.Debug("Create percentage device (curBurnPow)")
            Domoticz.Device(Name="Boiler current power", Unit=22, Type=243, Subtype=6).Create()
        if 23 not in Devices:
            Domoticz.Debug("Create percentage device (pumpMod)")
            Domoticz.Device(Name="Boiler pump modulation", Unit=23, Type=243, Subtype=6).Create()
        if 24 not in Devices:
            Domoticz.Debug("Create percentage device (wWCurFlow)")
            Domoticz.Device(Name="Boiler warm water flow", Unit=24, Type=243, Subtype=6).Create()
        if 28 not in Devices:
            Domoticz.Debug("Create percentage device (wWCircPump)")
            Domoticz.Device(Name="ww pump modulation", Unit=28, Type=243, Subtype=6).Create()
        if 38 not in Devices:
            Domoticz.Debug("Create percentage device (pump_mod_max)")
            Domoticz.Device(Name="pump modulation max", Unit=38, Type=243, Subtype=6).Create()
        if 39 not in Devices:
            Domoticz.Debug("Create percentage device (pump_mod_min)")
            Domoticz.Device(Name="pump modulation min", Unit=39, Type=243, Subtype=6).Create()
        # Current meter (called Ampere in Domoticz)
        if 29 not in Devices:
            Domoticz.Debug("Create ampere device (flameCurr)")
            Domoticz.Device(Name="Boiler flame current", Unit=29, Type=243, Subtype=23).Create()

        # Counters
        if 32 not in Devices:
            Domoticz.Debug("Create counter (wWStarts)")
            Domoticz.Device(Name="ww starts", Unit=32, Type=113, Subtype=0).Create()
        if 33 not in Devices:
            Domoticz.Debug("Create counter (wWWorkM)")
            Domoticz.Device(Name="ww work minutes", Unit=33, Type=113, Subtype=0).Create()
        if 34 not in Devices:
            Domoticz.Debug("Create counter (UBAuptime)")
            Domoticz.Device(Name="Boiler UBA uptime", Unit=34, Type=113, Subtype=0).Create()
        if 35 not in Devices:
            Domoticz.Debug("Create counter (burnStarts)")
            Domoticz.Device(Name="boiler burner starts", Unit=35, Type=113, Subtype=0).Create()
        if 36 not in Devices:
            Domoticz.Debug("Create counter (burnWorkMin)")
            Domoticz.Device(Name="boiler burner working minutes", Unit=36, Type=113, Subtype=0).Create()
        if 37 not in Devices:
            Domoticz.Debug("Create counter (heatWorkMin)")
            Domoticz.Device(Name="boiler heating working minutes", Unit=37, Type=113, Subtype=0).Create()

        # Temperature/room sensors of thermostats for each heating zone
        if 111 not in Devices:
            Domoticz.Debug("Create Temperature Device HC1")
            Domoticz.Device(Name="EMS thermostat current temp HC1", Unit=111, Type=80, Subtype=5).Create()
        if 121 not in Devices:
            Domoticz.Debug("Create Temperature Device HC2")
            Domoticz.Device(Name="EMS thermostat current temp HC2", Unit=121, Type=80, Subtype=5).Create()
        if 131 not in Devices:
            Domoticz.Debug("Create Temperature Device HC3")
            Domoticz.Device(Name="EMS thermostat current temp HC3", Unit=131, Type=80, Subtype=5).Create()
        if 141 not in Devices:
            Domoticz.Debug("Create Temperature Device HC4")
            Domoticz.Device(Name="EMS thermostat current temp HC4", Unit=141, Type=80, Subtype=5).Create()

        # Thermostat setpoints for each heating zone
        if 112 not in Devices:
            Domoticz.Debug("Create Thermostat Setpoint Device HC1")
            Domoticz.Device(Name="EMS thermostat setpoint HC1", Unit=112, Type=242, Subtype=1).Create()
        if 122 not in Devices:
            Domoticz.Debug("Create Thermostat Setpoint Device HC2")
            Domoticz.Device(Name="EMS thermostat setpoint HC2", Unit=122, Type=242, Subtype=1).Create()
        if 132 not in Devices:
            Domoticz.Debug("Create Thermostat Setpoint Device HC3")
            Domoticz.Device(Name="EMS thermostat setpoint HC3", Unit=132, Type=242, Subtype=1).Create()
        if 142 not in Devices:
            Domoticz.Debug("Create Thermostat Setpoint Device HC4")
            Domoticz.Device(Name="EMS thermostat setpoint HC4", Unit=142, Type=242, Subtype=1).Create()

        # For thermostat modes create a selector switch for each heating zone
        if 113 not in Devices:
            Domoticz.Debug("Create Thermostat mode selector HC1")
            Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                    }
            Domoticz.Device(Name="Thermostat mode HC1", Unit=113, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
        if 123 not in Devices:
            Domoticz.Debug("Create Thermostat mode selector HC2")
            Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                    }
            Domoticz.Device(Name="Thermostat mode HC2", Unit=123, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
        if 133 not in Devices:
            Domoticz.Debug("Create Thermostat mode selector HC3")
            Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                    }
            Domoticz.Device(Name="Thermostat mode HC3", Unit=133, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
        if 143 not in Devices:
            Domoticz.Debug("Create Thermostat mode selector HC4")
            Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                    }
            Domoticz.Device(Name="Thermostat mode HC4", Unit=143, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
            
        # Create selector switch for boiler modes
        if 30 not in Devices:
            Domoticz.Debug("Create boiler mode selector")
            Options = { "LevelActions" : "||",
                        "LevelNames"   : "Hot|Comfort|Intelligent",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                }
            Domoticz.Device(Name="Boiler mode", Unit=30, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
        # Create selector switch for ww modes
        if 31 not in Devices:
            Domoticz.Debug("Create ww mode selector")
            Options = { "LevelActions" : "||",
                        "LevelNames"   : "Hot|Eco|Intelligent",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                }
            Domoticz.Device(Name="ww mode", Unit=31, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()

        # Create switches for tapwater and heating active etc
        if 71 not in Devices:
            Domoticz.Debug("Create on/off switch (tapwater active)")
            Domoticz.Device(Name="Tapwater active", Unit=71, Type=244, Subtype=73, Switchtype=0).Create()
        if 72 not in Devices:
            Domoticz.Debug("Create on/off switch (heating active)")
            Domoticz.Device(Name="Heating active", Unit=72, Type=244, Subtype=73, Switchtype=0).Create()
        if 73 not in Devices:
            Domoticz.Debug("Create on/off switch (Gateway online/offline)")
            Domoticz.Device(Name="Gateway online", Unit=73, Type=244, Subtype=73, Switchtype=0).Create()

    # onMqttMessage decodes the MQTT messages and updates the Domoticz parameters
    def onMqttMessage(self, topic, payload):

        # Process the tapwater_active topic. Note the contents a single boolean (0 or 1) and not json.
        if "tapwater_active" in topic:
            if payload == 0:
                Devices[71].Update(nValue=0,sValue="off")
            if payload == 1:
                Devices[71].Update(nValue=1,sValue="on")

        # Process the heating_active topic. Note the contents a single boolean (0 or 1) and not json.
        if "heating_active" in topic:
            if payload == 0:
                Devices[72].Update(nValue=0,sValue="off")
            if payload == 1:
                Devices[72].Update(nValue=1,sValue="on")

        # Process the start topic. Note the contents a single word and not json. Does not work yet
#        if "start" in topic:
#            Domoticz.Debug("start topic received")    
            # if payload == "offline":
            #     Devices[73].Update(nValue=0,sValue="off")
            # if payload == "online":
            #     Devices[73].Update(nValue=1,sValue="on")

        # Process the thermostat parameters of each heating zone
        # Because there are other topics who have 'hc1' etc in the payload, check first
        # if its thermostat_data topic.
        # ToDo: Setting the thermostat mode doesn't work yet.
        if "thermostat_data" in topic:
            if "hc1" in payload:
                payloadHc1 = payload["hc1"]
                if "currtemp" in payloadHc1:
                    temp=round(float(payloadHc1["currtemp"]), 1)
                    Domoticz.Debug("thermostat_currtemp HC1: Current temp: {}".format(temp))
                    if Devices[111].sValue != temp:
                            Devices[111].Update(nValue=1, sValue=str(temp))
                if "seltemp" in payloadHc1:
                    temp=payloadHc1["seltemp"]
                    Domoticz.Debug("thermostat_seltemp HC1: Temp setting: {}".format(temp))
                    if Devices[112].sValue != temp:
                         Devices[112].Update(nValue=1, sValue=str(temp))
                if "mode" in payloadHc1:
                    thMode=payloadHc1["mode"]
                    Domoticz.Debug("Thermostat HC1: Mode is: "+str(thMode))
                    setSelectorByName(113, str(thMode))
            if "hc2" in payload:
                payloadHc2 = payload["hc2"]
                if "currtemp" in payloadHc2:
                    temp=round(float(payloadHc2["currtemp"]), 1)
                    Domoticz.Debug("thermostat_currtemp HC2: Current temp: {}".format(temp))
                    if Devices[121].sValue != temp:
                            Devices[121].Update(nValue=1, sValue=str(temp))
                if "seltemp" in payloadHc2:
                    temp=payloadHc2["seltemp"]
                    Domoticz.Debug("thermostat_seltemp HC2: Temp setting: {}".format(temp))
                    if Devices[122].sValue != temp:
                         Devices[122].Update(nValue=1, sValue=str(temp))
                if "mode" in payloadHc2:
                    thMode=payloadHc2["mode"]
                    Domoticz.Debug("Thermostat HC2: Mode is: "+str(thMode))
                    setSelectorByName(123, str(thMode))
            if "hc3" in payload:
                payloadHc3 = payload["hc3"]
                if "currtemp" in payloadHc3:
                    temp=round(float(payloadHc3["currtemp"]), 1)
                    Domoticz.Debug("thermostat_currtemp HC3: Current temp: {}".format(temp))
                    if Devices[131].sValue != temp:
                            Devices[131].Update(nValue=1, sValue=str(temp))
                if "seltemp" in payloadHc3:
                    temp=payloadHc3["seltemp"]
                    Domoticz.Debug("thermostat_seltemp HC3: Temp setting: {}".format(temp))
                    if Devices[132].sValue != temp:
                         Devices[132].Update(nValue=1, sValue=str(temp))
                if "mode" in payloadHc3:
                    thMode=payloadHc3["mode"]
                    Domoticz.Debug("Thermostat HC3: Mode is: "+str(thMode))
                    setSelectorByName(133, str(thMode))
            if "hc4" in payload:
                payloadHc4 = payload["hc4"]
                if "currtemp" in payloadHc1:
                    temp=round(float(payloadHc4["currtemp"]), 1)
                    Domoticz.Debug("thermostat_currtemp HC4: Current temp: {}".format(temp))
                    if Devices[141].sValue != temp:
                            Devices[141].Update(nValue=1, sValue=str(temp))
                if "seltemp" in payloadHc4:
                    temp=payloadHc4["seltemp"]
                    Domoticz.Debug("thermostat_seltemp HC4: Temp setting: {}".format(temp))
                    if Devices[142].sValue != temp:
                         Devices[142].Update(nValue=1, sValue=str(temp))
                if "mode" in payloadHc4:
                    thMode=payloadHc4["mode"]
                    Domoticz.Debug("Thermostat HC4: Mode is: "+str(thMode))
                    setSelectorByName(143, str(thMode))

        if "boiler_data" in topic:
            # Process the boiler parameters
            if "sysPress" in payload:
                pressure=payload["sysPress"]
                Domoticz.Debug("sysPress: Pressure: {}".format(pressure))
                if Devices[2].sValue != pressure:
                    Devices[2].Update(nValue=1, sValue=str(pressure))
            #11 to 16 + 25 to 27 temp
            if "selFlowTemp" in payload:
                temp=round(float(payload["selFlowTemp"]), 1)
                Domoticz.Debug("selFlowTemp: Current temp: {}".format(temp))
                if Devices[11].sValue != temp:
                    Devices[11].Update(nValue=1, sValue=str(temp))
            if "outdoorTemp" in payload:
                temp=round(float(payload["outdoorTemp"]), 1)
                Domoticz.Debug("outdoorTemp: Current temp: {}".format(temp))
                if Devices[12].sValue != temp:
                    Devices[12].Update(nValue=1, sValue=str(temp))
            if "wWCurTmp" in payload:
                temp=round(float(payload["wWCurTmp"]), 1)
                Domoticz.Debug("wWCurTmp: Current temp: {}".format(temp))
                if Devices[13].sValue != temp:
                    Devices[13].Update(nValue=1, sValue=str(temp))
            if "curFlowTemp" in payload:
                temp=round(float(payload["curFlowTemp"]), 1)
                Domoticz.Debug("curFlowTemp: Current temp: {}".format(temp))
                if Devices[14].sValue != temp:
                    Devices[14].Update(nValue=1, sValue=str(temp))
            if "retTemp" in payload:
                temp=round(float(payload["retTemp"]), 1)
                Domoticz.Debug("retTemp: Current temp: {}".format(temp))
                if Devices[15].sValue != temp:
                    Devices[15].Update(nValue=1, sValue=str(temp))
            if "boilTemp" in payload:
                temp=round(float(payload["boilTemp"]), 1)
                Domoticz.Debug("boilTemp: Current temp: {}".format(temp))
                if Devices[16].sValue != temp:
                    Devices[16].Update(nValue=1, sValue=str(temp))
            if "wWSelTemp" in payload:
                temp=round(float(payload["wWSelTemp"]), 1)
                Domoticz.Debug("wWSelTemp: Current temp: {}".format(temp))
                if Devices[25].sValue != temp:
                    Devices[25].Update(nValue=1, sValue=str(temp))
            if "wWDesiredTemp" in payload:
                temp=round(float(payload["wWDesiredTemp"]), 1)
                Domoticz.Debug("wWDesiredTemp: Current temp: {}".format(temp))
                if Devices[26].sValue != temp:
                    Devices[26].Update(nValue=1, sValue=str(temp))
            if "heating_temp" in payload:
                temp=round(float(payload["heating_temp"]), 1)
                Domoticz.Debug("heating_temp: Current temp: {}".format(temp))
                if Devices[27].sValue != temp:
                    Devices[27].Update(nValue=1, sValue=str(temp))
            # 29 ampere
            if "flameCurr" in payload:
                temp=round(float(payload["flameCurr"]), 1)
                Domoticz.Debug("flameCurr: {}".format(temp))
                if Devices[29].sValue != temp:
                    Devices[29].Update(nValue=1, sValue=str(temp))
            #21 to 24 + 28 + 38 + 39 percentage
            if "selBurnPow" in payload:
                percentage=payload["selBurnPow"]
                Domoticz.Debug("selBurnPow: Percentage: {}".format(percentage))
                if Devices[21].sValue != percentage:
                    Devices[21].Update(nValue=1, sValue=str(percentage))
            if "curBurnPow" in payload:
                percentage=payload["curBurnPow"]
                Domoticz.Debug("curBurnPow: Percentage: {}".format(percentage))
                if Devices[22].sValue != percentage:
                    Devices[22].Update(nValue=1, sValue=str(percentage))
            if "pumpMod" in payload:
                percentage=payload["pumpMod"]
                Domoticz.Debug("pumpMod: Percentage: {}".format(percentage))
                if Devices[23].sValue != percentage:
                    Devices[23].Update(nValue=1, sValue=str(percentage))
            if "wWCurFlow" in payload:
                percentage=payload["wWCurFlow"]
                Domoticz.Debug("wWCurFlow: Percentage: {}".format(percentage))
                if Devices[24].sValue != percentage:
                    Devices[24].Update(nValue=1, sValue=str(percentage))
            if "wWCircPump" in payload:
                percentage=payload["wWCircPump"]
                Domoticz.Debug("wWCircPump: Percentage: {}".format(percentage))
                if Devices[28].sValue != percentage:
                    Devices[28].Update(nValue=1, sValue=str(percentage))
            if "pump_mod_max" in payload:
                percentage=payload["pump_mod_max"]
                Domoticz.Debug("pump_mod_max: Percentage: {}".format(percentage))
                if Devices[38].sValue != percentage:
                    Devices[38].Update(nValue=1, sValue=str(percentage))
            if "pump_mod_min" in payload:
                percentage=payload["pump_mod_min"]
                Domoticz.Debug("pump_mod_min: Percentage: {}".format(percentage))
                if Devices[39].sValue != percentage:
                    Devices[39].Update(nValue=1, sValue=str(percentage))
            #4 to 10 switch
            if "burnGas" in payload:
                switchstate=payload["burnGas"]
                Domoticz.Debug("burnGas: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[4].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[4].Update(nValue=0,sValue="off")
            if "fanWork" in payload:
                switchstate=payload["fanWork"]
                Domoticz.Debug("fanWork: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[5].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[5].Update(nValue=0,sValue="off")
            if "ignWork" in payload:
                switchstate=payload["ignWork"]
                Domoticz.Debug("ignWork: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[6].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[6].Update(nValue=0,sValue="off")
            if "heatPmp" in payload:
                switchstate=payload["heatPmp"]
                Domoticz.Debug("heatPmp: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[7].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[7].Update(nValue=0,sValue="off")
            if "wWActivated" in payload:
                switchstate=payload["wWActivated"]
                Domoticz.Debug("wWActivated: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[8].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[8].Update(nValue=0,sValue="off")
            if "wWHeat" in payload:
                switchstate=payload["wWHeat"]
                Domoticz.Debug("wWHeat: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[9].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[9].Update(nValue=0,sValue="off")
            if "wWCirc" in payload:
                switchstate=payload["wWCirc"]
                Domoticz.Debug("wWCirc: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[10].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[10].Update(nValue=0,sValue="off")
            #17 to 20 text
            # Old parameter
            # if "wWComfort" in payload:
                # text=payload["wWComfort"]
                # Domoticz.Debug("wWComfort: Text: {}".format(text))
                # Devices[17].Update(nValue=1, sValue=str(text))
            # new parameter (doesn't work yet)
            # if "wWComfort" in payload:
                # mode=payload["wWComfort"]
                # Domoticz.Debug("wWComfort: Text: {}".format(mode))
                # setSelectorByName(30, str(mode["wWComfort"]))
            if "ServiceCode" in payload:
                text=payload["ServiceCode"]
                Domoticz.Debug("ServiceCode: Text: {}".format(text))
                Devices[18].Update(nValue=1, sValue=str(text)) 
            if "ServiceCodeNumber" in payload:
                text=payload["ServiceCodeNumber"]
                Domoticz.Debug("ServiceCodeNumber: Text: {}".format(text))
                Devices[19].Update(nValue=1, sValue=str(text))
            # Parameter of old plugin
            # if "THERMOSTAT_MODE" in payload:
                # text=payload["THERMOSTAT_MODE"]
                # Domoticz.Debug("THERMOSTAT_MODE: Text: {}".format(text))
                # Devices[20].Update(nValue=1, sValue=str(text))
            if "wWStarts" in payload:
                text=payload["wWStarts"]
                Domoticz.Debug("wWStarts: {}".format(text))
                Devices[32].Update(nValue=0,sValue=str(text))
            if "wWWorkM" in payload:
                text=payload["wWWorkM"]
                Domoticz.Debug("wWWorkM: {}".format(text))
                Devices[33].Update(nValue=0,sValue=str(text))
            if "UBAuptime" in payload:
                text=payload["UBAuptime"]
                Domoticz.Debug("UBAuptime: {}".format(text))
                Devices[34].Update(nValue=0,sValue=str(text))
            if "burnStarts" in payload:
                text=payload["burnStarts"]
                Domoticz.Debug("burnStarts: {}".format(text))
                Devices[35].Update(nValue=0,sValue=str(text))
            if "burnWorkMin" in payload:
                text=payload["burnWorkMin"]
                Domoticz.Debug("burnWorkMin: {}".format(text))
                Devices[36].Update(nValue=0,sValue=str(text))
            if "heatWorkMin" in payload:
                text=payload["heatWorkMin"]
                Domoticz.Debug("heatWorkMin: {}".format(text))
                Devices[37].Update(nValue=0,sValue=str(text))

        # Set tapwater and heating status
        # This doesn't work yet because onMQTTPublish can't handle a non-JSON object.
        # The heating and tapwater topic's content is just a boolean.


        # Decode heat pump data
        # This creates Domoticz devices only if a heatpump topic message has been received.
        # (Not everyone has a heat pump)
        if "hp_data" in topic:
            if ( 201 not in Devices ):                
                Domoticz.Debug("Create percentage device (Heatpump modulation)")
                Domoticz.Device(Name="Heatpump modulation", Unit=201, Type=243, Subtype=6).Create()
            if ( 202 not in Devices ):                
                Domoticz.Debug("Create percentage device (Heatpump speed)")
                Domoticz.Device(Name="Heatpump speed", Unit=202, Type=243, Subtype=6).Create()
            if "pumpmodulation" in payload:
                percentage=payload["pumpmodulation"]
                Domoticz.Debug("pumpmodulation: Percentage: {}".format(percentage))
                if Devices[201].sValue != percentage:
                    Devices[201].Update(nValue=1, sValue=str(percentage))
            if "pumpspeed" in payload:
                percentage=payload["pumpspeed"]
                Domoticz.Debug("pumpspeed: Percentage: {}".format(percentage))
                if Devices[202].sValue != percentage:
                    Devices[202].Update(nValue=1, sValue=str(percentage))

        # Decode sensors
        # These sensors have a Domoticz ID reserved in the range 220 to 240
        # This creates Domoticz devices only if a sensors topic message has been received.
        # (Not everyone has optional Dallas sensors)
        # Todo: create only sensors reported through the topic
        if "sensors" in topic:
            if 221 not in Devices:
                Domoticz.Debug("Create temperature device (Dallas sensor 1)")
                Domoticz.Device(Name="Dallas sensor 1", Unit=221, Type=80, Subtype=5).Create()
            if 222 not in Devices:
                Domoticz.Debug("Create temperature device (Dallas sensor 2)")
                Domoticz.Device(Name="Dallas sensor 2", Unit=222, Type=80, Subtype=5).Create()
            if 223 not in Devices:
                Domoticz.Debug("Create temperature device (Dallas sensor 3)")
                Domoticz.Device(Name="Dallas sensor 3", Unit=223, Type=80, Subtype=5).Create()
            if 224 not in Devices:
                Domoticz.Debug("Create temperature device (Dallas sensor 4)")
                Domoticz.Device(Name="Dallas sensor 4", Unit=224, Type=80, Subtype=5).Create()
            if 225 not in Devices:
                Domoticz.Debug("Create temperature device (Dallas sensor 5)")
                Domoticz.Device(Name="Dallas sensor 5", Unit=225, Type=80, Subtype=5).Create()
        # Process the Dallas sensors for firmware up to 1.9.5b32
            if "temp_1" in payload:
                temp=round(float(payload["temp_1"]), 1)
                Domoticz.Debug("Dallas temp 1: Current temp: {}".format(temp))
                if Devices[221].sValue != temp:
                    Devices[221].Update(nValue=1, sValue=str(temp))
            if "temp_2" in payload:
                temp=round(float(payload["temp_2"]), 1)
                Domoticz.Debug("Dallas temp 2: Current temp: {}".format(temp))
                if Devices[222].sValue != temp:
                    Devices[222].Update(nValue=1, sValue=str(temp))
            if "temp_3" in payload:
                temp=round(float(payload["temp_3"]), 1)
                Domoticz.Debug("Dallas temp 3: Current temp: {}".format(temp))
                if Devices[223].sValue != temp:
                    Devices[223].Update(nValue=1, sValue=str(temp))
            if "temp_4" in payload:
                temp=round(float(payload["temp_4"]), 1)
                Domoticz.Debug("Dallas temp 4: Current temp: {}".format(temp))
                if Devices[224].sValue != temp:
                    Devices[224].Update(nValue=1, sValue=str(temp))
            if "temp_5" in payload:
                temp=round(float(payload["temp_5"]), 1)
                Domoticz.Debug("Dallas temp 5: Current temp: {}".format(temp))
                if Devices[225].sValue != temp:
                    Devices[225].Update(nValue=1, sValue=str(temp))
        # Process the Dallas sensors for firmware as of 1.9.5b33
            if "sensor1" in payload:
                payloadsensor1 = payload["sensor1"]
                if "temp" in payloadsensor1:
                    temp=round(float(payload["temp"]), 1)
                    Domoticz.Debug("Dallas temp 1: Current temp: {}".format(temp))
                    if Devices[221].sValue != temp:
                        Devices[221].Update(nValue=1, sValue=str(temp))
            if "sensor2" in payload:
                payloadsensor2 = payload["sensor2"]
                if "temp" in payloadsensor2:
                    temp=round(float(payload["temp"]), 1)
                    Domoticz.Debug("Dallas temp 2: Current temp: {}".format(temp))
                    if Devices[222].sValue != temp:
                        Devices[222].Update(nValue=1, sValue=str(temp))
            if "sensor3" in payload:
                payloadsensor3 = payload["sensor3"]
                if "temp" in payloadsensor3:
                    temp=round(float(payload["temp"]), 1)
                    Domoticz.Debug("Dallas temp 3: Current temp: {}".format(temp))
                    if Devices[223].sValue != temp:
                        Devices[223].Update(nValue=1, sValue=str(temp))
            if "sensor4" in payload:
                payloadsensor4 = payload["sensor4"]
                if "temp" in payloadsensor4:
                    temp=round(float(payload["temp"]), 1)
                    Domoticz.Debug("Dallas temp 4: Current temp: {}".format(temp))
                    if Devices[224].sValue != temp:
                        Devices[224].Update(nValue=1, sValue=str(temp))
            if "sensor5" in payload:
                payloadsensor5 = payload["sensor5"]
                if "temp" in payloadsensor5:
                    temp=round(float(payload["temp"]), 1)
                    Domoticz.Debug("Dallas temp 5: Current temp: {}".format(temp))
                    if Devices[225].sValue != temp:
                        Devices[225].Update(nValue=1, sValue=str(temp))                        
                        
                        
        # Decode solar module
        # These devices have a Domoticz ID reserved in the range 80 to 99
        # This creates Domoticz devices only if a solar module topic message has been received.
        # (Not everyone has a solar module)
        # Available devices in topic: collectortemp bottomtemp pumpmodulation pump
        # Todo: energylasthour energytoday energytotal pumpWorkMin
        if "sm_data" in topic:
            if 81 not in Devices:
                Domoticz.Debug("Create temperature device (Solar module collectortemp)")
                Domoticz.Device(Name="Solar Module collector", Unit=81, Type=80, Subtype=5).Create()
            if 82 not in Devices:
                Domoticz.Debug("Create temperature device (Solar module bottomtemp)")
                Domoticz.Device(Name="Solar Module bottom", Unit=82, Type=80, Subtype=5).Create()
            if 83 not in Devices:
                Domoticz.Debug("Create on/off switch (Solar module pump)")
                Domoticz.Device(Name="Solar module pump", Unit=83, Type=244, Subtype=73, Switchtype=0).Create()
            if 84 not in Devices:                
                Domoticz.Debug("Create percentage device (Solar module pump modulation)")
                Domoticz.Device(Name="Solar module pump modulation", Unit=84, Type=243, Subtype=6).Create()
            if "collectortemp" in payload:
                temp=round(float(payload["collectortemp"]), 1)
                Domoticz.Debug("Solar module collectortemp: {}".format(temp))
                if Devices[81].sValue != temp:
                    Devices[81].Update(nValue=1, sValue=str(temp))
            if "bottomtemp" in payload:
                temp=round(float(payload["bottomtemp"]), 1)
                Domoticz.Debug("Solar module bottomtemp: {}".format(temp))
                if Devices[82].sValue != temp:
                    Devices[82].Update(nValue=1, sValue=str(temp))
            if "pump" in payload:
                switchstate=payload["pump"]
                Domoticz.Debug("Solar module pump: State: {}".format(switchstate))
                if (switchstate == "on"):
                    Devices[83].Update(nValue=1,sValue="on")
                if (switchstate == "off"):
                    Devices[83].Update(nValue=0,sValue="off")
            if "pumpmodulation" in payload:
                percentage=payload["pumpmodulation"]
                Domoticz.Debug("Solar module pumpmodulation: Percentage: {}".format(percentage))
                if Devices[84].sValue != percentage:
                    Devices[84].Update(nValue=1, sValue=str(percentage))

        # Decode mixing module data
        # This creates Domoticz devices only if a mixing module topic message has been received.
        # (Not everyone has a mixing module)
        # It also creates only those devices for heating circuits in the topic message.
        # Mixer modules for heating zones (topic mixing_data):
        if "mixing_data" in topic:
            if "hc1" in payload:
                payloadHc1 = payload["hc1"]
                if 151 not in Devices:                
                    Domoticz.Debug("Create percentage device (Mixing module HC1 pump modulation)")
                    Domoticz.Device(Name="Mixing module HC1 pump modulation", Unit=151, Type=243, Subtype=6).Create()
                if 152 not in Devices:
                    Domoticz.Debug("Create temperature device (Mixing module HC1 flowtemp)")
                    Domoticz.Device(Name="Mixing module HC1 flow", Unit=152, Type=80, Subtype=5).Create()
                if 153 not in Devices:
                    Domoticz.Debug("Create on/off switch (Mixing module HC1 valvestatus)")
                    Domoticz.Device(Name="Mixing module HC1 valve", Unit=153, Type=244, Subtype=73, Switchtype=0).Create()
                if "pumpMod" in payloadHc1:
                    percentage=payloadHc1["pumpMod"]
                    Domoticz.Debug("Mixing module HC1 pump modulation: {}".format(percentage))
                    if Devices[151].sValue != percentage:
                        Devices[151].Update(nValue=1, sValue=str(percentage))
                if "flowTemp" in payloadHc1:
                    temp=round(float(payloadHc1["flowTemp"]), 1)
                    Domoticz.Debug("Mixing module HC1 flowtemp: {}".format(temp))
                    if Devices[152].sValue != temp:
                        Devices[152].Update(nValue=1, sValue=str(temp))
                if "valveStatus" in payloadHc1:
                    switchstate=payloadHc1["valveStatus"]
                    Domoticz.Debug("Mixing module HC1 valve: State: {}".format(switchstate))
                    if (switchstate == "on"):
                        Devices[153].Update(nValue=1,sValue="on")
                    if (switchstate == "off"):
                        Devices[153].Update(nValue=0,sValue="off")

            if "hc2" in payload:
                payloadHc2 = payload["hc2"]
                if 161 not in Devices:                
                    Domoticz.Debug("Create percentage device (Mixing module HC2 pump modulation)")
                    Domoticz.Device(Name="Mixing module HC2 pump modulation", Unit=161, Type=243, Subtype=6).Create()
                if 162 not in Devices:
                    Domoticz.Debug("Create temperature device (Mixing module HC2 flowtemp)")
                    Domoticz.Device(Name="Mixing module HC2 flow", Unit=162, Type=80, Subtype=5).Create()
                if 163 not in Devices:
                    Domoticz.Debug("Create on/off switch (Mixing module HC2 valvestatus)")
                    Domoticz.Device(Name="Mixing module HC2 valve", Unit=163, Type=244, Subtype=73, Switchtype=0).Create()
                if "pumpMod" in payloadHc2:
                    percentage=payloadHc2["pumpMod"]
                    Domoticz.Debug("Mixing module HC2 pump modulation: {}".format(percentage))
                    if Devices[161].sValue != percentage:
                        Devices[161].Update(nValue=1, sValue=str(percentage))
                if "flowTemp" in payloadHc2:
                    temp=round(float(payloadHc2["flowTemp"]), 1)
                    Domoticz.Debug("Mixing module HC2 flowtemp: {}".format(temp))
                    if Devices[162].sValue != temp:
                        Devices[162].Update(nValue=1, sValue=str(temp))
                if "valveStatus" in payloadHc2:
                    switchstate=payloadHc2["valveStatus"]
                    Domoticz.Debug("Mixing module HC2 valve: State: {}".format(switchstate))
                    if (switchstate == "on"):
                        Devices[163].Update(nValue=1,sValue="on")
                    if (switchstate == "off"):
                        Devices[163].Update(nValue=0,sValue="off")

            if "hc3" in payload:
                payloadHc3 = payload["hc3"]
                if 171 not in Devices:                
                    Domoticz.Debug("Create percentage device (Mixing module HC3 pump modulation)")
                    Domoticz.Device(Name="Mixing module HC3 pump modulation", Unit=171, Type=243, Subtype=6).Create()
                if 172 not in Devices:
                    Domoticz.Debug("Create temperature device (Mixing module HC3 flowtemp)")
                    Domoticz.Device(Name="Mixing module HC3 flow", Unit=172, Type=80, Subtype=5).Create()
                if 173 not in Devices:
                    Domoticz.Debug("Create on/off switch (Mixing module HC3 valvestatus)")
                    Domoticz.Device(Name="Mixing module HC3 valve", Unit=173, Type=244, Subtype=73, Switchtype=0).Create()
                if "pumpMod" in payloadHc3:
                    percentage=payloadHc3["pumpMod"]
                    Domoticz.Debug("Mixing module HC3 pump modulation: {}".format(percentage))
                    if Devices[171].sValue != percentage:
                        Devices[171].Update(nValue=1, sValue=str(percentage))
                if "flowTemp" in payloadHc3:
                    temp=round(float(payloadHc3["flowTemp"]), 1)
                    Domoticz.Debug("Mixing module HC3 flowtemp: {}".format(temp))
                    if Devices[172].sValue != temp:
                        Devices[172].Update(nValue=1, sValue=str(temp))
                if "valveStatus" in payloadHc3:
                    switchstate=payloadHc3["valveStatus"]
                    Domoticz.Debug("Mixing module HC3 valve: State: {}".format(switchstate))
                    if (switchstate == "on"):
                        Devices[173].Update(nValue=1,sValue="on")
                    if (switchstate == "off"):
                        Devices[173].Update(nValue=0,sValue="off")

            if "hc4" in payload:
                payloadHc4 = payload["hc4"]
                if 181 not in Devices:                
                    Domoticz.Debug("Create percentage device (Mixing module HC4 pump modulation)")
                    Domoticz.Device(Name="Mixing module HC4 pump modulation", Unit=181, Type=243, Subtype=6).Create()
                if 182 not in Devices:
                    Domoticz.Debug("Create temperature device (Mixing module HC4 flowtemp)")
                    Domoticz.Device(Name="Mixing module HC4 flow", Unit=182, Type=80, Subtype=5).Create()
                if 183 not in Devices:
                    Domoticz.Debug("Create on/off switch (Mixing module HC1 valvestatus)")
                    Domoticz.Device(Name="Mixing module HC4 valve", Unit=183, Type=244, Subtype=73, Switchtype=0).Create()
                if "pumpMod" in payloadHc4:
                    percentage=payloadHc4["pumpMod"]
                    Domoticz.Debug("Mixing module HC4 pump modulation: {}".format(percentage))
                    if Devices[181].sValue != percentage:
                        Devices[181].Update(nValue=1, sValue=str(percentage))
                if "flowTemp" in payloadHc4:
                    temp=round(float(payloadHc4["flowTemp"]), 1)
                    Domoticz.Debug("Mixing module HC4 flowtemp: {}".format(temp))
                    if Devices[182].sValue != temp:
                        Devices[182].Update(nValue=1, sValue=str(temp))
                if "valveStatus" in payloadHc4:
                    switchstate=payloadHc4["valveStatus"]
                    Domoticz.Debug("Mixing module HC4 valve: State: {}".format(switchstate))
                    if (switchstate == "on"):
                        Devices[183].Update(nValue=1,sValue="on")
                    if (switchstate == "off"):
                        Devices[183].Update(nValue=0,sValue="off")


    # onCommand publishes a MQTT message for each command received from Domoticz
    def onCommand(self, mqttClient, unit, command, level, color):
        self.topicBase = Parameters["Mode1"].replace(" ", "")
        Domoticz.Log("onCommand called for Unit " + str(unit) + ": Parameter '" + str(command) + "', Level: " + str(level))

        # Change a thermostat setpoint for a specific HC
        if (unit in [112, 122, 132, 142]):
            if (str(command) == "Set Level"):
                thermostatSetpointTopic = "thermostat_cmd_temp"    
                mqttClient.Publish(self.topicBase+thermostatSetpointTopic+str(int((unit-102)/10)), str(level))
                                   
        # This still needs work:
        # Change a thermostat mode for a specific HC
        if (unit in [113, 123, 133, 143]):
            dictOptions = Devices[unit].Options
            listLevelNames = dictOptions['LevelNames'].split('|')
            strSelectedName = listLevelNames[int(int(level)/10)]
            Domoticz.Log("Thermostat mode for unit "+str(unit)+"= "+strSelectedName)
            thermostatModeTopic = "thermostat_cmd_mode"    
            mqttClient.Publish(self.topicBase+thermostatModeTopic+str(int((unit-102)/10)), strSelectedName.lower())


class BasePlugin:
    mqttClient = None

    def onStart(self):
        self.debugging = Parameters["Mode6"]

        if self.debugging == "Verbose+":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Verbose":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2+4+8)

        self.controller = EmsDevices()

        self.controller.checkDevices()

        self.topicBase = Parameters["Mode1"].replace(" ", "")

        self.topicsList = list(["thermostat_data", "boiler_data", "sensors", "mixing_data", "sm_data", "hp_data", "heating_active", "tapwater_active"])
        self.topics = [self.topicBase + s for s in self.topicsList]
        Domoticz.Debug("Topiclist is:")
        Domoticz.Debug(", ".join(self.topics))
        self.mqttserveraddress = Parameters["Address"].replace(" ", "")
        self.mqttserverport = Parameters["Port"].replace(" ", "")
        self.mqttClient = MqttClient(self.mqttserveraddress, self.mqttserverport, self.onMQTTConnected, self.onMQTTDisconnected, self.onMQTTPublish, self.onMQTTSubscribed)

    def checkDevices(self):
        Domoticz.Log("checkDevices called")

    def onStop(self):
        Domoticz.Log("onStop called")

    def onCommand(self, Unit, Command, Level, Color):
        Domoticz.Debug("Command: " + Command + " (" + str(Level))
        self.controller.onCommand(self.mqttClient, Unit, Command, Level, Color)

    def onConnect(self, Connection, Status, Description):
        self.mqttClient.onConnect(Connection, Status, Description)

    def onDisconnect(self, Connection):
        self.mqttClient.onDisconnect(Connection)

    def onMessage(self, Connection, Data):
        self.mqttClient.onMessage(Connection, Data)
        Domoticz.Log("onMessage called with: "+Data["Verb"])

    def onHeartbeat(self):
        Domoticz.Debug("Heartbeating...")

        # Reconnect if connection has dropped
        if self.mqttClient.mqttConn is None or (not self.mqttClient.mqttConn.Connecting() and not self.mqttClient.mqttConn.Connected() or not self.mqttClient.isConnected):
            Domoticz.Debug("Reconnecting")
            self.mqttClient.Open()
        else:
            self.mqttClient.Ping()

    def onMQTTConnected(self):
        Domoticz.Debug("onMQTTConnected")
        self.mqttClient.Subscribe(self.topics)

    def onMQTTDisconnected(self):
        Domoticz.Debug("onMQTTDisconnected")

    def onMQTTSubscribed(self):
        Domoticz.Debug("onMQTTSubscribed")

    def onMQTTPublish(self, topic, rawmessage):
        Domoticz.Debug("MQTT message: " + topic + " " + str(rawmessage))
        message = ""
        try:
            message = json.loads(rawmessage.decode('utf8'))
#        except Exception as ex:
#            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
#            messageE = template.format(type(ex).__name__, ex.args)
#            Domoticz.Debug(messageE)
        except JSONDecodeError:
            Domoticz.Debug("Exception of type JSONDecodeError")
            message = rawmessage.decode('utf8')

        if (topic in self.topics):
            self.controller.onMqttMessage(topic, message)


global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Color):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Color)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
    
# This will set a selector switch
# from https://github.com/jorgh6/domoticz-onkyo-plugin/blob/master/plugin.py#L686
def setSelectorByName(intId, strName):
    dictOptions = Devices[intId].Options
    listLevelNames = dictOptions['LevelNames'].split('|')
    intLevel = 0
    for strLevelName in listLevelNames:
        if strLevelName == strName:
            Devices[intId].Update(1,str(intLevel))
        intLevel += 10
