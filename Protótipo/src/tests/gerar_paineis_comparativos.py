"""
Script para montagem dos painéis comparativos 2x2 dos cenários experimentais.
Gera imagens compostas de alta resolução preservando a formatação e legendas originais.
"""

import os
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GRAFICOS_DIR = os.path.join(BASE_DIR, "benchmark_output", "graficos")
OUTPUT_DIR = os.path.join(GRAFICOS_DIR, "paineis_comparativos")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Diretórios dos cenários regulares (1 a 4)
CENARIOS_REGULARES = [
    os.path.join(GRAFICOS_DIR, "1 - Prompt antigo + temperatura padrao"),
    os.path.join(GRAFICOS_DIR, "2 - Prompt antigo + temperatura 0"),
    os.path.join(GRAFICOS_DIR, "3 - Prompt novo + temperatura padrao"),
    os.path.join(GRAFICOS_DIR, "4 - Prompt novo + temperatura 0"),
]

# Diretórios do teste de estresse (5 a 8)
CENARIOS_ESTRESSE = [
    os.path.join(GRAFICOS_DIR, "5 - Teste de estresse prompt antigo + temperatura padrao"),
    os.path.join(GRAFICOS_DIR, "6 - Teste de estresse prompt antigo + temperatura 0"),
    os.path.join(GRAFICOS_DIR, "7 - Teste de estresse prompt novo + temperatura padrao"),
    os.path.join(GRAFICOS_DIR, "8 - Teste de estresse prompt novo + temperatura 0"),
]

def criar_painel_2x2(pastas, nome_figura_origem, nome_saida, padding=25, bg_color=(255, 255, 255)):
    """
    Combina 4 imagens em uma matriz 2x2:
    [Cenário 1 / 5] [Cenário 2 / 6]
    [Cenário 3 / 7] [Cenário 4 / 8]
    """
    imagens = []
    for pasta in pastas:
        caminho = os.path.join(pasta, nome_figura_origem)
        if not os.path.exists(caminho):
            print(f"[AVISO] Arquivo não encontrado: {caminho}")
            return False
        imagens.append(Image.open(caminho))

    # Obter dimensões uniformes
    larguras = [im.width for im in imagens]
    alturas = [im.height for im in imagens]
    w = max(larguras)
    h = max(alturas)

    # Redimensionar suavemente caso haja diferença minúscula de pixels
    imagens_res = [im.resize((w, h), Image.Resampling.LANCZOS) for im in imagens]

    # Criar imagem final: 2 colunas, 2 linhas
    total_w = 2 * w + 3 * padding
    total_h = 2 * h + 3 * padding

    painel = Image.new("RGB", (total_w, total_h), bg_color)

    # Colar as 4 imagens
    # (0,0): Top-Left
    painel.paste(imagens_res[0], (padding, padding))
    # (0,1): Top-Right
    painel.paste(imagens_res[1], (w + 2 * padding, padding))
    # (1,0): Bottom-Left
    painel.paste(imagens_res[2], (padding, h + 2 * padding))
    # (1,1): Bottom-Right
    painel.paste(imagens_res[3], (w + 2 * padding, h + 2 * padding))

    caminho_final = os.path.join(OUTPUT_DIR, nome_saida)
    painel.save(caminho_final, format="PNG", quality=95)
    print(f"[OK] Painel gerado com sucesso: {caminho_final} ({total_w}x{total_h}px)")
    return True

def main():
    print("=== GERANDO PAINÉIS COMPARATIVOS 2x2 PARA O CAPÍTULO 4 ===")
    
    # 1. Painéis dos Cenários Regulares (Cenários 1 a 4)
    regulares = [
        ("fig03_taxa_sucesso.png", "painel_taxa_sucesso_fatorial.png"),
        ("fig04_acuracia_por_modelo.png", "painel_acuracia_modelo_fatorial.png"),
        ("fig09_consistencia_por_modelo.png", "painel_consistencia_modelo_fatorial.png"),
        ("fig01_tempo_medio_por_caso.png", "painel_tempo_medio_caso_fatorial.png"),
        ("fig07_heatmap_atributo_modelo.png", "painel_heatmap_atributos_fatorial.png"),
        ("fig10_radar_comparativo.png", "painel_radar_comparativo_fatorial.png"),
    ]
    
    for orig, saida in regulares:
        criar_painel_2x2(CENARIOS_REGULARES, orig, saida)

    # 2. Painéis do Teste de Estresse (Cenários 5 a 8)
    estresse = [
        ("fig06_acuracia_por_atributo.png", "painel_estresse_acuracia_atributo.png"),
        ("fig10_radar_comparativo.png", "painel_estresse_radar.png"),
        ("fig03_taxa_sucesso.png", "painel_estresse_taxa_sucesso.png"),
        ("fig04_acuracia_por_modelo.png", "painel_estresse_acuracia_modelo.png"),
    ]
    
    for orig, saida in estresse:
        criar_painel_2x2(CENARIOS_ESTRESSE, orig, saida)

    print("\nTodos os painéis foram salvos em:")
    print(OUTPUT_DIR)

    # 3. Copiar painéis e radares individuais para a pasta do LaTeX
    import shutil
    raiz_pfc = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "..", ".."))
    latex_cenarios_dir = os.path.join(raiz_pfc, "Latex PFC II", "Monografia_Emanuel___PFC_I", "Imagens", "cenarios")
    os.makedirs(latex_cenarios_dir, exist_ok=True)

    # Copiar todos os painéis gerados
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".png"):
            shutil.copy2(os.path.join(OUTPUT_DIR, f), os.path.join(latex_cenarios_dir, f))
            print(f"[LATEX] Painel copiado: {f}")

    # Copiar radares e gráficos de destaque individuais
    mapa_individuais = {
        # Radares
        "cenario1_radar.png": os.path.join(CENARIOS_REGULARES[0], "fig10_radar_comparativo.png"),
        "cenario2_radar.png": os.path.join(CENARIOS_REGULARES[1], "fig10_radar_comparativo.png"),
        "cenario3_radar.png": os.path.join(CENARIOS_REGULARES[2], "fig10_radar_comparativo.png"),
        "cenario4_radar.png": os.path.join(CENARIOS_REGULARES[3], "fig10_radar_comparativo.png"),
        "estresse_e5_radar.png": os.path.join(CENARIOS_ESTRESSE[0], "fig10_radar_comparativo.png"),
        "estresse_e6_radar.png": os.path.join(CENARIOS_ESTRESSE[1], "fig10_radar_comparativo.png"),
        "estresse_e7_radar.png": os.path.join(CENARIOS_ESTRESSE[2], "fig10_radar_comparativo.png"),
        "estresse_e8_radar.png": os.path.join(CENARIOS_ESTRESSE[3], "fig10_radar_comparativo.png"),
        # Gráficos de destaque empírico individual
        "cenario1_taxa_sucesso.png": os.path.join(CENARIOS_REGULARES[0], "fig03_taxa_sucesso.png"),
        "cenario2_consistencia_modelo.png": os.path.join(CENARIOS_REGULARES[1], "fig09_consistencia_por_modelo.png"),
        "cenario3_tempo_medio_caso.png": os.path.join(CENARIOS_REGULARES[2], "fig01_tempo_medio_por_caso.png"),
        "cenario4_heatmap_atributos.png": os.path.join(CENARIOS_REGULARES[3], "fig07_heatmap_atributo_modelo.png"),
        "estresse_e6_acuracia_atributo.png": os.path.join(CENARIOS_ESTRESSE[1], "fig06_acuracia_por_atributo.png"),
        "estresse_e8_acuracia_modelo.png": os.path.join(CENARIOS_ESTRESSE[3], "fig04_acuracia_por_modelo.png"),
    }
    for nome_dst, caminho_src in mapa_individuais.items():
        if os.path.exists(caminho_src):
            shutil.copy2(caminho_src, os.path.join(latex_cenarios_dir, nome_dst))
            print(f"[LATEX] Imagem individual copiada: {nome_dst}")

if __name__ == "__main__":
    main()
