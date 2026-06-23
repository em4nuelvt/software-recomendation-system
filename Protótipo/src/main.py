import sys
import json
from RequirementExtractor import RequirementExtractor 
from RecommendationEngine import RecommendationEngine
from ResponseFormatter import ResponseFormatter

USER_INPUT = "Gostaria de desenvolver um sistema de lista de tarefas local para computador sem banco de dados na linguagem Java"
if __name__ == "__main__":
    extractor = RequirementExtractor()
    engine = RecommendationEngine()
    formatter = ResponseFormatter()

    print("--- Sistema Recomendação de Tecnologias de Software ---\n")

    if not extractor.validateInput(USER_INPUT):
        print("Sou um sistema de recomendação de tecnologias de software. Não possuo capacidade de auxiliar sobre assuntos que fogem do meu escopo de atuação.")
    else:
        requirements = extractor.extractRequirement(USER_INPUT)
        recommendation = engine.recommend(requirements)
        
        print("=== Requisitos Extraídos (JSON) ===")
        print(json.dumps(requirements, indent=2, ensure_ascii=False))
        print()
        
        print(f"Entrada do Usuário: {USER_INPUT}\n")
        
        output = formatter.format(USER_INPUT, recommendation)
        print(output)
