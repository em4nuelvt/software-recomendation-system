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
- Adicionar valores permitidos para atributos. 
- Valores enumerados por atributos auxiliam a delimitar as respostas dos modelos. O Llama e o Qwen tendem a inventar valores quando o espaço de saída é aberto. Restringir a valores fixos reduz as alucinações e facilita o pós processamento. 
- Exemplos:
```
Atributos e Valores Permitidos (Escolha ESTRITAMENTE desta lista):
- **tipo_projeto**: "web" | "mobile" | "desktop" | "api" | "embarcado" | "hibrido" 
- **dominio_negocio**: "produtividade" | "financeiro" | "saude" | "educacao" | "ecommerce" | "logistica" | "entretenimento" | "outro"
- **persistencia**: "sem_banco" | "sql" | "nosql" | "hibrido" 
- **escala**: "pequena" | "media" | "grande" | "enterprise" 
- **integracao**: "nenhuma" | "apis_externas" | "servicos_internos" | "ambos"
- **arquitetura_esperada**: "monolito" | "microsservicos" | "serverless" | "event_driven" | "mvc" 
- **requisitos_desempenho**: "baixo" | "medio" | "alto" | "critico" 
- **experiencia_usuario**: "basica" | "intermediaria" | "avancada" | "acessivel" 
- **requisitos_seguranca**: "nenhum" | "basico" | "intermediario" | "avancado"
```


- O prompt sugerido poderia ser algo como: 
```
Você é um especialista em engenharia de requisitos de software. Analise a entrada do usuário e extraia exatamente 9 atributos, retornando **somente** um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.

### Atributos e valores permitidos:

- **tipo_projeto**: "web" | "mobile" | "desktop" | "api" | "embarcado" | "hibrido"
- **dominio_negocio**: "produtividade" | "financeiro" | "saude" | "educacao" | "ecommerce" | "logistica" | "entretenimento" | "outro"
- **persistencia**: "sem_banco" | "sql" | "nosql" | "hibrido"
- **escala**: "pequena" | "media" | "grande" | "enterprise"
- **integracao**: "nenhuma" | "apis_externas" | "servicos_internos" | "ambos"
- **arquitetura_esperada**: "monolito" | "microsservicos" | "serverless" | "event_driven" | "mvc"
- **requisitos_desempenho**: "baixo" | "medio" | "alto" | "critico"
- **experiencia_usuario**: "basica" | "intermediaria" | "avancada" | "acessivel"
- **requisitos_seguranca**: "nenhum" | "basico" | "intermediario" | "avancado"

### Regras de preenchimento:

1. Use apenas os valores listados acima para cada atributo.
2. Se um atributo não for mencionado ou puder ser inferido, escolha o valor mais **simples e comum** para o contexto descrito.
3. **Nunca** retorne campos nulos, vazios ou fora da lista de valores permitidos.
4. **Nunca** adicione texto fora do JSON.

### Entrada do usuário:
"{ENTRADA}"

### Saída esperada (somente JSON):
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

#### Configurar depois a Etapa 1 pra rodar com uma API na nuvem -> Ideia para fazer assim que ja tiver finalizado

#### Resumo: 
Atualmente o protótipo da etapa 1 de classificação de entrada do usuário utilizando modelos de LLM está pronto. 
A ideia é testar essa etapa com 3 modelos de LLM selecionados: Llama3, qwen2.5 e o deepseek 


