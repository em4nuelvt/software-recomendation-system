### Modelos a serem utilizados
- BERT (NER/Classificação) -> Compreender o texto de entrada do usuário e rotular em termos específicos baseados em compressão de significado.
	- É necessário um conjunto de dados inicial com exemplos de frases rotuladas para o treinamento/ajuste do modelo. 
- LLaMA (Prompting) -> Processar o texto através de instruções (prompts) para gerar a estrutura de saída diretamente. 
	- É necessário definir um prompt estruturado para guiar a geração e mitigar risco de imprecisões ou alucinações. 

### O que essa etapa retorna?
- É a camada de entrada do sistema. 
- O objetivo é receber o texto livre do usuário, validar se a entrada perence ao domínio de engenharia de software e gerar um dicionário estruturado de requisitos.


### Atributos de saída para a etapa 1
- tipo_projeto -> web, movile, desktop, api, pipeline de dados
- dominio_negocio -> contexto da aplicação: tarefas, jogos, e-commerce
- persisitencia -> como dados serão armazenados: arquivos, sql, sem persistência, web, cloud
- escala ->  volume de acessos ou processamento
- integracao -> se deve se conectar a sistemas externos (apis de pagamento, integração de hardware, etc)
- arquitetura_esperada -> 
- requisitos_desempenho -> 
- experiencia_usuario -> 
- requisitos_seguranca ->

### Prompt para LLaMa (ou outros modelos de IA)
```
Você é um extrator de requisitos de software.
Sua tarefa é analisar a entrada do usuário e extrair 9 atributos em formato JSON.
Atributos: tipo_projeto, dominio_negocio, persistencia, escala, integracao, arquitetura_esperada, requisitos_desempenho, experiencia_usuario, requisitos_seguranca.

Regras:
- Se o usuário não mencionar informações suficientes para preencher um atributo, preencha-o com a opção que torne o sistema o mais SIMPLES e comum possível de ser construído (ex: se arquitetura não for citada, use "Monolito").
- Retorne o conteúdo formatado em JSON sem textos adicionais, ou seja, a sua resposta deve ser somente o JSON estruturado. 

```

### Ideia de contextualizar mais o prompt
- Adicionar valores permitidos para atributos. Exemplos:
```
Atributos e Valores Permitidos (Escolha ESTRITAMENTE desta lista):
- tipo_projeto: ["Web Full-Stack", "Web Front-End", "API Back-End", "Mobile Nativo", "Mobile Híbrido", "Desktop", "CLI/Script", "Pipeline de Dados", "IoT", "Jogos"]
- dominio_negocio: [Resuma o contexto em até 2 palavras]
- persistencia: ["Relacional", "Documento (NoSQL)", "Chave-Valor", "Grafo", "Série Temporal", "Arquivo Local", "Nenhuma"]
- escala: ["Local/Pessoal", "Pequena (Centenas de acessos)", "Média (Milhares de acessos)", "Alta (Escala Global)"]
- integracao: ["Nenhuma", "APIs Externas", "Hardware/Sensores", "Sistemas Legados", "Mensageria/Filas"]
- arquitetura_esperada: ["Monolito Simples", "Monolito Modular", "Microsserviços", "Serverless", "Event-Driven"]
- requisitos_desempenho: ["Padrão (CRUD)", "Alto (Processamento pesado)", "Tempo Real (Streaming/WebSockets)", "Baixa Latência"]
- experiencia_usuario: ["Iniciante", "Intermediário", "Avançado"]
- requisitos_seguranca: ["Padrão", "Alta (Dados Sensíveis/LGPD)", "Crítica (Financeiro)"]

```

### Preparando o ambiente
#### Instalação do OLLAMA e modelos
- O Ollama é o programa que funciona como um motor para rodar modelos LLMs localmente no computador. 
- Ele funciona como um servidor local e permite baixar, gerencias e executar os modelos. 
- Foi instalado o programa [Ollama](ollama.com) do site oficial para rodar os modelos localmente. 
- Após a instalação basta executar o prompt para rodar um modelo (caso o modelo não esteja pré instalado, o download é realizado)
```
ollama run llama3
```

#### Configurar depois a Etapa 1 pra rodar com uma API na nuvem


