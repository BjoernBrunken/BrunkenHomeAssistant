# 🏠 Smart Home – Brunken, Ramvik

Dieses Repository enthält die Konfiguration unseres Smart Homes. Hier ist erklärt, was automatisch passiert, welche Geräte es gibt und wie man sie bedient.

---

## 📱 Geräte im Haus

### Beleuchtung

| Raum / Bereich | Beschreibung | Technischer Name |
|---|---|---|
| Küche – Spots | 14 Einbaustrahler (Zigbee2MQTT-Gruppe) | `light.mainhouse_kitchen_grp` |
| Küche – Zusatzlampen | 3 weitere Zigbee-Lampen | `light.0x44e2f8...`, `light.0x348d13...`, `light.0xf0fd45...` |
| Küche – Gesamt | Alle Küchenlampen als eine Gruppe (Spots + Zusatz) | `light.kuche_gesamt` |
| Küche – Fenster | Ambientlicht in den Fensterleibungen (Gruppe, inkl. Sturz) | `light.mainhouse_kitchen_ambient` |
| Küche – Sturz | Ambientlicht im Sturz zum Wohnzimmer (in der Fenster-Gruppe) | `light.mainhouse_kitchen_ambient_lintel` |
| Bad – Spots | 8 Spots (Zigbee2MQTT-Gruppe) | `light.mainhouse_bath_grp` |
| Bad – Fenster | Ambientlicht im Badfenster | `light.mainhouse_bath_ambient_window` |
| Fassade Süd | Außenlampen an der Südfassade | `light.mainhouse_exterior_light_south` |
| Hof | Flutlicht am Haupthaus | `light.gard_mainhouse_floodligt` |

### Musik / AV

| Gerät | Beschreibung | Technischer Name |
|---|---|---|
| Yamaha Receiver | AV-Verstärker im Wohnzimmer | `media_player.yamaha_wohnzimmer` |
| MoOde Audio | Raspberry Pi Musikplayer auf der Terrasse | `media_player.terrasse` |

### Fernbedienungen & Schalter

| Gerät | Ort | Technischer Name |
|---|---|---|
| IKEA Zigbee-Fernbedienung | Terrasse | `dc14ddd326019a3d0075359d08144aa9` |
| Shelly Wandschalter 1 | Küche (links) | `mainhouse_kitchen-shelly1` |
| Shelly Wandschalter 2 | Küche (rechts) | `mainhouse_kitchen-shelly2` |
| Aqara Magic Cube | Küche (Würfel auf der Theke) | `MainHouse-Kitchen_cube` |

### Sensoren

| Gerät | Beschreibung | Technischer Name |
|---|---|---|
| Bewegungsmelder 1 | Hof | `binary_sensor` (Gerät `99693693...`) |
| Bewegungsmelder 2 | Hof | `binary_sensor` (Gerät `504d9cec...`) |
| Helligkeitssensor | Hof | `sensor.0x001788010ebadd57_illuminance` |
| Kesseltemperatur | Holzvergaser (TFA-Sensor mit externem Fühler) | `sensor.holzvergaser_kesseltemperatur` |
| Heizraum | Temperatur / Luftfeuchte am selben TFA-Sensor | `sensor.holzvergaser_heizraum_temperatur`, `…_luftfeuchte` |

---

## ⚡ Was passiert automatisch?

### 🌅 Küche – Fensterlicht (`light.mainhouse_kitchen_ambient`)

Das dezente Licht in den Küchenfensterleibungen geht automatisch an und aus.

- **Abends EIN:** 20 Minuten vor Sonnenuntergang – auf 15 % Helligkeit
- **Morgens AUS:** 10 Minuten nach Sonnenaufgang

---

### 🌅 Bad – Fensterlicht (`light.mainhouse_bath_ambient_window`)

Wie in der Küche:

- **Abends EIN:** 20 Minuten vor Sonnenuntergang – auf 15 % Helligkeit
- **Morgens AUS:** 10 Minuten nach Sonnenaufgang

---

### 🍳 Küche – Licht beim Kochen

Wenn das Kochfeld eingeschaltet wird (Siemens, lokal über hcpy) und es nicht zu hell ist (Helligkeit unter 250 Lux), gehen die 3 Spots über dem Kochfeld auf 100 % kaltweiß an. Drückt man währenddessen den Wandschalter, wird die Szene **Kochen** aktiviert statt das Licht auszuschalten.

---

### 💡 Fassade Süd – Außenbeleuchtung (`light.mainhouse_exterior_light_south`)

Die Lampen an der Südfassade leuchten in zwei Zeitfenstern.

- **Abends EIN:** 20 Minuten vor Sonnenuntergang
- **Abends AUS:** Um Mitternacht (00:00 Uhr)
- **Morgens EIN:** Um 05:00 Uhr – *aber nur wenn die Sonne noch nicht aufgegangen ist!*
- **Morgens AUS:** 15 Minuten nach Sonnenaufgang

> **Hinweis Sommer:** In Ramvik geht die Sonne im Juni schon um ~03:10 Uhr auf. Deshalb schalten die Lampen morgens im Sommer gar nicht erst ein – es ist ja schon hell.

---

### 🎉 Party Modus (`input_boolean.party_modus`)

Startet den Colorloop-Effekt direkt auf allen 14 Küchen-Spots (läuft in der Lampen-Hardware, kein Node-RED benötigt).
Ein-/Ausschalten über den Knopf im HA Dashboard (Kitchen-Karte).
Beim Ausschalten wird automatisch die Szene **Kochen** wiederhergestellt.

---

### 📻 Terrasse – MoOde Audio (`media_player.terrasse`)

Der Musikplayer auf der Terrasse wird über die IKEA-Fernbedienung gesteuert.

| Taste | Funktion |
|---|---|
| Power | Play / Pause |
| Pfeil rechts | Nächster Sender (Bandit Rock → RIX FM → Mix Megapol → Star FM → …) |
| Helligkeit + | Lauter (+5%) |
| Helligkeit − | Leiser (−5%) |

---

### 🔦 Hoflicht (`light.gard_mainhouse_floodligt`)

Das Flutlicht im Hof geht bei Bewegung an.

- **EIN:** Wenn einer der beiden Bewegungsmelder anspricht **und** es dunkel ist (Helligkeit unter 80 Lux)
- **AUS:** 10 Minuten nachdem keine Bewegung mehr erkannt wird
- **Manuell 1 Stunde:** Kann per Knopf oder App für genau 1 Stunde eingeschaltet werden – ein zweiter Druck schaltet es sofort wieder aus
- **Sicherung:** Der Schalter „Hoflicht Override“ setzt sich nach 2 Stunden (und nach jedem HA-Neustart) automatisch zurück. Sonst würde das Licht nie wieder automatisch ausgehen.

---

## 🎛️ Küche bedienen

### Mit den Wandschaltern (Shelly)

Beide Shellys steuern alle 14 Spots + Zusatzlampen gemeinsam über `light.kuche_gesamt`.

| Schalter | Einzeldruck linke Taste | Einzeldruck rechte Taste | Doppeldruck linke Taste | Doppeldruck rechte Taste |
|---|---|---|---|---|
| **Shelly 1** (`mainhouse_kitchen-shelly1`) | Küchenlicht An/Aus | Lichtstimmung wechseln | Radio aus | Bandit Rock starten |
| **Shelly 2** (`mainhouse_kitchen-shelly2`) | Küchenlicht An/Aus | Lichtstimmung wechseln | Radio aus | Bandit Rock starten |

### Mit dem Aqara Würfel (auf der Theke)

Der Würfel steuert den Yamaha-Receiver im Wohnzimmer:

| Aktion | Funktion |
|---|---|
| Umdrehen auf Seite 1 | 📻 Bandit Rock starten |
| Umdrehen auf Seite 2 | 📻 Mix Megapol starten |
| Umdrehen auf Seite 3 | 📻 RIX FM starten |
| Umdrehen auf Seite 4 | 📺 Chromecast-Eingang auswählen |
| Drehen nach rechts | 🔊 Lauter |
| Drehen nach links | 🔉 Leiser |
| Schütteln | ⏯️ Receiver An/Aus |

---

## 🕯️ Lichtstimmungen in der Küche

Durch Drücken der rechten Taste am Wandschalter oder der Pfeil-Taste an der IKEA-Fernbedienung wird die Stimmung der Reihe nach gewechselt:

| Stimmung | Helligkeit | Lichtfarbe | Wofür? |
|---|---|---|---|
| **Kochen** (`scene.kochen`) | 100 % | Kaltweißes Tageslicht (6329 K) | Arbeiten, Kochen |
| **Essen** (`scene.essen`) | 47 % | Warmweißes Licht (3460 K) | Gemeinsames Essen |
| **Abend** (`scene.abend`) | 51 % | Sehr warmes Bernsteinlicht (2020 K) | Gemütlicher Abend |

Zusätzlich per Kachel „Dunkler Tag“ im Dashboard (Home, unter „Kitchen“):

| Stimmung | Helligkeit | Lichtfarbe | Wofür? |
|---|---|---|---|
| **Dunkler Tag** (`scene.kuche_dunkler_tag`) | 30 % | Warm (RGB 255, 209, 138) + Vitrinenlicht 30 % | Ein wenig Licht an trüben Tagen |

## 🛁 Lichtstimmungen im Bad

Fünf Kacheln im Dashboard-Tab **Badrum** (Abschnitt „Szenen Spots“), alle 8 Spots auf 30 %:

| Szene | Farbe (RGB) |
|---|---|
| Pfirsich (`scene.bad_pfirsich`) | 255, 209, 173 |
| Warmweiß (`scene.bad_warmweiss`) | 255, 224, 194 |
| Apricot (`scene.bad_apricot`) | 255, 196, 173 |
| Rosé (`scene.bad_rose`) | 255, 182, 193 |
| Himmelblau (`scene.bad_himmelblau`) | 135, 206, 250 |

---

## 🛁 Badetonne – Skimmer-Pumpe (`switch.garden_badtunna_pump`)

### Manuell – 6 Stunden

Über den Knopf **„Pumpe 6 Stunden"** (`input_button.badtunna_6h`) im Dashboard:

- **Einmal drücken:** Pumpe läuft 6 Stunden, dann automatisch aus
- **Nochmal drücken während sie läuft:** Pumpe sofort stoppen

### Täglich automatisch

- **Uhrzeit:** Jeden Tag um 10:00 Uhr
- **Laufzeit:** 30 Minuten
- **Bedingungen:** Pumpe läuft nur automatisch, wenn Außentemperatur > 5°C **und** kein manueller 6h-Betrieb aktiv ist

> **Hinweis Winter:** Unterhalb von 5°C Außentemperatur läuft die Pumpe nicht automatisch – im Winter einfach den 6h-Knopf benutzen wenn die Tonne in Betrieb ist.

---

## 🔥 Holzvergaser – Temperaturwarnung

Push-Nachricht an beide Handys (Björn, Mara):

| Situation | Wann | Benachrichtigung |
|---|---|---|
| **Warnung** | Kessel 5 Minuten über der Warnschwelle (**95 °C**) | normal, Kanal „Heizung“ |
| **Kritisch** | Kessel über der kritischen Schwelle (**98 °C**) | sofort, Alarmton – klingelt auch bei lautlos |
| **Fühler ausgefallen** | 30 Minuten kein Messwert | normal |

- Die Schwellen sind im Dashboard verstellbar (`input_number.holzvergaser_warnschwelle` / `…_kritische_schwelle`).
- Eine neue Warnung kommt erst, wenn die Temperatur zwischendurch wieder unter die Schwelle gefallen ist.
- Zum Testen nicht die Schwelle senken – das löst nichts aus (es zählt nur das Überschreiten von unten).

---

## 🔧 Technische Infos

- **Smart Home System:** [Home Assistant](https://www.home-assistant.io/)
- **Server:** BRUNKEN-SRV01
- **Zigbee-Geräte:** Verbunden über Zigbee2MQTT (MQTT-Protokoll)
- **Shelly-Geräte:** Verbunden über die Shelly-Integration
- **Standort für Sonnenauf/-untergang:** Ramvik, Härnösand (62.7°N, 17.9°E)
- **Server, MQTT, InfluxDB, Grafana, Wandanzeige:** siehe [docs/INFRASTRUKTUR.md](docs/INFRASTRUKTUR.md)
