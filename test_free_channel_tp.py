import requests

BOT_TOKEN = "REDACTED_TELEGRAM_BOT_TOKEN"
FREE_CHANNEL_ID = "-1004423283944"

free_tp_text = """🎯 <b>TAKE-PROFIT TARGET HIT! — #SOLUSDT</b> 🟢

💰 <b>Profit Secured:</b> <b>+5.80% (Spot Gain)</b>
💵 <b>Entry Price:</b> <code>$135.20</code>
🎯 <b>Exit Price:</b> <code>$144.00</code>
🧠 <b>Signal Engine:</b> PureQuant AI + Lorentzian ML (97+ Score)

───────────────
🔒 <i>VIP & Pro Members received this exact buy alert in real-time!</i>
👑 <b>Join VIP or Pro to get all AI intelligent data, 8–15 accurate daily signals & trailing risk shields!</b>"""

free_tp_kb = {
    "inline_keyboard": [
        [
            {"text": "⚡ Unlock VIP Signals ($3/mo)", "url": "https://t.me/PureQuantAIBot?start=upgrade"}
        ],
        [
            {"text": "🌐 View Live Dashboard", "url": "https://dashboard.purequantai.xyz/"}
        ]
    ]
}

resp = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", json={
    "chat_id": FREE_CHANNEL_ID,
    "text": free_tp_text,
    "parse_mode": "HTML",
    "reply_markup": free_tp_kb
}).json()

print("Telegram Free Channel TP Delivery Status:", resp)
