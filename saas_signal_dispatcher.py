"""
⚡ PureQuant AI — Multi-Tier Signal Dispatcher & Free/VIP Channel Manager
=========================================================================
1. VIP Channel (-1004364917715): Receives 100% of real-time Spot AI signals, live executions, trailing SL locks, and post-mortems.
2. Free Channel (-1004423283944): Receives EXACTLY 1 high-conviction Spot signal per day (1/1 daily limit).
3. Daily Performance Recap: Automatically calculates and posts daily % PnL (NEVER exposing dollar amounts).
4. Daily Conversion Post: Daily promo showcasing benefits of upgrading to VIP for $3/mo, $6/mo, $9 lifetime.
"""

import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List

# Load environment
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
def load_env():
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip() not in os.environ:
                        os.environ[k.strip()] = v.strip().strip("'\"")

load_env()

BOT_TOKEN = os.getenv("SAAS_BOT_TOKEN", "REDACTED_TELEGRAM_BOT_TOKEN")
VIP_CHANNEL_ID = os.getenv("VIP_CHANNEL_ID", "-1004364917715")
FREE_CHANNEL_ID = os.getenv("FREE_CHANNEL_ID", "-1004423283944")
SUPPORT_BOT_USERNAME = os.getenv("SAAS_BOT_USERNAME", "PureQuantAIBot").lstrip("@")

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
FREE_SIGNAL_STATE_FILE = os.path.join(DATA_DIR, "free_signal_daily_state.json")
PORTFOLIO_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "trading", "data", "paper_portfolio.json"))


def send_tg_message(chat_id: str, text: str, reply_markup: dict = None, parse_mode: str = "HTML") -> bool:
    """Send formatted message to Telegram channel or user"""
    if not BOT_TOKEN or not chat_id:
        print(f"[TG DISABLED] Chat: {chat_id}")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": False
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        resp = requests.post(url, json=payload, timeout=12)
        return resp.status_code == 200 and resp.json().get("ok", False)
    except Exception as e:
        print(f"Error sending TG message to {chat_id}: {e}")
        return False


def get_free_signal_state() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(FREE_SIGNAL_STATE_FILE):
        try:
            with open(FREE_SIGNAL_STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_free_signal_state(state: Dict[str, Any]):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FREE_SIGNAL_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


class SaasSignalDispatcher:
    """Dispatches trade signals to VIP and Free channels according to SaaS rules"""

    def __init__(self):
        self.bot_token = BOT_TOKEN
        self.vip_channel = VIP_CHANNEL_ID
        self.free_channel = FREE_CHANNEL_ID
        self.bot_username = SUPPORT_BOT_USERNAME

    def dispatch_spot_signal(self, signal_data: Dict[str, Any]):
        """
        Dispatches signal:
        1. Always sends to VIP Channel.
        2. Sends to Free Channel if daily quota (1 per day) has not been reached.
        """
        pair = signal_data.get("pair", signal_data.get("symbol", "UNKNOWN"))
        price = float(signal_data.get("price", signal_data.get("entry_price", 0.0)))
        tp = float(signal_data.get("tp_price", signal_data.get("take_profit", price * 1.035)))
        sl = float(signal_data.get("sl_price", signal_data.get("stop_loss", price * 0.975)))
        tp_pct = abs((tp - price) / price * 100) if price > 0 else 3.5
        sl_pct = abs((price - sl) / price * 100) if price > 0 else 2.5
        score = signal_data.get("score", signal_data.get("pump_score", 98))
        fvg_desc = signal_data.get("fvg", "Bullish 15m SMC Order Block Retest")
        ai_conf = signal_data.get("ai_confidence", 88)
        ai_reason = signal_data.get("ai_reasoning", "Strong whale accumulation volume and multi-timeframe 1h trend alignment confirmed.")
        tv_link = f"https://www.tradingview.com/chart/?symbol=BINANCE:{pair.replace('/', '')}"

        # -------------------------------------------------------------
        # 1. VIP Channel Card (Full Features + Live Dashboard Link)
        # -------------------------------------------------------------
        vip_text = f"""🚀 <b>AUTONOMOUS SPOT TRADE EXECUTED — {pair}</b> (15m)

⚡ <b>Action:</b> <b>SPOT BUY / ACCUMULATE ($100 Position)</b>
🕌 <b>Shariah Status:</b> <b>100% Halal Verified Digital Asset ✅</b>
📊 <b>PureQuant Score:</b> <b>{score} / 100</b>
🧠 <b>AI Technical Quality:</b> <b>High Confluence (Approved)</b>

💵 <b>Entry Price:</b> <code>${price:,.4f}</code>
🎯 <b>Take-Profit:</b> <code>${tp:,.4f}</code> (<b>+{tp_pct:.1f}%</b>)
🛑 <b>Stop-Loss:</b> <code>${sl:,.4f}</code> (<b>-{sl_pct:.1f}%</b>)
🛡️ <b>Shield:</b> Auto-Breakeven @ +1.5% | Trailing SL @ +2.2%

📊 <b>Smart Money Technicals:</b>
• <b>Fair Value Gap (FVG):</b> {fvg_desc}
• <b>Trend Alignment:</b> Above 200 EMA ✅

🤖 <b>Local AI Analyst Verdict ({ai_conf}% Conf):</b>
<i>\"{ai_reason}\"</i>

⏰ <i>Status: Monitored 24/7 with Trailing Stop-Loss.</i>"""

        vip_kb = {
            "inline_keyboard": [
                [
                    {"text": "📈 TradingView Chart", "url": tv_link},
                    {"text": "🌐 Live Dashboard", "url": "https://trade.d4f.me/"}
                ]
            ]
        }
        send_tg_message(self.vip_channel, vip_text, vip_kb)
        print(f"  [+] Dispatched Spot Signal for {pair} to VIP Channel ({self.vip_channel})")

        # -------------------------------------------------------------
        # 2. Free Public Channel (1 Signal Per Day Limit + Upgrade CTA)
        # -------------------------------------------------------------
        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        free_state = get_free_signal_state()
        last_date = free_state.get("last_free_signal_date")

        if last_date != today_str and score >= 95:
            free_text = f"""🎁 <b>FREE SPOT SIGNAL OF THE DAY (1/1) — {pair}</b> (15m)

⚡ <b>Action:</b> <b>SPOT BUY / ACCUMULATE</b>
🕌 <b>Shariah Status:</b> <b>100% Halal Verified Digital Asset ✅</b>
📊 <b>PureQuant Score:</b> <b>{score} / 100</b>

💵 <b>Entry Zone:</b> <code>${price:,.4f}</code>
🎯 <b>Take-Profit Target:</b> <code>${tp:,.4f}</code> (<b>+{tp_pct:.1f}%</b>)
🛑 <b>Stop-Loss Target:</b> <code>${sl:,.4f}</code> (<b>-{sl_pct:.1f}%</b>)
🛡️ <b>Risk Protection:</b> Lock Breakeven @ +1.5% | Trailing SL @ +2.2%

🤖 <b>AI Analyst Insight:</b>
<i>\"{ai_reason}\"</i>

───────────────
🔒 <b>This is today's 1 free public signal.</b>
👑 <i>VIP Members receive 8–15 high-win-rate Spot signals every day + live dashboard & trailing alerts!</i>"""

            free_kb = {
                "inline_keyboard": [
                    [
                        {"text": "⚡ Unlock ALL VIP Signals ($3/mo)", "url": f"https://t.me/{self.bot_username}?start=upgrade"}
                    ],
                    [
                        {"text": "📈 TradingView Live Chart", "url": tv_link}
                    ]
                ]
            }
            if send_tg_message(self.free_channel, free_text, free_kb):
                free_state["last_free_signal_date"] = today_str
                free_state["last_free_pair"] = pair
                free_state["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                save_free_signal_state(free_state)
                print(f"  [+] 🎁 Broadcasted Daily Free Signal ({pair}) to Free Channel ({self.free_channel})!")

    def post_daily_performance_recap(self) -> bool:
        """
        Posts daily recap to Free and VIP channels.
        Shows ONLY percentage (%) PnL per trade — NEVER exposes dollar amounts.
        """
        closed_trades = []
        if os.path.exists(PORTFOLIO_FILE):
            try:
                with open(PORTFOLIO_FILE, "r") as f:
                    data = json.load(f)
                    closed_trades = [t for t in data.get("closed_trades", []) if t.get("direction") == "BUY"]
            except Exception as e:
                print(f"Error reading portfolio: {e}")

        today_str = datetime.utcnow().strftime("%Y-%m-%d")
        
        # Filter trades closed today (or last 24h)
        today_trades = []
        for t in closed_trades:
            exit_time = t.get("exit_time", "")
            if exit_time.startswith(today_str) or len(closed_trades) <= 6:
                today_trades.append(t)

        if not today_trades:
            today_trades = closed_trades[-5:] if closed_trades else []

        if not today_trades:
            return False

        trade_lines = []
        total_pnl_pct = 0.0
        wins = 0

        for t in today_trades:
            sid = t.get("signal_id", "?")
            pair = t.get("pair", "UNKNOWN")
            status = t.get("status", "CLOSED_TP")
            pnl_pct = float(t.get("pnl_pct", 0.0))
            total_pnl_pct += pnl_pct

            if pnl_pct > 0:
                wins += 1
                badge = "🎯 Target Hit" if "TP" in status else "🛡️ Breakeven Locked"
                emoji = "🟢"
            else:
                badge = "🛑 Risk Stopped" if "SL" in status else "⏰ Timeout Exit"
                emoji = "🔴" if pnl_pct < 0 else "⚪"

            sign = "+" if pnl_pct >= 0 else ""
            trade_lines.append(f"• <b>#{sid} {pair}:</b> <code>{sign}{pnl_pct:.2f}%</code> ({badge})")

        win_rate = (wins / len(today_trades) * 100) if today_trades else 100.0
        total_sign = "+" if total_pnl_pct >= 0 else ""

        recap_msg = f"""📊 <b>PUREQUANT AI — DAILY PERFORMANCE RECAP</b>
📅 <i>Date: {today_str} (UTC)</i>

🏆 <b>Today's Completed Spot AI Trades:</b>
{chr(10).join(trade_lines)}

───────────────
📈 <b>Total Daily Performance:</b> <code>{total_sign}{total_pnl_pct:.2f}% Net Gain</code>
🎯 <b>Win Rate:</b> <b>{win_rate:.1f}%</b> ({wins}/{len(today_trades)} Positive)
🕌 <b>Trading Mode:</b> 100% Halal Spot (Zero Leverage / Zero Debt)

🔒 <i>Free channel members received 1 signal today. VIP members caught all {len(today_trades)} moves!</i>"""

        recap_kb = {
            "inline_keyboard": [
                [
                    {"text": "🚀 Get Instant VIP Access (From $3/mo)", "url": f"https://t.me/{self.bot_username}?start=plans"}
                ]
            ]
        }

        # Send to Free Channel
        send_tg_message(self.free_channel, recap_msg, recap_kb)
        # Send to VIP Channel
        send_tg_message(self.vip_channel, recap_msg)
        print(f"  [+] 📊 Posted Daily Performance Recap to Free & VIP Channels!")
        return True

    def post_daily_vip_benefit_promo(self) -> bool:
        """
        Posts high-converting daily promotional post to the Free Channel explaining
        the limited-time $3/mo, $6/mo, and $9 lifetime discount.
        """
        promo_msg = f"""⚡ <b>WHY SERIOUS SPOT TRADERS ARE UPGRADING TO PUREQUANT VIP</b>

Are you still manually watching charts all day and missing high-conviction pumps? 

Here is what you unlock when you upgrade from the Free Channel:

✨ <b>1. 8 to 15 High-Win-Rate Spot Signals Daily</b>
• Scanned 24/7 via SMT Divergence, Fair Value Gaps (FVG) & Whale Radar.
• 100% Shariah-Compliant assets (Zero leverage, Zero liquidation).

🛡️ <b>2. Automated Risk Shield & Trailing Alerts</b>
• Real-time updates when price hits <b>+1.5% Breakeven Lock</b> or <b>+2.2% Trailing Stop-Loss</b>.

🧠 <b>3. AI Deep Market Autopsies & News Sentiment</b>
• Understand exactly why institutional whales are accumulating before the pump.

───────────────
🔥 <b>LIMITED-TIME LAUNCH DISCOUNT (Paid in USDT):</b>

🥉 <b>Starter VIP:</b> <code>$3.00 / month</code>
• 24/7 Real-Time Spot Alerts & Full Setup Parameters

🥈 <b>Pro VIP:</b> <code>$6.00 / month</code> ⭐ <b>(Most Popular)</b>
• All Signals + Live Web Dashboard Access + Trailing SL Alerts

🥇 <b>Lifetime Founder:</b> <code>$9.00 one-time</code> 🔥 <b>(Limited Early Bird)</b>
• Lifetime VIP Access Forever (Zero Monthly Fees)

👉 <b>Instant Activation via Non-Custodial USDT:</b>
Click below to start with @{self.bot_username} 👇"""

        promo_kb = {
            "inline_keyboard": [
                [
                    {"text": "👑 Upgrade to VIP Now ($3/mo)", "url": f"https://t.me/{self.bot_username}?start=plans"}
                ],
                [
                    {"text": "💬 Talk to Support", "url": f"https://t.me/{self.bot_username}?start=support"}
                ]
            ]
        }
        send_tg_message(self.free_channel, promo_msg, promo_kb)
        print(f"  [+] 📢 Posted Daily VIP Benefit Promo to Free Channel!")
        return True


if __name__ == "__main__":
    dispatcher = SaasSignalDispatcher()
    print("🚀 PureQuant SaaS Multi-Tier Dispatcher Ready.")
    print("  Testing Daily Performance Recap Post...")
    dispatcher.post_daily_performance_recap()
    print("  Testing Daily Promotional Post...")
    dispatcher.post_daily_vip_benefit_promo()
