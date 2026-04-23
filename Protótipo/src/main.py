from RequirementExtractor import RequirementExtractor 
import user_input as ui 
import json

USER_INPUT = ui.inputs[1]
if __name__ == "__main__":
    extractor = RequirementExtractor()
    print("--- Motor de PLN com modelos generativos (LLM) ---")
    requirements = extractor.extractRequirement(USER_INPUT)
    print("Saída: \n")
    print(json.dumps(requirements, indent=4, ensure_ascii=False))