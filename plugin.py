# Domoticz Python Plugin for EMS bus Wi-Fi Gateway with Proddy's EMS-ESP firmware
# last update: October 2021
# Author: bbqkees @www.bbqkees-electronics.nl
# Credits to @Gert05 for creating the first version of this plugin
# https://github.com/bbqkees/ems-esp-domoticz-plugin
# Proddy's EMS-ESP repository: https://github.com/emsesp/EMS-ESP32
# Product Wiki: https://bbqkees-electronics.nl/wiki/
#
# This is the development and debug version. Use the master version for production.
#
"""
<plugin key="ems-gateway" name="EMS bus Wi-Fi Gateway DEV-multi2" version="1.3b16">
    <description>
      EMS bus Wi-Fi Gateway plugin version 1.3b16 20-MAY-2021 (DEVELOPMENT multiple instances)<br/>
      Plugin to interface with EMS bus equipped Bosch brands boilers together with the EMS-ESP firmware  '<a href="https://github.com/emsesp/EMS-ESP32">from Proddy</a>'<br/>
      <br/>
      Please look at the  <a href="https://bbqkees-electronics.nl/wiki/">Product Wiki</a> for all instructions.<br/>
      <i>Please update the firmware of the Gateway to V3 or higher for best functionality.</i><br/>
      Automatically creates Domoticz devices for connected EMS devices.<br/> Do not forget to "Accept new Hardware Devices" on first run.<br/><br/>
      For this plugin to work you need to set the MQTT format to 'nested' in the EMS-ESP web interface.
    <br/>
    Parameters:<br/>
    <b>MQTT server and port</b><br/>
    MQTT Server address is usually, but not always, at the same address as the machine where Domoticz is running. So the 'local' machine at 127.0.0.1.<br/>
    The default port is 1883 and no user or password.<br/>
    <b>MQTT topic</b><br/>
    The default MQTT topic root this plugin will look in is 'ems-esp/' That forward slash at the end should not be omitted.<br/>
    Make sure that this is set accordingly in the EMS-ESP firmware settings.<br/>
    You can change it here or in the Gateway web interface if its set differently.<br/>
    <br/>
    You need to add a new hardware instance of the plugin for every set of EMS devices.<br/>
    So if you have a boiler, thermostat and mixer module, you need to add a EMS-ESP hardware in Domoticz for the boiler and a second for the thermostat,
    and a third EMS-ESP hardware for the mixer module (You only install the plugin once, just create more hardware of the EMS-ESP type in Domoticz).<br/>
    </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Username" label="Username" width="300px"/>
        <param field="Password" label="Password" width="300px" default="" password="true"/>
        <param field="Mode1" label="Topic base" width="300px" required="true" default="ems-esp/"/>
        <param field="Mode5" label="EMS Devices" width="100px">
            <options>
                <option label="Boiler" value="boiler"/>
                <option label="Heatpump" value="heatpump"/>
                <option label="Thermostat" value="thermostat"/>
                <option label="Solar + mixer modules" value="solar_mixers"/>
                <option label="Dallas sensors" value="dallas"/>

            </options>
        </param>    
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
# And even well before you reach the limit the device list of Domoticz may get messed up.
#
# Boiler data (topic boiler_data):
# ID 1 to 59 (1 and 3 still free)
# ID 40 and up for new heat pump parameters
# ID 64 to 69 also reserved here
# 
# Shower data (topic shower_data):
# ID 60 to 63
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
# Heat pump parameters (topic heatpump_data):
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
# from Domoticz import Devices, Parameters
import json
import time
from mqtt import MqttClient


class BasePlugin:
    mqttClient = None

    def __init__(self):
        return

    def onStart(self):
        self.debugging = Parameters["Mode6"]
        
        if self.debugging == "Verbose+":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Verbose":
            Domoticz.Debugging(2+4+8+16+64)
        if self.debugging == "Debug":
            Domoticz.Debugging(2+4+8)
    
        self.EMSdevice = Parameters["Mode5"]
        Domoticz.Log("EMS hardware type is: ")
        Domoticz.Log(self.EMSdevice)

        self.checkDevices()

        self.topicBase = Parameters["Mode1"].replace(" ", "")

        self.topicsList = list(["thermostat_data", "boiler_data", "boiler_data_main", "boiler_data_ww", "sensor_data", "sensors", "dallassensor_data", "shower_data", "mixing_data", "solar_data", "hp_data", "heating_active", "tapwater_active", "status", "info", 
                                "mixing_data1", "mixing_data2", "mixing_data3", "mixing_data4", "mixing_data5", "mixing_data6", "mixing_data7", "mixing_data8", "mixing_data9", "mixing_data10", "heatpump_data"])
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
        self.onCommand(self.mqttClient, Unit, Command, Level, Color)

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
            self.onMqttMessage(topic, message)
    

    def checkDevices(self):
    # not used for now 
        Domoticz.Debug("checkDevices called")

    # onMqttMessage decodes the MQTT messages and updates the Domoticz parameters
    def onMqttMessage(self, topic, payload):

        # Convert all keys in the MQTT payload to lowercase before processing them (for compatibility with EMS-ESP V2.2).
        # EMS-ESP V2 has the keys in camelcase notation, V3 uses all lowercase.
        payload =  {k.lower(): v for k, v in payload.items()}

        if self.EMSdevice == "boiler" or self.EMSdevice == "heatpump":
            # In firmware V2.1 and higher the tapwater_active and heating_active are also included in boiler_data.
            # However, tapwater_active and heating_active are published on state change while boiler_data is periodical.
            # So its best to look at the separate topics here to keep the state in Domoticz in sync.

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

            # Process the shower_data topic.
            if "shower_data" in topic:
                if "duration" in payload:
                    text=payload["duration"]
                    if 60 not in Devices:
                        Domoticz.Debug("Create text device (shower duration)")
                        Domoticz.Device(Name="Shower duration", Unit=60, Type=243, Subtype=19).Create()
                    updateDevice(60, 243, 19, text)

        if self.EMSdevice == "thermostat":
            # Process the thermostat parameters of each heating zone
            if "thermostat_data" in topic:
                if "hc1" in payload:
                    payloadHc1 = payload["hc1"]
                    if "currtemp" in payloadHc1:
                        temp=round(float(payloadHc1["currtemp"]), 1)
                        if 111 not in Devices:
                            Domoticz.Debug("Create Temperature Device HC1")
                            Domoticz.Device(Name="EMS thermostat current temp HC1", Unit=111, Type=80, Subtype=5).Create()
                        updateDevice(111, 80, 5, temp)
                    if "seltemp" in payloadHc1:
                        temp=payloadHc1["seltemp"]
                        if 112 not in Devices:
                            Domoticz.Debug("Create Thermostat Setpoint Device HC1")
                            Domoticz.Device(Name="EMS thermostat setpoint HC1", Unit=112, Type=242, Subtype=1).Create()
                        updateDevice(112, 80, 5, temp)
                    if "mode" in payloadHc1:
                        thMode=payloadHc1["mode"]
                        if 113 not in Devices:
                            Domoticz.Debug("Create Thermostat mode selector HC1")
                            Options = { "LevelActions" : "||||",
                                "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                        }
                            Domoticz.Device(Name="Thermostat mode HC1", Unit=113, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(113, str(thMode))
                    if "modetype" in payloadHc1:
                        thMode=payloadHc1["modetype"]
                        if 114 not in Devices:
                            Domoticz.Debug("Create Thermostat mode type HC1")
                            Options = { "LevelActions" : "||||",
                                "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                        }
                            Domoticz.Device(Name="Thermostat mode type HC1", Unit=114, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(114, str(thMode))

                if "hc2" in payload:
                    payloadHc2 = payload["hc2"]
                    if "currtemp" in payloadHc2:
                        temp=round(float(payloadHc2["currtemp"]), 1)
                        if 121 not in Devices:
                            Domoticz.Debug("Create Temperature Device HC2")
                            Domoticz.Device(Name="EMS thermostat current temp HC2", Unit=121, Type=80, Subtype=5).Create()
                        updateDevice(121, 80, 5, temp)
                    if "seltemp" in payloadHc2:
                        temp=payloadHc2["seltemp"]
                        if 122 not in Devices:
                            Domoticz.Debug("Create Thermostat Setpoint Device HC2")
                            Domoticz.Device(Name="EMS thermostat setpoint HC2", Unit=122, Type=242, Subtype=1).Create()
                        updateDevice(122, 80, 5, temp)
                    if "mode" in payloadHc2:
                        thMode=payloadHc2["mode"]
                        if 123 not in Devices:
                            Domoticz.Debug("Create Thermostat mode selector HC2")
                            Options = { "LevelActions" : "||||",
                                        "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                        "LevelOffHidden" : "true",
                                        "SelectorStyle" : "0" 
                                        }
                            Domoticz.Device(Name="Thermostat mode HC2", Unit=123, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(123, str(thMode))
                    if "modetype" in payloadHc2:
                        thMode=payloadHc2["modetype"]
                        if 124 not in Devices:
                            Domoticz.Debug("Create Thermostat mode type HC2")
                            Options = { "LevelActions" : "||||",
                                "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                        }
                            Domoticz.Device(Name="Thermostat mode type HC2", Unit=124, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(124, str(thMode))

                if "hc3" in payload:
                    payloadHc3 = payload["hc3"]
                    if "currtemp" in payloadHc3:
                        temp=round(float(payloadHc3["currtemp"]), 1)
                        if 131 not in Devices:
                            Domoticz.Debug("Create Temperature Device HC3")
                            Domoticz.Device(Name="EMS thermostat current temp HC3", Unit=131, Type=80, Subtype=5).Create()
                        updateDevice(131, 80, 5, temp)
                    if "seltemp" in payloadHc3:
                        temp=payloadHc3["seltemp"]
                        if 132 not in Devices:
                            Domoticz.Debug("Create Thermostat Setpoint Device HC3")
                            Domoticz.Device(Name="EMS thermostat setpoint HC3", Unit=132, Type=242, Subtype=1).Create()
                        updateDevice(132, 80, 5, temp)
                    if "mode" in payloadHc3:
                        thMode=payloadHc3["mode"]
                        if 133 not in Devices:
                            Domoticz.Debug("Create Thermostat mode selector HC3")
                            Options = { "LevelActions" : "||||",
                                        "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                    "LevelOffHidden" : "true",
                                    "SelectorStyle" : "0" 
                                        }
                            Domoticz.Device(Name="Thermostat mode HC3", Unit=133, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(133, str(thMode))
                    if "modetype" in payloadHc3:
                        thMode=payloadHc3["modetype"]
                        if 134 not in Devices:
                            Domoticz.Debug("Create Thermostat mode type HC3")
                            Options = { "LevelActions" : "||||",
                                "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                    }
                            Domoticz.Device(Name="Thermostat mode type HC3", Unit=134, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(134, str(thMode))

                if "hc4" in payload:
                    payloadHc4 = payload["hc4"]
                    if "currtemp" in payloadHc4:
                        temp=round(float(payloadHc4["currtemp"]), 1)
                        if 141 not in Devices:
                            Domoticz.Debug("Create Temperature Device HC4")
                            Domoticz.Device(Name="EMS thermostat current temp HC4", Unit=141, Type=80, Subtype=5).Create()
                        updateDevice(141, 80, 5, temp)
                    if "seltemp" in payloadHc4:
                        temp=payloadHc4["seltemp"]
                        if 142 not in Devices:
                            Domoticz.Debug("Create Thermostat Setpoint Device HC4")
                            Domoticz.Device(Name="EMS thermostat setpoint HC4", Unit=142, Type=242, Subtype=1).Create()
                        updateDevice(142, 80, 5, temp)
                    if "mode" in payloadHc4:
                        thMode=payloadHc4["mode"]
                        if 143 not in Devices:
                            Domoticz.Debug("Create Thermostat mode selector HC4")
                            Options = { "LevelActions" : "||||",
                                        "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                        "LevelOffHidden" : "true",
                                        "SelectorStyle" : "0" 
                                        }
                            Domoticz.Device(Name="Thermostat mode HC4", Unit=143, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(143, str(thMode))
                    if "modetype" in payloadHc4:
                        thMode=payloadHc4["modetype"]
                        if 144 not in Devices:
                            Domoticz.Debug("Create Thermostat mode type HC4")
                            Options = { "LevelActions" : "||||",
                                "LevelNames"   : "off|auto|day|night|manual|heat|eco|nofrost",
                                "LevelOffHidden" : "true",
                                "SelectorStyle" : "0" 
                                        }
                        Domoticz.Device(Name="Thermostat mode type HC4", Unit=144, TypeName="Selector Switch", Switchtype=18, Options=Options, Used=1).Create()
                        setSelectorByName(144, str(thMode))

        if self.EMSdevice == "boiler" or self.EMSdevice == "heatpump":
                # Process the boiler parameters
                # Somewhere in 2.1bX this topic was split into two, one for heating and one for warm water.
            if "boiler_data" or "boiler_data_main" or "boiler_data_ww" in topic:
                if "syspress" in payload:
                    pressure=payload["syspress"]
                    if 2 not in Devices:
                        Domoticz.Debug("Create System Pressure Device")
                        Domoticz.Device(Name="Boiler system pressure", Unit=2, Type=243, Subtype=9).Create()
                    updateDevice(2, 243, 9, pressure)
                # 11 to 16 + 25 to 27 temp
                if "selflowtemp" in payload:
                    temp=round(float(payload["selflowtemp"]), 1)
                    if 11 not in Devices:
                        Domoticz.Debug("Create temperature device (selFlowTemp)")
                        Domoticz.Device(Name="Boiler selected flow temperature", Unit=11, Type=80, Subtype=5).Create()
                    updateDevice(11, 80, 5, temp)
                if "outdoortemp" in payload:
                    temp=round(float(payload["outdoortemp"]), 1)
                    if 12 not in Devices:
                        Domoticz.Debug("Create temperature device (outdoorTemp)")
                        Domoticz.Device(Name="Boiler connected outdoor temperature", Unit=12, Type=80, Subtype=5).Create()
                    updateDevice(12, 80, 5, temp)
                if "wwcurtemp" in payload:
                    temp=round(float(payload["wwcurtemp"]), 1)
                    if 13 not in Devices:
                        Domoticz.Debug("Create temperature device (wWCurTemp)")
                        Domoticz.Device(Name="Boiler warm water current temperature", Unit=13, Type=80, Subtype=5).Create()
                    updateDevice(13, 80, 5, temp)
                if "curflowtemp" in payload:
                    temp=round(float(payload["curflowtemp"]), 1)
                    if 14 not in Devices:
                        Domoticz.Debug("Create temperature device (curFlowTemp)")
                        Domoticz.Device(Name="Boiler current flow temperature", Unit=14, Type=80, Subtype=5).Create()
                    updateDevice(14, 80, 5, temp)
                if "rettemp" in payload:
                    temp=round(float(payload["rettemp"]), 1)
                    if 15 not in Devices:
                        Domoticz.Debug("Create temperature device (retTemp)")
                        Domoticz.Device(Name="Boiler return temperature", Unit=15, Type=80, Subtype=5).Create()
                    updateDevice(15, 80, 5, temp)
                if "boiltemp" in payload:
                    temp=round(float(payload["boiltemp"]), 1)
                    if 16 not in Devices:
                        Domoticz.Debug("Create temperature device (boiltemp)")
                        Domoticz.Device(Name="Boiler temperature", Unit=16, Type=80, Subtype=5).Create()
                    updateDevice(16, 80, 5, temp)
                if "wwseltemp" in payload:
                    temp=round(float(payload["wwseltemp"]), 1)
                    if 25 not in Devices:
                        Domoticz.Debug("Create temperature device (wWSelTemp)")
                        Domoticz.Device(Name="ww selected temperature", Unit=25, Type=80, Subtype=5).Create()
                    updateDevice(25, 80, 5, temp)
                if "wwdesiredtemp" in payload:
                    temp=round(float(payload["wwdesiredtemp"]), 1)
                    if 26 not in Devices:
                        Domoticz.Debug("Create temperature device (wWDesiredTemp)")
                        Domoticz.Device(Name="ww desired temperature", Unit=26, Type=80, Subtype=5).Create()
                    updateDevice(26, 80, 5, temp)
                if "heatingtemp" in payload:
                    temp=round(float(payload["heatingtemp"]), 1)
                    if 27 not in Devices:
                        Domoticz.Debug("Create temperature device (heatingtemp)")
                        Domoticz.Device(Name="Heating temperature", Unit=27, Type=80, Subtype=5).Create()
                    updateDevice(27, 80, 5, temp)
                # 29 ampere
                if "flamecurr" in payload:
                    temp=round(float(payload["flamecurr"]), 1)
                    if 29 not in Devices:
                        Domoticz.Debug("Create ampere device (flameCurr)")
                        Domoticz.Device(Name="Boiler flame current", Unit=29, Type=243, Subtype=23).Create()
                    updateDevice(29, 243, 23, temp)
                #21 to 24 + 28 + 38 + 39 percentage
                if "selburnpow" in payload:
                    percentage=payload["selburnpow"]
                    if 21 not in Devices:
                        Domoticz.Debug("Create percentage device (selBurnPow)")
                        Domoticz.Device(Name="Boiler selected power", Unit=21, Type=243, Subtype=6).Create()
                    updateDevice(21, 243, 6, percentage)
                if "curburnpow" in payload:
                    percentage=payload["curburnpow"]
                    if 22 not in Devices:
                        Domoticz.Debug("Create percentage device (curBurnPow)")
                        Domoticz.Device(Name="Boiler current power", Unit=22, Type=243, Subtype=6).Create()
                    updateDevice(22, 243, 6, percentage)
                if "pumpmod" in payload:
                    percentage=payload["pumpmod"]
                    if 23 not in Devices:
                        Domoticz.Debug("Create percentage device (pumpMod)")
                        Domoticz.Device(Name="Boiler pump modulation", Unit=23, Type=243, Subtype=6).Create()
                    updateDevice(23, 243, 6, percentage)
                if "wwcurflow" in payload:
                    percentage=payload["wwcurflow"]
                    if 24 not in Devices:
                        Domoticz.Debug("Create percentage device (wWCurFlow)")
                        Domoticz.Device(Name="Boiler warm water flow", Unit=24, Type=243, Subtype=6).Create()
                    updateDevice(24, 243, 6, percentage)
                if "wwcircpump" in payload:
                    percentage=payload["wwcircpump"]
                    if 28 not in Devices:
                        Domoticz.Debug("Create percentage device (wWCircPump)")
                        Domoticz.Device(Name="ww pump modulation", Unit=28, Type=243, Subtype=6).Create()
                    updateDevice(28, 243, 6, percentage)
                if "pumpmodmax" in payload:
                    percentage=payload["pumpmodmax"]
                    if 38 not in Devices:
                        Domoticz.Debug("Create percentage device (pumpModMax)")
                        Domoticz.Device(Name="pump modulation max", Unit=38, Type=243, Subtype=6).Create()
                    updateDevice(38, 243, 6, percentage)
                if "pumpmodmin" in payload:
                    percentage=payload["pumpmodmin"]
                    if 39 not in Devices:
                        Domoticz.Debug("Create percentage device (pumpMod_Min)")
                        Domoticz.Device(Name="pump modulation min", Unit=39, Type=243, Subtype=6).Create()
                    updateDevice(39, 243, 6, percentage)
                #4 to 10 switch
                if "burngas" in payload:
                    switchstate=payload["burngas"]
                    if 4 not in Devices:
                        Domoticz.Debug("Create on/off switch (burnGas)")
                        Domoticz.Device(Name="Boiler gas", Unit=4, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(4, 244, 73, switchstate)
                if "fanwork" in payload:
                    switchstate=payload["fanwork"]
                    if 5 not in Devices:
                        Domoticz.Debug("Create on/off switch (fanWork)")
                        Domoticz.Device(Name="Boiler fan", Unit=5, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(5, 244, 73, switchstate)
                if "ignwork" in payload:
                    switchstate=payload["ignwork"]
                    if 6 not in Devices:
                        Domoticz.Debug("Create on/off switch (ignWork)")
                        Domoticz.Device(Name="Boiler ingnition", Unit=6, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(6, 244, 73, switchstate)
                if "heatpump" in payload:
                    switchstate=payload["heatpump"]
                    if 7 not in Devices:
                        Domoticz.Debug("Create on/off switch (heatPump)")
                        Domoticz.Device(Name="Boiler heating pump", Unit=7, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(7, 244, 73, switchstate)
                if "wwactivated" in payload:
                    switchstate=payload["wwactivated"]
                    if 8 not in Devices:
                        Domoticz.Debug("Create on/off switch (wWActivated)")
                        Domoticz.Device(Name="Boiler warm water", Unit=8, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(8, 244, 73, switchstate)
                if "wwheat" in payload:
                    switchstate=payload["wwheat"]
                    if 9 not in Devices:
                        Domoticz.Debug("Create on/off switch (wWHeat)")
                        Domoticz.Device(Name="Boiler warm water heating", Unit=9, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(9, 244, 73, switchstate)
                if "wwcirc" in payload:
                    switchstate=payload["wwcirc"]
                    if 10 not in Devices:
                        Domoticz.Debug("Create on/off switch (wWCirc)")
                        Domoticz.Device(Name="Boiler warm water circulation", Unit=10, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(10, 244, 73, switchstate)
                if "servicecode" in payload:
                    text=payload["servicecode"]
                    if 18 not in Devices:
                        Domoticz.Debug("Create text device (serviceCode)")
                        Domoticz.Device(Name="Boiler Service code", Unit=18, Type=243, Subtype=19).Create()
                    updateDevice(18, 243, 19, text)
                if "servicecodenumber" in payload:
                    text=payload["servicecodenumber"]
                    if 19 not in Devices:
                        Domoticz.Debug("Create text device (serviceCodeNumber)")
                        Domoticz.Device(Name="Boiler Service code number", Unit=19, Type=243, Subtype=19).Create()
                    updateDevice(19, 243, 19, text)
                if "wwstarts" in payload:
                    text=payload["wwstarts"]
                    if 32 not in Devices:
                        Domoticz.Debug("Create counter (wwstarts)")
                        Domoticz.Device(Name="ww starts", Unit=32, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(32, 113, 0, text)
                if "wwworkm" in payload:
                    text=payload["wwworkm"]
                    if 33 not in Devices:
                        Domoticz.Debug("Create counter (wWWorkM)")
                        Domoticz.Device(Name="ww work minutes", Unit=33, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(33, 113, 0, text)
                if "ubauptime" in payload:
                    text=payload["ubauptime"]
                    if 34 not in Devices:
                        Domoticz.Debug("Create counter (UBAuptime)")
                        Domoticz.Device(Name="Boiler UBA uptime", Unit=34, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(34, 113, 0, text)
                if "burnstarts" in payload:
                    text=payload["burnstarts"]
                    if 35 not in Devices:
                        Domoticz.Debug("Create counter (burnStarts)")
                        Domoticz.Device(Name="boiler burner starts", Unit=35, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(35, 113, 0, text)
                if "burnworkmin" in payload:
                    text=payload["burnworkmin"]
                    if 36 not in Devices:
                        Domoticz.Debug("Create counter (burnWorkMin)")
                        Domoticz.Device(Name="boiler burner working minutes", Unit=36, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(36, 113, 0, text)
                if "heatworkmin" in payload:
                    text=payload["heatworkmin"]
                    if 37 not in Devices:
                        Domoticz.Debug("Create counter (heatWorkMin)")
                        Domoticz.Device(Name="boiler heating working minutes", Unit=37, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(37, 113, 0, text)
                # heat pump uptime parameters
                if "uptimecompheating" in payload:
                    text=payload["uptimecompheating"]
                    if 40 not in Devices:
                        Domoticz.Debug("Create counter (upTimeCompHeating)")
                        Domoticz.Device(Name="Operating time compressor heating", Unit=40, Type=113, Subtype=0, Switchtype=3).Create()
                if "uptimecompcooling" in payload:
                    text=payload["upTimeCompCooling"]
                    if 41 not in Devices:
                        Domoticz.Debug("Create counter (upTimeCompCooling)")
                        Domoticz.Device(Name="Operating time compressor cooling", Unit=41, Type=113, Subtype=0, Switchtype=3).Create()
                if "uptimecompww" in payload:
                    text=payload["uptimecompww"]
                    if 42 not in Devices:
                        Domoticz.Debug("Create counter (upTimeCompWw)")
                        Domoticz.Device(Name="Operating time compressor warm water", Unit=42, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(41, 113, 0, text)
                if "heatingstarts" in payload:
                    text=payload["heatingstarts"]
                    if 43 not in Devices:
                        Domoticz.Debug("Create counter (heatingStarts)")
                        Domoticz.Device(Name="Heating starts (control)", Unit=43, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(43, 113, 0, text)
                if "coolingstarts" in payload:
                    text=payload["coolingstarts"]
                    if 44 not in Devices:
                        Domoticz.Debug("Create counter (coolingStarts)")
                        Domoticz.Device(Name="Cooling starts (control)", Unit=44, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(44, 113, 0, text)
                if "wwstarts2" in payload:
                    text=payload["wwstarts2"]
                    if 45 not in Devices:
                        Domoticz.Debug("Create counter (wWStarts2)")
                        Domoticz.Device(Name="Warm water starts (control)", Unit=45, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(45, 113, 0, text)
                if "wwcomfort" in payload:
                    text=payload["wwcomfort"]
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
                if "wwmode" in payload:
                    text=payload["wwmode"]
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
                # new energy devices mainly for heatpumps
                if "nrgconstotal" in payload:
                    text=payload["nrgconstotal"]
                    if 50 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgConsTotal)")
                        Domoticz.Device(Name="Energy consumption total", Unit=50, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(50, 113, 0, text)
                if "auxelecheatnrgconstotal" in payload:
                    text=payload["auxelecheatnrgconstotal"]
                    if 51 not in Devices:
                        Domoticz.Debug("Create energy counter (auxElecHeatNrgConsTotal)")
                        Domoticz.Device(Name="uxiliary electrical heater energy consumption total", Unit=51, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(51, 113, 0, text)
                if "auxelecheatnrgconsheating" in payload:
                    text=payload["auxelecheatnrgconsheating"]
                    if 52 not in Devices:
                        Domoticz.Debug("Create energy counter (auxElecHeatNrgConsHeating)")
                        Domoticz.Device(Name="Auxiliary electrical heater energy consumption heating", Unit=52, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(52, 113, 0, text)
                if "auxelecheatnrgconsdhw" in payload:
                    text=payload["auxelecheatnrgconsdhw"]
                    if 53 not in Devices:
                        Domoticz.Debug("Create energy counter (auxElecHeatNrgConsDHW)")
                        Domoticz.Device(Name="Auxiliary electrical heater energy consumption DHW", Unit=53, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(53, 113, 0, text)
                if "nrgconscomptotal" in payload:
                    text=payload["nrgconscomptotal"]
                    if 54 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgConsCompTotal)")
                        Domoticz.Device(Name="Energy consumption compressor total", Unit=54, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(54, 113, 0, text)
                if "nrgconscompheating" in payload:
                    text=payload["nrgconscompheating"]
                    if 55 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgConsCompHeating)")
                        Domoticz.Device(Name="Energy consumption compressor heating", Unit=55, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(55, 113, 0, text)
                if "nrgconscompww" in payload:
                    text=payload["nrgconscompWw"]
                    if 56 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgConsCompWw)")
                        Domoticz.Device(Name="Energy consumption compressor warm water", Unit=56, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(56, 113, 0, text)
                if "nrgconscompcooling" in payload:
                    text=payload["nrgconscompcooling"]
                    if 57 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgConsCompCooling)")
                        Domoticz.Device(Name="Energy consumption compressor total", Unit=57, Type=113, Subtype=0, Switchtype=0).Create()
                    updateDevice(57, 113, 0, text)
                if "nrgsupptotal" in payload:
                    text=payload["nrgsupptotal"]
                    if 58 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgSuppTotal)")
                        Domoticz.Device(Name="Energy supplied total", Unit=58, Type=113, Subtype=0, Switchtype=4).Create()
                    updateDevice(58, 113, 0, text)
                if "nrgsuppheating" in payload:
                    text=payload["nrgsuppheating"]
                    if 59 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgSuppHeating)")
                        Domoticz.Device(Name="Energy supplied heating", Unit=59, Type=113, Subtype=0, Switchtype=4).Create()
                    updateDevice(59, 113, 0, text)
                if "nrgsuppww" in payload:
                    text=payload["nrgsuppww"]
                    if 64 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgSuppWw)")
                        Domoticz.Device(Name="Energy supplied warm water", Unit=64, Type=113, Subtype=0, Switchtype=4).Create()
                    updateDevice(64, 113, 0, text)
                if "nrgsuppcooling" in payload:
                    text=payload["nrgsuppcooling"]
                    if 65 not in Devices:
                        Domoticz.Debug("Create energy counter (nrgSuppCooling)")
                        Domoticz.Device(Name="Energy supplied cooling", Unit=65, Type=113, Subtype=0, Switchtype=4).Create()
                    updateDevice(65, 113, 0, text)

        if self.EMSdevice == "heatpump":
            # Decode heat_pump data
            # These sensors have a Domoticz ID reserved in the range 201 to 209
            # airHumidity dewTemperature 
            if "heatpump_data" in topic:
                if "airhumidity" in payload:
                    hum=round(float(payload["airhumidity"]), 1)
                    if 201 not in Devices:
                        Domoticz.Debug("Create humidity device (airHumidity)")
                        Domoticz.Device(Name="Heatpump air humidity", Unit=201, Type=81, Subtype=1).Create()
                    updateDevice(201, 81, 1, hum)    
                if "dewtemperature" in payload:
                    temp=round(float(payload["dewtemperature"]), 1)
                    if 16 not in Devices:
                        Domoticz.Debug("Create temperature device (dewTemperature)")
                        Domoticz.Device(Name="Boiler temperature", Unit=202, Type=80, Subtype=5).Create()
                    updateDevice(202, 80, 5, temp)

        if self.EMSdevice == "dallas":
            # Decode sensors
            # These sensors have a Domoticz ID reserved in the range 220 to 239
            # This creates Domoticz devices only if a sensor has been received in the topic message.
            if "sensor_data" or "sensors" or "dallassensor_data" in topic:
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

        if self.EMSdevice == "solar_mixers":
            # Decode solar module
            # These devices have a Domoticz ID reserved in the range 80 to 99
            if "solar_data" in topic:
                if "collectortemp" in payload:
                    temp=round(float(payload["collectortemp"]), 1)
                    if 81 not in Devices:
                        Domoticz.Debug("Create temperature device (Solar module collectortemp)")
                        Domoticz.Device(Name="Solar Module collector", Unit=81, Type=80, Subtype=5).Create()
                    updateDevice(81, 80, 5, temp)
                if "tankbottomtemp" in payload:
                    temp=round(float(payload["tankbottomtemp"]), 1)
                    if 82 not in Devices:
                        Domoticz.Debug("Create temperature device (Solar module bottomtemp)")
                        Domoticz.Device(Name="Solar Module bottom", Unit=82, Type=80, Subtype=5).Create()
                    updateDevice(82, 80, 5, temp)
                if "solarpump" in payload:
                    switchstate=payload["solarpump"]
                    if 83 not in Devices:
                        Domoticz.Debug("Create on/off switch (Solar module pump)")
                        Domoticz.Device(Name="Solar module pump", Unit=83, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(83, 244, 73, switchstate)
                if "solarpumpmodulation" in payload:
                    percentage=payload["solarpumpmodulation"]
                    if 84 not in Devices:                
                        Domoticz.Debug("Create percentage device (Solar module pump modulation)")
                        Domoticz.Device(Name="Solar module pump modulation", Unit=84, Type=243, Subtype=6).Create()
                    updateDevice(84, 243, 6, percentage)
                if "pumpworkmin" in payload:
                    text=payload["pumpworkmin"]
                    if 85 not in Devices:   
                        Domoticz.Debug("Create counter (solarPumpWorkMin)")
                        Domoticz.Device(Name="solar pump working minutes", Unit=85, Type=113, Subtype=0, Switchtype=3).Create()
                    updateDevice(85, 113, 0, text)
                if "cylinderpumpmodulation" in payload:
                    percentage=payload["cylinderpumpmodulation"]
                    if 86 not in Devices:                
                        Domoticz.Debug("Create percentage device (Solar module cylinderPumpModulation)")
                        Domoticz.Device(Name="Solar module cylinderPumpModulation", Unit=86, Type=243, Subtype=6).Create()
                    updateDevice(86, 243, 6, percentage)
                if "valvestatus" in payload:
                    switchstate=payload["valvestatus"]
                    if 87 not in Devices:
                        Domoticz.Debug("Create on/off switch (Solar module valveStatus)")
                        Domoticz.Device(Name="Solar module valveStatus", Unit=87, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(87, 244, 73, switchstate)
                if "tankheated" in payload:
                    switchstate=payload["tankheated"]
                    if 88 not in Devices:
                        Domoticz.Debug("Create on/off switch (Solar module tankHeated)")
                        Domoticz.Device(Name="Solar module tankHeated", Unit=88, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(88, 244, 73, switchstate)
                if "collectorshutdown" in payload:
                    switchstate=payload["collectorshutdown"]
                    if 89 not in Devices:
                        Domoticz.Debug("Create on/off switch (Solar module collectorShutdown)")
                        Domoticz.Device(Name="Solar module collectorShutdown", Unit=89, Type=244, Subtype=73, Switchtype=0).Create()
                    updateDevice(89, 244, 73, switchstate)
                if "energylasthour" in payload:
                    text=payload["energylasthour"]/1000 #Counter is in kWh, value in Wh.
                    if 90 not in Devices:   
                        Domoticz.Debug("Create counter (energyLastHour)")
                        Domoticz.Device(Name="solar pump energyLastHour", Unit=90, Type=113, Subtype=0).Create()
                    updateDevice(90, 113, 0, text)
                if "energytoday" in payload:
                    text=payload["energytoday"]/1000 #Counter is in kWh, value in Wh.
                    if 91 not in Devices:   
                        Domoticz.Debug("Create counter (energyToday)")
                        Domoticz.Device(Name="solar pump energyToday", Unit=91, Type=113, Subtype=0).Create()
                    updateDevice(91, 113, 0, text)
                if "energytotal" in payload:
                    text=payload["energytotal"]
                    if 92 not in Devices:   
                        Domoticz.Debug("Create counter (energyTotal)")
                        Domoticz.Device(Name="solar pump energyTotal", Unit=92, Type=113, Subtype=0).Create()
                    updateDevice(92, 113, 0, text)

            # Decode mixing module data
            # This creates Domoticz devices only if a mixing module topic message has been received.
            # It also creates only those devices for heating circuits in the topic message.
            # Mixer modules for heating zones (topic mixing_dataX)
            # TODO: automate this. Too many possible mixer ID's.
            if "mixing_data1" in topic:
                if "hc1" in payload:
                    payloadHc1 = payload["hc1"]
                    if "pumpmod" in payloadHc1:
                        percentage=payloadHc1["pumpmod"]                    
                        if 151 not in Devices:                
                            Domoticz.Debug("Create percentage device (Mixing module HC1 pump modulation)")
                            Domoticz.Device(Name="Mixing module HC1 pump modulation", Unit=151, Type=243, Subtype=6).Create()
                        updateDevice(151, 243, 6, percentage)
                    if "flowtemp" in payloadHc1:
                        temp=round(float(payloadHc1["flowtemp"]), 1)
                        if 152 not in Devices:
                            Domoticz.Debug("Create temperature device (Mixing module HC1 flowtemp)")
                            Domoticz.Device(Name="Mixing module HC1 flow", Unit=152, Type=80, Subtype=5).Create()
                        updateDevice(152, 80, 5, temp)
                    if "valvestatus" in payloadHc1:
                        switchstate=payloadHc1["valvestatus"]
                        if 153 not in Devices:
                            Domoticz.Debug("Create on/off switch (Mixing module HC1 valvestatus)")
                            Domoticz.Device(Name="Mixing module HC1 valve", Unit=153, Type=244, Subtype=73, Switchtype=0).Create()
                        updateDevice(153, 244, 73, switchstate)

                if "hc2" in payload:
                    payloadHc2 = payload["hc2"]
                    if "pumpmod" in payloadHc2:
                        percentage=payloadHc2["pumpmod"]
                        if 161 not in Devices:                
                            Domoticz.Debug("Create percentage device (Mixing module HC2 pump modulation)")
                            Domoticz.Device(Name="Mixing module HC2 pump modulation", Unit=161, Type=243, Subtype=6).Create()
                        updateDevice(161, 243, 6, percentage)
                    if "flowtemp" in payloadHc2:
                        temp=round(float(payloadHc2["flowtemp"]), 1)
                        if 162 not in Devices:
                            Domoticz.Debug("Create temperature device (Mixing module HC2 flowtemp)")
                            Domoticz.Device(Name="Mixing module HC2 flow", Unit=162, Type=80, Subtype=5).Create()
                        updateDevice(162, 80, 5, temp)
                    if "valvestatus" in payloadHc2:
                        switchstate=payloadHc2["valvestatus"]
                        if 163 not in Devices:
                            Domoticz.Debug("Create on/off switch (Mixing module HC2 valvestatus)")
                            Domoticz.Device(Name="Mixing module HC2 valve", Unit=163, Type=244, Subtype=73, Switchtype=0).Create()
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
                    if "pumpmod" in payloadHc3:
                        percentage=payloadHc3["pumpmod"]
                        updateDevice(171, 243, 6, percentage)
                    if "flowtemp" in payloadHc3:
                        temp=round(float(payloadHc3["flowtemp"]), 1)
                        updateDevice(172, 80, 5, temp)
                    if "valvestatus" in payloadHc3:
                        switchstate=payloadHc3["valvestatus"]
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
                    if "pumpmod" in payloadHc4:
                        percentage=payloadHc4["pumpmod"]
                        updateDevice(181, 243, 6, percentage)
                    if "flowtemp" in payloadHc4:
                        temp=round(float(payloadHc4["flowtemp"]), 1)
                        updateDevice(182, 80, 5, temp)
                    if "valvestatus" in payloadHc4:
                        switchstate=payloadHc4["valvestatus"]
                        updateDevice(183, 244, 73, switchstate)


    # onCommand publishes a MQTT message for each command received from Domoticz
    def onCommand(self, mqttClient, unit, command, level, color):
        self.topicBase = Parameters["Mode1"].replace(" ", "")
        Domoticz.Log("onCommand called for Unit " + str(unit) + ": Parameter '" + str(command) + "', Level: " + str(level))

        if self.EMSdevice == "thermostat":
            # Change a thermostat setpoint for a specific HC
            if (unit in [112, 122, 132, 142]):
                if (str(command) == "Set Level"):
                    sendEmsCommand(mqttClient, "thermostat", "temp", str(level), 1, str(int((unit-102)/10)))

        if self.EMSdevice == "boiler" or self.EMSdevice == "heatpump":
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

        if self.EMSdevice == "thermostat":
            # Change a thermostat mode for a specific HC
            if (unit in [113, 123, 133, 143]):
                dictOptions = Devices[unit].Options
                listLevelNames = dictOptions['LevelNames'].split('|')
                strSelectedName = listLevelNames[int(int(level)/10)]
                Domoticz.Log("Thermostat mode for unit "+str(unit)+"= "+strSelectedName)
                sendEmsCommand(mqttClient, "thermostat", "mode", strSelectedName.lower(), 1, str(int((unit-102)/10)))
    

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
    if (deviceType == 80 and deviceSubType == 5) or (deviceType == 81 and deviceSubType == 1):
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


