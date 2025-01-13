"""
Script principal para processar os dados dos municípios
"""
import os
import shutil
from src.data_processor import processar_dados_kml, processar_cidades_ale, processar_base_tratada, unificar_bases
from src.kml_generator import gerar_kml_por_tipo_unidade, gerar_kml_unificado

def copiar_para_dist():
    """
    Copia todo o conteúdo da pasta data para dist/data
    """
    # Caminhos
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    dist_dir = os.path.join(os.path.dirname(__file__), 'dist', 'data')
    
    # Criar pasta dist/data se não existir
    os.makedirs(dist_dir, exist_ok=True)
    
    # Remover tudo que existe em dist/data
    for item in os.listdir(dist_dir):
        item_path = os.path.join(dist_dir, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            shutil.rmtree(item_path)
    
    # Copiar tudo de data para dist/data
    for item in os.listdir(data_dir):
        src = os.path.join(data_dir, item)
        dst = os.path.join(dist_dir, item)
        
        if os.path.isfile(src):
            shutil.copy2(src, dst)
        elif os.path.isdir(src):
            shutil.copytree(src, dst)
    
    print(f"Arquivos copiados para: {dist_dir}")

def main():
    """
    Função principal que processa os dados e gera os KMLs
    """
    try:
        print("Iniciando processamento dos dados...")
        
        # Processar as bases de dados
        df_kml = processar_dados_kml()
        df_ale = processar_cidades_ale()
        df_base = processar_base_tratada()
        
        print("Unificando bases de dados...")
        # Unificar as bases
        df_unificado = unificar_bases(df_kml, df_ale, df_base)
        
        print("Gerando arquivos KML...")
        # Gerar KML por tipo de unidade
        gerar_kml_por_tipo_unidade(df_unificado)
        
        # Gerar KML unificado
        gerar_kml_unificado(df_unificado)
        
        print("\nCopiando arquivos para dist/data...")
        copiar_para_dist()
        
        print("\nProcessamento concluído com sucesso!")
        print("Os arquivos foram gerados em:")
        print(f"1. {os.path.join(os.path.dirname(__file__), 'data')}")
        print(f"2. {os.path.join(os.path.dirname(__file__), 'dist', 'data')}")
        
    except Exception as e:
        print(f"Erro durante o processamento: {str(e)}")
        raise

if __name__ == "__main__":
    main()
