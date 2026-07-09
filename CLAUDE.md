# Brunken Smart Home – CLAUDE.md

## Setup
- **HA instance:** http://192.168.68.100:8123 (Unraid Docker container, user: bjoernbrunken)
- **Config dir:** `\\BRUNKEN-SRV01\appdata\homeassistant` — direkt in den HA-Container gemountet
- **Node-RED:** `\\BRUNKEN-SRV01\appdata\nodered`
- **GitHub:** https://github.com/BjoernBrunken/BrunkenHomeAssistant.git

## Deploy-Workflow
Da die Config direkt gemountet ist, sind Datei-Edits sofort wirksam — kein git pull auf HA-Seite nötig.

1. **Edit** YAML lokal
2. **Reload** via REST API (Token in `.env.local`, nie committen)
3. **Verify** via API / Logs
4. **Commit + Push** zu GitHub (Backup)

## REST API
Token in `.env.local` (gitignored). Beispiel-Calls:
```bash
# Automationen neu laden
curl -s -X POST http://192.168.68.100:8123/api/services/automation/reload \
  -H "Authorization: Bearer $HASS_TOKEN"

# Konfiguration prüfen (config check via API nicht direkt verfügbar, Logs prüfen)
curl -s http://192.168.68.100:8123/api/error_log \
  -H "Authorization: Bearer $HASS_TOKEN" | tail -20

# State abfragen
curl -s http://192.168.68.100:8123/api/states/<entity_id> \
  -H "Authorization: Bearer $HASS_TOKEN"

# Core neu starten
curl -s -X POST http://192.168.68.100:8123/api/services/homeassistant/restart \
  -H "Authorization: Bearer $HASS_TOKEN"
```

## Reload vs. Restart
| Änderung | Aktion |
|---|---|
| automations.yaml, scripts.yaml, scenes.yaml | `automation.reload` / `script.reload` / `scene.reload` |
| configuration.yaml (input_boolean, input_select, etc.) | `homeassistant.restart` |

## Gitignored
`.env.local`, `secrets.yaml`, `.ha_run.lock`

## Standort
Ramvik, Härnösand — 62.7°N, 17.9°E (Sommer: Sonnenaufgang ~03:08, Sonnenuntergang ~22:52)
