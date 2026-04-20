import json
import ollama

MODEL = "qwen2.5"
#MODEL = "deepseek-r1:8b"
# PROMPT = """
# Você é um extrator de requisitos de software.
# Sua tarefa é analisar a entrada do usuário e extrair 9 atributos em formato JSON.
# Atributos: tipo_projeto, dominio_negocio, persistencia, escala, integracao, arquitetura_esperada, requisitos_desempenho, experiencia_usuario, requisitos_seguranca.

# Regras:
# - Se o usuário não mencionar informações suficientes para preencher um atributo, preencha-o com a opção que torne o sistema o mais SIMPLES e comum possível de ser construído (ex: se arquitetura não for citada, use "Monolito").
# - Retorne o conteúdo formatado em JSON sem textos adicionais, ou seja, a sua resposta deve ser somente o JSON estruturado.
# """

PROMPT = """
Você é um especialista em engenharia de requisitos de software. Analise a entrada do usuário e extraia exatamente 9 atributos, retornando **somente** um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.

### Atributos e valores permitidos:
- **tipo_projeto**: "web" | "mobile" | "desktop" | "api" | "embarcado" | "hibrido"
- **dominio_negocio**: "produtividade" | "financeiro" | "saude" | "educacao" | "ecommerce" | "logistica" | "entretenimento" | "outro"
- **persistencia**: "sem_banco" | "sql" | "nosql" | "hibrido"
- **escala**: "pequena" | "media" | "grande" | "enterprise"
- **integracao**: "nenhuma" | "apis_externas" | "servicos_internos" | "ambos"
- **arquitetura_esperada**: "monolito" | "microsservicos" | "serverless" | "event_driven" | "mvc"
- **requisitos_desempenho**: "baixo" | "medio" | "alto" | "critico"
- **experiencia_usuario**: "basica" | "intermediaria" | "avancada" | "acessivel"
- **requisitos_seguranca**: "nenhum" | "basico" | "intermediario" | "avancado"

### Regras de preenchimento:
1. Use apenas os valores listados acima para cada atributo.
2. Se um atributo não for mencionado ou puder ser inferido, escolha o valor mais **simples e comum** para o contexto descrito.
3. **Nunca** retorne campos nulos, vazios ou fora da lista de valores permitidos.
4. **Nunca** adicione texto fora do JSON.

### Saída esperada (preencha o template abaixo e não adicione NADA além dele):
{
  "tipo_projeto": "",
  "dominio_negocio": "",
  "persistencia": "",
  "escala": "",
  "integracao": "",
  "arquitetura_esperada": "",
  "requisitos_desempenho": "",
  "experiencia_usuario": "",
  "requisitos_seguranca": ""
}
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
        return {"ERRO": f"Falha na execução: {e}"}
    
if __name__ == "__main__":
    print("--- Motor de PLN com modelos generativos (LLM) ---")
    requirements = generate_requirement_extraction(MODEL,PROMPT, USER_INPUT)
    print("Saída: \n")
    print(json.dumps(requirements, indent=4, ensure_ascii=False))