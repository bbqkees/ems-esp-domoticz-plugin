# Domoticz Python Plugin for EMS bus Wi-Fi Gateway with Proddy's EMS-ESP firmware
# last update: 12 October 2020
# Author: bbqkees @www.bbqkees-electronics.nl
# Credits to @Gert05 for creating the first version of this plugin
# https://github.com/bbqkees/ems-esp-domoticz-plugin
# Proddy's EMS-ESP repository: https://github.com/proddy/EMS-ESP
# Product Wiki: https://bbqkees-electronics.nl/wiki/
#
#
"""
<plugin key="ems-gateway" name="EMS bus Wi-Fi Gateway" version="1.2">
    <description>
      EMS bus Wi-Fi Gateway plugin version 1.2<br/>
      Plugin to interface with EMS bus equipped Bosch brands boilers together with the EMS-ESP firmware  '<a href="https://github.com/proddy/EMS-ESP">from Proddy</a>'<br/>
      <br/>
      Please look at the  <a href="https://bbqkees-electronics.nl/wiki/">Product Wiki</a> for all instructions.<br/>
      <i>Please update the firmware of the Gateway to V2.1 or higher for best functionality.</i><br/>
      Automatically creates Domoticz devices for connected EMS devices.<br/> Do not forget to "Accept new Hardware Devices" on first run.<br/><br/>
      For this plugin to work you need to set the MQTT format to 'nested' in the EMS-ESP web interface.
    <br/>
    Parameters:<br/>
    <b>MQTT server and port</b><br/>
    MQTT Server address is usually, but not always, at the same address as the machine where Domoticz is running. So the 'local' machine at 127.0.0.1.<br/>
    The default port is 1883 and no user or password.<br/>
    <b>MQTT topic</b><br/>
    The default MQTT topic root this plugin will look in is 'ems-esp/' That forward slash at the end should not be omitted!<br/>
    Make sure that this is set accordingly in the EMS-ESP firmware settings.<br/>
    You can change it here or in the Gateway web interface if its set differently.<br/>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="Username" width="300px"/>
        <param field="Password" label="Password" width="300px" default="" password="true"/>
        <param field="Mode1" label="Topic base" width="300px" required="true" default="ems-esp/"/>
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
# ID 1 to 39 (1 and 3 still free)
#
# Shower data (topic shower_data):
# ID 60 to 69
#
# Tapwater/heating,Gateway etc on/off (topics tapwater_active and heating_active):
# ID 70 to 79
# 
# Solar module data (topic solar_data):
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
    # not used for now 
        Domoticz.Debug("checkDevices called")

    # onMqttMessage decodes the MQTT messages and updates the Domoticz parameters
    def onMqttMessage(self, topic, payload):

        # In firmware V2.1 the tapwater_active and heating_active are also included in boiler_data.
        # However, tapwater_active and heating_active are published on state change while boiler_data is periodical.
        # So its best to look at the separate topics to keep the state in Domoticz in sync.

        # Process the tapwater_active topic. Note the contents a single boolean (0 or 1) and not json.
        if "tapwater_active" in topic:
            if 71 not in Devices:
                Domoticz.Debug("Create on/off switch (tapwater active)")
                Domoticz.Device(Name="Tapwater active", Unit=71, Type=244, Subtype=73, Switchtype=0).Create()
            if payload == "off":
                Devices[71].Update(nValue=0, sValue="off")
            if payload == "on":
                Devices[71].Update(nValue=1, sValue="on")

        # Process the heating_active topic. Note the contents a single boolean (0 or 1) and not json.
        if "heating_active" in topic:
            if 72 not in Devices:
                Domoticz.Debug("Create on/off switch (heating active)")
                Domoticz.Device(Name="Heating active", Unit=72, Type=244, Subtype=73, Switchtype=0).Create()
            if payload == "off":
                Devices[72].Update(nValue=0,sValue="off")
            if payload == "on":
                Devices[72].Update(nValue=1,sValue="on")

        # Process the status topic. Note the contents a single word and not json.
        if "status" in topic:
            Domoticz.Debug("status topic received")   
            if 73 not in Devices:
                Domoticz.Debug("Create on/off switch (Gateway online/offline)")
                Domoticz.Device(Name="Gateway online", Unit=73, Type=244, Subtype=73, Switchtype=0).Create() 
            if payload == "offline":
                Devices[73].Update(nValue=0,sValue="off")
            if payload == "online":
                Devices[73].Update(nValue=1,sValue="on")

        # Process the info topic. It extracts the EMS-ESP version for future use.
        if "info" in topic:
            if "version" in payload:
                emsEspVersion = payload["version"]

        # Process the thermostat parameters of each heating zone
        # On first discovery of a hc 4 devices are created.
        if "thermostat_data" in topic:
            if "hc1" in payload:
                payloadHc1 = payload["hc1"]
                if 111 not in Devices:
                    Domoticz.Debug("Create Temperature Device HC1")
                    Domoticz.Device(Name="EMS thermostat current temp HC1", Unit=111, Type=80, Subtype=5).Create()
                if 112 not in Devices:
                    Domoticz.Debug("Create Thermostat Setpoint Device HC1")
                    Domoticz.Device(Name="EMS thermostat setpoint HC1", Unit=112, Type=242, Subtype=1).Create()
                if 113 not in Devices:
                    Domoticz.Debug("Create Thermostat mode selector HC1")
                    Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode HC1", Unit=113, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if 114 not in Devices:
                    Domoticz.Debug("Create Thermostat mode type HC1")
                    Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode type HC1", Unit=114, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if "currtemp" in payloadHc1:
                    temp=round(float(payloadHc1["currtemp"]), 1)
                    updateDevice(111, 80, 5, temp)
                if "seltemp" in payloadHc1:
                    temp=payloadHc1["seltemp"]
                    updateDevice(112, 80, 5, temp)
                if "mode" in payloadHc1:
                    thMode=payloadHc1["mode"]
                    Domoticz.Debug("Thermostat HC1: Mode is: "+str(thMode))
                    setSelectorByName(113, str(thMode))
                if "modetype" in payloadHc1:
                    thMode=payloadHc1["modetype"]
                    Domoticz.Debug("Thermostat HC1: Mode type is: "+str(thMode))
                    setSelectorByName(114, str(thMode))
            if "hc2" in payload:
                payloadHc2 = payload["hc2"]
                if 121 not in Devices:
                    Domoticz.Debug("Create Temperature Device HC2")
                    Domoticz.Device(Name="EMS thermostat current temp HC2", Unit=121, Type=80, Subtype=5).Create()
                if 122 not in Devices:
                    Domoticz.Debug("Create Thermostat Setpoint Device HC2")
                    Domoticz.Device(Name="EMS thermostat setpoint HC2", Unit=122, Type=242, Subtype=1).Create()
                if 123 not in Devices:
                    Domoticz.Debug("Create Thermostat mode selector HC2")
                    Options = { "LevelActions" : "||||",
                                "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode HC2", Unit=123, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if 124 not in Devices:
                    Domoticz.Debug("Create Thermostat mode type HC2")
                    Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode type HC2", Unit=124, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if "currtemp" in payloadHc2:
                    temp=round(float(payloadHc2["currtemp"]), 1)
                    updateDevice(121, 80, 5, temp)
                if "seltemp" in payloadHc2:
                    temp=payloadHc2["seltemp"]
                    updateDevice(122, 80, 5, temp)
                if "mode" in payloadHc2:
                    thMode=payloadHc2["mode"]
                    Domoticz.Debug("Thermostat HC2: Mode is: "+str(thMode))
                    setSelectorByName(123, str(thMode))
                if "modetype" in payloadHc2:
                    thMode=payloadHc2["modetype"]
                    Domoticz.Debug("Thermostat HC2: Mode type is: "+str(thMode))
                    setSelectorByName(124, str(thMode))
            if "hc3" in payload:
                payloadHc3 = payload["hc3"]
                if 131 not in Devices:
                    Domoticz.Debug("Create Temperature Device HC3")
                    Domoticz.Device(Name="EMS thermostat current temp HC3", Unit=131, Type=80, Subtype=5).Create()
                if 132 not in Devices:
                    Domoticz.Debug("Create Thermostat Setpoint Device HC3")
                    Domoticz.Device(Name="EMS thermostat setpoint HC3", Unit=132, Type=242, Subtype=1).Create()
                if 133 not in Devices:
                    Domoticz.Debug("Create Thermostat mode selector HC3")
                    Options = { "LevelActions" : "||||",
                                "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                               "LevelOffHidden" : "true",
                               "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode HC3", Unit=133, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if 134 not in Devices:
                    Domoticz.Debug("Create Thermostat mode type HC3")
                    Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode type HC3", Unit=134, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if "currtemp" in payloadHc3:
                    temp=round(float(payloadHc3["currtemp"]), 1)
                    updateDevice(131, 80, 5, temp)
                if "seltemp" in payloadHc3:
                    temp=payloadHc3["seltemp"]
                    updateDevice(132, 80, 5, temp)
                if "mode" in payloadHc3:
                    thMode=payloadHc3["mode"]
                    Domoticz.Debug("Thermostat HC3: Mode is: "+str(thMode))
                    setSelectorByName(133, str(thMode))
                if "modetype" in payloadHc3:
                    thMode=payloadHc3["modetype"]
                    Domoticz.Debug("Thermostat HC3: Mode type is: "+str(thMode))
                    setSelectorByName(134, str(thMode))
            if "hc4" in payload:
                payloadHc4 = payload["hc4"]
                if 141 not in Devices:
                    Domoticz.Debug("Create Temperature Device HC4")
                    Domoticz.Device(Name="EMS thermostat current temp HC4", Unit=141, Type=80, Subtype=5).Create()
                if 142 not in Devices:
                    Domoticz.Debug("Create Thermostat Setpoint Device HC4")
                    Domoticz.Device(Name="EMS thermostat setpoint HC4", Unit=142, Type=242, Subtype=1).Create()
                if 143 not in Devices:
                    Domoticz.Debug("Create Thermostat mode selector HC4")
                    Options = { "LevelActions" : "||||",
                                "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode HC4", Unit=143, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if 144 not in Devices:
                    Domoticz.Debug("Create Thermostat mode type HC4")
                    Options = { "LevelActions" : "||||",
                        "LevelNames"   : "Off|Auto|Day|Night|Manual|Heat|Eco|Nofrost",
                        "LevelOffHidden" : "true",
                        "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Thermostat mode type HC4", Unit=144, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                if "currtemp" in payloadHc4:
                    temp=round(float(payloadHc4["currtemp"]), 1)
                    updateDevice(141, 80, 5, temp)
                if "seltemp" in payloadHc4:
                    temp=payloadHc4["seltemp"]
                    updateDevice(142, 80, 5, temp)
                if "mode" in payloadHc4:
                    thMode=payloadHc4["mode"]
                    Domoticz.Debug("Thermostat HC4: Mode is: "+str(thMode))
                    setSelectorByName(143, str(thMode))
                if "modetype" in payloadHc4:
                    thMode=payloadHc4["modetype"]
                    Domoticz.Debug("Thermostat HC4: Mode type is: "+str(thMode))
                    setSelectorByName(144, str(thMode))

            # Process the boiler parameters
        if "boiler_data" in topic:
            if "sysPress" in payload:
                pressure=payload["sysPress"]
                if 2 not in Devices:
                    Domoticz.Debug("Create System Pressure Device")
                    Domoticz.Device(Name="Boiler system pressure", Unit=2, Type=243, Subtype=9).Create()
                updateDevice(2, 243, 9, pressure)
            # 11 to 16 + 25 to 27 temp
            if "selFlowTemp" in payload:
                temp=round(float(payload["selFlowTemp"]), 1)
                if 11 not in Devices:
                    Domoticz.Debug("Create temperature device (selFlowTemp)")
                    Domoticz.Device(Name="Boiler selected flow temperature", Unit=11, Type=80, Subtype=5).Create()
                updateDevice(11, 80, 5, temp)
            if "outdoorTemp" in payload:
                temp=round(float(payload["outdoorTemp"]), 1)
                if 12 not in Devices:
                    Domoticz.Debug("Create temperature device (outdoorTemp)")
                    Domoticz.Device(Name="Boiler connected outdoor temperature", Unit=12, Type=80, Subtype=5).Create()
                updateDevice(12, 80, 5, temp)
            if "wWCurTemp" in payload:
                temp=round(float(payload["wWCurTemp"]), 1)
                if 13 not in Devices:
                    Domoticz.Debug("Create temperature device (wWCurTemp)")
                    Domoticz.Device(Name="Boiler warm water current temperature", Unit=13, Type=80, Subtype=5).Create()
                updateDevice(13, 80, 5, temp)
            if "curFlowTemp" in payload:
                temp=round(float(payload["curFlowTemp"]), 1)
                if 14 not in Devices:
                    Domoticz.Debug("Create temperature device (curFlowTemp)")
                    Domoticz.Device(Name="Boiler current flow temperature", Unit=14, Type=80, Subtype=5).Create()
                updateDevice(14, 80, 5, temp)
            if "retTemp" in payload:
                temp=round(float(payload["retTemp"]), 1)
                if 15 not in Devices:
                    Domoticz.Debug("Create temperature device (retTemp)")
                    Domoticz.Device(Name="Boiler return temperature", Unit=15, Type=80, Subtype=5).Create()
                updateDevice(15, 80, 5, temp)
            #    Domoticz.Debug("retTemp: Current temp: {}".format(temp))
            if "boilTemp" in payload:
                temp=round(float(payload["boilTemp"]), 1)
                if 16 not in Devices:
                    Domoticz.Debug("Create temperature device (boilTemp)")
                    Domoticz.Device(Name="Boiler temperature", Unit=16, Type=80, Subtype=5).Create()
                updateDevice(16, 80, 5, temp)
            if "wWSelTemp" in payload:
                temp=round(float(payload["wWSelTemp"]), 1)
                if 25 not in Devices:
                    Domoticz.Debug("Create temperature device (wWSelTemp)")
                    Domoticz.Device(Name="ww selected temperature", Unit=25, Type=80, Subtype=5).Create()
                updateDevice(25, 80, 5, temp)
            if "wWDesiredTemp" in payload:
                temp=round(float(payload["wWDesiredTemp"]), 1)
                if 26 not in Devices:
                    Domoticz.Debug("Create temperature device (wWDesiredTemp)")
                    Domoticz.Device(Name="ww desired temperature", Unit=26, Type=80, Subtype=5).Create()
                updateDevice(26, 80, 5, temp)
            if "heating_temp" in payload:
                temp=round(float(payload["heating_temp"]), 1)
                if 27 not in Devices:
                    Domoticz.Debug("Create temperature device (heating_temp)")
                    Domoticz.Device(Name="Heating temperature", Unit=27, Type=80, Subtype=5).Create()
                updateDevice(27, 80, 5, temp)
            # 29 ampere
            if "flameCurr" in payload:
                temp=round(float(payload["flameCurr"]), 1)
                if 29 not in Devices:
                    Domoticz.Debug("Create ampere device (flameCurr)")
                    Domoticz.Device(Name="Boiler flame current", Unit=29, Type=243, Subtype=23).Create()
                updateDevice(29, 243, 23, temp)
            #21 to 24 + 28 + 38 + 39 percentage
            if "selBurnPow" in payload:
                percentage=payload["selBurnPow"]
                if 21 not in Devices:
                    Domoticz.Debug("Create percentage device (selBurnPow)")
                    Domoticz.Device(Name="Boiler selected power", Unit=21, Type=243, Subtype=6).Create()
                updateDevice(21, 243, 6, percentage)
            if "curBurnPow" in payload:
                percentage=payload["curBurnPow"]
                if 22 not in Devices:
                    Domoticz.Debug("Create percentage device (curBurnPow)")
                    Domoticz.Device(Name="Boiler current power", Unit=22, Type=243, Subtype=6).Create()
                updateDevice(22, 243, 6, percentage)
            if "pumpMod" in payload:
                percentage=payload["pumpMod"]
                if 23 not in Devices:
                    Domoticz.Debug("Create percentage device (pumpMod)")
                    Domoticz.Device(Name="Boiler pump modulation", Unit=23, Type=243, Subtype=6).Create()
                updateDevice(23, 243, 6, percentage)
            if "wWCurFlow" in payload:
                percentage=payload["wWCurFlow"]
                if 24 not in Devices:
                    Domoticz.Debug("Create percentage device (wWCurFlow)")
                    Domoticz.Device(Name="Boiler warm water flow", Unit=24, Type=243, Subtype=6).Create()
                updateDevice(24, 243, 6, percentage)
            if "wWCircPump" in payload:
                percentage=payload["wWCircPump"]
                if 28 not in Devices:
                    Domoticz.Debug("Create percentage device (wWCircPump)")
                    Domoticz.Device(Name="ww pump modulation", Unit=28, Type=243, Subtype=6).Create()
                updateDevice(28, 243, 6, percentage)
            if "pumpModMax" in payload:
                percentage=payload["pumpModMax"]
                if 38 not in Devices:
                    Domoticz.Debug("Create percentage device (pumpModMax)")
                    Domoticz.Device(Name="pump modulation max", Unit=38, Type=243, Subtype=6).Create()
                updateDevice(38, 243, 6, percentage)
            if "pumpModMin" in payload:
                percentage=payload["pumpModMin"]
                if 39 not in Devices:
                    Domoticz.Debug("Create percentage device (pumpMod_Min)")
                    Domoticz.Device(Name="pump modulation min", Unit=39, Type=243, Subtype=6).Create()
                updateDevice(39, 243, 6, percentage)
            #4 to 10 switch
            if "burnGas" in payload:
                switchstate=payload["burnGas"]
                if 4 not in Devices:
                    Domoticz.Debug("Create on/off switch (burnGas)")
                    Domoticz.Device(Name="Boiler gas", Unit=4, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(4, 244, 73, switchstate)
            if "fanWork" in payload:
                switchstate=payload["fanWork"]
                if 5 not in Devices:
                    Domoticz.Debug("Create on/off switch (fanWork)")
                    Domoticz.Device(Name="Boiler fan", Unit=5, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(5, 244, 73, switchstate)
            if "ignWork" in payload:
                switchstate=payload["ignWork"]
                if 6 not in Devices:
                    Domoticz.Debug("Create on/off switch (ignWork)")
                    Domoticz.Device(Name="Boiler ingnition", Unit=6, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(6, 244, 73, switchstate)
            if "heatPump" in payload:
                switchstate=payload["heatPump"]
                if 7 not in Devices:
                    Domoticz.Debug("Create on/off switch (heatPump)")
                    Domoticz.Device(Name="Boiler heating pump", Unit=7, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(7, 244, 73, switchstate)
            if "wWActivated" in payload:
                switchstate=payload["wWActivated"]
                if 8 not in Devices:
                    Domoticz.Debug("Create on/off switch (wWActivated)")
                    Domoticz.Device(Name="Boiler warm water", Unit=8, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(8, 244, 73, switchstate)
            if "wWHeat" in payload:
                switchstate=payload["wWHeat"]
                if 9 not in Devices:
                    Domoticz.Debug("Create on/off switch (wWHeat)")
                    Domoticz.Device(Name="Boiler warm water heating", Unit=9, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(9, 244, 73, switchstate)
            if "wWCirc" in payload:
                switchstate=payload["wWCirc"]
                if 10 not in Devices:
                    Domoticz.Debug("Create on/off switch (wWCirc)")
                    Domoticz.Device(Name="Boiler warm water circulation", Unit=10, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(10, 244, 73, switchstate)
            if "serviceCode" in payload:
                text=payload["serviceCode"]
                if 18 not in Devices:
                    Domoticz.Debug("Create text device (serviceCode)")
                    Domoticz.Device(Name="Boiler Service code", Unit=18, Type=243, Subtype=19).Create()
                updateDevice(18, 243, 19, text)
            if "serviceCodeNumber" in payload:
                text=payload["serviceCodeNumber"]
                if 19 not in Devices:
                    Domoticz.Debug("Create text device (serviceCodeNumber)")
                    Domoticz.Device(Name="Boiler Service code number", Unit=19, Type=243, Subtype=19).Create()
                updateDevice(19, 243, 19, text)
            if "wWStarts" in payload:
                text=payload["wWStarts"]
                if 32 not in Devices:
                    Domoticz.Debug("Create counter (wWStarts)")
                    Domoticz.Device(Name="ww starts", Unit=32, Type=113, Subtype=0, Switchtype=3).Create()
                updateDevice(32, 113, 0, text)
            if "wWWorkM" in payload:
                text=payload["wWWorkM"]
                if 33 not in Devices:
                    Domoticz.Debug("Create counter (wWWorkM)")
                    Domoticz.Device(Name="ww work minutes", Unit=33, Type=113, Subtype=0, Switchtype=3).Create()
                updateDevice(33, 113, 0, text)
            if "UBAuptime" in payload:
                text=payload["UBAuptime"]
                if 34 not in Devices:
                    Domoticz.Debug("Create counter (UBAuptime)")
                    Domoticz.Device(Name="Boiler UBA uptime", Unit=34, Type=113, Subtype=0, Switchtype=3).Create()
                updateDevice(34, 113, 0, text)
            if "burnStarts" in payload:
                text=payload["burnStarts"]
                if 35 not in Devices:
                    Domoticz.Debug("Create counter (burnStarts)")
                    Domoticz.Device(Name="boiler burner starts", Unit=35, Type=113, Subtype=0, Switchtype=3).Create()
                updateDevice(35, 113, 0, text)
            if "burnWorkMin" in payload:
                text=payload["burnWorkMin"]
                if 36 not in Devices:
                    Domoticz.Debug("Create counter (burnWorkMin)")
                    Domoticz.Device(Name="boiler burner working minutes", Unit=36, Type=113, Subtype=0, Switchtype=3).Create()
                updateDevice(36, 113, 0, text)
            if "heatWorkMin" in payload:
                text=payload["heatWorkMin"]
                if 37 not in Devices:
                    Domoticz.Debug("Create counter (heatWorkMin)")
                    Domoticz.Device(Name="boiler heating working minutes", Unit=37, Type=113, Subtype=0, Switchtype=3).Create()
                updateDevice(37, 113, 0, text)
            if "wWComfort" in payload:
                text=payload["wWComfort"]
                # Create selector switch for boiler modes
                if 30 not in Devices:
                    Domoticz.Debug("Create boiler mode selector")
                    Options = { "LevelActions" : "||",
                                "LevelNames"   : "Hot|Eco|Intelligent",
                               "LevelOffHidden" : "true",
                               "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="Boiler comfort mode", Unit=30, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                setSelectorByName(30, text)
            if "wWMode" in payload:
                text=payload["wWMode"]
                # Create selector switch for ww modes
                # this is actually a thermostat command but its not linked to a heating zone.
                if 31 not in Devices:
                    Domoticz.Debug("Create ww mode selector")
                    Options = { "LevelActions" : "||",
                                "LevelNames"   : "off|on|auto",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                }
                    Domoticz.Device(Name="ww mode", Unit=31, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                setSelectorByName(31, text)        

        # Decode heat pump data (This is not in EMS-ESP V2 anymore?)
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
                updateDevice(201, 243, 6, percentage)
            if "pumpspeed" in payload:
                percentage=payload["pumpspeed"]
                updateDevice(202, 243, 6, percentage)

        # Decode sensors
        # These sensors have a Domoticz ID reserved in the range 220 to 239
        # This creates Domoticz devices only if a sensor has been received in the topic message.
        if "sensor_data" in topic:
            if "sensor1" in payload:
                payloadS1 = payload["sensor1"]
                if 221 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 1)")
                    Domoticz.Device(Name="Dallas sensor 1", Unit=221, Type=80, Subtype=5).Create()
                if "temp" in payloadS1:
                    tempS=round(float(payloadS1["temp"]), 1)
                    updateDevice(221, 80, 5, tempS)
            if "sensor2" in payload:
                payloadS2 = payload["sensor2"]
                if 222 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 2)")
                    Domoticz.Device(Name="Dallas sensor 2", Unit=222, Type=80, Subtype=5).Create()
                if "temp" in payloadS2:
                    tempS=round(float(payloadS2["temp"]), 1)
                    updateDevice(222, 80, 5, tempS)
            if "sensor3" in payload:
                payloadS3 = payload["sensor3"]
                if 223 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 3)")
                    Domoticz.Device(Name="Dallas sensor 3", Unit=223, Type=80, Subtype=5).Create()
                if "temp" in payloadS3:
                    tempS=round(float(payloadS3["temp"]), 1)
                    updateDevice(223, 80, 5, tempS)
            if "sensor4" in payload:
                payloadS4 = payload["sensor4"]
                if 224 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 4)")
                    Domoticz.Device(Name="Dallas sensor 4", Unit=224, Type=80, Subtype=5).Create()
                if "temp" in payloadS2:
                    tempS=round(float(payloadS4["temp"]), 1)
                    updateDevice(224, 80, 5, tempS)
            if "sensor5" in payload:
                payloadS5 = payload["sensor5"]
                if 225 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 5)")
                    Domoticz.Device(Name="Dallas sensor 5", Unit=225, Type=80, Subtype=5).Create()
                if "temp" in payloadS5:
                    tempS=round(float(payloadS5["temp"]), 1)
                    updateDevice(225, 80, 5, tempS)
            if "sensor6" in payload:
                payloadS6 = payload["sensor6"]
                if 226 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 6)")
                    Domoticz.Device(Name="Dallas sensor 6", Unit=226, Type=80, Subtype=5).Create()
                if "temp" in payloadS6:
                    tempS=round(float(payloadS6["temp"]), 1)
                    updateDevice(226, 80, 5, tempS)
            if "sensor7" in payload:
                payloadS7 = payload["sensor7"]
                if 227 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 7)")
                    Domoticz.Device(Name="Dallas sensor 7", Unit=227, Type=80, Subtype=5).Create()
                if "temp" in payloadS7:
                    tempS=round(float(payloadS7["temp"]), 1)
                    updateDevice(226, 80, 5, tempS)
            if "sensor8" in payload:
                payloadS8 = payload["sensor8"]
                if 228 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 8)")
                    Domoticz.Device(Name="Dallas sensor 8", Unit=228, Type=80, Subtype=5).Create()
                if "temp" in payloadS8:
                    tempS=round(float(payloadS8["temp"]), 1)
                    updateDevice(228, 80, 5, tempS)
            if "sensor9" in payload:
                payloadS9 = payload["sensor9"]
                if 229 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 9)")
                    Domoticz.Device(Name="Dallas sensor 9", Unit=229, Type=80, Subtype=5).Create()
                if "temp" in payloadS9:
                    tempS=round(float(payloadS9["temp"]), 1)
                    updateDevice(229, 80, 5, tempS)
            if "sensor10" in payload:
                payloadS10 = payload["sensor10"]
                if 230 not in Devices:
                    Domoticz.Debug("Create temperature device (Dallas sensor 10)")
                    Domoticz.Device(Name="Dallas sensor 10", Unit=230, Type=80, Subtype=5).Create()
                if "temp" in payloadS10:
                    tempS=round(float(payloadS10["temp"]), 1)
                    updateDevice(230, 80, 5, tempS)

        # Decode solar module
        # These devices have a Domoticz ID reserved in the range 80 to 99
        # This creates Domoticz devices only if a solar module topic message has been received.
        # (Not everyone has a solar module)
        # Available devices in topic: collectorTemp tankBottomTemp pumpModulation solarPump pumpWorkMin
        if "solar_data" in topic:
            if "collectorTemp" in payload:
                temp=round(float(payload["collectorTemp"]), 1)
                if 81 not in Devices:
                    Domoticz.Debug("Create temperature device (Solar module collectortemp)")
                    Domoticz.Device(Name="Solar Module collector", Unit=81, Type=80, Subtype=5).Create()
                updateDevice(81, 80, 5, temp)
            if "tankBottomTemp" in payload:
                temp=round(float(payload["tankBottomTemp"]), 1)
                if 82 not in Devices:
                    Domoticz.Debug("Create temperature device (Solar module bottomtemp)")
                    Domoticz.Device(Name="Solar Module bottom", Unit=82, Type=80, Subtype=5).Create()
                updateDevice(82, 80, 5, temp)
            if "solarPump" in payload:
                switchstate=payload["solarPump"]
                if 83 not in Devices:
                    Domoticz.Debug("Create on/off switch (Solar module pump)")
                    Domoticz.Device(Name="Solar module pump", Unit=83, Type=244, Subtype=73, Switchtype=0).Create()
                updateDevice(83, 244, 73, switchstate)
            if "solarPumpModulation" in payload:
                percentage=payload["solarPumpModulation"]
                if 84 not in Devices:                
                    Domoticz.Debug("Create percentage device (Solar module pump modulation)")
                    Domoticz.Device(Name="Solar module pump modulation", Unit=84, Type=243, Subtype=6).Create()
                updateDevice(84, 243, 6, percentage)
            if "pumpWorkMin" in payload:
                text=payload["pumpWorkMin"]
                if 85 not in Devices:   
                    Domoticz.Debug("Create counter (solarPumpWorkMin)")
                    Domoticz.Device(Name="solar pump working minutes", Unit=36, Type=113, Subtype=0, Switchtype=3).Create()
                updateDevice(85, 113, 0, text)

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
                    updateDevice(151, 243, 6, percentage)
                if "flowTemp" in payloadHc1:
                    temp=round(float(payloadHc1["flowTemp"]), 1)
                    updateDevice(152, 80, 5, temp)
                if "valveStatus" in payloadHc1:
                    switchstate=payloadHc1["valveStatus"]
                    updateDevice(153, 244, 73, switchstate)

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
                    updateDevice(161, 243, 6, percentage)
                if "flowTemp" in payloadHc2:
                    temp=round(float(payloadHc2["flowTemp"]), 1)
                    updateDevice(162, 80, 5, temp)
                if "valveStatus" in payloadHc2:
                    switchstate=payloadHc2["valveStatus"]
                    updateDevice(163, 244, 73, switchstate)

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
                    updateDevice(171, 243, 6, percentage)
                if "flowTemp" in payloadHc3:
                    temp=round(float(payloadHc3["flowTemp"]), 1)
                    updateDevice(172, 80, 5, temp)
                if "valveStatus" in payloadHc3:
                    switchstate=payloadHc3["valveStatus"]
                    updateDevice(173, 244, 73, switchstate)

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
                    updateDevice(181, 243, 6, percentage)
                if "flowTemp" in payloadHc4:
                    temp=round(float(payloadHc4["flowTemp"]), 1)
                    updateDevice(182, 80, 5, temp)
                if "valveStatus" in payloadHc4:
                    switchstate=payloadHc4["valveStatus"]
                    updateDevice(183, 244, 73, switchstate)


    # onCommand publishes a MQTT message for each command received from Domoticz
    def onCommand(self, mqttClient, unit, command, level, color):
        self.topicBase = Parameters["Mode1"].replace(" ", "")
        Domoticz.Log("onCommand called for Unit " + str(unit) + ": Parameter '" + str(command) + "', Level: " + str(level))

        # Change a thermostat setpoint for a specific HC
        if (unit in [112, 122, 132, 142]):
            if (str(command) == "Set Level"):
                sendEmsCommand(mqttClient, "thermostat", "temp", str(level), 1, str(int((unit-102)/10)))

        # Set boiler comfort mode
        if (unit == 30):
            dictOptions = Devices[unit].Options
            listLevelNames = dictOptions['LevelNames'].split('|')
            strSelectedName = listLevelNames[int(int(level)/10)]
            Domoticz.Log("boiler comfort mode set to"+strSelectedName)
            sendEmsCommand(mqttClient, "boiler", "comfort", strSelectedName.lower(), 0, 0)

        # Set boiler ww mode (via thermostat command)
        if (unit == 31):
            dictOptions = Devices[unit].Options
            listLevelNames = dictOptions['LevelNames'].split('|')
            strSelectedName = listLevelNames[int(int(level)/10)]
            Domoticz.Log("boiler ww mode set to"+strSelectedName)
            sendEmsCommand(mqttClient, "thermostat", "wwmode", strSelectedName.lower(), 0, 0)              

        # Change a thermostat mode for a specific HC
        if (unit in [113, 123, 133, 143]):
            dictOptions = Devices[unit].Options
            listLevelNames = dictOptions['LevelNames'].split('|')
            strSelectedName = listLevelNames[int(int(level)/10)]
            Domoticz.Log("Thermostat mode for unit "+str(unit)+"= "+strSelectedName)
            sendEmsCommand(mqttClient, "thermostat", "mode", strSelectedName.lower(), 1, str(int((unit-102)/10)))
    
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

        self.topicsList = list(["thermostat_data", "boiler_data", "sensor_data", "mixing_data", "solar_data", "hp_data", "heating_active", "tapwater_active", "status", "info"])
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
        Domoticz.Debug("onMessage called with: "+Data["Verb"])

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
        except json.decoder.JSONDecodeError:
            Domoticz.Debug("Exception of type JSONDecodeError. Non-json object. Message is: ")
            message = rawmessage.decode('utf8')
            Domoticz.Debug(message)
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

# This is the general update function for a device based on its type and subtype
# It is excluding the selector switches
def updateDevice(deviceId, deviceType, deviceSubType, deviceValue):
    # 80 is a temperature sensor
    if deviceType == 80 and deviceSubType == 5:
        if Devices[deviceId].sValue == str(deviceValue):
            Domoticz.Debug("deviceId {} value has not changed. Device not updated".format(deviceId))
        else:
            Domoticz.Debug("deviceId {} updated with value {}.".format(deviceId, deviceValue))
            Devices[deviceId].Update(nValue=1, sValue=str(deviceValue))
    # 113 is a counter
    if deviceType == 113 and deviceSubType == 0:
        if Devices[deviceId].sValue == str(deviceValue):
            Domoticz.Debug("deviceId {} value has not changed. Device not updated".format(deviceId))
        else:
            Domoticz.Debug("deviceId {} updated with value {}.".format(deviceId, deviceValue))
            Devices[deviceId].Update(nValue=0, sValue=str(deviceValue))
    # 242 is a thermostat setpoint
    if deviceType == 242 and deviceSubType == 1:
        if Devices[deviceId].sValue == str(deviceValue):
            Domoticz.Debug("deviceId {} value has not changed. Device not updated".format(deviceId))
        else:
            Domoticz.Debug("deviceId {} updated with value {}.".format(deviceId, deviceValue))
            Devices[deviceId].Update(nValue=1, sValue=str(deviceValue))
    # 243 is the General Type. SubType is needed
    # Subtype 6 is a percentage sensor
    # Subtype 9 is a pressure sensor
    # Subtype 19 is a text sensor
    # Subtype 23 is a current sensor
    if deviceType == 243 and (deviceSubType in [6, 9, 19, 23]):
        if Devices[deviceId].sValue == str(deviceValue):
            Domoticz.Debug("deviceId {} value has not changed. Device not updated".format(deviceId))
        else:
            Domoticz.Debug("deviceId {} updated with value {}.".format(deviceId, deviceValue))
            Devices[deviceId].Update(nValue=1, sValue=str(deviceValue))
    # 244 is a switch type, Subtype is needed
    # Subtype 73 is an on/off switch when Switchtype is 0.
    if deviceType == 244 and deviceSubType == 73:
        if Devices[deviceId].sValue == str(deviceValue):
            Domoticz.Debug("deviceId {} state has not changed. Device not updated".format(deviceId))
        else:
            Domoticz.Debug("deviceId {} updated with state = {}.".format(deviceId, deviceValue))
            if Devices[deviceId].sValue != str(deviceValue):
                if (str(deviceValue) == "on"):
                    Devices[deviceId].Update(nValue=1,sValue="on")
                if (str(deviceValue) == "off"):
                    Devices[deviceId].Update(nValue=0,sValue="off")

# This is the general send command function over MQTT for an EMS device
# emsDevice are system, sensor, boiler, thermostat, solar, mixing and heatpump.
# The payload should be in the format
# {"cmd":<command> ,"data":<data>, "id":<id>} or {"cmd":<command> ,"data":<data>, "hc":<hc>}
# First implementing the thermostat and some boiler stuff.
def sendEmsCommand(mqttClient, emsDevice, emsCommand, emsData, emsId, emsHc):
    topicBase = Parameters["Mode1"].replace(" ", "")
    if emsDevice =="thermostat" and emsCommand =="temp":
        payloadString = "{\"cmd\":\"temp\" ,\"data\":"+str(emsData)+", \"hc\":"+str(emsHc)+"}"
        mqttClient.Publish(topicBase+"thermostat", payloadString)
    if emsDevice =="thermostat" and emsCommand =="wwmode":
        payloadString = "{\"cmd\":\"wwmode\" ,\"data\":\""+str(emsData)+"\"}"
        mqttClient.Publish(topicBase+"thermostat", payloadString)
    if emsDevice =="thermostat" and emsCommand =="mode":
        payloadString = "{\"cmd\":\"mode\" ,\"data\":\""+str(emsData)+"\", \"hc\":"+str(emsHc)+"}"
        mqttClient.Publish(topicBase+"thermostat", payloadString)
    if emsDevice =="boiler":
        payloadString = "{\"cmd\":\""+emsCommand+"\" ,\"data\":\""+str(emsData)+"\"}"
        mqttClient.Publish(topicBase+"boiler", payloadString)


