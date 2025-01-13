"""
Módulo para geração de arquivos KML
"""
import os
import simplekml
import pandas as pd
from datetime import datetime

from src.config import DATA_DIR
from src.utils import format_value, criar_pasta_kml, gerar_cor_unica

def gerar_kml_por_tipo_unidade(df):
    """
    Gera KML organizando por tipo de unidade
    """
    # Criar pasta de saída se não existir
    output_dir = criar_pasta_kml()
    
    # Agrupar por TIPO_UNIDADE
    tipos_unidade = sorted(df['TIPO UNIDADE'].unique())
    arquivos_gerados = []
    
    # Gerar um KML para cada tipo de unidade
    for tipo in tipos_unidade:
        # Criar KML base para este tipo
        kml = simplekml.Kml()
        doc = kml.document
        doc.name = f'Distribuidores - {tipo}'
        
        # Filtrar dados para este tipo
        df_tipo = df[df['TIPO UNIDADE'] == tipo]
        
        # Agrupar por UNIDADE
        unidades = sorted(df_tipo['UNIDADE'].unique())
        for unidade in unidades:
            # Criar pasta para a unidade
            folder_unidade = doc.newfolder(name=unidade)
            df_unidade = df_tipo[df_tipo['UNIDADE'] == unidade]
            
            # Agrupar por RAZAO SOCIAL
            razoes_sociais = sorted(df_unidade['RAZAO SOCIAL'].unique())
            for razao_social in razoes_sociais:
                # Criar pasta para a razão social
                folder_razao = folder_unidade.newfolder(name=razao_social)
                df_razao = df_unidade[df_unidade['RAZAO SOCIAL'] == razao_social]
                
                # Gerar cor única para esta razão social
                cor = 'F1EE8Eff' if tipo == 'EM BRANCO' else gerar_cor_unica(razao_social)
                
                # Criar estilo normal
                style_normal = simplekml.Style()
                style_normal.linestyle.color = 'FFFFFFFF'  # Borda branca
                style_normal.linestyle.width = 0.2
                style_normal.polystyle.color = cor
                style_normal.polystyle.fill = 1
                style_normal.polystyle.outline = 1
                
                # Criar estilo highlight
                style_highlight = simplekml.Style()
                style_highlight.linestyle.color = 'FFFFFFFF'  # Borda branca
                style_highlight.linestyle.width = 0.8
                style_highlight.polystyle.color = cor
                style_highlight.polystyle.fill = 1
                style_highlight.polystyle.outline = 1
                
                # Criar StyleMap
                style_map = simplekml.StyleMap()
                style_map.normalstyle = style_normal
                style_map.highlightstyle = style_highlight
                
                # Adicionar municípios da razão social
                for _, municipio in df_razao.iterrows():
                    # Criar placemark para o município
                    placemark = folder_razao.newpoint(
                        name=f"{municipio['MUNICIPIO']} / {municipio['UF']}\nPOPULAÇÃO: {format_value(municipio['POPULACAO'], True)}"
                    ) if municipio['COORDENADAS'].upper() == 'EM BRANCO' else folder_razao.newpolygon(
                        name=f"{municipio['MUNICIPIO']} / {municipio['UF']}\nPOPULAÇÃO: {format_value(municipio['POPULACAO'], True)}"
                    )
                    
                    # Adicionar descrição
                    desc = f"""DISTRIBUIDOR: {municipio['RAZAO SOCIAL']}
CONTATO DISTRIBUIDOR: {municipio['CONTATO DISTRIBUIDOR']}
RESPONSÁVEL: {municipio['RESPONSAVEL']}
CONTATO RESPONSÁVEL: {municipio['CONTATO RESPONSAVEL']}
ENDEREÇO: {municipio['SEDE DISTRIBUIDOR']}"""
                    placemark.description = desc
                    
                    # Aplicar estilo
                    placemark.stylemap = style_map
                    
                    # Adicionar coordenadas
                    if municipio['COORDENADAS'].upper() == 'EM BRANCO':
                        # Usar um ponto central para municípios sem coordenadas
                        placemark.coords = [(-15.7801, -47.9292)]  # Ponto em Brasília
                    else:
                        # Usar coordenadas normais para polígonos
                        coords_list = [tuple(map(float, coord.split(','))) for coord in municipio['COORDENADAS'].split()]
                        placemark.outerboundaryis = coords_list
                        placemark.tessellate = 1
        
        # Salvar KML para este tipo
        tipo_nome = tipo.replace(' ', '_').lower()
        output_file = os.path.join(output_dir, f'distribuidores_{tipo_nome}.kml')
        kml.save(output_file)
        print(f"KML gerado: {output_file}")
        arquivos_gerados.append(output_file)
    
    return arquivos_gerados

def gerar_kml_unificado(df):
    """
    Gera um KML unificado com todos os dados agrupados por TIPO UNIDADE > UNIDADE > RAZAO SOCIAL > MUNICIPIOS
    """
    # Criar pasta de saída se não existir
    output_dir = criar_pasta_kml()
    
    # Criar KML base
    kml = simplekml.Kml()
    doc = kml.document
    doc.name = 'Distribuidores - Unificado'
    
    # Agrupar por TIPO_UNIDADE
    tipos_unidade = sorted(df['TIPO UNIDADE'].unique())
    
    # Para cada TIPO_UNIDADE
    for tipo in tipos_unidade:
        # Criar pasta para o tipo
        folder_tipo = doc.newfolder(name=tipo)
        df_tipo = df[df['TIPO UNIDADE'] == tipo]
        
        # Agrupar por UNIDADE
        unidades = sorted(df_tipo['UNIDADE'].unique())
        for unidade in unidades:
            # Criar pasta para a unidade
            folder_unidade = folder_tipo.newfolder(name=unidade)
            df_unidade = df_tipo[df_tipo['UNIDADE'] == unidade]
            
            # Agrupar por RAZAO SOCIAL
            razoes_sociais = sorted(df_unidade['RAZAO SOCIAL'].unique())
            for razao_social in razoes_sociais:
                # Criar pasta para a razão social
                folder_razao = folder_unidade.newfolder(name=razao_social)
                df_razao = df_unidade[df_unidade['RAZAO SOCIAL'] == razao_social]
                
                # Gerar cor única para esta razão social
                cor = 'F1EE8Eff' if tipo == 'EM BRANCO' else gerar_cor_unica(razao_social)
                
                # Criar estilo normal
                style_normal = simplekml.Style()
                style_normal.linestyle.color = 'FFFFFFFF'  # Borda branca
                style_normal.linestyle.width = 0.2
                style_normal.polystyle.color = cor
                style_normal.polystyle.fill = 1
                style_normal.polystyle.outline = 1
                
                # Criar estilo highlight
                style_highlight = simplekml.Style()
                style_highlight.linestyle.color = 'FFFFFFFF'  # Borda branca
                style_highlight.linestyle.width = 0.8
                style_highlight.polystyle.color = cor
                style_highlight.polystyle.fill = 1
                style_highlight.polystyle.outline = 1
                
                # Criar StyleMap
                style_map = simplekml.StyleMap()
                style_map.normalstyle = style_normal
                style_map.highlightstyle = style_highlight
                
                # Adicionar municípios da razão social
                for _, municipio in df_razao.iterrows():
                    # Criar placemark para o município
                    placemark = folder_razao.newpoint(
                        name=f"{municipio['MUNICIPIO']} / {municipio['UF']}\nPOPULAÇÃO: {format_value(municipio['POPULACAO'], True)}"
                    ) if municipio['COORDENADAS'].upper() == 'EM BRANCO' else folder_razao.newpolygon(
                        name=f"{municipio['MUNICIPIO']} / {municipio['UF']}\nPOPULAÇÃO: {format_value(municipio['POPULACAO'], True)}"
                    )
                    
                    # Adicionar descrição
                    desc = f"""DISTRIBUIDOR: {municipio['RAZAO SOCIAL']}
CONTATO DISTRIBUIDOR: {municipio['CONTATO DISTRIBUIDOR']}
RESPONSÁVEL: {municipio['RESPONSAVEL']}
CONTATO RESPONSÁVEL: {municipio['CONTATO RESPONSAVEL']}
ENDEREÇO: {municipio['SEDE DISTRIBUIDOR']}"""
                    placemark.description = desc
                    
                    # Aplicar estilo
                    placemark.stylemap = style_map
                    
                    # Adicionar coordenadas
                    if municipio['COORDENADAS'].upper() == 'EM BRANCO':
                        # Usar um ponto central para municípios sem coordenadas
                        placemark.coords = [(-15.7801, -47.9292)]  # Ponto em Brasília
                    else:
                        # Usar coordenadas normais para polígonos
                        coords_list = [tuple(map(float, coord.split(','))) for coord in municipio['COORDENADAS'].split()]
                        placemark.outerboundaryis = coords_list
                        placemark.tessellate = 1
    
    # Salvar KML unificado
    output_file = os.path.join(output_dir, 'distribuidores_unificado.kml')
    kml.save(output_file)
    print(f"KML unificado gerado: {output_file}")
    return output_file

def gerar_kml(df_row):
    """
    Gera o KML para uma linha do DataFrame
    """
    # Gerar cor única para a unidade
    color = gerar_cor_unica(f"{df_row['UNIDADE']}_{df_row['RAZAO SOCIAL']}")
    
    # Template do KML
    kml_template = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <n>Distribuidores</n>
    <Style id="poly-{color}-1200-77-nodesc-normal">
        <LineStyle>
            <color>FFFFFFFF</color>
            <width>0.2</width>
        </LineStyle>
        <PolyStyle>
            <color>{color}FF</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <Style id="poly-{color}-1200-77-nodesc-highlight">
        <LineStyle>
            <color>FFFFFFFF</color>
            <width>0.8</width>
        </LineStyle>
        <PolyStyle>
            <color>{color}FF</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
    </Style>
    <StyleMap id="poly-{color}-1200-77-nodesc">
        <Pair>
            <key>normal</key>
            <styleUrl>#poly-{color}-1200-77-nodesc-normal</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#poly-{color}-1200-77-nodesc-highlight</styleUrl>
        </Pair>
    </StyleMap>
    <Placemark>
        <n>{df_row['MUNICIPIO']} / {df_row['UF']}\nPOPULAÇÃO: {format_value(df_row['POPULACAO'], True)}</n>
        <description>DISTRIBUIDOR: {df_row['UNIDADE']}\nCONTATO DISTRIBUIDOR: {df_row['CONTATO DISTRIBUIDOR']}\nRESPONSÁVEL: {df_row['RESPONSAVEL']}\nCONTATO RESPONSÁVEL: {df_row['CONTATO RESPONSAVEL']}\nENDEREÇO: {df_row['SEDE DISTRIBUIDOR']}</description>
        <styleUrl>#poly-{color}-1200-77-nodesc</styleUrl>
        <Polygon>
            <outerBoundaryIs>
                <LinearRing>
                    <tessellate>1</tessellate>
                    <coordinates>{df_row['COORDENADAS']}</coordinates>
                </LinearRing>
            </outerBoundaryIs>
        </Polygon>
    </Placemark>
  </Document>
</kml>'''
    
    return kml_template

def gerar_todos_kmls(df):
    """
    Gera os KMLs para todas as linhas do DataFrame
    
    Args:
        df (pd.DataFrame): DataFrame com os dados unificados
    """
    # Criar pasta de saída se não existir
    output_dir = criar_pasta_kml()
    
    # Gerar KML para cada linha
    for _, row in df.iterrows():
        if pd.notna(row['COORDENADAS']) and row['COORDENADAS'].strip():
            # Gerar nome do arquivo
            filename = f"{row['MUNICIPIO']}_{row['UF']}.kml"
            filepath = os.path.join(output_dir, filename)
            
            # Gerar e salvar KML
            kml_content = gerar_kml(row)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(kml_content)
            
            print(f'KML gerado: {filename}')
