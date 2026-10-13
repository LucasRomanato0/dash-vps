# Instruções para agentes de código

## Objetivo
Este repositório implementa o Dash VPS: painel para visualizar métricas de uma VPS, com frontend, API opcional, banco SQLite e coletor.

## Fluxo guiado por especificações (SDD)
Para mudanças de comportamento, comece ou atualize uma especificação em `docs/specs/` antes de implementar. Para mudanças que alterem riscos, dados, autenticação ou exposição de rede, revise também `docs/security/`. Registre decisões arquiteturais duradouras em `docs/adr/`.

Antes de codificar:
1. Leia `docs/README.md` e os documentos relevantes ao escopo.
2. Confira o comportamento atual no código; documentação não substitui validação do código.
3. Identifique requisitos, limites, erros esperados e critérios de aceite.

Durante a implementação:
- Mantenha a alteração dentro do escopo aprovado pela especificação.
- Preserve compatibilidade de API e do contrato de relatório; documente mudanças incompatíveis.
- Nunca exponha tokens, credenciais ou dados sensíveis no frontend, fixtures, logs ou documentos.
- Evite adicionar dependências sem necessidade justificada.

Ao concluir:
- Atualize especificações e documentação afetadas junto com o código.
- Resuma arquivos alterados, decisões, validações executadas e limitações.
- Não afirme que executou validações que não foram executadas.

## Mapa do projeto
- `src/`: frontend Vite/JavaScript, gráficos e validação/carregamento de relatórios.
- `backend/app/`: API FastAPI, schemas, rotas, persistência e configuração.
- `backend/collector/`: coleta e envio de métricas da VPS.
- `tests/` e `backend/tests/`: testes frontend/contratos e backend.
- `docs/`: especificações, segurança, decisões e modelos de documento.

## Comandos úteis
Veja `README.md` para requisitos e execução. Comandos existentes incluem `npm run lint`, `npm test`, `npm run build` e, no backend, `pytest`.
