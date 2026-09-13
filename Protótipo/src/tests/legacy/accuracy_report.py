import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean

DETAILED_FILE = Path(__file__).resolve().parent / "benchmark_output" / "resultados_detalhados.txt"
GROUND_TRUTH_FILE = Path(__file__).resolve().parent / "results_templates" / "gabarito_pessoal_requisitos.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "benchmark_output"
ACCURACY_REPORT_FILE = OUTPUT_DIR / "accuracy_report.txt"

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

SEPARATOR = "-" * 90


def parse_records(filepath: Path):
    text = filepath.read_text(encoding="utf-8")
    blocks = text.split(SEPARATOR)

    records = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        if "Modelo:" not in block or "Resposta_JSON:" not in block:
            continue

        model_m = re.search(r"^Modelo: (.+)$", block, re.MULTILINE)
        case_m = re.search(r"^Caso de teste: (\d+)$", block, re.MULTILINE)
        valid_m = re.search(r"^Formato_valido: (sim|nao)$", block, re.MULTILINE)

        if not (model_m and case_m and valid_m):
            continue

        model = model_m.group(1).strip()
        case_id = int(case_m.group(1))
        valid = valid_m.group(1) == "sim"

        json_idx = block.find("Resposta_JSON:")
        json_str = block[json_idx + len("Resposta_JSON:"):].strip()

        response = None
        if valid:
            try:
                response = json.loads(json_str)
            except json.JSONDecodeError:
                pass

        records.append({
            "model": model,
            "case_id": case_id,
            "valid": valid,
            "response": response,
        })

    return records


def compute_accuracy(record, ground_truth):
    """
    Retorna a acuracia de um registro em relacao ao gabarito.
    Retorna (acuracia_total, dict_por_atributo).
    acuracia_total = atributos_corretos / total_atributos
    dict_por_atributo = {atributo: True/False}
    """
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


def pct(value):
    return "{:.2f}%".format(value * 100.0)


def write_report(records, ground_truth):
    # Filtrar somente registros validos com case_id presente no gabarito
    valid_records = [
        r for r in records
        if r["valid"] and r["response"] is not None and str(r["case_id"]) in ground_truth
    ]

    if not valid_records:
        print("Nenhum registro valido encontrado para calcular acuracia.")
        return

    # Estruturas de agregacao
    by_model_case = defaultdict(list)   # (model, case_id) -> list of (accuracy, attr_results)
    by_model = defaultdict(list)         # model -> list of accuracy
    by_attribute = defaultdict(list)     # attribute -> list of bool

    for rec in valid_records:
        accuracy, attr_results = compute_accuracy(rec, ground_truth)
        key = (rec["model"], rec["case_id"])
        by_model_case[key].append((accuracy, attr_results))
        by_model[rec["model"]].append(accuracy)
        for attr, correct in attr_results.items():
            by_attribute[attr].append(correct)

    # Coletar modelos e cases na ordem original
    seen_models = []
    for rec in records:
        if rec["model"] not in seen_models:
            seen_models.append(rec["model"])

    case_ids = sorted({rec["case_id"] for rec in records})

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with ACCURACY_REPORT_FILE.open("w", encoding="utf-8") as f:
        f.write("Relatorio de Acuracia vs. Gabarito\n")
        f.write("Gabarito utilizado: {}\n".format(GROUND_TRUTH_FILE))
        f.write("Fonte de dados: {}\n".format(DETAILED_FILE))
        f.write("Registros validos avaliados: {}\n".format(len(valid_records)))
        f.write("=" * 90 + "\n")

        # 1) Acuracia por modelo e caso
        f.write("\n1) Acuracia por modelo e caso de teste\n")
        for model in seen_models:
            for case_id in case_ids:
                key = (model, case_id)
                if key not in by_model_case:
                    continue
                entries = by_model_case[key]
                accuracies = [e[0] for e in entries]
                fully_correct = sum(1 for a in accuracies if a == 1.0)

                f.write("\nModelo: {} | Caso de teste: {}\n".format(model, case_id))
                f.write("Execucoes validas avaliadas: {}\n".format(len(entries)))
                f.write("Acuracia media: {}\n".format(pct(mean(accuracies))))
                f.write("Acuracia minima: {}\n".format(pct(min(accuracies))))
                f.write("Acuracia maxima: {}\n".format(pct(max(accuracies))))
                f.write("Execucoes 100% corretas: {}/{}\n".format(fully_correct, len(entries)))

                # Acuracia por atributo neste (model, case)
                attr_correct = defaultdict(int)
                for _, attr_results in entries:
                    for attr, correct in attr_results.items():
                        if correct:
                            attr_correct[attr] += 1
                total_entries = len(entries)
                wrong_attrs = [
                    (attr, attr_correct[attr], total_entries)
                    for attr in EXPECTED_KEYS
                    if attr_correct[attr] < total_entries
                ]
                if wrong_attrs:
                    f.write("Atributos com acertos abaixo de 100%:\n")
                    for attr, correct_n, total_n in sorted(wrong_attrs, key=lambda x: x[1]):
                        f.write("  {}: {}/{} ({})\n".format(
                            attr, correct_n, total_n, pct(correct_n / total_n)
                        ))

        # 2) Acuracia consolidada por modelo
        f.write("\n2) Acuracia consolidada por modelo\n")
        model_ranking = []
        for model in seen_models:
            if model not in by_model:
                continue
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

        # 3) Acuracia por atributo (global)
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

        # 4) Ranking por acuracia media
        f.write("\n4) Ranking dos modelos por acuracia media\n")
        f.write("Criterio: maior acuracia media, depois maior proporcao de execucoes 100% corretas\n")
        model_ranking.sort(key=lambda x: (-x[1], -x[2]))
        for i, (model, avg, fully, total_n) in enumerate(model_ranking, start=1):
            f.write("{}. {} | acuracia media={} | 100% corretas={}/{}\n".format(
                i, model, pct(avg), fully, total_n
            ))

    print(f"Relatorio salvo: {ACCURACY_REPORT_FILE}")


def main():
    if not DETAILED_FILE.exists():
        print(f"Arquivo nao encontrado: {DETAILED_FILE}")
        return

    if not GROUND_TRUTH_FILE.exists():
        print(f"Gabarito nao encontrado: {GROUND_TRUTH_FILE}")
        print("Execute compute_ground_truth.py primeiro para gerar o gabarito.")
        return

    print(f"Lendo resultados: {DETAILED_FILE}")
    records = parse_records(DETAILED_FILE)
    total = len(records)
    valid = sum(1 for r in records if r["valid"])
    print(f"Registros: {total} total | {valid} validos | {total - valid} invalidos")

    print(f"Carregando gabarito: {GROUND_TRUTH_FILE}")
    ground_truth = json.loads(GROUND_TRUTH_FILE.read_text(encoding="utf-8"))
    print(f"Gabarito carregado com {len(ground_truth)} caso(s) de teste.")

    write_report(records, ground_truth)


if __name__ == "__main__":
    main()
