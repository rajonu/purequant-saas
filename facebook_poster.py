"""
⚡ PureQuant AI — Automated Facebook Page Publisher & Meta Compliance Engine
=============================================================================
Publishes real-time Take-Profit (TP) hits, Win-Rate statistics, and Daily Performance
Proof Cards directly to your Facebook Page via the Meta Graph API.

🛡️ Meta Policy & Anti-Ban Safeguards:
1. Strict FinTech / Data Science framing (No financial promises or "get rich" claims).
2. Automated Risk & Software Disclaimers on every post.
3. Clean technical terminology (Risk:Reward ratios, FVG mitigations, Lorentzian ML).
4. Direct Conversion Funnel: Facebook Page / Ad -> Free Telegram Radar -> VIP Paywall.
"""

import os
import json
import requests
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] %(message)s")
logger = logging.getLogger("FacebookPoster")


class FacebookPoster:
    """Manages automated publishing to Facebook Pages via Meta Graph API."""

    def __init__(
        self,
        page_id: Optional[str] = None,
        access_token: Optional[str] = None,
        telegram_channel_url: Optional[str] = None,
        landing_page_url: Optional[str] = None,
        graph_version: str = "v19.0"
    ):
        self.page_id = page_id or os.getenv("FB_PAGE_ID", "")
        self.access_token = access_token or os.getenv("FB_PAGE_ACCESS_TOKEN", "")
        self.telegram_url = telegram_channel_url or os.getenv("TELEGRAM_PUBLIC_URL", "https://t.me/PureQuantSignals")
        self.landing_url = landing_page_url or os.getenv("LANDING_PAGE_URL", "https://purequant.ai")
        self.graph_version = graph_version
        self.base_url = f"https://graph.facebook.com/{self.graph_version}"

    def is_configured(self) -> bool:
        """Checks if Facebook credentials are set."""
        return bool(self.page_id and self.access_token)

    def verify_connection(self) -> Dict[str, Any]:
        """Tests the token and checks page permissions."""
        if not self.is_configured():
            return {"status": "ERROR", "message": "FB_PAGE_ID or FB_PAGE_ACCESS_TOKEN missing."}
        
        try:
            url = f"{self.base_url}/{self.page_id}?fields=name,category,is_published&access_token={self.access_token}"
            res = requests.get(url, timeout=10)
            data = res.json()
            if res.status_code == 200:
                logger.info(f"✅ Facebook Page Connected: {data.get('name')} (Category: {data.get('category')})")
                return {"status": "SUCCESS", "page": data}
            else:
                logger.error(f"❌ Facebook Token Verification Failed: {data}")
                return {"status": "ERROR", "details": data}
        except Exception as e:
            logger.error(f"Exception verifying Facebook connection: {e}")
            return {"status": "ERROR", "error": str(e)}

    def build_compliant_tp_caption(
        self,
        pair: str,
        gain_pct: str,
        entry_price: str,
        exit_price: str,
        target_name: str = "TP Target Resolved",
        strategy: str = "Lorentzian ML + Bullish FVG Mitigation",
        risk_reward: str = "1 : 3.2",
        timeframe: str = "4-Hour / 1-Hour Spot"
    ) -> str:
        """
        Formats Take-Profit resolution copy that strictly adheres to Meta Financial Policies.
        Positions the post as a quantitative data model validation rather than financial advice.
        """
        caption = f"""🎯 Model Resolution: {pair} Spot Target Completed ({gain_pct})

Our quantitative telemetry engine detected and resolved a high-volume spot expansion:

📊 Algorithmic Setup Telemetry:
• Asset: {pair} (100% Spot Asset)
• Model Confluence: {strategy}
• Quantitative Entry: {entry_price}
• Target Realized: {exit_price} ({target_name})
• Risk-to-Reward Ratio: {risk_reward}
• Timeframe: {timeframe}

Mathematical discipline and pre-calculated capital defense are at the core of institutional quantitative execution.

📡 Track live quantitative market telemetry & orderflow scans in our free Telegram community:
👉 {self.telegram_url}

🌐 Explore our algorithmic screening platform:
👉 {self.landing_url}

---
⚠️ Software Disclaimer: PureQuant AI is an algorithmic analytics and market telemetry research platform. We do not provide financial, investment, or trading advice. Digital asset markets carry inherent volatility. Always practice strict risk management.

#FinTech #QuantTrading #AlgorithmicTrading #MachineLearning #CryptoAnalytics #DataScience #PureQuantAI"""
        return caption

    def build_compliant_winrate_recap_caption(
        self,
        date_str: str,
        win_rate: str,
        total_setups: int,
        winning_setups: int,
        net_model_expansion: str,
        highlight_pairs: str = "BTC, SOL, ETH, AVAX"
    ) -> str:
        """
        Formats a daily or weekly performance audit recap adhering to Meta policies.
        """
        caption = f"""📈 Quantitative Daily Performance Audit | {date_str}

A summary of today's quantitative machine-learning model resolutions across digital asset spot markets:

📊 Key Telemetry Metrics:
• Validated Model Setups: {total_setups}
• Target Resolutions Achieved: {winning_setups} / {total_setups}
• Model Hit Rate: {win_rate}
• Cumulative Net Volatility Captured: {net_model_expansion}
• Active Screened Assets: {highlight_pairs}

Automated algorithms eliminate emotional bias by focusing solely on liquidity sweeps, Fair Value Gaps (FVG), and order flow delta.

💬 Join 2,500+ quantitative traders in our live Telegram channel:
👉 {self.telegram_url}

🌐 Get full real-time access to the institutional screener:
👉 {self.landing_url}

---
⚠️ Performance Disclaimer: Past algorithmic model resolution metrics are compiled for research and educational purposes and do not guarantee future market outcomes. PureQuant AI is a software analytics provider, not a financial advisor.

#QuantitativeFinance #FinTech #CryptoScreener #MachineLearning #SmartMoneyConcepts #TradingTech #PureQuantAI"""
        return caption

    def publish_photo_post(
        self,
        image_path: str,
        caption: str
    ) -> Dict[str, Any]:
        """
        Uploads a generated photo (e.g. 1080x1080 Trade Proof Card) and publishes the post.
        """
        if not self.is_configured():
            logger.warning("[!] Facebook credentials not configured. Skipping Facebook publish.")
            return {"status": "SKIPPED", "message": "Credentials missing"}

        if not os.path.exists(image_path):
            logger.error(f"[!] Image file not found: {image_path}")
            return {"status": "ERROR", "message": f"File not found: {image_path}"}

        url = f"{self.base_url}/{self.page_id}/photos"

        try:
            with open(image_path, "rb") as img_file:
                payload = {
                    "caption": caption,
                    "access_token": self.access_token,
                    "published": "true"
                }
                files = {
                    "source": img_file
                }
                
                logger.info(f"📤 Uploading post to Facebook Page ID {self.page_id}...")
                response = requests.post(url, data=payload, files=files, timeout=30)
                result = response.json()

                if response.status_code == 200:
                    post_id = result.get("post_id") or result.get("id")
                    logger.info(f"✅ Facebook Post Successfully Published! Post ID: {post_id}")
                    return {
                        "status": "SUCCESS",
                        "post_id": post_id,
                        "fb_url": f"https://www.facebook.com/{post_id}"
                    }
                else:
                    logger.error(f"❌ Facebook Graph API Error: {result}")
                    return {"status": "ERROR", "details": result}

        except Exception as e:
            logger.error(f"❌ Exception while posting to Facebook: {e}")
            return {"status": "ERROR", "error": str(e)}


# Standalone Helper Functions for Easy Integration into Signal Engine

def post_tp_to_facebook(
    pair: str,
    gain_pct: str,
    entry_price: str,
    exit_price: str,
    image_path: str,
    target_name: str = "TP Target Resolved",
    strategy: str = "Lorentzian ML + Bullish FVG",
    risk_reward: str = "1 : 3.0"
) -> Dict[str, Any]:
    """One-line helper function to publish a Take Profit resolution to Facebook."""
    poster = FacebookPoster()
    caption = poster.build_compliant_tp_caption(
        pair=pair,
        gain_pct=gain_pct,
        entry_price=entry_price,
        exit_price=exit_price,
        target_name=target_name,
        strategy=strategy,
        risk_reward=risk_reward
    )
    return poster.publish_photo_post(image_path=image_path, caption=caption)


def post_recap_to_facebook(
    date_str: str,
    win_rate: str,
    total_setups: int,
    winning_setups: int,
    net_pnl: str,
    image_path: str
) -> Dict[str, Any]:
    """One-line helper function to publish daily performance audit to Facebook."""
    poster = FacebookPoster()
    caption = poster.build_compliant_winrate_recap_caption(
        date_str=date_str,
        win_rate=win_rate,
        total_setups=total_setups,
        winning_setups=winning_setups,
        net_model_expansion=net_pnl
    )
    return poster.publish_photo_post(image_path=image_path, caption=caption)


if __name__ == "__main__":
    import sys
    print("\n--- ⚡ PureQuant AI Facebook Auto-Poster Test Mode ---")
    poster = FacebookPoster()
    
    if not poster.is_configured():
        print("\n[!] Setup Instructions:")
        print("Set FB_PAGE_ID and FB_PAGE_ACCESS_TOKEN in your environment or .env file.")
        print("Example:")
        print("  export FB_PAGE_ID='123456789012345'")
        print("  export FB_PAGE_ACCESS_TOKEN='EAA...'")
        print("\nSample Compliant Post Preview:")
        print("="*60)
        sample_caption = poster.build_compliant_tp_caption(
            pair="SOL/USDT",
            gain_pct="+34.60%",
            entry_price="$135.20",
            exit_price="$181.90",
            target_name="TP3 (Macro Expansion)",
            strategy="4H Bullish FVG + Lorentzian ML",
            risk_reward="1 : 3.8"
        )
        print(sample_caption)
        print("="*60)
    else:
        status = poster.verify_connection()
        print(json.dumps(status, indent=2))
