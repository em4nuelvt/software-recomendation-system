"""
plot_results.py - Geração de gráficos para os resultados do benchmark.
Lê os arquivos de saída do benchmark e gera 11 figuras PNG em benchmark_output/graficos/.
"""

import os
import re
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from collections import defaultdict

matplotlib.use("Agg")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "benchmark_output")
GRAFICOS_DIR = os.path.join(OUTPUT_DIR, "graficos")
os.makedirs(GRAFICOS_DIR, exist_ok=True)

RESUMO_PATH = os.path.join(OUTPUT_DIR, "resumo_metricas.txt")
ACCURACY_PATH = os.path.join(OUTPUT_DIR, "accuracy_report.txt")
DETALHADOS_PATH = os.path.join(OUTPUT_DIR, "resultados_detalhados.txt")

CORES_MODELOS = {"qwen2.5": "#4C72B0", "llama3": "#DD8452", "deepseek-r1:8b": "#55A868"}
MODELOS_ORDEM = ["qwen2.5", "llama3", "deepseek-r1:8b"]
CASOS = ["1", "2", "3", "4", "5"]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#F8F9FA",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
})


def parse_resumo():
    por_caso = defaultdict(dict)
    consolidado = {}
    with open(RESUMO_PATH, encoding="utf-8") as f:
        texto = f.read()

    blocos = re.split(r"Modelo:\s+", texto)
    for bloco in blocos[1:]:
        m = re.match(r"(.+?)\s*\|\s*Caso de teste:\s*(\d+)", bloco)
        if m:
            modelo, caso = m.group(1).strip(), m.group(2).strip()
            d = {}
            for chave, regex in [
                ("tempo_medio", r"Tempo medio \(ms\):\s*([\d.]+)"),
                ("tempo_mediano", r"Tempo mediano \(ms\):\s*([\d.]+)"),
                ("tempo_p95", r"Tempo p95 \(ms\):\s*([\d.]+)"),
                ("tempo_min", r"Tempo minimo \(ms\):\s*([\d.]+)"),
                ("tempo_max", r"Tempo maximo \(ms\):\s*([\d.]+)"),
                ("taxa_formato", r"Taxa de formato valido:\s*([\d.]+)%"),
                ("taxa_sucesso", r"Taxa de sucesso:\s*([\d.]+)%"),
                ("consistencia_total", r"Consistencia total:\s*([\d.]+)%"),
                ("consistencia_validos", r"Consistencia somente validos:\s*([\d.]+)%"),
                ("saidas_distintas", r"Saidas validas distintas:\s*(\d+)"),
            ]:
                found = re.search(regex, bloco)
                d[chave] = float(found.group(1)) if found else 0.0
            por_caso[modelo][caso] = d
            continue

        m2 = re.match(r"(.+?)[\r\n]", bloco)
        if m2:
            modelo = m2.group(1).strip()
            if modelo in MODELOS_ORDEM:
                d = {}
                for chave, regex in [
                    ("tempo_medio", r"Tempo medio \(ms\):\s*([\d.]+)"),
                    ("tempo_mediano", r"Tempo mediano \(ms\):\s*([\d.]+)"),
                    ("taxa_sucesso", r"Taxa de sucesso:\s*([\d.]+)%"),
                    ("consistencia_validos", r"Consistencia somente validos:\s*([\d.]+)%"),
                    ("total_exec", r"Total de execucoes:\s*(\d+)"),
                ]:
                    found = re.search(regex, bloco)
                    d[chave] = float(found.group(1)) if found else 0.0
                consolidado[modelo] = d

    return por_caso, consolidado


def parse_accuracy():
    por_caso = defaultdict(dict)
    consolidado = {}
    por_atributo_geral = {}
    atrib_mc = defaultdict(lambda: defaultdict(dict))

    with open(ACCURACY_PATH, encoding="utf-8") as f:
        texto = f.read()

    secao1 = texto.split("2) Acuracia consolidada por modelo")[0]
    blocos = re.split(r"Modelo:\s+", secao1)
    for bloco in blocos[1:]:
        m = re.match(r"(.+?)\s*\|\s*Caso de teste:\s*(\d+)", bloco)
        if not m:
            continue
        modelo, caso = m.group(1).strip(), m.group(2).strip()
        ac_media = float(re.search(r"Acuracia media:\s*([\d.]+)%", bloco).group(1))
        ac_min = float(re.search(r"Acuracia minima:\s*([\d.]+)%", bloco).group(1))
        ac_max = float(re.search(r"Acuracia maxima:\s*([\d.]+)%", bloco).group(1))
        por_caso[modelo][caso] = {"acuracia_media": ac_media, "acuracia_min": ac_min, "acuracia_max": ac_max}

        for am in re.finditer(r"  (\w+):\s*\d+/\d+\s*\(([\d.]+)%\)", bloco):
            atrib_mc[modelo][caso][am.group(1)] = float(am.group(2))

    secao2_3 = texto.split("2) Acuracia consolidada por modelo")[1]
    secao2 = secao2_3.split("3) Acuracia por atributo")[0]
    for bm in re.finditer(r"Modelo:\s+(.+?)\n.*?Acuracia media:\s*([\d.]+)%.*?Execucoes 100% corretas:\s*(\d+)/(\d+)", secao2, re.DOTALL):
        modelo = bm.group(1).strip()
        consolidado[modelo] = {
            "acuracia_media": float(bm.group(2)),
            "exec_100pct": int(bm.group(3)),
            "total_exec": int(bm.group(4)),
        }

    secao3 = secao2_3.split("3) Acuracia por atributo")[1].split("4) Ranking")[0]
    for am in re.finditer(r"(\w+):\s*\d+/\d+\s*\(([\d.]+)%\)", secao3):
        por_atributo_geral[am.group(1)] = float(am.group(2))

    return por_caso, por_atributo_geral, consolidado, atrib_mc


def parse_tempos_detalhados():
    tempos = defaultdict(lambda: defaultdict(list))
    with open(DETALHADOS_PATH, encoding="utf-8") as f:
        modelo_atual = caso_atual = None
        for linha in f:
            linha = linha.strip()
            if linha.startswith("Modelo:"):
                modelo_atual = linha.split(":", 1)[1].strip()
            elif linha.startswith("Caso de teste:"):
                caso_atual = linha.split(":", 1)[1].strip()
            elif linha.startswith("Tempo_ms:"):
                t = float(linha.split(":", 1)[1].strip())
                tempos[modelo_atual][caso_atual].append(t)
    return tempos


def salvar(fig, nome):
    path = os.path.join(GRAFICOS_DIR, nome)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: {path}")


def fig01_tempo_medio_por_caso(resumo_caso):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(CASOS))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [resumo_caso[modelo][c]["tempo_medio"] / 1000 for c in CASOS]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Tempo Médio (s)")
    ax.set_title("Tempo Médio de Resposta por Caso de Teste e Modelo")
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in CASOS])
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, "fig01_tempo_medio_por_caso.png")


def fig02_boxplot_tempo(tempos):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    data = []
    labels = []
    colors = []
    for modelo in MODELOS_ORDEM:
        todos = []
        for c in CASOS:
            todos.extend(tempos[modelo][c])
        data.append([t / 1000 for t in todos])
        labels.append(modelo)
        colors.append(CORES_MODELOS[modelo])

    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.5,
                    medianprops=dict(color="black", linewidth=1.5))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    ax.set_ylabel("Tempo de Resposta (s)")
    ax.set_title("Distribuição do Tempo de Resposta por Modelo")
    salvar(fig, "fig02_boxplot_tempo.png")


def fig03_taxa_sucesso(resumo_consolidado):
    fig, ax = plt.subplots(figsize=(7, 5))
    modelos = MODELOS_ORDEM
    sucesso = [resumo_consolidado[m]["taxa_sucesso"] for m in modelos]
    falha = [100 - s for s in sucesso]
    x = np.arange(len(modelos))
    bars_s = ax.bar(x, sucesso, 0.5, color=[CORES_MODELOS[m] for m in modelos], edgecolor="white")
    bars_f = ax.bar(x, falha, 0.5, bottom=sucesso, color="#E07B73", edgecolor="white", alpha=0.85)
    for bar, val in zip(bars_s, sucesso):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2,
                f"{val:.1f}%", ha="center", va="center", fontweight="bold", color="white", fontsize=11)
    for bar, val, bot in zip(bars_f, falha, sucesso):
        if val > 2:
            ax.text(bar.get_x() + bar.get_width() / 2, bot + val / 2,
                    f"{val:.1f}%", ha="center", va="center", fontweight="bold", color="white", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(modelos)
    ax.set_ylabel("Porcentagem (%)")
    ax.set_title("Taxa de Sucesso vs. Falha por Modelo")
    ax.set_ylim(0, 105)
    legend_handles = [matplotlib.patches.Patch(facecolor=CORES_MODELOS[m], label=m) for m in modelos]
    legend_handles.append(matplotlib.patches.Patch(facecolor="#E07B73", alpha=0.85, label="Falha (%)"))
    ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, "fig03_taxa_sucesso.png")


def fig04_acuracia_por_modelo(acc_consolidado):
    fig, ax = plt.subplots(figsize=(7, 5))
    modelos = MODELOS_ORDEM
    vals = [acc_consolidado[m]["acuracia_media"] for m in modelos]
    bars = ax.bar(modelos, vals, 0.5, color=[CORES_MODELOS[m] for m in modelos], edgecolor="white")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{val:.2f}%", ha="center", va="bottom", fontweight="bold")
    ax.set_ylabel("Acurácia Média (%)")
    ax.set_title("Acurácia Média Consolidada por Modelo")
    ax.set_ylim(0, max(vals) + 10)
    salvar(fig, "fig04_acuracia_por_modelo.png")


def fig05_acuracia_por_caso(acc_caso):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(CASOS))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [acc_caso[modelo][c]["acuracia_media"] for c in CASOS]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Acurácia Média (%)")
    ax.set_title("Acurácia Média por Caso de Teste e Modelo")
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in CASOS])
    ax.set_ylim(0, 100)
    ax.legend()
    salvar(fig, "fig05_acuracia_por_caso.png")


def fig06_acuracia_por_atributo(atrib_geral):
    atribs_sorted = sorted(atrib_geral.items(), key=lambda x: x[1])
    nomes = [a[0].replace("_", " ").title() for a in atribs_sorted]
    vals = [a[1] for a in atribs_sorted]
    colors = ["#E07B73" if v < 60 else "#F0C05A" if v < 80 else "#55A868" for v in vals]

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(nomes, vals, color=colors, edgecolor="white", height=0.65)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}%", ha="left", va="center", fontsize=9)
    ax.set_xlabel("Acurácia (%)")
    ax.set_title("Acurácia por Atributo (Todos os Modelos)")
    ax.set_xlim(0, 110)
    legend_handles = [
        matplotlib.patches.Patch(facecolor="#55A868", label="\u2265 80%"),
        matplotlib.patches.Patch(facecolor="#F0C05A", label="60 \u2013 79%"),
        matplotlib.patches.Patch(facecolor="#E07B73", label="< 60%"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", title="Acurácia")
    salvar(fig, "fig06_acuracia_por_atributo.png")


def fig07_heatmap_atributo_modelo(atrib_mc):
    all_atribs = set()
    for modelo in MODELOS_ORDEM:
        for caso in CASOS:
            if caso in atrib_mc[modelo]:
                all_atribs.update(atrib_mc[modelo][caso].keys())

    atribs_list = sorted(all_atribs)
    matrix = np.zeros((len(atribs_list), len(MODELOS_ORDEM)))

    for j, modelo in enumerate(MODELOS_ORDEM):
        for i, atrib in enumerate(atribs_list):
            vals_casos = []
            for caso in CASOS:
                if caso in atrib_mc[modelo]:
                    if atrib in atrib_mc[modelo][caso]:
                        vals_casos.append(atrib_mc[modelo][caso][atrib])
                    else:
                        vals_casos.append(100.0)
                else:
                    vals_casos.append(100.0)
            matrix[i, j] = np.mean(vals_casos)

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(len(MODELOS_ORDEM)))
    ax.set_xticklabels(MODELOS_ORDEM, fontsize=10)
    ax.set_yticks(range(len(atribs_list)))
    ax.set_yticklabels([a.replace("_", " ").title() for a in atribs_list], fontsize=9)
    for i in range(len(atribs_list)):
        for j in range(len(MODELOS_ORDEM)):
            color = "white" if matrix[i, j] < 40 else "black"
            ax.text(j, i, f"{matrix[i, j]:.0f}%", ha="center", va="center", fontsize=9, color=color)
    ax.set_title("Heatmap: Acurácia Média por Atributo e Modelo")
    fig.colorbar(im, ax=ax, label="Acurácia (%)", shrink=0.8)
    salvar(fig, "fig07_heatmap_atributo_modelo.png")


def fig08_consistencia_por_caso(resumo_caso):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(CASOS))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [resumo_caso[modelo][c]["consistencia_validos"] for c in CASOS]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                    f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Consistência (%)")
    ax.set_title("Consistência (Somente Válidos) por Caso de Teste e Modelo")
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in CASOS])
    ax.set_ylim(0, max(75, max(resumo_caso[m][c]["consistencia_validos"] for m in MODELOS_ORDEM for c in CASOS) + 10))
    ax.legend()
    salvar(fig, "fig08_consistencia_por_caso.png")


def fig09_consistencia_por_modelo(resumo_consolidado):
    fig, ax = plt.subplots(figsize=(7, 5))
    modelos = MODELOS_ORDEM
    vals = [resumo_consolidado[m]["consistencia_validos"] for m in modelos]
    bars = ax.bar(modelos, vals, 0.5, color=[CORES_MODELOS[m] for m in modelos], edgecolor="white")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{val:.2f}%", ha="center", va="bottom", fontweight="bold")
    ax.set_ylabel("Consistência (%)")
    ax.set_title("Consistência Consolidada por Modelo (Somente Válidos)")
    ax.set_ylim(0, max(vals) + 10)
    salvar(fig, "fig09_consistencia_por_modelo.png")


def fig10_radar(acc_consolidado, resumo_consolidado):
    categorias = ["Acurácia", "Consistência", "Taxa Sucesso", "Velocidade"]
    N = len(categorias)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))

    tempos = {m: resumo_consolidado[m]["tempo_medio"] for m in MODELOS_ORDEM}
    t_min = min(tempos.values())

    for modelo in MODELOS_ORDEM:
        valores = [
            acc_consolidado[modelo]["acuracia_media"],
            resumo_consolidado[modelo]["consistencia_validos"],
            resumo_consolidado[modelo]["taxa_sucesso"],
            (t_min / tempos[modelo]) * 100 if tempos[modelo] > 0 else 0,
        ]
        valores += valores[:1]
        ax.plot(angles, valores, "o-", linewidth=2, label=modelo, color=CORES_MODELOS[modelo])
        ax.fill(angles, valores, alpha=0.15, color=CORES_MODELOS[modelo])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, fontsize=11)
    ax.set_ylim(0, 105)
    ax.set_title("Comparação Multidimensional dos Modelos", y=1.08)
    ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1))
    salvar(fig, "fig10_radar_comparativo.png")


def fig11_saidas_distintas(resumo_caso):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(CASOS))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [resumo_caso[modelo][c]["saidas_distintas"] for c in CASOS]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                    f"{int(bar.get_height())}", ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Nº de Saídas Distintas")
    ax.set_title("Quantidade de Saídas Válidas Distintas por Caso de Teste e Modelo")
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in CASOS])
    ax.legend()
    salvar(fig, "fig11_saidas_distintas.png")


def main():
    print("Parsing dados...")
    resumo_caso, resumo_consolidado = parse_resumo()
    acc_caso, atrib_geral, acc_consolidado, atrib_mc = parse_accuracy()
    tempos = parse_tempos_detalhados()

    print(f"\nGerando 11 gráficos em: {GRAFICOS_DIR}\n")

    fig01_tempo_medio_por_caso(resumo_caso)
    fig02_boxplot_tempo(tempos)
    fig03_taxa_sucesso(resumo_consolidado)
    fig04_acuracia_por_modelo(acc_consolidado)
    fig05_acuracia_por_caso(acc_caso)
    fig06_acuracia_por_atributo(atrib_geral)
    fig07_heatmap_atributo_modelo(atrib_mc)
    fig08_consistencia_por_caso(resumo_caso)
    fig09_consistencia_por_modelo(resumo_consolidado)
    fig10_radar(acc_consolidado, resumo_consolidado)
    fig11_saidas_distintas(resumo_caso)

    print(f"\nConcluído! {len(os.listdir(GRAFICOS_DIR))} gráficos salvos em {GRAFICOS_DIR}")


if __name__ == "__main__":
    main()
