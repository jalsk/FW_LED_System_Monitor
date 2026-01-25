#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/fw-led-monitor"

echo "Installing to $INSTALL_DIR..."

sudo mkdir -p "$INSTALL_DIR"
sudo cp "$SCRIPT_DIR/led_system_monitor.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/drawing.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/monitors.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/commands.py" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"
sudo cp "$SCRIPT_DIR/run.sh" "$INSTALL_DIR/"
sudo chmod +x "$INSTALL_DIR/run.sh"
sudo chown -R root:root "$INSTALL_DIR"

VENV_DIR="$INSTALL_DIR/venv"
if [ ! -d "$VENV_DIR" ]; then
    sudo python3 -m venv "$VENV_DIR"
fi

sudo "$VENV_DIR/bin/pip" install --upgrade pip
sudo "$VENV_DIR/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

rm -f "$SCRIPT_DIR/fwledmonitor.service" || true
cat <<EOF > "$SCRIPT_DIR/fwledmonitor.service"
[Unit]
Description=Framework 16 LED System Monitor
After=network.service

[Service]
Type=simple
Restart=always
RestartSec=5
WorkingDirectory=$INSTALL_DIR
ExecStart=/bin/bash $INSTALL_DIR/run.sh

[Install]
WantedBy=default.target
EOF

sudo systemctl stop fwledmonitor || true

SERVICE_DIR="/etc/systemd/system"
if ! sudo cp "$SCRIPT_DIR/fwledmonitor.service" "$SERVICE_DIR" 2>/dev/null; then
    SERVICE_DIR="/lib/systemd/system"
    sudo cp "$SCRIPT_DIR/fwledmonitor.service" "$SERVICE_DIR"
fi

sudo systemctl daemon-reload
sudo systemctl enable fwledmonitor

echo "Installation complete. Service installed to $INSTALL_DIR"

sudo service fwledmonitor start