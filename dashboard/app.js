import {
  DEFAULT_SCANNER_API_BASE,
  SCANNER_ENDPOINTS,
  aggregateKpis,
  buildActiveSignals,
  buildHistory,
  formatPnl,
  normalizeHealth,
  normalizePublicMetrics
} from './dashboard-core.mjs';

const apiBase = String(window.PUREQUANT_SCANNER_API_BASE || DEFAULT_SCANNER_API_BASE).replace(/\/$/, '');
const state = { signals: [], history: [], health: [], lastSync: null, error: null };
const $ = id => document.getElementById(id);

function text(value, fallback = '—') {
  return value === null || value === undefined || value === '' ? fallback : String(value);
}

function formatPrice(value) {
  if (typeof value !== 'number' || !Number.isFinite(value)) return '—';
  return `$${value >= 1 ? value.toLocaleString(undefined, { maximumFractionDigits: 6 }) : value.toPrecision(6)}`;
}

function formatTime(value) {
  if (!value) return '—';
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? '—' : date.toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
}

function setText(id, value) {
  const element = $(id);
  if (element) element.textContent = value;
}

function makeCell(value, className = '') {
  const cell = document.createElement('td');
  if (className) cell.className = className;
  cell.textContent = text(value);
  return cell;
}

function renderKpis() {
  const kpis = aggregateKpis(state.history);
  setText('kpi-net-return', formatPnl(kpis.netReturn));
  setText('kpi-win-rate', kpis.winRate === null ? '—' : `${kpis.winRate.toFixed(1)}%`);
  setText('kpi-active', String(state.signals.length));
  const healthy = state.health.filter(item => item.ok).length;
  const healthTotal = state.health.length;
  setText('kpi-health', healthTotal ? `${healthy}/${healthTotal}` : '—');
  $('kpi-net-return')?.classList.toggle('negative', typeof kpis.netReturn === 'number' && kpis.netReturn < 0);
  $('kpi-win-rate')?.classList.toggle('negative', typeof kpis.winRate === 'number' && kpis.winRate < 50);
}

function renderActive() {
  const body = $('active-body');
  if (!body) return;
  body.replaceChildren();
  if (!state.signals.length) {
    const row = document.createElement('tr');
    const cell = makeCell('No active scanner signals are currently available.', 'empty-state');
    cell.colSpan = 7;
    row.append(cell);
    body.append(row);
    return;
  }
  for (const signal of state.signals) {
    const row = document.createElement('tr');
    row.append(
      makeCell(signal.symbol, 'symbol'),
      makeCell(signal.direction),
      makeCell(formatPrice(signal.entry)),
      makeCell(signal.state),
      makeCell(signal.setup),
      makeCell(signal.score === null ? '—' : signal.score.toFixed(0)),
      makeCell(formatTime(signal.updatedAt))
    );
    body.append(row);
  }
}

function renderHistory() {
  const body = $('history-body');
  if (!body) return;
  body.replaceChildren();
  if (!state.history.length) {
    const row = document.createElement('tr');
    const cell = makeCell('No terminal scanner outcomes are available.');
    cell.colSpan = 7;
    cell.className = 'empty-state';
    row.append(cell);
    body.append(row);
    return;
  }
  for (const item of state.history) {
    const row = document.createElement('tr');
    const pnlClass = item.pnlPct === null ? 'muted' : item.pnlPct < 0 ? 'negative' : 'positive';
    row.append(
      makeCell(item.symbol, 'symbol'),
      makeCell(item.direction),
      makeCell(formatPrice(item.entry)),
      makeCell(formatPrice(item.exit)),
      makeCell(item.status),
      makeCell(formatPnl(item.pnlPct), pnlClass),
      makeCell(formatTime(item.closedAt))
    );
    body.append(row);
  }
}

function renderHealth() {
  const container = $('health-grid');
  if (!container) return;
  container.replaceChildren();
  const items = state.health.length ? state.health : [{ name: 'Scanner API', ok: false, detail: 'No health response received' }];
  for (const item of items) {
    const card = document.createElement('article');
    card.className = `health-card ${item.ok ? 'ok' : 'unavailable'}`;
    const title = document.createElement('h3');
    title.textContent = item.name;
    const status = document.createElement('strong');
    status.textContent = item.ok ? 'AVAILABLE' : 'UNAVAILABLE';
    const detail = document.createElement('p');
    detail.textContent = item.detail;
    card.append(title, status, detail);
    container.append(card);
  }
}

async function fetchJson(path) {
  const response = await fetch(`${apiBase}${path}`, { headers: { Accept: 'application/json' } });
  if (!response.ok) throw new Error(`${path} returned HTTP ${response.status}`);
  return response.json();
}

async function loadDashboard() {
  state.error = null;
  const metricsResult = await Promise.allSettled([fetchJson(SCANNER_ENDPOINTS.publicMetrics)]);
  if (metricsResult[0].status === 'fulfilled') {
    const metrics = normalizePublicMetrics(metricsResult[0].value);
    state.history = buildHistory(metrics.closedSignals, metrics.activeSignals);
    state.signals = buildActiveSignals(metrics.activeSignals, state.history);
    state.health = [...normalizeHealth(metrics.health), { name: 'Dashboard adapter', ok: true, detail: 'Read-only scanner metrics loaded' }];
  } else {
    state.history = [];
    state.signals = [];
    state.health = [{ name: 'Public metrics feed', ok: false, detail: 'Scanner metrics unavailable' }, { name: 'Dashboard adapter', ok: true, detail: 'No values inferred' }];
    state.error = 'Scanner metrics are unavailable. Values are not inferred.';
  }
  state.lastSync = new Date();
  renderKpis();
  renderActive();
  renderHistory();
  renderHealth();
  setText('last-sync', `Last sync: ${formatTime(state.lastSync)}`);
  setText('feed-message', state.error || `Read-only source: ${apiBase}${SCANNER_ENDPOINTS.publicMetrics}`);
}

function setupTabs() {
  document.querySelectorAll('[data-tab]').forEach(button => {
    button.addEventListener('click', () => {
      document.querySelectorAll('[data-tab]').forEach(item => item.classList.toggle('active', item === button));
      document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.toggle('active', panel.id === `panel-${button.dataset.tab}`));
    });
  });
}

setupTabs();
$('refresh-button')?.addEventListener('click', loadDashboard);
loadDashboard().catch(error => {
  state.error = 'Scanner dashboard could not load. Values are not inferred.';
  state.health = [{ name: 'Dashboard adapter', ok: false, detail: error.message }];
  renderKpis();
  renderActive();
  renderHistory();
  renderHealth();
  setText('feed-message', state.error);
});
