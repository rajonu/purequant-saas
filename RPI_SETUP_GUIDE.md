# 🍓 PureQuant AI — Raspberry Pi Facebook Auto-Poster Setup Guide

> **Lightweight, 24/7 Raspberry Pi Gateway**  
> Automatically captures Take-Profit (TP) signals from your Trading Board, renders high-converting 1080x1080 Trade Proof Cards, and publishes Meta-compliant posts to your Facebook Page without getting banned.

---

## 🏗️ Architecture Overview

```
[ Your Trading Board / Signal Engine ]
                  │
        (Webhook / API Poll)
                  ▼
┌────────────────────────────────────────┐
│  🍓 Raspberry Pi Microservice (:5050)  │
│  • Web Control Panel UI                │
│  • ARM-Optimized Trade Card Renderer   │
│  • Meta Anti-Ban Caption Builder       │
│  • Deduplication History Ledger        │
└────────────────────────────────────────┘
                  │
          (Meta Graph API)
                  ▼
        [ Facebook Page Post ]
                  │
       (Traffic / Boosted Ads)
                  ▼
   [ Free Telegram -> Paid VIP Bot ]
```

---

## 🚀 Quick Setup on Raspberry Pi (3 Steps)

### Step 1: Copy or Git Clone to Your Raspberry Pi
On your Raspberry Pi terminal, clone or copy the project folder:
```bash
git clone <your-repo-url> purequant-saas
cd purequant-saas
```

### Step 2: Run the 1-Command Automated Installer
Run the installer script. It will install all dependencies (Pillow, Flask, system fonts) and configure a background `systemd` service:
```bash
chmod +x install_raspberry_pi.sh
./install_raspberry_pi.sh
```

### Step 3: Configure Your Credentials in `.env`
Edit the `.env` file on your Raspberry Pi:
```bash
nano .env
```

Set your Facebook credentials:
```env
# Meta / Facebook Graph API Credentials
FB_PAGE_ID="123456789012345"
FB_PAGE_ACCESS_TOKEN="EAA..."

# (Optional) Trading Board Polling API
TRADING_BOARD_API_URL="https://your-trading-board.com/api/v1/closed-trades"
TRADING_BOARD_API_KEY="your-api-key"
AUTO_POLL_ENABLED=true
POLL_INTERVAL_SECONDS=60

# Links included in compliant post caption
TELEGRAM_PUBLIC_URL="https://t.me/PureQuantSignals"
LANDING_PAGE_URL="https://purequant.ai"
PORT=5050
```

Restart the service after saving:
```bash
sudo systemctl restart purequant-fb
```

---

## 🌐 Raspberry Pi Web Dashboard

Open your browser from any phone or PC connected to the same Wi-Fi:
```text
http://<your-raspberry-pi-ip>:5050
```
*(e.g. `http://192.168.1.150:5050` or `http://raspberrypi.local:5050`)*

**Features in Dashboard:**
* 🟢 **Live Integrations Status**: Checks Facebook Page connection and Trading Board status.
* 🚀 **1-Click Test Post**: Immediately renders a test card and publishes it to Facebook to verify your credentials.
* 📜 **Recent Posts Ledger**: Real-time log of published trades with direct Facebook post links.

---

## 🪝 How to Connect Your Trading Board (2 Methods)

### Method A: Real-Time Webhooks (Recommended — Fastest)
Configure your Trading Board to send a `POST` request to your Raspberry Pi whenever a TP hits:

**Endpoint:**
```text
POST http://<your-pi-ip>:5050/webhook/tp
```

**JSON Payload:**
```json
{
  "trade_id": "SOL_0825_1",
  "pair": "SOL/USDT",
  "gain_pct": "+34.60%",
  "entry_price": "$135.20",
  "exit_price": "$181.90",
  "target_name": "TP3 (Macro Expansion)",
  "strategy": "4H Bullish FVG + Lorentzian ML",
  "risk_reward": "1 : 3.8"
}
```

---

### Method B: Automated Background Polling
If your Trading Board cannot send webhooks, the Raspberry Pi can **poll your API** automatically:
1. In `.env`, set:
   ```env
   TRADING_BOARD_API_URL="https://your-trading-board.com/api/v1/closed-trades"
   TRADING_BOARD_API_KEY="your-key"
   AUTO_POLL_ENABLED=true
   POLL_INTERVAL_SECONDS=60
   ```
2. The Raspberry Pi background thread will query your API every 60 seconds, detect newly closed trades that hit TP, and publish them with automatic duplicate protection.

---

## 🛠️ Useful Service Commands

* **Check live status:**
  ```bash
  sudo systemctl status purequant-fb
  ```
* **View live logs:**
  ```bash
  sudo journalctl -u purequant-fb -f
  ```
* **Restart service:**
  ```bash
  sudo systemctl restart purequant-fb
  ```
* **Stop service:**
  ```bash
  sudo systemctl stop purequant-fb
  ```
