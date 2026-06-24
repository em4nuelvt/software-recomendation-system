import pandas as pd
import json
import networkx as nx
from collections import defaultdict
import os

# Mapeamento dos nomes do Survey para os IDs do nosso grafo
TECH_MAPPING = {
    # Linguagens
    "Python": "python",
    "JavaScript": "javascript",
    "TypeScript": "typescript",
    "Java": "java",
    "C#": "csharp",
    "PHP": "php",
    "Go": "go",
    "Kotlin": "kotlin",
    "Swift": "swift",
    "Ruby": "ruby",
    "Dart": "dart",
    "Rust": "rust",
    "C++": "cpp",
    "C": "c",
    # Frameworks web/back/front
    "Django": "django",
    "Flask": "flask",
    "FastAPI": "fastapi",
    "Express": "express",
    "NestJS": "nestjs",
    "Spring Boot": "spring",
    "Laravel": "laravel",
    "Ruby on Rails": "rails",
    "ASP.NET Core": "aspnet",
    "React": "react",
    "Vue.js": "vue",
    "Angular": "angular",
    "Svelte": "svelte",
    "Next.js": "nextjs",
    "Nuxt.js": "nuxtjs",
    "jQuery": "jquery",
    # Bancos de dados
    "PostgreSQL": "postgresql",
    "MySQL": "mysql",
    "SQLite": "sqlite",
    "MongoDB": "mongodb",
    "Redis": "redis",
    "Firebase Realtime Database": "firebase_rt",
    "Amazon DynamoDB": "dynamodb",
    "MariaDB": "mariadb",
    "Microsoft SQL Server": "sqlserver",
    # Infra
    "Docker": "docker",
    "Kubernetes": "kubernetes",
    "Amazon Web Services (AWS)": "aws",
    "Google Cloud": "gcp",
    "Microsoft Azure": "azure",
    "Heroku": "heroku",
    "Vercel": "vercel",
    "Elixir": "elixir",
    "Scala": "scala",
    "Apache Kafka": "kafka",
    "RabbitMQ": "rabbitmq",
    "Cassandra": "cassandra",
    "Neo4j": "neo4j"
    # Nginx e alguns mobile framework talvez não correspondam exatamente ou não estejam em categorias obvias,
    # vamos pegar o que casar exatamente.
}

def process_survey(csv_path: str, manual_graph_path: str, output_graph_path: str):
    print("Carregando CSV (isso pode demorar um pouco)...")
    df = pd.read_csv(csv_path, usecols=[
        "LanguageHaveWorkedWith", 
        "WebframeHaveWorkedWith", 
        "DatabaseHaveWorkedWith", 
        "PlatformHaveWorkedWith"
    ])
    
    # Preencher NaN com string vazia
    df.fillna("", inplace=True)
    
    tech_counts = defaultdict(int)
    pair_counts = defaultdict(int)

    print("Processando respostas do Survey...")
    for idx, row in df.iterrows():
        # Juntar todas as respostas do usuário em uma única lista
        user_techs_raw = []
        for col in df.columns:
            if row[col]:
                user_techs_raw.extend([t.strip() for t in row[col].split(";")])
        
        # Mapear para nossos IDs e remover duplicatas
        user_techs = set()
        for raw in user_techs_raw:
            if raw in TECH_MAPPING:
                user_techs.add(TECH_MAPPING[raw])
                
        user_techs = list(user_techs)
        
        # Incrementar contagem individual
        for t in user_techs:
            tech_counts[t] += 1
            
        # Incrementar pares
        for i in range(len(user_techs)):
            for j in range(i + 1, len(user_techs)):
                t1, t2 = user_techs[i], user_techs[j]
                if t1 > t2:
                    t1, t2 = t2, t1 # Garantir ordem para o par
                pair_counts[(t1, t2)] += 1

    print("Calculando co-ocorrências condicionais...")
    survey_edges = {}
    for (t1, t2), count in pair_counts.items():
        if tech_counts[t1] == 0 or tech_counts[t2] == 0:
            continue
        p_t2_given_t1 = count / tech_counts[t1]
        p_t1_given_t2 = count / tech_counts[t2]
        
        score = max(p_t2_given_t1, p_t1_given_t2)
        if score > 0.1: # Ignorar co-ocorrências muito baixas para não poluir o grafo
            survey_edges[(t1, t2)] = score

    print("Mesclando com o grafo manual...")
    with open(manual_graph_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    G = nx.node_link_graph(data)
    
    # Obter arestas manuais COMPATIVEL_COM existentes (como um set de pares ordenados alfabeticamente)
    manual_compativel = {}
    for u, v, attrs in G.edges(data=True):
        if attrs.get("relacao") == "COMPATIVEL_COM":
            t1, t2 = u, v
            if t1 > t2:
                t1, t2 = t2, t1
            manual_compativel[(t1, t2)] = attrs.get("peso", 0.0)

    # Processar todas as arestas do survey
    for (t1, t2), survey_weight in survey_edges.items():
        if (t1, t2) in manual_compativel:
            manual_weight = manual_compativel[(t1, t2)]
            # Media ponderada: 0.6 manual + 0.4 survey (favorece curadoria especialista)
            final_weight = 0.6 * manual_weight + 0.4 * survey_weight
        else:
            # Se não existia manual, o peso final é só o do survey com penalidade
            # para que dados puramente de popularidade não dominem arestas curadas
            final_weight = 0.5 * survey_weight
            
        # Atualiza o grafo
        if G.has_node(t1) and G.has_node(t2):
            if G.has_edge(t1, t2):
                if G.edges[t1, t2].get("relacao") == "COMPATIVEL_COM":
                    G[t1][t2]["peso"] = round(final_weight, 3)
                    G[t1][t2]["fonte"] = "survey_merged"
            else:
                G.add_edge(t1, t2, relacao="COMPATIVEL_COM", peso=round(final_weight, 3), fonte="survey_only")
                
            # Adicionar a volta, já que COMPATIVEL_COM é bidirecional
            if G.has_edge(t2, t1):
                if G.edges[t2, t1].get("relacao") == "COMPATIVEL_COM":
                    G[t2][t1]["peso"] = round(final_weight, 3)
                    G[t2][t1]["fonte"] = "survey_merged"
            else:
                G.add_edge(t2, t1, relacao="COMPATIVEL_COM", peso=round(final_weight, 3), fonte="survey_only")

    # Manter arestas manuais que não apareceram no survey? (ex: manual_weight não tocado)
    # Como elas já estão no grafo com fonte="manual", não precisamos fazer nada, o peso delas continua o manual.

    print(f"Salvando grafo final em {output_graph_path}...")
    final_data = nx.node_link_data(G)
    with open(output_graph_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
        
    print("Processamento concluído!")

if __name__ == "__main__":
    import os
    # Obter o diretório pai da pasta 'scripts' (que é a pasta 'src')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "results.csv")
    manual_graph_path = os.path.join(base_dir, "data", "graph", "knowledge_graph_manual.json")
    output_graph_path = os.path.join(base_dir, "data", "graph", "knowledge_graph.json")
    process_survey(csv_path, manual_graph_path, output_graph_path)
