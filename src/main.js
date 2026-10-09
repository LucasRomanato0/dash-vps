import { createIcons, Activity, LayoutDashboard, Server, FlaskConical, FileJson, ShieldCheck, ShieldAlert, Cpu, MemoryStick, HardDrive, Clock3, Boxes, ChartNoAxesCombined, Radio, Bot, Route, Layers, Globe, Bell, CircleCheck, TriangleAlert, Container, Box, Inbox, RefreshCw, Sun, Moon, ArrowUpRight } from 'lucide';
import { loadReport } from './data/report.js';
import { dashboard } from './components.js';
import { destroyCharts, renderCharts } from './charts.js';
import { selectPeriod } from './data/report.js';
import { datetime, escape, icon } from './format.js';
import './style.css';
const icons = { Activity, LayoutDashboard, Server, FlaskConical, FileJson, ShieldCheck, ShieldAlert, Cpu, MemoryStick, HardDrive, Clock3, Boxes, ChartNoAxesCombined, Radio, Bot, Route, Layers, Globe, Bell, CircleCheck, TriangleAlert, Container, Box, Inbox, RefreshCw, Sun, Moon, ArrowUpRight };
let data, days = 1, theme = 'dark';
try { theme = localStorage.getItem('dash-vps-theme') === 'light' ? 'light' : 'dark'; } catch { /* Storage may be blocked. */ }
document.documentElement.dataset.theme = theme;
document.querySelector('#app').innerHTML = `<header class="topbar"><a class="brand" href="./" aria-label="Dash VPS, início"><span class="brand-mark">${icon('activity')}</span>Dash <strong>VPS</strong></a><div class="header-divider"></div><span class="workspace">Painel de infraestrutura</span><div class="header-actions"><span id="last-update">Aguardando coleta</span><button id="theme" class="icon-button" aria-label="Alternar tema"></button><button id="refresh" class="refresh">${icon('refresh-cw')}<span>Atualizar</span></button></div></header><div class="app-shell"><nav class="sidebar" aria-label="Navegação principal"><a class="nav-active" href="#main" aria-label="Visão geral" title="Visão geral">${icon('layout-dashboard')}</a><span class="sidebar-line"></span><span class="sidebar-caption">VPS</span><span class="sidebar-bottom" title="Dashboard estático">${icon('server')}</span></nav><main id="main"><div id="feedback" role="status" aria-live="polite"></div><div id="content"><div class="loading">Carregando seu painel…</div></div></main></div>`;
const paintIcons = () => createIcons({ icons, attrs: { 'stroke-width': 1.7 } });
function themeButton() { document.querySelector('#theme').innerHTML = icon(theme === 'dark' ? 'sun' : 'moon'); document.querySelector('#theme').setAttribute('aria-label', `Ativar tema ${theme === 'dark' ? 'claro' : 'escuro'}`); }
function render() {
  destroyCharts();
  document.querySelector('#content').innerHTML = dashboard(data.report, days, data.demo);
  document.querySelector('#last-update').textContent = `Última coleta · ${datetime(data.report.collectedAt)}`;
  document.querySelectorAll('[data-period]').forEach(button => button.addEventListener('click', () => { days = Number(button.dataset.period); render(); document.querySelector(`[data-period="${days}"]`).focus(); }));
  renderCharts(selectPeriod(data.report, days).points, days);
  paintIcons();
}
async function refresh() {
  const button = document.querySelector('#refresh');
  button.disabled = true; button.classList.add('busy');
  document.querySelector('#content').setAttribute('aria-busy','true');
  const feedback = document.querySelector('#feedback');
  feedback.textContent = 'Carregando relatório…';
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 15000);
  try {
    data = await loadReport(import.meta.env.VITE_REPORT_URL?.trim(), controller.signal);
    render(); feedback.textContent = 'Relatório atualizado.';
  } catch (error) {
    feedback.innerHTML = `<div class="notice critical"><strong>Não foi possível atualizar.</strong> ${escape(error.name === 'AbortError' ? 'A fonte demorou mais de 15 segundos para responder.' : error.message)} ${data ? 'Exibindo a última leitura carregada.' : 'Use Atualizar para tentar novamente.'}</div>`;
    if (!data) document.querySelector('#content').innerHTML = '<div class="empty error-empty"><h2>Relatório indisponível</h2><p>Confira a URL e o formato do JSON configurado. Nenhum dado demonstrativo substituiu sua fonte.</p></div>';
  } finally { clearTimeout(timeout); button.disabled = false; button.classList.remove('busy'); document.querySelector('#content').setAttribute('aria-busy','false'); }
}
document.querySelector('#refresh').addEventListener('click', refresh);
document.querySelector('#theme').addEventListener('click', () => { theme = theme === 'dark' ? 'light' : 'dark'; document.documentElement.dataset.theme = theme; try { localStorage.setItem('dash-vps-theme', theme); } catch { /* Optional preference. */ } themeButton(); if (data) render(); paintIcons(); });
themeButton(); paintIcons(); refresh();
