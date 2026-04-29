
---

## Documentação — compute_ground_truth.py

### Visão Geral

O script `compute_ground_truth.py` analisa os resultados já gerados pelo benchmark e produz automaticamente uma sugestão de gabarito para os casos de teste. Ele utiliza a técnica de **majority vote** (votação por maioria): para cada par (caso de teste, atributo), o valor que apareceu com maior frequência entre todas as execuções válidas dos três modelos é escolhido como resposta sugerida.

O gabarito gerado por este script é apenas um **ponto de partida**. O passo seguinte é a revisão humana atributo a atributo para confirmar ou corrigir os valores, produzindo o arquivo `ground_truth.json` final.

---

### Por que usar majority vote como ponto de partida?

Para o domínio deste sistema, os 12 atributos de saída possuem um vocabulário fechado e predefinido. As regras de preenchimento estão explícitas no prompt: valores mencionados diretamente no texto devem ser identificados; valores não mencionados devem assumir o valor mais simples e comum para o contexto.

Nesse cenário, quando um valor é escolhido por uma ampla maioria das execuções (somando os três modelos e 30 repetições cada, o que resulta em até 90 votos por atributo), isso é um forte indicativo de que os modelos convergem para uma interpretação razoável. A votação por maioria agrupa esse sinal de forma objetiva e rastreável.

O majority vote **não substitui** a revisão humana porque os modelos também podem convergir para um valor errado caso o prompt seja ambíguo ou o atributo não esteja explícito na entrada. Por isso, a revisão é necessária antes de usar o gabarito como referência definitiva.

---

### O que o script produz

Ao ser executado, o script gera dois arquivos na pasta `benchmark_output/`:

| Arquivo | Descrição |
|---|---|
| `ground_truth_majority_vote.json` | Gabarito sugerido. Para cada caso de teste (chaves `"1"` a `"5"`), contém o valor com maior contagem em cada um dos 12 atributos. |
| `ground_truth_vote_distribution.txt` | Distribuição completa de votos por atributo e por caso. Mostra todos os valores que apareceram, suas contagens e percentuais. Usado na revisão humana. |

Nenhum arquivo anterior é re-executado pelo modelo. O script lê apenas o arquivo `resultados_detalhados.txt` já existente.

---

### Formato do gabarito gerado (`ground_truth_majority_vote.json`)

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
    },
    "2": { ... },
    ...
}
```

As chaves do objeto externo são strings `"1"` a `"5"`, correspondendo ao número do caso de teste. Cada objeto interno contém os 12 atributos do schema.

---

### Como executar

**Pré-requisito:** o arquivo `benchmark_output/resultados_detalhados.txt` deve existir, gerado por uma execução anterior do `requirement_extractor_benchmark.py`.

Navegue até a pasta `src/` e execute:

```bash
python compute_ground_truth.py
```

O script exibirá no terminal o número de registros lidos, a quantidade de registros válidos e o caminho dos arquivos gerados.

---

### Como criar o gabarito final (`ground_truth.json`)

Após executar o script, siga os passos abaixo:

**Passo 1 — Copiar o majority vote como base:**

```bash
# Windows
copy benchmark_output\ground_truth_majority_vote.json benchmark_output\ground_truth.json

# Linux / macOS
cp benchmark_output/ground_truth_majority_vote.json benchmark_output/ground_truth.json
```

**Passo 2 — Revisar com o auxílio da distribuição de votos:**

Abra `ground_truth_vote_distribution.txt` e verifique cada atributo. Para cada atributo, observe:

- Se a vitória foi **unânime ou quase unânime** (ex: 85/90 votos): o valor é confiável e provavelmente correto.
- Se houve **empate ou distribuição equilibrada** (ex: 45 vs 45): o texto de entrada deve ser analisado diretamente para decidir o valor correto.
- Se **nenhum valor** for explícito no texto da entrada: confirme se o valor vencedor é de fato o "mais simples e comum para o contexto", conforme a regra do prompt.

**Passo 3 — Editar `ground_truth.json` com os valores revisados:**

Abra o arquivo `ground_truth.json` e corrija os atributos que precisarem de ajuste. Salve o arquivo.

Após concluir a revisão, o `ground_truth.json` está pronto para ser usado pelo script `accuracy_report.py` e pelo `requirement_extractor_benchmark.py`.

---

### Comportamento detalhado do majority vote

- Apenas execuções com `Formato_valido: sim` são consideradas no cômputo dos votos.
- Execuções de todos os três modelos são somadas: cada caso de teste pode ter até 90 votos por atributo (30 repetições × 3 modelos).
- Em caso de empate (dois valores com o mesmo número de votos), o script escolhe o primeiro valor em ordem alfabética. Essa situação é indicada no arquivo de distribuição, pois todos os valores empatados são marcados com `<-- VENCEDOR`.
- O script nunca modifica os arquivos de resultado originais.

---

### Dependências

O script utiliza apenas a biblioteca padrão do Python (versão 3.8 ou superior). Nenhuma instalação adicional é necessária.

---

### Arquivos envolvidos

| Arquivo | Papel |
|---|---|
| `src/compute_ground_truth.py` | Script principal |
| `benchmark_output/resultados_detalhados.txt` | Entrada (gerada pelo benchmark) |
| `benchmark_output/ground_truth_majority_vote.json` | Saída — gabarito sugerido |
| `benchmark_output/ground_truth_vote_distribution.txt` | Saída — distribuição de votos para revisão |
| `benchmark_output/ground_truth.json` | Criado manualmente após revisão (entrada para accuracy_report.py) |
