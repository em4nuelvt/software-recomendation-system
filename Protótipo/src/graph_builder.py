import json
import networkx as nx
from pathlib import Path

def build_manual_graph(seed_path: str, output_path: str):
    # Inicializa o grafo direcionado
    G = nx.DiGraph()

    # 1. Carregar nós de tecnologia do seed
    with open(seed_path, 'r', encoding='utf-8') as f:
        technologies = json.load(f)

    for tech in technologies:
        G.add_node(tech['id'], type='technology', **tech)

    # 2. Definir e adicionar nós de atributo-valor
    atributos = {
        "tipo_projeto": ["web", "mobile", "desktop", "api", "embarcado", "hibrido"],
        "dominio_negocio": ["produtividade", "financeiro", "saude", "educacao", "ecommerce", "logistica", "entretenimento", "outro"],
        "persistencia": ["sem_banco", "sql", "nosql", "hibrido"],
        "escala": ["pequena", "media", "grande", "enterprise"],
        "integracao": ["nenhuma", "apis_externas", "servicos_internos", "ambos"],
        "arquitetura_esperada": ["monolito", "microsservicos", "serverless", "event_driven"],
        "experiencia_usuario": ["basica", "intermediaria", "avancada"],
        "requisitos_seguranca": ["nenhum", "basico", "intermediario", "avancado"],
        "ambiente_implantacao": ["local", "cloud", "on_premise", "hibrido"],
        "maturidade_equipe": ["iniciante", "intermediario", "experiente"],
        "tipo_autenticacao": ["nenhuma", "propria", "oauth", "enterprise"],
        "ciclo_desenvolvimento": ["mvp", "iterativo", "longo_prazo"]
    }

    for atributo, valores in atributos.items():
        for valor in valores:
            node_id = f"{atributo}={valor}"
            G.add_node(node_id, type='attribute-value', atributo=atributo, valor=valor)

    # 3. Adicionar arestas ADEQUADO_PARA (curadoria manual)
    # Estrutura: { tech_id: { atributo=valor: peso, ... } }
    # Pesos positivos (0.0 a 1.0) = adequação
    # Pesos negativos (-1.0 a 0.0) = penalização ativa
    adequabilidades = {
        # ════════════════════════════════════════════════
        # LINGUAGENS
        # ════════════════════════════════════════════════
        "python": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.9, "tipo_projeto=desktop": 0.5,
            "tipo_projeto=embarcado": -0.8,
            "dominio_negocio=saude": 0.9, "dominio_negocio=financeiro": 0.8,
            "dominio_negocio=educacao": 0.7, "dominio_negocio=produtividade": 0.8,
            "dominio_negocio=logistica": 0.8, "dominio_negocio=entretenimento": 0.5,
            "persistencia=sem_banco": 0.6, "persistencia=hibrido": 0.8,
            "escala=grande": 0.8, "escala=enterprise": 0.7,
            "integracao=apis_externas": 0.8,
            "arquitetura_esperada=monolito": 0.9, "arquitetura_esperada=microsservicos": 0.8,
            "arquitetura_esperada=serverless": 0.8,
            "ambiente_implantacao=local": 0.7,
            "maturidade_equipe=iniciante": 0.8,
            "ciclo_desenvolvimento=mvp": 0.8, "ciclo_desenvolvimento=iterativo": 0.8,
        },
        "javascript": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.8, "tipo_projeto=hibrido": 0.9,
            "tipo_projeto=embarcado": -1.0, "tipo_projeto=desktop": -0.5,
            "dominio_negocio=produtividade": 0.8, "dominio_negocio=educacao": 0.7,
            "dominio_negocio=entretenimento": 0.7,
            "integracao=apis_externas": 0.9,
            "arquitetura_esperada=monolito": 0.8, "arquitetura_esperada=microsservicos": 0.9,
            "arquitetura_esperada=serverless": 0.9,
            "maturidade_equipe=iniciante": 0.8,
            "tipo_autenticacao=oauth": 0.8,
            "ciclo_desenvolvimento=mvp": 0.9, "ciclo_desenvolvimento=iterativo": 0.9,
        },
        "typescript": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.9, "tipo_projeto=hibrido": 0.9,
            "tipo_projeto=embarcado": -1.0,
            "escala=media": 0.9, "escala=grande": 0.9, "escala=enterprise": 0.8,
            "integracao=apis_externas": 0.9,
            "maturidade_equipe=intermediario": 0.9,
        },
        "java": {
            "tipo_projeto=web": 0.8, "tipo_projeto=api": 0.9, "tipo_projeto=desktop": 0.7,
            "tipo_projeto=embarcado": -0.8,
            "escala=grande": 0.9, "escala=enterprise": 0.9,
            "dominio_negocio=financeiro": 0.9, "dominio_negocio=logistica": 0.9,
            "dominio_negocio=educacao": 0.7,
            "persistencia=hibrido": 0.8,
            "integracao=servicos_internos": 0.9, "integracao=ambos": 0.9,
            "arquitetura_esperada=event_driven": 0.8,
            "ambiente_implantacao=on_premise": 0.9,
            "requisitos_seguranca=avancado": 0.9,
            "maturidade_equipe=intermediario": 0.8,
            "tipo_autenticacao=enterprise": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.9,
        },
        "csharp": {
            "tipo_projeto=web": 0.8, "tipo_projeto=api": 0.9, "tipo_projeto=desktop": 0.9,
            "tipo_projeto=embarcado": -0.8,
            "escala=grande": 0.9, "escala=enterprise": 0.9,
            "integracao=servicos_internos": 0.9,
            "ambiente_implantacao=on_premise": 0.9,
            "requisitos_seguranca=avancado": 0.9,
            "maturidade_equipe=intermediario": 0.8,
            "tipo_autenticacao=enterprise": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.9,
        },
        "php": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.7,
            "tipo_projeto=embarcado": -1.0, "tipo_projeto=desktop": -1.0,
            "escala=pequena": 0.9, "escala=media": 0.8,
            "escala=enterprise": -0.7,
            "dominio_negocio=saude": 0.8, "dominio_negocio=ecommerce": 0.9,
            "dominio_negocio=educacao": 0.7,
            "maturidade_equipe=iniciante": 0.9,
            "ciclo_desenvolvimento=mvp": 0.9,
        },
        "go": {
            "tipo_projeto=api": 0.9,
            "tipo_projeto=web": -0.3,
            "escala=media": 0.9, "escala=grande": 0.9, "escala=enterprise": 0.9,
            "dominio_negocio=logistica": 0.9,
            "integracao=apis_externas": 0.9, "integracao=servicos_internos": 0.9,
            "arquitetura_esperada=microsservicos": 0.9, "arquitetura_esperada=event_driven": 0.9,
            "maturidade_equipe=experiente": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.8, "ciclo_desenvolvimento=iterativo": 0.8,
        },
        "kotlin": {
            "tipo_projeto=mobile": 0.9, "tipo_projeto=api": 0.8,
        },
        "swift": {
            "tipo_projeto=mobile": 0.9,
        },
        "ruby": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.8,
            "tipo_projeto=embarcado": -1.0, "tipo_projeto=desktop": -0.8,
            "escala=pequena": 0.9, "escala=media": 0.8,
            "dominio_negocio=saude": 0.8, "dominio_negocio=ecommerce": 0.8,
        },
        "dart": {
            "tipo_projeto=mobile": 0.9, "tipo_projeto=hibrido": 0.9,
            "experiencia_usuario=intermediaria": 0.8,
        },
        "rust": {
            "tipo_projeto=api": 0.8, "tipo_projeto=embarcado": 0.9,
            "escala=grande": 0.9,
            "persistencia=sem_banco": 0.8,
            "integracao=nenhuma": 0.7,
            "ambiente_implantacao=local": 0.8,
            "maturidade_equipe=experiente": 0.9,
        },
        "cpp": {
            "tipo_projeto=desktop": 0.9, "tipo_projeto=embarcado": 0.9,
            "tipo_projeto=web": -1.0,
            "dominio_negocio=entretenimento": 0.9,
            "persistencia=sem_banco": 0.9,
            "integracao=nenhuma": 0.8,
            "ambiente_implantacao=local": 0.9,
            "tipo_autenticacao=nenhuma": 0.9,
        },
        "c": {
            "tipo_projeto=embarcado": 0.9,
            "tipo_projeto=web": -1.0, "tipo_projeto=mobile": -1.0,
            "persistencia=sem_banco": 0.9,
            "integracao=nenhuma": 0.9,
            "ambiente_implantacao=local": 0.9,
        },
        "elixir": {
            "tipo_projeto=api": 0.9, "tipo_projeto=web": 0.7,
            "escala=grande": 0.9, "escala=enterprise": 0.8,
            "arquitetura_esperada=microsservicos": 0.9, "arquitetura_esperada=event_driven": 0.9,
            "maturidade_equipe=experiente": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.8,
        },
        "scala": {
            "tipo_projeto=api": 0.8,
            "escala=grande": 0.9, "escala=enterprise": 0.9,
            "dominio_negocio=financeiro": 0.8, "dominio_negocio=logistica": 0.8,
            "arquitetura_esperada=event_driven": 0.9,
            "maturidade_equipe=experiente": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.8,
        },

        # ════════════════════════════════════════════════
        # FRAMEWORKS BACKEND
        # ════════════════════════════════════════════════
        "django": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.7,
            "escala=pequena": 0.9, "escala=media": 0.8,
            "arquitetura_esperada=monolito": 0.9,
            "persistencia=sql": 0.9, "persistencia=hibrido": 0.7,
            "dominio_negocio=saude": 0.9, "dominio_negocio=financeiro": 0.8,
            "dominio_negocio=educacao": 0.7, "dominio_negocio=produtividade": 0.8,
            "experiencia_usuario=basica": 0.7,
            "requisitos_seguranca=basico": 0.9,
            "maturidade_equipe=iniciante": 0.8,
            "tipo_autenticacao=propria": 0.9,
            "ciclo_desenvolvimento=iterativo": 0.8,
        },
        "flask": {
            "tipo_projeto=web": 0.8, "tipo_projeto=api": 0.8,
            "escala=pequena": 0.9, "arquitetura_esperada=microsservicos": 0.8,
            "persistencia=sem_banco": 0.7,
            "experiencia_usuario=basica": 0.8,
            "integracao=nenhuma": 0.7,
            "ambiente_implantacao=local": 0.8,
            "requisitos_seguranca=nenhum": 0.8,
            "maturidade_equipe=iniciante": 0.8,
            "tipo_autenticacao=nenhuma": 0.8,
            "ciclo_desenvolvimento=mvp": 0.9,
        },
        "fastapi": {
            "tipo_projeto=api": 0.9, "escala=media": 0.9, "escala=grande": 0.8,
            "arquitetura_esperada=microsservicos": 0.9, "arquitetura_esperada=serverless": 0.8,
            "integracao=apis_externas": 0.9, "integracao=ambos": 0.8,
            "dominio_negocio=logistica": 0.8, "dominio_negocio=saude": 0.8,
            "maturidade_equipe=experiente": 0.8,
            "tipo_autenticacao=oauth": 0.9,
        },
        "express": {
            "tipo_projeto=web": 0.8, "tipo_projeto=api": 0.9,
            "escala=pequena": 0.9, "escala=media": 0.8,
            "arquitetura_esperada=microsservicos": 0.8,
            "integracao=apis_externas": 0.8,
            "requisitos_seguranca=nenhum": 0.8,
            "tipo_autenticacao=nenhuma": 0.8,
            "ciclo_desenvolvimento=mvp": 0.8, "ciclo_desenvolvimento=iterativo": 0.8,
        },
        "nestjs": {
            "tipo_projeto=api": 0.9, "escala=media": 0.9, "escala=grande": 0.8,
            "arquitetura_esperada=microsservicos": 0.9, "arquitetura_esperada=monolito": 0.8,
            "integracao=apis_externas": 0.8, "integracao=ambos": 0.8,
            "dominio_negocio=logistica": 0.8,
            "requisitos_seguranca=intermediario": 0.8,
            "maturidade_equipe=intermediario": 0.9,
            "tipo_autenticacao=oauth": 0.9,
            "ciclo_desenvolvimento=iterativo": 0.9,
        },
        "spring": {
            "tipo_projeto=api": 0.9, "tipo_projeto=web": 0.8,
            "escala=grande": 0.9, "escala=enterprise": 0.9,
            "arquitetura_esperada=microsservicos": 0.9, "arquitetura_esperada=monolito": 0.8,
            "arquitetura_esperada=event_driven": 0.8,
            "persistencia=hibrido": 0.8,
            "dominio_negocio=financeiro": 0.9, "dominio_negocio=saude": 0.8,
            "dominio_negocio=logistica": 0.9,
            "integracao=servicos_internos": 0.9, "integracao=ambos": 0.9,
            "ambiente_implantacao=on_premise": 0.9,
            "requisitos_seguranca=intermediario": 0.9, "requisitos_seguranca=avancado": 0.9,
            "maturidade_equipe=intermediario": 0.8, "maturidade_equipe=experiente": 0.9,
            "tipo_autenticacao=oauth": 0.8, "tipo_autenticacao=enterprise": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.9,
        },
        "laravel": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.8,
            "escala=pequena": 0.9, "escala=media": 0.9,
            "arquitetura_esperada=monolito": 0.9,
            "dominio_negocio=ecommerce": 0.9, "dominio_negocio=saude": 0.8,
            "dominio_negocio=educacao": 0.7,
            "experiencia_usuario=basica": 0.7,
            "requisitos_seguranca=basico": 0.9,
            "maturidade_equipe=iniciante": 0.9,
            "tipo_autenticacao=propria": 0.9,
            "ciclo_desenvolvimento=mvp": 0.8,
        },
        "rails": {
            "tipo_projeto=web": 0.9, "tipo_projeto=api": 0.8,
            "escala=pequena": 0.9, "escala=media": 0.8,
            "arquitetura_esperada=monolito": 0.9,
            "dominio_negocio=ecommerce": 0.8, "dominio_negocio=saude": 0.8,
            "experiencia_usuario=basica": 0.7,
            "requisitos_seguranca=basico": 0.8,
            "tipo_autenticacao=propria": 0.8,
        },
        "aspnet": {
            "tipo_projeto=api": 0.9, "tipo_projeto=web": 0.8,
            "escala=grande": 0.9, "escala=enterprise": 0.9,
            "integracao=servicos_internos": 0.8,
            "ambiente_implantacao=on_premise": 0.9,
            "requisitos_seguranca=intermediario": 0.9, "requisitos_seguranca=avancado": 0.9,
            "tipo_autenticacao=oauth": 0.8, "tipo_autenticacao=enterprise": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.9,
        },
        "gin": {
            "tipo_projeto=api": 0.9, "escala=media": 0.9, "escala=grande": 0.9,
            "arquitetura_esperada=microsservicos": 0.9,
            "integracao=servicos_internos": 0.9,
            "maturidade_equipe=experiente": 0.8,
        },
        "phoenix": {
            "tipo_projeto=api": 0.9, "tipo_projeto=web": 0.8,
            "escala=grande": 0.9, "escala=enterprise": 0.8,
            "arquitetura_esperada=microsservicos": 0.9, "arquitetura_esperada=event_driven": 0.9,
            "maturidade_equipe=experiente": 0.9,
        },

        # ════════════════════════════════════════════════
        # FRAMEWORKS FRONTEND
        # ════════════════════════════════════════════════
        "react": {
            "tipo_projeto=web": 0.9, "tipo_projeto=hibrido": 0.8,
            "experiencia_usuario=intermediaria": 0.9, "experiencia_usuario=avancada": 0.9,
            "maturidade_equipe=intermediario": 0.8,
            "ciclo_desenvolvimento=iterativo": 0.8,
        },
        "vue": {
            "tipo_projeto=web": 0.9,
            "experiencia_usuario=intermediaria": 0.9, "experiencia_usuario=avancada": 0.8,
            "maturidade_equipe=intermediario": 0.8,
        },
        "angular": {
            "tipo_projeto=web": 0.9,
            "experiencia_usuario=avancada": 0.9, "escala=enterprise": 0.9,
        },
        "svelte": {
            "tipo_projeto=web": 0.9,
            "experiencia_usuario=intermediaria": 0.9, "experiencia_usuario=avancada": 0.8,
        },
        "nextjs": {
            "tipo_projeto=web": 0.9,
            "experiencia_usuario=avancada": 0.9, "escala=grande": 0.9,
        },
        "nuxtjs": {
            "tipo_projeto=web": 0.9,
            "experiencia_usuario=avancada": 0.9,
        },
        "jquery": {
            "tipo_projeto=web": 0.8,
            "experiencia_usuario=basica": 0.9,
            "maturidade_equipe=iniciante": 0.9,
        },

        # ════════════════════════════════════════════════
        # FRAMEWORKS MOBILE
        # ════════════════════════════════════════════════
        "react_native": {
            "tipo_projeto=mobile": 0.9, "tipo_projeto=hibrido": 0.9,
            "dominio_negocio=educacao": 0.7,
            "experiencia_usuario=intermediaria": 0.8,
        },
        "flutter": {
            "tipo_projeto=mobile": 0.9, "tipo_projeto=hibrido": 0.9,
            "dominio_negocio=educacao": 0.8,
            "experiencia_usuario=intermediaria": 0.9,
        },
        "swiftui": {
            "tipo_projeto=mobile": 0.9,
        },
        "android_kotlin": {
            "tipo_projeto=mobile": 0.9,
        },
        "ionic": {
            "tipo_projeto=mobile": 0.8, "tipo_projeto=hibrido": 0.9,
        },

        # ════════════════════════════════════════════════
        # BANCOS DE DADOS
        # ════════════════════════════════════════════════
        "postgresql": {
            "persistencia=sql": 0.95, "escala=media": 0.9, "escala=grande": 0.9, "escala=enterprise": 0.9,
            "requisitos_seguranca=basico": 0.8, "requisitos_seguranca=intermediario": 0.9,
            "requisitos_seguranca=avancado": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.8,
        },
        "mysql": {
            "persistencia=sql": 0.95, "escala=pequena": 0.9, "escala=media": 0.9,
            "requisitos_seguranca=basico": 0.8,
        },
        "sqlite": {
            "persistencia=sql": 0.95, "escala=pequena": 0.9, "tipo_projeto=mobile": 0.9,
            "ambiente_implantacao=local": 0.9,
            "requisitos_seguranca=nenhum": 0.8,
        },
        "mongodb": {
            "persistencia=nosql": 0.95, "escala=media": 0.9, "escala=grande": 0.8,
        },
        "redis": {
            "persistencia=nosql": 0.9, "escala=media": 0.9, "escala=grande": 0.9,
        },
        "firebase_rt": {
            "persistencia=nosql": 0.9, "tipo_projeto=mobile": 0.9, "tipo_projeto=web": 0.8, "escala=pequena": 0.9,
            "ciclo_desenvolvimento=mvp": 0.9,
        },
        "dynamodb": {
            "persistencia=nosql": 0.95, "escala=grande": 0.9, "escala=enterprise": 0.9, "ambiente_implantacao=cloud": 0.9,
        },
        "mariadb": {
            "persistencia=sql": 0.9, "escala=media": 0.9,
        },
        "sqlserver": {
            "persistencia=sql": 0.95, "escala=grande": 0.9, "escala=enterprise": 0.9,
            "requisitos_seguranca=avancado": 0.9,
            "tipo_autenticacao=enterprise": 0.8,
        },
        "cassandra": {
            "persistencia=nosql": 0.9, "escala=grande": 0.9, "escala=enterprise": 0.9,
            "arquitetura_esperada=event_driven": 0.8,
            "maturidade_equipe=experiente": 0.8,
        },
        "neo4j": {
            "persistencia=nosql": 0.8, "escala=media": 0.8,
            "dominio_negocio=logistica": 0.8,
        },

        # ════════════════════════════════════════════════
        # INFRAESTRUTURA
        # ════════════════════════════════════════════════
        "docker": {
            "ambiente_implantacao=cloud": 0.9, "arquitetura_esperada=microsservicos": 0.9,
        },
        "kubernetes": {
            "ambiente_implantacao=cloud": 0.9, "arquitetura_esperada=microsservicos": 0.9,
            "escala=grande": 0.9, "escala=enterprise": 0.9,
            "requisitos_seguranca=avancado": 0.8,
            "maturidade_equipe=experiente": 0.9,
            "ciclo_desenvolvimento=longo_prazo": 0.9,
        },
        "aws": {
            "ambiente_implantacao=cloud": 0.9,
            "arquitetura_esperada=serverless": 0.9, "arquitetura_esperada=event_driven": 0.9,
        },
        "gcp": {
            "ambiente_implantacao=cloud": 0.9,
            "arquitetura_esperada=serverless": 0.9, "arquitetura_esperada=event_driven": 0.8,
        },
        "azure": {
            "ambiente_implantacao=cloud": 0.9,
            "arquitetura_esperada=serverless": 0.9, "arquitetura_esperada=event_driven": 0.8,
        },
        "nginx": {
            "arquitetura_esperada=monolito": 0.8, "arquitetura_esperada=microsservicos": 0.8,
        },
        "heroku": {
            "ambiente_implantacao=cloud": 0.9, "escala=pequena": 0.9, "escala=media": 0.8,
            "escala=enterprise": -0.8,
        },
        "vercel": {
            "ambiente_implantacao=cloud": 0.9, "tipo_projeto=web": 0.9,
        },
        "kafka": {
            "arquitetura_esperada=microsservicos": 0.9, "arquitetura_esperada=event_driven": 0.9,
            "escala=grande": 0.9, "escala=enterprise": 0.9,
            "maturidade_equipe=experiente": 0.9,
        },
        "rabbitmq": {
            "arquitetura_esperada=microsservicos": 0.8, "arquitetura_esperada=event_driven": 0.8,
            "escala=media": 0.8, "escala=grande": 0.8,
            "maturidade_equipe=intermediario": 0.8,
        },
    }

    # Assegurar que todas as linguagens possuem pelo menos alguns atributos basicos para não ficarem órfãs
    for tech_id, kwargs in adequabilidades.items():
        for attr_val, peso in kwargs.items():
            if G.has_node(attr_val):
                G.add_edge(tech_id, attr_val, relacao="ADEQUADO_PARA", peso=peso, fonte="manual")
            else:
                # Caso haja um erro de digitação
                pass

    # 4. Adicionar arestas REQUER (manuais)
    requer_edges = [
        ("django", "python", 1.0), ("flask", "python", 1.0), ("fastapi", "python", 1.0),
        ("express", "javascript", 1.0), ("nestjs", "typescript", 1.0),
        ("spring", "java", 1.0),
        ("laravel", "php", 1.0),
        ("rails", "ruby", 1.0),
        ("aspnet", "csharp", 1.0),
        ("gin", "go", 1.0),
        ("phoenix", "elixir", 1.0),
        ("react", "javascript", 1.0), ("vue", "javascript", 1.0), ("angular", "typescript", 1.0),
        ("svelte", "javascript", 1.0), ("nextjs", "react", 1.0), ("nuxtjs", "vue", 1.0),
        ("react_native", "react", 1.0), ("flutter", "dart", 1.0), ("swiftui", "swift", 1.0),
        ("android_kotlin", "kotlin", 1.0), ("ionic", "javascript", 1.0)
    ]
    for source, target, peso in requer_edges:
        G.add_edge(source, target, relacao="REQUER", peso=peso, fonte="manual")

    # 5. Adicionar arestas COMPLEMENTA (manuais)
    complementa_edges = [
        ("django", "react", 0.8), ("django", "vue", 0.7),
        ("express", "react", 0.9), ("express", "vue", 0.8), ("express", "angular", 0.8),
        ("spring", "angular", 0.9), ("spring", "react", 0.8), ("spring", "vue", 0.7),
        ("laravel", "vue", 0.9), ("laravel", "react", 0.8),
        ("flask", "vue", 0.8), ("flask", "react", 0.8),
        ("fastapi", "react", 0.8), ("fastapi", "vue", 0.8), ("fastapi", "angular", 0.7),
        ("nestjs", "angular", 0.9), ("nestjs", "react", 0.8),
        ("aspnet", "angular", 0.8), ("aspnet", "react", 0.8), ("aspnet", "vue", 0.7),
        ("gin", "vue", 0.8), ("gin", "react", 0.8),
        ("rails", "react", 0.7), ("rails", "vue", 0.7),
        ("phoenix", "react", 0.7), ("phoenix", "vue", 0.7),
    ]
    for source, target, peso in complementa_edges:
        G.add_edge(source, target, relacao="COMPLEMENTA", peso=peso, fonte="manual")

    # 6. Arestas COMPATIVEL_COM manuais (serão mescladas com Survey)
    compativel_edges = [
        # Backend → DB
        ("django", "postgresql", 0.9), ("django", "mysql", 0.7), ("django", "sqlite", 0.8),
        ("laravel", "mysql", 0.9), ("laravel", "postgresql", 0.7),
        ("spring", "postgresql", 0.9), ("spring", "mysql", 0.8), ("spring", "sqlserver", 0.8), ("spring", "mariadb", 0.7),
        ("express", "mongodb", 0.9), ("express", "postgresql", 0.8),
        ("nestjs", "postgresql", 0.9), ("nestjs", "mongodb", 0.8),
        ("aspnet", "sqlserver", 0.9), ("aspnet", "postgresql", 0.7),
        ("flask", "sqlite", 0.8), ("flask", "postgresql", 0.7),
        ("fastapi", "postgresql", 0.9), ("fastapi", "mongodb", 0.7),
        ("gin", "postgresql", 0.9), ("gin", "mysql", 0.7),
        ("rails", "postgresql", 0.8), ("rails", "mysql", 0.7), ("rails", "sqlite", 0.7),
        # Mobile → DB
        ("flutter", "sqlite", 0.9), ("flutter", "firebase_rt", 0.9),
        ("react_native", "sqlite", 0.8), ("react_native", "firebase_rt", 0.9),
        # Infra
        ("kafka", "spring", 0.9), ("kafka", "nestjs", 0.7), ("kafka", "fastapi", 0.7),
        ("rabbitmq", "spring", 0.8), ("rabbitmq", "nestjs", 0.7), ("rabbitmq", "django", 0.6),
    ]
    for source, target, peso in compativel_edges:
        G.add_edge(source, target, relacao="COMPATIVEL_COM", peso=peso, fonte="manual")
        # Criar a aresta bidirecional para facilitar
        G.add_edge(target, source, relacao="COMPATIVEL_COM", peso=peso, fonte="manual")

    # Salvar o grafo manual inicial
    data = nx.node_link_data(G)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import os
    # cwd é src
    seed_path = os.path.join("data", "graph", "technology_seed.json")
    output_path = os.path.join("data", "graph", "knowledge_graph_manual.json")
    build_manual_graph(seed_path, output_path)
    print(f"Grafo manual construído com sucesso e salvo em {output_path}")
