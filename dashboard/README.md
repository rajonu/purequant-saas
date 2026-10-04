# Scanner dashboard

This is a standalone, read-only SaaS dashboard at `/dashboard/`. It does not execute trades, place orders, read portfolio state, or import the local trading project.

## Read-only source contract

The browser adapter reads the read-only public scanner metrics API configured by `window.PUREQUANT_SCANNER_API_BASE` (default: `https://dashboard.purequantai.xyz`):

- `GET /api/public/metrics` — `{ active_signals, closed_signals, system_health, updated_at }`.

The live public metrics response is an aggregation of the canonical scanner signal feed and its terminal signal ledger. The adapter deliberately recalculates PnL from each closed row’s prices instead of trusting a supplied `pnl_pct` field. Canonical endpoints remain supported by the core contract for future adapter expansion.

The expected public metrics shapes are:

- `active_signals[]`: `signal_id`, `symbol`, `direction`, `entry_reference`, `score`, `setup`, `tp1`, `tp2`, `tp3`, `stop_loss`, and `risk_reward`.
- `closed_signals[]`: `signal_id`, `pair` or `symbol`, `direction`, `entry_price`, `exit_price`, `exit_time`, and `status`.
- `system_health.modules[]`: `name`, `status`, `detail`, and optional `target`.

Active canonical signals should include `signal_id`, `symbol`, `direction` (`BUY`/`SELL` or `LONG`/`SHORT`), `current_state`, and `trade_plan.entry_reference`.

Terminal lifecycle events must include `signal_id`, a terminal `event_type` or `data.status`, and an exit price. The recommended shape is:

```json
{
  "signal_id": "sig_example",
  "event_type": "TP_HIT",
  "timestamp": "2026-10-04T00:00:00.000Z",
  "data": {
    "symbol": "BTCUSDT",
    "direction": "BUY",
    "entry_price": 100,
    "exit_price": 105
  }
}
```

Supported terminal statuses are `TP_HIT`/`TAKE_PROFIT`, `TP3_HIT`, `SL_HIT`/`STOP_LOSS`, `TIMEOUT`/`EXPIRED`, and `CLOSED`. `TP1_HIT` and `TP2_HIT` are treated as intermediate lifecycle states, not full closures.

PnL is calculated from actual prices:

- BUY/LONG: `(exit - entry) / entry * 100`
- SELL/SHORT: `(entry - exit) / entry * 100`

Invalid or missing prices produce `—` and are excluded from Net Return and Win Rate. No historical performance values are fabricated by this module.
