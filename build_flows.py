import json

func_init = (
    "const lamps = [];\n"
    "for (let i = 1; i <= 14; i++) {\n"
    "  lamps.push(`MainHouse-Kitchen_${i}`);\n"
    "}\n\n"
    "global.set('rainbowActive', true);\n\n"
    "// Goldener Winkel: benachbarte Lampen haben maximal unterschiedliche Startfarben\n"
    "const goldenAngle = 137.508;\n"
    "const cycles = {};\n"
    "lamps.forEach((lamp, index) => {\n"
    "  cycles[lamp] = (index * goldenAngle) % 360;\n"
    "});\n\n"
    "global.set('lampCycles', cycles);\n"
    "global.set('lamps', lamps);\n\n"
    "node.status({fill: \"green\", shape: \"dot\", text: \"Laeuft - 14 Lampen\"});\n"
    "return {payload: `Rainbow gestartet - ${lamps.length} Lampen`};"
)

func_calculator = (
    "if (!global.get('rainbowActive')) {\n"
    "  return null;\n"
    "}\n\n"
    "const lamps = global.get('lamps');\n"
    "const lampCycles = global.get('lampCycles');\n\n"
    "if (!lamps || !lampCycles) {\n"
    "  node.warn('Lamps oder lampCycles nicht initialisiert');\n"
    "  return null;\n"
    "}\n\n"
    "// 20 Grad pro Tick, Interval 500ms = 40 Grad/Sek\n"
    "Object.keys(lampCycles).forEach(lamp => {\n"
    "  lampCycles[lamp] = (lampCycles[lamp] + 20) % 360;\n"
    "});\n\n"
    "global.set('lampCycles', lampCycles);\n\n"
    "const messages = [];\n"
    "lamps.forEach((lamp) => {\n"
    "  const hue = lampCycles[lamp];\n"
    "  messages.push({\n"
    "    topic: `zigbee2mqtt/${lamp}/set`,\n"
    "    payload: JSON.stringify({\n"
    "      color: { h: hue, s: 100 },\n"
    "      brightness: 200,\n"
    "      transition: 0.4\n"
    "    })\n"
    "  });\n"
    "});\n\n"
    "return [messages];"
)

func_stop = (
    "global.set('rainbowActive', false);\n"
    "node.status({fill: \"red\", shape: \"dot\", text: \"Gestoppt\"});\n"
    "// Output 1 -> Debug | Output 2 -> Lampen zuruecksetzen\n"
    "return [{payload: \"Rainbow gestoppt\"}, {payload: \"restore\"}];"
)

func_restore = (
    "// Alle 14 Spots ueber die Gruppe auf warmes Weiss zuruecksetzen\n"
    "msg.topic = 'zigbee2mqtt/MainHouse-Kitchen_GRP/set';\n"
    "msg.payload = JSON.stringify({\n"
    "  color_temp: 300,\n"
    "  brightness: 180,\n"
    "  transition: 2.0\n"
    "});\n"
    "return msg;"
)

func_temp = (
    "var temp = msg.payload.temperature;\n"
    "msg.payload = { temp_value: temp };\n"
    "msg.tags = { sensor: \"MainHouse-Temp_out-1\" };\n"
    "return msg;"
)

flows = [
    # Globale Konfigurationen
    {"id": "5fdf061cc038ab42", "type": "mqtt-broker", "name": "Brunken-SRV01_Mosquitto",
     "broker": "192.168.68.100", "port": 1883, "clientid": "", "autoConnect": True,
     "usetls": False, "protocolVersion": 4, "keepalive": 60, "cleansession": True,
     "autoUnsubscribe": True, "birthTopic": "", "birthQos": "0", "birthRetain": "false",
     "birthPayload": "", "birthMsg": {}, "closeTopic": "", "closeQos": "0",
     "closeRetain": "false", "closePayload": "", "closeMsg": {}, "willTopic": "",
     "willQos": "0", "willRetain": "false", "willPayload": "", "willMsg": {},
     "userProps": "", "sessionExpiry": ""},

    {"id": "b7f6eae96219cf36", "type": "influxdb", "hostname": "192.168.68.100",
     "port": 8086, "protocol": "http", "database": "sensor_data",
     "name": "BRUNKEN-SRV01_InfluxDB", "usetls": False, "tls": "",
     "influxdbVersion": "1.x", "url": "http://192.168.68.100:8086",
     "timeout": 10, "rejectUnauthorized": False},

    # Tab 1: Flow 1 (Temperatur -> InfluxDB)
    {"id": "a3fd79c206232ef6", "type": "tab", "label": "Flow 1",
     "disabled": False, "info": "", "env": []},

    {"id": "623594d945e43848", "type": "mqtt in", "z": "a3fd79c206232ef6",
     "name": "Temp-out", "topic": "zigbee2mqtt/MainHouse-Temp_out-1",
     "qos": "0", "datatype": "auto-detect", "broker": "5fdf061cc038ab42",
     "nl": False, "rap": True, "rh": 0, "inputs": 0,
     "x": 160, "y": 160, "wires": [["5e3872dd29c9511d", "1b415cd8dc8b369e"]]},

    {"id": "5e3872dd29c9511d", "type": "debug", "z": "a3fd79c206232ef6",
     "name": "debug 1", "active": False, "tosidebar": True, "console": False,
     "tostatus": False, "complete": "false", "statusVal": "", "statusType": "auto",
     "x": 340, "y": 80, "wires": []},

    {"id": "1b415cd8dc8b369e", "type": "function", "z": "a3fd79c206232ef6",
     "name": "function 1", "func": func_temp, "outputs": 1, "timeout": 0,
     "noerr": 0, "initialize": "", "finalize": "", "libs": [],
     "x": 380, "y": 160, "wires": [["db821fe75719b5b7", "312ed9003f4e1c03"]]},

    {"id": "db821fe75719b5b7", "type": "influxdb out", "z": "a3fd79c206232ef6",
     "influxdb": "b7f6eae96219cf36", "name": "Data to DB",
     "measurement": "sensor_data", "precision": "", "retentionPolicy": "",
     "database": "sensor_data", "precisionV18FluxV20": "ms",
     "retentionPolicyV18Flux": "", "org": "organisation", "bucket": "bucket",
     "x": 620, "y": 160, "wires": []},

    {"id": "312ed9003f4e1c03", "type": "debug", "z": "a3fd79c206232ef6",
     "name": "debug 2", "active": False, "tosidebar": True, "console": False,
     "tostatus": False, "complete": "false", "statusVal": "", "statusType": "auto",
     "x": 600, "y": 300, "wires": []},

    # Tab 2: Lichtsteuerung (Rainbow-Effekt)
    {"id": "12df0e2120915233", "type": "tab", "label": "Lichtsteuerung",
     "disabled": False, "info": "", "env": []},

    {"id": "mqtt_start_trigger", "type": "mqtt in", "z": "12df0e2120915233",
     "name": "MQTT: Rainbow Start", "topic": "nodered/rainbow/start",
     "qos": "2", "datatype": "auto", "broker": "5fdf061cc038ab42",
     "nl": False, "rap": True, "rh": 0, "inputs": 0,
     "x": 310, "y": 120, "wires": [["rainbow_init"]]},

    {"id": "rainbow_starter", "type": "inject", "z": "12df0e2120915233",
     "name": "Button: Rainbow starten",
     "props": [{"p": "payload"}], "repeat": "", "crontab": "",
     "once": False, "onceDelay": 0.1, "topic": "",
     "payload": "start", "payloadType": "str",
     "x": 330, "y": 200, "wires": [["rainbow_init"]]},

    {"id": "rainbow_init", "type": "function", "z": "12df0e2120915233",
     "name": "Rainbow initialisieren", "func": func_init,
     "outputs": 1, "noerr": 0, "initialize": "", "finalize": "", "libs": [],
     "x": 560, "y": 160, "wires": [["debug_init"]]},

    {"id": "debug_init", "type": "debug", "z": "12df0e2120915233",
     "name": "Debug Init", "active": True, "tosidebar": True, "console": False,
     "tostatus": False, "complete": "payload", "targetType": "msg",
     "statusVal": "", "statusType": "auto",
     "x": 780, "y": 160, "wires": []},

    {"id": "rainbow_loop", "type": "inject", "z": "12df0e2120915233",
     "name": "Update alle 500ms",
     "props": [{"p": "payload"}], "repeat": "0.5", "crontab": "",
     "once": False, "onceDelay": 0.1, "topic": "",
     "payload": "tick", "payloadType": "str",
     "x": 330, "y": 300, "wires": [["rainbow_calculator"]]},

    {"id": "rainbow_calculator", "type": "function", "z": "12df0e2120915233",
     "name": "Farben berechnen", "func": func_calculator,
     "outputs": 1, "noerr": 0, "initialize": "", "finalize": "", "libs": [],
     "x": 570, "y": 300, "wires": [["mqtt_split", "debug_calc"]]},

    {"id": "debug_calc", "type": "debug", "z": "12df0e2120915233",
     "name": "Debug Hues", "active": False, "tosidebar": True, "console": False,
     "tostatus": False, "complete": "payload", "targetType": "msg",
     "statusVal": "", "statusType": "auto",
     "x": 790, "y": 240, "wires": []},

    {"id": "mqtt_split", "type": "split", "z": "12df0e2120915233",
     "name": "Split fuer jede Lampe", "splt": "\\n", "spltType": "str",
     "arraySplt": 1, "arraySpltType": "auto", "stream": False, "addname": "",
     "x": 790, "y": 340, "wires": [["send_zigbee"]]},

    {"id": "send_zigbee", "type": "mqtt out", "z": "12df0e2120915233",
     "name": "Zigbee2MQTT", "topic": "", "qos": "1", "retain": False,
     "respTopic": "", "contentType": "", "userProps": "", "correl": "", "expiry": "",
     "broker": "5fdf061cc038ab42",
     "x": 980, "y": 340, "wires": []},

    {"id": "mqtt_stop_trigger", "type": "mqtt in", "z": "12df0e2120915233",
     "name": "MQTT: Rainbow Stop", "topic": "nodered/rainbow/stop",
     "qos": "2", "datatype": "auto", "broker": "5fdf061cc038ab42",
     "nl": False, "rap": True, "rh": 0, "inputs": 0,
     "x": 310, "y": 460, "wires": [["stop_handler"]]},

    {"id": "rainbow_stopper", "type": "inject", "z": "12df0e2120915233",
     "name": "Button: Rainbow stoppen",
     "props": [{"p": "payload"}], "repeat": "", "crontab": "",
     "once": False, "onceDelay": 0.1, "topic": "",
     "payload": "stop", "payloadType": "str",
     "x": 330, "y": 540, "wires": [["stop_handler"]]},

    {"id": "stop_handler", "type": "function", "z": "12df0e2120915233",
     "name": "Stop", "func": func_stop,
     "outputs": 2, "noerr": 0, "initialize": "", "finalize": "", "libs": [],
     "x": 560, "y": 500, "wires": [["debug_stop"], ["restore_func"]]},

    {"id": "debug_stop", "type": "debug", "z": "12df0e2120915233",
     "name": "Debug Stop", "active": True, "tosidebar": True, "console": False,
     "tostatus": False, "complete": "payload", "targetType": "msg",
     "statusVal": "", "statusType": "auto",
     "x": 780, "y": 460, "wires": []},

    {"id": "restore_func", "type": "function", "z": "12df0e2120915233",
     "name": "Lampen zuruecksetzen", "func": func_restore,
     "outputs": 1, "noerr": 0, "initialize": "", "finalize": "", "libs": [],
     "x": 790, "y": 540, "wires": [["restore_mqtt"]]},

    {"id": "restore_mqtt", "type": "mqtt out", "z": "12df0e2120915233",
     "name": "Zigbee2MQTT Restore", "topic": "", "qos": "1", "retain": False,
     "respTopic": "", "contentType": "", "userProps": "", "correl": "", "expiry": "",
     "broker": "5fdf061cc038ab42",
     "x": 1010, "y": 540, "wires": []}
]

dst = r'//BRUNKEN-SRV01/appdata/homeassistant/flows_new.json'
with open(dst, 'w', encoding='utf-8') as f:
    json.dump(flows, f, indent=4, ensure_ascii=False)

print(f"Gespeichert: {dst}")
print(f"Nodes gesamt: {len(flows)}")
tabs = [n['label'] for n in flows if n['type'] == 'tab']
print(f"Tabs: {tabs}")
