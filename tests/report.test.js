import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createDemo } from '../src/data/demo.js';
import { average, health, loadReport, selectPeriod, validateReport } from '../src/data/report.js';
const make = () => createDemo(new Date('2026-10-09T12:00:00Z'));
test('demonstração é válida e tem 30 dias de histórico ordenado', () => {
  const report = validateReport(make());
  assert.equal(report.history.length, 721);
  assert.equal(selectPeriod(report, 1).points.length,25);
  assert.equal(selectPeriod(report, 7).points.length,169);
  assert.equal(selectPeriod(report, 30).points.length,721);
  assert.notEqual(average(selectPeriod(report,1).points,'disk'), average(selectPeriod(report,30).points,'disk'));
  assert.equal(selectPeriod(report,1).alerts.length,2);
  assert.equal(selectPeriod(report,7).alerts.length,3);
});
test('status cobre atenção, normal, crítico e ausência de dados', () => {
  const report = make();
  assert.equal(health(report).level,'warning');
  report.history.at(-1).containers.exited = 0;
  assert.equal(health(report).level,'normal');
  report.history.at(-1).disk = 91;
  assert.equal(health(report).level,'critical');
  report.history.at(-1).disk = 50;
  report.services[0].online = false;
  assert.equal(health(report).level,'critical');
  report.history = [];
  assert.equal(health(report).level,'unknown');
  assert.equal(average([], 'cpu'),null);
});
test('validação rejeita percentuais inválidos, contagens, datas e histórico fora de ordem', () => {
  for (const mutate of [r=>r.history[0].cpu=101,r=>r.history[0].ram=NaN,r=>r.history[0].containers.running=-1,r=>r.collectedAt='invalid',r=>r.history.reverse(),r=>r.services[0].online='yes',r=>r.alerts[0].priority='urgent']) {
    const report = make(); mutate(report); assert.throws(()=>validateReport(report), /JSON inválido/);
  }
});
test('carregador usa demonstração somente sem URL e expõe erros da fonte real', async () => {
  assert.equal((await loadReport('')).demo,true);
  const original = globalThis.fetch;
  try {
    globalThis.fetch = async () => ({ ok:false, status:503 });
    await assert.rejects(loadReport('/report.json'),/HTTP 503/);
    globalThis.fetch = async () => ({ ok:true, json:async()=>make() });
    assert.equal((await loadReport('/report.json')).demo,false);
    globalThis.fetch = async () => ({ ok:true, json:async()=>({}) });
    await assert.rejects(loadReport('/report.json'),/JSON inválido/);
  } finally { globalThis.fetch = original; }
});
