"""
Configurações do projeto
"""
import os
import sys
import logging

def get_base_path():
    # Se estiver rodando como executável
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    # Se estiver rodando como script
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def ensure_directories():
    """Cria a estrutura de diretórios necessária se não existir"""
    logging.info(f"Criando estrutura de diretórios em: {BASE_DIR}")
    
    # Diretórios principais
    for dir_path in [DATA_DIR]:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
            logging.info(f"Diretório criado: {dir_path}")
    
    # Subdiretórios de data
    data_subdirs = ['output']
    for subdir in data_subdirs:
        path = os.path.join(DATA_DIR, subdir)
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            logging.info(f"Subdiretório criado: {path}")

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Diretórios
BASE_DIR = get_base_path()
DATA_DIR = os.path.join(BASE_DIR, 'data')

# Arquivos de dados
DADOS_UNIFICADOS = os.path.join(DATA_DIR, 'base_unificada.xlsx')

# Arquivos KML
KML_EM_BRANCO = os.path.join(DATA_DIR, 'output', 'municipios_em_branco.kml')
KML_REGIONAL = os.path.join(DATA_DIR, 'output', 'municipios_regional.kml')
KML_FILIAL = os.path.join(DATA_DIR, 'output', 'municipios_filial.kml')
KML_UNIFICADO = os.path.join(DATA_DIR, 'output', 'municipios_unificado.kml')

# Criar estrutura de diretórios ao importar o módulo
ensure_directories()
