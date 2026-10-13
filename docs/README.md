# Documentação de engenharia

Esta pasta organiza o desenvolvimento guiado por especificações (SDD) do Dash VPS. `AGENTS.md` contém as instruções operacionais para agentes de código; os documentos daqui registram comportamento esperado, segurança e decisões.

## Índice

- `specs/SPEC-001-dashboard.md` — comportamento do painel e contrato de dados que ele consome.
- `specs/SPEC-002-metrics-api.md` — ingestão, consulta e persistência de métricas.
- `security/SEC-001-security-baseline.md` — ativos, fronteiras de confiança e requisitos mínimos de segurança.
- `adr/ADR-0001-documentation-architecture.md` — organização documental e fluxo SDD adotados.
- `templates/` — modelos para novas SPECs, SECs e ADRs.

## Convenções

- SPEC descreve comportamento e critérios observáveis, sem prescrever detalhes internos desnecessários.
- SEC registra ativos, fronteiras, ameaças relevantes e controles verificáveis.
- ADR registra uma decisão duradoura, seu contexto, alternativas e consequências. ADRs aceitos não são reescritos; decisões posteriores criam um novo ADR que os substitui.
- IDs são sequenciais e estáveis: `SPEC-NNN`, `SEC-NNN`, `ADR-NNNN`.
- Use estado `Rascunho`, `Aceito`, `Substituído` ou `Arquivado`, com data e responsável quando conhecidos. Não invente responsáveis.
- Cada requisito recebe um identificador estável (`FR-`, `NFR-`, `SEC-`) e critérios de aceite testáveis.
- Código é a fonte do comportamento atual; SPEC é a fonte do comportamento pretendido. Divergências devem ser resolvidas atualizando código ou especificação.
- Vincule documentos relacionados e, quando útil, os caminhos de código/teste que implementam ou verificam os requisitos.

## Ciclo de mudança

1. Delimitar a mudança e seus usuários/sistemas afetados.
2. Criar ou atualizar a SPEC; avaliar impacto de segurança e necessidade de SEC.
3. Registrar ADR quando houver decisão arquitetural relevante ou difícil de reverter.
4. Implementar e validar os critérios de aceite.
5. Atualizar documentação e registrar lacunas conhecidas.
