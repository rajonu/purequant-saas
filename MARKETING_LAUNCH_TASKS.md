# PureQuant Marketing Launch Task Handler

## Completed in this update

- [x] Remove the $6 Pro tier from the landing page and Telegram plan menu.
- [x] Keep only $3/month Starter and $9 one-time Lifetime plans.
- [x] Remove the matching `pro` checkout tracking path.
- [x] Replace unsupported return, liquidation, urgency and certainty claims with risk-aware copy.
- [x] Align free-channel wording with the current one-signal-per-day behavior.

## Before deployment

- [ ] Run HTML/script and Python syntax checks.
- [ ] Confirm landing-page pricing, bot pricing and payment plan keys match.
- [ ] Confirm no `start=pro` links remain.
- [ ] Confirm payment invoice and admin approval still work for `starter` and `lifetime_vip`.
- [ ] Confirm free/VIP signal dispatch code is unchanged except for wording.

## Deployment and verification

- [ ] Commit only landing-page, bot-plan and task-handler files; exclude runtime logs and data files.
- [ ] Deploy the landing-page source to the linked Vercel project.
- [ ] Verify the live page, Telegram plan menu and both payment deep links.
- [ ] Verify scanner, dashboard, Telegram free channel and health page links.
- [ ] Keep the ad campaign paused until live checks pass.

## Marketing launch gate

- [ ] Use product/feature claims that can be demonstrated on the live scanner.
- [ ] Avoid guaranteed profit, zero-risk, guaranteed accuracy, fake scarcity and unsupported win-rate claims.
- [ ] Start with a small creative test and track landing view, free-channel join, verified scanner session and checkout start.
- [ ] Scale only after the funnel and payment support path are stable.
