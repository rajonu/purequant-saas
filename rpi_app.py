#!/usr/bin/env python3
"""
⚡ PureQuant AI — Raspberry Pi Facebook Auto-Poster & Webhook App
================================================================
Lightweight microservice designed to run 24/7 on a Raspberry Pi.

Capabilities:
1. 🌐 Web Control Panel UI (http://<your-pi-ip>:5050) for monitoring & manual tests.
2. 🪝 Webhook Receiver (/webhook/tp): Accepts real-time TP signals from your Trading Board.
3. 🔄 Auto-Polling Engine: Periodically queries your Trading Board API for new closed trades/TPs.
4. 🎨 Trade Proof Card Generator: Generates 1080x1080 branded proof cards on the Pi.
5. 🛡️ Meta Anti-Ban Caption Builder: Formats compliance-safe quantitative posts.
6. 📤 Facebook Graph API Dispatcher: Automatically publishes photo + caption.
7. 📜 Deduplication & History Ledger: Prevents duplicate posts for the same trade ID.
"""

import os
import sys
import json
import time
import threading
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import requests
from flask import Flask, request, jsonify, render_template_string

# Configure Logging
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("PureQuantRPi")

app = Flask(__name__)

# Base Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(DATA_DIR, "fb_posted_history.json")

# Environment & Default Config
CONFIG = {
    "FB_PAGE_ID": os.getenv("FB_PAGE_ID", ""),
    "FB_PAGE_ACCESS_TOKEN": os.getenv("FB_PAGE_ACCESS_TOKEN", ""),
    "TRADING_BOARD_API_URL": os.getenv("TRADING_BOARD_API_URL", ""),
    "TRADING_BOARD_API_KEY": os.getenv("TRADING_BOARD_API_KEY", ""),
    "TELEGRAM_PUBLIC_URL": os.getenv("TELEGRAM_PUBLIC_URL", "https://t.me/PureQuantSignals"),
    "LANDING_PAGE_URL": os.getenv("LANDING_PAGE_URL", "https://purequant.ai"),
    "POLL_INTERVAL_SECONDS": int(os.getenv("POLL_INTERVAL_SECONDS", "60")),
    "AUTO_POLL_ENABLED": os.getenv("AUTO_POLL_ENABLED", "true").lower() == "true",
    "PORT": int(os.getenv("PORT", "5050"))
}


def load_history() -> list:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(entry: dict):
    history = load_history()
    history.insert(0, entry)
    # Keep last 100 entries
    history = history[:100]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def is_trade_already_posted(trade_id: str) -> bool:
    if not trade_id:
        return False
    history = load_history()
    return any(str(h.get("trade_id")) == str(trade_id) for h in history)


# ==========================================
# 🎨 Lightweight Trade Proof Card Generator
# ==========================================
def generate_pi_proof_card(
    pair: str = "SOL/USDT",
    gain_pct: str = "+34.60%",
    entry_price: str = "$135.20",
    exit_price: str = "$181.90",
    target_name: str = "TP Target Resolved",
    strategy: str = "4H Bullish FVG + Lorentzian ML",
    risk_reward: str = "1 : 3.8",
    output_path: str = "/tmp/rpi_proof_card.png"
) -> str:
    from PIL import Image, ImageDraw, ImageFont
    
    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), color=(7, 10, 15))
    draw = ImageDraw.Draw(img)

    # Vertical gradient
    for i in range(height):
        r = int(7 + (13 - 7) * (i / height))
        g = int(10 + (20 - 10) * (i / height))
        b = int(15 + (30 - 15) * (i / height))
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Outer Neon Cyan / Matrix Emerald Border
    draw.rounded_rectangle([20, 20, width - 20, height - 20], radius=24, outline=(0, 242, 254), width=3)
    draw.rounded_rectangle([24, 24, width - 24, height - 24], radius=22, outline=(0, 245, 160), width=1)

    # System fonts fallback
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc"
    ]
    font_large = None
    for p in font_paths:
        if os.path.exists(p):
            try:
                font_large = ImageFont.truetype(p, 54)
                font_pair = ImageFont.truetype(p, 64)
                font_pnl = ImageFont.truetype(p, 96)
                font_body = ImageFont.truetype(p, 30)
                font_badge = ImageFont.truetype(p, 24)
                break
            except Exception:
                continue

    if not font_large:
        font_large = ImageFont.load_default()
        font_pair = font_large
        font_pnl = font_pnl_font = font_large
        font_body = font_large
        font_badge = font_large

    # Header Bar
    draw.rounded_rectangle([50, 50, width - 50, 130], radius=16, fill=(13, 22, 38), outline=(0, 242, 254), width=1)
    draw.text((70, 68), "⚡ PUREQUANT AI", fill=(0, 242, 254), font=font_large)
    
    # VIP Badge
    draw.rounded_rectangle([width - 320, 68, width - 70, 114], radius=10, fill=(255, 184, 0))
    draw.text((width - 300, 78), "👑 VIP INSTITUTIONAL", fill=(7, 11, 18), font=font_badge)

    # Pair Title
    draw.text((60, 165), f"🎯 {pair}", fill=(255, 255, 255), font=font_pair)

    # PnL Center Hero Card
    draw.rounded_rectangle([50, 260, width - 50, 470], radius=20, fill=(11, 25, 34), outline=(0, 245, 160), width=2)
    draw.text((80, 285), "SPOT MODEL RESOLUTION", fill=(0, 245, 160), font=font_badge)
    
    is_positive = not gain_pct.startswith("-")
    pnl_color = (0, 245, 160) if is_positive else (255, 83, 118)
    draw.text((80, 330), gain_pct, fill=pnl_color, font=font_pnl)

    # Strategy Badge
    draw.rounded_rectangle([50, 500, width - 50, 570], radius=14, fill=(16, 26, 44), outline=(79, 172, 254), width=1)
    draw.text((70, 520), f"⚡ Confluence: {strategy}", fill=(241, 245, 249), font=font_body)

    # Telemetry Grid Box
    draw.rounded_rectangle([50, 600, width - 50, 930], radius=16, fill=(13, 19, 30), outline=(255, 255, 255, 40), width=1)
    
    metrics = [
        ("QUANTITATIVE ENTRY", entry_price),
        ("TARGET ACHIEVED", exit_price),
        ("TARGET STAGE", target_name),
        ("RISK : REWARD", risk_reward),
        ("CAPITAL DEFENSE", "Trailing SL + Breakeven"),
        ("TRADING MODE", "100% Halal Spot Asset")
    ]

    for idx, (label, val) in enumerate(metrics):
        col = idx % 2
        row = idx // 2
        x = 80 if col == 0 else 560
        y = 630 + (row * 95)
        draw.text((x, y), label, fill=(148, 163, 184), font=font_badge)
        draw.text((x, y + 32), val, fill=(255, 255, 255), font=font_body)

    # Footer Disclaimer
    draw.text((60, 965), "PureQuant AI Telemetry • Non-Custodial Spot Intelligence • Not Financial Advice", fill=(100, 116, 139), font=font_badge)
    draw.text((60, 1005), "t.me/PureQuantSignals  •  https://purequant.ai", fill=(0, 242, 254), font=font_badge)

    img.save(output_path, "PNG", quality=95)
    return output_path


# ==========================================
# 🛡️ Meta Compliant Facebook Publisher
# ==========================================
def publish_to_facebook(
    image_path: str,
    pair: str,
    gain_pct: str,
    entry_price: str,
    exit_price: str,
    target_name: str = "TP Target Resolved",
    strategy: str = "4H Bullish FVG + Lorentzian ML",
    risk_reward: str = "1 : 3.2"
) -> Dict[str, Any]:
    page_id = CONFIG["FB_PAGE_ID"]
    token = CONFIG["FB_PAGE_ACCESS_TOKEN"]
    tg_url = CONFIG["TELEGRAM_PUBLIC_URL"]
    landing_url = CONFIG["LANDING_PAGE_URL"]

    if not page_id or not token:
        return {"status": "ERROR", "message": "FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN not configured."}

    caption = f"""🎯 Model Resolution: {pair} Spot Target Completed ({gain_pct})

Our quantitative telemetry engine detected and resolved a high-volume spot expansion:

📊 Algorithmic Setup Telemetry:
• Asset: {pair} (100% Spot Asset)
• Model Confluence: {strategy}
• Quantitative Entry: {entry_price}
• Target Realized: {exit_price} ({target_name})
• Risk-to-Reward Ratio: {risk_reward}
• Capital Defense: Automated Trailing SL & Breakeven Lock

Mathematical discipline and pre-calculated capital defense are at the core of institutional quantitative execution.

📡 Track live quantitative market telemetry & orderflow scans in our free Telegram community:
👉 {tg_url}

🌐 Explore our algorithmic screening platform:
👉 {landing_url}

---
⚠️ Software Disclaimer: PureQuant AI is an algorithmic analytics and market telemetry research platform. We do not provide financial, investment, or trading advice. Digital asset markets carry inherent volatility. Always practice strict risk management.

#FinTech #QuantTrading #AlgorithmicTrading #MachineLearning #CryptoAnalytics #DataScience #PureQuantAI"""

    url = f"https://graph.facebook.com/v19.0/{page_id}/photos"

    try:
        with open(image_path, "rb") as img_file:
            payload = {
                "caption": caption,
                "access_token": token,
                "published": "true"
            }
            files = {"source": img_file}
            res = requests.post(url, data=payload, files=files, timeout=30)
            data = res.json()

            if res.status_code == 200:
                post_id = data.get("post_id") or data.get("id")
                fb_url = f"https://www.facebook.com/{post_id}"
                logger.info(f"✅ Published to Facebook: {fb_url}")
                return {"status": "SUCCESS", "post_id": post_id, "fb_url": fb_url}
            else:
                logger.error(f"❌ Meta Graph API Error: {data}")
                return {"status": "ERROR", "details": data}
    except Exception as e:
        logger.error(f"❌ Facebook Publish Exception: {e}")
        return {"status": "ERROR", "error": str(e)}


# ==========================================
# 🔄 Background Trading Board Poller
# ==========================================
def poll_trading_board_loop():
    logger.info("🚀 Background Trading Board Poller Started...")
    while True:
        try:
            if CONFIG["AUTO_POLL_ENABLED"] and CONFIG["TRADING_BOARD_API_URL"]:
                headers = {}
                if CONFIG["TRADING_BOARD_API_KEY"]:
                    headers["Authorization"] = f"Bearer {CONFIG['TRADING_BOARD_API_KEY']}"
                    headers["X-API-Key"] = CONFIG["TRADING_BOARD_API_KEY"]

                res = requests.get(CONFIG["TRADING_BOARD_API_URL"], headers=headers, timeout=15)
                if res.status_code == 200:
                    trades_data = res.json()
                    # Expecting a list or dict with trades
                    trades = trades_data if isinstance(trades_data, list) else trades_data.get("trades", [])

                    for trade in trades:
                        trade_id = str(trade.get("id") or trade.get("signal_id") or trade.get("trade_id", ""))
                        status = trade.get("status", "").upper()
                        is_tp = "TP" in status or trade.get("is_tp", False) or float(str(trade.get("pnl_pct", 0)).replace("%", "").replace("+", "")) > 0

                        if trade_id and not is_trade_already_posted(trade_id) and is_tp:
                            pair = trade.get("pair") or trade.get("symbol", "BTC/USDT")
                            gain_pct = trade.get("gain_pct") or trade.get("pnl_pct", "+3.20%")
                            if not str(gain_pct).startswith("+") and not str(gain_pct).startswith("-"):
                                gain_pct = f"+{gain_pct}%"

                            entry_price = str(trade.get("entry_price", "$0.00"))
                            exit_price = str(trade.get("exit_price") or trade.get("close_price", "$0.00"))
                            target_name = trade.get("target_name") or trade.get("target_hit", "Target Hit")
                            strategy = trade.get("strategy", "Lorentzian ML + Bullish FVG")
                            risk_reward = trade.get("risk_reward", "1 : 3.0")

                            logger.info(f"🎯 New TP Detected from Trading Board: {pair} ({gain_pct}) [Trade ID: {trade_id}]")
                            card_path = f"/tmp/tp_card_{trade_id}.png"
                            generate_pi_proof_card(
                                pair=pair,
                                gain_pct=gain_pct,
                                entry_price=entry_price,
                                exit_price=exit_price,
                                target_name=target_name,
                                strategy=strategy,
                                risk_reward=risk_reward,
                                output_path=card_path
                            )

                            pub_res = publish_to_facebook(
                                image_path=card_path,
                                pair=pair,
                                gain_pct=gain_pct,
                                entry_price=entry_price,
                                exit_price=exit_price,
                                target_name=target_name,
                                strategy=strategy,
                                risk_reward=risk_reward
                            )

                            save_history({
                                "trade_id": trade_id,
                                "pair": pair,
                                "gain_pct": gain_pct,
                                "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                                "status": pub_res.get("status"),
                                "fb_url": pub_res.get("fb_url", ""),
                                "source": "AUTO_POLL"
                            })
        except Exception as e:
            logger.error(f"Error in polling loop: {e}")

        time.sleep(CONFIG["POLL_INTERVAL_SECONDS"])


# ==========================================
# 🌐 Flask Web UI & API Endpoints
# ==========================================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PureQuant AI — Raspberry Pi Facebook Engine</title>
<style>
  :root {
    --bg: #070a0f;
    --card: rgba(13, 18, 27, 0.85);
    --border: rgba(0, 242, 254, 0.2);
    --cyan: #00f2fe;
    --emerald: #00f5a0;
    --gold: #ffd166;
    --red: #ff5376;
    --text: #f1f5f9;
    --muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; padding: 24px; }
  .container { max-width: 900px; margin: 0 auto; }
  .header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 24px; border-bottom: 1px solid var(--border); padding-bottom: 16px; }
  .header h1 { font-size: 24px; color: var(--cyan); display: flex; align-items: center; gap: 8px; }
  .badge-pi { background: rgba(0, 245, 160, 0.15); color: var(--emerald); border: 1px solid var(--emerald); padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
  @media (max-width: 700px) { .grid { grid-template-columns: 1fr; } }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 20px; }
  .card h2 { font-size: 16px; margin-bottom: 12px; color: var(--cyan); text-transform: uppercase; letter-spacing: 0.5px; }
  .status-item { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05); font-size: 14px; }
  .val-ok { color: var(--emerald); font-weight: bold; }
  .val-warn { color: var(--gold); }
  .val-err { color: var(--red); }
  .btn { background: linear-gradient(135deg, var(--cyan), #4facfe); color: #000; border: none; padding: 12px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; width: 100%; transition: all 0.2s; }
  .btn:hover { opacity: 0.9; transform: translateY(-1px); }
  .input-group { margin-bottom: 12px; }
  .input-group label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
  .input-group input { width: 100%; background: #0b111a; border: 1px solid var(--border); color: #fff; padding: 8px 12px; border-radius: 6px; }
  .code-box { background: #05080c; border: 1px solid rgba(0, 242, 254, 0.2); padding: 12px; border-radius: 6px; font-family: monospace; font-size: 12px; color: var(--emerald); word-break: break-all; margin-top: 8px; }
  table { width: 100%; border-collapse: collapse; margin-top: 12px; font-size: 13px; }
  th, td { padding: 10px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.08); }
  th { color: var(--muted); font-size: 11px; text-transform: uppercase; }
  a { color: var(--cyan); text-decoration: none; }
  a:hover { text-decoration: underline; }
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>⚡ PureQuant AI <span style="font-size: 14px; color: var(--muted);">| Raspberry Pi Gateway</span></h1>
    <span class="badge-pi">🟢 RPi Engine Online</span>
  </div>

  <div class="grid">
    <!-- Status Card -->
    <div class="card">
      <h2>📡 Integrations Status</h2>
      <div class="status-item">
        <span>Facebook Page ID</span>
        <span class="{{ 'val-ok' if config.FB_PAGE_ID else 'val-err' }}">{{ config.FB_PAGE_ID or 'Not Set' }}</span>
      </div>
      <div class="status-item">
        <span>Facebook Page Token</span>
        <span class="{{ 'val-ok' if config.FB_PAGE_ACCESS_TOKEN else 'val-err' }}">{{ 'Configured' if config.FB_PAGE_ACCESS_TOKEN else 'Missing' }}</span>
      </div>
      <div class="status-item">
        <span>Trading Board API</span>
        <span class="{{ 'val-ok' if config.TRADING_BOARD_API_URL else 'val-warn' }}">{{ 'Connected' if config.TRADING_BOARD_API_URL else 'Webhook Only' }}</span>
      </div>
      <div class="status-item">
        <span>Auto-Poll Status</span>
        <span class="{{ 'val-ok' if config.AUTO_POLL_ENABLED else 'val-warn' }}">{{ 'Every ' ~ config.POLL_INTERVAL_SECONDS ~ 's' if config.AUTO_POLL_ENABLED else 'Disabled' }}</span>
      </div>
      
      <h2 style="margin-top: 20px;">🪝 Webhook Endpoint</h2>
      <p style="font-size: 12px; color: var(--muted);">Send POST requests from your Trading Board to this Pi URL:</p>
      <div class="code-box">POST http://&lt;your-pi-ip&gt;:{{ config.PORT }}/webhook/tp</div>
    </div>

    <!-- Quick Manual Test Card -->
    <div class="card">
      <h2>🚀 Send 1-Click Test Post</h2>
      <form action="/api/test-post" method="POST">
        <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 0;">
          <div class="input-group">
            <label>Trading Pair</label>
            <input type="text" name="pair" value="SOL/USDT">
          </div>
          <div class="input-group">
            <label>Target Gain %</label>
            <input type="text" name="gain_pct" value="+34.60%">
          </div>
        </div>
        <div class="grid" style="grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 0;">
          <div class="input-group">
            <label>Entry Price</label>
            <input type="text" name="entry_price" value="$135.20">
          </div>
          <div class="input-group">
            <label>Exit Price</label>
            <input type="text" name="exit_price" value="$181.90">
          </div>
        </div>
        <div class="input-group">
          <label>Target Name</label>
          <input type="text" name="target_name" value="TP3 (Macro Expansion)">
        </div>
        <button type="submit" class="btn">🚀 Render Proof Card & Post to Facebook</button>
      </form>
    </div>
  </div>

  <!-- Recent History Card -->
  <div class="card">
    <h2>📜 Recent Facebook Posts Ledger</h2>
    {% if history %}
    <table>
      <thead>
        <tr>
          <th>Time (UTC)</th>
          <th>Trade / Pair</th>
          <th>Gain</th>
          <th>Source</th>
          <th>Status</th>
          <th>Facebook Link</th>
        </tr>
      </thead>
      <tbody>
        {% for item in history %}
        <tr>
          <td>{{ item.timestamp }}</td>
          <td><b>{{ item.pair }}</b></td>
          <td style="color: var(--emerald); font-weight: bold;">{{ item.gain_pct }}</td>
          <td>{{ item.source }}</td>
          <td><span class="{{ 'val-ok' if item.status == 'SUCCESS' else 'val-err' }}">{{ item.status }}</span></td>
          <td>
            {% if item.fb_url %}
            <a href="{{ item.fb_url }}" target="_blank">View Post ↗</a>
            {% else %}
            —
            {% endif %}
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <p style="color: var(--muted); font-size: 14px; padding: 12px 0;">No posts published yet. Use the 1-Click test button above or trigger your webhook!</p>
    {% endif %}
  </div>
</div>
</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    history = load_history()
    return render_template_string(HTML_TEMPLATE, config=CONFIG, history=history)


@app.route("/api/status", methods=["GET"])
def api_status():
    return jsonify({
        "status": "ONLINE",
        "device": "Raspberry Pi",
        "fb_configured": bool(CONFIG["FB_PAGE_ID"] and CONFIG["FB_PAGE_ACCESS_TOKEN"]),
        "trading_board_connected": bool(CONFIG["TRADING_BOARD_API_URL"]),
        "total_posts_logged": len(load_history())
    })


@app.route("/webhook/tp", methods=["POST"])
def webhook_tp():
    """
    Webhook endpoint to receive TP events from Trading Board.
    Payload format:
    {
      "trade_id": "SOL_12345",
      "pair": "SOL/USDT",
      "gain_pct": "+34.60%",
      "entry_price": "$135.20",
      "exit_price": "$181.90",
      "target_name": "TP3 (Macro Expansion)",
      "strategy": "4H Bullish FVG + Lorentzian ML",
      "risk_reward": "1 : 3.8"
    }
    """
    try:
        data = request.get_json(force=True, silent=True) or request.form.to_dict()
        if not data:
            return jsonify({"status": "ERROR", "message": "Invalid JSON payload"}), 400

        trade_id = str(data.get("trade_id") or data.get("id") or f"trade_{int(time.time())}")
        if is_trade_already_posted(trade_id):
            logger.info(f"Duplicate trade received: {trade_id}. Skipping.")
            return jsonify({"status": "SKIPPED", "message": "Trade already published."})

        pair = data.get("pair") or data.get("symbol", "BTC/USDT")
        gain_pct = data.get("gain_pct") or data.get("pnl_pct", "+2.40%")
        entry_price = str(data.get("entry_price", "$0.00"))
        exit_price = str(data.get("exit_price", "$0.00"))
        target_name = data.get("target_name", "Target Resolved")
        strategy = data.get("strategy", "Lorentzian ML + Bullish FVG")
        risk_reward = data.get("risk_reward", "1 : 3.0")

        # 1. Render Card
        card_path = f"/tmp/proof_card_{trade_id}.png"
        generate_pi_proof_card(
            pair=pair,
            gain_pct=gain_pct,
            entry_price=entry_price,
            exit_price=exit_price,
            target_name=target_name,
            strategy=strategy,
            risk_reward=risk_reward,
            output_path=card_path
        )

        # 2. Publish to Facebook
        pub_res = publish_to_facebook(
            image_path=card_path,
            pair=pair,
            gain_pct=gain_pct,
            entry_price=entry_price,
            exit_price=exit_price,
            target_name=target_name,
            strategy=strategy,
            risk_reward=risk_reward
        )

        # 3. Log History
        save_history({
            "trade_id": trade_id,
            "pair": pair,
            "gain_pct": gain_pct,
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
            "status": pub_res.get("status"),
            "fb_url": pub_res.get("fb_url", ""),
            "source": "WEBHOOK"
        })

        return jsonify({"status": "SUCCESS", "facebook": pub_res})
    except Exception as e:
        logger.error(f"Webhook exception: {e}")
        return jsonify({"status": "ERROR", "error": str(e)}), 500


@app.route("/api/test-post", methods=["POST"])
def manual_test_post():
    data = request.form.to_dict() if request.form else (request.get_json(force=True, silent=True) or {})
    
    pair = data.get("pair", "SOL/USDT")
    gain_pct = data.get("gain_pct", "+34.60%")
    entry_price = data.get("entry_price", "$135.20")
    exit_price = data.get("exit_price", "$181.90")
    target_name = data.get("target_name", "TP3 (Macro Expansion)")
    trade_id = f"test_{int(time.time())}"

    card_path = f"/tmp/test_card_{trade_id}.png"
    generate_pi_proof_card(
        pair=pair,
        gain_pct=gain_pct,
        entry_price=entry_price,
        exit_price=exit_price,
        target_name=target_name,
        output_path=card_path
    )

    pub_res = publish_to_facebook(
        image_path=card_path,
        pair=pair,
        gain_pct=gain_pct,
        entry_price=entry_price,
        exit_price=exit_price,
        target_name=target_name
    )

    save_history({
        "trade_id": trade_id,
        "pair": pair,
        "gain_pct": gain_pct,
        "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
        "status": pub_res.get("status"),
        "fb_url": pub_res.get("fb_url", ""),
        "source": "MANUAL_TEST"
    })

    if request.form:
        return f"""
        <html><body style="background:#070a0f;color:#fff;font-family:sans-serif;padding:40px;text-align:center;">
        <h2 style="color:#00f5a0;">✅ Post Dispatched!</h2>
        <p>Status: {pub_res.get('status')}</p>
        <p><a style="color:#00f2fe;" href="{pub_res.get('fb_url', '#')}" target="_blank">View on Facebook</a></p>
        <br><a style="color:#94a3b8;" href="/">← Return to Control Panel</a>
        </body></html>
        """
    return jsonify(pub_res)


if __name__ == "__main__":
    # Start background poller thread
    poller_thread = threading.Thread(target=poll_trading_board_loop, daemon=True)
    poller_thread.start()

    port = CONFIG["PORT"]
    logger.info(f"🌐 Starting Raspberry Pi Web Interface on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=False)
