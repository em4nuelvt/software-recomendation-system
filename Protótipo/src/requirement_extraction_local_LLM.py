import json
import ollama

#MODEL = "qwen2.5"
MODEL = "deepseek-r1:8b"
PROMPT = """
Você é um extrator de requisitos de software.
Sua tarefa é analisar a entrada do usuário e extrair 9 atributos em formato JSON.
Atributos: tipo_projeto, dominio_negocio, persistencia, escala, integracao, arquitetura_esperada, requisitos_desempenho, experiencia_usuario, requisitos_seguranca.

Regras:
- Se o usuário não mencionar informações suficientes para preencher um atributo, preencha-o com a opção que torne o sistema o mais SIMPLES e comum possível de ser construído (ex: se arquitetura não for citada, use "Monolito").
- Retorne o conteúdo formatado em JSON sem textos adicionais, ou seja, a sua resposta deve ser somente o JSON estruturado.
"""
USER_INPUT = "Tecnologias para sistema de lista de tarefas web"


def generate_requirement_extraction(model,prompt,user_input):
    complete_prompt = f'{prompt}\n\nEntrada do usuário: "{user_input}"'
    try:
        response = ollama.generate(
            model = model,
            prompt = complete_prompt,
            format = 'json'
        )
        requirements_dictionary = json.loads(response['response'])
        return requirements_dictionary 
    except json.JSONDecodeError:
        return {"ERRO": "O modelo não retornou um JSON válido."}
    except Exception as e:
        return {"ERRO": "Falha na execução: {e}"}
    
if __name__ == "__main__":
    print("--- Motor de PLN com modelos generativos (LLM) ---")
    requirements = generate_requirement_extraction(MODEL,PROMPT, USER_INPUT)
    print("Saída: \n")
    print(json.dumps(requirements, indent=4, ensure_ascii=False))