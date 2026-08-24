# 🚀 PureQuant AI — Complete Deployment & Production Guide

This guide covers step-by-step deployment for both the **Landing Page** and the **Telegram Paywall Bot Backend**.

---

## 🌐 1. Landing Page Deployment

The landing page (`landing_page/index.html` + `landing_page/assets/`) is zero-dependency static HTML/CSS/JS.

### Option A: Cloudflare Pages (Recommended · 100% Free & Fast CDN)
1. Log in to [Cloudflare Dashboard](https://dash.cloudflare.com/) $\rightarrow$ **Workers & Pages** $\rightarrow$ **Create Application** $\rightarrow$ **Pages**.
2. Connect your GitHub repository.
3. Build Settings:
   - **Build command**: *(Leave blank)*
   - **Build output directory**: `landing_page`
4. Click **Save and Deploy**. Your site is now live on a global edge CDN with free SSL.

### Option B: Vercel
```bash
npm i -g vercel
cd landing_page
vercel --prod
```

### Option C: Ubuntu / Nginx VPS
```bash
# Copy files to web root
sudo mkdir -p /var/www/purequant
sudo cp -r landing_page/* /var/www/purequant/

# Nginx virtual host configuration (/etc/nginx/sites-available/purequant)
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    root /var/www/purequant;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

---

## 🤖 2. Telegram Bot Backend Deployment (VPS)

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
