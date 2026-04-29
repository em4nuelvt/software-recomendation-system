import json
import re
from collections import Counter, defaultdict
from pathlib import Path

 
# Esse arquivo gera um gabarito de classificação "ideal" de atributos através da contagem das respostas
# mais recorrentes de cada entrada classificada pelos modelos executados. 

DETAILED_FILE = Path(__file__).resolve().parent / "benchmark_output" / "resultados_detalhados.txt"
OUTPUT_DIR = Path(__file__).resolve().parent / "results_templates"

MAJORITY_VOTE_FILE = OUTPUT_DIR / "ground_truth_majority_vote.json"
DISTRIBUTION_FILE = OUTPUT_DIR / "ground_truth_vote_distribution.txt"

EXPECTED_KEYS = [
    "tipo_projeto",
    "dominio_negocio",
    "persistencia",
    "escala",
    "integracao",
    "arquitetura_esperada",
    "experiencia_usuario",
    "requisitos_seguranca",
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


def compute_majority_vote(records):
    # Para cada (case_id, atributo): contar frequencia de cada valor
    # somando todos os modelos, somente execucoes validas.
    vote_counts = defaultdict(lambda: defaultdict(Counter))

    for rec in records:
        if not rec["valid"] or rec["response"] is None:
            continue
        case_id = rec["case_id"]
        for key in EXPECTED_KEYS:
            value = rec["response"].get(key)
            if value:
                vote_counts[case_id][key][value] += 1

    majority_vote = {}
    for case_id in sorted(vote_counts.keys()):
        majority_vote[str(case_id)] = {}
        for key in EXPECTED_KEYS:
            counter = vote_counts[case_id][key]
            if counter:
                majority_vote[str(case_id)][key] = counter.most_common(1)[0][0]
            else:
                majority_vote[str(case_id)][key] = ""

    return majority_vote, vote_counts


def write_distribution(vote_counts, filepath: Path):
    with filepath.open("w", encoding="utf-8") as f:
        f.write("Distribuicao de votos por caso de teste e atributo\n")
        f.write("(base: todas as execucoes validas dos 3 modelos somadas)\n")
        f.write("=" * 90 + "\n")

        for case_id in sorted(vote_counts.keys()):
            f.write(f"\nCaso de teste: {case_id}\n")
            f.write("-" * 60 + "\n")
            for key in EXPECTED_KEYS:
                counter = vote_counts[case_id][key]
                total = sum(counter.values())
                top_count = counter.most_common(1)[0][1] if counter else 0
                f.write(f"  {key}:\n")
                for value, count in counter.most_common():
                    pct = (count / total * 100) if total > 0 else 0.0
                    marker = " <-- VENCEDOR" if count == top_count else ""
                    f.write(f"    {value}: {count}/{total} ({pct:.1f}%){marker}\n")


def main():
    if not DETAILED_FILE.exists():
        print(f"Arquivo nao encontrado: {DETAILED_FILE}")
        return

    print(f"Lendo: {DETAILED_FILE}")
    records = parse_records(DETAILED_FILE)
    total = len(records)
    valid = sum(1 for r in records if r["valid"])
    print(f"Registros lidos: {total} | Validos: {valid} | Invalidos: {total - valid}")

    majority_vote, vote_counts = compute_majority_vote(records)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    MAJORITY_VOTE_FILE.write_text(
        json.dumps(majority_vote, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )
    print(f"\nGabarito salvo: {MAJORITY_VOTE_FILE}")

    write_distribution(vote_counts, DISTRIBUTION_FILE)
    print(f"Distribuicao salva: {DISTRIBUTION_FILE}")

    print("\n--- Proximo passo ---")
    print("Revise o gabarito gerado e crie ground_truth.json com o gabarito final.")
    print("Voce pode copiar ground_truth_majority_vote.json como ponto de partida:")
    print(f"  copy \"{MAJORITY_VOTE_FILE}\" \"{OUTPUT_DIR / 'ground_truth.json'}\"")
    print("Depois execute accuracy_report.py para calcular a acuracia dos modelos.")


if __name__ == "__main__":
    main()
