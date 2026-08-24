# ⚡ PureQuant AI — Commercial Spot Crypto SaaS Platform

> **High-Volume, Low-Ticket Crypto SaaS Platform**  
> Automated Spot AI Trading Signals, Fair Value Gap (FVG) Engine, Lorentzian ML Classification, Telegram VIP Paywall & Non-Custodial USDT Checkout.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Pricing: 3-6-9](https://img.shields.io/badge/Pricing-%243--%246--%249_VIP-emerald.svg)](#-pricing--monetization-model)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production_Ready-green.svg)](#)

---

## 📌 Executive Overview

**PureQuant AI** packages high-probability quantitative spot trading intelligence into a fully automated subscription service:
* **Core Value Proposition**: 100% Halal Spot-Only Trading Signals (zero liquidation risk, zero margin debt), Lorentzian k-NN Machine Learning Classifiers, Fair Value Gap (FVG) entries, SMT Divergence tracking, and dynamic automated capital defense (+1.5% Breakeven locks & +2.2% Trailing SL steps).
* **Launch Pricing Strategy**: Ultra-low-barrier **3 — 6 — 9 Pricing Ladder** (\$3/mo Starter, \$6/mo Pro VIP, and \$9 one-time Lifetime VIP) to maximize global conversion volume.
* **Non-Custodial Paywall**: Automated blockchain verification on TRC-20, BEP-20, Polygon, Solana, and TON with single-use 24-hour expiring Telegram invite generation.

---

## 📂 Project Structure

```
purequant-saas/
├── .gitignore                        # Git exclusion rules
├── .env.example                      # Configuration template (Bot token, Channel IDs, Wallets)
├── README.md                         # Main repository documentation & quick start
├── TELEGRAM_SETUP_TUTORIAL.md        # Step-by-step visual tutorial for Channels & Bot setup
├── BUSINESS_IMPLEMENTATION_PLAN.md   # Marketing, Meta Ads & Go-To-Market blueprint
├── ARCHITECTURE.md                   # Complete technical architecture & data flow
├── DEPLOYMENT_GUIDE.md               # VPS, Cloudflare Pages & Systemd deployment
├── PROJECT_MEMORY.md                 # Context, design system tokens & business rules
├── subscription_bot.py               # Interactive USDT/USDC Telegram Paywall & Signal Engine
├── landing_page/
│   ├── index.html                    # High-converting Cyber-Quant dark landing page
│   └── assets/
│       ├── proof_btc.jpg             # Verified Bitcoin winning trade screenshot
│       ├── proof_sol.jpg             # Verified Solana breakout winning trade screenshot
│       └── proof_eth.jpg             # Verified Ethereum winning trade screenshot
└── data/
    ├── subscribers.json              # Local persistent subscriber store (auto-created)
    └── pending_payments.json         # Pending verification store (auto-created)
```

---

## 💰 Pricing & Monetization Model

```
┌────────────────────────────────┬────────────────────────────────┬────────────────────────────────┐
│ 🥉 STARTER SPOT                │ 🥈 PRO VIP AI (Most Popular)   │ 👑 LIFETIME VIP PASS           │
│ ~~$9~~ ➔ $3 / month (USDT)     │ ~~$19~~ ➔ $6 / month (USDT)    │ ~~$99~~ ➔ $9 ONE-TIME (USDT)   │
│ [ 67% OFF · VIP DISCOUNT ]     │ [ 68% OFF · FULL AI SUITE ]    │ [ 91% OFF · ZERO MONTHLY FEES] │
├────────────────────────────────┼────────────────────────────────┼────────────────────────────────┤
│ • 24/7 Telegram Spot Alerts    │ • Everything in Starter Spot   │ • Lifetime Full VIP Telegram   │
│ • Top 50 High-Volume Pairs     │ • Live Web Scanner Radar       │ • All Future ML Upgrades Free  │
│ • Calculated Entry, SL & TP    │ • Lorentzian ML Confidence %   │ • Private VIP Strategy Group   │
│ • 100% Halal / Spot-Only       │ • Dynamic Trailing SL Alerts   │ • Priority 1-on-1 Support      │
│ • Grandfathered $3/mo Lock     │ • Daily AI Post-Mortem Autopsy │ • Never Pay Another Fee Again  │
└────────────────────────────────┴────────────────────────────────┴────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
* Python 3.9+ installed
* Telegram Bot Token from [@BotFather](https://t.me/BotFather)
* Private Telegram VIP Channel ID (e.g. `-1001234567890`)

### 2. Installation
```bash
# Clone the repository
git clone https://github.com/your-username/purequant-saas.git
cd purequant-saas

# Install Python requirements
pip3 install requests
```

### 3. Configure Environment Variables
Set your credentials in your environment or `.env` file:
```bash
export SAAS_BOT_TOKEN="123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
export VIP_CHANNEL_ID="-1001234567890"
export SUPPORT_USERNAME="@PureQuantSupport"

# Multi-chain deposit wallets
export USDT_TRC20_WALLET="TYourTrc20DepositAddressHere"
export USDT_BEP20_WALLET="0xYourBscDepositAddressHere"
export USDT_POLYGON_WALLET="0xYourPolygonDepositAddressHere"
export USDT_SOLANA_WALLET="YourSolanaDepositAddressHere"
export USDT_TON_WALLET="YourTonDepositAddressHere"
```

### 4. Run the Paywall Bot
```bash
python3 subscription_bot.py
```

### 5. Deploy the Landing Page
The landing page in [`landing_page/index.html`](landing_page/index.html) is completely standalone and zero-dependency:
* **Cloudflare Pages**: Point root directory to `landing_page/` (Instant CDN deployment).
* **Vercel**: Deploy directory `landing_page/`.
* **Nginx / Apache**: Copy `landing_page/` contents to `/var/www/html/`.

---

## 📱 Telegram Signal Format

All automated spot signals follow our institutional layout:

```
⚡ PUREQUANT AI :: SPOT BUY ALERT
🏆 GRADE A+ SETUP · 96.2% LORENTZIAN CONFIDENCE

Asset: #SOL/USDT (Spot Only)
Exchange: Binance / Bybit Spot

📊 INSTITUTIONAL CONFLUENCES:
• 4H Bullish FVG Mitigated @ $135.20
• SMT Bullish Divergence (SOL Higher Low vs BTC Lower Low)
• Whale Orderflow Delta Surge (+420% Aggressive Bids)
• Asian Session Liquidity Pool Swept Clean

🎯 EXECUTION TARGETS:
• 🟢 Entry Zone: $135.20 – $137.50
• 🎯 TP 1: $144.00 (+5.8%) → Close 30% & Move SL to Entry
• 🎯 TP 2: $158.00 (+16.2%) → Close 40% & Trail SL to TP1
• 🎯 TP 3: $181.90 (+34.6%) → Moonbag Macro Liquidity
• 🛑 Initial SL: $131.40 (-2.9% Fixed Risk)

🛡️ AUTOMATED RISK DEFENSE RULES:
1. When price reaches +1.5%, bot notifies to lock Breakeven (0 risk).
2. When TP1 hits, move SL to guaranteed profit.
3. Dynamic Trailing Shield steps up behind 15M swing lows.
```

---

## 📄 License & Legal
PureQuant AI is distributed under the **MIT License**.
*Disclaimer*: PureQuant AI is an algorithmic analytics and educational software tool. Cryptocurrency trading carries market risk.
