from dataclasses import dataclass
import ollama

PROMPT_RESUMO = """
"Você é o Módulo de Formatação Analítica do Sistema de Recomendação de Tecnologias.
Seu papel é receber as métricas matemáticas calculadas pelo motor de recomendação e redigir um relatório técnico, impessoal e direto ao usuário."


Sua tarefa é avaliar as top 3 stacks sugeridas pelo motor de recomendação e decidir qual se adequa mais ao contexto da entrada do usuário

Siga as seguintes reggras:
1. Analise a entrada do usuário, os requisitos extraídos e as 3 opções de Stacks (e suas respectivas notas de aderência/Score).
2. ESCOLHA qual das 3 opções é a MELHOR e MAIS ADEQUADA para a realidade e contexto descritos pelo usuário. Não fique preso apenas aos números, use seu conhecimento.
3. Se o projeto for Web, DEDUZA e cite textualmente as tecnologias base de Front-End necessárias (ex: HTML, CSS e JavaScript ou WebAssembly), mesmo que não estejam explicitamente na stack selecionada. 
4. Redija a recomendação final em 2 ou 3 parágrafos diretos. Separe-os com quebras de linhas. Indique claramente qual Stack você escolheu como a Vencedora, por que ela vence as outras duas alternativas listadas, e descreva a arquitetura.
5. Não use introduções como "Aqui está o resumo", vá direto ao ponto.
6. Não adicione saudações.
7. Formate a saída de forma simples, pois o conteúdo será exibido em um terminal. Por isso, não use caracteres especiais, como '-', '#', '_', '+', '='. 
8. Verifique se a entrada fornecida pelo usuário solicita explicitamente alguma tecnologia (linguagem, banco de dados ou framework). 
    - Se a tecnologia mencionada NÃO estiver no top 3 do motor de recomendação, use sua capacidade de inferência para julgar se o que o usuário pediu é melhor ou pior do que as opções matemáticas do motor. Justifique a sua recomendação indicando ao usuário se a tecnologia que ele pediu é válida ou não para o caso dele. 
    - Se a tecnologia mencionada estiver no top 3 do motor, siga a sua avaliação normal e a defenda.
9. AUDITORIA DE DO MOTOR DE RECOMENDAÇÃO: Caso você note que o Score das opções listadas é muito baixo (abaixo de 3.0), ou caso entenda que NENHUMA das tecnologias ranqueadas pelo motor atende bem aos requisitos da solicitação do usuário, indique que as tecnologias listadas foram processadas pelo motor de recomendação, mas sugira outra stack que julgar ideal e justifique isso ao usuário.
10. COERÊNCIA ARQUITETURAL: Verifique se a stack recomendada faz sentido como uma solução completa. Se o projeto for mobile ou híbrido e a stack não incluir uma API backend, recomende que o usuário considere uma API intermediária para conectar o app ao banco de dados de forma segura.

Estrutura:
1. Estrutura padrão: 
    Parágrafo 1: Indicar a melhor opção e justificar a sua relação com a solicitação apresentada na entrada.
    Parágrafo 2: Justificar a viabilidade das demais opções e as limitações delas.
    Parágrafo 3 (se necessário): Informações adicionais.
2. Caso o motor de recomendação não apresente um top 3 com tecnologias que se adequam a solicitação do usuário (regra 9)
    Parágrafo 1: "O motor de recomendação classificou 3 conjuntos de tecnologias que não se adequam totalmente à solicitação inserida". [FINALIZE O PARÁGRAFO COMPLEMENTANDO A FRASE ANTERIOR COM A JUSTIFICATIVA]
    Parágrafo 2: Recomende uma stack tecnológica para a entrada solicitada. Justifique a seleção dessa stack
    Parágrafo 3(se necessário): Informações adicionais. 
Abaixo está a entrada de um usuário descrevendo o projeto que ele quer construir, os requisitos extraídos automaticamente, e as 3 opções de Stacks (combinações de tecnologias) mais viáveis calculadas matematicamente pelo nosso Motor de Recomendação Baseado em Grafos.
Entrada do usuário:
"{ENTRADA_USUARIO}"

Requisitos extraídos pelo sistema:
{REQUISITOS_JSON}

Top 3 Stacks sugeridas pelo Motor (para você escolher):
{RECOMENDACAO_ESTRUTURADA}
"""

@dataclass
class ResponseFormatter:
    model: str = "qwen2.5"

    def format(self, user_input: str, recommendation: dict) -> str:
        stacks = recommendation.get("stacks_recomendadas", [])
        if not stacks:
            return "Nenhuma recomendação encontrada."

        # 1. Montar a parte textual formatada para o terminal
        top1 = stacks[0]
        
        output_lines = []
        output_lines.append("=== Opções Selecionadas pelo Motor de Recomendação ===")
        output_lines.append("")
        
        reqs = recommendation.get("atributos_utilizados", {})
        tipo_projeto = reqs.get("tipo_projeto", "N/A").upper()
        output_lines.append(f"Tipo de desenvolvimento : {tipo_projeto}")
        
        arq = reqs.get("arquitetura_esperada", "N/A").capitalize()
        output_lines.append(f"Arquitetura sugerida    : {arq}")
        
        complexidade = reqs.get("experiencia_usuario", "N/A").capitalize()
        output_lines.append(f"Complexidade de UX      : {complexidade}")
        output_lines.append("")
        
        for i, stack in enumerate(stacks[:3]):
            alt_lang_dict = stack.get("linguagem")
            alt_lang = alt_lang_dict.get("nome", "") if alt_lang_dict else ""
            score = stack.get("score", 0.0)
            
            alt_fw_dict = stack.get("framework")
            alt_fw = alt_fw_dict.get("nome", "") if alt_fw_dict else ""
            
            alt_fronts = [c["nome"] for c in stack.get("complementos", []) if c["categoria"] == "framework_frontend"]
            
            alt_db_dict = stack.get("banco_dados")
            alt_db = alt_db_dict.get("nome", "") if alt_db_dict else ""
            
            parts = [alt_lang]
            if alt_fw: parts.append(f"{alt_fw} (back)")
            if alt_fronts: parts.append(f"{alt_fronts[0]} (front)")
            if alt_db: parts.append(f"{alt_db} (db)")
            
            combo = " + ".join(p for p in parts if p)
            output_lines.append(f"Opção {i+1} [Aderência {score}/10]: {combo}")
            
        output_lines.append("")
        output_lines.append("--- Resumo da Recomendação ---")
        
        # 2. Gerar Resumo via LLM
        recomendacao_str = self._stringify_recommendation(stacks)
        requisitos_str = self._stringify_requisitos(reqs)
        prompt = (PROMPT_RESUMO
            .replace("{ENTRADA_USUARIO}", user_input)
            .replace("{REQUISITOS_JSON}", requisitos_str)
            .replace("{RECOMENDACAO_ESTRUTURADA}", recomendacao_str))
        
        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt
            )
            resumo = response['response'].strip()
            output_lines.append(f"Resumo: {resumo}")
        except Exception as e:
            output_lines.append(f"Resumo: (Erro ao gerar resumo textual via LLM: {str(e)})")

        return "\n".join(output_lines)

    def _stringify_recommendation(self, stacks) -> str:
        lines = []
        for stack in stacks:
            lang = stack.get("linguagem")
            lang_nome = lang.get("nome", "") if lang else ""
            fw = stack.get("framework")
            fw_nome = fw.get("nome", "") if fw else ""
            db = stack.get("banco_dados")
            db_nome = db.get("nome", "") if db else ""
            comps = [c["nome"] for c in stack.get("complementos", [])]
            lines.append(f"Posição {stack['posicao']} (Score: {stack['score']}/10): Linguagem: {lang_nome}, Framework: {fw_nome}, Banco de Dados: {db_nome}, Infra e Outros: {','.join(comps)}")
        return "\n".join(lines)

    def _stringify_requisitos(self, reqs: dict) -> str:
        """Formata os requisitos extraídos para o LLM ter contexto completo."""
        lines = []
        for attr, valor in reqs.items():
            lines.append(f"  {attr}: {valor}")
        return "\n".join(lines)
