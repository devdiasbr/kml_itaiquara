"""
Funções utilitárias para o projeto
"""
import os
import hashlib
import colorsys
from src.config import DATA_DIR
import pandas as pd

def format_value(value, is_population=False):
    """
    Formata um valor numérico para exibição
    """
    try:
        if pd.isna(value):
            return "N/A"
        
        if is_population:
            return f"{int(value):,}".replace(",", ".")
        
        return str(value)
    except:
        return str(value)

def criar_pasta_kml():
    """Cria a pasta para os KMLs se não existir"""
    output_dir = os.path.join(DATA_DIR, 'output', 'kml')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def criar_estrutura_pastas():
    """
    Cria a estrutura de pastas necessária para o projeto
    """
    # Lista de pastas a serem criadas
    pastas = [
        os.path.join(DATA_DIR, 'input'),
        os.path.join(DATA_DIR, 'output'),
        os.path.join(DATA_DIR, 'output', 'kml'),
        os.path.join(DATA_DIR, 'temp')
    ]
    
    # Criar cada pasta se não existir
    for pasta in pastas:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"Pasta criada: {pasta}")
        else:
            print(f"Pasta já existe: {pasta}")

def gerar_cor_unica(texto):
    """
    Gera uma cor única baseada no texto
    """
    # Usar hash para gerar um número único para cada texto
    hash_obj = hashlib.md5(texto.encode())
    hash_hex = hash_obj.hexdigest()
    
    # Converter os primeiros 6 caracteres do hash para um número entre 0 e 1
    hue = int(hash_hex[:6], 16) / 0xFFFFFF
    
    # Converter HSV para RGB
    rgb = colorsys.hsv_to_rgb(hue, 0.7, 0.8)  # Saturação e valor fixos
    
    # Converter RGB para formato KML (aabbggrr)
    r = int(rgb[0] * 255)
    g = int(rgb[1] * 255)
    b = int(rgb[2] * 255)
    a = 200  # Alpha fixo em ~78%
    
    return f'{a:02x}{b:02x}{g:02x}{r:02x}'

def get_color_for_unit(unit_name, unit_type):
    """Gera uma cor única para a unidade baseada no nome"""
    # Usar hash para gerar um número único para cada nome
    hash_obj = hashlib.md5(unit_name.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    
    # Ajustar a cor base de acordo com o tipo de unidade
    if unit_type == 'Regional':
        hue = (hash_int % 100) / 100.0  # Variação no tom
        saturation = 0.8  # Alta saturação
        value = 0.8  # Brilho moderado
    elif unit_type == 'Filial':
        hue = ((hash_int + 50) % 100) / 100.0  # Tom diferente
        saturation = 0.6  # Saturação média
        value = 0.9  # Brilho alto
    else:  # Em Branco
        hue = 0  # Sem tom
        saturation = 0  # Sem saturação
        value = 0.7  # Brilho médio
    
    # Converter HSV para RGB
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    
    # Converter RGB para ABGR (formato do KML)
    abgr = f'{int(rgb[2]*255):02x}{int(rgb[1]*255):02x}{int(rgb[0]*255):02x}'
    
    return abgr
