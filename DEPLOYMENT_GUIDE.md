## 🏗️ Architecture Split: Landing Page vs. 24/7 Telegram Bot

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          1 GITHUB REPOSITORY                                │
└───────────────────────┬─────────────────────────────┬───────────────────────┘
                        │                             │
                        ▼                             ▼
       ┌────────────────────────────────┐ ┌────────────────────────────────┐
       │     🌐 1. LANDING PAGE         │ │     🤖 2. 24/7 TELEGRAM BOT    │
       │    (Vercel / Cloudflare)       │ │     (Render / Railway / VPS)   │
       │                                │ │                                │
       │  • Fast Global Edge CDN        │ │  • Persistent Python Process   │
       │  • 100% Free Hosting           │ │  • Long-polling Telegram Loop  │
       │  • Zero Configuration Needed   │ │  • 24/7 Expiration Watchdog    │
       └────────────────────────────────┘ └────────────────────────────────┘
```

> **Why can't Vercel run the Telegram Bot?**  
> Vercel is a **Serverless** platform designed for static websites and short API calls (times out after 10–60s). A Telegram paywall bot requires a **persistent background worker** that stays connected 24/7 to listen for payments, process user commands, and run the automated 30-day expiration watchdog.

---

## 🌐 Part 1: Landing Page Deployment (Vercel)

1. Push this repository to GitHub.
2. Go to [Vercel Dashboard](https://vercel.com/) ➔ **Add New Project** ➔ Import your repo.
3. Keep default settings (Vercel automatically detects `index.html` and `vercel.json`).
4. Click **Deploy**. Your landing page is live with global SSL!

---

## 🤖 Part 2: 24/7 Telegram Bot Deployment

Choose any of the following 3 options to run the bot 24/7 for free or under $5/mo:

### Option A: Render.com (Recommended · 1-Click GitHub Deploy)
1. Sign up at [Render.com](https://render.com/).
2. Click **New +** ➔ **Background Worker**.
3. Connect your GitHub repository (`purequant-saas`).
4. Build Settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 subscription_bot.py`
5. Click **Advanced ➔ Add Environment Variables**:
   - Add all variables from your `.env` file (`SAAS_BOT_TOKEN`, `VIP_CHANNEL_ID`, `ADMIN_TELEGRAM_ID`, etc.).
6. Click **Create Background Worker**. Render will keep the bot running 24/7 and restart it automatically if it ever crashes.

---

### Option B: Railway.app (Fast & Reliable)
1. Go to [Railway.app](https://railway.app/) ➔ **New Project** ➔ **Deploy from GitHub Repo**.
2. Select `purequant-saas`.
3. Go to **Variables** tab and paste your `.env` variables.
4. Railway automatically detects `Procfile` and runs `python3 subscription_bot.py` 24/7.

---

### Option C: Ubuntu VPS (DigitalOcean / Hetzner / Contabo)

### Step 1: Telegram Bot Credentials Setup
1. Message [@BotFather](https://t.me/BotFather) on Telegram and run `/newbot`.
2. Save your API Token (e.g. `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`).
3. Create your private Telegram VIP Channel (e.g., `PureQuant VIP Signals`).
4. Add your bot as an **Administrator** in the VIP channel with permissions:
   - *Invite Users via Link*: **ON**
   - *Ban/Remove Members*: **ON**
   - *Post Messages*: **ON**
5. Get your channel ID (Forward a message from your channel to [@userinfobot](https://t.me/userinfobot) or [@JsonDumpBot](https://t.me/JsonDumpBot) to find your `-100...` ID).

### Step 2: Systemd Daemon Service Setup (Ubuntu / Debian)
Create a persistent system service so the bot runs 24/7 and restarts automatically:

```bash
# 1. SSH into your VPS
ssh root@your-vps-ip

# 2. Clone repo & install dependencies
git clone https://github.com/your-username/purequant-saas.git /opt/purequant-saas
cd /opt/purequant-saas
pip3 install requests

# 3. Create Systemd Service File
sudo nano /etc/systemd/system/purequant-bot.service
```

Paste the following configuration:
```ini
[Unit]
Description=PureQuant AI Telegram Paywall Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/purequant-saas
Environment=SAAS_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
Environment=VIP_CHANNEL_ID="-1001234567890"
Environment=SUPPORT_USERNAME="@PureQuantSupport"
Environment=USDT_TRC20_WALLET="TYourTrc20Address"
Environment=USDT_BEP20_WALLET="0xYourBscAddress"
Environment=USDT_POLYGON_WALLET="0xYourPolygonAddress"
Environment=USDT_SOLANA_WALLET="YourSolanaAddress"
Environment=USDT_TON_WALLET="YourTonAddress"
ExecStart=/usr/bin/python3 /opt/purequant-saas/subscription_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# 4. Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable purequant-bot
sudo systemctl start purequant-bot

# 5. Check live logs
sudo journalctl -u purequant-bot -f
```

---

### Option B: PM2 Process Manager
```bash
npm install -g pm2
pm2 start subscription_bot.py --name "purequant-bot" --interpreter python3
pm2 save
pm2 startup
```

---

## 🔒 Security Best Practices
1. **Never commit private keys or bot tokens to Git.** Always load them via environment variables.
2. **Cold Storage Settlement**: Ensure all receiving wallet addresses point directly to a hardware wallet (Ledger, Trezor, Keystone, Phantom).
3. **Backup Subscriber Ledger**: Set up a daily cron job to backup `data/subscribers.json` to private S3 or secure backup storage.
