import json
import networkx as nx
from dataclasses import dataclass, field
from collections import defaultdict
import os

MULTIPLICADORES = {
    "tipo_projeto": 2.0,
    "dominio_negocio": 1.5,
    "persistencia": 1.5,
    "escala": 1.5,
    "integracao": 1.0,
    "arquitetura_esperada": 1.0,
    "experiencia_usuario": 1.0,
    "requisitos_seguranca": 1.0,
    "ambiente_implantacao": 1.0,
    "maturidade_equipe": 1.0,
    "tipo_autenticacao": 1.0,
    "ciclo_desenvolvimento": 1.0
}

@dataclass
class RecommendationEngine:
    graph_path: str = field(default_factory=lambda: os.path.join(os.path.dirname(__file__), "data", "graph", "knowledge_graph.json"))
    graph: nx.DiGraph = field(init=False)

    def __post_init__(self):
        try:
            with open(self.graph_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data, edges="links")
        except Exception as e:
            print(f"Erro ao carregar o grafo de conhecimento: {e}")
            self.graph = nx.DiGraph()

    def recommend(self, requirements: dict) -> dict:
        if not self.graph.nodes:
            return {"ERRO": "Grafo de conhecimento não carregado ou vazio."}

        # 1. Converter requisitos em nós de busca e calcular scores individuais
        # Suporta pesos negativos (penalizações)
        tech_scores = defaultdict(float)
        tech_justifications = defaultdict(list)

        for atributo, valor in requirements.items():
            if not valor:
                continue
            
            node_id = f"{atributo}={valor}"
            if not self.graph.has_node(node_id):
                continue
                
            multiplicador = MULTIPLICADORES.get(atributo, 1.0)
            
            # Percorrer arestas do nó de atributo para tecnologias (in_edges, pois tech -> atributo)
            for u, v, data in self.graph.in_edges(node_id, data=True):
                if data.get("relacao") == "ADEQUADO_PARA":
                    peso = data.get("peso", 0.0)
                    score_contribuicao = peso * multiplicador
                    tech_scores[u] += score_contribuicao
                    # Registrar justificativa (positiva ou negativa)
                    if score_contribuicao != 0:
                        tech_justifications[u].append(node_id)

        # Filtrar tecnologias com score negativo (penalizadas demais)
        tech_scores_positivos = {k: v for k, v in tech_scores.items() if v > 0}

        # Obter a pontuação máxima real obtida pelas tecnologias para normalização relativa
        top_score = max(tech_scores_positivos.values()) if tech_scores_positivos else 0.0

        # Normalizar scores (0 a 10) baseados no topo real para termos variações de 0 a 10 sempre
        tech_ranking = []
        for tech, score in tech_scores_positivos.items():
            normalized_score = round((score / top_score) * 10, 1) if top_score > 0 else 0
            if normalized_score > 0:
                # Adicionar dados do nó de tecnologia
                tech_data = self.graph.nodes[tech]
                tech_ranking.append({
                    "id": tech,
                    "nome": tech_data.get("nome", tech),
                    "categoria": tech_data.get("categoria", "desconhecida"),
                    "score": normalized_score,
                    "justificativa": tech_justifications[tech]
                })

        # Ordenar por score decrescente
        tech_ranking.sort(key=lambda x: x["score"], reverse=True)

        # Categorizar as tecnologias
        langs = [t for t in tech_ranking if t["categoria"] == "linguagem"]
        frameworks_back = [t for t in tech_ranking if t["categoria"] == "framework_backend"]
        frameworks_front = [t for t in tech_ranking if t["categoria"] == "framework_frontend"]
        frameworks_mobile = [t for t in tech_ranking if t["categoria"] == "framework_mobile"]
        bancos = [t for t in tech_ranking if t["categoria"] == "banco_dados"]
        infras = [t for t in tech_ranking if t["categoria"] == "infraestrutura"]

        # 2. Montar stacks
        # Decidir os frameworks baseados no tipo_projeto
        tipo_projeto = requirements.get("tipo_projeto", "web")
        
        candidatos_principais = []
        if tipo_projeto in ["web", "api"]:
            candidatos_principais = frameworks_back if frameworks_back else langs
        elif tipo_projeto in ["mobile", "hibrido"]:
            candidatos_principais = frameworks_mobile if frameworks_mobile else langs
        else:
            candidatos_principais = langs

        stacks_recomendadas = []
        posicao = 1

        for main_tech in candidatos_principais[:3]: # Tentar formar stack ao redor do top 3 techs
            stack = {
                "posicao": posicao,
                "score": 0.0,
                "tecnologias_base": [],
                "linguagem": None,
                "framework": None,
                "banco_dados": None,
                "complementos": [],
                "justificativa_principal": main_tech["justificativa"]
            }

            main_id = main_tech["id"]
            
            # Se a tech principal já for uma linguagem, definimos. Se for framework, buscamos quem ela REQUER recursivamente
            if main_tech["categoria"] == "linguagem":
                stack["linguagem"] = {"nome": main_tech["nome"], "score": main_tech["score"]}
            else:
                stack["framework"] = {"nome": main_tech["nome"], "score": main_tech["score"]}
                # Encontrar a linguagem requerida iterativamente
                lang_req_id = None
                visited = set()
                queue = [main_id]
                
                while queue and not lang_req_id:
                    curr = queue.pop(0)
                    if curr in visited: continue
                    visited.add(curr)
                    for u, v, data in self.graph.out_edges(curr, data=True):
                        if data.get("relacao") == "REQUER":
                            if self.graph.nodes[v].get("categoria") == "linguagem":
                                lang_req_id = v
                                break
                            else:
                                queue.append(v)
                
                if lang_req_id:
                    # Encontrar o score dessa linguagem
                    lang_item = next((l for l in langs if l["id"] == lang_req_id), None)
                    if lang_item:
                        stack["linguagem"] = {"nome": lang_item["nome"], "score": lang_item["score"]}
                    else:
                        stack["linguagem"] = {"nome": self.graph.nodes[lang_req_id].get("nome", lang_req_id), "score": 0.0}

            # Encontrar banco de dados COMPATIVEL ou com melhor score
            # Se for 'sem_banco', não coloca
            if requirements.get("persistencia") != "sem_banco" and bancos:
                # Primeiro tentar os compativeis com o framework/linguagem principal
                best_db = None
                best_db_score = -1
                
                for db in bancos:
                    if self.graph.has_edge(main_id, db["id"]) and self.graph.edges[main_id, db["id"]].get("relacao") == "COMPATIVEL_COM":
                        peso_compativel = self.graph.edges[main_id, db["id"]].get("peso", 0.0)
                        combined_score = db["score"] * (1 + peso_compativel) # Bonus de compatibilidade
                        if combined_score > best_db_score:
                            best_db_score = combined_score
                            best_db = db

                if best_db:
                    stack["banco_dados"] = {"nome": best_db["nome"], "score": best_db["score"]}
                else:
                    stack["banco_dados"] = {"nome": bancos[0]["nome"], "score": bancos[0]["score"]}

            # Encontrar complementos (front-end e infra)
            if tipo_projeto == "web" and main_tech["categoria"] == "framework_backend" and frameworks_front:
                best_front = None
                best_front_score = -1
                for front in frameworks_front:
                    # Checar COMPLEMENTA
                    peso_comp = 0.0
                    if self.graph.has_edge(main_id, front["id"]) and self.graph.edges[main_id, front["id"]].get("relacao") == "COMPLEMENTA":
                        peso_comp = self.graph.edges[main_id, front["id"]].get("peso", 0.0)
                    
                    combined_score = front["score"] * (1 + peso_comp)
                    if combined_score > best_front_score:
                        best_front_score = combined_score
                        best_front = front
                        
                if best_front:
                    stack["complementos"].append({"nome": best_front["nome"], "categoria": "framework_frontend", "score": best_front["score"]})

            # Infra — SOMENTE se ambiente_implantacao NÃO for "local"
            ambiente = requirements.get("ambiente_implantacao", "cloud")
            if infras and ambiente in ["cloud", "hibrido", "on_premise"]:
                top_infra = infras[0]
                stack["complementos"].append({"nome": top_infra["nome"], "categoria": "infraestrutura", "score": top_infra["score"]})

            # Calcular score total da stack (média ponderada)
            total_stack_score = 0
            count = 0
            if stack["linguagem"]:
                total_stack_score += stack["linguagem"]["score"]
                count += 1
            if stack["framework"]:
                total_stack_score += stack["framework"]["score"]
                count += 1
            if stack["banco_dados"]:
                total_stack_score += stack["banco_dados"]["score"]
                count += 1
            for comp in stack["complementos"]:
                total_stack_score += comp["score"]
                count += 1
                
            stack["score"] = round(total_stack_score / count, 1) if count > 0 else 0.0

            stacks_recomendadas.append(stack)
            posicao += 1

        # Ordenar stacks por score
        stacks_recomendadas.sort(key=lambda x: x["score"], reverse=True)
        # Atualizar a posição após re-ordenar
        for i, stack in enumerate(stacks_recomendadas):
            stack["posicao"] = i + 1

        return {
            "stacks_recomendadas": stacks_recomendadas,
            "atributos_utilizados": requirements
        }

if __name__ == "__main__":
    engine = RecommendationEngine()
    reqs = {
        "tipo_projeto": "web",
        "dominio_negocio": "ecommerce",
        "persistencia": "sql",
        "escala": "media",
        "arquitetura_esperada": "monolito"
    }
    res = engine.recommend(reqs)
    print(json.dumps(res, indent=2, ensure_ascii=False))
