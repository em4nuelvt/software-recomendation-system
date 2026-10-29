# Sistema de Recomendação de Tecnologias de Software


---

## 📌 Visão Geral do Projeto

A seleção de pilhas tecnológicas (*stacks* de software — linguagens de programação, *frameworks* de backend/frontend, bancos de dados e infraestrutura) é uma das decisões mais críticas e complexas na fase inicial da Engenharia de Software. Escolhas inadequadas podem acarretar dívida técnica precoce, falhas de escalabilidade, custos excessivos e retrabalho arquitetural.

Este projeto propõe e implementa uma **arquitetura híbrida especialista** que une a flexibilidade semântica de **Modelos de Linguagem de Grande Escala (LLMs) executados localmente** ao rigor determinístico e explicabilidade de **Grafos de Conhecimento**.

A solução opera de maneira **100% local e gratuita**, garantindo total privacidade dos requisitos do projeto e independência de APIs proprietárias pagas ou conexão com a nuvem.

---

## 🏗️ Arquitetura do Sistema

O sistema é estruturado em um fluxo contínuo de três etapas sequenciais:

```
                  ┌────────────────────────────────────────┐
                  │      Entrada do Usuário (Texto)        │
                  │   Descrição informal do projeto em LN  │
                  └───────────────────┬────────────────────┘
                                      │
                         [ Validador de Escopo LLM ]
                                      │ (Se for desenvolvimento de software)
                                      ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ ETAPA 1: Processamento de Linguagem Natural e Extração (LLM)   │
     │ - Modelo: Qwen 2.5 local via Ollama (Temperatura 0.0)           │
     │ - Extrai estritamente 12 atributos de requisitos em JSON válido │
     └────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ ETAPA 2: Motor de Recomendação Baseado em Grafo de Conhecimento │
     │ - Grafo direcionado ponderado (111 nós e 2.646 arestas)         │
     │ - Multiplicadores de prioridade por categoria de requisito      │
     │ - Ranqueamento e composição das Top 3 Stacks tecnológicas       │
     └────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
     ┌─────────────────────────────────────────────────────────────────┐
     │ ETAPA 3: Formatação Técnica e Síntese Analítica (LLM)           │
     │ - Avalia criticamente o ranking matemático do grafo             │
     │ - Redige relatório técnico fundamentando a stack vencedora      │
     │ - Identifica tecnologias complementares de apoio                │
     └────────────────────────────────┬────────────────────────────────┘
                                      │
                                      ▼
                  ┌────────────────────────────────────────┐
                  │      Relatório Técnico Final           │
                  │   Exibição no terminal e arquivo txt   │
                  └────────────────────────────────────────┘
```

### Detalhamento das Etapas:
1. **Validação de Escopo:** O LLM avalia se a entrada do usuário trata de uma solicitação real de desenvolvimento de software, prevenindo processamento indevido.
2. **Etapa 1 (Extração de Requisitos):** Classifica o texto livre em um vocabulário controlado de **12 atributos padronizados**:
   - **4 Classificadores Primários:** `tipo_projeto`, `dominio_negocio`, `persistencia` e `escala`.
   - **8 Atributos de Suporte:** `arquitetura_esperada`, `integracao`, `requisito_seguranca`, `tipo_autenticacao`, `ambiente_implantacao`, `experiencia_usuario`, `maturidade_equipe` e `ciclo_desenvolvimento`.
3. **Etapa 2 (Motor em Grafo):** Calcula os escores de compatibilidade entre os atributos extraídos e tecnologias candidatas utilizando as relações estruturadas no Grafo de Conhecimento (`ADEQUADO_PARA`, `REQUER`, `COMPATIVEL_COM`, `COMPLEMENTA`).
4. **Etapa 3 (Síntese Analítica):** O LLM gera um parecer técnico contextualizado, comparando as 3 melhores alternativas sugeridas pelo grafo e fundamentando a stack mais recomendada.

---

## ⚙️ Pré-requisitos

Para executar o sistema, certifique-se de possuir em seu ambiente:

1. **Python 3.10 ou superior** (testado em Python 3.10, 3.12, 3.13 e 3.14).
2. **Ollama** instalado e em execução ([ollama.com](https://ollama.com/)).
3. **Modelo Qwen 2.5** baixado no Ollama:
   ```bash
   ollama pull qwen2.5
   ```
   *(Obs.: O modelo Qwen 2.5 foi comprovado experimentalmente nesta pesquisa como o modelo mais assertivo e estável, atingindo 81,67% de acurácia global, 100% de sucesso estrutural e 100% de consistência no Cenário 4).*

---

## 🚀 Instalação e Configuração

### 1. Clonar o Repositório
```bash
<<<<<<< HEAD
git clone https://github.com/em4nuelvt/software-recomendation-system.git
=======
git clone https://github.com/em4nuelvt/software-recomendation-system
>>>>>>> 448c6827fbab3dd4fc4c7008c38d656d7c1476cb
cd software-recomendation-system
```

### 2. (Opcional, mas recomendado) Criar e Ativar Ambiente Virtual
- **No Linux/macOS:**
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- **No Windows (PowerShell):**
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  ```

### 3. Instalar as Dependências do Projeto
```bash
pip install -r Protótipo/src/requirements.txt
```

### 4. Certificar-se de que o Ollama está Ativo
Em um terminal separado, verifique se o serviço do Ollama está rodando e se o modelo está disponível:
```bash
ollama list
```
Deverá constar `qwen2.5:latest` (ou `qwen2.5`) na listagem.

---

## 💻 Como Executar o Sistema

Acesse o diretório do código-fonte do protótipo:
```bash
cd Protótipo/src
```

### 1. Execução do Sistema Completo (Etapas 1, 2 e 3)
Para executar o fluxo ponta a ponta (Validação $\rightarrow$ Extração de Requisitos $\rightarrow$ Grafo de Conhecimento $\rightarrow$ Síntese Analítica):

```bash
python executar_sistema.py
```

Ao executar, o terminal apresenta opções de entrada:
- Pressionar **`[ENTER]`**: executa o caso de teste padrão (Caso 6 - Plataforma Acadêmica Integrada).
- Digitar um **número de 1 a 6**: executa o respectivo caso de teste padronizado da pesquisa.
- Digitar uma **descrição textual livre**: processa qualquer nova solicitação de software em linguagem natural.

Você também pode passar a entrada diretamente como argumento de linha de comando:
```bash
python executar_sistema.py "Quero desenvolver um aplicativo mobile para Android e iOS voltado para o agendamento de consultas médicas e telemedicina, com pagamento integrado e segurança avançada."
```
Ou passar diretamente o número do caso de teste:
```bash
python executar_sistema.py 2   # Executa o Caso 2 (App Mobile de Badminton)
```

---

### 2. Execução Isolada do Extrator de Requisitos (Etapa 1)
Caso deseje testar exclusivamente o extrator de requisitos estruturados via LLM:

```bash
python main.py
```
Esse script utiliza a entrada configurada em `user_input.py`, executa o `RequirementExtractor` e exibe o dicionário JSON de requisitos gerado pelo modelo.

---

## 📄 Exemplo de Saída Gerada

Ao finalizar o processamento, o sistema imprime o parecer técnico detalhado no terminal e salva o resultado no arquivo `Protótipo/src/resultado_da_execucao.txt`:

```text
=== Opções Selecionadas pelo Motor de Recomendação ===

Tipo de desenvolvimento : WEB
Arquitetura sugerida    : Microsservicos
Complexidade de UX      : Intermediaria

Opção 1 [Aderência 7.3/10]: Python + Django (back) + React (front) + PostgreSQL (db)
Opção 2 [Aderência 7.2/10]: Java + Spring Boot (back) + React (front) + PostgreSQL (db)
Opção 3 [Aderência 6.6/10]: Elixir + Phoenix (back) + React (front) + PostgreSQL (db)

--- Resumo da Recomendação ---
Resumo: A melhor opção para o sistema acadêmico descrito é a stack composta por 
Python, Django, PostgreSQL, React e Kubernetes. Esse conjunto de tecnologias oferece 
uma arquitetura robusta e escalável, adequada ao contexto do projeto, que requer 
uma grande escala e integração com APIs externas.

O Django é um framework robusto e de alto nível para Python, perfeitamente adequado 
para aplicações complexas como uma plataforma acadêmica...

Tempo total de execução: 90.98 segundos (Etapa 1: 22.14 s | Etapa 2: 0.0004 s | Etapa 3: 55.16 s)
```

---

## 📂 Estrutura de Pastas do Repositório

```text
software-recomendation-system/
│
├── README.md                     # Documentação principal e guia de execução
│
└── Protótipo/
    ├── Etapa 1 - NLP.md          # Especificação da etapa de PLN
    │
    ├── Documentação/             # Diretrizes de classificação e métricas do TCC
    │   ├── Diretrizes de classificação.md
    │   └── Teste de modelos - Métricas utilizadas.md
    │
    └── src/
        ├── executar_sistema.py      # Script principal de execução do fluxo completo (Etapas 1, 2 e 3)
        ├── main.py                  # Demonstração e teste isolado do Extrator de Requisitos (Etapa 1)
        ├── requirements.txt         # Dependências Python do projeto
        ├── RequirementExtractor.py  # Módulo Etapa 1: Extração de requisitos com LLM
        ├── RecommendationEngine.py  # Módulo Etapa 2: Motor de inferência em grafo
        ├── ResponseFormatter.py     # Módulo Etapa 3: Síntese e parecer técnico com LLM
        ├── user_input.py            # Entradas de teste padronizadas da pesquisa
        ├── resultado_da_execucao.txt # Último resultado gerado pela execução
        │
        ├── data/
        │   └── graph/
        │       ├── knowledge_graph.json         # Grafo de conhecimento compilado (111 nós)
        │       └── technology_seed.json         # Definições base de tecnologias
        │
        ├── scripts/
        │   ├── graph_builder.py     # Script para construção e validação do grafo
        │   └── SurveyProcessor.py   # Processamento de dados da pesquisa de campo
        │
        └── tests/                   # Bateria experimental de testes de modelos
            ├── evaluate_models.py
            ├── calculate_accuracy.py
            ├── plot_results.py
            └── benchmark_output/    # Relatórios e gráficos gerados nos cenários
```

---

## 🔬 Síntese da Metodologia Experimental

A configuração integrada a este protótipo (`Qwen 2.5` + `Prompt Descritivo` + `Temperatura 0,0`) foi definida por meio de um protocolo experimental fatorial (1.800 execuções nos 4 cenários principais) comparando três modelos locais (**Qwen 2.5**, **LLaMA 3** e **DeepSeek-R1:8B**):

| Cenário | Formulação e Temperatura | Principais Resultados |
| :---: | :--- | :--- |
| **Cenário 1** | Prompt Conciso + Temp. Padrão (0,8) | Alta dispersão de saídas (consistência $\le 35,33\%$). Qwen 2.5 obteve 72,33% de acurácia. |
| **Cenário 2** | Prompt Conciso + Temp. Zero (0,0) | **Melhor equilíbrio coletivo:** 100% de sucesso estrutural nos três modelos (Qwen 2.5: **78,28%**, LLaMA 3: **75,00%**, DeepSeek-R1:8B: **70,06%**). |
| **Cenário 3** | Prompt Descritivo + Temp. Padrão (0,8) | Qwen 2.5 manteve 100% de sucesso (72,89% de acurácia), mas a variabilidade estocástica limitou a consistência. |
| **Cenário 4** | Prompt Descritivo + Temp. Zero (0,0) | **Maior pico individual:** O **Qwen 2.5** atingiu **81,67% de acurácia global**, com **100% de sucesso estrutural** e **100% de consistência determinística**. |
