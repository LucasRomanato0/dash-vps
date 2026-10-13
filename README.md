# Dash VPS

Dashboard responsivo em português para **dash-vps.romaia.com.br**. Vite + JavaScript modular + Chart.js, sem backend obrigatório. Tema escuro padrão, tema claro persistido localmente, gráficos com tooltips e legendas clicáveis e tabela de amostras acessível por teclado.

## Executar

Requer Node.js 22.12+ e npm. As versões resolvidas estão no `package-lock.json`.

```sh
npm ci
npm run dev
npm run lint
npm test
npm run build
npm run preview
```

Desenvolvimento: `http://localhost:5173`. Preview do build: `http://localhost:4173`. `npm run preview` é apenas para conferir o build localmente.

## Publicação estática

Execute `npm ci && npm run build` e publique **o conteúdo de `dist/`** no diretório público do domínio. Funciona em Nginx, Caddy, hospedagem estática ou aplicação estática no Coolify (comando de build `npm run build`, diretório de saída `dist`). Configure DNS e HTTPS de `dash-vps.romaia.com.br` na hospedagem. Não é necessário Node.js no servidor que entrega os arquivos. Este projeto não configura DNS nem faz deploy automaticamente.

## Backend API

O diretório `backend/` contém uma API FastAPI isolada do frontend. O painel Vite continua usando seus dados demonstrativos e não faz chamadas para esta API.

Requer Python 3.11+.

```sh
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API estará em `http://127.0.0.1:8000`; `GET /api/v1/health` retorna:

```json
{"status":"ok","service":"dash-vps-api","database":"sqlite"}
```

Por padrão, o banco é criado em `backend/data/dash-vps.db`. Copie `backend/.env.example` para `backend/.env` e ajuste `DASH_VPS_DATABASE_PATH` se necessário, ou exporte essa variável antes de iniciar a API. O bootstrap é idempotente: cria a tabela `snapshots` e adiciona, sem apagar dados, as colunas necessárias a bancos criados pela versão inicial.

### Ingestão de métricas

`POST /api/v1/metrics` recebe uma fotografia de métricas e responde `201 Created` com `{ "id": 1, "collected_at": "..." }`. Os campos simples são armazenados em colunas consultáveis; as estruturas opcionais são preservadas como JSON. Autenticação ainda não faz parte deste incremento, portanto o endpoint deve ficar restrito a um ambiente confiável.

```sh
curl -X POST http://127.0.0.1:8000/api/v1/metrics \
  -H 'Content-Type: application/json' \
  -d '{
    "collected_at":"2026-10-09T12:00:00Z",
    "hostname":"vps-01",
    "cpu_percent":24.8,
    "memory_percent":62.4,
    "disk_percent":56.6,
    "load_1m":1.24,
    "uptime_seconds":1977480,
    "containers":{"running":12,"stopped":1,"exited":1,"restarting":0},
    "services":[{"name":"Hermes","online":true,"latency_ms":42}],
    "alerts":[],
    "problem_containers":[]
  }'
```

Contrato resumido: `collected_at` é uma data ISO 8601 com fuso horário; `hostname` é texto não vazio; CPU, memória e disco vão de 0 a 100; `load_1m` é não negativo; `uptime_seconds` e as quatro contagens de `containers` são inteiros não negativos. `services`, `alerts` e `problem_containers` podem ser omitidos, ser `null` ou conter listas de objetos JSON serializáveis. Não envie senhas, tokens, credenciais ou outros segredos nessas estruturas. Campos desconhecidos e valores inválidos retornam `422` com a localização do erro.

Para executar os testes do backend, dentro de `backend/` e com o ambiente virtual ativado:

```sh
pytest
```

Os testes criam seus próprios bancos em diretórios temporários, sem usar nem modificar o banco de desenvolvimento.

## Demonstração e fonte real

Sem `VITE_REPORT_URL`, o painel mostra explicitamente **Modo demonstrativo**. A fonte única `src/data/demo.js` gera 721 amostras horárias determinísticas, com última coleta na hora cheia e 30 dias de histórico. Atualizar relê a fonte; na mesma hora, a demonstração permanece igual.

Para integrar o JSON produzido pelo cron:

1. Gere um arquivo segundo o contrato abaixo. Não inclua senhas, tokens, logs sensíveis ou credenciais: tudo que o navegador recebe fica público.
2. Coloque-o, por exemplo, em `public/data/report.json` antes do build, ou publique `/data/report.json` no servidor e atualize-o atomicamente a cada execução do cron.
3. Copie `.env.example` para `.env.local` e defina `VITE_REPORT_URL=/data/report.json`.
4. Reinicie o desenvolvimento ou gere um novo build. Variáveis Vite são incorporadas no build e não são secretas.

O carregador em `src/data/report.js` faz um GET sem credenciais, sem cache e com limite de 15 segundos. Não existe endpoint de API presumido. Uma URL externa exige CORS na origem. Em caso de erro, mantém a última leitura bem-sucedida com aviso; na primeira falha, mostra estado de erro. **Não substitui silenciosamente erros por dados demonstrativos.**

Para exportar um exemplo completo compatível:

```sh
mkdir -p public/data
node --input-type=module -e "import { createDemo } from './src/data/demo.js'; import { writeFileSync } from 'node:fs'; writeFileSync('public/data/report.json', JSON.stringify(createDemo(), null, 2));"
```

### Contrato JSON v1

```json
{
  "version": 1,
  "hostname": "vps-01.example.com",
  "collectedAt": "2026-10-09T12:00:00Z",
  "host": {
    "cores": 4,
    "ramGb": 8,
    "diskGb": 80,
    "uptimeSeconds": 1977480,
    "os": "Ubuntu 24.04 LTS",
    "region": "São Paulo, BR"
  },
  "history": [{
    "timestamp": "2026-10-09T12:00:00Z",
    "cpu": 24.8,
    "ram": 62.4,
    "disk": 56.6,
    "load": 1.24,
    "containers": { "running": 12, "stopped": 1, "exited": 1, "restarting": 0 }
  }],
  "services": [{ "name": "Hermes", "description": "Assistente & automações", "online": true, "latencyMs": 42 }],
  "alerts": [{
    "priority": "warning",
    "title": "Container encerrado",
    "description": "Verifique o backup-worker.",
    "timestamp": "2026-10-09T11:30:00Z"
  }],
  "problemContainers": [{ "name": "backup-worker", "state": "exited", "detail": "Código de saída 1" }]
}
```

Todos os campos estruturais são obrigatórios. `latencyMs` pode ser omitido ou `null`. Arrays vazios são aceitos e exibem estados vazios. `history` deve estar em ordem cronológica estrita, sem duplicatas, com timestamps até `collectedAt`. CPU/RAM/disco: números de 0 a 100. Load: número não negativo (média de 1 minuto, sem normalização). Contagens: inteiros não negativos. Prioridades: `info`, `warning`, `critical`. Estados: `running`, `stopped`, `exited`, `restarting`. Serviços são configuráveis; a demonstração inclui Hermes, 9Router, Coolify e Sites.

### Semântica do painel

- Cards: última amostra disponível; uptime e serviços: último relatório. Médias dos cards, gráficos, tabela e alertas mudam com 24h/7 dias/30 dias.
- Períodos terminam em `collectedAt`, não no relógio local. Não há interpolação nem invenção de amostras faltantes. Para mostrar 30 dias, o cron deve preservar histórico.
- Status **Crítico**: CPU/RAM/disco ≥90%, load ≥2× núcleos ou serviço offline. **Atenção**: recursos ≥75%, load ≥núcleos ou containers exited/restarting. Caso contrário, **Normal**. Sem histórico: **Sem dados**. Alertas históricos não determinam status atual.
- Coleta com mais de 26 horas recebe aviso de desatualização, adequado ao cron diário. Altere esse limiar se a frequência mudar.
- Datas, números e percentuais em pt-BR; horários no fuso do navegador. Latências vêm do JSON: o navegador não testa serviços.
- Passe o cursor/toque nos gráficos para consultar valores; clique nas legendas para ocultar séries. A tabela expansível permite acesso aos mesmos valores por teclado e leitor de tela.

## Organização

- `src/main.js`: inicialização, atualização, tema e filtros.
- `src/components.js`: composição dos cards e seções, com escape de textos externos.
- `src/charts.js`: ciclo de vida e interação dos gráficos.
- `src/data/demo.js`: dados demonstrativos.
- `src/data/report.js`: carregamento, validação, filtros e cálculo de saúde.
- `src/format.js`, `src/style.css`: formatação e estilos responsivos.
- `tests/report.test.js`: testes de contrato, status, filtros, médias e carregamento.

## Limitações desta versão

Não inclui coletor real na VPS, cron, autenticação, Telegram, alertas ativos nem ações sobre containers. Atualização do frontend é manual, sem polling, e ele ainda não consome a API. A coleta futura deve adaptar seu formato ao contrato v1. Fontes Google são opcionais (há fallback local); ícones e gráficos são empacotados no build. Para histórico de alta frequência, agregue as amostras antes de publicar o JSON, evitando payloads e tabelas excessivos.

Referências da stack: [Vite](https://vite.dev/guide/) e [Chart.js](https://www.chartjs.org/docs/latest/getting-started/).
