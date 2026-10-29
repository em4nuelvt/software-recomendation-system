"""
Ponto de entrada na raiz do repositório para o Sistema de Recomendação de Tecnologias.
Redireciona a execução diretamente para o módulo em Protótipo/src/executar_sistema.py.

Uso:
    python run.py
    python run.py "Quero um aplicativo mobile..."
"""

import os
import sys

# Adiciona o diretório do protótipo ao path de importação
PROTO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Protótipo", "src")
if PROTO_DIR not in sys.path:
    sys.path.insert(0, PROTO_DIR)

if __name__ == "__main__":
    from executar_sistema import executar_fluxo_completo
    executar_fluxo_completo()
