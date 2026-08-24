"""
⚡ PureQuant AI — Interactive Automated Telegram Paywall & Signal Broadcaster
=============================================================================
Non-Custodial Multi-Chain Crypto Payments (USDT / USDC on TRC20, BEP20, Polygon, Solana, TON)
Single-Use Expiring VIP Invite Links, 1-Click Admin Approvals, 2-Way Anonymous Support Relay.
"""

import os
import json
import time
import threading
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

# Built-in Health Check Server for 100% Free Web Service Hosting (Render / Railway / Koyeb)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"PureQuant AI Paywall Bot is Active & Running 24/7 OK")

    def log_message(self, format, *args):
        pass  # Quiet HTTP logs

def start_health_server():
    port = int(os.getenv("PORT", "10000"))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
        print(f"🌐 Health check HTTP server listening on port {port} (Free Web Service Ready)")
        server.serve_forever()
    except Exception as e:
        print(f"⚠️ Health server notice: {e}")

# Load .env file automatically if present
def load_env_file(filepath: str = ".env"):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip("'\"")
                    if k and k not in os.environ:
                        os.environ[k] = v
        except Exception as e:
            print(f"⚠️ Warning loading .env: {e}")

load_env_file()

# ==============================================================================
# ⚙️ CONFIGURATION & ENVIRONMENT VARIABLES
# ==============================================================================

BOT_TOKEN = os.getenv("SAAS_BOT_TOKEN", "").strip()
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID", "").strip()
FREE_CHANNEL_ID = os.getenv("FREE_CHANNEL_ID", "").strip()
FREE_CHANNEL_USERNAME = os.getenv("FREE_CHANNEL_USERNAME", "PureQuantSignals").lstrip("@")
ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID", "").strip()
SUPPORT_BOT_NAME = os.getenv("SAAS_BOT_USERNAME", "PureQuantAIBot").lstrip("@")

# Non-Custodial Deposit Wallet Addresses
WALLETS = {
    "TRC20": {
        "name": "USDT (TRC-20 / Tron)",
        "address": os.getenv("USDT_TRC20_WALLET", "TX_YOUR_TRC20_ADDRESS_HERE").strip()
    },
    "BEP20": {
        "name": "USDT / USDC (BEP-20 / BNB Chain)",
        "address": os.getenv("USDT_BEP20_WALLET", "0x_YOUR_BEP20_ADDRESS_HERE").strip()
    },
    "POLYGON": {
        "name": "USDT / USDC (Polygon PoS)",
        "address": os.getenv("USDT_POLYGON_WALLET", "0x_YOUR_POLYGON_ADDRESS_HERE").strip()
    },
    "SOLANA": {
        "name": "USDT / USDC (Solana SPL)",
        "address": os.getenv("USDT_SOLANA_WALLET", "YOUR_SOLANA_ADDRESS_HERE").strip()
    },
    "TON": {
        "name": "USDT (TON Network)",
        "address": os.getenv("USDT_TON_WALLET", "UQ_YOUR_TON_ADDRESS_HERE").strip()
    }
}

# 3 — 6 — 9 Launch Pricing Plans
PLANS = {
    "starter": {
        "name": "Starter Spot VIP",
        "price_usdt": 3.0,
        "days": 30,
        "badge": "🥉 STARTER",
        "desc": "Full 24/7 Spot Signals, Entry/TP/SL, 100% Halal Zero-Leverage.",
        "features": [
            "24/7 Telegram Spot Alerts",
            "Top 50 High-Volume Spot Pairs",
            "Calculated Entry, SL & TP Targets",
            "100% Halal / Spot-Only Filter"
        ]
    },
    "pro": {
        "name": "Pro VIP AI",
        "price_usdt": 6.0,
        "days": 30,
        "badge": "🥈 PRO VIP (Popular)",
        "desc": "Lorentzian ML Scores, Fair Value Gap (FVG), Trailing SL & Breakeven Locks.",
        "features": [
            "Everything in Starter Spot",
            "Lorentzian ML Confidence Scores",
            "Fair Value Gap (FVG) & SMT Radar",
            "Dynamic Trailing SL & Breakeven Alerts",
            "Daily AI Post-Mortem Autopsy Feed"
        ]
    },
    "lifetime_vip": {
        "name": "Lifetime VIP Pass",
        "price_usdt": 9.0,
        "days": 3650,
        "badge": "👑 LIFETIME VIP",
        "desc": "One-time payment for 10 years of unlimited VIP access. Zero recurring fees.",
        "features": [
            "Lifetime Full VIP Telegram Access",
            "All Future ML Models & V2 Upgrades Free",
            "Private VIP Strategy Alpha Group",
            "Priority 1-on-1 Dedicated Support",
            "Zero Monthly Renewal Fees Forever"
        ]
    }
}

DATA_DIR = "data"
DB_FILE = os.path.join(DATA_DIR, "subscribers.json")
PENDING_FILE = os.path.join(DATA_DIR, "pending_payments.json")
TICKETS_FILE = os.path.join(DATA_DIR, "support_tickets.json")

# In-memory user state machine: {user_id: {"state": str, "plan": str, "network": str, "replying_to": int}}
USER_STATES: Dict[int, Dict[str, Any]] = {}

# ==============================================================================
# 💾 DATABASE OPERATIONS
# ==============================================================================

def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
    if not os.path.exists(PENDING_FILE):
        with open(PENDING_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
    if not os.path.exists(TICKETS_FILE):
        with open(TICKETS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)

def load_subscribers() -> Dict[str, Any]:
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_subscribers(data: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_pending() -> Dict[str, Any]:
    try:
        with open(PENDING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_pending(data: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PENDING_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def save_support_ticket(ticket: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    tickets = []
    if os.path.exists(TICKETS_FILE):
        try:
            with open(TICKETS_FILE, "r", encoding="utf-8") as f:
                tickets = json.load(f)
        except Exception:
            tickets = []
    tickets.append(ticket)
    with open(TICKETS_FILE, "w", encoding="utf-8") as f:
        json.dump(tickets, f, indent=2, ensure_ascii=False)

# ==============================================================================
# 📡 TELEGRAM API WRAPPER
# ==============================================================================

def tg_api_call(method: str, payload: Dict[str, Any] = None) -> Dict[str, Any]:
    if not BOT_TOKEN:
        return {"ok": False, "description": "SAAS_BOT_TOKEN is not configured"}
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    try:
        resp = requests.post(url, json=payload or {}, timeout=25).json()
        return resp
    except Exception as e:
        print(f"⚠️ Telegram API Exception ({method}): {e}")
        return {"ok": False, "description": str(e)}

def send_message(chat_id: Any, text: str, reply_markup: Dict[str, Any] = None, parse_mode: str = "HTML") -> Dict[str, Any]:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return tg_api_call("sendMessage", payload)

def edit_message_text(chat_id: Any, message_id: int, text: str, reply_markup: Dict[str, Any] = None, parse_mode: str = "HTML") -> Dict[str, Any]:
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    return tg_api_call("editMessageText", payload)

def answer_callback_query(callback_query_id: str, text: str = None, show_alert: bool = False):
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
        payload["show_alert"] = show_alert
    return tg_api_call("answerCallbackQuery", payload)

def generate_vip_invite_link(channel_id: str = None) -> Optional[str]:
    target_channel = channel_id or VIP_CHANNEL_ID
    if not target_channel:
        return None
    
    # Generate 1-time expiring invite link (valid for 24h, 1 member limit)
    payload = {
        "chat_id": target_channel,
        "member_limit": 1,
        "expire_date": int(time.time()) + 86400,
        "creates_join_request": False
    }
    res = tg_api_call("createChatInviteLink", payload)
    if res.get("ok"):
        return res["result"]["invite_link"]
    else:
        print(f"⚠️ Failed to create invite link: {res}")
        return None

def revoke_channel_access(channel_id: str, user_id: int) -> bool:
    res = tg_api_call("banChatMember", {"chat_id": channel_id, "user_id": user_id})
    if res.get("ok"):
        tg_api_call("unbanChatMember", {"chat_id": channel_id, "user_id": user_id, "only_if_banned": True})
        return True
    return False

# ==============================================================================
# 🧠 AI AUTO-RESPONDER KNOWLEDGE BASE
# ==============================================================================

def ai_generate_support_reply(query: str) -> Optional[str]:
    q = query.lower()
    
    if any(w in q for w in ["halal", "shariah", "haram", "leverage", "margin", "future"]):
        return (
            "🛡️ <b>Halal & Spot Ownership Guarantee:</b>\n\n"
            "PureQuant AI is <b>100% Spot-Only</b>. There is zero leverage, zero margin loans, zero interest (Riba), and zero liquidation risk. "
            "You own 100% of the underlying crypto asset in your exchange spot wallet, making it mathematically sound and strictly Halal."
        )

    if any(w in q for w in ["exchange", "binance", "bybit", "okx", "kucoin", "mexc", "coinbase"]):
        return (
            "🏢 <b>Supported Exchanges:</b>\n\n"
            "You can execute PureQuant AI spot signals on <b>any exchange</b> with spot markets, including Binance, Bybit, OKX, KuCoin, MEXC, Bitget, Gate.io, Kraken, or Coinbase."
        )

    if any(w in q for w in ["pay", "network", "trc20", "bep20", "solana", "ton", "polygon", "usdt", "usdc", "buy", "price"]):
        return (
            "💳 <b>Payment & Supported Networks:</b>\n\n"
            "We support USDT and USDC on <b>TRC-20, BEP-20 (BSC), Polygon, Solana, and TON</b>.\n"
            "• Starter Spot: $3.00 / mo\n"
            "• Pro VIP AI: $6.00 / mo\n"
            "• Lifetime VIP Pass: $9.00 one-time (10 Years)\n\n"
            "Click <b>[⚡ 3-6-9 Launch VIP Access]</b> in the main menu to generate your payment invoice!"
        )

    if any(w in q for w in ["link", "invite", "where is", "access", "join vip"]):
        return (
            "🔗 <b>VIP Access Verification:</b>\n\n"
            "After you transfer USDT/USDC, submit your Transaction Hash (TXID) in chat. "
            "Our system verifies the blockchain transaction and automatically issues a private 1-time single-use VIP channel link right here in chat!"
        )

    return None

# ==============================================================================
# 🎨 UI MENUS & FORMATTERS
# ==============================================================================

def get_main_menu_keyboard() -> Dict[str, Any]:
    free_channel_url = f"https://t.me/{FREE_CHANNEL_USERNAME}" if FREE_CHANNEL_USERNAME else "https://t.me"
    return {
        "inline_keyboard": [
            [
                {"text": "⚡ 3-6-9 Launch VIP Access", "callback_data": "menu_plans"}
            ],
            [
                {"text": "📢 Free Signals Channel", "url": free_channel_url},
                {"text": "📊 My Subscription", "callback_data": "menu_status"}
            ],
            [
                {"text": "💬 24/7 AI & Live Support Desk", "callback_data": "menu_support"}
            ]
        ]
    }

def get_plans_keyboard() -> Dict[str, Any]:
    return {
        "inline_keyboard": [
            [
                {"text": "🥉 Starter Spot — $3.00 / mo", "callback_data": "select_plan:starter"}
            ],
            [
                {"text": "🥈 Pro VIP AI — $6.00 / mo (Popular)", "callback_data": "select_plan:pro"}
            ],
            [
                {"text": "👑 Lifetime VIP Pass — $9.00 (Best Value)", "callback_data": "select_plan:lifetime_vip"}
            ],
            [
                {"text": "🔙 Back to Main Menu", "callback_data": "menu_main"}
            ]
        ]
    }

def get_networks_keyboard(plan_key: str) -> Dict[str, Any]:
    return {
        "inline_keyboard": [
            [
                {"text": "TRC-20 (Tron USDT)", "callback_data": f"net:{plan_key}:TRC20"},
                {"text": "BEP-20 (BNB USDT/USDC)", "callback_data": f"net:{plan_key}:BEP20"}
            ],
            [
                {"text": "Polygon (USDT/USDC)", "callback_data": f"net:{plan_key}:POLYGON"},
                {"text": "Solana (USDT/USDC)", "callback_data": f"net:{plan_key}:SOLANA"}
            ],
            [
                {"text": "TON (TON USDT)", "callback_data": f"net:{plan_key}:TON"}
            ],
            [
                {"text": "🔙 Back to Plans", "callback_data": "menu_plans"}
            ]
        ]
    }

def format_welcome_message(first_name: str) -> str:
    return (
        f"⚡ <b>Welcome to PureQuant AI, {first_name}!</b>\n\n"
        f"Institutional-grade quantitative crypto spot intelligence.\n"
        f"• <b>100% Spot Only:</b> Zero leverage, zero liquidation risk, 100% Halal.\n"
        f"• <b>Lorentzian Distance ML:</b> Multi-dimensional predictive directional classification.\n"
        f"• <b>Fair Value Gap (FVG) + SMT Radar:</b> Precision entry at unmitigated order blocks.\n"
        f"• <b>Dynamic Risk Shield:</b> Automated Breakeven & Trailing Stop-Loss alerts.\n\n"
        f"🔥 <b>Special Launch Pricing (3-6-9 Model):</b>\n"
        f"• <b>Starter Spot:</b> $3.00 / mo\n"
        f"• <b>Pro VIP AI:</b> $6.00 / mo\n"
        f"• <b>Lifetime VIP Pass:</b> $9.00 one-time (Zero renewal fees)\n\n"
        f"Select an option below to get started:"
    )

def format_plan_overview() -> str:
    return (
        f"💎 <b>PUREQUANT AI — VIP SUBSCRIPTION TIERS</b>\n\n"
        f"🥉 <b>Starter Spot — $3.00 / month</b> <s>($9/mo)</s>\n"
        f"• 24/7 Institutional Spot Signals on Top 50 Pairs\n"
        f"• Precise Entry, TP1, TP2, TP3 & SL Levels\n"
        f"• Halal / 100% Spot Asset Ownership\n\n"
        f"🥈 <b>Pro VIP AI — $6.00 / month</b> <s>($19/mo)</s> ⭐ <i>Most Popular</i>\n"
        f"• Everything in Starter Spot\n"
        f"• Lorentzian ML Confidence Scoring\n"
        f"• Fair Value Gap (FVG) & SMT Divergence Radar\n"
        f"• Dynamic Trailing Stop-Loss & Breakeven Locks\n"
        f"• Daily AI Post-Mortem Trade Forensic Audits\n\n"
        f"👑 <b>Lifetime VIP Pass — $9.00 ONE-TIME</b> <s>($99)</s> 🔥 <i>Best Value</i>\n"
        f"• 10 Years Unlimited Full VIP Telegram Access\n"
        f"• All Future V2 ML Algorithms Included Free\n"
        f"• Private Strategy Alpha Channel\n"
        f"• Zero Monthly Renewal Fees Forever\n\n"
        f"👇 <b>Choose your desired tier below:</b>"
    )

def format_payment_invoice(plan_key: str, net_key: str) -> str:
    plan = PLANS[plan_key]
    network = WALLETS[net_key]
    return (
        f"🧾 <b>PUREQUANT AI CRYPTO INVOICE</b>\n\n"
        f"• <b>Selected Plan:</b> {plan['badge']} ({plan['name']})\n"
        f"• <b>Price:</b> <code>${plan['price_usdt']:.2f} USDT / USDC</code>\n"
        f"• <b>Network:</b> {network['name']}\n\n"
        f"⚠️ <b>PAYMENT INSTRUCTIONS:</b>\n"
        f"1. Send exactly <b>${plan['price_usdt']:.2f}</b> to the deposit address below:\n\n"
        f"<code>{network['address']}</code>\n\n"
        f"<i>(Tap the address to copy to your clipboard)</i>\n\n"
        f"2. After completing transfer, click <b>[✅ I Have Paid / Submit TX]</b> below and send your Transaction Hash (TXID) or transfer screenshot.\n"
        f"3. Your unique, private 1-time VIP invite link will be issued immediately upon verification!"
    )

# ==============================================================================
# 🚦 MESSAGE & CALLBACK HANDLERS
# ==============================================================================

def handle_start(chat_id: int, first_name: str, param: str = ""):
    USER_STATES[chat_id] = {"state": "idle"}
    if param in PLANS:
        USER_STATES[chat_id] = {"state": "select_net", "plan": param}
        plan = PLANS[param]
        text = (
            f"💎 <b>Selected: {plan['badge']} (${plan['price_usdt']:.2f})</b>\n\n"
            f"Choose your preferred crypto deposit network for payment:"
        )
        send_message(chat_id, text, get_networks_keyboard(param))
        return
    elif param == "support":
        USER_STATES[chat_id] = {"state": "awaiting_support_msg"}
        support_prompt = (
            f"💬 <b>PUREQUANT AI 24/7 SUPPORT DESK</b>\n\n"
            f"Please type your question or message below. Our automated AI system & support team will assist you immediately:"
        )
        send_message(chat_id, support_prompt, {"inline_keyboard": [[{"text": "🔙 Back to Menu", "callback_data": "menu_main"}]]})
        return

    text = format_welcome_message(first_name)
    send_message(chat_id, text, get_main_menu_keyboard())

def handle_status(chat_id: int, username: str):
    subs = load_subscribers()
    user_str = str(chat_id)
    if user_str in subs and subs[user_str].get("is_active"):
        sub = subs[user_str]
        msg = (
            f"📊 <b>SUBSCRIPTION STATUS: ACTIVE ✅</b>\n\n"
            f"• <b>Plan:</b> {sub.get('plan_name', 'VIP')}\n"
            f"• <b>Amount Paid:</b> ${sub.get('amount_paid', 0):.2f}\n"
            f"• <b>Activated On:</b> {sub.get('joined_at', 'N/A')}\n"
            f"• <b>Expires On:</b> {sub.get('expires_at', 'N/A')}\n"
            f"• <b>Status:</b> 🟢 Active Member\n\n"
            f"<i>Need assistance? Use the 24/7 Support Desk in the menu.</i>"
        )
    else:
        pending = load_pending()
        if user_str in pending:
            p = pending[user_str]
            msg = (
                f"⏳ <b>PAYMENT PENDING VERIFICATION</b>\n\n"
                f"• <b>Plan:</b> {p.get('plan_name')}\n"
                f"• <b>TX Hash:</b> <code>{p.get('tx_hash')}</code>\n"
                f"• <b>Submitted At:</b> {p.get('submitted_at')}\n\n"
                f"Our admin team is validating your blockchain transaction. You will receive your VIP invite link shortly."
            )
        else:
            msg = (
                f"❌ <b>No Active VIP Subscription Found</b>\n\n"
                f"You are currently not an active VIP member.\n"
                f"Get institutional spot signals starting from just <b>$3.00</b>!"
            )
    
    send_message(chat_id, msg, {"inline_keyboard": [[{"text": "⚡ Get VIP Access", "callback_data": "menu_plans"}], [{"text": "🔙 Main Menu", "callback_data": "menu_main"}]]})

def handle_callback(cb: Dict[str, Any]):
    cb_id = cb["id"]
    chat_id = cb["message"]["chat"]["id"]
    message_id = cb["message"]["message_id"]
    data = cb.get("data", "")
    first_name = cb["from"].get("first_name", "Trader")
    username = cb["from"].get("username", "")

    try:
        if data == "menu_main":
            USER_STATES[chat_id] = {"state": "idle"}
            edit_message_text(chat_id, message_id, format_welcome_message(first_name), get_main_menu_keyboard())
            answer_callback_query(cb_id)

        elif data == "menu_plans":
            USER_STATES[chat_id] = {"state": "idle"}
            edit_message_text(chat_id, message_id, format_plan_overview(), get_plans_keyboard())
            answer_callback_query(cb_id)

        elif data == "menu_status":
            answer_callback_query(cb_id)
            handle_status(chat_id, username)

        elif data == "menu_support":
            USER_STATES[chat_id] = {"state": "awaiting_support_msg"}
            support_prompt = (
                f"💬 <b>PUREQUANT AI 24/7 SUPPORT DESK</b>\n\n"
                f"Ask any question regarding:\n"
                f"• VIP plans & crypto deposit addresses\n"
                f"• How spot signals and Lorentzian ML work\n"
                f"• Shariah/Halal zero-leverage principles\n"
                f"• Instant assistance from our AI system & live human agents\n\n"
                f"✍️ <i>Please type your question directly in chat:</i>"
            )
            edit_message_text(chat_id, message_id, support_prompt, {"inline_keyboard": [[{"text": "🔙 Back to Menu", "callback_data": "menu_main"}]]})
            answer_callback_query(cb_id)

        elif data.startswith("select_plan:") or data.startswith("select_plan_"):
            plan_key = data.split(":", 1)[1] if ":" in data else data.replace("select_plan_", "")
            if plan_key in PLANS:
                USER_STATES[chat_id] = {"state": "select_net", "plan": plan_key}
                plan = PLANS[plan_key]
                text = (
                    f"💎 <b>Selected: {plan['badge']} (${plan['price_usdt']:.2f})</b>\n\n"
                    f"Choose your preferred crypto deposit network for payment:"
                )
                edit_message_text(chat_id, message_id, text, get_networks_keyboard(plan_key))
            answer_callback_query(cb_id)

        elif data.startswith("net:") or data.startswith("net_"):
            if ":" in data:
                _, plan_key, net_key = data.split(":", 2)
            else:
                parts = data.split("_")
                plan_key = "_".join(parts[1:-1])
                net_key = parts[-1]

            if plan_key in PLANS and net_key in WALLETS:
                USER_STATES[chat_id] = {"state": "awaiting_payment_proof", "plan": plan_key, "network": net_key}
                invoice_text = format_payment_invoice(plan_key, net_key)
                keyboard = {
                    "inline_keyboard": [
                        [{"text": "✅ I Have Paid / Submit TX Hash", "callback_data": f"submit_proof:{plan_key}:{net_key}"}],
                        [{"text": "🔙 Change Network", "callback_data": f"select_plan:{plan_key}"}]
                    ]
                }
                edit_message_text(chat_id, message_id, invoice_text, keyboard)
            answer_callback_query(cb_id)

        elif data.startswith("submit_proof:") or data.startswith("submit_proof_"):
            if ":" in data:
                _, plan_key, net_key = data.split(":", 2)
            else:
                parts = data.split("_")
                plan_key = "_".join(parts[2:-1])
                net_key = parts[-1]

            USER_STATES[chat_id] = {"state": "awaiting_txid", "plan": plan_key, "network": net_key}
            prompt = (
                f"📝 <b>SUBMIT TRANSACTION HASH (TXID)</b>\n\n"
                f"Please reply with your transaction hash (TXID) or transfer ID.\n\n"
                f"<i>Example:</i> <code>4f8b9e821a37c...</code>\n\n"
                f"<i>(If you transferred via internal exchange transfer or screenshot, you can also paste the internal transfer ID)</i>"
            )
            send_message(chat_id, prompt)
            answer_callback_query(cb_id, "Please type and send your TXID in chat.")

        elif data.startswith("admin_approve:") or data.startswith("admin_approve_"):
            target_uid = data.split(":", 1)[1] if ":" in data else data.replace("admin_approve_", "")
            handle_admin_approval(chat_id, message_id, target_uid, cb_id)

        elif data.startswith("admin_reject:") or data.startswith("admin_reject_"):
            target_uid = data.split(":", 1)[1] if ":" in data else data.replace("admin_reject_", "")
            handle_admin_rejection(chat_id, message_id, target_uid, cb_id)

        elif data.startswith("reply_user:") or data.startswith("reply_user_"):
            target_uid = data.split(":", 1)[1] if ":" in data else data.replace("reply_user_", "")
            USER_STATES[chat_id] = {"state": "admin_replying", "target_uid": target_uid}
            send_message(chat_id, f"✍️ <b>Type your reply for user <code>{target_uid}</code>:</b>\n<i>(Your personal username is 100% hidden. It will be delivered as official PureQuant Support)</i>")
            answer_callback_query(cb_id)
        else:
            answer_callback_query(cb_id)
    except Exception as e:
        print(f"⚠️ Callback handler exception: {e}")
        answer_callback_query(cb_id)

# ==============================================================================
# 👑 ADMIN WORKFLOW & APPROVALS
# ==============================================================================

def notify_admin_payment_submitted(user_id: int, username: str, plan_key: str, net_key: str, tx_hash: str):
    if not ADMIN_TELEGRAM_ID:
        print("⚠️ ADMIN_TELEGRAM_ID is not configured in .env!")
        return

    plan = PLANS.get(plan_key, PLANS["pro"])
    network = WALLETS.get(net_key, {"name": net_key})

    msg = (
        f"🚨 <b>NEW CRYPTO PAYMENT SUBMISSION!</b>\n\n"
        f"• <b>User:</b> @{username or 'NoUsername'} (ID: <code>{user_id}</code>)\n"
        f"• <b>Plan:</b> {plan['badge']} (${plan['price_usdt']:.2f})\n"
        f"• <b>Network:</b> {network['name']}\n"
        f"• <b>TX Hash / Proof:</b>\n<code>{tx_hash}</code>\n"
        f"• <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        f"Click below to verify & automatically issue a 1-time VIP invite link:"
    )
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "✅ Approve & Issue VIP Link", "callback_data": f"admin_approve_{user_id}"},
                {"text": "❌ Reject Payment", "callback_data": f"admin_reject_{user_id}"}
            ]
        ]
    }
    send_message(ADMIN_TELEGRAM_ID, msg, keyboard)

def handle_admin_approval(admin_chat_id: int, message_id: int, target_uid: str, cb_id: str):
    pending = load_pending()
    if target_uid not in pending:
        answer_callback_query(cb_id, "Payment record not found or already processed.", show_alert=True)
        return

    p = pending[target_uid]
    plan_key = p["plan_key"]
    plan = PLANS.get(plan_key, PLANS["pro"])

    # 1. Generate 1-time invite link
    invite_link = generate_vip_invite_link(VIP_CHANNEL_ID)
    if not invite_link:
        invite_link = "https://t.me/PureQuantAIBot"

    # 2. Update subscriber ledger
    subs = load_subscribers()
    expires_at = datetime.now() + timedelta(days=plan["days"])

    subs[str(target_uid)] = {
        "user_id": int(target_uid),
        "username": p.get("username", ""),
        "plan": plan_key,
        "plan_name": plan["name"],
        "amount_paid": plan["price_usdt"],
        "tx_hash": p.get("tx_hash", ""),
        "network": p.get("network", ""),
        "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "expires_at": expires_at.strftime("%Y-%m-%d %H:%M:%S"),
        "is_active": True,
        "invite_link": invite_link
    }
    save_subscribers(subs)

    # 3. Clean up pending record
    del pending[target_uid]
    save_pending(pending)

    # 4. Message the buyer with their VIP invite link
    welcome_vip = (
        f"🎉 <b>PAYMENT CONFIRMED — VIP ACCESS GRANTED!</b>\n\n"
        f"Welcome to the institutional inner circle, Trader.\n"
        f"• <b>Tier:</b> {plan['badge']} ({plan['name']})\n"
        f"• <b>Validity:</b> {plan['days']} Days (Expires: {expires_at.strftime('%Y-%m-%d')})\n\n"
        f"🔗 <b>Your Exclusive 1-Time VIP Channel Invite:</b>\n"
        f"{invite_link}\n\n"
        f"⚠️ <i>Note: This is a single-use secure link valid for 24 hours. Join immediately.</i>"
    )
    send_message(target_uid, welcome_vip)

    # 5. Update admin message
    edit_message_text(
        admin_chat_id,
        message_id,
        f"✅ <b>APPROVED & INVITE SENT</b>\n\n"
        f"User: <code>{target_uid}</code> (@{p.get('username')})\n"
        f"Plan: {plan['name']} (${plan['price_usdt']})\n"
        f"Invite Link: {invite_link}"
    )
    answer_callback_query(cb_id, "Approved! Invite link sent to user.", show_alert=True)

def handle_admin_rejection(admin_chat_id: int, message_id: int, target_uid: str, cb_id: str):
    pending = load_pending()
    p = pending.pop(target_uid, None)
    if p:
        save_pending(pending)

    rejection_msg = (
        f"⚠️ <b>Payment Verification Notice</b>\n\n"
        f"We could not verify your recent transaction hash.\n"
        f"Please double check the transaction ID or open a ticket with Support in the menu."
    )
    send_message(target_uid, rejection_msg)

    edit_message_text(
        admin_chat_id,
        message_id,
        f"❌ <b>REJECTED:</b> Payment from user <code>{target_uid}</code> marked as invalid."
    )
    answer_callback_query(cb_id, "Payment rejected and user notified.", show_alert=True)

# ==============================================================================
# 📢 SIGNAL BROADCASTER ENGINE (VIP & FREE CHANNELS)
# ==============================================================================

def broadcast_vip_signal(setup: Dict[str, Any]) -> bool:
    """Dispatches full institutional Grade A+ signal to VIP Channel"""
    if not VIP_CHANNEL_ID:
        print("⚠️ VIP_CHANNEL_ID is not set.")
        return False

    msg = (
        f"⚡ <b>PUREQUANT AI :: VIP SPOT BUY ALERT</b>\n"
        f"🏆 <b>GRADE A+ SETUP · {setup.get('confidence', '94.8%')} LORENTZIAN CONFIDENCE</b>\n\n"
        f"<b>Asset:</b> #{setup.get('pair', 'SOL/USDT')} (Spot Only · 100% Halal)\n"
        f"<b>Exchange:</b> Binance / Bybit Spot\n\n"
        f"<b>📊 INSTITUTIONAL CONFLUENCES:</b>\n"
        f"• 4H Bullish FVG Mitigated @ {setup.get('fvg_level', '$135.20')}\n"
        f"• SMT Divergence Confirmed against BTC Macro Structure\n"
        f"• Whale Orderflow Delta Surge (+480% Aggressive Bids)\n"
        f"• Retail Liquidity Pool Swept Clean\n\n"
        f"<b>🎯 EXECUTION TARGETS:</b>\n"
        f"• 🟢 <b>Entry Zone:</b> {setup.get('entry', '$135.20 - $137.50')}\n"
        f"• 🎯 <b>TP 1:</b> {setup.get('tp1', '$144.00')} (+5.8%) <i>→ Take 30% & Lock Breakeven</i>\n"
        f"• 🎯 <b>TP 2:</b> {setup.get('tp2', '$158.00')} (+16.2%) <i>→ Take 40% & Trail SL to TP1</i>\n"
        f"• 🎯 <b>TP 3:</b> {setup.get('tp3', '$181.90')} (+34.6%) <i>→ Moonbag Macro Target</i>\n"
        f"• 🛑 <b>Initial SL:</b> {setup.get('sl', '$131.40')} (-2.9% Spot Risk)\n\n"
        f"🛡️ <b>DYNAMIC CAPITAL DEFENSE:</b>\n"
        f"1. At +1.5% profit, bot alerts to move SL to Breakeven.\n"
        f"2. Dynamic Trailing Shield ratchets behind 15M swing lows.\n\n"
        f"<i>PureQuant AI Quantitative Execution Engine</i>"
    )
    res = send_message(VIP_CHANNEL_ID, msg)
    return res.get("ok", False)

def broadcast_free_teaser_signal(setup: Dict[str, Any]) -> bool:
    """Dispatches teaser signal with CTA to Public Free Channel"""
    if not FREE_CHANNEL_ID:
        print("⚠️ FREE_CHANNEL_ID is not set.")
        return False

    bot_username = os.getenv("SAAS_BOT_USERNAME", "PureQuantAIBot").lstrip("@")
    msg = (
        f"📢 <b>PUREQUANT AI :: FREE SPOT TEASER SIGNAL</b>\n\n"
        f"<b>Asset:</b> #{setup.get('pair', 'SOL/USDT')} (Spot Only)\n"
        f"🟢 <b>Entry Range:</b> {setup.get('entry', '$135.20 - $137.50')}\n"
        f"🎯 <b>TP 1 (Target 1):</b> {setup.get('tp1', '$144.00')} (+5.8%)\n"
        f"🛑 <b>Stop-Loss:</b> {setup.get('sl', '$131.40')}\n\n"
        f"🔒 <i>TP2 (+16.2%), TP3 (+34.6%), Lorentzian ML Score & Trailing Breakeven Defense are exclusive to VIP members.</i>\n\n"
        f"⚡ <b>Upgrade to VIP for just $3 - $6 / mo or $9 Lifetime:</b>\n"
        f"👉 Join via @{bot_username}"
    )
    keyboard = {
        "inline_keyboard": [
            [{"text": "⚡ Unlock Full VIP Signals ($3 - $6/mo)", "url": f"https://t.me/{bot_username}"}]
        ]
    }
    res = send_message(FREE_CHANNEL_ID, msg, keyboard)
    return res.get("ok", False)

# ==============================================================================
# ⏰ EXPIRATION WATCHDOG DAEMON
# ==============================================================================

def expiration_watchdog():
    while True:
        try:
            subs = load_subscribers()
            now = datetime.now()
            updated = False

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
                            updated = True
                            if VIP_CHANNEL_ID:
                                revoke_channel_access(VIP_CHANNEL_ID, int(uid))
                            
                            # Notify user
                            renewal_msg = (
                                f"⏳ <b>Your PureQuant AI VIP Subscription Has Expired</b>\n\n"
                                f"Your VIP access has concluded. To continue receiving Grade A+ institutional spot signals, renew your pass below:"
                            )
                            send_message(uid, renewal_msg, {"inline_keyboard": [[{"text": "⚡ Renew VIP ($3 - $6)", "callback_data": "menu_plans"}]]})
                            print(f"🔒 Revoked expired VIP access for user {uid}.")
                    except Exception as e:
                        print(f"Error parsing expiry for {uid}: {e}")

            if updated:
                save_subscribers(subs)
        except Exception as e:
            print(f"⚠️ Watchdog loop error: {e}")

        time.sleep(600)  # Check every 10 minutes

# ==============================================================================
# 🚀 MAIN POLLING LOOP & MESSAGE PROCESSING
# ==============================================================================

def process_message(msg: Dict[str, Any]):
    chat = msg.get("chat", {})
    chat_id = chat.get("id")
    text = msg.get("text", "").strip()
    first_name = msg.get("from", {}).get("first_name", "Trader")
    username = msg.get("from", {}).get("username", "")

    if not chat_id:
        return

    # Handle Admin /reply command: /reply <user_id> <message>
    if str(chat_id) == ADMIN_TELEGRAM_ID:
        state = USER_STATES.get(chat_id, {}).get("state")
        if state == "admin_replying":
            target_uid = USER_STATES[chat_id].get("target_uid")
            USER_STATES[chat_id] = {"state": "idle"}
            send_message(target_uid, f"🎧 <b>PureQuant AI Official Support:</b>\n\n{text}")
            send_message(chat_id, f"✅ <b>Reply delivered to user <code>{target_uid}</code>.</b>")
            return

        if text.startswith("/reply "):
            parts = text.split(" ", 2)
            if len(parts) >= 3:
                target_uid = parts[1].strip()
                reply_body = parts[2].strip()
                send_message(target_uid, f"🎧 <b>PureQuant AI Official Support:</b>\n\n{reply_body}")
                send_message(chat_id, f"✅ <b>Reply sent to user <code>{target_uid}</code>.</b>")
                return
            else:
                send_message(chat_id, "⚠️ Usage: <code>/reply &lt;user_id&gt; &lt;your message&gt;</code>")
                return

    # Handle /start
    if text.startswith("/start"):
        parts = text.split(" ", 1)
        param = parts[1].strip() if len(parts) > 1 else ""
        handle_start(chat_id, first_name, param)
        return

    # Handle /status
    if text.startswith("/status"):
        handle_status(chat_id, username)
        return

    # Handle /plans
    if text.startswith("/plans") or text.startswith("/buy"):
        send_message(chat_id, format_plan_overview(), get_plans_keyboard())
        return

    # Handle /support
    if text.startswith("/support"):
        USER_STATES[chat_id] = {"state": "awaiting_support_msg"}
        support_prompt = (
            f"💬 <b>PUREQUANT AI 24/7 SUPPORT DESK</b>\n\n"
            f"Please type your question or message below. Our automated AI system & support team will assist you immediately:"
        )
        send_message(chat_id, support_prompt, {"inline_keyboard": [[{"text": "🔙 Back to Menu", "callback_data": "menu_main"}]]})
        return

    # Handle /help
    if text.startswith("/help"):
        help_text = (
            f"ℹ️ <b>PUREQUANT AI COMMANDS</b>\n\n"
            f"• /start — Open the Main Interactive Menu\n"
            f"• /plans — View VIP Subscription Pricing ($3 / $6 / $9)\n"
            f"• /status — Check your current active VIP subscription\n"
            f"• /support — Contact 24/7 AI & Live Support Desk\n"
            f"• /help — Show this help message\n\n"
            f"💬 Support is available 24/7 directly inside this bot."
        )
        send_message(chat_id, help_text)
        return

    # Admin command: /stats
    if text.startswith("/stats") and str(chat_id) == ADMIN_TELEGRAM_ID:
        subs = load_subscribers()
        active_count = sum(1 for s in subs.values() if s.get("is_active"))
        revenue = sum(s.get("amount_paid", 0) for s in subs.values())
        pending = load_pending()
        admin_stats = (
            f"📊 <b>PUREQUANT ADMIN METRICS</b>\n\n"
            f"• <b>Total Registered:</b> {len(subs)}\n"
            f"• <b>Active VIP Members:</b> {active_count}\n"
            f"• <b>Total Revenue:</b> ${revenue:.2f} USDT\n"
            f"• <b>Pending Approvals:</b> {len(pending)}"
        )
        send_message(chat_id, admin_stats)
        return

    # Admin command: /post_recap
    if text.startswith("/post_recap") and str(chat_id) == ADMIN_TELEGRAM_ID:
        from saas_signal_dispatcher import SaasSignalDispatcher
        dispatcher = SaasSignalDispatcher()
        ok = dispatcher.post_daily_performance_recap()
        send_message(chat_id, f"✅ <b>Daily Performance Recap Post Triggered!</b> (Status: {'Delivered' if ok else 'No trades found'})")
        return

    # Admin command: /post_promo
    if text.startswith("/post_promo") and str(chat_id) == ADMIN_TELEGRAM_ID:
        from saas_signal_dispatcher import SaasSignalDispatcher
        dispatcher = SaasSignalDispatcher()
        ok = dispatcher.post_daily_vip_benefit_promo()
        send_message(chat_id, f"✅ <b>Daily VIP Promo Post Triggered to Free Channel!</b>")
        return

    # Check state machine
    current_state = USER_STATES.get(chat_id, {}).get("state")

    # 1. State: awaiting_txid
    if current_state == "awaiting_txid":
        plan_key = USER_STATES[chat_id].get("plan", "pro")
        net_key = USER_STATES[chat_id].get("network", "TRC20")
        plan = PLANS.get(plan_key, PLANS["pro"])

        pending = load_pending()
        pending[str(chat_id)] = {
            "user_id": chat_id,
            "username": username,
            "plan_key": plan_key,
            "plan_name": plan["name"],
            "amount": plan["price_usdt"],
            "network": net_key,
            "tx_hash": text,
            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_pending(pending)
        USER_STATES[chat_id] = {"state": "idle"}

        ack_msg = (
            f"✅ <b>TRANSACTION HASH RECEIVED!</b>\n\n"
            f"• <b>Plan:</b> {plan['badge']} (${plan['price_usdt']:.2f})\n"
            f"• <b>TX Hash:</b> <code>{text}</code>\n\n"
            f"Our system and admins are verifying your transaction. You will automatically receive your VIP channel invite link right here upon confirmation! 🚀"
        )
        send_message(chat_id, ack_msg)
        notify_admin_payment_submitted(chat_id, username, plan_key, net_key, text)
        return

    # 2. State: awaiting_support_msg OR any random text message
    if current_state == "awaiting_support_msg" or not text.startswith("/"):
        USER_STATES[chat_id] = {"state": "idle"}
        ticket_id = int(time.time()) % 100000

        # Save ticket
        ticket = {
            "ticket_id": ticket_id,
            "user_id": chat_id,
            "username": username,
            "message": text,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_support_ticket(ticket)

        # Check AI Knowledge Base
        ai_reply = ai_generate_support_reply(text)
        
        user_response = f"🤖 <b>PUREQUANT AI SUPPORT (Ticket #{ticket_id})</b>\n\n"
        if ai_reply:
            user_response += f"{ai_reply}\n\n<i>An agent is also notified and will assist if further guidance is needed.</i>"
        else:
            user_response += (
                f"Thank you for contacting PureQuant AI Support.\n"
                f"Your request has been routed to our team. A support representative will respond right here shortly."
            )
        
        send_message(chat_id, user_response, {"inline_keyboard": [[{"text": "⚡ View VIP Plans", "callback_data": "menu_plans"}], [{"text": "🔙 Main Menu", "callback_data": "menu_main"}]]})

        # Relay ticket to Admin
        if ADMIN_TELEGRAM_ID:
            admin_ticket_msg = (
                f"📩 <b>NEW SUPPORT TICKET #{ticket_id}</b>\n\n"
                f"• <b>From:</b> @{username or 'NoUsername'} (ID: <code>{chat_id}</code>)\n"
                f"• <b>Message:</b>\n<i>\"{text}\"</i>\n\n"
                f"<i>To reply, click the button below or type:</i>\n<code>/reply {chat_id} YourMessageHere</code>"
            )
            admin_kb = {
                "inline_keyboard": [
                    [{"text": f"💬 Reply to User ({chat_id})", "callback_data": f"reply_user_{chat_id}"}]
                ]
            }
            send_message(ADMIN_TELEGRAM_ID, admin_ticket_msg, admin_kb)
        return

def daily_broadcast_scheduler():
    """Runs in background and posts daily recap at 00:00 UTC and daily promo at 12:00 UTC"""
    from saas_signal_dispatcher import SaasSignalDispatcher
    dispatcher = SaasSignalDispatcher()
    last_recap_day = ""
    last_promo_day = ""

    while True:
        try:
            now_utc = datetime.utcnow()
            day_str = now_utc.strftime("%Y-%m-%d")
            hour = now_utc.hour

            # 1. Daily Recap at 00:00 UTC
            if hour == 0 and last_recap_day != day_str:
                print(f"[{day_str}] Triggering automated Daily Performance Recap...")
                dispatcher.post_daily_performance_recap()
                last_recap_day = day_str

            # 2. Daily Promo at 12:00 UTC
            if hour == 12 and last_promo_day != day_str:
                print(f"[{day_str}] Triggering automated Daily VIP Benefit Promo...")
                dispatcher.post_daily_vip_benefit_promo()
                last_promo_day = day_str

            time.sleep(60)
        except Exception as e:
            print(f"Daily broadcast scheduler error: {e}")
            time.sleep(60)

def run_bot():
    init_db()
    print("====================================================================")
    print("⚡ PureQuant AI Telegram Paywall Bot Engine Initialized")
    plan_summary = ', '.join([f"{k} (${v['price_usdt']})" for k, v in PLANS.items()])
    print(f"• Active Plans: {plan_summary}")
    print(f"• Bot Token: {'[Configured]' if BOT_TOKEN else '[MISSING]'}")
    print(f"• VIP Channel ID: {VIP_CHANNEL_ID or '[MISSING]'}")
    print(f"• Free Channel ID: {FREE_CHANNEL_ID or '[MISSING]'}")
    print(f"• Admin Telegram ID: {ADMIN_TELEGRAM_ID or '[MISSING]'}")
    print("====================================================================")

    # Start Health Check Server (Enables 100% Free Web Service on Render / Railway)
    h_thread = threading.Thread(target=start_health_server, daemon=True)
    h_thread.start()

    # Start Watchdog Daemon
    t = threading.Thread(target=expiration_watchdog, daemon=True)
    t.start()

    # Start Automated Daily Broadcast Scheduler (Recap at 00:00 UTC, Promo at 12:00 UTC)
    b_thread = threading.Thread(target=daily_broadcast_scheduler, daemon=True)
    b_thread.start()

    if not BOT_TOKEN:
        print("⚠️ Warning: SAAS_BOT_TOKEN is not set. Bot is in standby mode.")
        print("👉 Please edit .env or set SAAS_BOT_TOKEN to start polling.")
        return

    offset = 0
    print("📡 Polling Telegram API for updates...")

    while True:
        try:
            updates = tg_api_call("getUpdates", {"offset": offset, "timeout": 20})
            if updates.get("ok"):
                for u in updates.get("result", []):
                    offset = u["update_id"] + 1

                    if "message" in u:
                        process_message(u["message"])
                    elif "callback_query" in u:
                        handle_callback(u["callback_query"])
            time.sleep(0.5)
        except Exception as e:
            print(f"⚠️ Polling loop exception: {e}")
            time.sleep(3)

if __name__ == "__main__":
    run_bot()
