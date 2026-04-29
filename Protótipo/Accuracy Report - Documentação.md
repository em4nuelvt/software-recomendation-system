
---

## Documentação — accuracy_report.py

### Visão Geral

O script `accuracy_report.py` calcula a **acurácia dos modelos em relação ao gabarito** definido no arquivo `ground_truth.json`. Ele opera exclusivamente sobre os arquivos de saída já gerados pelo benchmark, sem executar nenhum modelo novamente.

Para cada execução válida registrada no `resultados_detalhados.txt`, o script compara os 12 atributos retornados pelo modelo com os valores esperados no gabarito e calcula qual proporção foi respondida corretamente.

---

### O que o script produz

O script gera o arquivo `benchmark_output/accuracy_report.txt` com quatro seções:

| Seção | Conteúdo |
|---|---|
| 1) Por modelo e caso | Acurácia média, mínima, máxima e número de execuções 100% corretas para cada combinação modelo × caso de teste. Lista os atributos que não atingiram 100% de acerto. |
| 2) Por modelo (consolidado) | Acurácia média e execuções 100% corretas somando todos os casos de teste do modelo. |
| 3) Por atributo (global) | Acurácia de cada um dos 12 atributos somando todos os modelos e casos. Indica quais atributos os modelos erram com mais frequência. |
| 4) Ranking por acurácia | Ordenação dos modelos do melhor para o pior, usando acurácia média como critério principal. |

---

### Definição de acurácia

Para cada execução válida, a acurácia é definida como:

$$\text{acurácia} = \frac{\text{atributos corretos}}{12}$$

Um atributo é considerado correto quando o valor retornado pelo modelo é exatamente igual ao valor definido no gabarito para aquele caso de teste.

A **acurácia média** de um modelo ou caso é a média aritmética das acurácias individuais de todas as execuções válidas avaliadas.

Execuções com `Formato_valido: nao` são excluídas do cálculo, pois não possuem atributos comparáveis.

---

### Como executar

**Pré-requisitos:**
1. O arquivo `benchmark_output/resultados_detalhados.txt` deve existir.
2. O arquivo `benchmark_output/ground_truth.json` deve existir (criado a partir de `compute_ground_truth.py` com revisão humana).

Navegue até a pasta `src/` e execute:

```bash
python accuracy_report.py
```

O script exibirá no terminal o número de registros lidos e o caminho do relatório gerado.

---

### Formato do `ground_truth.json`

O gabarito deve ser um objeto JSON com as chaves `"1"` a `"5"` (número do caso de teste) e, para cada caso, os 12 atributos com seus valores esperados:

```json
{
    "1": {
        "tipo_projeto": "web",
        "dominio_negocio": "produtividade",
        "persistencia": "sql",
        "escala": "pequena",
        "integracao": "nenhuma",
        "arquitetura_esperada": "monolito",
        "experiencia_usuario": "basica",
        "requisitos_seguranca": "nenhum",
        "ambiente_implantacao": "local",
        "maturidade_equipe": "iniciante",
        "tipo_autenticacao": "nenhuma",
        "ciclo_desenvolvimento": "mvp"
    }
}
```

---

### Como interpretar o relatório

**Seção 1 — Por modelo e caso de teste:**

A acurácia média indica qual proporção dos atributos foi respondida corretamente em média. Uma acurácia de 83.33% significa que, em média, 10 dos 12 atributos estavam corretos. O campo "execuções 100% corretas" mostra quantas execuções tiveram todos os 12 atributos idênticos ao gabarito.

A lista de atributos abaixo de 100% ajuda a identificar quais atributos o modelo tende a errar para aquele caso específico.

**Seção 3 — Por atributo:**

Esta seção revela padrões sistemáticos de erro. Um atributo com baixa acurácia global indica que os modelos têm dificuldade em interpretá-lo corretamente, independentemente do caso de teste. Isso pode indicar que o prompt precisa de ajuste para aquele atributo ou que o gabarito precisa ser revisado.

**Seção 4 — Ranking:**

O critério primário é a maior acurácia média. Em empate, prevalece a maior proporção de execuções com 100% de acerto.

---

### Relação com as demais métricas do benchmark

A acurácia vs. gabarito complementa as métricas já existentes:

| Métrica | O que mede |
|---|---|
| Taxa de sucesso | Se o modelo retorna um JSON válido com o schema correto |
| Consistência | Se o modelo retorna sempre a mesma resposta |
| **Acurácia vs. gabarito** | **Se a resposta retornada está correta em relação ao esperado** |

É possível um modelo ter 100% de taxa de sucesso e baixa consistência, mas alta acurácia — o que significa que o modelo sempre retorna respostas válidas, varia nas respostas, mas tende a acertar o valor correto com frequência. A acurácia é a única métrica que avalia a **qualidade do conteúdo** da resposta.

---

### Integração com o benchmark principal

Quando o arquivo `ground_truth.json` está presente na pasta `benchmark_output/` no momento em que o `requirement_extractor_benchmark.py` é executado, a seção 5 (Acurácia vs. Gabarito) é adicionada automaticamente ao arquivo `resumo_metricas.txt`. Essa seção contém o subconjunto de métricas de acurácia (por modelo e caso, por modelo consolidado e ranking). Para o relatório completo por atributo, execute `accuracy_report.py` separadamente.

---

### Dependências

O script utiliza apenas a biblioteca padrão do Python (versão 3.8 ou superior). Nenhuma instalação adicional é necessária.

---

### Arquivos envolvidos

| Arquivo | Papel |
|---|---|
| `src/accuracy_report.py` | Script principal |
| `benchmark_output/resultados_detalhados.txt` | Entrada (gerada pelo benchmark) |
| `benchmark_output/ground_truth.json` | Entrada — gabarito revisado |
| `benchmark_output/accuracy_report.txt` | Saída — relatório de acurácia |
