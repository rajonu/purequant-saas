import requests

BOT_TOKEN = "REDACTED_TELEGRAM_BOT_TOKEN"
FREE_CHANNEL_ID = "-1004423283944"

signal_text = """🎁 <b>PUREQUANT AI :: FREE SPOT SIGNAL OF THE DAY (1/1)</b>
🏆 <b>GRADE A+ SETUP · 95.4% LORENTZIAN CONFIDENCE</b>

<b>Asset:</b> #SOL/USDT (Spot Only)
🟢 <b>Entry:</b> $135.20 - $137.50
🎯 <b>TP 1:</b> $144.00 (+5.8%)
🎯 <b>TP 2:</b> $158.00 (+16.2%)
🎯 <b>TP 3:</b> $181.90 (+34.6%)
🛑 <b>Stop-Loss:</b> $131.40
🛡️ <b>Risk Shield:</b> Auto-Breakeven @ +1.5% | Trailing SL @ +2.2%

───────────────
🔒 <i>This is today's 1 free public signal.</i>
👑 <b>VIP Members receive 8–15 high-win-rate Spot signals every day + live dashboard & trailing alerts!</b>"""

reply_markup = {
    "inline_keyboard": [
        [
            {"text": "⚡ Unlock ALL VIP Signals ($3/mo)", "url": "https://t.me/PureQuantAIBot?start=upgrade"}
        ],
        [
            {"text": "📈 TradingView Live Chart", "url": "https://www.tradingview.com/chart/?symbol=BINANCE:SOLUSDT"}
        ]
    ]
}

resp = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
    "chat_id": FREE_CHANNEL_ID,
    "text": signal_text,
    "parse_mode": "HTML",
    "reply_markup": reply_markup
}).json()

print("Telegram Free Channel Delivery Status:", resp)
