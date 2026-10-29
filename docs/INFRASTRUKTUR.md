# 🖥️ Infrastruktur – Brunken Smart Home

Technische Übersicht über Server, Datenwege und Dienste rund um Home Assistant.
Stand: **28.10.2026** (nach dem Umzug vom alten Raspberry Pi auf unraid).

> Begriffe: **unraid** = Server `BRUNKEN-SRV01` (192.168.68.100). **Pi** = alter Raspberry Pi `dockerpi` (192.168.68.67, früher .66). **Mirror** = MagicMirror-Pi an der Wand (192.168.68.77).

---

## Geräte im Netz

| Gerät | IP | Rolle |
|---|---|---|
| Deco (Haupt-Router) | 192.168.68.1 | Router/DHCP, Netz `192.168.68.0/22`, DHCP-Pool `.68.70 – .71.250` |
| **unraid** (BRUNKEN-SRV01) | 192.168.68.100 | Alle Dienste als Docker-Container (siehe unten) |
| `mosquitto-legacy` (Container auf unraid) | 192.168.68.66 | Übernimmt die alte Pi-IP für die ESP32 (Broker-IP fest im Code) |
| **Pi** (`dockerpi`, Raspberry, IOTstack) | 192.168.68.67 | Außer Betrieb, nur noch Rückfallebene → wird abgeschaltet |
| **Mirror** (Raspberry Pi 2) | 192.168.68.77 | Wandanzeige: Firefox-Kiosk mit Grafana |
| ESP32 „Barometer“ | DHCP (zuletzt .68.94) | Akkutank-Fühler + Luftdruck, sendet an .66 |
| MobileAlerts-Gateway (TFA) | 192.168.68.73 | Funk-Gateway der TFA-Sensoren, Proxy → unraid:8081 |
| Siemens Kochfeld | 192.168.68.88 | Home Connect lokal über hcpy (IP in `appdata/hcpy/config/devices.json`, im Deco reservieren!) |

Statische IPs außerhalb des DHCP-Pools (`.2 – .69`) werden vom Deco nie vergeben – dort liegen .66, .67 und .77.

---

## Container auf unraid

| Container | Port(s) | Zweck |
|---|---|---|
| Home-Assistant-Container | 8123 | Home Assistant |
| mosquitto | 1883 | Haupt-MQTT-Broker (anonym) |
| **mosquitto-legacy** | 192.168.68.66:1883 (br0) | Bridge `topic # out` → Haupt-Broker. Konfig: [`infra/mosquitto-legacy/`](../infra/mosquitto-legacy/) |
| zigbee2mqtt | **8080** (Frontend) | Zigbee |
| **maserver** | **8081** (Proxy), host-Netz | MobileAlerts → MQTT `MobileAlerts/<id>/json`. Konfig im Image eingebaut: [`infra/maserver/`](../infra/maserver/) |
| NodeRed | 1880 | MQTT → InfluxDB. Flows: [`infra/node-red/flows.json`](../infra/node-red/flows.json) |
| Influxdb-1.8 | 8086 | Datenbank `sensor_data` |
| Grafana | 3000 | Dashboards (Version 13.2) |
| hcpy | – | Siemens Kochfeld ↔ MQTT (`homeconnect/hob/...`) |
| traccar + mariadb-traccar | 8082 / 5055 | GPS-Tracking |
| immich_* | – | Fotos |

> ⚠️ Port **8080** gehört dem Zigbee2MQTT-Frontend. Der MobileAlerts-Proxy läuft deshalb auf **8081**.

---

## Datenwege

```
ESP32 (Akkutanks, Luftdruck) ──► mosquitto-legacy (.66) ──bridge──► mosquitto (.100) ─┐
TFA-Sensoren ──► Gateway (.73) ──HTTP-Proxy──► maserver (:8081) ──► mosquitto (.100) ─┤
Zigbee-Geräte ──► zigbee2mqtt ──► mosquitto (.100) ───────────────────────────────────┤
                                                                                       ├─► Node-RED ──► InfluxDB ──► Grafana ──► Mirror
                                                                                       └─► Home Assistant (Sensoren, Warnungen)
```

### MQTT-Topics

| Topic | Quelle | Inhalt |
|---|---|---|
| `/home/heating` | ESP32 | `{"temp":…, "sensorId":"28…"}` – 9 DS18B20 an den Akkutanks, alle ~2,5 min |
| `/home/sensors` | ESP32 | `{"p":100364}` – Luftdruck in Pa |
| `/home/spa` | ESP Badtunna | `{"temp":…, "sensorId":…}` (derzeit keine Daten) |
| `MobileAlerts/0933fcd67fd3/json` | TFA „Heizung“ | `temperatureExt` = **Kesseltemperatur**, `temperature`/`humidity` = Heizraum |
| `MobileAlerts/033e60bbf6e6/json` | TFA Küche | Temperatur, Luftfeuchte |
| `MobileAlerts/032ab291bcae/json` | TFA | Temperatur, Luftfeuchte |
| `MobileAlerts/08396a64b798/json` | TFA Regen (MA10650) | `eventCounter` = Kippungen seit Batteriewechsel |
| `zigbee2mqtt/MainHouse-Temp_out-1` | Zigbee | Außentemperatur |

### InfluxDB `sensor_data`

- Measurement `sensor_data`, Retention-Policy **`autogen` (unbegrenzt)**, einzige Policy (`two_years` am 28.10.2026 gelöscht).
- Felder: `Temp`/`ID` (Akkutanks, Spa), `TempOut`/`Humidity`/`Sensor` (TFA), `RainCounter`/`RainMM` (Regen, seit 28.10.2026), `RainVolume` (alt, ungenau), `pressure` (Pa), `temp_value` + Tag `Sensor` (Außentemperatur Zigbee).
- `Sensor` gibt es als Feld **und** als Tag → in Abfragen `"Sensor"::field` verwenden.
- Historie vom Pi seit **14.08.2023** übernommen (bis 28.10.2026 09:00 UTC).
- Backups: `appdata/influx-backup/` (`unraid-2026-10-28-1030`, `pi-2026-10-28`).

---

## Backup

- Plugin **Appdata Backup** auf unraid, Ziel: Synology **BRUNKEN-NAS** (192.168.68.45), NFS-Freigabe `/volume1/unraid-backup`, eingebunden über Unassigned Devices unter `/mnt/remotes/BRUNKEN-NAS_unraid-backup/appdata-backup`.
- **Jeden Montag 04:00**, Container werden nacheinander kurz gestoppt, Sicherung wird geprüft. Aufbewahrung: mindestens 8 Sicherungen, ältere als 56 Tage werden gelöscht. Zusätzlich Sicherung des USB-Sticks (unraid-Konfiguration).
- Ausgenommen: Immich-Vorschaubilder und umgewandelte Videos (`immich/library/thumbs`, `encoded-video`, ~45 GB, regenerierbar). Die Fotos selbst liegen auf der Synology (`/volume1/photo`).
- Zusätzlich gesichert: `appdata/maserver` (Quellcode/Konfig des MobileAlerts-Images, hat kein Volume).
- Eine Sicherung ist ca. 2 GB groß. Wiederherstellen: unraid → Settings → Appdata Backup → Restore.

---

## Immich

- Compose + `.env` in `appdata/immich/`, Datenbank in `appdata/immich/postgres` (sieht per SMB leer aus – Rechte 700/uid 999, Inhalt nur per SSH sichtbar).
- Fotos: externe Bibliothek, NFS-Freigabe der Synology `/volume1/photo` → Unassigned Devices `/mnt/remotes/BRUNKEN-NAS_photo` → im Container `/mnt/media` (read-only). Bibliotheks-Scan stündlich 8–22 UTC.
- Tägliche DB-Sicherung durch Immich selbst: `immich/library/backups/` (02:00).
- **Vorfall 28.10.2026:** Nach dem Einbinden der Backup-Freigabe wurden die NFS-Freigaben neu gemountet, `immich_server` startete 9 s **vor** dem Foto-Mount und sah nur ein leeres Verzeichnis. Der Scan um 16:00 hat daraufhin alle 89 966 Fotos als offline markiert und in den Papierkorb geschoben (30 Tage Aufbewahrung). Behoben am 29.10. mit `docker restart immich_server` + Scan – alle Fotos wiederhergestellt.
- **Schutz seither:** Unassigned-Devices-Skript `/boot/config/plugins/unassigned.devices/BRUNKEN-NAS_photo.sh` (in `samba_mount.cfg` als `command=` bei der Foto-Freigabe eingetragen). Es startet `immich_server` nach jedem Einbinden der Freigabe neu und schreibt einen Eintrag ins Syslog (`immich-nfs`). Getestet am 29.10.2026 per Remount.
  - ⚠️ UD arbeitet mit einer RAM-Kopie `/tmp/unassigned.devices/config/samba_mount.cfg` und schreibt sie bei Änderungen auf den Stick zurück. Konfiguration daher über die UD-Oberfläche ändern oder **beide** Dateien gleich anpassen.
  - Remount zum Testen: `rc.unassigned umount 'BRUNKEN-NAS:/volume1/photo'` und `rc.unassigned mount …` – mit dem Gerätenamen, nicht dem Mount-Pfad (sonst passiert nichts, Ausgabe trotzdem „success“).
- Prüfen bei „Immich ist leer“: `docker exec immich_server mount | grep media` – muss `nfs` zeigen, nicht `tmpfs`. **Papierkorb in Immich nicht leeren**, solange das nicht geklärt ist.

---

## Regenmesser

- MobileAlerts MA10650: zählt die Kippungen einer Wippe (`eventCounter`, kumuliert seit Batteriewechsel, 16 Bit).
- Node-RED-Funktion „Regen: Zähler -> mm“ schreibt `RainCounter` (Rohwert) und `RainMM` (Regen seit der letzten Nachricht). Batteriewechsel/Überlauf werden erkannt. Der letzte Zählerstand liegt im persistenten Node-RED-Kontext (`contextStorage` „file“ in `nodered/settings.js`).
- **Kalibriert am 28.10.2026:** 100 ml (= 10 mm auf 100 cm²) → 27 Kippungen + Rest → **0,364 mm pro Kippung** (Herstellerangabe 0,258 mm misst ~30 % zu wenig).
- Grafana „Regn“-Kacheln = Summe `RainMM` über den Zeitraum. Alte Werte (`RainVolume`, immer 0,258 je Nachricht) sind unbrauchbar und werden nicht angezeigt.
- Schnee/Hagel werden nicht gemessen (Trichter unbeheizt).

---

## Grafana

- Dashboards (Export: [`infra/grafana/`](../infra/grafana/)): **WeatherMore**, **tanks**, **Weather test**. Datenquelle `BRUNKEN-SRV01_InfluxDB` (uid `dfg6sxrlykidcf`), Abfragen auf Policy `default`.
- Plugins: `grafana-clock-panel` (Uhr, Datum Schwedisch), `gapit-htmlgraphics-panel`.
- **Utetemperatur**: Luftdruck in hPa auf der rechten Achse (Soft-Bereich 990–1030 hPa). Die Abfragen C/D sind unsichtbare Hilfswerte (Mittelwert ±5 °C), damit die Temperaturachse immer mindestens 10 °C breit ist.
- **WeatherMore** ist als öffentliches Dashboard freigegeben (nur im Heimnetz erreichbar) – das zeigt der Mirror an.

---

## Mirror (Wandanzeige, 192.168.68.77)

Raspberry Pi 2, Raspbian 10, Benutzer `pi`, WLAN braucht nach dem Booten ~85 s.

- Autostart: `~/.config/autostart/grafana-kiosk.desktop` → `~/grafana-kiosk.sh` wartet, bis Grafana erreichbar ist, dann `firefox-esr --kiosk` mit dem öffentlichen WeatherMore-Dashboard.
- `user.js` im Firefox-Profil verhindert „Sitzung wiederherstellen“ nach Stromausfall.
- Neustart jeden **Sonntag 03:00** (`/etc/cron.d/kiosk-reboot`).
- Nach dem Einschalten dauert es 3–4 min, bis das Dashboard steht.
- MagicMirror ist noch installiert, aber aus pm2 entfernt. Zurück: `~/magicmirror-wiederherstellen.sh`.
- Dateien: [`infra/magicmirror/`](../infra/magicmirror/)

---

## Home Assistant – Ergänzungen (Oktober 2026)

Alles über die HA-Oberfläche/REST-API angelegt (landet in `automations.yaml`, `scripts.yaml`, `scenes.yaml`); Helfer liegen in `.storage`.

| Was | Entitäten |
|---|---|
| Holzvergaser-Warnung | `automation.holzvergaser_temperaturwarnung`, `script.heizung_benachrichtigen`, `input_number.holzvergaser_warnschwelle` (95 °C), `input_number.holzvergaser_kritische_schwelle` (98 °C) |
| Kessel-/Heizraum-Sensoren (MQTT-Discovery, retained) | `sensor.holzvergaser_kesseltemperatur`, `sensor.holzvergaser_heizraum_temperatur`, `sensor.holzvergaser_heizraum_luftfeuchte` (`expire_after` 30 min) |
| Hoflicht-Override Auto-Reset | `automation.hoflicht_override_auto_reset` |
| Bad-Fensterlicht | `automation.window_ambient_bath_on/off` |
| Bad-Spots Szenen | `scene.bad_pfirsich`, `bad_warmweiss`, `bad_apricot`, `bad_rose`, `bad_himmelblau` |
| Küche „Dunkler Tag“ | `scene.kuche_dunkler_tag` |

Warnschwellen abgeleitet aus der Kessel-Historie 2023–2026: Median 42 °C, 99 % der Zeit unter 93 °C, 99,9 % unter 97 °C.

---

## Offene Punkte

- [ ] Pi abschalten (läuft nur noch als Rückfallebene; Node-RED und MobileAlerts dort deaktiviert).
- [ ] unraid-Netzmaske `br0` von /24 auf /22 korrigieren (Deco-Netz ist /22).
- [ ] Spa-Sensor (`/home/spa`) und TFA-Regensensor prüfen – derzeit keine Daten.
- [ ] Kochfeld-IP 192.168.68.88 im Deco reservieren (MAC 68:A4:0E:8C:F0:C0).
- [ ] Nach der Migration aufräumen: Grafana-Service-Account `claude-migration`, SSH-Schlüssel auf unraid/Pi/Mirror.
