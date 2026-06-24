from dataclasses import dataclass
import json
import ollama


#MODEL = "deepseek-r1:8b"
# PROMPT = """
# Você é um extrator de requisitos de software.
# Sua tarefa é analisar a entrada do usuário e extrair 9 atributos em formato JSON.
# Atributos: tipo_projeto, dominio_negocio, persistencia, escala, integracao, arquitetura_esperada, requisitos_desempenho, experiencia_usuario, requisitos_seguranca.

# Regras:
# - Se o usuário não mencionar informações suficientes para preencher um atributo, preencha-o com a opção que torne o sistema o mais SIMPLES e comum possível de ser construído (ex: se arquitetura não for citada, use "Monolito").
# - Retorne o conteúdo formatado em JSON sem textos adicionais, ou seja, a sua resposta deve ser somente o JSON estruturado.
# """

VALIDATION_PROMPT = """
Você é um validador de entrada para um sistema de recomendação de tecnologias de software.

Analise a entrada do usuário e responda APENAS com "true" ou "false", sem aspas, sem texto adicional:
- "true": se a entrada for uma solicitação de recomendação de tecnologias para desenvolver algum sistema, aplicação ou software.
- "false": se a entrada não tiver relação com desenvolvimento de software ou pedido de recomendação de tecnologia.

Entrada do usuário: "{ENTRADA}"

Responda apenas: "true" ou "false"
"""

PROMPT = """
Você é um especialista em engenharia de requisitos de software. Analise a entrada do usuário e extraia exatamente 12 atributos, retornando **somente** um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.

### Atributos e Valores Permitidos (Escolha ESTRITAMENTE desta lista):

- **tipo_projeto**: "web" | "mobile" | "desktop" | "api" | "embarcado" | "hibrido"
- **dominio_negocio**: "produtividade" | "financeiro" | "saude" | "educacao" | "ecommerce" | "logistica" | "entretenimento" | "outro"
- **persistencia**: "sem_banco" | "sql" | "nosql" | "hibrido"
- **escala**: "pequena" | "media" | "grande" | "enterprise"
- **integracao**: "nenhuma" | "apis_externas" | "servicos_internos" | "ambos"
- **arquitetura_esperada**: "monolito" | "microsservicos" | "serverless" | "event_driven"
- **experiencia_usuario**: "basica" | "intermediaria" | "avancada"
- **requisitos_seguranca**: "nenhum" | "basico" | "intermediario" | "avancado"
- **ambiente_implantacao**: "local" | "cloud" | "on_premise" | "hibrido"
- **maturidade_equipe**: "iniciante" | "intermediario" | "experiente"
- **tipo_autenticacao**: "nenhuma" | "propria" | "oauth" | "enterprise"
- **ciclo_desenvolvimento**: "mvp" | "iterativo" | "longo_prazo"

### Regras de preenchimento:

1. Use apenas os valores listados acima para cada atributo.
2. Se um atributo não for mencionado, escolha o valor mais **simples e comum** para o contexto descrito.
3. **Nunca** retorne campos nulos, vazios ou fora da lista de valores permitidos.
4. **Nunca** adicione texto fora do JSON.

### Entrada do usuário:
"{ENTRADA}"

### Saída esperada (somente JSON):
"""
#USER_INPUT = "Tecnologias para sistema de lista de tarefas web"

@dataclass
class RequirementExtractor:
    model: str = "qwen2.5" #modelo padrão
    prompt: str = PROMPT
    temperature: float = None

    def extractRequirement(self, user_input: str) -> dict:
        complete_prompt = f'{self.prompt}\n\nEntrada do usuário: "{user_input}"'
        
        generate_kwargs = {
            "model": self.model,
            "prompt": complete_prompt,
            "format": 'json'
        }
        
        if self.temperature is not None:
            generate_kwargs["options"] = {"temperature": self.temperature}

        try:
            response = ollama.generate(**generate_kwargs)
            requirements_dictionary = json.loads(response['response'])
            return requirements_dictionary 
        except json.JSONDecodeError:
            return {"ERRO": "O modelo não retornou um JSON válido."}
        except Exception as e:
            return {"ERRO": f"Falha na execução: {e}"}
        
    def validateInput(self, user_input: str) -> bool:
        complete_prompt = VALIDATION_PROMPT.replace("{ENTRADA}", user_input)
        try:
            response = ollama.generate(
                model = self.model,
                prompt = complete_prompt                
            )
            result = response['response'].strip().lower()
            return result == "true"
        except Exception:
            return False

