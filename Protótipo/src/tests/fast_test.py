import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from typing import Any, Dict, List, Tuple
import sys

# Insere a raiz do src no path para poder importar RequirementExtractor e user_input
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from RequirementExtractor import RequirementExtractor
import user_input as ui

# =============================================================================
# CONFIGURAÇÕES DO BENCHMARK
# =============================================================================
MODELS = ["qwen2.5", "llama3", "deepseek-r1:8b"]
REPETITIONS = 30
TEST_INPUTS = ui.inputs

OUTPUT_DIR = Path(__file__).resolve().parent / "benchmark_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Novos arquivos de saída
DETAILED_OUTPUT_FILE = OUTPUT_DIR / "resultados_detalhados_fast_test.txt"
SUMMARY_OUTPUT_FILE = OUTPUT_DIR / "resumo_metricas_fast_test.txt"
ACCURACY_REPORT_FILE = OUTPUT_DIR / "accuracy_report_fast_test.txt"

# Gabarito de referência utilizado no cálculo de acurácia
ACCURACY_GROUND_TRUTH = Path(__file__).resolve().parent / "results_templates" / "gabarito_pessoal_requisitos.json"

EXPECTED_KEYS = [
    "tipo_projeto",
    "dominio_negocio",
    "persistencia",
    "escala",
    "integracao",
    "arquitetura_esperada",
    "experiencia_usuario",
    "requisito_seguranca",
    "ambiente_implantacao",
    "maturidade_equipe",
    "tipo_autenticacao",
    "ciclo_desenvolvimento",
]

ALLOWED_VALUES = {
    "tipo_projeto": {"web", "mobile", "desktop", "api", "embarcado", "hibrido"},
    "dominio_negocio": {"produtividade", "financeiro", "saude", "educacao", "ecommerce", "logistica", "entretenimento", "outro"},
    "persistencia": {"sem_banco", "sql", "nosql", "hibrido"},
    "escala": {"pequena", "media", "grande", "enterprise"},
    "integracao": {"nenhuma", "apis_externas", "servicos_internos", "ambos"},
    "arquitetura_esperada": {"monolito", "microsservicos", "serverless", "event_driven"},
    "experiencia_usuario": {"basica", "intermediaria", "avancada"},
    "requisito_seguranca": {"nenhum", "basico", "intermediario", "avancado"},
    "ambiente_implantacao": {"local", "cloud", "on_premise", "hibrido"},
    "maturidade_equipe": {"iniciante", "intermediario", "experiente"},
    "tipo_autenticacao": {"nenhuma", "propria", "oauth", "enterprise"},
    "ciclo_desenvolvimento": {"mvp", "iterativo", "longo_prazo"},
}

# =============================================================================
# MÉTODOS DO BENCHMARK (requirement_extractor_benchmark.py)
# =============================================================================

def percentile(values: List[float], p: float) -> float:
    if not values: return 0.0
    values = sorted(values)
    if len(values) == 1: return values[0]
    pos = (len(values) - 1) * (p / 100.0)
    low = int(math.floor(pos))
    high = int(math.ceil(pos))
    if low == high: return values[low]
    weight = pos - low
    return values[low] + (values[high] - values[low]) * weight

def validate_schema(response: Any) -> Tuple[bool, List[str], float]:
    reasons: List[str] = []
    if not isinstance(response, dict): return False, ["resposta_nao_e_dict"], 0.0
    if "ERRO" in response: return False, ["erro_extractor"], 0.0
    expected_set = set(EXPECTED_KEYS)
    received_set = set(response.keys())
    for key in sorted(expected_set - received_set): reasons.append("chave_ausente:" + key)
    for key in sorted(received_set - expected_set): reasons.append("chave_extra:" + key)
    for key in EXPECTED_KEYS:
        if key not in response: continue
        val = response[key]
        if not isinstance(val, str):
            reasons.append("tipo_invalido:" + key)
            continue
        if val not in ALLOWED_VALUES[key]:
            reasons.append("valor_invalido:" + key + "=" + str(val))
    key_coverage = len(received_set.intersection(expected_set)) / float(len(EXPECTED_KEYS))
    return len(reasons) == 0, reasons, key_coverage

def canonicalize_valid_response(response: Dict[str, str]) -> str:
    ordered = {}
    for key in EXPECTED_KEYS:
        ordered[key] = response.get(key, "")
    return json.dumps(ordered, ensure_ascii=False, sort_keys=False)

def aggregate_metrics(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    total = len(records)
    if total == 0:
        return {"total_runs": 0, "mean_latency_ms": 0.0, "median_latency_ms": 0.0, "p95_latency_ms": 0.0, "min_latency_ms": 0.0, "max_latency_ms": 0.0, "format_valid_rate": 0.0, "error_rate": 0.0, "success_rate": 0.0, "avg_key_coverage": 0.0, "distinct_valid_outputs": 0, "consistency_total_rate": 0.0, "consistency_valid_rate": 0.0}
    latencies = [r["latency_ms"] for r in records]
    key_coverages = [r["key_coverage"] for r in records]
    valid_count = sum(1 for r in records if r["schema_valid"])
    error_count = sum(1 for r in records if r["has_error"])
    success_count = sum(1 for r in records if r["schema_valid"] and not r["has_error"])
    valid_outputs = [r["canonical_output"] for r in records if r["canonical_output"]]
    distinct_valid_outputs = 0
    consistency_total_rate = 0.0
    consistency_valid_rate = 0.0
    if valid_outputs:
        counter = Counter(valid_outputs)
        top_count = counter.most_common(1)[0][1]
        distinct_valid_outputs = len(counter)
        consistency_total_rate = top_count / float(total)
        consistency_valid_rate = top_count / float(len(valid_outputs))
    return {
        "total_runs": total, "mean_latency_ms": mean(latencies), "median_latency_ms": median(latencies), "p95_latency_ms": percentile(latencies, 95), "min_latency_ms": min(latencies), "max_latency_ms": max(latencies), "format_valid_rate": valid_count / float(total), "error_rate": error_count / float(total), "success_rate": success_count / float(total), "avg_key_coverage": mean(key_coverages), "distinct_valid_outputs": distinct_valid_outputs, "consistency_total_rate": consistency_total_rate, "consistency_valid_rate": consistency_valid_rate
    }

def pct(value: float) -> str:
    return "{:.2f}%".format(value * 100.0)

def shorten(text: str, limit: int = 120) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit: return compact
    return compact[: limit - 3] + "..."

def format_duration(seconds: float) -> str:
    total_seconds = int(round(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def run_benchmark() -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    total_runs = len(MODELS) * len(TEST_INPUTS) * REPETITIONS
    completed_runs = 0
    progress_start = perf_counter()
    if total_runs == 0: return records
    for model in MODELS:
        extractor = RequirementExtractor(model=model)
        for case_id, input_text in enumerate(TEST_INPUTS, start=1):
            for iteration in range(1, REPETITIONS + 1):
                start = perf_counter()
                try:
                    response = extractor.extractRequirement(input_text)
                except Exception as exc:
                    response = {"ERRO": "falha_no_benchmark: " + str(exc)}
                latency_ms = (perf_counter() - start) * 1000.0
                schema_valid, invalid_reasons, key_coverage = validate_schema(response)
                has_error = isinstance(response, dict) and ("ERRO" in response)
                error_message = ""
                if has_error:
                    try: error_message = str(response.get("ERRO", ""))
                    except Exception: error_message = "erro_desconhecido"
                canonical_output = ""
                if schema_valid and not has_error and isinstance(response, dict):
                    canonical_output = canonicalize_valid_response(response)
                records.append({
                    "model": model, "case_id": case_id, "iteration": iteration, "input_text": input_text, "latency_ms": latency_ms, "schema_valid": schema_valid, "has_error": has_error, "error_message": error_message, "invalid_reasons": invalid_reasons, "key_coverage": key_coverage, "response": response, "canonical_output": canonical_output
                })
                completed_runs += 1
                elapsed = perf_counter() - progress_start
                percent = (completed_runs / total_runs) * 100.0
                print(f"\rProgresso: {completed_runs}/{total_runs} ({percent:.1f}%) | Decorrido: {elapsed:.1f}s | Modelo: {model} | Caso: {case_id} | Iteracao: {iteration}", end="", flush=True)
    print()
    return records

def write_detailed_report(records: List[Dict[str, Any]], started_at: datetime, ended_at: datetime) -> None:
    with DETAILED_OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("Benchmark Etapa 1 - Resultados Detalhados\n")
        f.write("Inicio: {}\n".format(started_at.strftime("%Y-%m-%d %H:%M:%S")))
        f.write("Fim: {}\n".format(ended_at.strftime("%Y-%m-%d %H:%M:%S")))
        f.write("Modelos: {}\n".format(", ".join(MODELS)))
        f.write("Casos de teste: {}\n".format(len(TEST_INPUTS)))
        f.write("Repeticoes por caso/modelo: {}\n".format(REPETITIONS))
        f.write("=" * 90 + "\n")
        for rec in records:
            f.write("Modelo: {}\n".format(rec["model"]))
            f.write("Caso de teste: {}\n".format(rec["case_id"]))
            f.write("Iteracao: {}\n".format(rec["iteration"]))
            f.write("Tempo_ms: {:.2f}\n".format(rec["latency_ms"]))
            f.write("Formato_valido: {}\n".format("sim" if rec["schema_valid"] else "nao"))
            f.write("Cobertura_de_chaves: {:.2f}%\n".format(rec["key_coverage"] * 100.0))
            f.write("Erro_execucao: {}\n".format("sim" if rec["has_error"] else "nao"))
            if rec["error_message"]: f.write("Mensagem_erro: {}\n".format(rec["error_message"]))
            if rec["invalid_reasons"]: f.write("Motivos_invalidacao: {}\n".format("; ".join(rec["invalid_reasons"])))
            else: f.write("Motivos_invalidacao: nenhum\n")
            f.write("Entrada:\n")
            f.write(rec["input_text"].strip() + "\n")
            f.write("Resposta_JSON:\n")
            f.write(json.dumps(rec["response"], ensure_ascii=False, indent=4, sort_keys=True))
            f.write("\n")
            f.write("-" * 90 + "\n")

def write_summary_report(records: List[Dict[str, Any]], started_at: datetime, ended_at: datetime) -> None:
    by_model_case: Dict[Tuple[str, int], List[Dict[str, Any]]] = defaultdict(list)
    by_model: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for rec in records:
        by_model_case[(rec["model"], rec["case_id"])].append(rec)
        by_model[rec["model"]].append(rec)
    with SUMMARY_OUTPUT_FILE.open("w", encoding="utf-8") as f:
        f.write("Benchmark Etapa 1 - Resumo de Metricas\n")
        f.write("Inicio: {}\n".format(started_at.strftime("%Y-%m-%d %H:%M:%S")))
        f.write("Fim: {}\n".format(ended_at.strftime("%Y-%m-%d %H:%M:%S")))
        total_seconds = (ended_at - started_at).total_seconds()
        f.write("Tempo total: {}\n".format(format_duration(total_seconds)))
        f.write("Modelos: {}\n".format(", ".join(MODELS)))
        f.write("Casos de teste: {}\n".format(len(TEST_INPUTS)))
        f.write("Repeticoes por caso/modelo: {}\n".format(REPETITIONS))
        f.write("\n")
        f.write("Metricas:\n")
        f.write("- Tempo medio (ms), tempo mediano (ms), tempo p95 (ms), tempo minimo (ms), tempo maximo (ms)\n")
        f.write("- Taxa de formato valido, taxa de erro de execucao, taxa de sucesso\n")
        f.write("- Consistencia total, consistencia somente validos, saidas validas distintas\n")
        f.write("- Cobertura media de chaves\n")
        f.write("=" * 90 + "\n")
        f.write("\n1) Resultado por modelo e caso de teste\n")
        for model in MODELS:
            for case_id in range(1, len(TEST_INPUTS) + 1):
                key = (model, case_id)
                if key not in by_model_case: continue
                metrics = aggregate_metrics(by_model_case[key])
                f.write("\nModelo: {} | Caso de teste: {}\n".format(model, case_id))
                f.write("Entrada (resumo): {}\n".format(shorten(TEST_INPUTS[case_id - 1])))
                f.write("Total de execucoes: {}\n".format(metrics["total_runs"]))
                f.write("Tempo medio (ms): {:.2f}\n".format(metrics["mean_latency_ms"]))
                f.write("Tempo mediano (ms): {:.2f}\n".format(metrics["median_latency_ms"]))
                f.write("Tempo p95 (ms): {:.2f}\n".format(metrics["p95_latency_ms"]))
                f.write("Tempo minimo (ms): {:.2f}\n".format(metrics["min_latency_ms"]))
                f.write("Tempo maximo (ms): {:.2f}\n".format(metrics["max_latency_ms"]))
                f.write("Taxa de formato valido: {}\n".format(pct(metrics["format_valid_rate"])))
                f.write("Taxa de erro de execucao: {}\n".format(pct(metrics["error_rate"])))
                f.write("Taxa de sucesso: {}\n".format(pct(metrics["success_rate"])))
                f.write("Cobertura media de chaves: {}\n".format(pct(metrics["avg_key_coverage"])))
                f.write("Saidas validas distintas: {}\n".format(metrics["distinct_valid_outputs"]))
                f.write("Consistencia total: {}\n".format(pct(metrics["consistency_total_rate"])))
                f.write("Consistencia somente validos: {}\n".format(pct(metrics["consistency_valid_rate"])))
        f.write("\n2) Resultado consolidado por modelo\n")
        model_ranking = []
        for model in MODELS:
            if model not in by_model: continue
            metrics = aggregate_metrics(by_model[model])
            model_ranking.append((model, metrics))
            f.write("\nModelo: {}\n".format(model))
            f.write("Total de execucoes: {}\n".format(metrics["total_runs"]))
            f.write("Tempo medio (ms): {:.2f}\n".format(metrics["mean_latency_ms"]))
            f.write("Tempo mediano (ms): {:.2f}\n".format(metrics["median_latency_ms"]))
            f.write("Tempo p95 (ms): {:.2f}\n".format(metrics["p95_latency_ms"]))
            f.write("Tempo minimo (ms): {:.2f}\n".format(metrics["min_latency_ms"]))
            f.write("Tempo maximo (ms): {:.2f}\n".format(metrics["max_latency_ms"]))
            f.write("Taxa de formato valido: {}\n".format(pct(metrics["format_valid_rate"])))
            f.write("Taxa de erro de execucao: {}\n".format(pct(metrics["error_rate"])))
            f.write("Taxa de sucesso: {}\n".format(pct(metrics["success_rate"])))
            f.write("Cobertura media de chaves: {}\n".format(pct(metrics["avg_key_coverage"])))
            f.write("Saidas validas distintas: {}\n".format(metrics["distinct_valid_outputs"]))
            f.write("Consistencia total: {}\n".format(pct(metrics["consistency_total_rate"])))
            f.write("Consistencia somente validos: {}\n".format(pct(metrics["consistency_valid_rate"])))
        global_metrics = aggregate_metrics(records)
        f.write("\n3) Resultado global de todos os modelos\n")
        f.write("Total de execucoes: {}\n".format(global_metrics["total_runs"]))
        f.write("Tempo medio (ms): {:.2f}\n".format(global_metrics["mean_latency_ms"]))
        f.write("Tempo mediano (ms): {:.2f}\n".format(global_metrics["median_latency_ms"]))
        f.write("Tempo p95 (ms): {:.2f}\n".format(global_metrics["p95_latency_ms"]))
        f.write("Taxa de formato valido: {}\n".format(pct(global_metrics["format_valid_rate"])))
        f.write("Taxa de erro de execucao: {}\n".format(pct(global_metrics["error_rate"])))
        f.write("Taxa de sucesso: {}\n".format(pct(global_metrics["success_rate"])))
        f.write("Cobertura media de chaves: {}\n".format(pct(global_metrics["avg_key_coverage"])))
        f.write("Consistencia total: {}\n".format(pct(global_metrics["consistency_total_rate"])))
        f.write("Consistencia somente validos: {}\n".format(pct(global_metrics["consistency_valid_rate"])))
        model_ranking.sort(key=lambda x: (-x[1]["success_rate"], -x[1]["consistency_valid_rate"], x[1]["mean_latency_ms"]))
        f.write("\n4) Ranking sugerido dos modelos\n")
        f.write("Criterio: sucesso maior, depois consistencia maior, depois menor tempo medio\n")
        for i, (model, metrics) in enumerate(model_ranking, start=1):
            f.write("{}. {} | sucesso={} | consistencia validos={} | tempo medio (ms)={:.2f}\n".format(i, model, pct(metrics["success_rate"]), pct(metrics["consistency_valid_rate"]), metrics["mean_latency_ms"]))

# =============================================================================
# MÉTODOS DE ACURÁCIA (accuracy_report.py)
# =============================================================================

def parse_records_for_accuracy(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    blocks = text.split("-" * 90)
    records = []
    for block in blocks:
        block = block.strip()
        if not block: continue
        if "Modelo:" not in block or "Resposta_JSON:" not in block: continue
        model_m = re.search(r"^Modelo: (.+)$", block, re.MULTILINE)
        case_m = re.search(r"^Caso de teste: (\d+)$", block, re.MULTILINE)
        valid_m = re.search(r"^Formato_valido: (sim|nao)$", block, re.MULTILINE)
        if not (model_m and case_m and valid_m): continue
        model = model_m.group(1).strip()
        case_id = int(case_m.group(1))
        valid = valid_m.group(1) == "sim"
        json_idx = block.find("Resposta_JSON:")
        json_str = block[json_idx + len("Resposta_JSON:"):].strip()
        response = None
        if valid:
            try: response = json.loads(json_str)
            except json.JSONDecodeError: pass
        records.append({
            "model": model, "case_id": case_id, "valid": valid, "response": response,
        })
    return records

def compute_single_accuracy(record, ground_truth):
    case_key = str(record["case_id"])
    expected = ground_truth.get(case_key, {})
    response = record["response"]
    attr_results = {}
    for key in EXPECTED_KEYS:
        if key in expected and key in response:
            attr_results[key] = (response[key] == expected[key])
        else:
            attr_results[key] = False
    correct = sum(1 for v in attr_results.values() if v)
    accuracy = correct / len(EXPECTED_KEYS)
    return accuracy, attr_results

def generate_accuracy_report():
    if not DETAILED_OUTPUT_FILE.exists():
        print(f"Arquivo nao encontrado para acuracia: {DETAILED_OUTPUT_FILE}")
        return
    if not ACCURACY_GROUND_TRUTH.exists():
        print(f"Gabarito de acuracia nao encontrado: {ACCURACY_GROUND_TRUTH}")
        return

    records = parse_records_for_accuracy(DETAILED_OUTPUT_FILE)
    ground_truth = json.loads(ACCURACY_GROUND_TRUTH.read_text(encoding="utf-8"))

    valid_records = [r for r in records if r["valid"] and r["response"] is not None and str(r["case_id"]) in ground_truth]
    if not valid_records:
        print("Nenhum registro valido encontrado para calcular acuracia no relatorio de acuracia.")
        return

    by_model_case = defaultdict(list)
    by_model = defaultdict(list)
    by_attribute = defaultdict(list)
    for rec in valid_records:
        accuracy, attr_results = compute_single_accuracy(rec, ground_truth)
        key = (rec["model"], rec["case_id"])
        by_model_case[key].append((accuracy, attr_results))
        by_model[rec["model"]].append(accuracy)
        for attr, correct in attr_results.items():
            by_attribute[attr].append(correct)

    seen_models = []
    for rec in records:
        if rec["model"] not in seen_models: seen_models.append(rec["model"])
    case_ids = sorted({rec["case_id"] for rec in records})

    with ACCURACY_REPORT_FILE.open("w", encoding="utf-8") as f:
        f.write("Relatorio de Acuracia vs. Gabarito\n")
        f.write("Gabarito utilizado: {}\n".format(ACCURACY_GROUND_TRUTH))
        f.write("Fonte de dados: {}\n".format(DETAILED_OUTPUT_FILE))
        f.write("Registros validos avaliados: {}\n".format(len(valid_records)))
        f.write("=" * 90 + "\n")
        f.write("\n1) Acuracia por modelo e caso de teste\n")
        for model in seen_models:
            for case_id in case_ids:
                key = (model, case_id)
                if key not in by_model_case: continue
                entries = by_model_case[key]
                accuracies = [e[0] for e in entries]
                fully_correct = sum(1 for a in accuracies if a == 1.0)
                f.write("\nModelo: {} | Caso de teste: {}\n".format(model, case_id))
                f.write("Execucoes validas avaliadas: {}\n".format(len(entries)))
                f.write("Acuracia media: {}\n".format(pct(mean(accuracies))))
                f.write("Acuracia minima: {}\n".format(pct(min(accuracies))))
                f.write("Acuracia maxima: {}\n".format(pct(max(accuracies))))
                f.write("Execucoes 100% corretas: {}/{}\n".format(fully_correct, len(entries)))
                attr_correct = defaultdict(int)
                for _, attr_results in entries:
                    for attr, correct in attr_results.items():
                        if correct: attr_correct[attr] += 1
                total_entries = len(entries)
                wrong_attrs = [(attr, attr_correct[attr], total_entries) for attr in EXPECTED_KEYS if attr_correct[attr] < total_entries]
                if wrong_attrs:
                    f.write("Atributos com acertos abaixo de 100%:\n")
                    for attr, correct_n, total_n in sorted(wrong_attrs, key=lambda x: x[1]):
                        f.write("  {}: {}/{} ({})\n".format(attr, correct_n, total_n, pct(correct_n / total_n)))

        f.write("\n2) Acuracia consolidada por modelo\n")
        model_ranking = []
        for model in seen_models:
            if model not in by_model: continue
            accuracies = by_model[model]
            avg = mean(accuracies)
            fully = sum(1 for a in accuracies if a == 1.0)
            model_ranking.append((model, avg, fully, len(accuracies)))
            f.write("\nModelo: {}\n".format(model))
            f.write("Total de execucoes validas avaliadas: {}\n".format(len(accuracies)))
            f.write("Acuracia media: {}\n".format(pct(avg)))
            f.write("Acuracia minima: {}\n".format(pct(min(accuracies))))
            f.write("Acuracia maxima: {}\n".format(pct(max(accuracies))))
            f.write("Execucoes 100% corretas: {}/{}\n".format(fully, len(accuracies)))

        f.write("\n3) Acuracia por atributo (todos os modelos e casos)\n")
        f.write("(mostra quais atributos os modelos mais erram)\n")
        attr_summary = []
        for attr in EXPECTED_KEYS:
            results = by_attribute[attr]
            if results:
                acc = sum(results) / len(results)
                attr_summary.append((attr, acc, sum(results), len(results)))
        attr_summary.sort(key=lambda x: x[1])
        for attr, acc, correct_n, total_n in attr_summary:
            f.write("  {}: {}/{} ({})\n".format(attr, correct_n, total_n, pct(acc)))

        f.write("\n4) Ranking dos modelos por acuracia media\n")
        f.write("Criterio: maior acuracia media, depois maior proporcao de execucoes 100% corretas\n")
        model_ranking.sort(key=lambda x: (-x[1], -x[2]))
        for i, (model, avg, fully, total_n) in enumerate(model_ranking, start=1):
            f.write("{}. {} | acuracia media={} | 100% corretas={}/{}\n".format(i, model, pct(avg), fully, total_n))
    print(f"Relatorio de acuracia final salvo: {ACCURACY_REPORT_FILE}")

# =============================================================================
# MAIN
# =============================================================================

def main() -> None:
    print(f"Iniciando FAST_TEST de benchmark para os modelos {MODELS}\n")
    started_at = datetime.now()
    records = run_benchmark()
    ended_at = datetime.now()

    write_detailed_report(records, started_at, ended_at)
    write_summary_report(records, started_at, ended_at)

    print("\nGerando relatorio de acuracia estendido...")
    generate_accuracy_report()

    print("\nTeste finalizado com sucesso!")
    print(f"Detalhado: {DETAILED_OUTPUT_FILE}")
    print(f"Resumo: {SUMMARY_OUTPUT_FILE}")
    print(f"Acuracia: {ACCURACY_REPORT_FILE}")

if __name__ == "__main__":
    main()
