import sys
import os
from RequirementExtractor import RequirementExtractor 
from RecommendationEngine import RecommendationEngine
from ResponseFormatter import ResponseFormatter
import user_input as ui 

if __name__ == "__main__":
    extractor = RequirementExtractor()
    engine = RecommendationEngine()
    formatter = ResponseFormatter()

    output_path = os.path.join(os.path.dirname(__file__), "test_results.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        original_stdout = sys.stdout
        sys.stdout = f

        try:
            print("--- Sistema Inteligente de Recomendação de Tecnologias de Software ---\n")

            for i, user_input in enumerate(ui.inputs):
                print(f"=== TESTE {i+1} ===")
                print(f"Entrada: {user_input}")

                if not extractor.validateInput(user_input):
                    print("Resultado: Fora do escopo.\n")
                else:
                    requirements = extractor.extractRequirement(user_input)
                    recommendation = engine.recommend(requirements)
                    output = formatter.format(user_input, recommendation)
                    print(output)
                    print("\n" + "="*50 + "\n")
        finally:
            # Restore original stdout
            sys.stdout = original_stdout
            
    print(f"Testes finalizados! Resultados salvos em test_results.txt com encoding UTF-8 correto.")
