
# Diretrizes de Classificação
# Descrição dos 12 Atributos de Requisitos

## Atributos Primários (Maior Peso na Decisão Arquitetural)

### 1. `tipo_projeto`
*O que classifica:* A plataforma principal de entrega e interação do software. Define como o usuário final utilizará o produto.
* **web**: Aplicações acessadas via navegador (ex: SPAs, portais).
* **mobile**: Aplicativos nativos ou cross-platform para smartphones (iOS/Android).
* **desktop**: Software instalável rodando diretamente no sistema operacional do usuário (Windows/Mac/Linux).
* **api**: Sistemas *headless* focados em prover dados ou serviços para outros clientes.
* **embarcado**: Software rodando em hardware específico (IoT, microcontroladores).
* **hibrido**: Sistemas que misturam plataformas (ex: PWA ou App que encapsula Web).

### 2. `dominio_negocio`
*O que classifica:* A área de atuação, setor da indústria ou propósito principal que define as regras de negócio do sistema.
* **produtividade**: Ferramentas de gestão, tarefas, colaboração.
* **financeiro**: Fintechs, bancos, transações com alta consistência.
* **saude**: Prontuários, telemedicina (exige alto sigilo).
* **educacao**: E-learning, plataformas EAD, gestão escolar.
* **ecommerce**: Lojas virtuais, carrinhos de compra, gateways de pagamento.
* **logistica**: Rastreamento, gestão de frotas, estoques.
* **entretenimento**: Jogos, streaming de mídia, redes sociais.
* **outro**: Quando a descrição não se encaixa claramente em nenhuma das anteriores.

### 3. `persistencia`
*O que classifica:* O paradigma de armazenamento de dados e necessidade de estruturação.
* **sem_banco**: Aplicações estáticas ou que não retêm estado próprio (ex.: calculadoras simples).
* **sql**: Dados altamente estruturados, necessidade de transações ACID e relacionamentos claros (ex.: PostgreSQL, MySQL).
* **nosql**: Dados não estruturados, documentos flexíveis ou foco em alta performance e escalabilidade horizontal (ex.: MongoDB, Redis).
* **hibrido**: Projetos complexos que usam relacionais para regras de negócio e NoSQL para cache ou grandes volumes. 

### 4. `escala`
*O que classifica:* O volume esperado de usuários utilizando de forma concorrente, tráfego e processamento de dados.
* **pequena**: Uso interno de pequenas equipes, centenas de usuários, pouco processamento.
* **media**: Uso regional, milhares de usuários, picos moderados de tráfego.
* **grande**: Escala nacional/global, dezenas a centenas de milhares de acessos, necessidade de balanceamento de carga e cache.
* **enterprise**: Sistemas críticos de missão corporativa global. Milhões de requisições, alta disponibilidade (99.99% uptime), tolerância a falhas rigorosa.

---

## Atributos de Suporte (Refinamento da Stack)

### 5. `integracao`
*O que classifica:* O nível de comunicação do sistema com o mundo externo ou interno.
* **nenhuma**: Sistema isolado, não consome APIs nem se comunica com outros módulos.
* **apis_externas**: Consome serviços de terceiros (ex: gateways de pagamento, APIs de clima, mapas).
* **servicos_internos**: Comunica-se com outros microsserviços ou legados dentro da mesma empresa.
* **ambos**: Necessita lidar tanto com infraestrutura interna quanto integrações de terceiros.

### 6. `arquitetura_esperada`
*O que classifica:* O padrão arquitetural de alto nível projetado para o backend.
* **monolito**: Código e banco de dados centralizados em uma única base de implantação. Bom para MVP e complexidade baixa/média.
* **microsservicos**: Domínios de negócios separados em múltiplos serviços independentes (bom para equipes grandes e escalabilidade isolada).
* **serverless**: Foco em funções sob demanda (FaaS) e infraestrutura totalmente gerenciada pela nuvem (cobrança por uso).
* **event_driven**: Sistemas altamente reativos baseados em mensageria (Kafka, RabbitMQ) onde as ações são guiadas por eventos.

### 7. `experiencia_usuario` (UX/UI)
*O que classifica:* A complexidade e interatividade demandada para o frontend.
* **basica**: Interfaces simples, focadas em funcionalidade, formulários tradicionais (CRUD), renderização no servidor.
* **intermediaria**: Necessidade de componentes responsivos, certa dinamicidade (modais, validações em tempo real).
* **avancada**: Alta reatividade, atualizações em tempo real (WebSockets), animações fluidas, comportamento de Single Page Application (SPA).

### 8. `requisito_seguranca`
*O que classifica:* O rigor com proteção de dados, acessos e conformidade (compliance).
* **nenhum**: Dados públicos, sem restrição de acesso crítica.
* **basico**: Login simples (usuário e senha), criptografia trivial de dados sensíveis.
* **intermediario**: Controle de permissões (RBAC), proteção contra injeções comuns, dados sensíveis criptografados ativamente.
* **avancado**: Conformidade com LGPD/GDPR, grau bancário/saúde, auditoria de trilhas, testes de penetração constantes, HSM.

### 9. `ambiente_implantacao`
*O que classifica:* Onde o software será hospedado e rodado.
* **local**: Roda estritamente na máquina do usuário, sem servidores.
* **cloud**: Implantado nativamente em provedores de nuvem (AWS, GCP, Azure), utilizando recursos elásticos.
* **on_premise**: Implantado em servidores físicos (datacenter) controlados pela própria empresa, geralmente por razões de segurança ou restrições legais.
* **hibrido**: Parte do sistema roda na infraestrutura privada (dados sensíveis) e parte na nuvem elástica (processamento).

### 10. `maturidade_equipe`
*O que classifica:* O nível de senioridade ou experiência técnica do time que desenvolverá e manterá o sistema. Impacta diretamente se uma stack complexa ou simples será recomendada.
* **iniciante**: Foco em frameworks muito opinativos, fáceis de usar, com muita convenção e menos configuração.
* **intermediario**: Equipe consegue lidar com arquiteturas separadas, integrações modernas.
* **experiente**: Equipe madura, capaz de configurar microsserviços do zero, lidar com infraestrutura as code, Kubernetes, pipelines complexos.

### 11. `tipo_autenticacao`
*O que classifica:* Como a identidade do usuário será gerenciada.
* **nenhuma**: Acesso anônimo ou sistema aberto.
* **propria**: Gestão interna de identidade (banco de dados próprio, sessões/JWT gerados pelo próprio backend).
* **oauth**: Login via provedores sociais (Google, Facebook, Apple, GitHub) para redução de atrito no cadastro.
* **enterprise**: SSO (Single Sign-On), integração com Active Directory, SAML, Keycloak (comum em software corporativo interno).

### 12. `ciclo_desenvolvimento`
*O que classifica:* O prazo, urgência e a metodologia principal do ciclo de vida do software.
* **mvp**: Produto Mínimo Viável. Prioridade altíssima na velocidade de entrega para testar o mercado (sacrifica escalabilidade precoce por tempo de desenvolvimento).
* **iterativo**: Desenvolvimento contínuo de médio prazo (Agile), balanceando entrega de valor com qualidade do código.
* **longo_prazo**: Sistemas desenhados para durar décadas, foco extremo em manutenibilidade, design patterns robustos (DDD, Clean Architecture), onde a arquitetura é pensada antes da codificação ágil.
--- 

## Gabarito esperado para cada caso de entrada de teste

Abaixo estão listadas as entradas de teste reais utilizadas na execução das métricas. Para cada caso: a entrada original, o gabarito esperado e, em seguida, quais classificações alternativas ainda são aceitáveis e a justificativa.

### Caso 1
**Entrada:**
```
Tecnologias para sistema de lista de tarefas web
```


**Valor de referência**
```json
{
    "tipo_projeto": "web",
    "dominio_negocio": "produtividade",
    "persistencia": "sql",
    "escala": "pequena",
    "integracao": "nenhuma",
    "arquitetura_esperada": "monolito",
    "experiencia_usuario": "basica",
    "requisito_seguranca": "basico",
    "ambiente_implantacao": "cloud",
    "maturidade_equipe": "iniciante",
    "tipo_autenticacao": "propria",
    "ciclo_desenvolvimento": "mvp"
}
```

**Classificações Alternativas Aceitáveis:**

| Atributo | Alternativa(s) | Justificativa |
|---|---|---|
| `persistencia` | `sem_banco` | A entrada é muito curta e não menciona armazenamento. Um modelo pode inferir que uma lista de tarefas simples usa apenas armazenamento local (localStorage, arquivo). |
| `escala` | `media` | A entrada não especifica o número de usuários. 'Lista de tarefas web' pode ser um SaaS multi-usuário com escala média. |
| `integracao` | `apis_externas` | Sistemas de produtividade modernos frequentemente integram APIs de calendário ou notificação (Google Calendar, Slack). A entrada não descarta isso. |
| `arquitetura_esperada` | `serverless` | Para uma aplicação web simples e pequena, serverless (ex: AWS Lambda + frontend estático) é uma escolha moderna e razoável. |
| `requisito_seguranca` | `nenhum` | A entrada não menciona autenticação, login ou proteção de dados. Um modelo pode inferir ausência de requisito de segurança em uma ferramenta pessoal simples. |
| `ambiente_implantacao` | `local` | Não há menção de hospedagem. Modelos tendem a assumir 'local' para sistemas simples sem contexto de deployment. |
| `tipo_autenticacao` | `nenhuma` | Nenhuma autenticação é mencionada. O gabarito assume login próprio, mas um modelo pode inferir que uma lista de tarefas simples é de uso pessoal/aberto. |
| `maturidade_equipe` | `intermediario` | A entrada não fornece nenhum contexto sobre a equipe. 'Iniciante' e 'intermediario' são igualmente plausíveis. |
| `ciclo_desenvolvimento` | `iterativo` | Sem contexto de prazo ou metodologia, 'iterativo' é igualmente razoável para um sistema web com evolução contínua. |

### Caso 2
**Entrada:**
```
Gostaria de desenvolver um aplicativo para Android e iOS sobre o esporte badminton, com foco no apoio ao ensino nas aulas de Educação Física. O aplicativo deve conter informações sobre equipamentos, regras oficiais e tutoriais de como jogar.
```
**Valor de referência**
```json
{
    "tipo_projeto": "mobile",
    "dominio_negocio": "educacao",
    "persistencia": "sem_banco",
    "escala": "pequena",
    "integracao": "nenhuma",
    "arquitetura_esperada": "monolito",
    "experiencia_usuario": "intermediaria",
    "requisito_seguranca": "nenhum",
    "ambiente_implantacao": "local",
    "maturidade_equipe": "iniciante",
    "tipo_autenticacao": "nenhuma",
    "ciclo_desenvolvimento": "mvp"
}
```

**Classificações Alternativas Aceitáveis:**

| Atributo | Alternativa(s) | Justificativa |
|---|---|---|
| `persistencia` | `sql` | A entrada menciona 'informações sobre equipamentos, regras e tutoriais', que podem ser gerenciadas em banco de dados relacional para facilitar atualizações. |
| | `nosql` | Conteúdo educacional estático (tutoriais, regras) pode ser armazenado em documentos NoSQL. |
| `escala` | `media` | Um aplicativo educativo para Android e iOS pode alcançar escala nacional se adotado em redes escolares. |
| `integracao` | `apis_externas` | Apps educativos frequentemente integram APIs de vídeo (YouTube) ou plataformas de conteúdo externas para exibir tutoriais. |
| `arquitetura_esperada` | `serverless` | Um app de conteúdo estático com backend mínimo é candidato natural a serverless. |
| `experiencia_usuario` | `basica` | O app exibe informações estáticas (regras, tutoriais). Pode ser classificado como interface básica sem interatividade elevada. |
| `ambiente_implantacao` | `cloud` | Aplicativos mobile distribuídos via App Store/Play Store dependem de backend em nuvem. Um modelo pode associar 'mobile' a 'cloud'. |
| `maturidade_equipe` | `intermediario` | Sem contexto da equipe, 'iniciante' e 'intermediario' são igualmente plausíveis. |
| `ciclo_desenvolvimento` | `iterativo` | App educativo com updates de conteúdo contínuos pode ser interpretado como ciclo iterativo. |

### Caso 3
**Entrada:**

```
Gostaria de desenvolver um sistema de gestão para clínicas médicas, acessível por qualquer plataforma por meio de um site na internet. O sistema deve armazenar dados de pacientes, médicos, consultas, exames e informações financeiras.
```

**Valor de referência**
```json
{
    "tipo_projeto": "web",
    "dominio_negocio": "saude",
    "persistencia": "sql",
    "escala": "media",
    "integracao": "nenhuma",
    "arquitetura_esperada": "monolito",
    "experiencia_usuario": "intermediaria",
    "requisito_seguranca": "avancado",
    "ambiente_implantacao": "cloud",
    "maturidade_equipe": "intermediario",
    "tipo_autenticacao": "propria",
    "ciclo_desenvolvimento": "iterativo"
}
```

**Classificações Alternativas Aceitáveis:**

| Atributo | Alternativa(s) | Justificativa |
|---|---|---|
| `escala` | `grande` | 'Clínicas médicas' no plural e acesso por 'qualquer plataforma' pode sugerir um sistema multi-clínica com grande volume de dados. |
| `integracao` | `apis_externas` | Sistemas de saúde frequentemente integram planos de saúde, laboratórios ou sistemas de prontuário eletrônico (RNDS). |
| | `ambos` | A integração pode ser tanto com sistemas externos (planos, labs) quanto com módulos internos (financeiro, agenda). |
| `arquitetura_esperada` | `microsservicos` | A menção de múltiplos domínios distintos (pacientes, médicos, consultas, exames, financeiro) pode sugerir separação em microsserviços. |
| `requisito_seguranca` | `intermediario` | Dados de saúde exigem proteção, mas a entrada não menciona auditoria ou conformidade com LGPD explicitamente. Um modelo conservador pode inferir 'intermediario'. |
| `tipo_autenticacao` | `oauth` | Sistemas de saúde modernos adotam login federado (Google Workspace hospitalar, Microsoft 365). Sem contexto, 'oauth' é razoável. |
| | `enterprise` | Ambientes hospitalares corporativos frequentemente usam SSO/Active Directory, o que justificaria 'enterprise'. |
| `ciclo_desenvolvimento` | `longo_prazo` | Um sistema de gestão clínica com múltiplos módulos pode ser lido como projeto de longa duração e manutenção contínua. |

### Caso 4
**Entrada:**
```
Quero desenvolver um sistema para controle de horas complementares no ambiente acadêmico, acessível pela internet. Cada aluno deve cadastrar seu perfil e curso, além de gerenciar as horas necessárias para concluir a graduação. 
```

**Valor de referência**
```json
{
    "tipo_projeto": "web",
    "dominio_negocio": "educacao",
    "persistencia": "sql",
    "escala": "media",
    "integracao": "nenhuma",
    "arquitetura_esperada": "monolito",
    "experiencia_usuario": "intermediaria",
    "requisito_seguranca": "basico",
    "ambiente_implantacao": "cloud",
    "maturidade_equipe": "iniciante",
    "tipo_autenticacao": "propria",
    "ciclo_desenvolvimento": "iterativo"
}
```

**Classificações Alternativas Aceitáveis:**

| Atributo | Alternativa(s) | Justificativa |
|---|---|---|
| `escala` | `pequena` | Um sistema para controle de horas de uma única instituição com poucos alunos pode ser considerado pequena escala. |
| `integracao` | `servicos_internos` | Sistemas acadêmicos frequentemente se integram com a secretaria, sistemas de matrícula ou portais institucionais internos. |
| `requisito_seguranca` | `intermediario` | Dados de alunos e progresso acadêmico podem requerer proteção intermediária (controle de acesso por perfil, criptografia de dados). |
| `ambiente_implantacao` | `on_premise` | Instituições de ensino com infraestrutura própria frequentemente hospedam sistemas acadêmicos em servidores locais. |
| `tipo_autenticacao` | `oauth` | Instituições de ensino frequentemente adotam login via conta institucional Google/Microsoft, o que tornaria 'oauth' razoável. |
| `maturidade_equipe` | `intermediario` | Sem contexto da equipe, 'iniciante' e 'intermediario' são igualmente plausíveis. |

### Caso 5
**Entrada:**
```
Quero construir um jogo da memória para computadores desktop, utilizando conceitos de sistemas distribuídos. Os jogadores devem se comunicar entre si por meio de um servidor middleware.
```

**Valor de referência**
```json
{
    "tipo_projeto": "desktop",
    "dominio_negocio": "entretenimento",
    "persistencia": "sem_banco",
    "escala": "pequena",
    "integracao": "servicos_internos",
    "arquitetura_esperada": "event_driven",
    "experiencia_usuario": "basica",
    "requisito_seguranca": "nenhum",
    "ambiente_implantacao": "local",
    "maturidade_equipe": "intermediario",
    "tipo_autenticacao": "nenhuma",
    "ciclo_desenvolvimento": "iterativo"
}
```

**Classificações Alternativas Aceitáveis:**

| Atributo | Alternativa(s) | Justificativa |
|---|---|---|
| `persistencia` | `sql` | Um jogo com múltiplos jogadores pode precisar registrar partidas, pontuações ou histórico de sessões em banco de dados. |
| | `nosql` | Dados de sessão de jogo (estado das cartas, jogadores conectados) se encaixam bem em documentos NoSQL ou cache. |
| `integracao` | `ambos` | O servidor middleware é um serviço interno, mas o jogo pode também integrar APIs externas (ex: autenticação, ranking online). |
| `arquitetura_esperada` | `microsservicos` | Servidor middleware separado dos clientes pode ser interpretado como arquitetura de microsserviços, com serviços independentes de jogo e comunicação. |
| `requisito_seguranca` | `basico` | A comunicação entre jogadores via servidor pode ser interpretada como necessitando de autenticação mínima de sessão. |
| `maturidade_equipe` | `experiente` | O uso de sistemas distribuídos e middleware sugere conhecimento técnico elevado. Um modelo pode inferir 'experiente' para esse contexto. |
| `ciclo_desenvolvimento` | `mvp` | Projetos acadêmicos geralmente têm prazo fixo e entrega única, o que sugere MVP em vez de desenvolvimento iterativo contínuo. |
| `ambiente_implantacao` | `on_premise` | O servidor middleware pode ser interpretado como um servidor físico controlado localmente, aproximando-se de 'on_premise'. |

### Caso 6
**Entrada:**
```
O sistema deverá ser uma plataforma acadêmica integrada, destinada à gestão das atividades administrativas, acadêmicas e pedagógicas de instituições de ensino superior, com funcionalidades de matrícula em disciplinas, visualização de notas e frequência em disciplinas. A solução deverá ser desenvolvida em arquitetura web responsiva, permitindo acesso por computadores, tablets e dispositivos móveis, com autenticação segura e controle de acesso baseado em perfis de usuário. As instituições que utilizarão o sistema estão distribuídas geograficamente e apresentam volumes distintos de cursos, departamentos, docentes e discentes a cada período letivo. O período de matrícula pode apresentar picos de concorrência e é crítico para o funcionamento institucional.

O sistema deverá contemplar, no mínimo, os perfis de administrador, gestor acadêmico, coordenador de curso, professor e estudante. Dessa forma, deve permitir que cada usuário visualize e execute somente as funcionalidades compatíveis com suas atribuições. O cadastro acadêmico deverá armazenar informações de estudantes, professores, cursos, matrizes curriculares, componentes curriculares, departamentos, períodos letivos, turmas, horários, salas e demais dados necessários ao funcionamento institucional.

O módulo de **gestão de cursos e currículos** deverá permitir cadastrar cursos, estruturas curriculares, disciplinas obrigatórias e optativas, cargas horárias, créditos, ementas, pré-requisitos, correquisitos, equivalências e regras para integralização curricular. Deverá ser possível manter diferentes versões de uma matriz curricular e identificar a estrutura à qual cada estudante está vinculado.

O módulo de matrícula deverá possibilitar oferta de turmas por período letivo, solicitação de matrícula e ajuste de matrícula pelos estudantes, verificação automática de vagas, conflitos de horário, pré-requisitos e restrições curriculares. Situações excepcionais deverão poder ser encaminhadas para análise da coordenação ou do setor responsável, mantendo histórico da solicitação, justificativa, parecer e decisão.

Para os professores, o sistema deverá disponibilizar um diário eletrônico de turma, contendo relação de estudantes matriculados, plano de ensino, registro de aulas, frequência, avaliações, notas e cálculo da situação final. Os estudantes deverão ter acesso às disciplinas cursadas, horários, notas, frequência, histórico acadêmico, integralização curricular e documentos acadêmicos disponibilizados pela instituição.

A plataforma deverá incluir recursos para gestão de requerimentos acadêmicos, tais como aproveitamento de estudos, quebra de pré-requisito, trancamento, matrícula em disciplina isolada e outras solicitações configuráveis pela instituição. Cada processo deverá possuir fluxo de tramitação, responsáveis, prazos, anexos, registro de decisões e possibilidade de acompanhamento pelo interessado.

Também deverão existir funcionalidades para emissão de relatórios e indicadores acadêmicos, incluindo número de matrículas, aprovações, reprovações, evasão, retenção, carga horária integralizada e desempenho por curso, turma ou componente curricular.

Todas as operações relevantes deverão possuir registro de auditoria, identificando usuário, data, horário e alteração realizada. O sistema deverá garantir integridade, confidencialidade e disponibilidade das informações, respeitando a legislação de proteção de dados. A arquitetura deverá ainda possibilitar integração futura com sistemas institucionais externos por meio de APIs, bem como expansão modular para funcionalidades de extensão, pesquisa, estágio, trabalho de conclusão de curso e atividades complementares.
```

**Valor de referência:**
```json
{
    "tipo_projeto": "web",
    "dominio_negocio": "educacao",
    "persistencia": "sql",
    "escala": "grande",
    "integracao": "apis_externas",
    "arquitetura_esperada": "monolito",
    "experiencia_usuario": "avancada",
    "requisito_seguranca": "avancado",
    "ambiente_implantacao": "cloud",
    "maturidade_equipe": "experiente",
    "tipo_autenticacao": "enterprise",
    "ciclo_desenvolvimento": "longo_prazo"
}
```

**Classificações Alternativas Aceitáveis:**

| Atributo                | Alternativa(s)   | Justificativa                                                                                                                                                                                                                                           |
| ----------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `escala`                | `enterprise`     | O sistema é para 'instituições de ensino superior' geograficamente distribuídas, com picos de concorrência críticos. Um modelo pode interpretar isso como escala enterprise. Este é o atributo com maior risco de ambiguidade no teste de estresse.     |
| `integracao`            | `ambos`          | A entrada menciona integração futura com sistemas externos por API E expansão para módulos internos adicionais, o que justifica 'ambos' em vez de apenas 'apis_externas'.                                                                               |
| `arquitetura_esperada`  | `microsservicos` | A estrutura em módulos bem definidos (matrícula, currículo, requerimentos, relatórios, diário eletrônico) é forte indicador de microsserviços. O gabarito assume monolito como escolha mais conservadora, mas 'microsservicos' é plenamente defensável. |
|                         | `event_driven`   | Fluxos de tramitação de requerimentos com responsáveis, prazos e notificações são padrão event-driven. Um modelo especializado pode inferir isso.                                                                                                       |
| `tipo_autenticacao`     | `oauth`          | SSO/SAML é característico de ambientes universitários, mas OAuth (via Google/Microsoft corporativo) também é amplamente adotado em instituições de ensino superior.                                                                                     |
| `maturidade_equipe`     | `intermediario`  | A complexidade da plataforma sugere equipe experiente, mas sistemas acadêmicos muitas vezes são desenvolvidos por equipes internas de maturidade intermediária.                                                                                         |
| `ciclo_desenvolvimento` | `iterativo`      | A complexidade e os múltiplos módulos apontam para longo prazo, mas um modelo pode inferir desenvolvimento ágil iterativo por módulo.                                                                                                                   |

