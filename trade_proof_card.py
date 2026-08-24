import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

def generate_trade_proof_card(
    pair: str = "SOL/USDT",
    pnl_percent: str = "+34.60%",
    entry_price: str = "$135.20",
    exit_price: str = "$181.90",
    target_hit: str = "TP3 (Macro Expansion)",
    ml_confidence: str = "95.4%",
    strategy: str = "4H Bullish FVG + Lorentzian ML",
    duration: str = "18h 40m",
    risk_reward: str = "1 : 3.8",
    output_path: str = "/tmp/trade_proof_card.png"
) -> str:
    """Generates a high-converting institutional trade proof card image"""
    width, height = 1080, 1080
    img = Image.new("RGB", (width, height), color=(7, 11, 18))
    draw = ImageDraw.Draw(img)

    # Draw gradient / glowing background rects
    for i in range(height):
        # subtle vertical gradient
        r = int(7 + (13 - 7) * (i / height))
        g = int(11 + (20 - 11) * (i / height))
        b = int(18 + (34 - 18) * (i / height))
        draw.line([(0, i), (width, i)], fill=(r, g, b))

    # Outer decorative glowing border
    draw.rounded_rectangle([20, 20, width - 20, height - 20], radius=24, outline=(0, 242, 254), width=3)
    draw.rounded_rectangle([24, 24, width - 24, height - 24], radius=22, outline=(0, 245, 160), width=1)

    # Try loading default fonts or fallback
    try:
        font_title_large = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 46)
        font_pair = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 64)
        font_pnl = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 96)
        font_body = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 30)
        font_body_bold = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 32)
        font_badge = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 24)
        font_small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 22)
    except Exception:
        font_title_large = ImageFont.load_default()
        font_pair = font_title_large
        font_pnl = font_title_large
        font_body = font_title_large
        font_body_bold = font_title_large
        font_badge = font_title_large
        font_small = font_title_large

    # 1. Header Banner
    draw.rounded_rectangle([50, 50, width - 50, 130], radius=16, fill=(13, 22, 38), outline=(0, 242, 254), width=1)
    draw.text((70, 72), "⚡ PUREQUANT AI", fill=(0, 242, 254), font=font_title_large)
    
    # VIP Tag
    draw.rounded_rectangle([width - 310, 68, width - 70, 112], radius=10, fill=(255, 184, 0), outline=(255, 215, 0))
    draw.text((width - 290, 76), "👑 VIP INSTITUTIONAL", fill=(7, 11, 18), font=font_badge)

    # 2. Pair Title & Direction
    clean_pair = pair.upper().lstrip("#")
    draw.text((60, 165), f"#{clean_pair}", fill=(255, 255, 255), font=font_pair)
    
    # Spot Buy Badge
    draw.rounded_rectangle([width - 260, 175, width - 60, 225], radius=10, fill=(0, 245, 160))
    draw.text((width - 240, 185), "SPOT LONG ✅", fill=(7, 11, 18), font=font_badge)

    # 3. Giant Hero PnL Container
    draw.rounded_rectangle([50, 260, width - 50, 480], radius=24, fill=(11, 28, 30), outline=(0, 245, 160), width=3)
    draw.text((80, 285), "PROFIT HARVESTED (CLOSED POSITION)", fill=(130, 210, 180), font=font_small)
    draw.text((80, 325), pnl_percent, fill=(0, 245, 160), font=font_pnl)
    draw.text((width - 430, 385), f"🎯 {target_hit}", fill=(0, 242, 254), font=font_body_bold)

    # 4. Strategy & Model Feature Badges
    badges = [
        f"🧠 Lorentzian ML: {ml_confidence}",
        f"⚡ {strategy}",
        "🛡️ 100% Spot (Zero Liquidation)"
    ]
    bx = 50
    by = 510
    for b in badges:
        draw.rounded_rectangle([bx, by, bx + 310, by + 50], radius=10, fill=(18, 28, 48), outline=(60, 90, 140), width=1)
        draw.text((bx + 14, by + 12), b, fill=(200, 220, 255), font=font_badge)
        bx += 330
        if bx + 310 > width:
            bx = 50
            by += 65

    # 5. Trade Statistics Matrix Grid
    grid_top = 650
    draw.rounded_rectangle([50, grid_top, width - 50, grid_top + 260], radius=20, fill=(13, 20, 34), outline=(30, 50, 80), width=1)
    
    stats = [
        ("🟢 Entry Trigger", entry_price),
        ("🎯 Exit / High", exit_price),
        ("⏱️ Trade Duration", duration),
        ("⚖️ Risk-to-Reward", risk_reward),
        ("🔒 Capital Defense", "Automated Breakeven + Trailing Lock"),
        ("📅 Executed On", datetime.now().strftime("%B %d, %Y · UTC"))
    ]

    for idx, (label, val) in enumerate(stats):
        col = idx % 2
        row = idx // 2
        sx = 80 if col == 0 else 560
        sy = grid_top + 25 + (row * 75)
        
        draw.text((sx, sy), label, fill=(140, 160, 190), font=font_small)
        draw.text((sx, sy + 30), val, fill=(255, 255, 255), font=font_body_bold)

    # 6. High-Converting Bottom Brand CTA Bar
    draw.rounded_rectangle([50, 940, width - 50, 1025], radius=16, fill=(0, 242, 254), outline=(0, 245, 160), width=2)
    draw.text((80, 962), "🔥 UNLOCK NEXT INSTITUTIONAL SETUP ➔ @PureQuantAIBot", fill=(7, 11, 18), font=font_body_bold)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "PNG", quality=95)
    return output_path

if __name__ == "__main__":
    out = generate_trade_proof_card()
    print("Sample card rendered successfully at:", out)
