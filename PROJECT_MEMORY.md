# 🧠 PureQuant AI — Project Memory & Technical Context

> **Persistent Context for AI Agents & Developers**  
> Read this document before making architectural or design modifications to ensure brand consistency and code integrity.

---

## 🏷️ Brand Identity & Core Principles

* **Product Name**: PureQuant AI
* **Positioning**: Institutional-grade quantitative crypto spot intelligence combining machine learning and Smart Money Concepts (SMC).
* **Key Differentiators**:
  1. **100% Spot Only**: Zero leverage, zero liquidation risk, 100% Shariah/Halal asset ownership.
  2. **Lorentzian Distance ML**: Multi-dimensional k-NN pattern classification predicting directional expansions.
  3. **Fair Value Gap (FVG) Engine**: Precision entry at unmitigated institutional order blocks.
  4. **SMT Divergence Radar**: Correlation cracks across BTC/ETH/SOL vs. DXY.
  5. **Dynamic Capital Defense**: Automated +1.5% Breakeven locks and +2.2% Trailing Stop-Loss alerts.
  6. **AI Post-Mortem Autopsies**: Forensic trade diagnostics.

---

## 💰 Active Pricing Strategy: 3 — 6 — 9 Model

| Tier Key | Public Name | Price | Duration | Target Audience |
| :--- | :--- | :--- | :--- | :--- |
| `starter` | **Starter Spot** | **\$3.00** / mo | 30 Days | Beginners, basic 24/7 alerts |
| `pro` | **Pro VIP AI** *(Most Popular)* | **\$6.00** / mo | 30 Days | Active spot traders, full ML suite |
| `lifetime_vip` | **Lifetime VIP Pass** *(Best Value)* | **\$9.00** one-time | 3650 Days (10y) | Long-term VIPs, zero recurring fees |

*Urgency / Anchor Framing*: Strikethrough pricing (~~\$9~~, ~~\$19~~, ~~\$99~~) with grandfathered renewal rate guarantees.

---

## 🎨 Design System Tokens

* **Background**: `#070a0f`
* **Card Surface**: `rgba(13, 18, 27, 0.75)` with `backdrop-filter: blur(18px)`
* **Borders**: `rgba(255, 255, 255, 0.08)` (Default) / `rgba(0, 242, 254, 0.35)` (Glow / Hover)
* **Primary Accent**: Electric Neon Cyan (`#00f2fe` $\rightarrow$ `#4facfe`)
* **Success / Profit**: Matrix Emerald (`#00f5a0`)
* **Warning / Gold**: Amber Gold (`#ffd166`)
* **Stop-Loss / Error**: Crimson Red (`#ff5376`)
* **Typography**:
  - Headings: `Space Grotesk`, sans-serif (`letter-spacing: -0.025em`)
  - Body: `Plus Jakarta Sans`, sans-serif
  - Numbers / Code / Terminal: `JetBrains Mono`, monospace

---

## 🤖 Telegram Bot & Paywall Architecture

* **Entry Point**: `subscription_bot.py`
* **Database**: `data/subscribers.json` (Atomic JSON store)
* **Invite Generator**: Telegram Bot API `createChatInviteLink` with `member_limit=1` and `expire_date=now + 86400s`.
* **Access Revocation**: `banChatMember` followed by `unbanChatMember`.
* **Signal Alert Template**: `format_spot_signal_message(setup)` in HTML format with confluences, FVG levels, targets, and risk defense rules.
* **Supported Chains**: USDT / USDC on TRC-20, BEP-20 (BSC), Polygon, Solana, and TON.

---

## 📂 Key File Map

* [`landing_page/index.html`](file:///Users/rajrio/Desktop/dev/purequant-saas/landing_page/index.html): Complete standalone landing page with live signal radar, proof screenshots, and 3-6-9 pricing.
* [`landing_page/assets/`](file:///Users/rajrio/Desktop/dev/purequant-saas/landing_page/assets/): Verified exchange proof images (`proof_btc.jpg`, `proof_sol.jpg`, `proof_eth.jpg`).
* [`subscription_bot.py`](file:///Users/rajrio/Desktop/dev/purequant-saas/subscription_bot.py): Paywall bot backend and signal formatter.
* [`BUSINESS_IMPLEMENTATION_PLAN.md`](file:///Users/rajrio/Desktop/dev/purequant-saas/BUSINESS_IMPLEMENTATION_PLAN.md): Marketing and commercial blueprint.
* [`ARCHITECTURE.md`](file:///Users/rajrio/Desktop/dev/purequant-saas/ARCHITECTURE.md): Technical system architecture and diagrams.
* [`DEPLOYMENT_GUIDE.md`](file:///Users/rajrio/Desktop/dev/purequant-saas/DEPLOYMENT_GUIDE.md): Production deployment for Cloudflare Pages and VPS Systemd.
