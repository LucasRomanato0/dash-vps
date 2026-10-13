# ADR-0001 — Organização documental guiada por especificações

- Estado: Aceito
- Data: 2026-10-13
- Decisores: não registrados

## Contexto
O projeto possui frontend, API, coletor e implantação documentados principalmente no README. Mudanças precisam de requisitos verificáveis, controles de segurança rastreáveis e decisões arquiteturais consultáveis por agentes e pessoas.

## Decisão
Adotar documentação SDD em Markdown no repositório: `AGENTS.md` para instruções de trabalho; `docs/specs/` para comportamento e critérios de aceite; `docs/security/` para requisitos e riscos; `docs/adr/` para decisões; `docs/templates/` para novos documentos. Mudanças comportamentais começam pela SPEC relacionada. Alterações de segurança revisam SEC; decisões duradouras geram ADR.

## Alternativas consideradas
- Manter toda documentação no README: simples, mas mistura uso, requisitos, segurança e decisões.
- Adotar ferramenta externa de requisitos: adiciona serviço e fluxo de manutenção para um projeto pequeno.
- Criar documentos separados sem convenções: liberdade inicial, mas baixo rastreamento e consistência.

## Consequências
- O repositório passa a manter requisitos versionados junto do código.
- Documentação precisa ser atualizada junto das mudanças.
- As SPECs iniciais são rascunhos baseados no comportamento documentado e observado; devem ser confirmadas conforme o produto evoluir.
