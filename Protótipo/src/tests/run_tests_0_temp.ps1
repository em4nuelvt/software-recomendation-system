$ErrorActionPreference = "Stop"

Write-Host "Iniciando execucao do PROMPT1 (Antigo)"
python "evaluate_models_0_temperature.py"

Write-Host "Movendo resultados do PROMPT1..."
$outDir = "benchmark_output"
$backupAntigo = "$outDir\test_backup\temperature0\prompt antigo"

if (!(Test-Path $backupAntigo)) { New-Item -ItemType Directory -Force -Path $backupAntigo }

Move-Item -Path "$outDir\resultados_detalhados.txt" -Destination "$backupAntigo\resultados_detalhados.txt" -Force
Move-Item -Path "$outDir\resumo_metricas.txt" -Destination "$backupAntigo\resumo_metricas.txt" -Force

Write-Host "Trocando PROMPT1 por PROMPT2 em RequirementExtractor.py..."
$reqExtrFile = "..\RequirementExtractor.py"
(Get-Content $reqExtrFile -Encoding UTF8) -replace 'prompt: str = PROMPT1', 'prompt: str = PROMPT2' | Set-Content $reqExtrFile -Encoding UTF8

Write-Host "Iniciando execucao do PROMPT2 (Novo)"
python "evaluate_models_0_temperature.py"

Write-Host "Movendo resultados do PROMPT2..."
$backupNovo = "$outDir\test_backup\temperature0\prompt novo"

if (!(Test-Path $backupNovo)) { New-Item -ItemType Directory -Force -Path $backupNovo }

Move-Item -Path "$outDir\resultados_detalhados.txt" -Destination "$backupNovo\resultados_detalhados.txt" -Force
Move-Item -Path "$outDir\resumo_metricas.txt" -Destination "$backupNovo\resumo_metricas.txt" -Force

Write-Host "Restaurando PROMPT1 em RequirementExtractor.py..."
(Get-Content $reqExtrFile -Encoding UTF8) -replace 'prompt: str = PROMPT2', 'prompt: str = PROMPT1' | Set-Content $reqExtrFile -Encoding UTF8

Write-Host "Todas as execucoes concluidas com sucesso!"

Write-Host 'Gerando Relatorios de Acuracia Oficiais...'
python "calculate_accuracy.py"

Write-Host 'Atualizando Graficos...'
python "plot_results.py"
