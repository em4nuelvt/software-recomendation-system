from RequirementExtractor import RequirementExtractor 
import user_input as ui 
import json
USER_INPUT = "Quero fazer uma aplicação sobre futebol que me ajuda a responder duvidas como: foi a ultima vez que a seleção brasileira de futebol ganhou uma copa do mundo?"
#USER_INPUT = ui.inputs[1]
if __name__ == "__main__":
    extractor = RequirementExtractor()
    print("--- Motor de PLN com modelos generativos (LLM) ---")

    if not extractor.validateInput(USER_INPUT):
        print("Sou um sistema de recomendação de tecnologias de software. Não possuo capacidade de auxiliar sobre assuntos que fogem do meu escopo de atuação.")
    else:
        requirements = extractor.extractRequirement(USER_INPUT)
        print("Saída: \n")
        print(json.dumps(requirements, indent=4, ensure_ascii=False))