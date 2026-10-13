import { createDemo } from './demo.js';
export const states = ['running', 'stopped', 'exited', 'restarting'];
const number = (v) => typeof v === 'number' && Number.isFinite(v) && v >= 0;
const date = (v) => typeof v === 'string' && Number.isFinite(Date.parse(v));
export function validateReport(data) {
  const fail = () => { throw new Error('JSON inválido. Confira o contrato do relatório no README.'); };
  if (!data || data.version !== 1 || typeof data.hostname !== 'string' || !date(data.collectedAt)) fail();
  if (!data.host || !['cores', 'ramGb', 'diskGb', 'uptimeSeconds'].every(k => number(data.host[k])) || data.host.cores < 1) fail();
  if (!['os', 'region'].every(k => typeof data.host[k] === 'string')) fail();
  if (!['history', 'services', 'alerts', 'problemContainers'].every(k => Array.isArray(data[k]))) fail();
  let previous = -Infinity;
  for (const point of data.history) {
    if (!point || !date(point.timestamp) || Date.parse(point.timestamp) <= previous || Date.parse(point.timestamp) > Date.parse(data.collectedAt)) fail();
    if (!['cpu', 'ram', 'disk', 'load'].every(k => number(point[k])) || ['cpu', 'ram', 'disk'].some(k => point[k] > 100)) fail();
    if (!point.containers || !states.every(k => Number.isInteger(point.containers[k]) && point.containers[k] >= 0)) fail();
    previous = Date.parse(point.timestamp);
  }
  for (const s of data.services) if (!s || typeof s.name !== 'string' || typeof s.description !== 'string' || typeof s.online !== 'boolean' || (s.latencyMs != null && !number(s.latencyMs))) fail();
  for (const a of data.alerts) if (!a || !['info', 'warning', 'critical'].includes(a.priority) || !date(a.timestamp) || typeof a.title !== 'string' || typeof a.description !== 'string') fail();
  for (const c of data.problemContainers) if (!c || typeof c.name !== 'string' || typeof c.detail !== 'string' || !states.includes(c.state)) fail();
  return data;
}
export async function loadReport(url, signal) {
  if (!url) return { report: validateReport(createDemo()), demo: true };
  const response = await fetch(url, { signal, cache: 'no-store', credentials: 'omit' });
  if (!response.ok) throw new Error(`Não foi possível carregar o relatório (HTTP ${response.status}).`);
  return { report: validateReport(await response.json()), demo: false };
}
export async function loadDashboard(apiUrl, reportUrl, days, signal) {
  if (!apiUrl?.trim()) return loadReport(reportUrl?.trim(), signal);
  const period = { 1: '24h', 7: '7d', 30: '30d' }[days];
  if (!period) throw new Error('Período inválido.');
  const base = apiUrl.trim().replace(/\/+$/, '');
  const response = await fetch(`${base}/api/v1/dashboard?period=${period}`, { signal, cache: 'no-store', credentials: 'omit' });
  if (!response.ok) throw new Error(`Não foi possível carregar a API (HTTP ${response.status}).`);
  return { report: validateReport(await response.json()), demo: false, source: 'api' };
}
export function selectPeriod(report, days) {
  const end = Date.parse(report.collectedAt);
  const start = end - days * 86400000;
  return { points: report.history.filter(p => Date.parse(p.timestamp) >= start && Date.parse(p.timestamp) <= end), alerts: report.alerts.filter(a => Date.parse(a.timestamp) >= start && Date.parse(a.timestamp) <= end).sort((a,b) => Date.parse(b.timestamp) - Date.parse(a.timestamp)) };
}
export function health(report) {
  const last = report.history.at(-1);
  if (!last) return { level: 'unknown', label: 'Sem dados', description: 'Aguardando amostras de monitoramento.' };
  if (Math.max(last.cpu, last.ram, last.disk) >= 90 || report.services.some(s => !s.online) || last.load >= report.host.cores * 2) return { level: 'critical', label: 'Crítico', description: 'Uma ou mais métricas precisam de intervenção.' };
  if (Math.max(last.cpu, last.ram, last.disk) >= 75 || last.load >= report.host.cores || last.containers.exited > 0 || last.containers.restarting > 0) return { level: 'warning', label: 'Atenção', description: 'Serviços monitorados. Há pontos que merecem sua atenção.' };
  return { level: 'normal', label: 'Normal', description: 'Tudo em ordem. Sua infraestrutura está operando normalmente.' };
}
export const average = (points, key) => points.length ? points.reduce((sum, p) => sum + p[key], 0) / points.length : null;
