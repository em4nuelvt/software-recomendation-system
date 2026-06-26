import json
import math
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from statistics import mean, median
from time import perf_counter
from typing import Any, Dict, List, Tuple

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from RequirementExtractor import RequirementExtractor
import user_input as ui


MODELS = ["qwen2.5", "llama3", "deepseek-r1:8b"]
REPETITIONS = 30
TEST_INPUTS = ui.inputs

OUTPUT_DIR = Path(__file__).resolve().parent / "benchmark_output"
DETAILED_OUTPUT_FILE = OUTPUT_DIR / "resultados_detalhados.txt"
SUMMARY_OUTPUT_FILE = OUTPUT_DIR / "resumo_metricas.txt"
GROUND_TRUTH_FILE = Path(__file__).resolve().parent / "results_templates" / "ground_truth.json"

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


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0

    values = sorted(values)
    if len(values) == 1:
        return values[0]

    pos = (len(values) - 1) * (p / 100.0)
    low = int(math.floor(pos))
    high = int(math.ceil(pos))

    if low == high:
        return values[low]

    weight = pos - low
    return values[low] + (values[high] - values[low]) * weight


def validate_schema(response: Any) -> Tuple[bool, List[str], float]:
    reasons: List[str] = []

    if not isinstance(response, dict):
        return False, ["resposta_nao_e_dict"], 0.0

    if "ERRO" in response:
        return False, ["erro_extractor"], 0.0

    expected_set = set(EXPECTED_KEYS)
    received_set = set(response.keys())

    missing_keys = sorted(expected_set - received_set)
    extra_keys = sorted(received_set - expected_set)

    for key in missing_keys:
        reasons.append("chave_ausente:" + key)
    for key in extra_keys:
        reasons.append("chave_extra:" + key)

    for key in EXPECTED_KEYS:
        if key not in response:
            continue

        value = response[key]
        if not isinstance(value, str):
            reasons.append("tipo_invalido:" + key)
            continue

        if value not in ALLOWED_VALUES[key]:
            reasons.append("valor_invalido:" + key + "=" + str(value))

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
        return {
            "total_runs": 0,
            "mean_latency_ms": 0.0,
            "median_latency_ms": 0.0,
            "p95_latency_ms": 0.0,
            "min_latency_ms": 0.0,
            "max_latency_ms": 0.0,
            "format_valid_rate": 0.0,
            "error_rate": 0.0,
            "success_rate": 0.0,
            "avg_key_coverage": 0.0,
            "distinct_valid_outputs": 0,
            "consistency_total_rate": 0.0,
            "consistency_valid_rate": 0.0,
        }

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
        "total_runs": total,
        "mean_latency_ms": mean(latencies),
        "median_latency_ms": median(latencies),
        "p95_latency_ms": percentile(latencies, 95),
        "min_latency_ms": min(latencies),
        "max_latency_ms": max(latencies),
        "format_valid_rate": valid_count / float(total),
        "error_rate": error_count / float(total),
        "success_rate": success_count / float(total),
        "avg_key_coverage": mean(key_coverages),
        "distinct_valid_outputs": distinct_valid_outputs,
        "consistency_total_rate": consistency_total_rate,
        "consistency_valid_rate": consistency_valid_rate,
    }


def compute_accuracy_metrics(records, ground_truth):
    """
    Compara cada execucao valida com o gabarito.
    Retorna (by_model_case, by_model):
      by_model_case: {(model, case_id): [accuracy, ...]}
      by_model:      {model: [accuracy, ...]}
    """
    by_model_case: Dict[Tuple[str, int], List[float]] = defaultdict(list)
    by_model: Dict[str, List[float]] = defaultdict(list)

    for rec in records:
        if not rec["schema_valid"] or rec["has_error"]:
            continue
        case_key = str(rec["case_id"])
        if case_key not in ground_truth:
            continue

        expected = ground_truth[case_key]
        response = rec["response"]

        correct = sum(
            1 for key in EXPECTED_KEYS
            if key in expected and key in response and response[key] == expected[key]
        )
        accuracy = correct / float(len(EXPECTED_KEYS))

        by_model_case[(rec["model"], rec["case_id"])].append(accuracy)
        by_model[rec["model"]].append(accuracy)

    return by_model_case, by_model


def pct(value: float) -> str:
    return "{:.2f}%".format(value * 100.0)


def shorten(text: str, limit: int = 120) -> str:
    compact = " ".join(text.split())
    if len(compact) <= limit:
        return compact
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

    if total_runs == 0:
        return records

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
                    try:
                        error_message = str(response.get("ERRO", ""))
                    except Exception:
                        error_message = "erro_desconhecido"

                canonical_output = ""
                if schema_valid and not has_error and isinstance(response, dict):
                    canonical_output = canonicalize_valid_response(response)

                records.append(
                    {
                        "model": model,
                        "case_id": case_id,
                        "iteration": iteration,
                        "input_text": input_text,
                        "latency_ms": latency_ms,
                        "schema_valid": schema_valid,
                        "has_error": has_error,
                        "error_message": error_message,
                        "invalid_reasons": invalid_reasons,
                        "key_coverage": key_coverage,
                        "response": response,
                        "canonical_output": canonical_output,
                    }
                )

                completed_runs += 1
                elapsed = perf_counter() - progress_start
                percent = (completed_runs / total_runs) * 100.0
                print(
                    f"\rProgresso: {completed_runs}/{total_runs} ({percent:.1f}%) | "
                    f"Decorrido: {elapsed:.1f}s | Modelo: {model} | "
                    f"Caso: {case_id} | Iteracao: {iteration}",
                    end="",
                    flush=True,
                )

    print()

    return records


def write_detailed_report(records: List[Dict[str, Any]], started_at: datetime, ended_at: datetime) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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

            if rec["error_message"]:
                f.write("Mensagem_erro: {}\n".format(rec["error_message"]))

            if rec["invalid_reasons"]:
                f.write("Motivos_invalidacao: {}\n".format("; ".join(rec["invalid_reasons"])))
            else:
                f.write("Motivos_invalidacao: nenhum\n")

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
        if GROUND_TRUTH_FILE.exists():
            f.write("- Acuracia media vs. gabarito, acuracia minima, acuracia maxima, execucoes 100% corretas\n")
        f.write("=" * 90 + "\n")

        f.write("\n1) Resultado por modelo e caso de teste\n")
        for model in MODELS:
            for case_id in range(1, len(TEST_INPUTS) + 1):
                key = (model, case_id)
                if key not in by_model_case:
                    continue

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
            if model not in by_model:
                continue

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

        model_ranking.sort(
            key=lambda x: (
                -x[1]["success_rate"],
                -x[1]["consistency_valid_rate"],
                x[1]["mean_latency_ms"],
            )
        )

        f.write("\n4) Ranking sugerido dos modelos\n")
        f.write("Criterio: sucesso maior, depois consistencia maior, depois menor tempo medio\n")
        for i, (model, metrics) in enumerate(model_ranking, start=1):
            f.write(
                "{}. {} | sucesso={} | consistencia validos={} | tempo medio (ms)={:.2f}\n".format(
                    i,
                    model,
                    pct(metrics["success_rate"]),
                    pct(metrics["consistency_valid_rate"]),
                    metrics["mean_latency_ms"],
                )
            )

        if GROUND_TRUTH_FILE.exists():
            try:
                ground_truth = json.loads(GROUND_TRUTH_FILE.read_text(encoding="utf-8"))
                accuracy_by_model_case, accuracy_by_model = compute_accuracy_metrics(records, ground_truth)

                f.write("\n5) Acuracia vs. Gabarito\n")
                f.write("Gabarito: {}\n".format(GROUND_TRUTH_FILE))

                f.write("\n5a) Acuracia por modelo e caso de teste\n")
                for model in MODELS:
                    for case_id in range(1, len(TEST_INPUTS) + 1):
                        key = (model, case_id)
                        if key not in accuracy_by_model_case:
                            continue
                        accs = accuracy_by_model_case[key]
                        fully = sum(1 for a in accs if a == 1.0)
                        f.write("\nModelo: {} | Caso de teste: {}\n".format(model, case_id))
                        f.write("Execucoes validas avaliadas: {}\n".format(len(accs)))
                        f.write("Acuracia media: {}\n".format(pct(mean(accs))))
                        f.write("Execucoes 100% corretas: {}/{}\n".format(fully, len(accs)))

                f.write("\n5b) Acuracia consolidada por modelo\n")
                accuracy_ranking = []
                for model in MODELS:
                    if model not in accuracy_by_model:
                        continue
                    accs = accuracy_by_model[model]
                    avg = mean(accs)
                    fully = sum(1 for a in accs if a == 1.0)
                    accuracy_ranking.append((model, avg, fully, len(accs)))
                    f.write("\nModelo: {}\n".format(model))
                    f.write("Total de execucoes validas avaliadas: {}\n".format(len(accs)))
                    f.write("Acuracia media: {}\n".format(pct(avg)))
                    f.write("Execucoes 100% corretas: {}/{}\n".format(fully, len(accs)))

                accuracy_ranking.sort(key=lambda x: (-x[1], -x[2]))
                f.write("\n5c) Ranking dos modelos por acuracia media\n")
                f.write("Criterio: maior acuracia media, depois maior proporcao de execucoes 100% corretas\n")
                for i, (model, avg, fully, total_n) in enumerate(accuracy_ranking, start=1):
                    f.write("{}. {} | acuracia media={} | 100% corretas={}/{}\n".format(
                        i, model, pct(avg), fully, total_n
                    ))
            except Exception as exc:
                f.write("\n5) Acuracia vs. Gabarito\n")
                f.write("Erro ao calcular acuracia: {}\n".format(exc))


def main() -> None:
    print(f"Iniciando teste de benchmark para os modelos {MODELS}\n")
    started_at = datetime.now()
    records = run_benchmark()
    ended_at = datetime.now()

    write_detailed_report(records, started_at, ended_at)
    write_summary_report(records, started_at, ended_at)

    print("Benchmark finalizado.")
    print("Detalhado:", DETAILED_OUTPUT_FILE)
    print("Resumo:", SUMMARY_OUTPUT_FILE)


if __name__ == "__main__":
    main()