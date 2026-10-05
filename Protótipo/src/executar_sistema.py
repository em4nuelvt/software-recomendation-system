import time
import os
import json
from RequirementExtractor import RequirementExtractor
from RecommendationEngine import RecommendationEngine
from ResponseFormatter import ResponseFormatter
import user_input

def executar_fluxo_completo():
    # Caso 6: Plataforma Acadêmica Integrada (Teste de Estresse)
    USER_INPUT = user_input.inputs[5]
    
    print("=== Iniciando Execução do Sistema de Recomendação de Tecnologias ===")
    print(f"Modelo de Linguagem: Qwen 2.5 (7B) | Temperatura: 0.0 | Prompt: Descritivo (PROMPT2)\n")
    
    t_inicio_total = time.perf_counter()
    
    # Configuração dos módulos com a melhor parametrização do Qwen 2.5
    extractor = RequirementExtractor(model="qwen2.5", prompt_index=1, temperature=0.0)
    engine = RecommendationEngine()
    formatter = ResponseFormatter(model="qwen2.5")
    
    # 1. Validação da entrada
    print("[1/3] Validando pertinência da entrada textual...")
    if not extractor.validateInput(USER_INPUT):
        mensagem_erro = "Sou um sistema de recomendação de tecnologias de software. Não possuo capacidade de auxiliar sobre assuntos que fogem do meu escopo de atuação."
        print(mensagem_erro)
        return
    
    # 2. Etapa 1: Extração estruturada de requisitos
    print("[1/3] Executando Etapa 1: Extração de Requisitos via LLM...")
    t_e1_inicio = time.perf_counter()
    requirements = extractor.extractRequirement(USER_INPUT)
    t_e1 = time.perf_counter() - t_e1_inicio
    print(f"      Etapa 1 concluída em {t_e1:.2f} segundos.")
    print("      Requisitos extraídos:")
    print(json.dumps(requirements, indent=2, ensure_ascii=False))
    print()
    
    # 3. Etapa 2: Motor de recomendação baseado em grafo
    print("[2/3] Executando Etapa 2: Navegação no Grafo de Conhecimento...")
    t_e2_inicio = time.perf_counter()
    recommendation = engine.recommend(requirements)
    t_e2 = time.perf_counter() - t_e2_inicio
    print(f"      Etapa 2 concluída em {t_e2:.4f} segundos.")
    print()
    
    # 4. Etapa 3: Resposta estruturada e síntese analítica
    print("[3/3] Executando Etapa 3: Formatação e Síntese Analítica via LLM...")
    t_e3_inicio = time.perf_counter()
    output_texto = formatter.format(USER_INPUT, recommendation)
    t_e3 = time.perf_counter() - t_e3_inicio
    print(f"      Etapa 3 concluída em {t_e3:.2f} segundos.")
    print()
    
    t_total = time.perf_counter() - t_inicio_total
    
    # Montar texto final consolidado
    linha_tempo = f"\nTempo total de execução: {t_total:.2f} segundos (Etapa 1: {t_e1:.2f} s | Etapa 2: {t_e2:.4f} s | Etapa 3: {t_e3:.2f} s)"
    resultado_final = output_texto + linha_tempo
    
    # Exibir no terminal
    print("\n" + "="*60)
    print("SAÍDA GERADA PELO PROTÓTIPO:")
    print("="*60)
    print(resultado_final)
    print("="*60)
    
    # Salvar / sobrescrever arquivo resultado_da_execucao.txt
    caminho_arquivo = os.path.join(os.path.dirname(__file__), "resultado_da_execucao.txt")
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(resultado_final + "\n")
    
    print(f"\nArquivo salvo com sucesso em: {caminho_arquivo}")
    return {
        "requirements": requirements,
        "recommendation": recommendation,
        "t_e1": t_e1,
        "t_e2": t_e2,
        "t_e3": t_e3,
        "t_total": t_total,
        "caminho_arquivo": caminho_arquivo
    }

if __name__ == "__main__":
    executar_fluxo_completo()
