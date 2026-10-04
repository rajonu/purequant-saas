import test from 'node:test';
import assert from 'node:assert/strict';
import {
  aggregateKpis,
  buildActiveSignals,
  buildHistory,
  isTerminalStatus,
  normalizePublicMetrics,
  normalizeHealth,
  normalizeTerminalEvent,
  pnlPercent
} from './dashboard-core.mjs';

test('calculates BUY PnL from entry and exit prices', () => {
  assert.equal(pnlPercent(100, 112.5, 'BUY'), 12.5);
  assert.equal(pnlPercent(100, 97.25, 'LONG'), -2.75);
});

test('calculates SELL PnL in the opposite direction', () => {
  assert.equal(pnlPercent(100, 87.5, 'SELL'), 12.5);
  assert.equal(pnlPercent(100, 103.25, 'SHORT'), -3.25);
});

test('rejects missing, invalid, and unknown PnL inputs', () => {
  assert.equal(pnlPercent(null, 100, 'BUY'), null);
  assert.equal(pnlPercent(100, 0, 'BUY'), null);
  assert.equal(pnlPercent(100, 105, 'SIDEWAYS'), null);
});

test('maps terminal lifecycle events without inventing missing PnL', () => {
  assert.equal(isTerminalStatus('TP1_HIT'), false);
  assert.equal(isTerminalStatus('TP3_HIT'), true);
  const item = normalizeTerminalEvent({
    signal_id: 'sig-1',
    event_type: 'SL_HIT',
    timestamp: '2026-10-04T00:00:00Z',
    data: { symbol: 'ETHUSDT', direction: 'SELL', entry_price: 2000 }
  });
  assert.equal(item.status, 'SL_HIT');
  assert.equal(item.pnlPct, null);
  assert.equal(item.dataIncomplete, true);
  const eventWithLiveSignal = normalizeTerminalEvent(
    { signal_id: 'sig-2', event_type: 'TP_HIT', data: { exit_price: 110 } },
    { signal_id: 'sig-2', current_state: 'ENTRY_REACHED', direction: 'BUY', trade_plan: { entry_reference: 100 } }
  );
  assert.equal(eventWithLiveSignal.pnlPct, 10);
});

test('builds history and removes closed IDs from active signals', () => {
  const signals = [
    { signal_id: 'open', symbol: 'BTCUSDT', direction: 'BUY', current_state: 'ENTRY_REACHED', trade_plan: { entry_reference: 100 } },
    { signal_id: 'closed', symbol: 'ETHUSDT', direction: 'BUY', current_state: 'TP3_HIT', trade_plan: { entry_reference: 200 } }
  ];
  const history = buildHistory([{ signal_id: 'closed', event_type: 'TP3_HIT', timestamp: '2026-10-04T00:00:00Z', data: { exit_price: 220 } }], signals);
  assert.equal(history.length, 1);
  assert.equal(history[0].pnlPct, 10);
  assert.deepEqual(buildActiveSignals(signals, history).map(item => item.signalId), ['open']);
});

test('aggregates KPIs from valid closed results only', () => {
  const kpis = aggregateKpis([{ pnlPct: 10 }, { pnlPct: -4 }, { pnlPct: null }]);
  assert.deepEqual(kpis, { closedSignals: 3, validResults: 2, netReturn: 6, wins: 1, winRate: 50 });
  assert.equal(aggregateKpis([]).netReturn, null);
  assert.equal(aggregateKpis([]).winRate, null);
});

test('adapts the live public metrics shape and recalculates PnL from prices', () => {
  const metrics = normalizePublicMetrics({
    active_signals: [{ signal_id: 'live-1', symbol: 'BTCUSDT', direction: 'LONG', entry_reference: 100, score: 90, setup: 'EMA_ALIGNMENT' }],
    closed_signals: [{ signal_id: 'closed-1', pair: 'BTC/USDT', direction: 'BUY', entry_price: 100, exit_price: 105, pnl_pct: 999, status: 'WIN', exit_time: '2026-10-04T01:00:00Z' }],
    system_health: { modules: [{ name: 'Scanner', status: 'operational', detail: 'Live' }] }
  });
  const history = buildHistory(metrics.closedSignals, metrics.activeSignals);
  assert.equal(history[0].pnlPct, 5);
  assert.equal(history[0].symbol, 'BTC/USDT');
  assert.deepEqual(normalizeHealth(metrics.health), [{ name: 'Scanner', ok: true, detail: 'Live' }]);
});
