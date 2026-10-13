# SPEC-002 — API de métricas e coletor

- Estado: Aceito
- Data: 2026-10-13
- Escopo: `backend/app/`, `backend/collector/`, integração frontend/API
- Relacionados: `SPEC-001`, `SEC-001`

## Objetivo
Receber snapshots autenticados do coletor, persistir histórico de métricas e fornecer dados ao dashboard.

## Requisitos funcionais

- FR-001: `GET /api/v1/health` deve informar disponibilidade sem exigir token.
- FR-002: `POST /api/v1/metrics` deve exigir `Authorization: Bearer <token>` e retornar `201` com identificador e instante persistidos em caso de sucesso.
- FR-003: A ingestão deve falhar de forma segura com `503` quando o token de ingestão não estiver configurado e `401` para autorização ausente/inválida.
- FR-004: Payloads inválidos ou com campos desconhecidos devem ser rejeitados com `422` e localização do erro.
- FR-005: Campos escalares consultáveis devem ser armazenados em colunas; estruturas opcionais devem ser preservadas como JSON.
- FR-006: O coletor deve suportar `--dry-run`, coletando e imprimindo payload sem transmiti-lo.
- FR-007: O coletor deve obter métricas do host, containers Docker e probes de serviços configurados; indisponibilidade opcional não deve descartar métricas do host.
- FR-008: A API deve fornecer ao frontend dados compatíveis com o contrato documentado em `SPEC-001`.
- FR-009: Cada snapshot enviado diariamente pelo Hermes deve ser validado e persistido pelo fluxo padrão de ingestão.
- FR-010: A API não deve ser responsável por agendar o Hermes nem enviar mensagens ao Telegram.
- FR-011: Hermes deve acionar o coletor do host por comando SSH restrito e consultar o dashboard para obter os dados do resumo.
## Integração diária com Hermes

Hermes é o orquestrador diário, executado na mesma VPS. Em cada execução, obtém um snapshot das métricas principais da VPS e o envia autenticado para `POST /api/v1/metrics`. A API valida e persiste o snapshot; ela não inicia o coletor nem agenda execuções.

Hermes usa o snapshot coletado para preparar o resumo diário. A entrega via Telegram pertence ao Hermes e fica fora do escopo desta API. `GET /api/v1/dashboard?period=24h|7d|30d` é uma consulta somente leitura que retorna os dados em JSON; não gera um resumo textual.

Hermes roda em um container próprio e não acessa o host automaticamente. Para coletar a VPS, ele usa uma chave SSH dedicada e restrita para acionar um comando fixo no host. Esse comando executa `backend/collector/collect.py` com a configuração protegida no host e envia o snapshot para `POST /api/v1/metrics`. Depois, Hermes consulta `GET /api/v1/dashboard?period=24h` para preparar o resumo. O token de ingestão permanece no ambiente protegido do coletor no host. A API não gera texto nem envia Telegram.

## Requisitos de qualidade

- NFR-001: Inicialização/migração do SQLite deve preservar dados existentes.
- NFR-002: A API deve limitar e validar os dados de entrada conforme schemas.
- NFR-003: O token é exclusivo do coletor/backend e nunca deve ser compilado em variáveis `VITE_*`.
- NFR-004: Configuração de CORS deve exigir origens explícitas; curingas não são aceitos.

## Critérios de aceite

- CA-001: Health responde sem token e informa o estado de banco previsto.
- CA-002: Ingestão válida autenticada persiste snapshot e retorna `201`.
- CA-003: Token ausente/inválido e token não configurado produzem os status definidos sem registrar o segredo.
- CA-004: Payload fora do contrato é rejeitado sem persistência parcial.
- CA-005: `--dry-run` não faz requisição de rede para a API.
- CA-006: Reinicialização do backend mantém snapshots existentes.
- CA-007: Depois de uma ingestão válida do Hermes, a próxima consulta do dashboard retorna o snapshot como dado mais recente.
- CA-008: A coleta de métricas e containers representa a VPS host, não somente o container do dashboard.

## Questões em aberto
- Definir retenção e limites de histórico no SQLite.
- Formalizar garantias de timeout/reintento e idempotência do coletor.
