### Modelos candidatos a serem utilizados
- BERT (NER/Classificação) -> Compreender o texto de entrada do usuário e rotular em termos específicos baseados em compressão de significado.
	- É necessário um conjunto de dados inicial com exemplos de frases rotuladas para o treinamento/ajuste do modelo. 
	- Não será utilizado, mas é interessante citar no texto, pois é relevante na bibliografia sobre processamento de linguagem natural. 
- LLaMA (Prompting) -> Processar o texto através de instruções (prompts) para gerar a estrutura de saída diretamente. 
	- É necessário definir um prompt estruturado para guiar a geração e mitigar risco de imprecisões ou alucinações. 

### O que essa etapa retorna?
- É a camada de entrada do sistema. 
- O objetivo é receber o texto livre do usuário, validar se a entrada perence ao domínio de engenharia de software e gerar um dicionário estruturado de requisitos.


### Atributos de saída para a etapa 1
- **tipo_projeto** — natureza da interface ou entrega principal do sistema
- **dominio_negocio** — contexto de negócio em que o sistema está inserido
- **persistencia** — como e onde os dados do sistema serão armazenados
- **escala** — volume esperado de acessos simultâneos ou de processamento
- **integracao** — necessidade de conexão com serviços ou sistemas externos
- **arquitetura_esperada** — estilo arquitetural do sistema
- **experiencia_usuario** — nível de complexidade esperado para a interface e interação com o usuário
- **requisitos_seguranca** — nível de preocupação com segurança, autenticação e proteção de dados
- **ambiente_implantacao** — onde o sistema será executado e hospedado
- **maturidade_equipe** — nível de experiência técnica da equipe de desenvolvimento
- **tipo_autenticacao** — mecanismo de autenticação e controle de acesso do sistema
- **ciclo_desenvolvimento** — horizonte e ritmo esperado de desenvolvimento

### Prompt para LLM (modelos de IA)
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
- **arquitetura_esperada**: "monolito" | "microsservicos" | "serverless" | "event_driven" 
- **experiencia_usuario**: "basica" | "intermediaria" | "avancada" 
- **requisitos_seguranca**: "nenhum" | "basico" | "intermediario" | "avancado" 
- **ambiente_implantacao**: "local" | "cloud" | "on_premise" | "hibrido" 
- **maturidade_equipe**: "iniciante" | "intermediario" | "experiente"
- **tipo_autenticacao**: "nenhuma" | "propria" | "oauth" | "enterprise"
- **ciclo_desenvolvimento**: "mvp" | "iterativo" | "longo_prazo"
```


- O prompt sugerido poderia ser algo como: 
```
Você é um especialista em engenharia de requisitos de software. Analise a entrada do usuário e extraia exatamente 12 atributos, retornando **somente** um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.

### Atributos e Valores Permitidos (Escolha ESTRITAMENTE desta lista):

- **tipo_projeto**: "web" | "mobile" | "desktop" | "api" | "embarcado" | "hibrido"
- **dominio_negocio**: "produtividade" | "financeiro" | "saude" | "educacao" | "ecommerce" | "logistica" | "entretenimento" | "outro"
- **persistencia**: "sem_banco" | "sql" | "nosql" | "hibrido"
- **escala**: "pequena" | "media" | "grande" | "enterprise"
- **integracao**: "nenhuma" | "apis_externas" | "servicos_internos" | "ambos"
- **arquitetura_esperada**: "monolito" | "microsservicos" | "serverless" | "event_driven"
- **experiencia_usuario**: "basica" | "intermediaria" | "avancada"
- **requisitos_seguranca**: "nenhum" | "basico" | "intermediario" | "avancado"
- **ambiente_implantacao**: "local" | "cloud" | "on_premise" | "hibrido"
- **maturidade_equipe**: "iniciante" | "intermediario" | "experiente"
- **tipo_autenticacao**: "nenhuma" | "propria" | "oauth" | "enterprise"
- **ciclo_desenvolvimento**: "mvp" | "iterativo" | "longo_prazo"

### Regras de preenchimento:

1. Use apenas os valores listados acima para cada atributo.
2. Se um atributo não for mencionado, escolha o valor mais **simples e comum** para o contexto descrito.
3. **Nunca** retorne campos nulos, vazios ou fora da lista de valores permitidos.
4. **Nunca** adicione texto fora do JSON.

### Entrada do usuário:
"{ENTRADA}"

### Saída esperada (somente JSON):
```
https://gist.github.com/em4nuelvt/c174bc079d537a51e99e508b919835e0
### Preparando o ambiente
#### Instalação do OLLAMA e modelos
- O Ollama é o programa que funciona como um motor para rodar modelos LLMs localmente no computador. 
- Ele funciona como um servidor local e permite baixar, gerencias e executar os modelos. 
- Foi instalado o programa [Ollama](ollama.com) do site oficial para rodar os modelos localmente. 
- Após a instalação basta executar o prompt para rodar um modelo (caso o modelo não esteja pré instalado, o download é realizado)
```
ollama run llama3
```



### Relação de códigos desenvolvidos

#### Classe RequirementExtractor.py
Classe responsável por fazer a extração de requisitos.
Ela recebe a entrada do usuário e pode receber o modelo a ser utilizado para construir o prompt completo passado para execução do modelo e retorna a resposta. 
Foi modelada como classe para ser reaproveitada em outros scripts. 
#### main.py
Onde executa o sistema de recomendação principal. 
#### requirement_extractor_benchmark.py
Script criado para extrair dados de teste para variação de 5 entradas definidas, 30 vezes por modelo, para os 3 modelos escolhidos para teste.
Explicado em detalhes em  [[Teste de modelos - Métricas utilizadas]].

#### user_input.py
Script criado para adicionar as entradas que serão utilizadas para testar os modelos.
Cria uma lista de inputs. Os testes percorrem essa lista para serem executados. 

#### compute_ground_truth
Lê o arquivo gerado por requirement_extractor_benchmark e aplica _majority vote_: para cada par (caso de teste, atributo), soma os votos de todas as execuções válidas dos três modelos e elege o valor mais frequente como resposta sugerida. Gera o gabarito sugerido e uma distribuição dos votos para análise. 

#### accuracy_report
Lê o arquivo gerado por requirement_extractor_benchmark com os resultados de teste e também lê um gabarito de resultado esperado para os inputs para validar a acurácia da classificação de requisitos das entradas. Gera o arquivo `accuracy_report.txt` com acurácia por modelo/caso, por modelo consolidado, por atributo (indicando quais atributos os modelos mais erram) e ranking


### Breve análise de resultados
Os testes realizados avaliaram os modelos em duas dimensões: conformidade de saída, que verifica se a resposta segue o esquema definido e acurácia semântica, que compara os valores extraídos com um gabarito de referência.

Os modelos deep seek e o qwen retornaram sempre saídas válidas dentro do escopo definido: retorno de um json com os atributos/requisitos de software devidamente classificados de acordo com a entrada. 
O deep seek foi o melhor modelo no quesito de validação do formato da saída, pois apresentou todas saídas válidas em todos os processamentos. Além disso, foi o que teve menor tempo médio de execução. O qwen também foi consistente e apresentou saídas válidas. Entretanto, o Llama já não apresentou a saída dentro do escopo válido para todos os casos de teste, sendo assim o pior classificado dentro dos modelos testados. 

Ao analisar somente as execuções válidas, verificou-se também a acurácia do modelo para 5 entradas distintas e seus respectivos "gabaritos", ou seja, a saída esperada para cada um deles. Nesse cenário, observou-se que alguns dos atributos não tiveram constância nas respostas. Dependendo da entrada informada, o modelo pode ter que inferir um atributo e isso naturalmente faz com que haja variação da resposta para atributos específicos para entradas específicas.
- Atribuos determináveis são inferíveis diretamente da entrada, para o teste se destacaram atributos como 'tipo_projeto' e 'dominio_negocio'. 
- Já atributos de inferência contextual são atributos que não foram mencionados explicitramente pelo usuário e o modelo precisa inferir com base no contexto da entrada. Dessa forma pode ser possível que haja mais de uma resposta válida. 

Conclusões interessantes:
- qwen2.5 lidera em acurácia média (71.72%), mas deepseek-r1:8b tem mais execuções 100% corretas (6 vs 1) — isso sugere que o deepseek é mais preciso quando acerta, mas menos consistente.
- llama3 tem dupla desvantagem: menor acurácia (62.84%) e menor taxa de formato válido (70–93%), tornando-o menos confiável
- Os resultados de 62–72% de acurácia são razoáveis considerando que vários atributos dependem de interpretação subjetiva. Para atributos explícitos, a acurácia seria muito maior
- A consistência é baixa para todos os modelos, o que indica que eles não apresentam sempre a mesma saída para uma mesma entrada. Modelos LLMs são não-determinísticos por padrão, então, nesse cenário de testes onde ele precisa inferir algumas informações para classificar os atributos, é justificável variações nas respostas. 

#### Configurar depois a Etapa 1 pra rodar com uma API na nuvem -> Ideia para fazer assim que ja tiver finalizado

#### Resumo: 
Atualmente o protótipo da etapa 1 de classificação de entrada do usuário utilizando modelos de LLM está pronto. 
A ideia é testar essa etapa com 3 modelos de LLM selecionados: Llama3, qwen2.5 e o deepseek 
Atualização: os testes foram executados, mas os modelos apresentaram muita variação. 






