export const DEFAULT_SCANNER_API_BASE = 'https://dashboard.purequantai.xyz';

export const SCANNER_ENDPOINTS = Object.freeze({
  publicMetrics: '/api/public/metrics',
  activeSignals: '/api/v2/signals',
  lifecycleEvents: '/api/v2/events',
  health: '/api/health'
});

const TERMINAL_STATUS_ALIASES = new Map([
  ['TP_HIT', 'TP'],
  ['TP', 'TP'],
  ['TAKE_PROFIT', 'TP'],
  ['TAKE_PROFIT_HIT', 'TP'],
  ['TP3_HIT', 'TP'],
  ['SL_HIT', 'SL'],
  ['STOP_LOSS', 'SL'],
  ['STOP_LOSS_HIT', 'SL'],
  ['TIMEOUT', 'TIMEOUT'],
  ['TIMED_OUT', 'TIMEOUT'],
  ['TIMEOUT_WIN', 'TIMEOUT'],
  ['TIMEOUT_LOSS', 'TIMEOUT'],
  ['EXPIRED', 'TIMEOUT'],
  ['WIN', 'CLOSED'],
  ['PROFIT', 'CLOSED'],
  ['GAIN', 'CLOSED'],
  ['LOSS', 'CLOSED'],
  ['CLOSED', 'CLOSED'],
  ['CLOSE', 'CLOSED']
]);

const NON_ACTIVE_STATUSES = new Set([
  'INVALIDATED',
  'ALREADY_MOVED',
  ...TERMINAL_STATUS_ALIASES.keys()
]);

function asObject(value) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
}

function firstDefined(...values) {
  return values.find(value => value !== undefined && value !== null && value !== '');
}

export function finitePositiveNumber(value) {
  const number = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(number) && number > 0 ? number : null;
}

function finiteNumber(value) {
  const number = typeof value === 'number' ? value : Number(value);
  return Number.isFinite(number) ? number : null;
}

export function normalizeDirection(value) {
  const direction = String(value || '').trim().toUpperCase();
  if (direction === 'BUY' || direction === 'LONG') return 'BUY';
  if (direction === 'SELL' || direction === 'SHORT') return 'SELL';
  return null;
}

export function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase().replace(/[ -]+/g, '_');
}

export function terminalOutcomeKind(value) {
  return TERMINAL_STATUS_ALIASES.get(normalizeStatus(value)) || null;
}

export function isTerminalStatus(value) {
  return terminalOutcomeKind(value) !== null;
}

export function isSignalActive(signal) {
  const item = asObject(signal);
  const status = normalizeStatus(firstDefined(item.current_state, item.status, item.state));
  return !NON_ACTIVE_STATUSES.has(status);
}

function tradePlan(value) {
  return asObject(value).trade_plan || {};
}

export function entryPrice(value) {
  const item = asObject(value);
  const plan = tradePlan(item);
  return finitePositiveNumber(firstDefined(
    item.entry_price,
    item.entry,
    item.entry_reference,
    plan.entry_price,
    plan.entry_reference,
    item.reference_price,
    item.data && item.data.entry_price,
    item.data && item.data.entry,
    item.data && item.data.entry_reference,
    item.data && item.data.trade_plan && item.data.trade_plan.entry_reference
  ));
}

export function exitPrice(value) {
  const item = asObject(value);
  const outcome = asObject(item.outcome);
  const data = asObject(item.data);
  return finitePositiveNumber(firstDefined(
    item.exit_price,
    item.close_price,
    item.closed_price,
    item.exit,
    outcome.exit_price,
    outcome.close_price,
    data.exit_price,
    data.close_price,
    data.closed_price,
    data.exit,
    data.outcome && data.outcome.exit_price,
    data.outcome && data.outcome.close_price
  ));
}

export function pnlPercent(entry, exit, direction) {
  const entryValue = finitePositiveNumber(entry);
  const exitValue = finitePositiveNumber(exit);
  const side = normalizeDirection(direction);
  if (entryValue === null || exitValue === null || side === null) return null;
  const grossReturn = side === 'SELL'
    ? ((entryValue - exitValue) / entryValue) * 100
    : ((exitValue - entryValue) / entryValue) * 100;
  return Number.isFinite(grossReturn) ? Number(grossReturn.toFixed(2)) : null;
}

export function formatPnl(value) {
  return typeof value === 'number' && Number.isFinite(value)
    ? `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
    : '—';
}

function eventPayload(event) {
  const item = asObject(event);
  const data = asObject(item.data);
  return {
    ...data,
    ...(asObject(data.signal)),
    ...(asObject(data.outcome)),
    ...(asObject(item.outcome))
  };
}

export function normalizeActiveSignal(signal) {
  const item = asObject(signal);
  const plan = tradePlan(item);
  const direction = normalizeDirection(firstDefined(item.direction, plan.direction));
  return {
    signalId: firstDefined(item.signal_id, item.id) || null,
    symbol: firstDefined(item.symbol, item.pair) || 'UNKNOWN',
    direction,
    entry: entryPrice(item),
    state: firstDefined(item.current_state, item.status, item.state) || 'ACTIVE',
    setup: firstDefined(item.setup, item.setup_type) || '—',
    tp1: finitePositiveNumber(item.tp1 ?? plan.tp1),
    tp2: finitePositiveNumber(item.tp2 ?? plan.tp2),
    tp3: finitePositiveNumber(item.tp3 ?? plan.tp3),
    stopLoss: finitePositiveNumber(item.stop_loss ?? plan.stop_loss),
    riskReward: finiteNumber(item.risk_reward ?? plan.risk_reward),
    score: finiteNumber(item.score),
    updatedAt: firstDefined(item.updated_at, item.timing && item.timing.updated_at, item.timestamp) || null,
    expiresAt: firstDefined(item.expires_at, item.timing && item.timing.expires_at) || null
  };
}

export function normalizeTerminalEvent(event, signal = {}) {
  const item = asObject(event);
  const payload = eventPayload(item);
  const source = { ...item, ...asObject(signal), ...payload };
  const plan = tradePlan(source);
  const direction = normalizeDirection(firstDefined(
    source.direction,
    plan.direction,
    signal.direction,
    signal.trade_plan && signal.trade_plan.direction
  ));
  const status = normalizeStatus(firstDefined(
    item.status,
    item.outcome_status,
    item.current_state,
    item.event_type,
    payload.status,
    payload.outcome_status,
    payload.current_state,
    payload.event_type,
    signal.current_state
  ));
  const kind = terminalOutcomeKind(status);
  if (!kind) return null;

  const entry = entryPrice(source) ?? entryPrice(signal);
  const exit = exitPrice(source);
  const pnl = pnlPercent(entry, exit, direction);
  return {
    signalId: firstDefined(item.signal_id, source.signal_id, signal.signal_id) || null,
    symbol: firstDefined(source.symbol, source.pair, signal.symbol) || 'UNKNOWN',
    direction,
    entry,
    exit,
    pnlPct: pnl,
    status: status || kind,
    rawStatus: status || 'CLOSED',
    closedAt: firstDefined(item.timestamp, source.closed_at, source.exit_timestamp, source.exit_time, source.timestamp) || null,
    dataIncomplete: entry === null || exit === null || direction === null
  };
}

export function normalizePublicMetrics(payload) {
  const data = asObject(payload);
  return {
    activeSignals: Array.isArray(data.active_signals) ? data.active_signals : [],
    closedSignals: Array.isArray(data.closed_signals) ? data.closed_signals : [],
    health: asObject(data.system_health),
    sourceUpdatedAt: data.updated_at || null
  };
}

export function normalizeHealth(health) {
  const data = asObject(health);
  const modules = Array.isArray(data.modules) ? data.modules : [];
  return modules.map(module => ({
    name: firstDefined(module.name, module.module) || 'Scanner module',
    ok: String(module.status || '').toLowerCase() === 'operational',
    detail: [module.detail, module.target].filter(Boolean).join(' · ') || 'No detail reported'
  }));
}

function eventTimestamp(value) {
  const time = Date.parse(value || '');
  return Number.isFinite(time) ? time : 0;
}

export function buildHistory(events, signals = []) {
  const signalById = new Map(signals.map(signal => [signal.signal_id, signal]));
  const latestBySignal = new Map();
  for (const signal of Array.isArray(signals) ? signals : []) {
    const normalized = normalizeTerminalEvent(signal, signal);
    if (normalized && normalized.signalId) latestBySignal.set(normalized.signalId, normalized);
  }
  for (const event of Array.isArray(events) ? events : []) {
    const signal = signalById.get(event && event.signal_id) || {};
    const normalized = normalizeTerminalEvent(event, signal);
    if (!normalized || !normalized.signalId) continue;
    const previous = latestBySignal.get(normalized.signalId);
    if (!previous || eventTimestamp(normalized.closedAt) >= eventTimestamp(previous.closedAt)) {
      latestBySignal.set(normalized.signalId, normalized);
    }
  }
  return [...latestBySignal.values()].sort((a, b) => eventTimestamp(b.closedAt) - eventTimestamp(a.closedAt));
}

export function buildActiveSignals(signals, history = []) {
  const closedIds = new Set(history.map(item => item.signalId).filter(Boolean));
  return (Array.isArray(signals) ? signals : [])
    .filter(signal => isSignalActive(signal) && !closedIds.has(signal.signal_id))
    .map(normalizeActiveSignal)
    .filter(signal => signal.signalId);
}

export function aggregateKpis(history) {
  const valid = (Array.isArray(history) ? history : []).filter(item => typeof item.pnlPct === 'number' && Number.isFinite(item.pnlPct));
  const netReturn = valid.length ? Number(valid.reduce((sum, item) => sum + item.pnlPct, 0).toFixed(2)) : null;
  const wins = valid.filter(item => item.pnlPct > 0).length;
  return {
    closedSignals: Array.isArray(history) ? history.length : 0,
    validResults: valid.length,
    netReturn,
    wins,
    winRate: valid.length ? Number(((wins / valid.length) * 100).toFixed(1)) : null
  };
}

export function unwrapSignals(payload) {
  return Array.isArray(payload) ? payload : Array.isArray(payload?.signals) ? payload.signals : [];
}

export function unwrapEvents(payload) {
  return Array.isArray(payload) ? payload : Array.isArray(payload?.events) ? payload.events : [];
}
