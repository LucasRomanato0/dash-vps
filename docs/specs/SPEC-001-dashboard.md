# SPEC-001 — Dashboard e contrato de relatório

- Estado: Aceito
- Data: 2026-10-13
- Escopo: `src/`, contrato de relatório v1 e apresentação de métricas
- Relacionados: `SPEC-002`, `SEC-001`

## Objetivo
Apresentar de forma responsiva e acessível o estado e o histórico de uma VPS a partir de uma fonte configurada, mantendo explícita a diferença entre dados reais e demonstração.

## Atores e contexto
- Operador: consulta saúde, recursos, serviços, containers, alertas e histórico.
- Fonte de dados: API JSON configurada, relatório JSON estático ou gerador demonstrativo.
- Navegador: renderiza a interface; não executa probes de serviços nem recebe segredos de ingestão.

## Requisitos funcionais

- FR-001: O painel deve carregar a API configurada por `VITE_API_URL`; na ausência dela, pode carregar o JSON de `VITE_REPORT_URL`; na ausência de ambas, deve identificar claramente o modo demonstrativo.
- FR-002: Uma falha na fonte real não pode ser substituída silenciosamente por dados demonstrativos. Após uma leitura válida, a última leitura pode permanecer visível com aviso.
- FR-003: O painel deve exibir hostname, última coleta, uso de CPU/RAM/disco, load, uptime, serviços, containers, alertas e containers problemáticos quando fornecidos.
- FR-004: O usuário deve poder selecionar períodos de 24 horas, 7 dias e 30 dias. O período termina em `collectedAt`; amostras faltantes não são inventadas nem interpoladas.
- FR-005: Gráficos devem oferecer consulta dos valores e alternativa tabular acessível por teclado/leitor de tela.
- FR-006: A preferência de tema claro/escuro deve persistir localmente quando o armazenamento do navegador estiver disponível.
- FR-007: Datas, números e percentuais devem ser apresentados em pt-BR e horários no fuso do navegador.

## Requisitos de qualidade

- NFR-001: Layout responsivo para telas estreitas e largas.
- NFR-002: Conteúdo textual vindo de fontes externas deve ser escapado antes de inserção no DOM.
- NFR-003: Carregamentos remotos devem ter timeout e estados de erro compreensíveis.
- NFR-004: O frontend deve continuar publicável como conteúdo estático, sem exigir backend.

## Contrato de dados
O contrato v1 é descrito no README e validado em `src/data/report.js`. Os campos estruturais incluem versão, hostname, instante de coleta, host, histórico, serviços, alertas e containers problemáticos. Histórico em ordem cronológica estrita; métricas percentuais entre 0 e 100; contagens inteiras não negativas; timestamps com fuso e não posteriores à coleta.

## Critérios de aceite

- CA-001: A interface identifica modo demonstrativo quando não há fonte configurada.
- CA-002: Fonte real inválida/indisponível produz aviso/estado de erro e não troca para demonstração.
- CA-003: Filtros alteram os dados agregados sem criar amostras inexistentes.
- CA-004: Textos externos não são interpretados como HTML executável.
- CA-005: Controles principais funcionam via teclado e exibem rótulos acessíveis.

## Questões em aberto
- Confirmar se os requisitos e limiares de saúde descritos no README representam o comportamento desejado de produto.
- Definir política de retenção/agregação do histórico caso o volume cresça.
