import Chart from 'chart.js/auto';
import { datetime, fmt } from './format.js';
let charts = [];
export function destroyCharts() { charts.forEach(c => c.destroy()); charts = []; }
export function renderCharts(points, days) {
  destroyCharts();
  if (!points.length) return;
  const css = getComputedStyle(document.documentElement);
  const text = css.getPropertyValue('--muted').trim();
  const grid = css.getPropertyValue('--line').trim();
  const labels = points.map(p => new Intl.DateTimeFormat('pt-BR', days === 1 ? { hour: '2-digit', minute: '2-digit' } : { day: '2-digit', month: '2-digit' }).format(new Date(p.timestamp)));
  const definitions = [ ['resources', [{ key: 'cpu', label: 'CPU', color: '#70dfb0' }, { key: 'ram', label: 'RAM', color: '#a99aff' }]], ['storage', [{ key: 'disk', label: 'Disco', color: '#65b6fa' }]], ['load', [{ key: 'load', label: 'Load average (1 min)', color: '#ebba70' }]], ['containers', [{ key: 'running', label: 'Running', color: '#70dfb0' }, { key: 'stopped', label: 'Stopped', color: '#7e8ea6' }, { key: 'exited', label: 'Exited', color: '#ee927d' }, { key: 'restarting', label: 'Restarting', color: '#ebba70' }]] ];
  for (const [id, series] of definitions) {
    const container = id === 'containers';
    const percent = ['resources', 'storage'].includes(id);
    charts.push(new Chart(document.getElementById(`chart-${id}`), {
      type: 'line', data: { labels, datasets: series.map(s => ({ label: s.label, data: points.map(p => container ? p.containers[s.key] : p[s.key]), borderColor: s.color, backgroundColor: `${s.color}18`, borderWidth: 2, pointRadius: 0, pointHoverRadius: 4, tension: .3, fill: container || id === 'storage', stepped: container })) },
      options: { responsive: true, maintainAspectRatio: false, animation: false, interaction: { intersect: false, mode: 'index' }, plugins: { legend: { display: false }, tooltip: { backgroundColor: '#192330', titleColor: '#f1f5f9', bodyColor: '#d4dce8', padding: 12, callbacks: { title: items => datetime(points[items[0].dataIndex].timestamp), label: ctx => `${ctx.dataset.label}: ${fmt(ctx.parsed.y, percent ? 1 : 2)}${percent ? '%' : ''}` } } }, scales: { x: { grid: { display: false }, ticks: { color: text, maxTicksLimit: days === 1 ? 7 : 6, maxRotation: 0, autoSkip: true }, border: { display: false } }, y: { min: 0, max: percent ? 100 : undefined, stacked: container, grid: { color: grid }, border: { display: false }, ticks: { color: text, precision: container ? 0 : undefined, maxTicksLimit: 5, callback: value => `${fmt(value)}${percent ? '%' : ''}` } } } }
    }));
  }
  document.querySelectorAll('[data-series]').forEach(button => button.addEventListener('click', () => {
    const chart = charts[Number(button.dataset.chart)];
    const index = Number(button.dataset.series);
    const visible = chart.isDatasetVisible(index);
    chart.setDatasetVisibility(index, !visible); chart.update(); button.setAttribute('aria-pressed', String(!visible));
  }));
}
