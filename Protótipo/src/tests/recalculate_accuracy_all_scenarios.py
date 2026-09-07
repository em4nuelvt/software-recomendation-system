"""
Recalcula a acurácia de TODOS os 4 cenários de teste salvos em test_backup/,
considerando TODAS as execuções (válidas E inválidas) no cálculo.

Mudança principal em relação ao accuracy_report.py original:
  - O script original filtrava somente registros com Formato_valido == "sim",
    o que enviesa a métrica (denominador variável por modelo).
  - Este script usa TODAS as N execuções como denominador fixo.
    Execuções inválidas que não geraram JSON parseável contam como 0/12 acertos.

Uso:
    python recalculate_accuracy_all_scenarios.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean

# ── Caminhos ─────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).resolve().parent
BACKUP_DIR = BASE_DIR / "benchmark_output" / "test_backup"
GROUND_TRUTH_FILE = BASE_DIR / "results_templates" / "gabarito_pessoal_requisitos.json"

# Mapeamento dos 4 cenários (Casos 1-5) + 4 cenários do teste de estresse (Caso 6)
SCENARIOS = [
    # ── Casos 1-5 ────────────────────────────────────────────────────────────
    {
        "name": "Cenário 1 — Temp Padrão + Prompt Antigo",
        "path": BACKUP_DIR / "standardtemperature" / "prompt antigo",
        "detailed_file": "resultados_detalhados_fast_test.txt",
        "output_file": "accuracy_report_fast_test.txt",
    },
    {
        "name": "Cenário 2 — Temp Padrão + Prompt Novo",
        "path": BACKUP_DIR / "standardtemperature" / "prompt novo",
        "detailed_file": "resultados_detalhados_fast_test.txt",
        "output_file": "accuracy_report_fast_test.txt",
    },
    {
        "name": "Cenário 3 — Temp Zero + Prompt Antigo",
        "path": BACKUP_DIR / "temperature0" / "prompt antigo",
        "detailed_file": "resultados_detalhados_0_temperature.txt",
        "output_file": "accuracy_report_0_temperature.txt",
    },
    {
        "name": "Cenário 4 — Temp Zero + Prompt Novo",
        "path": BACKUP_DIR / "temperature0" / "prompt novo",
        "detailed_file": "resultados_detalhados_0_temperature.txt",
        "output_file": "accuracy_report_0_temperature.txt",
    },
    # ── Teste de Estresse (Caso 6) ───────────────────────────────────────────
    {
        "name": "Estresse 1 — Prompt Antigo + Temp Padrão",
        "path": BACKUP_DIR / "largeInputTest" / "prompt antigo" / "standardtemperature",
        "detailed_file": "resultados_detalhados_stress_test.txt",
        "output_file": "accuracy_report_stress_test.txt",
    },
    {
        "name": "Estresse 2 — Prompt Antigo + Temp Zero",
        "path": BACKUP_DIR / "largeInputTest" / "prompt antigo" / "temperature0",
        "detailed_file": "resultados_detalhados_stress_test.txt",
        "output_file": "accuracy_report_stress_test.txt",
    },
    {
        "name": "Estresse 3 — Prompt Novo + Temp Padrão",
        "path": BACKUP_DIR / "largeInputTest" / "prompt novo" / "standardtemperature",
        "detailed_file": "resultados_detalhados_stress_test.txt",
        "output_file": "accuracy_report_stress_test.txt",
    },
    {
        "name": "Estresse 4 — Prompt Novo + Temp Zero",
        "path": BACKUP_DIR / "largeInputTest" / "prompt novo" / "temperature0",
        "detailed_file": "resultados_detalhados_stress_test.txt",
        "output_file": "accuracy_report_stress_test.txt",
    },
]

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


# ── Funções auxiliares ───────────────────────────────────────────────────────


def parse_records(filepath: Path):
    """Lê o arquivo de resultados detalhados e retorna lista de registros.
    
    Somente registros com Formato_valido == 'sim' têm o JSON parseado.
    Registros inválidos recebem response=None e contam como 0/12 na acurácia.
    """
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

        # Só parseia JSON se o formato foi validado como correto
        response = None
        if valid:
            json_idx = block.find("Resposta_JSON:")
            json_str = block[json_idx + len("Resposta_JSON:"):].strip()
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
    """Calcula acurácia de um registro em relação ao gabarito.
    
    Registros com formato inválido têm response=None, logo todos os 12
    atributos recebem False e a acurácia é 0.0 (0/12).
    """
    case_key = str(record["case_id"])
    expected = ground_truth.get(case_key, {})
    response = record["response"]

    attr_results = {}
    for key in EXPECTED_KEYS:
        if response is not None and key in expected and key in response:
            attr_results[key] = (response[key] == expected[key])
        else:
            attr_results[key] = False

    correct = sum(1 for v in attr_results.values() if v)
    accuracy = correct / len(EXPECTED_KEYS)
    return accuracy, attr_results


def pct(value):
    return "{:.2f}%".format(value * 100.0)


def write_report(records, ground_truth, output_file: Path, scenario_name: str):
    """Gera o relatório de acurácia considerando TODOS os registros."""

    # Filtrar registros com case_id presente no gabarito (TODOS, não só válidos)
    all_records = [
        r for r in records
        if str(r["case_id"]) in ground_truth
    ]

    if not all_records:
        print(f"  Nenhum registro encontrado para calcular acurácia.")
        return

    # Contadores para o cabeçalho
    total_records = len(all_records)
    valid_records = sum(1 for r in all_records if r["valid"])
    invalid_records = total_records - valid_records
    parseable_records = sum(1 for r in all_records if r["response"] is not None)
    unparseable_records = total_records - parseable_records

    # Estruturas de agregação
    by_model_case = defaultdict(list)   # (model, case_id) -> list of (accuracy, attr_results, valid)
    by_model = defaultdict(list)        # model -> list of (accuracy, valid)
    by_attribute = defaultdict(list)    # attribute -> list of bool

    for rec in all_records:
        accuracy, attr_results = compute_accuracy(rec, ground_truth)
        key = (rec["model"], rec["case_id"])
        by_model_case[key].append((accuracy, attr_results, rec["valid"]))
        by_model[rec["model"]].append((accuracy, rec["valid"]))
        for attr, correct in attr_results.items():
            by_attribute[attr].append(correct)

    # Coletar modelos e cases na ordem original
    seen_models = []
    for rec in records:
        if rec["model"] not in seen_models:
            seen_models.append(rec["model"])

    case_ids = sorted({rec["case_id"] for rec in records})

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        f.write(f"Relatorio de Acuracia vs. Gabarito — {scenario_name}\n")
        f.write(f"Gabarito utilizado: {GROUND_TRUTH_FILE}\n")
        f.write(f"Fonte de dados: resultados_detalhados_fast_test.txt\n")
        f.write(f"Total de registros avaliados: {total_records}\n")
        f.write(f"  - Formato valido (sim): {valid_records}\n")
        f.write(f"  - Formato invalido (nao): {invalid_records}\n")
        f.write(f"  - JSON parseavel: {parseable_records}\n")
        f.write(f"  - JSON nao parseavel (contam como 0% de acuracia): {unparseable_records}\n")
        f.write("=" * 90 + "\n")
        f.write("NOTA: Este relatorio considera TODAS as execucoes no calculo da acuracia.\n")
        f.write("Execucoes com JSON nao parseavel recebem acuracia 0% (0/12 acertos).\n")
        f.write("=" * 90 + "\n")

        # 1) Acurácia por modelo e caso
        f.write("\n1) Acuracia por modelo e caso de teste\n")
        for model in seen_models:
            for case_id in case_ids:
                key = (model, case_id)
                if key not in by_model_case:
                    continue
                entries = by_model_case[key]
                accuracies = [e[0] for e in entries]
                valid_count = sum(1 for e in entries if e[2])
                invalid_count = len(entries) - valid_count
                fully_correct = sum(1 for a in accuracies if a == 1.0)

                f.write(f"\nModelo: {model} | Caso de teste: {case_id}\n")
                f.write(f"Total de execucoes: {len(entries)} (validas: {valid_count}, invalidas: {invalid_count})\n")
                f.write(f"Acuracia media: {pct(mean(accuracies))}\n")
                f.write(f"Acuracia minima: {pct(min(accuracies))}\n")
                f.write(f"Acuracia maxima: {pct(max(accuracies))}\n")
                f.write(f"Execucoes 100% corretas: {fully_correct}/{len(entries)}\n")

                # Acurácia por atributo neste (model, case)
                attr_correct = defaultdict(int)
                for _, attr_results, _ in entries:
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

        # 2) Acurácia consolidada por modelo
        f.write("\n2) Acuracia consolidada por modelo\n")
        model_ranking = []
        for model in seen_models:
            if model not in by_model:
                continue
            entries = by_model[model]
            accuracies = [e[0] for e in entries]
            valid_count = sum(1 for e in entries if e[1])
            invalid_count = len(entries) - valid_count
            avg = mean(accuracies)
            fully = sum(1 for a in accuracies if a == 1.0)
            model_ranking.append((model, avg, fully, len(entries)))

            f.write(f"\nModelo: {model}\n")
            f.write(f"Total de execucoes avaliadas: {len(entries)} (validas: {valid_count}, invalidas: {invalid_count})\n")
            f.write(f"Acuracia media: {pct(avg)}\n")
            f.write(f"Acuracia minima: {pct(min(accuracies))}\n")
            f.write(f"Acuracia maxima: {pct(max(accuracies))}\n")
            f.write(f"Execucoes 100% corretas: {fully}/{len(entries)}\n")

        # 3) Acurácia por atributo (global)
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

        # 4) Ranking por acurácia média
        f.write("\n4) Ranking dos modelos por acuracia media\n")
        f.write("Criterio: maior acuracia media, depois maior proporcao de execucoes 100% corretas\n")
        model_ranking.sort(key=lambda x: (-x[1], -x[2]))
        for i, (model, avg, fully, total_n) in enumerate(model_ranking, start=1):
            f.write("{}. {} | acuracia media={} | 100% corretas={}/{}\n".format(
                i, model, pct(avg), fully, total_n
            ))

    print(f"  Relatorio salvo: {output_file}")


def main():
    if not GROUND_TRUTH_FILE.exists():
        print(f"Gabarito nao encontrado: {GROUND_TRUTH_FILE}")
        return

    print(f"Carregando gabarito: {GROUND_TRUTH_FILE}")
    ground_truth = json.loads(GROUND_TRUTH_FILE.read_text(encoding="utf-8"))
    print(f"Gabarito carregado com {len(ground_truth)} caso(s) de teste.\n")

    for scenario in SCENARIOS:
        scenario_path = scenario["path"]
        scenario_name = scenario["name"]
        detailed_file = scenario_path / scenario["detailed_file"]
        output_file = scenario_path / scenario["output_file"]

        print(f"{'='*80}")
        print(f"Processando: {scenario_name}")
        print(f"  Pasta: {scenario_path}")

        if not detailed_file.exists():
            print(f"  AVISO: Arquivo nao encontrado: {detailed_file}")
            print(f"  Pulando este cenario.\n")
            continue

        records = parse_records(detailed_file)
        total = len(records)
        valid = sum(1 for r in records if r["valid"])
        parseable = sum(1 for r in records if r["response"] is not None)
        print(f"  Registros: {total} total | {valid} validos | {total - valid} invalidos | {parseable} parseaveis")

        write_report(records, ground_truth, output_file, scenario_name)
        print()

    print("Recalculo concluido para todos os cenarios.")


if __name__ == "__main__":
    main()
