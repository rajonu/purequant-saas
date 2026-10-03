# PureQuant AI SaaS Scanner Security Audit

Date: 2026-10-03 (Asia/Dhaka)

## Scope and method

This audit covers the supplied checkout, its Vercel configuration, static HTML, scanner gate module, Telegram bot health listener, deployment files, environment-variable references, and tracked runtime data. It does not claim that an external production deployment was reachable or that a live endpoint was penetration-tested.

## Verified architecture

- The public scanner is a static HTML page. Its signal table is a client-side mock dataset with a local price-tick animation; this checkout contains no scanner API implementation or browser source-map files.
- `vercel.json` serves the public landing/scanner pages and rewrites several health/status paths to static HTML.
- `subscription_bot.py` runs the Telegram polling/paywall process and exposes a small HTTP health listener on `0.0.0.0:$PORT`.
- `scanner_gate.py` provides an optional stateless HMAC token gate, but this checkout contains no server route that consumes the token. `SCANNER_GATE_ENABLED` therefore does not protect the static Vercel scanner by itself.

## Findings

### High — credentials and operational details were present in public static content

The tracked status dashboard contained a Telegram Bot API URL with a bot-token-shaped credential. The credential is removed from the dashboard in this branch. Any credential that has appeared in a public repository, deployed asset, browser cache, or build artifact must be rotated out-of-band; this report intentionally does not reproduce it.

The same dashboard contains a client-side founder PIN and stores the value in browser storage. Because the HTML and JavaScript are delivered to the browser, this is not server-side authentication and can be bypassed by anyone who can retrieve or modify the page. It remains a documented deployment limitation rather than being represented as a real security boundary.

### High — static deployment could include server/runtime material

The repository contains server-side Python modules, deployment documentation, local JSON ledgers, and environment templates alongside public assets. Git ignore rules alone do not guarantee that tracked files are excluded from a Vercel upload. `.vercelignore` now excludes Python/runtime code, environment files, source maps, local data, and internal documentation from the static deployment bundle. The Docker deployment path is unchanged.

### Medium — health/status pages disclose architecture and endpoints

The health/status pages enumerate subsystem names, vendor endpoints, route names, channel identifiers, and operational claims. They are still directly reachable if deployed because removing them would change the existing operator-facing behavior. They now carry `noindex` metadata, `X-Robots-Tag: noindex`, `no-store`, and robots exclusions to reduce indexing and caching. These controls are discoverability/caching controls, not access control.

### Medium — public client code is inherently copyable

The scanner's HTML, CSS, JavaScript, mock data, labels, and displayed strategy terminology are sent to every browser. Disabling right-click or developer-tool shortcuts does not prevent extraction and is not a security control. A public web application cannot keep client-delivered logic secret. Sensitive strategy computation must remain server-side, with authenticated/authorized API responses and server-side rate limiting if confidentiality is required.

### Low — health listener fingerprinting and cache behavior

The Telegram bot health listener returned a fixed status body but inherited a Python server identity and did not set explicit cache/security headers. It now supports `GET` and `HEAD`, sends a fixed content length, `no-store`, `nosniff`, `no-referrer`, and a no-script CSP, and uses a neutral server banner. Route-level authentication was not added because the existing platform health-check contract is unspecified and changing it could stop the bot service from being considered healthy.

## Implemented changes

- Added `.vercelignore` rules for server/runtime code, local data, environment files, source maps, and internal documentation.
- Added HSTS, Permissions Policy, cross-domain policy, and existing baseline security headers to the Vercel response configuration.
- Added noindex/no-store controls for health/status routes and removed those routes from both sitemaps. Robots exclusions are only crawler guidance and are not treated as security.
- Removed the bot-token-shaped URL from the status dashboard and stopped that card from probing Telegram with a browser-visible credential.
- Hardened the bot health response without changing its existing success body or port configuration.

## Explicitly not implemented

- No scanner signal API, payment flow, Telegram free/VIP delivery, trading bot, or production service was changed.
- No live execution, deployment, restart, push, or external credential rotation was performed.
- No client-side PIN was promoted to a claimed security boundary. Real protection for `/status`, `/health`, sensitive scanner APIs, and any paid signal response requires an authenticated server/proxy or private control plane; adding that requires an explicit architecture choice and route-by-route compatibility review.
- No blanket Content Security Policy was enforced because the existing pages use inline scripts and multiple third-party analytics/telemetry origins; an enforced policy should follow a browser-verified allowlist rollout.

## Deployment recommendation

The changes are safe to review and test locally. Production deployment is safe to consider only after reviewing the generated Vercel file list and confirming that the intended health/status operator workflow does not rely on public access. Before deployment, rotate any credential previously exposed in repository history or deployed HTML, configure secrets only in the runtime environment, and add real server-side authentication/rate limiting for sensitive routes. Do not treat the static client-side PIN, robots.txt, noindex tags, or Vercel headers as substitutes for that control.
