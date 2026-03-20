# PFC Emanuel Vieira Tavares — Cronograma e Issues 2026

## Marcos principais

|Marco|Data|
|---|---|
|Entrega do texto para banca — PFC I|08/06/2026|
|Defesa — PFC I|até 20/06/2026|
|Entrega do texto para banca — PFC II|26/11/2026|
|Defesa — PFC II|até 11/12/2026|

## Delimitação das etapas do projeto

```
[Texto do usuário]
        ↓
[Etapa 1 — PLN: Extração de Requisitos]
   Pesquisar modelos e selecionar os mais adequados para o caso.
        ↓
[Etapa 2 — Base de Conhecimento: Grafo + IA]
   Pesquisar bases prontas e definir a melhor forma de conexão com a Etapa 1.
        ↓
[Etapa 3 — Resposta estruturada no terminal]
   Gerar saída legível, comparativa e com justificativa.
```

---

## Divisão de responsabilidades entre PFC I e PFC II

**PFC I** — Revisão, decisões técnicas, protótipo de PLN e modelagem conceitual da base

O PFC I não precisa entregar um sistema funcionando. Ele precisa entregar decisões fundamentadas e o início da implementação. Ao final do PFC I, o trabalho deve ter: o módulo de PLN v1 operacional, a modelagem conceitual da base de conhecimento definida e a especificação da interface entre Etapa 1 e Etapa 2 documentada. Isso garante que o PFC II possa focar inteiramente em implementação e validação, sem decisões de arquitetura em aberto.

**PFC II** — Implementação da base, motor de recomendação, Etapa 3, integração, testes e redação final

---

# Cronograma semanal

## Fevereiro de 2026 — Planejamento e fundação

### Semana 1 — 02/02 a 08/02

- Reunião inicial com orientador.
- Revisão da avaliação do pré-projeto e alinhamento do escopo revisado (sem front-end web).
- Atualização do plano de trabalho.
- **Entrega:** cronograma revisado + escopo delimitado nas três etapas.

### Semana 2 — 09/02 a 15/02

- Levantamento inicial de referências sobre PLN, grafos de conhecimento e sistemas de recomendação.
- Organização da bibliografia em gerenciador (Zotero ou Mendeley).
- **Entrega:** lista comentada com referências iniciais organizadas.

### Semana 3 — 16/02 a 22/02

- Busca de bases públicas, taxonomias e ontologias candidatas para apoiar a base de conhecimento.
- Avaliação preliminar do Stack Overflow Developer Survey como fonte de co-ocorrências de tecnologias.
- **Entrega:** relatório de fontes candidatas com avaliação inicial de viabilidade.

### Semana 4 — 23/02 a 01/03

- Definição do recorte final do problema.
- Especificação do formato de entrada e do padrão mínimo da resposta estruturada no terminal.
- **Entrega:** documento de requisitos do protótipo (o que o sistema recebe e o que devolve).

---

## Março de 2026 — Pesquisa técnica das Etapas 1 e 2 em paralelo

> A partir desta fase, as pesquisas das Etapas 1 e 2 avançam em paralelo no nível conceitual. A escolha de quais requisitos extrair na Etapa 1 depende diretamente da estrutura do grafo da Etapa 2, por isso as duas precisam ser pensadas juntas desde o início.

### Semana 5 — 02/03 a 08/03

- **Etapa 1:** Revisão bibliográfica sobre extração de requisitos a partir de texto livre.
- **Etapa 2:** Aprofundamento na análise das fontes candidatas levantadas na Semana 3.
- **Entrega:** fichamento dos artigos centrais de PLN + avaliação das fontes da Etapa 2.

### Semana 6 — 09/03 a 15/03

- **Etapa 1:** Mapeamento e comparação de abordagens de PLN — regras, embeddings, classificadores e transformers.
- **Etapa 2:** Revisão bibliográfica sobre grafos de conhecimento, knowledge graphs e sistemas de recomendação baseados em grafo.
- **Entrega:** tabela comparativa de abordagens de PLN + síntese sobre grafos de conhecimento.

### Semana 7 — 16/03 a 22/03

- **Etapa 1:** Definição das categorias de requisitos a extrair (desempenho, escala, persistência, integração, domínio etc.).
- **Etapa 2:** Esboço inicial da estrutura do grafo — tipos de nós, tipos de arestas e atributos principais.
- **Entrega:** esquema de categorias de requisitos + esboço conceitual do grafo.

### Semana 8 — 23/03 a 29/03

- **Etapa 1:** Seleção preliminar de modelos e bibliotecas de PLN com base nas semanas anteriores.
- **Etapa 2:** Verificar alinhamento entre as categorias de requisitos definidas e a estrutura do grafo — ajustar o que for necessário.
- **Entrega:** decisão técnica preliminar da Etapa 1 + confirmação de coerência entre Etapa 1 e Etapa 2.

### Semana 9 — 30/03 a 05/04

- Escrita inicial da fundamentação teórica: PLN aplicado a requisitos, grafos de conhecimento e sistemas de recomendação.
- **Entrega:** rascunho parcial da revisão bibliográfica (Cap. 2).

---

## Abril de 2026 — Implementação da Etapa 1 e modelagem conceitual da Etapa 2

### Semana 10 — 06/04 a 12/04

- **Etapa 1:** Preparação do corpus inicial de descrições de projeto em linguagem natural.
- **Etapa 2:** Seleção definitiva das fontes para a base de conhecimento com justificativa técnica.
- **Entrega:** corpus inicial de descrições + fontes da base de conhecimento selecionadas.

### Semana 11 — 13/04 a 19/04

- **Etapa 1:** Implementação do pré-processamento textual — limpeza, normalização e preparação da entrada.
- **Entrega:** módulo de pré-processamento funcional com exemplos de entrada e saída.

### Semana 12 — 20/04 a 26/04

- **Etapa 1:** Implementação da extração preliminar de requisitos — protótipo PLN v0.
- **Etapa 2:** Modelagem conceitual da base de conhecimento — diagrama de nós, arestas e atributos.
- **Entrega:** protótipo PLN v0 + diagrama conceitual do grafo.

### Semana 13 — 27/04 a 03/05

- **Etapa 1:** Testes do protótipo PLN v0 e análise de erros.
- **Etapa 2:** Especificação da interface entre Etapa 1 e Etapa 2 — como o dicionário de requisitos se mapeia sobre o grafo.
- **Entrega:** relatório de erros do PLN + especificação técnica da interface E1 → E2.

---

## Maio de 2026 — Refinamento do PLN e fechamento conceitual da base

### Semana 14 — 04/05 a 10/05

- **Etapa 1:** Ajustes no módulo de PLN com base nos erros da semana anterior.
- **Entrega:** protótipo PLN v1.

### Semana 15 — 11/05 a 17/05

- **Etapa 2:** Consolidação do modelo conceitual da base de conhecimento — revisão do diagrama, validação das relações principais e definição de atributos de cada nó.
- **Entrega:** diagrama conceitual final do grafo, pronto para documentação no PFC I.

### Semana 16 — 18/05 a 24/05

- **Etapa 2:** Revisão e consolidação da especificação técnica da interface E1 → E2.
- Alinhamento com orientador do estado geral do trabalho.
- **Entrega:** especificação técnica E1 → E2 consolidada.

### Semana 17 — 25/05 a 31/05

- Início do fechamento do texto do PFC I — introdução, revisão bibliográfica e metodologia.
- **Entrega:** rascunho do texto do PFC I para revisão.

---

## Junho de 2026 — Entrega e defesa do PFC I

### Semana 18 — 01/06 a 07/06

- Revisão final do texto do PFC I com orientador.
- Ajustes e formatação.
- **Entrega:** versão final do texto para submissão.

### Semana 19 — 08/06 a 14/06

- 🔴 **Entrega formal do texto do PFC I — 08/06/2026.**
- Preparação dos slides da apresentação.
- Ensaio da apresentação.
- **Entrega:** slides e roteiro da apresentação do PFC I.

### Semana 20 — 15/06 a 21/06

- 🎓 **Defesa do PFC I — até 20/06/2026.**
- Registro das observações e exigências da banca.
- **Entrega:** lista de correções e encaminhamentos para o PFC II.

---

## Julho de 2026 — Pós-banca e início da implementação da Etapa 2

### Semana 21 — 22/06 a 28/06

- Incorporação das observações da banca do PFC I.
- Revisão e atualização do plano de trabalho para o PFC II.
- **Entrega:** plano revisado do PFC II.

### Semana 22 — 29/06 a 05/07

- **Etapa 2 — Camada 1:** Construção do seed manual da base — ~40 tecnologias com atributos e relações iniciais validados manualmente.
- **Entrega:** base de conhecimento v0 (seed manual carregado no grafo).

### Semana 23 — 06/07 a 12/07

- **Etapa 2 — Camada 2:** Processamento do Stack Overflow Developer Survey para extrair co-ocorrências reais de tecnologias e popular as arestas com peso estatístico.
- **Entrega:** script de extração + arestas com pesos do SO Survey integradas à base.

### Semana 24 — 13/07 a 19/07

- **Etapa 2 — Camada 3:** Curadoria via LLM — dado um par de tecnologias, o LLM valida e pontua a relação; expandir e enriquecer o grafo existente.
- **Entrega:** script de curadoria via LLM + base de conhecimento v1 com maior cobertura.

### Semana 25 — 20/07 a 26/07

- Definição dos critérios de recomendação: aderência, compatibilidade, curva de aprendizado, popularidade e demais pesos.
- **Entrega:** documento de critérios do motor de recomendação.

### Semana 26 — 27/07 a 02/08

- Definição da abordagem de inferência sobre o grafo — graph traversal, scoring e ranking.
- **Entrega:** arquitetura lógica da Etapa 2.

---

## Agosto de 2026 — Motor de recomendação e integração

### Semana 27 — 03/08 a 09/08

- **Etapa 2:** Implementação do motor de recomendação v0 — dado dicionário de requisitos, retorna tecnologias candidatas com score.
- **Entrega:** motor de recomendação v0 funcional.

### Semana 28 — 10/08 a 16/08

- **Etapa 2:** Testes do motor com casos simples — verificar consistência do ranking e das justificativas.
- **Entrega:** relatório de testes iniciais do motor.

### Semana 29 — 17/08 a 23/08

- **Etapa 2:** Ajuste de pesos, heurísticas e critérios com base nos testes.
- **Entrega:** motor de recomendação v1 com resultados mais consistentes.

### Semana 30 — 24/08 a 30/08

- Integração estável entre Etapa 1 e Etapa 2 — pipeline PLN → base → motor funcionando de ponta a ponta.
- **Entrega:** pipeline E1 + E2 integrado.

### Semana 31 — 31/08 a 06/09

- Documentação técnica da arquitetura implementada até aqui.
- **Entrega:** capítulo de metodologia atualizado.

---

## Setembro de 2026 — Etapa 3 e integração final

### Semana 32 — 07/09 a 13/09

- **Etapa 3:** Definição do formato da resposta no terminal — estrutura, campos obrigatórios, justificativas e alternativas.
- **Entrega:** especificação da resposta textual.

### Semana 33 — 14/09 a 20/09

- **Etapa 3:** Implementação da primeira versão da saída estruturada no terminal.
- **Entrega:** módulo terminal v0.

### Semana 34 — 21/09 a 27/09

- **Etapa 3:** Ajustes para tornar a saída clara, comparativa e interpretável — prós/contras, justificativa baseada no grafo, alternativas.
- **Entrega:** módulo terminal v1.

### Semana 35 — 28/09 a 04/10

- Integração final das três etapas — texto de entrada → PLN → base → motor → terminal.
- **Entrega:** protótipo integrado funcional (sistema v0.1).

---

## Outubro de 2026 — Validação e testes

### Semana 36 — 05/10 a 11/10

- Definição do protocolo de avaliação — métricas de precisão, relevância e estudos de caso.
- **Entrega:** plano de validação detalhado.

### Semana 37 — 12/10 a 18/10

- Execução dos estudos de caso com descrições de projetos variadas.
- **Entrega:** conjunto de resultados experimentais.

### Semana 38 — 19/10 a 25/10

- Validação qualitativa com orientador e especialistas, quando possível.
- **Entrega:** parecer técnico das recomendações + sistema v0.2 refinado.

### Semana 39 — 26/10 a 01/11

- Ajustes finais no sistema com base na avaliação.
- **Entrega:** versão refinada do protótipo (sistema v0.3).

---

## Novembro de 2026 — Redação final

### Semana 40 — 02/11 a 08/11

- Redação do capítulo de desenvolvimento e implementação.
- **Entrega:** capítulo técnico (Etapas 1, 2 e 3) consolidado.

### Semana 41 — 09/11 a 15/11

- Redação do capítulo de resultados e discussão.
- **Entrega:** capítulo de resultados.

### Semana 42 — 16/11 a 22/11

- Redação da conclusão, limitações e trabalhos futuros.
- **Entrega:** versão quase completa do texto.

### Semana 43 — 23/11 a 29/11

- Revisão geral, padronização, figuras, tabelas e referências.
- **Entrega:** 🔴 versão final preliminar do PFC II — entrega até 26/11/2026.

---

## Dezembro de 2026 — Defesa e fechamento

### Semana 44 — 30/11 a 06/12

- Revisão final com orientador.
- Fechamento de anexos e apêndices.
- **Entrega:** versão final para banca do PFC II.

### Semana 45 — 07/12 a 13/12

- Preparação dos slides e ensaio da apresentação final.
- **Entrega:** apresentação final pronta.

### Semana 46 — 14/12 a 20/12 (considerar 11/12)

- 🎓 **Defesa do PFC II.**
- Registro das observações da banca.
- **Entrega:** lista de correções finais.

### Semana 47 — 21/12 a 27/12

- Ajustes pós-banca.
- **Entrega:** versão definitiva corrigida.

---

## Marco sintético por fase

|Fase|Período|Foco|
|---|---|---|
|Planejamento|Fevereiro|Escopo, bibliografia, fontes da Etapa 2, requisitos do sistema|
|Pesquisa técnica|Março|PLN e modelagem conceitual do grafo em paralelo|
|Implementação PLN + Modelagem base|Abril–Maio|PLN v1, diagrama do grafo, interface E1→E2|
|**Entrega PFC I**|Junho|PLN v1 + modelagem conceitual da base + interface E1→E2 documentada|
|Implementação base|Julho|Seed manual + SO Survey + curadoria LLM + motor v0|
|Motor + integração|Agosto|Motor v1 + pipeline E1+E2 integrado|
|Etapa 3 + integração final|Setembro|Terminal v1 + sistema v0.1 completo|
|Validação|Outubro|Testes, estudos de caso, ajustes finais|
|Redação|Novembro|Capítulos de implementação, resultados e conclusão|
|**Entrega PFC II**|Novembro/Dezembro|Texto final entregue até 26/11|
|Defesa|Dezembro|Apresentação e ajustes pós-banca|

---

# Sugestão de colunas para o Kanban

- Backlog
- A fazer
- Em andamento
- Em revisão
- Concluído
- Bloqueado

---

# Issues para o GitHub Kanban

---

## Planejamento e escopo

---

### Issue 1 — Revisar avaliação do pré-projeto e redefinir escopo

**Descrição:** Consolidar as observações da avaliação e recomendações da banca. Ajustar o escopo do trabalho para priorizar bases já validadas, eliminar o front-end web e delimitar claramente as três etapas do sistema.

**Critérios de aceitação:**

- [ ] Etapas 1, 2 e 3 delimitadas e documentadas
- [ ] Escopo alinhado às recomendações da banca (sem front-end)
- [ ] Cronograma-base atualizado

**Labels:** `planejamento` `documentação` `pfc1`

---

### Issue 2 — Definir problema, entrada e saída esperada do sistema

**Descrição:** Delimitar claramente o que o sistema recebe (texto livre do usuário) e o que deve devolver (resposta estruturada no terminal). Especificar o formato mínimo de entrada e o padrão da saída.

**Critérios de aceitação:**

- [ ] Documento de requisitos funcionais do protótipo
- [ ] Formato de entrada descrito com exemplos
- [ ] Formato de saída descrito com estrutura mínima

**Labels:** `planejamento` `requisitos` `pfc1`

---

## Revisão bibliográfica e pesquisa

---

### Issue 3 — Consolidar bibliografia inicial

**Descrição:** Levantar e organizar referências sobre PLN para extração de requisitos, grafos de conhecimento, sistemas de recomendação e integração entre essas áreas. Organizar no gerenciador bibliográfico.

**Critérios de aceitação:**

- [ ] Pelo menos 20 referências relevantes levantadas
- [ ] Referências organizadas no Zotero ou Mendeley
- [ ] Pelo menos um conjunto-base de artigos fichados
- [ ] Síntese comparativa ou tabela das referências centrais

**Labels:** `pesquisa` `pln` `grafo` `pfc1`

---

### Issue 4 — Identificar bases prontas e fontes públicas para a base de conhecimento

**Descrição:** Buscar bases, taxonomias, ontologias e fontes de dados candidatas para compor a base de conhecimento. Incluir avaliação do Stack Overflow Developer Survey como fonte de co-ocorrências reais de tecnologias.

**Critérios de aceitação:**

- [ ] Relatório com fontes candidatas e justificativa de viabilidade
- [ ] Stack Overflow Developer Survey avaliado como fonte de arestas do grafo
- [ ] Fontes ranqueadas por critérios de acessibilidade, cobertura e qualidade

**Labels:** `pesquisa` `dados` `grafo` `pfc1`

---

## Etapa 1 — PLN: Extração de Requisitos

---

### Issue 5 — Mapear e comparar abordagens de PLN para extração de requisitos

**Descrição:** Revisar a literatura sobre extração de requisitos a partir de texto livre. Comparar abordagens — regras, embeddings, classificadores e transformers — com base em critérios de precisão, custo computacional e facilidade de integração.

**Critérios de aceitação:**

- [ ] Fichamento de pelo menos 5 artigos centrais
- [ ] Tabela comparativa das abordagens
- [ ] Critérios de seleção definidos e documentados

**Labels:** `pesquisa` `pln` `pfc1`

---

### Issue 6 — Definir taxonomia de requisitos a extrair

**Descrição:** Especificar quais categorias de requisitos serão identificadas no texto do usuário — por exemplo: tipo de projeto, domínio de negócio, requisitos de desempenho, escala, persistência e integração. Garantir coerência com a estrutura do grafo da Etapa 2.

**Critérios de aceitação:**

- [ ] Taxonomia de requisitos documentada
- [ ] Exemplos anotados para cada categoria
- [ ] Alinhamento verificado com a modelagem do grafo da Etapa 2

**Labels:** `pln` `requisitos` `pfc1`

---

### Issue 7 — Selecionar modelo e biblioteca para a Etapa 1

**Descrição:** Escolher as ferramentas mais adequadas para o pipeline de PLN com base nas comparações das Issues 5 e 6. Documentar a decisão com justificativa técnica.

**Critérios de aceitação:**

- [ ] Stack selecionada (ex.: spaCy, HuggingFace, Mistral via Ollama ou combinação)
- [ ] Justificativa técnica registrada
- [ ] Decisão validada com orientador

**Labels:** `pln` `arquitetura` `pfc1`

---

### Issue 8 — Montar corpus inicial de descrições de projeto

**Descrição:** Construir conjunto de exemplos de entradas em linguagem natural para desenvolvimento e teste do módulo de PLN. Incluir casos simples, intermediários e com ambiguidade.

**Critérios de aceitação:**

- [ ] Corpus inicial versionado no repositório
- [ ] Casos simples e intermediários incluídos
- [ ] Exemplos anotados com os requisitos esperados para cada entrada

**Labels:** `dados` `pln` `pfc1`

---

### Issue 9 — Implementar pré-processamento textual

**Descrição:** Implementar o módulo de limpeza, normalização e preparação do texto de entrada antes da extração de requisitos.

**Critérios de aceitação:**

- [ ] Módulo de pré-processamento v0 implementado
- [ ] Exemplos executando sem erro
- [ ] Saída normalizada compatível com a entrada do extrator de requisitos

**Labels:** `desenvolvimento` `pln` `pfc1`

---

### Issue 10 — Implementar e refinar o módulo de PLN (v0 → v1)

**Descrição:** Desenvolver o pipeline de extração de requisitos desde o protótipo inicial até uma versão estável. Inclui a implementação do protótipo, os testes com o corpus, a análise de erros e os ajustes necessários.

**Critérios de aceitação:**

- [ ] Protótipo PLN v0 funcional para casos simples
- [ ] Relatório de erros e ambiguidades documentado
- [ ] Ajustes aplicados com base nos erros encontrados
- [ ] Módulo PLN v1 com saída interpretável e estável

**Labels:** `desenvolvimento` `testes` `pln` `pfc1`

---

## Etapa 2 — Base de Conhecimento: Grafo + IA

---

### Issue 11 — Selecionar fontes e modelar conceitualmente a base de conhecimento

**Descrição:** Selecionar a melhor combinação de fontes para representar tecnologias, atributos e relações. Definir nós, tipos de arestas, atributos e critérios de compatibilidade no modelo conceitual do grafo.

**Critérios de aceitação:**

- [ ] Comparativo de bases e fontes concluído
- [ ] Fontes selecionadas com justificativa
- [ ] Diagrama conceitual do grafo com nós, arestas e atributos principais
- [ ] Relações principais mapeadas e nomeadas (ex.: `COMPATIVEL_COM`, `IDEAL_PARA`, `REQUER`)

**Labels:** `pesquisa` `grafo` `arquitetura` `pfc1`

---

### Issue 12 — Especificar a interface entre Etapa 1 e Etapa 2

**Descrição:** Definir como os requisitos extraídos pelo módulo de PLN serão conectados à base de conhecimento. Documentar o contrato entre as duas etapas — formato do dicionário de requisitos e como ele se mapeia sobre o grafo.

**Critérios de aceitação:**

- [ ] Formato do dicionário de saída da Etapa 1 definido
- [ ] Mapeamento entre categorias de requisitos e atributos do grafo documentado
- [ ] Especificação técnica da interface E1 → E2 revisada com orientador

**Labels:** `integração` `pln` `grafo` `pfc1`

---

### Issue 13 — Construir a base de conhecimento v0 — seed manual

**Descrição:** Implementar a primeira camada da base com um conjunto inicial de ~40 tecnologias, seus atributos e relações validados manualmente. Esta é a fundação curada da base.

**Critérios de aceitação:**

- [ ] Seed com ~40 tecnologias (linguagens, frameworks, bancos e infra)
- [ ] Atributos de cada nó preenchidos (curva de aprendizado, performance, domínio ideal etc.)
- [ ] Script de carga do seed no banco de grafo funcional
- [ ] Base v0 disponível e versionada

**Labels:** `desenvolvimento` `grafo` `pfc2`

---

### Issue 14 — Expandir a base com dados públicos — Stack Overflow Survey

**Descrição:** Processar o Stack Overflow Developer Survey para extrair co-ocorrências reais de tecnologias e popular as arestas da base com peso estatístico. Esta é a segunda camada de dados da base, que responde à crítica da banca por bases validadas.

**Critérios de aceitação:**

- [ ] Script de extração das co-ocorrências implementado
- [ ] Arestas com pesos estatísticos integradas à base
- [ ] Base de conhecimento v1 com cobertura ampliada e rastreável

**Labels:** `desenvolvimento` `dados` `grafo` `pfc2`

---

### Issue 15 — Enriquecer a base via curadoria com LLM

**Descrição:** Usar um LLM como curador interno para validar e pontuar relações entre pares de tecnologias. O LLM não recomenda diretamente ao usuário — ele enriquece o grafo durante o desenvolvimento, garantindo coerência das arestas.

**Critérios de aceitação:**

- [ ] Script de curadoria via LLM implementado
- [ ] Relações validadas ou ajustadas pelo LLM registradas na base
- [ ] Base de conhecimento v2 com maior consistência e cobertura

**Labels:** `desenvolvimento` `grafo` `ia` `pfc2`

---

### Issue 16 — Definir critérios e arquitetura do motor de recomendação

**Descrição:** Estabelecer os critérios de recomendação (aderência, compatibilidade, curva de aprendizado, popularidade etc.) e a abordagem de inferência sobre o grafo — graph traversal, scoring por similaridade e ranking de stacks.

**Critérios de aceitação:**

- [ ] Critérios de recomendação documentados com pesos iniciais
- [ ] Estratégia de ranking definida
- [ ] Arquitetura lógica da Etapa 2 documentada

**Labels:** `arquitetura` `recomendacao` `pfc2`

---

### Issue 17 — Implementar e refinar o motor de recomendação (v0 → v1)

**Descrição:** Desenvolver o mecanismo de inferência sobre a base desde o protótipo inicial até uma versão estável. Inclui implementação, testes com casos simples e ajuste de pesos e heurísticas.

**Critérios de aceitação:**

- [ ] Motor v0: dado dicionário de requisitos, retorna tecnologias candidatas com score
- [ ] Relatório de testes com casos simples documentado
- [ ] Pesos, filtros e heurísticas ajustados
- [ ] Motor v1 com ranking consistente e justificativas rastreáveis

**Labels:** `desenvolvimento` `testes` `recomendacao` `pfc2`

---

## Integração

---

### Issue 18 — Integrar Etapa 1 e Etapa 2

**Descrição:** Unificar o pipeline das duas primeiras etapas — texto do usuário → extração de requisitos → consulta à base → ranking de tecnologias.

**Critérios de aceitação:**

- [ ] Pipeline E1 + E2 executando de ponta a ponta
- [ ] Casos simples rodando sem erro
- [ ] Saída intermediária (requisitos extraídos) verificável para depuração

**Labels:** `integração` `pln` `grafo` `recomendacao` `pfc2`

---

## Etapa 3 — Resposta estruturada no terminal

---

### Issue 19 — Especificar o formato da resposta no terminal

**Descrição:** Definir como apresentar as tecnologias sugeridas, justificativas baseadas no grafo, alternativas e comparações. A saída deve ser legível, comparativa e auditável.

**Critérios de aceitação:**

- [ ] Estrutura de campos da resposta definida
- [ ] Exemplo de saída-padrão documentado
- [ ] Justificativas rastreáveis às arestas do grafo

**Labels:** `terminal` `requisitos` `pfc2`

---

### Issue 20 — Implementar e refinar o módulo de resposta no terminal (v0 → v1)

**Descrição:** Construir a saída estruturada no terminal desde o protótipo inicial até uma versão clara, comparativa e robusta.

**Critérios de aceitação:**

- [ ] Módulo terminal v0 funcional
- [ ] Saída apresenta stacks ranqueadas com score e justificativa
- [ ] Formato estável e legível — prós/contras, casos de uso ideais, alternativas
- [ ] Módulo terminal v1 consolidado

**Labels:** `desenvolvimento` `terminal` `pfc2`

---

### Issue 21 — Integrar as três etapas — sistema completo

**Descrição:** Unificar o pipeline completo: texto de entrada → PLN → base + motor → resposta no terminal.

**Critérios de aceitação:**

- [ ] Execução de ponta a ponta funcional (sistema v0.1)
- [ ] Casos simples, intermediários e complexos rodando
- [ ] Saída final verificável e interpretável

**Labels:** `integração` `pln` `grafo` `recomendacao` `terminal` `pfc2`

---

## Validação

---

### Issue 22 — Definir protocolo de validação e estudos de caso

**Descrição:** Definir métricas de avaliação, critérios de qualidade das recomendações, estudos de caso a executar e forma de análise dos resultados.

**Critérios de aceitação:**

- [ ] Métricas de precisão e relevância definidas
- [ ] Conjunto de estudos de caso especificado
- [ ] Protocolo de coleta de dados documentado

**Labels:** `validacao` `testes` `pfc2`

---

### Issue 23 — Executar estudos de caso e validar o protótipo

**Descrição:** Aplicar o sistema em diferentes descrições de projeto, analisar resultados, coletar parecer qualitativo com orientador e especialistas quando possível, e aplicar melhorias.

**Critérios de aceitação:**

- [ ] Estudos de caso executados e resultados registrados
- [ ] Parecer qualitativo das recomendações documentado
- [ ] Sistema refinado com base na avaliação (v0.3)
- [ ] Relatório experimental consolidado

**Labels:** `validacao` `testes` `pfc2`

---

## Documentação e apresentação

---

### Issue 24 — Redigir texto do PFC I

**Descrição:** Consolidar introdução, revisão bibliográfica, metodologia e estado atual do sistema — PLN v1, modelagem conceitual da base e especificação da interface E1→E2.

**Critérios de aceitação:**

- [ ] Capítulos de introdução e revisão bibliográfica finalizados
- [ ] Metodologia documentada com decisões técnicas justificadas
- [ ] Versão final do texto pronta até 08/06/2026

**Labels:** `documentação` `pfc1` `entrega`

---

### Issue 25 — Preparar apresentação e realizar defesa do PFC I

**Descrição:** Criar a apresentação, ensaiar e realizar a defesa do PFC I no prazo.

**Critérios de aceitação:**

- [ ] Slides prontos antes da defesa
- [ ] Ensaio realizado com orientador
- [ ] Defesa realizada até 20/06/2026
- [ ] Observações da banca registradas

**Labels:** `apresentação` `pfc1`

---

### Issue 26 — Incorporar ajustes apontados na banca do PFC I

**Descrição:** Registrar as observações da banca e adaptar o plano e o texto para o PFC II.

**Critérios de aceitação:**

- [ ] Lista de correções organizada por prioridade
- [ ] Plano do PFC II revisado com os encaminhamentos da banca

**Labels:** `revisão` `planejamento` `pfc2`

---

### Issue 27 — Redigir capítulo de desenvolvimento e implementação

**Descrição:** Documentar tecnicamente a implementação das três etapas — módulo de PLN, base de conhecimento (seed, SO Survey, curadoria LLM, motor) e resposta no terminal.

**Critérios de aceitação:**

- [ ] Arquitetura do sistema descrita com diagrama
- [ ] Decisões de implementação justificadas
- [ ] Capítulo técnico revisado com orientador

**Labels:** `documentação` `pfc2`

---

### Issue 28 — Redigir capítulo de resultados e discussão

**Descrição:** Apresentar os resultados dos estudos de caso, analisar a qualidade das recomendações e discutir limitações e pontos de melhoria.

**Critérios de aceitação:**

- [ ] Resultados experimentais apresentados com métricas
- [ ] Discussão sobre limitações do sistema
- [ ] Capítulo revisado com orientador

**Labels:** `documentação` `pfc2`

---

### Issue 29 — Redigir conclusão, limitações e trabalhos futuros

**Descrição:** Fechar o trabalho com uma síntese dos resultados, das contribuições do projeto e das direções de evolução futura.

**Critérios de aceitação:**

- [ ] Conclusão alinhada com os objetivos definidos no início do trabalho
- [ ] Limitações do sistema identificadas honestamente
- [ ] Pelo menos três direções de trabalho futuro descritas

**Labels:** `documentação` `pfc2`

---

### Issue 30 — Revisão geral, formatação e fechamento do texto do PFC II

**Descrição:** Revisar o texto completo — coerência, padronização ABNT, figuras, tabelas e referências. Fechar o documento para entrega formal.

**Critérios de aceitação:**

- [ ] Texto revisado e padronizado
- [ ] Referências completas e formatadas
- [ ] Versão final entregue até 26/11/2026

**Labels:** `documentação` `pfc2` `entrega`

---

### Issue 31 — Preparar apresentação e realizar defesa do PFC II

**Descrição:** Criar a apresentação final, ensaiar e realizar a defesa do PFC II no prazo.

**Critérios de aceitação:**

- [ ] Slides finais prontos
- [ ] Pelo menos um ensaio completo realizado
- [ ] Defesa realizada até 11/12/2026
- [ ] Observações finais da banca registradas

**Labels:** `apresentação` `pfc2` `entrega`
