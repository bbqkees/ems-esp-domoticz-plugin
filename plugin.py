# Domoticz Python Plugin for EMS bus Wi-Fi Gateway with Proddy's EMS-ESP firmware
# last update: 17 November 2019
# Author: bbqkees
# Credits to @Gert05 for creating the first version of this plugin
# https://github.com/bbqkees/ems-esp-domoticz-plugin
# Proddy's EMS-ESP repository: https://github.com/proddy/EMS-ESP
#
"""
<plugin key="ems-gateway" name="EMS bus Wi-Fi Gateway" version="0.6.1">
    <description>
      Plugin to interface with Bosch boilers together with the EMS-ESP '<a href="https://github.com/proddy/EMS-ESP"> from Proddy</a>' firmware<br/>
      <br/>Support for boiler data, thermostats (current temp and setpoint) and the SM10 solar module. Dallas temp sensors not supported yet.<br/>
      Automatically creates Domoticz devices for connected device.<br/> Do not forget to "Accept new Hardware Devices" on first run<br/>
    Parameters:<br/>
    MQTT Server address is usually, but not always, at the same address as the machine where Domoticz is running. So the 'local' machine at 127.0.0.1.<br/>
    The default port is 1883 and no user or password.<br/>
    You can set whether you have a solar module or not. (This function is not active yet.)<br/>
    The default MQTT topic folder this plugin will look in is 'home/ems-esp'.<br/>
    Make sure that this is set accordingly in the EMS-ESP firmware settings. In the latest versions the default topic is just ems-esp.<br/>
      </description>
    <params>
        <param field="Address" label="MQTT Server address" width="300px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="300px" required="true" default="1883"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="Extra verbose" value="Verbose+"/>
                <option label="Verbose" value="Verbose"/>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal" default="true" />
            </options>
        </param>
        <param field="SM10" label="SM10 solar module" width="75px">
            <options>
                <option label="Yes" value="Yes"/>
                <option label="No" value="No" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import json
import time
from mqtt import MqttClient


class EmsDevices:

    def checkDevices(self):

        # self.SM10 = Parameters["SM10"]

        if 1 not in Devices:
            Domoticz.Debug("Create Temperature Device")
            Domoticz.Device(Name="EMS thermostat current temp", Unit=1, Type=80, Subtype=5).Create()
        if 2 not in Devices:
            Domoticz.Debug("Create System Pressure Device")
            Domoticz.Device(Name="Boiler system pressure", Unit=2, Type=243, Subtype=9).Create()
        if 3 not in Devices:
            Domoticz.Debug("Create Thermostat Setpoint Device")
            Domoticz.Device(Name="EMS thermostat setpoint", Unit=3, Type=242, Subtype=1).Create()
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
            Domoticz.Device(Name="Boiler selected flow temperate", Unit=11, Type=80, Subtype=5).Create()
        if 12 not in Devices:
            Domoticz.Debug("Create temperature device (outdoorTemp)")
            Domoticz.Device(Name="Boiler connected outdoor temperature", Unit=12, Type=80, Subtype=5).Create()
        if 13 not in Devices:
            Domoticz.Debug("Create temperature device (wWCurTmp)")
            Domoticz.Device(Name="Boiler warm water current temperate", Unit=13, Type=80, Subtype=5).Create()
        if 14 not in Devices:
            Domoticz.Debug("Create temperature device (curFlowTemp)")
            Domoticz.Device(Name="Boiler current flow temperate", Unit=14, Type=80, Subtype=5).Create()
        if 15 not in Devices:
            Domoticz.Debug("Create temperature device (retTemp)")
            Domoticz.Device(Name="Boiler return temperate", Unit=15, Type=80, Subtype=5).Create()
        if 16 not in Devices:
            Domoticz.Debug("Create temperature device (boilTemp)")
            Domoticz.Device(Name="Boiler temperate", Unit=16, Type=80, Subtype=5).Create()
        if 17 not in Devices:
            Domoticz.Debug("Create text device (wWComfort)")
            Domoticz.Device(Name="Boiler warm water comfort setting", Unit=17, Type=243, Subtype=19).Create()
        if 18 not in Devices:
            Domoticz.Debug("Create text device (ServiceCode)")
            Domoticz.Device(Name="Boiler Service code", Unit=18, Type=243, Subtype=19).Create()
        if 19 not in Devices:
            Domoticz.Debug("Create text device (ServiceCodeNumber)")
            Domoticz.Device(Name="Boiler Service code number", Unit=19, Type=243, Subtype=19).Create()
        if 20 not in Devices:
            Domoticz.Debug("Create text device (THERMOSTAT_MODE)")
            Domoticz.Device(Name="EMS thermostat mode", Unit=20, Type=243, Subtype=19).Create()
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

        
    def onMqttMessage(self, topic, payload):
        if "hc1" in payload:
            payload = payload["hc1"]
            if "currtemp" in payload:
                temp=round(float(payload["currtemp"]), 1)
                Domoticz.Debug("thermostat_currtemp: Current temp: {}".format(temp))
                if Devices[1].sValue != temp:
                        Devices[1].Update(nValue=1, sValue=str(temp))
            if "seltemp" in payload:
                temp=payload["seltemp"]
                Domoticz.Debug("thermostat_seltemp: Temp setting: {}".format(temp))
                if Devices[3].sValue != temp:
                     Devices[3].Update(nValue=1, sValue=str(temp))
        if "sysPress" in payload:
            pressure=payload["sysPress"]
            Domoticz.Debug("sysPress: Pressure: {}".format(pressure))
            if Devices[2].sValue != pressure:
                Devices[2].Update(nValue=1, sValue=str(pressure))
        #11 to 16 temp
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
        #21 to 24 percentage
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
        if "wWComfort" in payload:
            text=payload["wWComfort"]
            Domoticz.Debug("wWComfort: Text: {}".format(text))
            Devices[17].Update(nValue=1, sValue=str(text))
        if "ServiceCode" in payload:
            text=payload["ServiceCode"]
            Domoticz.Debug("ServiceCode: Text: {}".format(text))
            Devices[18].Update(nValue=1, sValue=str(text)) 
        if "ServiceCodeNumber" in payload:
            text=payload["ServiceCodeNumber"]
            Domoticz.Debug("ServiceCodeNumber: Text: {}".format(text))
            Devices[19].Update(nValue=1, sValue=str(text))
        if "THERMOSTAT_MODE" in payload:
            text=payload["THERMOSTAT_MODE"]
            Domoticz.Debug("THERMOSTAT_MODE: Text: {}".format(text))
            Devices[20].Update(nValue=1, sValue=str(text)) 

    def onCommand(self, mqttClient, unit, command, level, color):
        topic = "home/ems-esp/thermostat_cmd_temp"
        if command == "Set Level":
            mqttClient.Publish(topic, str(level))


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

        self.topics = list(["home/ems-esp/thermostat_data", "home/ems-esp/boiler_data", "home/ems-esp/STATE"])
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
        except ValueError:
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
