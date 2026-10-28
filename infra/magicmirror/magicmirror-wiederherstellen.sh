#!/bin/bash
# Stellt den alten Zustand her: MagicMirror per pm2 statt Grafana-Kiosk (Aenderung vom 28.10.2026)
pm2 start /home/pi/mm.sh --name mm --interpreter bash && pm2 save
rm -f ~/.config/autostart/grafana-kiosk.desktop ~/grafana-kiosk.sh
echo "MagicMirror wieder aktiv, Grafana-Kiosk-Autostart entfernt. Neustart: sudo reboot"
