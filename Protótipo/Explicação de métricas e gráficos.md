# Explicação Completa das Métricas e Gráficos do Benchmark

## Contexto do Experimento

O benchmark avaliou **3 modelos de linguagem (LLMs)** executados localmente via Ollama:

| Modelo | Descrição |
|--------|-----------|
| **qwen2.5** | Modelo da Alibaba |
| **llama3** | Modelo da Meta |
| **deepseek-r1:8b** | Modelo da DeepSeek (8 bilhões de parâmetros) |

Cada modelo recebeu **5 entradas de texto** (casos de teste) simulando descrições de projetos de software feitas por um usuário leigo. Cada entrada foi repetida **30 vezes** para o mesmo modelo, totalizando **450 execuções** (3 modelos × 5 entradas × 30 repetições).

### As 5 entradas utilizadas

| Caso | Descrição resumida |
|------|-------------------|
| 1 | Sistema de lista de tarefas web (entrada curta e simples) |
| 2 | Aplicativo mobile de badminton para ensino de Educação Física |
| 3 | Sistema de gestão para clínicas médicas (web, dados sensíveis) |
| 4 | Controle de horas complementares acadêmicas (web) |
| 5 | Jogo da memória desktop com sistemas distribuídos e middleware |

### O que o modelo deve responder

Para cada entrada, o modelo deve retornar um JSON com **12 atributos** que classificam requisitos do projeto:

```
tipo_projeto, dominio_negocio, persistencia, escala, integracao,
arquitetura_esperada, experiencia_usuario, requisitos_seguranca,
ambiente_implantacao, maturidade_equipe, tipo_autenticacao, ciclo_desenvolvimento
```

Cada atributo aceita apenas valores de um conjunto pré-definido (por exemplo, `tipo_projeto` pode ser `web`, `mobile`, `desktop`, `api`, `embarcado` ou `hibrido`).

### O gabarito

Para medir se o modelo acertou, existe um **gabarito** (`gabarito_pessoal_requisitos.json`) com as respostas corretas esperadas para cada uma das 5 entradas. O gabarito foi criado manualmente pelo avaliador.

---

## Parte 1 — Métricas do `resumo_metricas.txt`

Estas métricas avaliam **desempenho operacional**: velocidade, confiabilidade estrutural e reprodutibilidade.

---

### 1.1 Métricas de Tempo (Latência)

Todas medem o tempo que o modelo levou para processar a entrada e gerar a resposta, em milissegundos (ms).

#### Tempo Médio

**O que é:** A média aritmética dos tempos de todas as execuções.

**Fórmula:**

```
Tempo Médio = (t₁ + t₂ + ... + tₙ) / n
```

Onde `t₁, t₂, ..., tₙ` são os tempos de cada execução e `n` é o total de execuções.

**Para que serve:** Dá uma visão geral da velocidade do modelo. Um tempo médio menor indica que o modelo responde mais rápido em geral.

**Exemplo dos dados:** O deepseek-r1:8b tem tempo médio consolidado de ~19.550ms (~19,5s), enquanto o qwen2.5 tem ~27.463ms (~27,5s). Isso significa que o deepseek é, em média, **40% mais rápido**.

---

#### Tempo Mediano

**O que é:** O valor do meio quando todos os tempos são ordenados do menor para o maior. Metade das execuções foram mais rápidas que esse valor, e metade foram mais lentas.

**Fórmula:**

```
Se n é ímpar:  Mediana = valor na posição (n+1)/2
Se n é par:    Mediana = média dos valores nas posições n/2 e (n/2)+1
```

**Para que serve:** A mediana é mais resistente a valores extremos (outliers) do que a média. Se um modelo teve uma execução muito lenta (um pico de lentidão), a média sobe bastante, mas a mediana quase não muda. Portanto, a mediana representa melhor o **comportamento típico** do modelo.

**Quando a mediana difere muito da média:** Significa que existem outliers. Exemplo: o llama3 tem tempo médio de 24.720ms, mas mediano de 24.041ms. Essa diferença relativamente pequena sugere poucos outliers. Já se houvesse uma diferença grande, indicaria execuções isoladas muito lentas.

---

#### Tempo P95 (Percentil 95)

**O que é:** O valor abaixo do qual estão 95% das execuções. Em outras palavras, apenas 5% das execuções demoraram mais que este valor.

**Fórmula (interpolação linear):**

```
posição = (n - 1) × 0.95
P95 = valor[piso(posição)] + fração × (valor[teto(posição)] - valor[piso(posição)])
```

**Para que serve:** Mede o pior caso "realista". Se o P95 é 29s, significa que em 95% das vezes o modelo responde em até 29s. Apenas 5% das vezes ele demora mais que isso. É uma métrica muito usada em engenharia de software para garantir que o sistema atende a padrões de tempo aceitáveis.

---

#### Tempo Mínimo e Tempo Máximo

**O que são:** Simplesmente a execução mais rápida e a mais lenta registradas.

**Para que servem:** O mínimo mostra o melhor cenário possível. O máximo revela se houve algum pico de lentidão extremo. Exemplo: o llama3 teve um máximo de 37.868ms (quase 38s) no caso 1, enquanto os outros ficaram em torno de 27-30s — isso indica um outlier.

---

### 1.2 Métricas de Confiabilidade Estrutural

Estas métricas avaliam se a resposta do modelo é **estruturalmente válida**, independentemente de estar certa ou errada.

#### Taxa de Formato Válido

**O que é:** A proporção de execuções em que o modelo retornou um JSON com todas as 12 chaves esperadas e com valores pertencentes aos conjuntos permitidos.

**Fórmula:**

```
Taxa de Formato Válido = (nº de respostas com formato correto) / (total de execuções) × 100%
```

**Para que serve:** Mede se o modelo consegue seguir o esquema/formato solicitado. Uma resposta pode ter o formato válido mas os valores errados (ex.: dizer `tipo_projeto: "web"` quando o correto é `"mobile"` — o formato está OK, mas a resposta está errada).

**Exemplo:** qwen2.5 e deepseek-r1:8b tiveram 100% de formato válido. O llama3 teve 82,67%, o que significa que em ~17% das execuções ele não conseguiu produzir um JSON válido com as chaves corretas.

---

#### Taxa de Erro de Execução

**O que é:** A proporção de execuções que resultaram em erro durante a chamada ao modelo (falha de conexão, timeout, etc.).

**Fórmula:**

```
Taxa de Erro = (nº de execuções com erro) / (total de execuções) × 100%
```

**Nos seus dados:** Todos os modelos tiveram 0% de erro de execução, ou seja, nenhuma chamada falhou tecnicamente.

---

#### Taxa de Sucesso

**O que é:** A proporção de execuções que foram simultaneamente de formato válido E sem erro de execução.

**Fórmula:**

```
Taxa de Sucesso = (nº de execuções com formato válido E sem erro) / (total de execuções) × 100%
```

**Para que serve:** É a métrica mais direta de confiabilidade. Uma taxa de sucesso de 82,67% (llama3) significa que, de cada 10 vezes que você usa o modelo, aproximadamente 2 vezes ele não entrega uma resposta utilizável.

---

#### Cobertura Média de Chaves

**O que é:** A proporção média de chaves esperadas (dos 12 atributos) que aparecem na resposta do modelo.

**Fórmula:**

```
Cobertura de uma execução = (nº de chaves esperadas presentes na resposta) / 12
Cobertura Média = média das coberturas de todas as execuções
```

**Para que serve:** Mede se o modelo está retornando todos os 12 atributos, mesmo quando o formato geral não é 100% válido. Uma cobertura de 97,22% (llama3, caso 1) significa que, em média, faltou ~1 chave das 12 nas respostas.

---

### 1.3 Métricas de Reprodutibilidade (Consistência)

Estas métricas avaliam se o modelo dá a **mesma resposta** quando recebe a **mesma entrada** múltiplas vezes.

#### Saídas Válidas Distintas

**O que é:** O número de respostas JSON diferentes (únicas) produzidas pelo modelo para a mesma entrada, considerando apenas as execuções válidas.

**Para que serve:** Um número baixo indica alta reprodutibilidade. Se o modelo deu 30 respostas válidas e apenas 5 são distintas, ele tem um repertório limitado de variações. Se são 22 respostas distintas, praticamente cada execução retornou algo diferente.

**Exemplo:** deepseek-r1:8b no caso 5 teve 22 saídas distintas em 30 execuções — quase nenhuma repetição, indicando alta variabilidade.

---

#### Consistência Total

**O que é:** A proporção de execuções que coincidem com a resposta mais frequente, considerando **todas** as execuções (incluindo as inválidas).

**Fórmula:**

```
Consistência Total = (nº de vezes que a resposta mais frequente apareceu) / (total de execuções) × 100%
```

**Exemplo:** Se em 30 execuções a resposta mais frequente apareceu 11 vezes, a consistência total é 11/30 = 36,67%.

---

#### Consistência Somente Válidos

**O que é:** O mesmo cálculo da Consistência Total, mas o denominador inclui apenas as execuções válidas.

**Fórmula:**

```
Consistência Válidos = (nº de vezes que a resposta mais frequente apareceu) / (total de execuções válidas) × 100%
```

**Para que serve:** É mais justa que a Consistência Total quando um modelo tem execuções inválidas (como o llama3). Se o llama3 teve 24 respostas válidas de 30, e a mais frequente apareceu 11 vezes, a consistência total é 11/30 = 36,67%, mas a consistência entre válidos é 11/24 = 45,83%.

**Como interpretar:** Valores mais altos indicam maior previsibilidade — o modelo tende a dar a mesma resposta. Valores baixos indicam que o modelo é "instável" e varia bastante nas respostas.

---

## Parte 2 — Métricas do `accuracy_report.txt`

Estas métricas comparam as respostas do modelo com o **gabarito** para medir a **qualidade/correção** das respostas.

---

### 2.1 Acurácia de uma Execução

**O que é:** A proporção de atributos que o modelo acertou em relação ao gabarito, em uma única execução.

**Fórmula:**

```
Acurácia = (nº de atributos corretos) / 12 × 100%
```

**Exemplo:** Se o modelo acertou 10 dos 12 atributos, a acurácia é 10/12 = 83,33%.

---

### 2.2 Acurácia Média (por modelo e caso)

**O que é:** A média das acurácias de todas as execuções válidas de um modelo para um determinado caso de teste.

**Fórmula:**

```
Acurácia Média = (acurácia_exec₁ + acurácia_exec₂ + ... + acurácia_execₙ) / n
```

---

### 2.3 Acurácia Mínima e Máxima

**O que são:** A menor e a maior acurácia obtida por um modelo em um caso de teste, entre todas as repetições.

**Para que servem:** Revelam a amplitude de variação da qualidade. Se a acurácia mínima é 25% e a máxima é 83%, o modelo é muito inconsistente — às vezes acerta bem, às vezes erra muito.

---

### 2.4 Execuções 100% Corretas

**O que é:** O número de execuções onde o modelo acertou **todos** os 12 atributos.

**Fórmula:**

```
Exec 100% = Σ(1 para cada execução onde acurácia = 100%)
```

**Nos seus dados:** Apenas o deepseek-r1:8b conseguiu 6 execuções 100% corretas (todas no caso 4), e o qwen2.5 conseguiu 1 (também no caso 4). O llama3 não obteve nenhuma.

---

### 2.5 Acurácia por Atributo

**O que é:** Para cada um dos 12 atributos, qual a porcentagem de execuções (de todos os modelos e casos) em que aquele atributo foi classificado corretamente.

**Fórmula:**

```
Acurácia do Atributo X = (nº de execuções em que X foi correto) / (total de execuções válidas avaliadas) × 100%
```

**Exemplo dos dados:**
- `tipo_projeto` tem 99,76% de acurácia — quase sempre acertado
- `requisitos_seguranca` tem 38,21% — muito frequentemente errado

---

## Parte 3 — Leitura dos Gráficos

---

### Fig 01 — Tempo Médio por Caso de Teste e Modelo

**Tipo:** Barras agrupadas

**Como ler:** O eixo X mostra os 5 casos de teste. Para cada caso, há 3 barras (uma para cada modelo). O eixo Y mostra o tempo médio em segundos. O número acima de cada barra é o valor exato.

**O que revela:** O deepseek-r1:8b é consistentemente o mais rápido (~19-20s) em todos os casos. O qwen2.5 é o mais lento (~26-29s). A entrada praticamente não afeta o tempo do deepseek, mas afeta levemente os outros.

---

### Fig 02 — Boxplot de Tempo de Resposta

**Tipo:** Boxplot (diagrama de caixa)

**Como ler:** Cada caixa mostra a distribuição dos tempos de **todas** as execuções de um modelo:
- A **linha no meio** da caixa é a mediana
- As **bordas** da caixa são o 1º quartil (25%) e o 3º quartil (75%)
- Os **traços** (whiskers) mostram a amplitude dos dados
- **Pontos isolados** fora dos traços são outliers

**O que revela:** O deepseek-r1:8b tem a caixa menor (menos dispersão), indicando tempos muito consistentes. O llama3 tem um outlier em ~38s. Quanto menor e mais baixa a caixa, melhor é o modelo em termos de velocidade.

---

### Fig 03 — Taxa de Sucesso vs. Falha

**Tipo:** Barras empilhadas

**Como ler:** Cada barra representa um modelo. A parte colorida (azul/verde) é o percentual de sucesso. A parte vermelha no topo é o percentual de falha. Os números dentro de cada seção são os percentuais.

**O que revela:** qwen2.5 e deepseek-r1:8b têm 100% de sucesso. O llama3 tem ~17% de falha, ou seja, produziu JSONs inválidos em parte das execuções.

---

### Fig 04 — Acurácia Consolidada por Modelo

**Tipo:** Barras simples

**Como ler:** Cada barra mostra a acurácia média geral de um modelo considerando todos os 5 casos de teste. O número acima da barra é o valor exato.

**O que revela:** O qwen2.5 lidera com 71,72%, seguido do deepseek-r1:8b com 69,39% e llama3 com 62,84%. A diferença entre os dois primeiros é pequena (~2%).

---

### Fig 05 — Acurácia por Caso de Teste e Modelo

**Tipo:** Barras agrupadas

**Como ler:** Igual à Fig 01, mas o eixo Y mostra acurácia (%) em vez de tempo. Para cada caso de teste, 3 barras mostram o desempenho de cada modelo.

**O que revela:** 
- O **Caso 3** (clínica médica) e o **Caso 4** (horas complementares) tiveram a maior acurácia geral
- O **Caso 2** (app badminton) e o **Caso 5** (jogo distribuído) foram os mais difíceis
- O deepseek-r1:8b foi o melhor no Caso 4 (90,6%) mas o pior no Caso 5 (47,2%)

---

### Fig 06 — Acurácia por Atributo (Geral)

**Tipo:** Barras horizontais ordenadas

**Como ler:** Cada barra representa um atributo. As barras são ordenadas da menor para a maior acurácia. A cor indica a faixa: vermelho (<60%), amarelo (60-80%), verde (>80%).

**O que revela:** 
- `requisitos_seguranca` é o atributo mais difícil (38,2%) — os modelos erram muito
- `tipo_projeto` é o mais fácil (99,8%) — quase sempre acertam
- Atributos subjetivos (segurança, maturidade, autenticação) tendem a ter menor acurácia

---

### Fig 07 — Heatmap de Acurácia por Atributo e Modelo

**Tipo:** Mapa de calor (heatmap)

**Como ler:** As linhas são os atributos e as colunas são os modelos. Cada célula mostra a acurácia média (em %) daquele atributo naquele modelo, com cor variando de vermelho (baixa acurácia) a verde escuro (alta acurácia).

**O que revela:** Este é o gráfico mais rico em informação. Permite identificar:
- O llama3 tem 39% em `integracao` enquanto os outros têm ~84-100% — uma fraqueza específica
- `requisitos_seguranca` é fraco para todos, mas menos para o deepseek (55%)
- `tipo_projeto` é verde escuro para todos (99-100%)

---

### Fig 08 — Consistência por Caso de Teste e Modelo

**Tipo:** Barras agrupadas

**Como ler:** Para cada caso de teste, mostra o percentual de consistência (somente válidos) de cada modelo. Consistência alta = o modelo deu a mesma resposta mais vezes.

**O que revela:**
- O **Caso 3** (clínica médica) teve a maior consistência (~60%) para qwen2.5 e deepseek — a entrada é clara e bem definida
- O **Caso 5** (jogo distribuído) teve a menor consistência (~10-24%) — a entrada é ambígua e os modelos "ficam em dúvida"

---

### Fig 09 — Consistência Consolidada por Modelo

**Tipo:** Barras simples

**Como ler:** Cada barra mostra a consistência média geral do modelo.

**O que revela:** Os três modelos possuem consistência baixa em geral (8-12%), indicando que raramente dão a mesma resposta exata ao receber a mesma entrada repetidamente. Isso é inerente à natureza estocástica dos LLMs.

---

### Fig 10 — Radar Comparativo Multidimensional

**Tipo:** Radar (spider chart)

**Como ler:** Cada eixo representa uma dimensão de avaliação (acurácia, consistência, taxa de sucesso, velocidade). Cada modelo é uma "teia" colorida. Quanto mais a teia se estende para a borda, melhor o modelo naquela dimensão.

**Como a velocidade é calculada:** Como menor tempo é melhor, a velocidade é normalizada inversamente: o modelo mais rápido recebe ~100 e o mais lento recebe ~0.

**O que revela:** Nenhum modelo domina em todas as dimensões. O deepseek-r1:8b se destaca em velocidade e taxa de sucesso. O qwen2.5 lidera em acurácia. O llama3 fica atrás nas três primeiras dimensões mas tem velocidade intermediária.

---

### Fig 11 — Saídas Válidas Distintas

**Tipo:** Barras agrupadas

**Como ler:** Para cada caso de teste, mostra quantas respostas JSON únicas/diferentes cada modelo produziu em 30 repetições.

**O que revela:** Valores mais baixos indicam maior reprodutibilidade. O Caso 3 teve poucas saídas distintas (5-7), enquanto o Caso 5 teve muitas (17-22). O deepseek-r1:8b é o que mais variou no Caso 5 (22 saídas distintas em 30 execuções).

---

## Parte 4 — Como Interpretar os Resultados

### Qual a melhor forma de analisar: por modelo ou por caso de teste?

**Ambas as perspectivas são essenciais e complementares.** A resposta depende da pergunta que você quer responder:

| Pergunta | Analisar por... |
|----------|-----------------|
| "Qual modelo é o melhor para usar no sistema?" | **Por modelo** (consolidado) |
| "Qual entrada/caso de teste é mais difícil para os LLMs?" | **Por caso de teste** |
| "Qual modelo funciona melhor para entradas simples vs. complexas?" | **Cruzamento modelo × caso** |
| "Quais atributos os LLMs mais erram?" | **Por atributo** |

### Recomendação de estrutura para a monografia

1. **Primeiro**, apresente os resultados **consolidados por modelo** (Fig 03, 04, 09, 10) — isso responde à pergunta principal: "qual modelo é melhor?"

2. **Depois**, aprofunde **por caso de teste** (Fig 01, 05, 08, 11) — mostra como a complexidade da entrada influencia o desempenho

3. **Por fim**, analise **por atributo** (Fig 06, 07) — revela os pontos cegos dos LLMs e quais classificações são intrinsecamente mais difíceis

### Resumo dos achados principais

| Dimensão | Melhor modelo | Observação |
|----------|--------------|------------|
| **Acurácia** | qwen2.5 (71,72%) | Margem pequena sobre deepseek (69,39%) |
| **Taxa de sucesso** | qwen2.5 e deepseek (100%) | llama3 falhou em ~17% das vezes |
| **Velocidade** | deepseek-r1:8b (~19,5s) | ~40% mais rápido que qwen2.5 |
| **Consistência** | Todos baixos (~8-12%) | Característica inerente dos LLMs |
| **Exec. 100% corretas** | deepseek-r1:8b (6/150) | Único com taxa relevante |
| **Atributo mais difícil** | `requisitos_seguranca` (38%) | Todos os modelos erram bastante |
| **Atributo mais fácil** | `tipo_projeto` (99,8%) | Praticamente trivial |
| **Caso mais difícil** | Caso 5 (jogo distribuído) | Entrada ambígua e incomum |
| **Caso mais fácil** | Caso 3/4 (clínica/horas) | Entradas claras e bem definidas |
