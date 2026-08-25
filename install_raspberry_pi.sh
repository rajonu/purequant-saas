#!/usr/bin/env bash
# ==============================================================================
# ⚡ PureQuant AI — Raspberry Pi Automated Installation & Service Installer
# ==============================================================================

set -e

echo "=================================================="
echo "⚡ Setting up PureQuant AI on Raspberry Pi..."
echo "=================================================="

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER_NAME="$(whoami)"

echo "[1/4] Installing system dependencies (fonts & python3-venv)..."
sudo apt-get update -y
sudo apt-get install -y python3 python3-pip python3-venv fonts-dejavu-core

echo "[2/4] Creating Python Virtual Environment..."
cd "$APP_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

echo "[3/4] Installing Python packages..."
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r requirements.txt

# Create .env from template if missing
if [ ! -f ".env" ]; then
    cp config.env.example .env
    echo "[!] Created .env file. Remember to edit .env with your FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN!"
fi

echo "[4/4] Creating systemd background service (purequant-fb.service)..."
SERVICE_FILE="/etc/systemd/system/purequant-fb.service"

sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=PureQuant AI Facebook Auto-Poster & Webhook Service
After=network.target

[Service]
Type=simple
User=$USER_NAME
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python3 $APP_DIR/rpi_app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOL

sudo systemctl daemon-reload
sudo systemctl enable purequant-fb.service
sudo systemctl restart purequant-fb.service

# Get Pi IP Address
PI_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "=================================================="
echo "🎉 PureQuant AI Raspberry Pi Engine Installed & Running!"
echo "=================================================="
echo "🌐 Web Dashboard:  http://$PI_IP:5050"
echo "🪝 Webhook URL:    http://$PI_IP:5050/webhook/tp"
echo ""
echo "📋 Useful Service Commands:"
echo "  • Check Status:  sudo systemctl status purequant-fb"
echo "  • View Live Logs: sudo journalctl -u purequant-fb -f"
echo "  • Restart App:   sudo systemctl restart purequant-fb"
echo "=================================================="
