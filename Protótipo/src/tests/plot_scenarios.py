"""
plot_scenarios.py - Consolidacao e geracao de graficos dos 4 cenarios de teste do extrator.

Le os resultados arquivados em benchmark_output/test_backup/ para os 4 cenarios
resultantes do cruzamento entre versao do prompt e regime de temperatura:

    Cenario 1: Temperatura padrao (0.8) + Prompt Antigo (PROMPT1)
    Cenario 2: Temperatura padrao (0.8) + Prompt Novo   (PROMPT2)
    Cenario 3: Temperatura 0.0        + Prompt Antigo (PROMPT1)
    Cenario 4: Temperatura 0.0        + Prompt Novo   (PROMPT2)

Resolve a divergencia de nomes de arquivo entre as pastas de backup: os cenarios
de temperatura padrao usam o sufixo "_fast_test" e os de temperatura zero usam
"_0_temperature". A resolucao e feita por busca de padrao, sem renomear os
arquivos originais.

Saidas:
  benchmark_output/graficos_cenarios/comparativo/   -> figuras comparativas entre cenarios
  benchmark_output/graficos_cenarios/cenario_N/     -> conjunto completo por cenario
  benchmark_output/graficos_cenarios/tabelas_consolidadas.txt -> dados em texto para as tabelas LaTeX
"""

import math
import os
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# =============================================================================
# CONFIGURACAO
# =============================================================================
SCRIPT_DIR = Path(__file__).resolve().parent
BACKUP_DIR = SCRIPT_DIR / "benchmark_output" / "test_backup"
OUT_ROOT = SCRIPT_DIR / "benchmark_output" / "graficos_cenarios"
COMP_DIR = OUT_ROOT / "comparativo"

MODELOS_ORDEM = ["qwen2.5", "llama3", "deepseek-r1:8b"]
MODELOS_ROTULO = {"qwen2.5": "Qwen 2.5", "llama3": "LLaMA 3", "deepseek-r1:8b": "DeepSeek-R1:8B"}
CORES_MODELOS = {"qwen2.5": "#4C72B0", "llama3": "#DD8452", "deepseek-r1:8b": "#55A868"}
CASOS = ["1", "2", "3", "4", "5"]

ATRIBUTOS_ORDEM = [
    "tipo_projeto", "dominio_negocio", "persistencia", "escala",
    "integracao", "arquitetura_esperada", "experiencia_usuario", "requisito_seguranca",
    "ambiente_implantacao", "maturidade_equipe", "tipo_autenticacao", "ciclo_desenvolvimento",
]

# Cada cenario aponta para a pasta de backup correspondente.
CENARIOS = [
    {"id": 1, "rotulo": "Cenário 1", "curto": "C1",
     "desc": "Temp. padrão + Prompt Antigo", "temp": "0,8", "prompt": "Antigo",
     "pasta": BACKUP_DIR / "standardtemperature" / "prompt antigo",
     "cor": "#8C8C8C"},
    {"id": 2, "rotulo": "Cenário 2", "curto": "C2",
     "desc": "Temp. padrão + Prompt Novo", "temp": "0,8", "prompt": "Novo",
     "pasta": BACKUP_DIR / "standardtemperature" / "prompt novo",
     "cor": "#DD8452"},
    {"id": 3, "rotulo": "Cenário 3", "curto": "C3",
     "desc": "Temp. zero + Prompt Antigo", "temp": "0,0", "prompt": "Antigo",
     "pasta": BACKUP_DIR / "temperature0" / "prompt antigo",
     "cor": "#6ACC64"},
    {"id": 4, "rotulo": "Cenário 4", "curto": "C4",
     "desc": "Temp. zero + Prompt Novo", "temp": "0,0", "prompt": "Novo",
     "pasta": BACKUP_DIR / "temperature0" / "prompt novo",
     "cor": "#4C72B0"},
]

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "#F8F9FA",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.titleweight": "bold",
})


# =============================================================================
# RESOLUCAO DE ARQUIVOS (trata os sufixos _fast_test e _0_temperature)
# =============================================================================
def localizar(pasta: Path, base: str) -> Path:
    """Localiza o arquivo cujo nome comeca por 'base', independente do sufixo."""
    if not pasta.exists():
        raise FileNotFoundError(f"Pasta de cenario nao encontrada: {pasta}")
    candidatos = sorted(pasta.glob(f"{base}*.txt"))
    if not candidatos:
        raise FileNotFoundError(f"Arquivo '{base}*.txt' nao encontrado em {pasta}")
    return candidatos[0]


# =============================================================================
# PARSERS
# =============================================================================
def parse_resumo(path: Path):
    """Extrai metricas de tempo, formato e consistencia por modelo-caso e consolidadas."""
    por_caso = defaultdict(dict)
    consolidado = {}
    texto = path.read_text(encoding="utf-8")

    campos_caso = [
        ("tempo_medio", r"Tempo medio \(ms\):\s*([\d.]+)"),
        ("tempo_mediano", r"Tempo mediano \(ms\):\s*([\d.]+)"),
        ("tempo_p95", r"Tempo p95 \(ms\):\s*([\d.]+)"),
        ("tempo_min", r"Tempo minimo \(ms\):\s*([\d.]+)"),
        ("tempo_max", r"Tempo maximo \(ms\):\s*([\d.]+)"),
        ("taxa_formato", r"Taxa de formato valido:\s*([\d.]+)%"),
        ("taxa_erro", r"Taxa de erro de execucao:\s*([\d.]+)%"),
        ("taxa_sucesso", r"Taxa de sucesso:\s*([\d.]+)%"),
        ("cobertura", r"Cobertura media de chaves:\s*([\d.]+)%"),
        ("consistencia_total", r"Consistencia total:\s*([\d.]+)%"),
        ("consistencia_validos", r"Consistencia somente validos:\s*([\d.]+)%"),
        ("saidas_distintas", r"Saidas validas distintas:\s*(\d+)"),
        ("total_exec", r"Total de execucoes:\s*(\d+)"),
    ]

    for bloco in re.split(r"Modelo:\s+", texto)[1:]:
        m = re.match(r"(.+?)\s*\|\s*Caso de teste:\s*(\d+)", bloco)
        if m:
            modelo, caso = m.group(1).strip(), m.group(2).strip()
            if modelo not in MODELOS_ORDEM:
                continue
            d = {}
            for chave, regex in campos_caso:
                achado = re.search(regex, bloco)
                d[chave] = float(achado.group(1)) if achado else 0.0
            por_caso[modelo][caso] = d
            continue

        m2 = re.match(r"(.+?)[\r\n]", bloco)
        if m2:
            modelo = m2.group(1).strip()
            if modelo in MODELOS_ORDEM:
                d = {}
                for chave, regex in campos_caso:
                    achado = re.search(regex, bloco)
                    d[chave] = float(achado.group(1)) if achado else 0.0
                consolidado[modelo] = d

    return por_caso, consolidado


def parse_accuracy(path: Path):
    """Extrai acuracia por modelo-caso, consolidada, por atributo global e por atributo-modelo-caso."""
    por_caso = defaultdict(dict)
    consolidado = {}
    por_atributo = {}
    atrib_mc = defaultdict(lambda: defaultdict(dict))
    texto = path.read_text(encoding="utf-8")

    # Secao 1: por modelo e caso
    secao1 = texto.split("2) Acuracia consolidada por modelo")[0]
    for bloco in re.split(r"Modelo:\s+", secao1)[1:]:
        m = re.match(r"(.+?)\s*\|\s*Caso de teste:\s*(\d+)", bloco)
        if not m:
            continue
        modelo, caso = m.group(1).strip(), m.group(2).strip()
        if modelo not in MODELOS_ORDEM:
            continue
        med = re.search(r"Acuracia media:\s*([\d.]+)%", bloco)
        mini = re.search(r"Acuracia minima:\s*([\d.]+)%", bloco)
        maxi = re.search(r"Acuracia maxima:\s*([\d.]+)%", bloco)
        perf = re.search(r"Execucoes 100% corretas:\s*(\d+)/(\d+)", bloco)
        val = re.search(r"Execucoes validas avaliadas:\s*(\d+)", bloco)
        por_caso[modelo][caso] = {
            "acuracia_media": float(med.group(1)) if med else 0.0,
            "acuracia_min": float(mini.group(1)) if mini else 0.0,
            "acuracia_max": float(maxi.group(1)) if maxi else 0.0,
            "perfeitas": int(perf.group(1)) if perf else 0,
            "validas": int(val.group(1)) if val else 0,
        }
        # Atributos listados aparecem somente quando ficam abaixo de 100%
        for am in re.finditer(r"^\s+(\w+):\s*\d+/\d+\s*\(([\d.]+)%\)", bloco, re.MULTILINE):
            atrib_mc[modelo][caso][am.group(1)] = float(am.group(2))

    # Secao 2: consolidada por modelo
    resto = texto.split("2) Acuracia consolidada por modelo")
    if len(resto) > 1:
        secao2 = resto[1].split("3) Acuracia por atributo")[0]
        for bloco in re.split(r"Modelo:\s+", secao2)[1:]:
            m2 = re.match(r"(.+?)[\r\n]", bloco)
            if not m2:
                continue
            modelo = m2.group(1).strip()
            if modelo not in MODELOS_ORDEM:
                continue
            med = re.search(r"Acuracia media:\s*([\d.]+)%", bloco)
            mini = re.search(r"Acuracia minima:\s*([\d.]+)%", bloco)
            maxi = re.search(r"Acuracia maxima:\s*([\d.]+)%", bloco)
            perf = re.search(r"Execucoes 100% corretas:\s*(\d+)/(\d+)", bloco)
            consolidado[modelo] = {
                "acuracia_media": float(med.group(1)) if med else 0.0,
                "acuracia_min": float(mini.group(1)) if mini else 0.0,
                "acuracia_max": float(maxi.group(1)) if maxi else 0.0,
                "perfeitas": int(perf.group(1)) if perf else 0,
                "total_validas": int(perf.group(2)) if perf else 0,
            }

    # Secao 3: acuracia por atributo (global)
    if "3) Acuracia por atributo" in texto:
        secao3 = texto.split("3) Acuracia por atributo")[1].split("4) Ranking")[0]
        for am in re.finditer(r"^\s+(\w+):\s*\d+/\d+\s*\(([\d.]+)%\)", secao3, re.MULTILINE):
            por_atributo[am.group(1)] = float(am.group(2))

    return por_caso, consolidado, por_atributo, atrib_mc


def parse_detalhados(path: Path):
    """Extrai a lista de tempos individuais por modelo e caso, para os boxplots."""
    tempos = defaultdict(lambda: defaultdict(list))
    modelo_atual = caso_atual = None
    with path.open(encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if linha.startswith("Modelo:"):
                modelo_atual = linha.split(":", 1)[1].strip()
            elif linha.startswith("Caso de teste:"):
                caso_atual = linha.split(":", 1)[1].strip()
            elif linha.startswith("Tempo_ms:"):
                try:
                    tempos[modelo_atual][caso_atual].append(float(linha.split(":", 1)[1].strip()))
                except ValueError:
                    pass
    return tempos


def carregar_cenario(cen):
    """Carrega todos os dados de um cenario."""
    resumo_path = localizar(cen["pasta"], "resumo_metricas")
    acc_path = localizar(cen["pasta"], "accuracy_report")
    det_path = localizar(cen["pasta"], "resultados_detalhados")

    resumo_caso, resumo_cons = parse_resumo(resumo_path)
    acc_caso, acc_cons, acc_atrib, atrib_mc = parse_accuracy(acc_path)
    tempos = parse_detalhados(det_path)

    dados = dict(cen)
    dados.update({
        "resumo_caso": resumo_caso, "resumo_cons": resumo_cons,
        "acc_caso": acc_caso, "acc_cons": acc_cons,
        "acc_atrib": acc_atrib, "atrib_mc": atrib_mc, "tempos": tempos,
    })
    return dados


# =============================================================================
# UTILITARIOS DE PLOTAGEM
# =============================================================================
def salvar(fig, pasta: Path, nome: str):
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = pasta / nome
    fig.savefig(caminho, dpi=200, bbox_inches="tight")
    plt.close(fig)
    print(f"  Salvo: {caminho.relative_to(SCRIPT_DIR)}")


def metrica_cons(cen, modelo, chave, fonte="resumo_cons"):
    """Leitura defensiva de metrica consolidada."""
    return cen[fonte].get(modelo, {}).get(chave, 0.0)


def barras_cenario_modelo(dados, extrator, titulo, ylabel, nome, fmt="{:.1f}",
                          ylim=None, anotar=True):
    """Grafico de barras agrupadas: eixo x = 4 cenarios, series = 3 modelos."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(dados))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [extrator(cen, modelo) for cen in dados]
        barras = ax.bar(x + i * w, vals, w, label=MODELOS_ROTULO[modelo],
                        color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        if anotar:
            for barra in barras:
                altura = barra.get_height()
                ax.text(barra.get_x() + barra.get_width() / 2, altura + (ylim[1] * 0.012 if ylim else 0.4),
                        fmt.format(altura), ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("Cenário de Teste")
    ax.set_ylabel(ylabel)
    ax.set_title(titulo)
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"{c['rotulo']}\n{c['desc']}" for c in dados], fontsize=9)
    if ylim:
        ax.set_ylim(*ylim)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, COMP_DIR, nome)


# =============================================================================
# FIGURAS COMPARATIVAS ENTRE CENARIOS (fig12 a fig22)
# =============================================================================
def fig12_taxa_sucesso(dados):
    barras_cenario_modelo(
        dados, lambda c, m: metrica_cons(c, m, "taxa_sucesso"),
        "Taxa de Sucesso Estrutural por Cenário e Modelo",
        "Taxa de Sucesso (%)", "fig12_cenarios_taxa_sucesso.png",
        fmt="{:.1f}", ylim=(0, 115))


def fig13_acuracia_media(dados):
    barras_cenario_modelo(
        dados, lambda c, m: metrica_cons(c, m, "acuracia_media", "acc_cons"),
        "Acurácia Média por Cenário e Modelo",
        "Acurácia Média (%)", "fig13_cenarios_acuracia_media.png",
        fmt="{:.1f}", ylim=(0, 100))


def fig14_tempo_medio(dados):
    barras_cenario_modelo(
        dados, lambda c, m: metrica_cons(c, m, "tempo_medio") / 1000.0,
        "Tempo Médio de Execução por Cenário e Modelo",
        "Tempo Médio (s)", "fig14_cenarios_tempo_medio.png",
        fmt="{:.1f}", ylim=(0, 65))


def fig15_consistencia(dados):
    barras_cenario_modelo(
        dados, lambda c, m: metrica_cons(c, m, "consistencia_validos"),
        "Consistência das Respostas Válidas por Cenário e Modelo",
        "Consistência (%)", "fig15_cenarios_consistencia.png",
        fmt="{:.1f}", ylim=(0, 60))


def fig16_execucoes_perfeitas(dados):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(dados))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [c["acc_cons"].get(modelo, {}).get("perfeitas", 0) for c in dados]
        barras = ax.bar(x + i * w, vals, w, label=MODELOS_ROTULO[modelo],
                        color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for barra in barras:
            ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 0.4,
                    f"{int(barra.get_height())}", ha="center", va="bottom", fontsize=9)
    ax.set_xlabel("Cenário de Teste")
    ax.set_ylabel("Execuções com Acerto Total")
    ax.set_title("Execuções 100\\% Corretas por Cenário e Modelo".replace("\\", ""))
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"{c['rotulo']}\n{c['desc']}" for c in dados], fontsize=9)
    ax.set_ylim(0, 35)
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, COMP_DIR, "fig16_cenarios_execucoes_perfeitas.png")


def fig17_heatmap_cenario_modelo(dados):
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
    especificacoes = [
        ("acuracia_media", "acc_cons", "Acurácia Média (%)"),
        ("taxa_sucesso", "resumo_cons", "Taxa de Sucesso (%)"),
    ]
    for ax, (chave, fonte, titulo) in zip(axes, especificacoes):
        matriz = np.zeros((len(dados), len(MODELOS_ORDEM)))
        for i, cen in enumerate(dados):
            for j, modelo in enumerate(MODELOS_ORDEM):
                matriz[i, j] = metrica_cons(cen, modelo, chave, fonte)
        im = ax.imshow(matriz, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
        ax.set_xticks(range(len(MODELOS_ORDEM)))
        ax.set_xticklabels([MODELOS_ROTULO[m] for m in MODELOS_ORDEM], fontsize=9)
        ax.set_yticks(range(len(dados)))
        ax.set_yticklabels([f"{c['rotulo']}" for c in dados], fontsize=10)
        for i in range(len(dados)):
            for j in range(len(MODELOS_ORDEM)):
                cor = "white" if matriz[i, j] < 40 else "black"
                ax.text(j, i, f"{matriz[i, j]:.1f}", ha="center", va="center", fontsize=10, color=cor)
        ax.set_title(titulo, fontsize=12)
        ax.grid(False)
        fig.colorbar(im, ax=ax, shrink=0.85)
    fig.suptitle("Desempenho por Cenário e Modelo", fontsize=14, fontweight="bold", y=1.02)
    salvar(fig, COMP_DIR, "fig17_heatmap_cenario_modelo.png")


def fig18_efeito_prompt_temperatura(dados):
    """Efeitos marginais: prompt (antigo -> novo) e temperatura (0,8 -> 0,0)."""
    por_id = {c["id"]: c for c in dados}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Painel A: efeito do prompt, com a temperatura mantida fixa
    ax = axes[0]
    pares = [(1, 2, "Temp. 0,8"), (3, 4, "Temp. 0,0")]
    x = np.arange(len(pares) * len(MODELOS_ORDEM))
    rotulos, valores, cores = [], [], []
    for antigo, novo, rot_temp in pares:
        for modelo in MODELOS_ORDEM:
            delta = (metrica_cons(por_id[novo], modelo, "acuracia_media", "acc_cons")
                     - metrica_cons(por_id[antigo], modelo, "acuracia_media", "acc_cons"))
            valores.append(delta)
            rotulos.append(f"{MODELOS_ROTULO[modelo]}\n{rot_temp}")
            cores.append(CORES_MODELOS[modelo])
    barras = ax.bar(x, valores, 0.6, color=cores, edgecolor="white")
    for barra, val in zip(barras, valores):
        deslocamento = 0.35 if val >= 0 else -0.9
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + deslocamento,
                f"{val:+.1f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=9,
                fontweight="bold")
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos, fontsize=8)
    ax.set_ylabel("Variação da Acurácia Média (p.p.)")
    ax.set_title("Efeito da Troca do Prompt\n(Antigo para Novo)", fontsize=12)

    # Painel B: efeito da temperatura, com o prompt mantido fixo
    ax = axes[1]
    pares = [(1, 3, "Prompt Antigo"), (2, 4, "Prompt Novo")]
    x = np.arange(len(pares) * len(MODELOS_ORDEM))
    rotulos, valores, cores = [], [], []
    for padrao, zero, rot_prompt in pares:
        for modelo in MODELOS_ORDEM:
            delta = (metrica_cons(por_id[zero], modelo, "acuracia_media", "acc_cons")
                     - metrica_cons(por_id[padrao], modelo, "acuracia_media", "acc_cons"))
            valores.append(delta)
            rotulos.append(f"{MODELOS_ROTULO[modelo]}\n{rot_prompt}")
            cores.append(CORES_MODELOS[modelo])
    barras = ax.bar(x, valores, 0.6, color=cores, edgecolor="white")
    for barra, val in zip(barras, valores):
        deslocamento = 0.35 if val >= 0 else -0.9
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + deslocamento,
                f"{val:+.1f}", ha="center", va="bottom" if val >= 0 else "top", fontsize=9,
                fontweight="bold")
    ax.axhline(0, color="black", linewidth=1)
    ax.set_xticks(x)
    ax.set_xticklabels(rotulos, fontsize=8)
    ax.set_ylabel("Variação da Acurácia Média (p.p.)")
    ax.set_title("Efeito da Redução da Temperatura\n(0,8 para 0,0)", fontsize=12)

    fig.suptitle("Efeitos Isolados do Prompt e da Temperatura sobre a Acurácia",
                 fontsize=14, fontweight="bold", y=1.03)
    salvar(fig, COMP_DIR, "fig18_efeito_prompt_temperatura.png")


def fig19_heatmap_atributo_cenario(dados):
    matriz = np.zeros((len(ATRIBUTOS_ORDEM), len(dados)))
    for j, cen in enumerate(dados):
        for i, atrib in enumerate(ATRIBUTOS_ORDEM):
            matriz[i, j] = cen["acc_atrib"].get(atrib, 0.0)

    fig, ax = plt.subplots(figsize=(8.5, 8))
    im = ax.imshow(matriz, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(len(dados)))
    ax.set_xticklabels([f"{c['rotulo']}\n{c['desc']}" for c in dados], fontsize=9)
    ax.set_yticks(range(len(ATRIBUTOS_ORDEM)))
    ax.set_yticklabels([a.replace("_", " ").title() for a in ATRIBUTOS_ORDEM], fontsize=9)
    for i in range(len(ATRIBUTOS_ORDEM)):
        for j in range(len(dados)):
            cor = "white" if matriz[i, j] < 40 else "black"
            ax.text(j, i, f"{matriz[i, j]:.0f}%", ha="center", va="center", fontsize=9, color=cor)
    ax.set_title("Acurácia por Atributo em Cada Cenário")
    ax.grid(False)
    fig.colorbar(im, ax=ax, label="Acurácia (%)", shrink=0.8)
    salvar(fig, COMP_DIR, "fig19_heatmap_atributo_cenario.png")


def fig20_radar_cenarios(dados, modelo="qwen2.5"):
    categorias = ["Acurácia", "Consistência", "Taxa Sucesso", "Velocidade"]
    n = len(categorias)
    angulos = [k / float(n) * 2 * math.pi for k in range(n)]
    angulos += angulos[:1]

    fig, ax = plt.subplots(figsize=(7.2, 7.2), subplot_kw=dict(polar=True))
    tempos = [metrica_cons(c, modelo, "tempo_medio") for c in dados]
    t_min = min(t for t in tempos if t > 0)

    for cen in dados:
        t = metrica_cons(cen, modelo, "tempo_medio")
        valores = [
            metrica_cons(cen, modelo, "acuracia_media", "acc_cons"),
            metrica_cons(cen, modelo, "consistencia_validos"),
            metrica_cons(cen, modelo, "taxa_sucesso"),
            (t_min / t) * 100 if t > 0 else 0,
        ]
        valores += valores[:1]
        ax.plot(angulos, valores, "o-", linewidth=2, label=f"{cen['rotulo']}", color=cen["cor"])
        ax.fill(angulos, valores, alpha=0.12, color=cen["cor"])

    ax.set_xticks(angulos[:-1])
    ax.set_xticklabels(categorias, fontsize=11)
    for rotulo, angulo in zip(ax.get_xticklabels(), angulos[:-1]):
        graus = math.degrees(angulo) % 360
        if graus < 90 or graus > 270:
            rotulo.set_ha("left")
        elif 90 < graus < 270:
            rotulo.set_ha("right")
    ax.set_ylim(0, 105)
    ax.set_title(f"Comparação Multidimensional dos Cenários ({MODELOS_ROTULO[modelo]})", y=1.09)
    ax.legend(loc="upper right", bbox_to_anchor=(1.32, 1.12))
    salvar(fig, COMP_DIR, "fig20_radar_cenarios.png")


def fig21_acuracia_caso_cenario(dados):
    """Acuracia por caso de teste, com um painel para cada modelo."""
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
    x = np.arange(len(CASOS))
    w = 0.2
    for ax, modelo in zip(axes, MODELOS_ORDEM):
        for i, cen in enumerate(dados):
            vals = [cen["acc_caso"].get(modelo, {}).get(c, {}).get("acuracia_media", 0.0) for c in CASOS]
            ax.bar(x + i * w, vals, w, label=cen["rotulo"], color=cen["cor"],
                   edgecolor="white", linewidth=0.5)
        ax.set_xticks(x + 1.5 * w)
        ax.set_xticklabels([f"Caso {c}" for c in CASOS], fontsize=9)
        ax.set_title(MODELOS_ROTULO[modelo], fontsize=12)
        ax.set_xlabel("Caso de Teste")
        ax.set_ylim(0, 105)
    axes[0].set_ylabel("Acurácia Média (%)")
    axes[-1].legend(loc="upper left", bbox_to_anchor=(1.02, 1), borderaxespad=0, fontsize=9)
    fig.suptitle("Acurácia por Caso de Teste em Cada Cenário", fontsize=14, fontweight="bold", y=1.04)
    salvar(fig, COMP_DIR, "fig21_acuracia_caso_cenario.png")


def fig22_boxplot_tempo_cenarios(dados):
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), sharey=True)
    for ax, modelo in zip(axes, MODELOS_ORDEM):
        series, rotulos, cores = [], [], []
        for cen in dados:
            todos = []
            for c in CASOS:
                todos.extend(cen["tempos"].get(modelo, {}).get(c, []))
            series.append([t / 1000 for t in todos] if todos else [0])
            rotulos.append(cen["curto"])
            cores.append(cen["cor"])
        bp = ax.boxplot(series, tick_labels=rotulos, patch_artist=True, widths=0.55,
                        medianprops=dict(color="black", linewidth=1.4), showfliers=True,
                        flierprops=dict(markersize=3, alpha=0.5))
        for patch, cor in zip(bp["boxes"], cores):
            patch.set_facecolor(cor)
            patch.set_alpha(0.75)
        ax.set_title(MODELOS_ROTULO[modelo], fontsize=12)
        ax.set_xlabel("Cenário")
    axes[0].set_ylabel("Tempo de Resposta (s)")
    fig.suptitle("Distribuição do Tempo de Resposta por Cenário e Modelo",
                 fontsize=14, fontweight="bold", y=1.04)
    salvar(fig, COMP_DIR, "fig22_boxplot_tempo_cenarios.png")


# =============================================================================
# CONJUNTO POR CENARIO (mesmo padrao visual das figuras originais)
# =============================================================================
def acc_caso_valida(cen, modelo, caso):
    """Retorna a acuracia media do par modelo-caso, ou None quando nao houve execucao valida."""
    entrada = cen["acc_caso"].get(modelo, {}).get(caso)
    if not entrada or entrada.get("validas", 0) == 0:
        return None
    return entrada["acuracia_media"]


def atributo_medio(cen, modelo, atrib):
    """Media da acuracia de um atributo para um modelo, considerando apenas casos com execucao valida.

    O relatorio lista somente atributos com acerto inferior a 100%, portanto os
    ausentes correspondem a 100%. Casos sem execucao valida sao descartados para
    nao inflar a media do modelo.
    """
    valores = []
    for caso in CASOS:
        if acc_caso_valida(cen, modelo, caso) is None:
            continue
        valores.append(cen["atrib_mc"].get(modelo, {}).get(caso, {}).get(atrib, 100.0))
    return float(np.mean(valores)) if valores else None


# =============================================================================
# CONJUNTO CLASSICO ATUALIZADO: UM PAINEL POR CENARIO (fig25 a fig30)
# =============================================================================
def _painel_2x2(dados, plot_fn, titulo, nome, figsize=(15, 9.5), polar=False):
    """Cria uma figura com quatro paineis, um por cenario."""
    kw = dict(subplot_kw=dict(polar=True)) if polar else {}
    fig, axes = plt.subplots(2, 2, figsize=figsize, **kw)
    for ax, cen in zip(axes.flat, dados):
        plot_fn(ax, cen)
        ax.set_title(f"{cen['rotulo']}: {cen['desc']}", fontsize=12, pad=14 if polar else 8)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=len(labels),
                   bbox_to_anchor=(0.5, -0.02), fontsize=11)
    fig.suptitle(titulo, fontsize=15, fontweight="bold", y=0.98)
    fig.tight_layout(rect=[0, 0.02, 1, 0.96])
    salvar(fig, COMP_DIR, nome)


def fig25_radar_por_cenario(dados):
    categorias = ["Acurácia", "Consistência", "Taxa Sucesso", "Velocidade"]
    n = len(categorias)
    angulos = [k / float(n) * 2 * math.pi for k in range(n)]
    angulos += angulos[:1]

    # Referencia global de velocidade: menor tempo observado no experimento
    todos_tempos = [metrica_cons(c, m, "tempo_medio") for c in dados for m in MODELOS_ORDEM]
    t_min = min(t for t in todos_tempos if t > 0)

    def desenha(ax, cen):
        for modelo in MODELOS_ORDEM:
            t = metrica_cons(cen, modelo, "tempo_medio")
            valores = [
                metrica_cons(cen, modelo, "acuracia_media", "acc_cons"),
                metrica_cons(cen, modelo, "consistencia_validos"),
                metrica_cons(cen, modelo, "taxa_sucesso"),
                (t_min / t) * 100 if t > 0 else 0,
            ]
            valores += valores[:1]
            ax.plot(angulos, valores, "o-", linewidth=2, label=MODELOS_ROTULO[modelo],
                    color=CORES_MODELOS[modelo], markersize=4)
            ax.fill(angulos, valores, alpha=0.12, color=CORES_MODELOS[modelo])
        ax.set_xticks(angulos[:-1])
        ax.set_xticklabels(categorias, fontsize=9.5)
        for rotulo, angulo in zip(ax.get_xticklabels(), angulos[:-1]):
            graus = math.degrees(angulo) % 360
            if graus < 90 or graus > 270:
                rotulo.set_ha("left")
            elif 90 < graus < 270:
                rotulo.set_ha("right")
        ax.set_ylim(0, 105)
        ax.set_yticks([25, 50, 75, 100])
        ax.set_yticklabels(["25", "50", "75", "100"], fontsize=8)

    _painel_2x2(dados, desenha,
                "Comparação Multidimensional dos Modelos em Cada Cenário",
                "fig25_radar_por_cenario.png", figsize=(13, 12), polar=True)


def fig26_tempo_caso_por_cenario(dados):
    def desenha(ax, cen):
        x = np.arange(len(CASOS))
        w = 0.26
        for i, modelo in enumerate(MODELOS_ORDEM):
            vals = [cen["resumo_caso"].get(modelo, {}).get(c, {}).get("tempo_medio", 0) / 1000
                    for c in CASOS]
            ax.bar(x + i * w, vals, w, label=MODELOS_ROTULO[modelo],
                   color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        ax.set_xticks(x + w)
        ax.set_xticklabels([f"C{c}" for c in CASOS], fontsize=10)
        ax.set_xlabel("Caso de Teste", fontsize=10)
        ax.set_ylabel("Tempo Médio (s)", fontsize=10)
        ax.set_ylim(0, 90)

    _painel_2x2(dados, desenha,
                "Tempo Médio de Resposta por Caso de Teste em Cada Cenário",
                "fig26_tempo_caso_por_cenario.png")


def fig27_acuracia_caso_por_cenario(dados):
    def desenha(ax, cen):
        x = np.arange(len(CASOS))
        w = 0.26
        for i, modelo in enumerate(MODELOS_ORDEM):
            vals, marcas = [], []
            for c in CASOS:
                v = acc_caso_valida(cen, modelo, c)
                vals.append(v if v is not None else 0.0)
                marcas.append(v is None)
            barras = ax.bar(x + i * w, vals, w, label=MODELOS_ROTULO[modelo],
                            color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
            for barra, sem_dado in zip(barras, marcas):
                if sem_dado:
                    barra.set_hatch("///")
                    barra.set_facecolor("#D9D9D9")
                    barra.set_edgecolor("#8C8C8C")
                    ax.text(barra.get_x() + barra.get_width() / 2, 3,
                            "s/v", ha="center", va="bottom", fontsize=7, rotation=90,
                            color="#333333")
        ax.set_xticks(x + w)
        ax.set_xticklabels([f"C{c}" for c in CASOS], fontsize=10)
        ax.set_xlabel("Caso de Teste", fontsize=10)
        ax.set_ylabel("Acurácia Média (%)", fontsize=10)
        ax.set_ylim(0, 105)

    _painel_2x2(dados, desenha,
                "Acurácia Média por Caso de Teste em Cada Cenário",
                "fig27_acuracia_caso_por_cenario.png")


def fig28_consistencia_caso_por_cenario(dados):
    def desenha(ax, cen):
        x = np.arange(len(CASOS))
        w = 0.26
        for i, modelo in enumerate(MODELOS_ORDEM):
            vals = [cen["resumo_caso"].get(modelo, {}).get(c, {}).get("consistencia_validos", 0)
                    for c in CASOS]
            ax.bar(x + i * w, vals, w, label=MODELOS_ROTULO[modelo],
                   color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        ax.set_xticks(x + w)
        ax.set_xticklabels([f"C{c}" for c in CASOS], fontsize=10)
        ax.set_xlabel("Caso de Teste", fontsize=10)
        ax.set_ylabel("Consistência (%)", fontsize=10)
        ax.set_ylim(0, 112)

    _painel_2x2(dados, desenha,
                "Consistência das Respostas Válidas por Caso de Teste em Cada Cenário",
                "fig28_consistencia_caso_por_cenario.png")


def fig29_saidas_distintas_por_cenario(dados):
    def desenha(ax, cen):
        x = np.arange(len(CASOS))
        w = 0.26
        for i, modelo in enumerate(MODELOS_ORDEM):
            vals = [cen["resumo_caso"].get(modelo, {}).get(c, {}).get("saidas_distintas", 0)
                    for c in CASOS]
            barras = ax.bar(x + i * w, vals, w, label=MODELOS_ROTULO[modelo],
                            color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
            for barra in barras:
                ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 0.4,
                        f"{int(barra.get_height())}", ha="center", va="bottom", fontsize=7.5)
        ax.set_xticks(x + w)
        ax.set_xticklabels([f"C{c}" for c in CASOS], fontsize=10)
        ax.set_xlabel("Caso de Teste", fontsize=10)
        ax.set_ylabel("Saídas Distintas", fontsize=10)
        ax.set_ylim(0, 32)

    _painel_2x2(dados, desenha,
                "Quantidade de Saídas Válidas Distintas por Caso de Teste em Cada Cenário",
                "fig29_saidas_distintas_por_cenario.png")


def fig30_heatmap_atributo_modelo_por_cenario(dados):
    def desenha(ax, cen):
        matriz = np.full((len(ATRIBUTOS_ORDEM), len(MODELOS_ORDEM)), np.nan)
        for j, modelo in enumerate(MODELOS_ORDEM):
            for i, atrib in enumerate(ATRIBUTOS_ORDEM):
                v = atributo_medio(cen, modelo, atrib)
                if v is not None:
                    matriz[i, j] = v
        mascarada = np.ma.masked_invalid(matriz)
        cmap = plt.get_cmap("RdYlGn").copy()
        cmap.set_bad("#CCCCCC")
        ax.imshow(mascarada, cmap=cmap, aspect="auto", vmin=0, vmax=100)
        ax.set_xticks(range(len(MODELOS_ORDEM)))
        ax.set_xticklabels([MODELOS_ROTULO[m] for m in MODELOS_ORDEM], fontsize=8.5)
        ax.set_yticks(range(len(ATRIBUTOS_ORDEM)))
        ax.set_yticklabels([a.replace("_", " ").title() for a in ATRIBUTOS_ORDEM], fontsize=8)
        for i in range(len(ATRIBUTOS_ORDEM)):
            for j in range(len(MODELOS_ORDEM)):
                if np.isnan(matriz[i, j]):
                    ax.text(j, i, "n/d", ha="center", va="center", fontsize=7, color="#555555")
                else:
                    cor = "white" if matriz[i, j] < 40 else "black"
                    ax.text(j, i, f"{matriz[i, j]:.0f}", ha="center", va="center",
                            fontsize=7.5, color=cor)
        ax.grid(False)

    _painel_2x2(dados, desenha,
                "Acurácia por Atributo e Modelo em Cada Cenário",
                "fig30_heatmap_atributo_modelo_cenario.png", figsize=(13, 15))


def figuras_por_cenario(cen):
    pasta = OUT_ROOT / f"cenario_{cen['id']}"
    sufixo = f"Cenário {cen['id']}: {cen['desc']}"

    # Tempo medio por caso
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(CASOS))
    w = 0.25
    for i, modelo in enumerate(MODELOS_ORDEM):
        vals = [cen["resumo_caso"].get(modelo, {}).get(c, {}).get("tempo_medio", 0) / 1000 for c in CASOS]
        barras = ax.bar(x + i * w, vals, w, label=MODELOS_ROTULO[modelo],
                        color=CORES_MODELOS[modelo], edgecolor="white", linewidth=0.5)
        for barra in barras:
            ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 0.5,
                    f"{barra.get_height():.1f}", ha="center", va="bottom", fontsize=8)
    ax.set_xlabel("Caso de Teste")
    ax.set_ylabel("Tempo Médio (s)")
    ax.set_title(f"Tempo Médio por Caso e Modelo\n{sufixo}")
    ax.set_xticks(x + w)
    ax.set_xticklabels([f"Caso {c}" for c in CASOS])
    ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1), borderaxespad=0)
    salvar(fig, pasta, "fig01_tempo_medio_por_caso.png")

    # Taxa de sucesso
    fig, ax = plt.subplots(figsize=(7, 5))
    sucesso = [metrica_cons(cen, m, "taxa_sucesso") for m in MODELOS_ORDEM]
    falha = [100 - s for s in sucesso]
    x = np.arange(len(MODELOS_ORDEM))
    bs = ax.bar(x, sucesso, 0.5, color=[CORES_MODELOS[m] for m in MODELOS_ORDEM], edgecolor="white")
    bf = ax.bar(x, falha, 0.5, bottom=sucesso, color="#E07B73", edgecolor="white", alpha=0.85)
    for barra, val in zip(bs, sucesso):
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() / 2, f"{val:.1f}%",
                ha="center", va="center", fontweight="bold", color="white", fontsize=11)
    for barra, val, bot in zip(bf, falha, sucesso):
        if val > 2:
            ax.text(barra.get_x() + barra.get_width() / 2, bot + val / 2, f"{val:.1f}%",
                    ha="center", va="center", fontweight="bold", color="white", fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels([MODELOS_ROTULO[m] for m in MODELOS_ORDEM], fontsize=9)
    ax.set_ylabel("Porcentagem (%)")
    ax.set_title(f"Taxa de Sucesso e de Falha\n{sufixo}")
    ax.set_ylim(0, 105)
    salvar(fig, pasta, "fig03_taxa_sucesso.png")

    # Acuracia por modelo
    fig, ax = plt.subplots(figsize=(7, 5))
    vals = [metrica_cons(cen, m, "acuracia_media", "acc_cons") for m in MODELOS_ORDEM]
    barras = ax.bar([MODELOS_ROTULO[m] for m in MODELOS_ORDEM], vals, 0.5,
                    color=[CORES_MODELOS[m] for m in MODELOS_ORDEM], edgecolor="white")
    for barra, val in zip(barras, vals):
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height() + 0.6,
                f"{val:.2f}%", ha="center", va="bottom", fontweight="bold")
    ax.set_ylabel("Acurácia Média (%)")
    ax.set_title(f"Acurácia Média Consolidada\n{sufixo}")
    ax.set_ylim(0, 100)
    salvar(fig, pasta, "fig04_acuracia_por_modelo.png")

    # Acuracia por atributo
    itens = sorted(cen["acc_atrib"].items(), key=lambda kv: kv[1])
    if itens:
        nomes = [k.replace("_", " ").title() for k, _ in itens]
        vals = [v for _, v in itens]
        cores = ["#E07B73" if v < 60 else "#F0C05A" if v < 80 else "#55A868" for v in vals]
        fig, ax = plt.subplots(figsize=(9, 6))
        barras = ax.barh(nomes, vals, color=cores, edgecolor="white", height=0.65)
        for barra, val in zip(barras, vals):
            ax.text(barra.get_width() + 0.8, barra.get_y() + barra.get_height() / 2,
                    f"{val:.1f}%", ha="left", va="center", fontsize=9)
        ax.set_xlabel("Acurácia (%)")
        ax.set_title(f"Acurácia por Atributo\n{sufixo}")
        ax.set_xlim(0, 110)
        legendas = [
            matplotlib.patches.Patch(facecolor="#55A868", label="\u2265 80%"),
            matplotlib.patches.Patch(facecolor="#F0C05A", label="60 \u2013 79%"),
            matplotlib.patches.Patch(facecolor="#E07B73", label="< 60%"),
        ]
        ax.legend(handles=legendas, loc="lower right", title="Acurácia")
        salvar(fig, pasta, "fig06_acuracia_por_atributo.png")


# =============================================================================
# TABELAS CONSOLIDADAS EM TEXTO
# =============================================================================
def escrever_tabelas(dados):
    linhas = []
    linhas.append("=" * 100)
    linhas.append("DADOS CONSOLIDADOS DOS 4 CENARIOS DE TESTE DO EXTRATOR DE REQUISITOS")
    linhas.append("=" * 100)

    linhas.append("\n\n1) TABELA GERAL POR CENARIO E MODELO")
    linhas.append("-" * 100)
    cab = f"{'Cenario':<10}{'Modelo':<18}{'Sucesso':>10}{'Acuracia':>11}{'Perfeitas':>12}{'Tempo(s)':>11}{'Consist.':>10}"
    linhas.append(cab)
    linhas.append("-" * 100)
    for cen in dados:
        for modelo in MODELOS_ORDEM:
            suc = metrica_cons(cen, modelo, "taxa_sucesso")
            acc = metrica_cons(cen, modelo, "acuracia_media", "acc_cons")
            perf = cen["acc_cons"].get(modelo, {}).get("perfeitas", 0)
            tot = cen["acc_cons"].get(modelo, {}).get("total_validas", 0)
            tempo = metrica_cons(cen, modelo, "tempo_medio") / 1000
            cons = metrica_cons(cen, modelo, "consistencia_validos")
            linhas.append(f"{cen['curto']:<10}{MODELOS_ROTULO[modelo]:<18}{suc:>9.2f}%{acc:>10.2f}%"
                          f"{f'{perf}/{tot}':>12}{tempo:>11.2f}{cons:>9.2f}%")
        linhas.append("-" * 100)

    linhas.append("\n\n2) TEMPO: MEDIANA, P95, MINIMO E MAXIMO (segundos)")
    linhas.append("-" * 100)
    linhas.append(f"{'Cenario':<10}{'Modelo':<18}{'Media':>10}{'Mediana':>10}{'p95':>10}{'Min':>10}{'Max':>10}")
    linhas.append("-" * 100)
    for cen in dados:
        for modelo in MODELOS_ORDEM:
            r = cen["resumo_cons"].get(modelo, {})
            linhas.append(f"{cen['curto']:<10}{MODELOS_ROTULO[modelo]:<18}"
                          f"{r.get('tempo_medio', 0)/1000:>10.2f}{r.get('tempo_mediano', 0)/1000:>10.2f}"
                          f"{r.get('tempo_p95', 0)/1000:>10.2f}{r.get('tempo_min', 0)/1000:>10.2f}"
                          f"{r.get('tempo_max', 0)/1000:>10.2f}")
        linhas.append("-" * 100)

    linhas.append("\n\n3) ACURACIA POR ATRIBUTO EM CADA CENARIO (%)")
    linhas.append("-" * 100)
    linhas.append(f"{'Atributo':<24}" + "".join(f"{c['curto']:>10}" for c in dados))
    linhas.append("-" * 100)
    for atrib in ATRIBUTOS_ORDEM:
        linhas.append(f"{atrib:<24}" + "".join(f"{c['acc_atrib'].get(atrib, 0.0):>9.2f}%" for c in dados))

    linhas.append("\n\n4) ACURACIA POR CASO DE TESTE, MODELO E CENARIO (%)")
    linhas.append("-" * 100)
    linhas.append(f"{'Modelo':<18}{'Caso':<8}" + "".join(f"{c['curto']:>10}" for c in dados))
    linhas.append("-" * 100)
    for modelo in MODELOS_ORDEM:
        for caso in CASOS:
            vals = "".join(f"{c['acc_caso'].get(modelo, {}).get(caso, {}).get('acuracia_media', 0.0):>9.2f}%"
                           for c in dados)
            linhas.append(f"{MODELOS_ROTULO[modelo]:<18}{'Caso ' + caso:<8}{vals}")
        linhas.append("-" * 100)

    linhas.append("\n\n5) TAXA DE SUCESSO POR CASO DE TESTE, MODELO E CENARIO (%)")
    linhas.append("-" * 100)
    linhas.append(f"{'Modelo':<18}{'Caso':<8}" + "".join(f"{c['curto']:>10}" for c in dados))
    linhas.append("-" * 100)
    for modelo in MODELOS_ORDEM:
        for caso in CASOS:
            vals = "".join(f"{c['resumo_caso'].get(modelo, {}).get(caso, {}).get('taxa_sucesso', 0.0):>9.2f}%"
                           for c in dados)
            linhas.append(f"{MODELOS_ROTULO[modelo]:<18}{'Caso ' + caso:<8}{vals}")
        linhas.append("-" * 100)

    linhas.append("\n\n6) SAIDAS VALIDAS DISTINTAS E COBERTURA DE CHAVES")
    linhas.append("-" * 100)
    linhas.append(f"{'Cenario':<10}{'Modelo':<18}{'Distintas':>12}{'Cobertura':>12}{'Formato':>11}")
    linhas.append("-" * 100)
    for cen in dados:
        for modelo in MODELOS_ORDEM:
            r = cen["resumo_cons"].get(modelo, {})
            linhas.append(f"{cen['curto']:<10}{MODELOS_ROTULO[modelo]:<18}"
                          f"{int(r.get('saidas_distintas', 0)):>12}{r.get('cobertura', 0):>11.2f}%"
                          f"{r.get('taxa_formato', 0):>10.2f}%")
        linhas.append("-" * 100)

    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    destino = OUT_ROOT / "tabelas_consolidadas.txt"
    destino.write_text("\n".join(linhas), encoding="utf-8")
    print(f"\n  Tabelas salvas: {destino.relative_to(SCRIPT_DIR)}")


# =============================================================================
# EXECUCAO
# =============================================================================
def main():
    print("Carregando dados dos 4 cenarios de teste...\n")
    dados = []
    for cen in CENARIOS:
        carregado = carregar_cenario(cen)
        n_modelos = len(carregado["resumo_cons"])
        print(f"  {cen['rotulo']} ({cen['desc']}): {n_modelos} modelos carregados")
        dados.append(carregado)

    print("\nGerando figuras comparativas entre cenarios...")
    fig12_taxa_sucesso(dados)
    fig13_acuracia_media(dados)
    fig14_tempo_medio(dados)
    fig15_consistencia(dados)
    fig16_execucoes_perfeitas(dados)
    fig17_heatmap_cenario_modelo(dados)
    fig18_efeito_prompt_temperatura(dados)
    fig19_heatmap_atributo_cenario(dados)
    fig20_radar_cenarios(dados)
    fig21_acuracia_caso_cenario(dados)
    fig22_boxplot_tempo_cenarios(dados)
    fig23_matriz_cenarios()

    print("\nGerando conjunto classico atualizado (um painel por cenario)...")
    fig25_radar_por_cenario(dados)
    fig26_tempo_caso_por_cenario(dados)
    fig27_acuracia_caso_por_cenario(dados)
    fig28_consistencia_caso_por_cenario(dados)
    fig29_saidas_distintas_por_cenario(dados)
    fig30_heatmap_atributo_modelo_por_cenario(dados)

    print("\nGerando conjunto de figuras por cenario...")
    for cen in dados:
        print(f"  {cen['rotulo']}:")
        figuras_por_cenario(cen)

    escrever_tabelas(dados)
    print("\nConcluido.")


# =============================================================================
# DIAGRAMA DA MATRIZ DE CENARIOS (figura conceitual para a Metodologia)
# =============================================================================
def fig23_matriz_cenarios():
    """Diagrama 2x2 do desenho experimental: prompt x temperatura."""
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 8)
    ax.axis("off")
    ax.grid(False)

    celulas = [
        (1, 4.2, "#8C8C8C", "Cenário 1", "Prompt Antigo\nTemperatura 0,8",
         "Configuração de referência\n(linha de base)"),
        (5.6, 4.2, "#DD8452", "Cenário 2", "Prompt Novo\nTemperatura 0,8",
         "Efeito isolado\nda instrução"),
        (1, 0.6, "#6ACC64", "Cenário 3", "Prompt Antigo\nTemperatura 0,0",
         "Efeito isolado\nda temperatura"),
        (5.6, 0.6, "#4C72B0", "Cenário 4", "Prompt Novo\nTemperatura 0,0",
         "Efeito combinado\ndas duas variáveis"),
    ]

    for x, y, cor, titulo, config, papel in celulas:
        ret = plt.Rectangle((x, y), 3.4, 2.9, facecolor=cor, alpha=0.22,
                            edgecolor=cor, linewidth=2.2)
        ax.add_patch(ret)
        ax.text(x + 1.7, y + 2.42, titulo, ha="center", va="center",
                fontsize=13, fontweight="bold", color=cor)
        ax.text(x + 1.7, y + 1.55, config, ha="center", va="center", fontsize=10.5)
        ax.text(x + 1.7, y + 0.55, papel, ha="center", va="center",
                fontsize=9, style="italic", color="#444444")

    ax.text(5.0, 7.55, "Versão da Instrução de Extração", ha="center", va="center",
            fontsize=11.5, fontweight="bold")
    ax.text(2.7, 7.15, "Menos descritiva", ha="center", va="center", fontsize=10)
    ax.text(7.3, 7.15, "Mais descritiva", ha="center", va="center", fontsize=10)

    ax.text(0.42, 5.65, "Amostragem\nestocástica\n(0,8)", ha="center", va="center",
            fontsize=10, rotation=90)
    ax.text(0.42, 2.05, "Amostragem\ndeterminística\n(0,0)", ha="center", va="center",
            fontsize=10, rotation=90)
    ax.text(-0.15, 3.85, "Regime de Temperatura", ha="center", va="center",
            fontsize=11.5, fontweight="bold", rotation=90)

    ax.text(5.0, 0.06, "Cada célula corresponde a 450 execuções (3 modelos × 5 casos × 30 repetições)",
            ha="center", va="center", fontsize=9.5, style="italic", color="#333333")

    salvar(fig, COMP_DIR, "fig23_matriz_cenarios.png")


if __name__ == "__main__":
    main()
