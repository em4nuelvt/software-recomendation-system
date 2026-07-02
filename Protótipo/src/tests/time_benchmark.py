import sys
import os
import time

# Adicionando o diretório 'src' ao sys.path para permitir importações
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from RequirementExtractor import RequirementExtractor
from user_input import inputs

def main():
    models = ["deepseek-r1:8b", "qwen2.5"]
    test_inputs = inputs[:2]  # Pegar apenas as 2 primeiras entradas
    num_runs = 3
    
    output_dir = os.path.join(current_dir, "benchmark_output")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "time_benchmark_result.txt")
    
    results_text = "Benchmark de Tempo de Execução\n"
    results_text += "="*40 + "\n\n"
    
    model_times = {model: [] for model in models}
    
    for i, user_input in enumerate(test_inputs, 1):
        results_text += f"=== Entrada {i} ===\n"
        results_text += f"Texto: {user_input}\n\n"
        
        for model in models:
            results_text += f"--- Modelo: {model} ---\n"
            extractor = RequirementExtractor(model=model)
            
            for run in range(1, num_runs + 1):
                start_time = time.time()
                response = extractor.extractRequirement(user_input)
                end_time = time.time()
                
                execution_time = end_time - start_time
                model_times[model].append(execution_time)
                
                results_text += f"Execução {run}:\n"
                results_text += f"Tempo: {execution_time:.4f} segundos\n"
                results_text += f"Resposta: {response}\n\n"
                
    results_text += "=== Resumo de Tempos Médios ===\n"
    for model in models:
        if model_times[model]:
            avg_time = sum(model_times[model]) / len(model_times[model])
            results_text += f"Modelo {model}: Média de {avg_time:.4f} segundos por execução\n"
        
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(results_text)
        
    print(f"Benchmark finalizado com sucesso! Resultados salvos em: {output_file}")
    
if __name__ == "__main__":
    main()
