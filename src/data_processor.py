"""
Processador de dados para combinar informações de municípios, KML e unidades
"""
import os
import pandas as pd
import xml.etree.ElementTree as ET
import unicodedata

# Diretório onde estão os arquivos de dados
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
KML_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'kml-brasil', 'lib', '2010', 'municipios')

def remover_acentos(texto):
    """Remove acentos de um texto"""
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')

def extrair_dados_kml(caminho_kml, debug=False):
    """
    Extrai os dados de um arquivo KML
    """
    try:
        tree = ET.parse(caminho_kml)
        root = tree.getroot()
        
        # Namespace do KML
        ns = {'kml': 'http://www.opengis.net/kml/2.2'}
        
        # Debug - imprimir estrutura do XML
        if debug:
            print("\nEstrutura do XML para:", caminho_kml)
            for elem in root.iter():
                print(f"Tag: {elem.tag}, Text: {elem.text}")
        
        # Extrair informações
        placemark = root.find('.//kml:Placemark', ns)
        if placemark is not None:
            nome = placemark.find('kml:name', ns).text if placemark.find('kml:name', ns) is not None else None
            descricao = placemark.find('kml:description', ns).text if placemark.find('kml:description', ns) is not None else None
            coordenadas = placemark.find('.//kml:coordinates', ns).text.strip() if placemark.find('.//kml:coordinates', ns) is not None else None
        else:
            nome = None
            descricao = None
            coordenadas = None
        
        dados = {
            'arquivo': os.path.basename(caminho_kml),
            'uf': os.path.basename(os.path.dirname(os.path.dirname(caminho_kml))),
            'nome_municipio': nome,
            'descricao': descricao,
            'coordenadas': coordenadas
        }
        
        return dados
    except Exception as e:
        print(f"Erro ao processar KML {caminho_kml}: {str(e)}")
        return None

def processar_dados_kml():
    """
    Processa os dados dos municípios do KML e retorna DataFrame com:
    ARQUIVO, UF, MUNICIPIO, DESCRICAO, COORDENADAS
    """
    df = pd.DataFrame(columns=['ARQUIVO', 'UF', 'MUNICIPIO', 'DESCRICAO', 'COORDENADAS'])
    
    # Processar cada estado
    for estado in os.listdir(KML_DIR):
        # Diretório dos arquivos KML do estado
        dir_estado = os.path.join(KML_DIR, estado, 'kml')
        
        # Processar cada arquivo KML no diretório
        for arquivo in os.listdir(dir_estado):
            if arquivo.endswith('.kml'):
                caminho_kml = os.path.join(dir_estado, arquivo)
                
                # Extrair informações do KML
                tree = ET.parse(caminho_kml)
                root = tree.getroot()
                
                if root.tag == '{http://www.opengis.net/kml/2.2}kml':
                    # Extrair dados do KML
                    placemark = root.find('.//{http://www.opengis.net/kml/2.2}Placemark')
                    if placemark is not None:
                        nome = placemark.find('{http://www.opengis.net/kml/2.2}name').text
                        descricao = placemark.find('{http://www.opengis.net/kml/2.2}description').text
                        coordenadas = placemark.find('.//{http://www.opengis.net/kml/2.2}coordinates').text.strip()
                        
                        # Adicionar ao DataFrame
                        df.loc[len(df)] = {
                            'ARQUIVO': arquivo,
                            'UF': estado,
                            'MUNICIPIO': nome,
                            'DESCRICAO': descricao,
                            'COORDENADAS': coordenadas
                        }
    
    # Criar coluna chave MUNICIPIO_UF
    df['MUNICIPIO_UF'] = df.apply(lambda row: f"{remover_acentos(row['MUNICIPIO'])}_{row['UF']}".upper().replace(' ', '_'), axis=1)
    
    # Salvar em Excel
    output_file = os.path.join(DATA_DIR, 'output', 'dados_municipios_kml.xlsx')
    df.to_excel(output_file, index=False)
    
    return df

def processar_cidades_ale():
    """
    Processa as cidades da ALE com as colunas:
    MUNICIPIO, UF, UNIDADE, RAZAO SOCIAL
    """
    # Carregar dados do Excel da aba CIDADES ALE
    caminho_excel = os.path.join(DATA_DIR, 'BRUNO.xlsx')
    df_ale = pd.read_excel(caminho_excel, sheet_name='CIDADES ALE')
    
    # Criar coluna chave MUNICIPIO_UF
    df_ale['MUNICIPIO_UF'] = df_ale.apply(lambda row: f"{remover_acentos(row['MUNICIPIO'])}_{row['UF']}".upper().replace(' ', '_'), axis=1)
    
    # Salvar em Excel
    output_file = os.path.join(DATA_DIR, 'output', 'cidades_ale.xlsx')
    df_ale.to_excel(output_file, index=False)
    
    return df_ale

def processar_base_tratada():
    """
    Processa os dados da aba BASE TRATADA
    """
    # Carregar dados do Excel da aba BASE TRATADA
    caminho_excel = os.path.join(DATA_DIR, 'BRUNO.xlsx')
    df_base = pd.read_excel(caminho_excel, sheet_name='BASE TRATADA')
    
    # Criar coluna chave MUNICIPIO_UF
    df_base['MUNICIPIO_UF'] = df_base.apply(lambda row: f"{remover_acentos(row['MUNICIPIO'])}_{row['UF']}".upper().replace(' ', '_'), axis=1)
    
    # Salvar em Excel
    output_file = os.path.join(DATA_DIR, 'output', 'base_tratada.xlsx')
    df_base.to_excel(output_file, index=False)
    
    return df_base

def processar_distribuidores_ale():
    """
    Processa os dados da aba DISTRIBUIDORES ALE
    """
    # Carregar dados do Excel da aba DISTRIBUIDORES ALE
    caminho_excel = os.path.join(DATA_DIR, 'BRUNO.xlsx')
    df_dist = pd.read_excel(caminho_excel, sheet_name='DISTRIBUIDORES ALE')
    print("Colunas dos distribuidores:", df_dist.columns.tolist())
    return df_dist

def unificar_bases(df_kml, df_ale, df_base):
    """
    Unifica as bases usando MUNICIPIO_UF como chave
    """
    # Primeiro merge: KML com ALE
    df_merge = pd.merge(df_kml, df_ale, on='MUNICIPIO_UF', how='outer', suffixes=('', '_ale'))
    
    # Remover colunas duplicadas do primeiro merge
    colunas_drop = [col for col in df_merge.columns if col.endswith('_ale')]
    df_merge = df_merge.drop(columns=colunas_drop)
    
    # Segundo merge: com BASE TRATADA
    df_final = pd.merge(df_merge, df_base, on='MUNICIPIO_UF', how='outer', suffixes=('', '_base'))
    
    # Remover colunas duplicadas do segundo merge
    colunas_drop = [col for col in df_final.columns if col.endswith('_base')]
    df_final = df_final.drop(columns=colunas_drop)
    
    # Preencher valores vazios com "Em Branco"
    df_final = df_final.fillna("Em Branco")
    
    # Criar coluna TIPO UNIDADE baseado na UNIDADE
    def get_tipo_unidade(unidade):
        if unidade == "Em Branco":
            return "Em Branco"
        elif "FILIAL" in unidade.upper():
            return "FILIAL"
        elif "REGIONAL" in unidade.upper():
            return "REGIONAL"
        else:
            return unidade
    
    df_final['TIPO UNIDADE'] = df_final['UNIDADE'].apply(get_tipo_unidade)
    
    # Ordenar colunas para melhor visualização
    colunas_ordem = [
        'MUNICIPIO', 'UF', 'MUNICIPIO_UF', 
        'UNIDADE', 'TIPO UNIDADE', 'RAZAO SOCIAL',
        'POPULACAO', 'RESPONSAVEL', 'CONTATO RESPONSAVEL',
        'SEDE DISTRIBUIDOR', 'CONTATO DISTRIBUIDOR',
        'DESCRICAO', 'COORDENADAS'
    ]
    df_final = df_final[colunas_ordem]
    
    # Salvar resultado
    output_file = os.path.join(DATA_DIR, 'output', 'base_unificada.xlsx')
    df_final.to_excel(output_file, index=False)
    
    return df_final