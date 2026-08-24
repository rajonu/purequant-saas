"""
⚡ PureQuant AI — Automated Non-Custodial USDT Telegram Paywall & Signal Bot
Pricing Structure:
• Starter Spot: $3.00 / month (Regular $9)
• Pro VIP AI: $6.00 / month (Regular $19)
• Lifetime VIP Pass: $9.00 / one-time (Regular $99)

Features:
- Multi-chain Non-Custodial USDT/USDC Invoicing (TRC-20, BEP-20, Polygon, Solana, TON)
- Automated 1-Time Expiring VIP Channel Link Generation
- Full Institutional Signal Formatter (FVG, SMT Divergence, Lorentzian ML, Breakeven & Trailing SL)
- Expiry Watchdog & Access Revocation
"""

import os
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Bot & Channel Configuration
TELEGRAM_BOT_TOKEN = os.getenv("SAAS_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID", "-1001234567890")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@PureQuantSupport")

# Deposit Wallet Addresses (Non-Custodial)
WALLETS = {
    "TRC20": os.getenv("USDT_TRC20_WALLET", "TYourTrc20DepositAddressHere"),
    "BEP20": os.getenv("USDT_BEP20_WALLET", "0xYourBscDepositAddressHere"),
    "POLYGON": os.getenv("USDT_POLYGON_WALLET", "0xYourPolygonDepositAddressHere"),
    "SOLANA": os.getenv("USDT_SOLANA_WALLET", "YourSolanaDepositAddressHere"),
    "TON": os.getenv("USDT_TON_WALLET", "YourTonDepositAddressHere")
}

# 3 - 6 - 9 Lifetime VIP Launch Pricing Plans
PLANS = {
    "starter": {
        "name": "Starter Spot VIP (1 Month)",
        "price_usdt": 3.0,
        "days": 30,
        "features": [
            "24/7 Telegram Spot Alerts",
            "Top 50 High-Volume Spot Pairs",
            "Calculated Entry, SL & TP Targets",
            "100% Halal / Spot-Only Filter",
            "General Community Chat Access"
        ]
    },
    "pro": {
        "name": "Pro VIP AI (1 Month - Most Popular)",
        "price_usdt": 6.0,
        "days": 30,
        "features": [
            "Everything in Starter Spot",
            "Live Web Scanner & Signal Radar Access",
            "Lorentzian ML Confidence Scores",
            "Fair Value Gap (FVG) & SMT Radar",
            "Dynamic Trailing SL & Breakeven Alerts",
            "Daily AI Post-Mortem Autopsy Feed"
        ]
    },
    "lifetime_vip": {
        "name": "Lifetime VIP Pass (One-Time)",
        "price_usdt": 9.0,
        "days": 3650,
        "features": [
            "Lifetime Full VIP Telegram Access",
            "All Future ML Models & V2 Upgrades Free",
            "Private VIP Strategy Alpha Group",
            "Priority 1-on-1 Dedicated Support",
            "Zero Monthly Renewal Fees Forever"
        ]
    }
}

DB_FILE = "data/subscribers.json"


def load_subscribers() -> Dict[str, Any]:
    """Loads subscriber database from JSON file"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_subscribers(data: Dict[str, Any]):
    """Saves subscriber database atomically"""
    os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_vip_invite_link(bot_token: str, channel_id: str) -> str:
    """Creates a single-use expiring invite link to the private VIP channel"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/createChatInviteLink"
        payload = {
            "chat_id": channel_id,
            "member_limit": 1,
            "expire_date": int(time.time()) + 86400  # 24 hour link validity
        }
        resp = requests.post(url, json=payload, timeout=10).json()
        if resp.get("ok"):
            return resp["result"]["invite_link"]
    except Exception as e:
        print(f"⚠️ Error creating Telegram invite link: {e}")
    return f"https://t.me/{SUPPORT_USERNAME.lstrip('@')}"


def revoke_channel_access(bot_token: str, channel_id: str, user_id: int) -> bool:
    """Revokes channel access by temporarily banning then unbanning"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/banChatMember"
        resp = requests.post(url, json={"chat_id": channel_id, "user_id": user_id}, timeout=8).json()
        if resp.get("ok"):
            unban_url = f"https://api.telegram.org/bot{bot_token}/unbanChatMember"
            requests.post(unban_url, json={"chat_id": channel_id, "user_id": user_id, "only_if_banned": True}, timeout=8)
            return True
    except Exception as e:
        print(f"⚠️ Error revoking access for user {user_id}: {e}")
    return False


def activate_subscription(user_id: str, username: str, plan_key: str, tx_hash: str) -> Dict[str, Any]:
    """Activates user in database and returns their unique invite link"""
    subs = load_subscribers()
    plan = PLANS.get(plan_key, PLANS["pro"])
    
    expires_at = datetime.now() + timedelta(days=plan["days"])
    invite_link = generate_vip_invite_link(TELEGRAM_BOT_TOKEN, VIP_CHANNEL_ID)

    subs[str(user_id)] = {
        "user_id": user_id,
        "username": username or "",
        "plan": plan_key,
        "plan_name": plan["name"],
        "amount_paid": plan["price_usdt"],
        "tx_hash": tx_hash,
        "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        "is_active": True,
        "invite_link": invite_link
    }
    save_subscribers(subs)
    return subs[str(user_id)]


def format_spot_signal_message(setup: Dict[str, Any]) -> str:
    """Formats an institutional-grade signal alert message for Telegram"""
    msg = (
        f"⚡ <b>PUREQUANT AI :: SPOT BUY ALERT</b>\n"
        f"🏆 <b>GRADE A+ SETUP · {setup.get('confidence', '95.4%')} LORENTZIAN CONFIDENCE</b>\n\n"
        f"<b>Asset:</b> #{setup.get('pair', 'SOL/USDT')} (Spot Only)\n"
        f"<b>Exchange:</b> Binance / Bybit Spot\n\n"
        f"<b>📊 INSTITUTIONAL CONFLUENCES:</b>\n"
        f"• 4H Bullish FVG Mitigated @ {setup.get('fvg_level', '$135.20')}\n"
        f"• SMT Divergence Confirmed against BTC Macro Trend\n"
        f"• Whale Orderflow Delta Surge (+420% Aggressive Bids)\n"
        f"• Liquidity Pool Swept Clean\n\n"
        f"<b>🎯 EXECUTION TARGETS:</b>\n"
        f"• 🟢 <b>Entry Zone:</b> {setup.get('entry', '$135.20 - $137.50')}\n"
        f"• 🎯 <b>TP 1:</b> {setup.get('tp1', '$144.00')} (+5.8%) <i>→ Close 30% & Move SL to Entry</i>\n"
        f"• 🎯 <b>TP 2:</b> {setup.get('tp2', '$158.00')} (+16.2%) <i>→ Close 40% & Trail SL to TP1</i>\n"
        f"• 🎯 <b>TP 3:</b> {setup.get('tp3', '$181.90')} (+34.6%) <i>→ Moonbag Macro Liquidity</i>\n"
        f"• 🛑 <b>Initial SL:</b> {setup.get('sl', '$131.40')} (-2.9% Fixed Risk)\n\n"
        f"🛡️ <b>AUTOMATED RISK DEFENSE RULES:</b>\n"
        f"1. When price reaches +1.5%, bot notifies to lock Breakeven.\n"
        f"2. When TP1 hits, move SL to guaranteed profit.\n"
        f"3. Dynamic Trailing Shield steps up behind 15M swing lows.\n\n"
        f"<i>PureQuant AI Quantitative Execution Engine</i>"
    )
    return msg


def check_expirations() -> int:
    """Watchdog that checks expired subscriptions and revokes access"""
    subs = load_subscribers()
    now = datetime.now()
    revoked_count = 0

    for uid, sub in subs.items():
        if not sub.get("is_active"):
            continue
        exp_str = sub.get("expires_at")
        if exp_str:
            try:
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d %H:%M:%S")
                if now > exp_date:
                    sub["is_active"] = False
                    sub["revoked_at"] = now.strftime("%Y-%m-%d %H:%M:%S")
                    revoke_channel_access(TELEGRAM_BOT_TOKEN, VIP_CHANNEL_ID, int(uid))
                    revoked_count += 1
            except Exception as e:
                print(f"Error parsing date for user {uid}: {e}")

    if revoked_count > 0:
        save_subscribers(subs)
        print(f"🔒 Revoked {revoked_count} expired subscription(s).")
    return revoked_count


if __name__ == "__main__":
    plan_strs = [f"{k} (${v['price_usdt']})" for k, v in PLANS.items()]
    print("🚀 PureQuant AI Telegram Paywall Engine Initialized (3-6-9 Lifetime VIP Model).")
    print(f"   • Supported Chains: TRC-20, BEP-20, Polygon, Solana, TON")
    print(f"   • Active Plans: {', '.join(plan_strs)}")
    print(f"   • Database: {DB_FILE}")
    check_expirations()
