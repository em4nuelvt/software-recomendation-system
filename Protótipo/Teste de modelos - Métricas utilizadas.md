
---

## Documentação das Métricas do Benchmark - Etapa 1

### Visão Geral

O benchmark da Etapa 1 avalia o desempenho de modelos de PLN na extração de requisitos de software. As métricas medem três dimensões principais: **desempenho** (tempo), **confiabilidade** (formato e erros) e **consistência** (variação de respostas).

### Notação Matemática

Para os cálculos descritos abaixo, considere:
- $N$ = total de execuções no grupo
- $t_i$ = tempo da execução $i$ em milissegundos
- $V$ = número de respostas com formato válido
- $E$ = número de respostas com erro de execução
- $S$ = número de respostas de sucesso (formato válido e sem erro)
- $K$ = número de chaves esperadas (aqui, $K=12$)
- $D$ = número de respostas válidas distintas
- $M$ = quantidade da resposta válida mais frequente

---

## Métricas de Tempo

### Tempo Total
Duração total do benchmark, calculada como a diferença entre o horário de término e o horário de início. Aparece apenas no resumo geral do benchmark.

### Tempo Médio (ms)
Media aritmética de todos os tempos de execução.

$$\text{tempo médio} = \frac{1}{N}\sum_{i=1}^{N} t_i$$

**Interpretação:** representa o tempo típico de execução. Valores menores indicam modelos mais rápidos.

### Tempo Mediano (ms)
Valor central dos tempos ordenados; metade das execuções ficam abaixo e metade acima.

**Interpretação:** menos sensível a outliers que a média. Util para identificar o "comportamento típico" quando há picos de lentidão.

### Tempo p95 (ms)
95º percentil; 95% das execuções ficaram abaixo deste tempo.

**Interpretação:** mostra o limite superior esperado em condições normais. Valores baixos indicam previsibilidade.

### Tempo Mínimo (ms)
Menor tempo observado em todas as execuções.

$$\text{mín} = \min(t_i)$$

### Tempo Máximo (ms)
Maior tempo observado em todas as execuções.

$$\text{máx} = \max(t_i)$$

**Interpretação:** a diferença (máx - mín) mostra a variação total de tempo. Intervalos grandes sugerem instabilidade.

---

## Métricas de Formato e Erro

### Taxa de Formato Válido
Proporção de respostas que seguem o schema esperado, ou seja, possuem todas as 12 chaves obrigatórias e os valores estão dentro da lista permitida.

$$\text{taxa de formato válido} = \frac{V}{N} \times 100\%$$

**Interpretação:** quanto maior, melhor. Uma taxa de 100% indica que o modelo sempre retorna respostas estruturadas corretamente.

### Taxa de Erro de Execução
Proporção de respostas que contêm o campo ERRO, indicando falha na execução (ex: JSON inválido, exceção não capturada).

$$\text{taxa de erro} = \frac{E}{N} \times 100\%$$

**Interpretação:** quanto menor, melhor. Idealmente deve ser 0%.

### Taxa de Sucesso
Proporção de respostas que foram executadas sem erro **e** possuem formato válido simultaneamente.

$$\text{taxa de sucesso} = \frac{S}{N} \times 100\%$$

**Interpretação:** métrica mais importante para confiabilidade global. Deve ser superior a 90% para considerar o modelo viável.

---

## Métricas de Cobertura

### Cobertura Média de Chaves
Mede, em média, quantas das 12 chaves esperadas estão presentes em cada resposta.

Para cada execução $i$:
$$\text{cobertura}_i = \frac{\text{número de chaves presentes}}{K}$$

Depois, calcula-se a média:
$$\text{cobertura média} = \frac{1}{N}\sum_{i=1}^{N}\text{cobertura}_i \times 100\%$$

**Interpretação:** distingue entre resposta totalmente inválida (0% de chaves) e resposta parcialmente válida (ex: 75% de chaves presentes). Uma cobertura de 100% significa que todas as respostas possuem as 12 chaves.

---

## Métricas de Consistência (Variação)

### Saídas Válidas Distintas
Quantidade de respostas **válidas** diferentes observadas nas execuções.

$$D = \left|\{\text{respostas válidas distintas}\}\right|$$

**Interpretação:** quanto menor, mais consistente é o modelo. Um valor de 1 significa que o modelo sempre retorna a mesma resposta válida. Um valor alto indica alta variabilidade.

### Consistência Total
Frequência relativa da resposta válida mais comum, dividida pelo total de execuções (incluindo inválidas).

$$\text{consistência total} = \frac{M}{N} \times 100\%$$

Onde $M$ é a quantidade de vezes que a resposta mais frequente apareceu.

**Interpretação:** mostra qual proporção do total é dominada pela resposta mais comum. Útil para comparar modelos com taxas de sucesso diferentes.

### Consistência Somente Válidos
Frequência relativa da resposta válida mais comum, dividida apenas pelo número de execuções válidas.

$$\text{consistência somente válidos} = \frac{M}{V} \times 100\%$$

**Interpretação:** a métrica mais importante para avaliar **variabilidade de resposta**. Mede estabilidade desacoplada de erros. Valores acima de 50% indicam que o modelo tende a retornar respostas similares; valores próximos a 10-20% indicam alta variação mesmo entre respostas válidas.

---

## Critério de Ranking

Os modelos são rankeados por:

1. **Taxa de sucesso** (descendente): modelos com mais sucessos vêm primeiro.
2. **Consistência somente válidos** (descendente): em empate de sucesso, o modelo mais consistente vem primeiro.
3. **Tempo médio** (ascendente): em empate anterior, o mais rápido vem primeiro.

Esta ordem prioriza confiabilidade acima de velocidade, refletindo o objetivo de um extrator de requisitos robusto.

---

## Configuração do Experimento

### Visão Geral do Protocolo

O experimento avalia 3 modelos de linguagem em 5 casos de entrada distintos, com 30 repetições por par (modelo, caso), totalizando 450 execuções. Cada execução corresponde a uma chamada independente ao método `extractRequirement` da classe `RequirementExtractor`, sem reaproveitamento de contexto entre chamadas.

### Modelos Avaliados

| Modelo | Família | Parâmetros | Acesso |
|--------|---------|------------|--------|
| qwen2.5 | Qwen (Alibaba) | 7B | Ollama local |
| llama3 | LLaMA 3 (Meta) | 8B | Ollama local |
| deepseek-r1:8b | DeepSeek-R1 | 8B | Ollama local |

Os três modelos foram selecionados por serem open source, executáveis localmente via Ollama e representarem famílias distintas de modelos generativos, permitindo uma comparação entre arquiteturas diferentes dentro da mesma faixa de parâmetros.

[IMPORTANTE] -> Necessário estudar sobre a quantidade de parâmetros de cada modelo, estudar e anotar o que isso muda para justificar a escolha dos modelos avaliados. 

### Casos de Teste

Os casos foram elaborados para cobrir domínios e complexidades distintas, variando de descrições curtas e diretas até descrições longas com múltiplos requisitos implícitos:

| Caso | Descrição |
|------|-----------|
| 1 | "Tecnologias para sistema de lista de tarefas web" |
| 2 | "Gostaria de desenvolver um aplicativo para Android e iOS sobre o esporte badminton, com foco no apoio ao ensino nas aulas de Educação Física. O aplicativo deve conter informações sobre equipamentos, regras oficiais e tutoriais de como jogar." |
| 3 | "Gostaria de desenvolver um sistema de gestão para clínicas médicas, acessível por qualquer plataforma por meio de um site na internet. O sistema deve armazenar dados de pacientes, médicos, consultas, exames e informações financeiras." |
| 4 | "Quero desenvolver um sistema para controle de horas complementares no ambiente acadêmico, acessível pela internet. Cada aluno deve cadastrar seu perfil e curso, além de gerenciar as horas necessárias para concluir a graduação." |
| 5 | "Quero construir um jogo da memória para computadores desktop, utilizando conceitos de sistemas distribuídos. Os jogadores devem se comunicar entre si por meio de um servidor middleware." |

### Justificativa do Número de Repetições

Foram definidas 30 repetições por par (modelo, caso). Esse valor é fundamentado no Teorema do Limite Central, segundo o qual amostras com $N \geq 30$ tendem a uma distribuição normal, permitindo o uso de estatísticas descritivas (média, mediana, percentis) com maior confiabilidade. O número também equilibra representatividade estatística com custo computacional — dado que cada execução leva em média ~25 segundos em execução local, as 450 execuções totalizam aproximadamente 3 horas de benchmark.

### Ambiente de Execução

- **Plataforma de inferência:** Ollama (execução local)
- **Formato de saída forçado:** JSON nativo via parâmetro `format='json'` da API Ollama
- **Sistema operacional:** *(preencher)*
- **Hardware:** *(preencher — CPU/GPU, memória RAM)*
- **Versão do Ollama:** *(preencher)*

### Definição de uma Execução

Uma execução é definida como uma chamada isolada ao método `extractRequirement(user_input)` para um par (modelo, caso de teste), medindo o tempo decorrido desde o envio do prompt até o retorno completo da resposta. Não há compartilhamento de contexto ou histórico entre execuções — cada chamada é independente.

---

