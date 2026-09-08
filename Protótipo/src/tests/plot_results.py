import os
import re
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from collections import defaultdict

matplotlib.use("Agg")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(SCRIPT_DIR, "benchmark_output", "test_backup")
BASE_OUT_DIR = os.path.join(SCRIPT_DIR, "benchmark_output", "graficos")

CORES_MODELOS = {"qwen2.5": "#4C72B0", "llama3": "#DD8452", "deepseek-r1:8b": "#55A868"}
MODELOS_ORDEM = ["qwen2.5", "llama3", "deepseek-r1:8b"]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#F8F9FA",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
})

SCENARIOS = [
    {
        "folder_name": "1 - Prompt antigo + temperatura padrao",
        "subtitle": "Prompt antigo + Temperatura padrão",
        "path": os.path.join(BACKUP_DIR, "standardtemperature", "prompt antigo"),
    },
    {
        "folder_name": "2 - Prompt antigo + temperatura 0",
        "subtitle": "Prompt antigo + Temperatura 0",
        "path": os.path.join(BACKUP_DIR, "temperature0", "prompt antigo"),
    },
    {
        "folder_name": "3 - Prompt novo + temperatura padrao",
        "subtitle": "Prompt novo + Temperatura padrão",
        "path": os.path.join(BACKUP_DIR, "standardtemperature", "prompt novo"),
    },
    {
        "folder_name": "4 - Prompt novo + temperatura 0",
        "subtitle": "Prompt novo + Temperatura 0",
        "path": os.path.join(BACKUP_DIR, "temperature0", "prompt novo"),
    },
    {
        "folder_name": "5 - Teste de estresse prompt antigo + temperatura padrao",
        "subtitle": "Teste de estresse (Caso 6) | Prompt antigo + Temp padrão",
        "path": os.path.join(BACKUP_DIR, "largeInputTest", "prompt antigo", "standardtemperature"),
    },
    {
        "folder_name": "6 - Teste de estresse prompt antigo + temperatura 0",
        "subtitle": "Teste de estresse (Caso 6) | Prompt antigo + Temp 0",
        "path": os.path.join(BACKUP_DIR, "largeInputTest", "prompt antigo", "temperature0"),
    },
    {
        "folder_name": "7 - Teste de estresse prompt novo + temperatura padrao",
        "subtitle": "Teste de estresse (Caso 6) | Prompt novo + Temp padrão",
        "path": os.path.join(BACKUP_DIR, "largeInputTest", "prompt novo", "standardtemperature"),
    },
    {
        "folder_name": "8 - Teste de estresse prompt novo + temperatura 0",
        "subtitle": "Teste de estresse (Caso 6) | Prompt novo + Temp 0",
        "path": os.path.join(BACKUP_DIR, "largeInputTest", "prompt novo", "temperature0"),
    }
]

def get_files(path):
    files = os.listdir(path)
    resumo = next(f for f in files if f.startswith("resumo_metricas"))
    acc = next(f for f in files if f.startswith("accuracy_report"))
    det = next(f for f in files if f.startswith("resultados_detalhados"))
    return os.path.join(path, resumo), os.path.join(path, acc), os.path.join(path, det)

def parse_resumo(path):
    por_caso = defaultdict(dict)
    consolidado = {}
    with open(path, encoding="utf-8") as f:
        texto = f.read()

    blocos = re.split(r"Modelo:\s+", texto)
    for bloco in blocos[1:]:
        m = re.match(r"(.+?)\s*\|\s*Caso de teste:\s*(\d+)", bloco)
        if m:
            modelo, caso = m.group(1).strip(), m.group(2).strip()
            d = {}
            for chave, regex in [
                ("tempo_medio", r"Tempo medio \(ms\):\s*([\d.]+)"),
                ("taxa_sucesso", r"Taxa de sucesso:\s*([\d.]+)%"),
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
                    ("taxa_sucesso", r"Taxa de sucesso:\s*([\d.]+)%"),
                    ("consistencia_validos", r"Consistencia somente validos:\s*([\d.]+)%"),
                    ("saidas_distintas", r"Saidas validas distintas:\s*(\d+)"),
                ]:
                    found = re.search(regex, bloco)
                    d[chave] = float(found.group(1)) if found else 0.0
                consolidado[modelo] = d
                
    # Para os testes de estresse, não há quebra por caso no arquivo de resumo, só o consolidado.
    # Vamos replicar o consolidado para o caso "6" para os gráficos não quebrarem.
    if not por_caso:
        for modelo, dados in consolidado.items():
            por_caso[modelo]["6"] = dict(dados)

    return por_caso, consolidado


def parse_accuracy(path):
    por_caso = defaultdict(dict)
    consolidado = {}
    por_atributo_geral = {}
    atrib_mc = defaultdict(lambda: defaultdict(dict))

    with open(path, encoding="utf-8") as f:
        texto = f.read()

    secao1 = texto.split("2) Acuracia consolidada por modelo")[0]
    blocos = re.split(r"Modelo:\s+", secao1)
    for bloco in blocos[1:]:
        m = re.match(r"(.+?)\s*\|\s*Caso de teste:\s*(\d+)", bloco)
        if not m:
            continue
        modelo, caso = m.group(1).strip(), m.group(2).strip()
        ac_media = float(re.search(r"Acuracia media:\s*([\d.]+)%", bloco).group(1))
        por_caso[modelo][caso] = {"acuracia_media": ac_media}

        for am in re.finditer(r"  (\w+):\s*\d+/\d+\s*\(([\d.]+)%\)", bloco):
            atrib_mc[modelo][caso][am.group(1)] = float(am.group(2))

    secao2_3 = texto.split("2) Acuracia consolidada por modelo")[1]
    secao2 = secao2_3.split("3) Acuracia por atributo")[0]
    for bm in re.finditer(r"Modelo:\s+(.+?)\n.*?Acuracia media:\s*([\d.]+)%", secao2, re.DOTALL):
        modelo = bm.group(1).strip()
        consolidado[modelo] = {"acuracia_media": float(bm.group(2))}

    secao3 = secao2_3.split("3) Acuracia por atributo")[1].split("4) Ranking")[0]
    for am in re.finditer(r"(\w+):\s*\d+/\d+\s*\(([\d.]+)%\)", secao3):
        por_atributo_geral[am.group(1)] = float(am.group(2))

    return por_caso, por_atributo_geral, consolidado, atrib_mc


def parse_tempos_detalhados(path):
    tempos = defaultdict(lambda: defaultdict(list))
    with open(path, encoding="utf-8") as f:
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


def configure_titles(fig, ax, main_title, subtitle):
    # Usar pad no título principal garante o espaço, e centraliza nos eixos (não na figura inteira)
    ax.set_title(main_title, fontsize=14, fontweight="bold", pad=28)
    
    # O subtítulo entra no espaço criado pelo pad, também centralizado exato no eixo
    # Cor #222222 é um cinza muito escuro/chumbo
    ax.annotate(subtitle, xy=(0.5, 1), xytext=(0, 10),
                xycoords="axes fraction", textcoords="offset points",
                ha="center", va="bottom", fontsize=11, color="#222222")


def salvar(fig, out_dir, nome):
    path = os.path.join(out_dir, nome)
    fig.tight_layout()
    fig.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def fig01_tempo_medio_por_caso(resumo_caso, casos, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(casos))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [resumo_caso[modelo][c].get("tempo_medio", 0) / 1000 for c in casos]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2, f"{h:.1f}", ha="center", va="bottom", fontsize=8)
    
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Tempo Médio (s)")
    configure_titles(fig, ax, "Tempo Médio de Resposta por Caso de Teste e Modelo", subtitle)
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in casos])
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, out_dir, "fig01_tempo_medio_por_caso.png")


def fig02_boxplot_tempo(tempos, casos, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(8, 5.5))
    data, labels, colors = [], [], []
    for modelo in MODELOS_ORDEM:
        todos = []
        for c in casos:
            todos.extend(tempos[modelo][c])
        if todos:
            data.append([t / 1000 for t in todos])
            labels.append(modelo)
            colors.append(CORES_MODELOS[modelo])

    if not data:
        plt.close(fig)
        return

    bp = ax.boxplot(data, tick_labels=labels, patch_artist=True, widths=0.5, medianprops=dict(color="black", linewidth=1.5))
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.75)
    
    ax.set_ylabel("Tempo de Resposta (s)")
    configure_titles(fig, ax, "Distribuição do Tempo de Resposta por Modelo", subtitle)
    salvar(fig, out_dir, "fig02_boxplot_tempo.png")


def fig03_taxa_sucesso(resumo_consolidado, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    modelos = MODELOS_ORDEM
    sucesso = [resumo_consolidado[m].get("taxa_sucesso", 0) for m in modelos]
    falha = [100 - s for s in sucesso]
    x = np.arange(len(modelos))
    
    bars_s = ax.bar(x, sucesso, 0.5, color=[CORES_MODELOS[m] for m in modelos], edgecolor="white")
    bars_f = ax.bar(x, falha, 0.5, bottom=sucesso, color="#E07B73", edgecolor="white", alpha=0.85)
    
    for bar, val in zip(bars_s, sucesso):
        if val > 5:
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() / 2, f"{val:.1f}%", ha="center", va="center", fontweight="bold", color="white", fontsize=11)
    for bar, val, bot in zip(bars_f, falha, sucesso):
        if val > 5:
            ax.text(bar.get_x() + bar.get_width() / 2, bot + val / 2, f"{val:.1f}%", ha="center", va="center", fontweight="bold", color="white", fontsize=10)
    
    ax.set_xticks(x)
    ax.set_xticklabels(modelos)
    ax.set_ylabel("Porcentagem (%)")
    configure_titles(fig, ax, "Taxa de Sucesso (Formato Válido) por Modelo", subtitle)
    ax.set_ylim(0, 105)
    
    legend_handles = [matplotlib.patches.Patch(facecolor=CORES_MODELOS[m], label=m) for m in modelos]
    legend_handles.append(matplotlib.patches.Patch(facecolor="#E07B73", alpha=0.85, label="Falha (%)"))
    ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, out_dir, "fig03_taxa_sucesso.png")


def fig04_acuracia_por_modelo(acc_consolidado, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    modelos = MODELOS_ORDEM
    vals = [acc_consolidado[m].get("acuracia_media", 0) for m in modelos]
    
    bars = ax.bar(modelos, vals, 0.5, color=[CORES_MODELOS[m] for m in modelos], edgecolor="white")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val:.2f}%", ha="center", va="bottom", fontweight="bold")
    
    ax.set_ylabel("Acurácia Média (%)")
    configure_titles(fig, ax, "Acurácia Média Consolidada por Modelo", subtitle)
    ax.set_ylim(0, max(max(vals) + 15, 100))
    salvar(fig, out_dir, "fig04_acuracia_por_modelo.png")


def fig05_acuracia_por_caso(acc_caso, casos, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(casos))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [acc_caso[modelo][c].get("acuracia_media", 0) for c in casos]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5, f"{h:.1f}", ha="center", va="bottom", fontsize=8)
    
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Acurácia Média (%)")
    configure_titles(fig, ax, "Acurácia Média por Caso de Teste e Modelo", subtitle)
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in casos])
    ax.set_ylim(0, 105)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, out_dir, "fig05_acuracia_por_caso.png")


def fig06_acuracia_por_atributo(atrib_geral, out_dir, subtitle):
    if not atrib_geral:
        return
    atribs_sorted = sorted(atrib_geral.items(), key=lambda x: x[1])
    nomes = [a[0].replace("_", " ").title() for a in atribs_sorted]
    vals = [a[1] for a in atribs_sorted]
    colors = ["#E07B73" if v < 60 else "#F0C05A" if v < 80 else "#55A868" for v in vals]

    fig, ax = plt.subplots(figsize=(9, 6.5))
    bars = ax.barh(nomes, vals, color=colors, edgecolor="white", height=0.65)
    for bar, val in zip(bars, vals):
        ax.text(bar.get_width() + 0.8, bar.get_y() + bar.get_height() / 2, f"{val:.1f}%", ha="left", va="center", fontsize=9)
    
    ax.set_xlabel("Acurácia (%)")
    configure_titles(fig, ax, "Acurácia por Atributo (Todos os Modelos)", subtitle)
    ax.set_xlim(0, 110)
    
    legend_handles = [
        matplotlib.patches.Patch(facecolor="#55A868", label="\u2265 80%"),
        matplotlib.patches.Patch(facecolor="#F0C05A", label="60 \u2013 79%"),
        matplotlib.patches.Patch(facecolor="#E07B73", label="< 60%"),
    ]
    ax.legend(handles=legend_handles, loc="lower right", title="Acurácia")
    salvar(fig, out_dir, "fig06_acuracia_por_atributo.png")


def fig07_heatmap_atributo_modelo(atrib_mc, casos, out_dir, subtitle):
    all_atribs = set()
    for modelo in MODELOS_ORDEM:
        for caso in casos:
            if caso in atrib_mc[modelo]:
                all_atribs.update(atrib_mc[modelo][caso].keys())

    if not all_atribs:
        return

    atribs_list = sorted(all_atribs)
    matrix = np.zeros((len(atribs_list), len(MODELOS_ORDEM)))

    for j, modelo in enumerate(MODELOS_ORDEM):
        for i, atrib in enumerate(atribs_list):
            vals_casos = []
            for caso in casos:
                if caso in atrib_mc.get(modelo, {}) and atrib in atrib_mc[modelo][caso]:
                    vals_casos.append(atrib_mc[modelo][caso][atrib])
                else:
                    vals_casos.append(0.0) # Se nulo, 0.
            matrix[i, j] = np.mean(vals_casos) if vals_casos else 0.0

    fig, ax = plt.subplots(figsize=(8, 8))
    im = ax.imshow(matrix, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    
    ax.set_xticks(range(len(MODELOS_ORDEM)))
    ax.set_xticklabels(MODELOS_ORDEM, fontsize=10)
    ax.set_yticks(range(len(atribs_list)))
    ax.set_yticklabels([a.replace("_", " ").title() for a in atribs_list], fontsize=9)
    
    for i in range(len(atribs_list)):
        for j in range(len(MODELOS_ORDEM)):
            color = "white" if matrix[i, j] < 40 or matrix[i,j] > 80 else "black"
            ax.text(j, i, f"{matrix[i, j]:.0f}%", ha="center", va="center", fontsize=9, color=color)
            
    configure_titles(fig, ax, "Heatmap: Acurácia Média por Atributo e Modelo", subtitle)
    fig.colorbar(im, ax=ax, label="Acurácia (%)", shrink=0.8)
    salvar(fig, out_dir, "fig07_heatmap_atributo_modelo.png")


def fig08_consistencia_por_caso(resumo_caso, casos, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(casos))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [resumo_caso[modelo][c].get("consistencia_validos", 0) for c in casos]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.5, f"{h:.1f}", ha="center", va="bottom", fontsize=8)
    
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Consistência (%)")
    configure_titles(fig, ax, "Consistência (Somente Válidos) por Caso de Teste e Modelo", subtitle)
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in casos])
    max_val = max((resumo_caso[m][c].get("consistencia_validos", 0) for m in MODELOS_ORDEM for c in casos), default=0)
    ax.set_ylim(0, max(75, max_val + 15))
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, out_dir, "fig08_consistencia_por_caso.png")


def fig09_consistencia_por_modelo(resumo_consolidado, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(7, 5.5))
    modelos = MODELOS_ORDEM
    vals = [resumo_consolidado[m].get("consistencia_validos", 0) for m in modelos]
    bars = ax.bar(modelos, vals, 0.5, color=[CORES_MODELOS[m] for m in modelos], edgecolor="white")
    for bar, val in zip(bars, vals):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, f"{val:.2f}%", ha="center", va="bottom", fontweight="bold")
    
    ax.set_ylabel("Consistência (%)")
    configure_titles(fig, ax, "Consistência Consolidada por Modelo (Somente Válidos)", subtitle)
    ax.set_ylim(0, max(max(vals) + 15, 100))
    salvar(fig, out_dir, "fig09_consistencia_por_modelo.png")


def fig10_radar(acc_consolidado, resumo_consolidado, out_dir, subtitle):
    categorias = ["Acurácia", "Consistência\n(Válidos)", "Taxa Sucesso", "Velocidade"]
    N = len(categorias)
    angles = [n / float(N) * 2 * math.pi for n in range(N)]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    tempos = {m: resumo_consolidado[m].get("tempo_medio", 0) for m in MODELOS_ORDEM}
    t_min = min((t for t in tempos.values() if t > 0), default=0)

    for modelo in MODELOS_ORDEM:
        vel = (t_min / tempos[modelo]) * 100 if tempos[modelo] > 0 else 0
        valores = [
            acc_consolidado[modelo].get("acuracia_media", 0),
            resumo_consolidado[modelo].get("consistencia_validos", 0),
            resumo_consolidado[modelo].get("taxa_sucesso", 0),
            vel,
        ]
        valores += valores[:1]
        ax.plot(angles, valores, "o-", linewidth=2, label=modelo, color=CORES_MODELOS[modelo])
        ax.fill(angles, valores, alpha=0.15, color=CORES_MODELOS[modelo])

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categorias, fontsize=11)
    for label, angle in zip(ax.get_xticklabels(), angles[:-1]):
        angle_deg = math.degrees(angle) % 360
        if angle_deg < 90 or angle_deg > 270:
            label.set_ha("left")
        elif 90 < angle_deg < 270:
            label.set_ha("right")
    ax.set_ylim(0, 105)
    
    configure_titles(fig, ax, "Comparação Multidimensional dos Modelos", subtitle)
    
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.1))
    salvar(fig, out_dir, "fig10_radar_comparativo.png")


def fig11_saidas_distintas(resumo_caso, casos, out_dir, subtitle):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(casos))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [resumo_caso[modelo][c].get("saidas_distintas", 0) for c in casos]
        bars = ax.bar(x + i * w, vals, w, label=modelo, color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax.text(bar.get_x() + bar.get_width() / 2, h + 0.2, f"{int(h)}", ha="center", va="bottom", fontsize=9)
    
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Nº de Saídas Distintas")
    configure_titles(fig, ax, "Quantidade de Saídas Válidas Distintas por Caso de Teste e Modelo", subtitle)
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in casos])
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, out_dir, "fig11_saidas_distintas.png")


def main():
    print("Iniciando geracao de graficos para todos os 8 cenarios...\n")
    
    for sc in SCENARIOS:
        print(f"Processando: {sc['folder_name']}")
        
        path = sc["path"]
        if not os.path.exists(path):
            print(f"  Diretorio nao encontrado: {path}")
            continue
            
        try:
            res_path, acc_path, det_path = get_files(path)
        except StopIteration:
            print(f"  Arquivos insuficientes em: {path}")
            continue

        out_dir = os.path.join(BASE_OUT_DIR, sc["folder_name"])
        os.makedirs(out_dir, exist_ok=True)
        subtitle = sc["subtitle"]

        resumo_caso, resumo_consolidado = parse_resumo(res_path)
        acc_caso, atrib_geral, acc_consolidado, atrib_mc = parse_accuracy(acc_path)
        tempos = parse_tempos_detalhados(det_path)

        # Descobrir casos automaticamente (1 a 5, ou só 6)
        casos_set = set()
        for m in MODELOS_ORDEM:
            casos_set.update(resumo_caso[m].keys())
        # Se não achou no resumo, pega do accuracy (acontece no teste de estresse)
        if not casos_set:
            for m in MODELOS_ORDEM:
                casos_set.update(acc_caso[m].keys())
                
        casos = sorted(list(casos_set), key=lambda x: int(x))

        if not casos:
            print("  Nenhum caso encontrado nos dados.")
            continue

        fig01_tempo_medio_por_caso(resumo_caso, casos, out_dir, subtitle)
        fig02_boxplot_tempo(tempos, casos, out_dir, subtitle)
        fig03_taxa_sucesso(resumo_consolidado, out_dir, subtitle)
        fig04_acuracia_por_modelo(acc_consolidado, out_dir, subtitle)
        fig05_acuracia_por_caso(acc_caso, casos, out_dir, subtitle)
        fig06_acuracia_por_atributo(atrib_geral, out_dir, subtitle)
        fig07_heatmap_atributo_modelo(atrib_mc, casos, out_dir, subtitle)
        fig08_consistencia_por_caso(resumo_caso, casos, out_dir, subtitle)
        fig09_consistencia_por_modelo(resumo_consolidado, out_dir, subtitle)
        fig10_radar(acc_consolidado, resumo_consolidado, out_dir, subtitle)
        fig11_saidas_distintas(resumo_caso, casos, out_dir, subtitle)
        
        print(f"  Concluido: Graficos salvos em {out_dir}\n")

if __name__ == "__main__":
    main()
