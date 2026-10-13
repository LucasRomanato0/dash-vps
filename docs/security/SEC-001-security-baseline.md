# SEC-001 — Baseline de segurança

- Estado: Aceito
- Data: 2026-10-13
- Escopo: frontend, API FastAPI, SQLite, coletor e deployment
- Relacionados: `SPEC-001`, `SPEC-002`

## Ativos
- Token de ingestão e configuração de ambiente.
- Métricas e metadados do host, serviços e containers.
- Banco SQLite e volume persistente.
- Integridade/disponibilidade do dashboard e API.

## Fronteiras de confiança
1. VPS/coletor para API pela rede: payload não confiável até autenticação e validação.
2. API para banco local: processo da aplicação e permissões do volume.
3. Fonte de dados para navegador: dados são públicos para qualquer visitante do painel.
4. Build/deploy: variáveis `VITE_*` são incorporadas ao bundle e são públicas.
5. Hermes container para coletor host via SSH: a credencial deve permitir somente acionar o comando fixo de coleta.

## Requisitos de segurança

- SEC-001: Proteger `POST /api/v1/metrics` com token Bearer de alta entropia; não registrar nem retornar o token.
- SEC-002: Falhar fechado na ingestão se o token não estiver configurado.
- SEC-003: Não incluir segredos em JSON servido ao navegador, relatório estático, erros, logs, repositório ou imagens de build.
- SEC-004: Validar tipos, intervalos e estrutura dos payloads antes de persistir.
- SEC-005: Restringir CORS a origens explícitas quando a API for acessada de outra origem.
- SEC-006: Limitar timeouts de chamadas externas e dados de diagnóstico; evitar incluir URLs/configurações sensíveis em mensagens.
- SEC-007: Proteger arquivo de ambiente do coletor e volume SQLite com permissões mínimas necessárias.
- SEC-008: Escapar conteúdo externo antes de renderizar na interface.
- SEC-009: Servir tráfego externo com HTTPS na infraestrutura de deploy.
- SEC-010: A chave SSH do Hermes deve executar somente o comando fixo do coletor, sem shell interativo, PTY ou encaminhamento de portas.
- SEC-011: O token de ingestão deve permanecer no ambiente protegido do coletor no host e não deve ser exposto ao contexto conversacional do Hermes, ao frontend ou aos logs.

## Ameaças e mitigação

| Ameaça | Mitigação atual/documentada | Lacuna a avaliar |
|---|---|---|
| Ingestão não autorizada | Bearer token obrigatório | Rotação e revogação não implementadas |
| Exposição acidental de segredo | Separação de `VITE_*` e segredo backend | Revisar pipeline e logs do deploy |
| Payload malicioso | Schemas e escape no frontend | Definir limites de tamanho/request |
| Exposição de métricas | Relatório público sem credenciais | Definir se hostname, região e serviços podem ser públicos |
| Abuso de probes do coletor | URLs administrativas configuradas localmente e timeout | Avaliar risco de SSRF conforme modelo de configuração |
| Comprometimento do Hermes | Chave SSH restrita e token fora do container Hermes | Configurar comando forçado, permissões do arquivo e acesso mínimo ao Docker |

## Critérios de verificação
- Buscar segredos em payloads/logs e confirmar que valores de `VITE_*` não incluem token.
- Confirmar autorização, rejeição de payloads inválidos e comportamento de CORS.
- Confirmar que conteúdo de relatório não executa HTML/script na UI.
- Confirmar HTTPS e permissões do ambiente/volume na implantação.
- Confirmar que a chave SSH do Hermes só executa o coletor e que o token não aparece no container, saída do comando ou logs.

## Fora de escopo atual
Rotação automatizada de tokens, alertas ativos, autorização por usuário e proteção contra abuso em escala não estão implementadas; considerar antes de expor ingestão à Internet sem controles de infraestrutura adicionais.
