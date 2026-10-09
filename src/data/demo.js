// Fonte demonstrativa determinística, sem chamadas à infraestrutura real.
export function createDemo(now = new Date()) {
  const end = Math.floor(now.getTime() / 3600000) * 3600000;
  const history = Array.from({ length: 721 }, (_, i) => {
    const wave = Math.sin(i * .43);
    const spike = i % 97 === 0 ? 37 : 0;
    return { timestamp: new Date(end - (720 - i) * 3600000).toISOString(), cpu: +(23 + wave * 9 + Math.sin(i * .13) * 7 + spike).toFixed(1), ram: +(49 + i / 65 + wave * 3).toFixed(1), disk: +(49 + i / 95).toFixed(1), load: +(0.7 + (wave + 1) * .32 + spike / 25).toFixed(2), containers: { running: i % 97 === 0 ? 10 : 12, stopped: 1, exited: 1, restarting: i % 97 === 0 ? 2 : 0 } };
  });
  Object.assign(history.at(-1), { cpu: 24.8, ram: 62.4, disk: 56.6, load: 1.24 });
  return {
    version: 1, hostname: 'vps-01.romaia.com.br', collectedAt: new Date(end).toISOString(),
    host: { cores: 4, ramGb: 8, diskGb: 80, uptimeSeconds: 1977480, os: 'Ubuntu 24.04 LTS', region: 'São Paulo, BR' },
    history,
    services: [ { name: 'Hermes', description: 'Assistente & automações', online: true, latencyMs: 42 }, { name: '9Router', description: 'Gateway de modelos', online: true, latencyMs: 86 }, { name: 'Coolify', description: 'Deploy & infraestrutura', online: true, latencyMs: 124 }, { name: 'Sites', description: 'Aplicações & páginas web', online: true, latencyMs: 38 } ],
    alerts: [ { priority: 'warning', title: 'Container encerrado', description: 'backup-worker encerrou com código 1. Verifique os logs antes da próxima execução.', timestamp: new Date(end - 2100000).toISOString() }, { priority: 'info', title: 'Backup concluído', description: 'Snapshot diário da VPS criado com sucesso. Retenção de 7 dias.', timestamp: new Date(end - 7200000).toISOString() }, { priority: 'warning', title: 'Pico de utilização da CPU', description: 'CPU acima de 80% durante uma tarefa de build. Utilização normalizada.', timestamp: new Date(end - 3 * 86400000).toISOString() } ],
    problemContainers: [ { name: 'backup-worker', state: 'exited', detail: 'Código de saída 1' }, { name: 'staging-preview', state: 'stopped', detail: 'Parado manualmente' } ]
  };
}
