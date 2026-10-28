#!/bin/sh
# Wartet, bis Grafana auf unraid erreichbar ist (max. 5 min), dann Firefox im Kiosk-Modus.
URL="http://192.168.68.100:3000/public-dashboards/<PUBLIC_DASHBOARD_TOKEN>"
i=0
until curl -s -o /dev/null -m 5 "$URL" || [ $i -ge 60 ]; do i=$((i+1)); sleep 5; done
exec firefox-esr --kiosk "$URL"
