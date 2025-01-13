import os
import sys
from enum import Enum

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Adicionar o diretório src ao PYTHONPATH
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.append(src_dir)

import os
import logging
import flet as ft
import pandas as pd
from datetime import datetime
import sys
import os

# Adiciona o diretório atual ao PYTHONPATH
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from kml_generator import gerar_kml_por_tipo_unidade, gerar_kml_unificado
from config import DATA_DIR
from utils import format_value

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AcaoHistorico(Enum):
    CRIACAO = "CRIAÇÃO"
    EDICAO = "EDIÇÃO"
    EXCLUSAO = "EXCLUSÃO"

class DataManager:
    def __init__(self):
        logging.info("Iniciando carregamento dos dados...")
        # Carregar a base unificada
        data_path = os.path.join(os.path.dirname(DATA_DIR), 'data', 'output', 'base_unificada.xlsx')
        logging.info(f"Tentando carregar arquivo: {data_path}")
        
        try:
            self.df = pd.read_excel(data_path)
            # Adicionar coluna de histórico se não existir
            if 'HISTORICO' not in self.df.columns:
                self.df['HISTORICO'] = ''
            logging.info(f"Dados carregados com sucesso. Shape: {self.df.shape}")
            logging.info(f"Colunas disponíveis: {list(self.df.columns)}")
        except Exception as e:
            logging.error(f"Erro ao carregar dados: {str(e)}")
            raise
            
        self.filtered_df = self.df.copy()
        self.page_size = 10
        self.current_page = 0
        self.has_changes = False
        
        # Definir colunas editáveis
        self.editable_columns = [
            'TIPO UNIDADE', 'UNIDADE', 'RAZAO SOCIAL',
            'RESPONSAVEL', 'CONTATO RESPONSAVEL',
            'SEDE DISTRIBUIDOR', 'CONTATO DISTRIBUIDOR'
        ]
        
        # Definir colunas que nunca podem ser editadas
        self.never_editable = [
            'POPULACAO', 'COORDENADAS', 'DESCRICAO', 
            'MUNICIPIO', 'UF', 'MUNICIPIO_UF', 'HISTORICO'
        ]
        
        # Definir colunas originais que não podem ser excluídas
        self.non_deletable_columns = [
            'POPULACAO', 'COORDENADAS', 'DESCRICAO', 
            'MUNICIPIO', 'UF', 'MUNICIPIO_UF', 'HISTORICO',
            'TIPO UNIDADE', 'UNIDADE', 'RAZAO SOCIAL',
            'RESPONSAVEL', 'CONTATO RESPONSAVEL',
            'SEDE DISTRIBUIDOR', 'CONTATO DISTRIBUIDOR'
        ]
        
        # Ordenar as colunas: primeiro as não editáveis, depois as editáveis, por fim as criadas pelo usuário
        self._reorder_columns()
        
    def _reorder_columns(self):
        """Reordena as colunas do DataFrame"""
        # Pegar todas as colunas atuais
        all_columns = list(self.df.columns)
        
        # Separar em categorias
        never_editable = [col for col in all_columns if col in self.never_editable]
        editable = [col for col in all_columns if col in self.editable_columns]
        user_created = [col for col in all_columns if col not in never_editable and col not in editable]
        
        # Nova ordem: não editáveis -> editáveis -> criadas pelo usuário
        new_order = never_editable + editable + user_created
        
        # Aplicar nova ordem
        self.df = self.df[new_order]
        self.filtered_df = self.filtered_df[new_order]
        
    def registrar_historico(self, row_idx, mensagem, acao: AcaoHistorico):
        """Registra uma ação no histórico"""
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        historico = self.filtered_df.iloc[row_idx]['HISTORICO'] if pd.notna(self.filtered_df.iloc[row_idx]['HISTORICO']) else ''
        novo_registro = f"{timestamp} - {mensagem} [{acao.value}]\n"
        self.filtered_df.at[row_idx, 'HISTORICO'] = historico + novo_registro
        
    def update_cell(self, row_idx, col_name, new_value):
        """Atualiza o valor de uma célula e registra no histórico"""
        if col_name in self.never_editable:
            return False
            
        old_value = self.filtered_df.iloc[row_idx][col_name]
        if old_value != new_value:
            mensagem = f"{col_name}: '{old_value}' -> '{new_value}'"
            self.registrar_historico(row_idx, mensagem, AcaoHistorico.EDICAO)
            
            # Atualizar valor
            self.filtered_df.at[row_idx, col_name] = new_value
            self.has_changes = True
            return True
        return False
    
    def add_column(self, col_name):
        """Adiciona uma nova coluna e registra no histórico"""
        if col_name not in self.df.columns:
            mensagem = f"Coluna '{col_name}'"
            # Registrar no histórico para todas as linhas
            for idx in range(len(self.filtered_df)):
                self.registrar_historico(idx, mensagem, AcaoHistorico.CRIACAO)
            
            # Adicionar nova coluna
            self.filtered_df[col_name] = ''
            self.df[col_name] = ''
            
            # Reordenar as colunas para manter o padrão
            self._reorder_columns()
            
            self.has_changes = True
            return True
        return False
    
    def delete_column(self, col_name):
        """Remove uma coluna e registra no histórico"""
        if col_name in self.never_editable:
            return False
            
        if col_name in self.df.columns:
            mensagem = f"Coluna '{col_name}'"
            # Registrar no histórico para todas as linhas
            for idx in range(len(self.filtered_df)):
                self.registrar_historico(idx, mensagem, AcaoHistorico.EXCLUSAO)
            
            # Remover coluna
            self.filtered_df.drop(columns=[col_name], inplace=True)
            self.df.drop(columns=[col_name], inplace=True)
            if col_name in self.editable_columns:
                self.editable_columns.remove(col_name)
            self.has_changes = True
            return True
        return False

    def is_user_created_column(self, column):
        """Verifica se a coluna foi criada pelo usuário"""
        return column not in self.non_deletable_columns
    
    def is_deletable_column(self, column):
        """Verifica se a coluna pode ser excluída"""
        return column not in self.non_deletable_columns

    def search_data(self, search_term):
        """Filtra os dados por unidade ou razão social"""
        logging.info(f"Realizando busca por: {search_term}")
        if not search_term:
            self.filtered_df = self.df.copy()
            logging.info("Busca vazia, mostrando todos os dados")
        else:
            search_term = search_term.lower()
            # Verificar se as colunas existem antes de tentar filtrar
            unidade_col = next((col for col in self.df.columns if 'UNIDADE' in col.upper()), None)
            razao_col = next((col for col in self.df.columns if 'RAZAO' in col.upper()), None)
            
            mask = pd.Series(False, index=self.df.index)
            if unidade_col:
                mask |= self.df[unidade_col].astype(str).str.lower().str.contains(search_term, na=False)
            if razao_col:
                mask |= self.df[razao_col].astype(str).str.lower().str.contains(search_term, na=False)
            
            self.filtered_df = self.df[mask]
            logging.info(f"Encontrados {len(self.filtered_df)} resultados")
        self.current_page = 0  # Resetar para a primeira página

    def get_page_data(self):
        """Retorna os dados da página atual"""
        logging.info(f"Obtendo dados da página {self.current_page}")
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        return self.filtered_df.iloc[start_idx:end_idx]

    def total_pages(self):
        return len(self.filtered_df) // self.page_size + (1 if len(self.filtered_df) % self.page_size > 0 else 0)
        
    def save_data(self):
        """Salva os dados e atualiza os dados originais"""
        try:
            # Garantir que a coluna HISTORICO existe no DataFrame principal
            if 'HISTORICO' not in self.df.columns:
                self.df['HISTORICO'] = ''
            
            # Copiar alterações do filtered_df para o df principal
            for col in self.filtered_df.columns:
                self.df[col] = self.filtered_df[col]
            
            # Reordenar as colunas antes de salvar
            self._reorder_columns()
            
            # Salvar no arquivo
            output_path = os.path.join(DATA_DIR, 'output', 'base_unificada.xlsx')
            logging.info(f"Salvando dados em: {output_path}")
            logging.info(f"Colunas sendo salvas: {list(self.df.columns)}")
            self.df.to_excel(output_path, index=False)
            self.has_changes = False
            logging.info("Dados salvos com sucesso")
        except Exception as e:
            logging.error(f"Erro ao salvar dados: {str(e)}")
            raise

def main(page: ft.Page):
    logging.info("Iniciando aplicação...")
    page.title = "Gerenciador de Contratos Itaiquara Alimentos SA"
    page.theme_mode = "light"
    page.padding = 20
    page.window_width = 1200
    page.window_height = 800
    page.window_maximized = True
    page.expand = True

    # Função para alternar entre dark/light mode
    def toggle_theme(e):
        page.theme_mode = "dark" if page.theme_mode == "light" else "light"
        theme_button.icon = ft.icons.DARK_MODE if page.theme_mode == "light" else ft.icons.LIGHT_MODE
        page.update()

    # Botão de alternar tema
    theme_button = ft.IconButton(
        icon=ft.icons.DARK_MODE if page.theme_mode == "light" else ft.icons.LIGHT_MODE,
        on_click=toggle_theme,
        tooltip="Alternar tema"
    )

    # Barra superior com título e botão de tema
    title_row = ft.Row(
        [
            ft.Container(width=40),  # Espaçamento à esquerda
            ft.Text("Gerenciador de Contratos Itaiquara Alimentos SA", size=30, weight=ft.FontWeight.BOLD, expand=True, text_align=ft.TextAlign.CENTER),
            theme_button
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
    )

    page.add(title_row)

    # Referências para os controles
    search_field = ft.Ref[ft.TextField]()
    new_column_name = ft.Ref[ft.TextField]()
    kml_button = ft.Ref[ft.ElevatedButton]()
    
    # Indicador de carregamento
    loading_container = ft.Container(
        content=ft.Column(
            [
                ft.ProgressRing(),
                ft.Text("Carregando dados...")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        ),
        alignment=ft.alignment.center
    )
    page.controls.append(loading_container)
    page.update()
    
    try:
        logging.info("Criando gerenciador de dados...")
        data_manager = DataManager()
        
        # Remover indicador de carregamento assim que os dados forem carregados
        if loading_container in page.controls:
            page.controls.remove(loading_container)
            page.update()
        
        def create_table():
            logging.info("Criando tabela...")
            # Criar cabeçalho da tabela
            columns = [
                ft.DataColumn(
                    ft.Text("#", size=10, weight=ft.FontWeight.BOLD),
                    numeric=True
                )
            ]
            columns.extend([
                ft.DataColumn(
                    ft.Row(
                        [
                            ft.Text(col, size=10, weight=ft.FontWeight.BOLD, color=ft.colors.BLUE if col in data_manager.never_editable else None),
                            ft.IconButton(
                                ft.icons.DELETE,
                                icon_color=ft.colors.RED_400,
                                icon_size=16,
                                tooltip="Excluir coluna",
                                on_click=lambda e, col=col: delete_column(col),
                            ) if data_manager.is_deletable_column(col) else ft.Container(width=0)
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5
                    )
                ) for col in data_manager.filtered_df.columns
            ])
            
            table = ft.DataTable(
                columns=columns,
                rows=[],
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=10,
                vertical_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                horizontal_lines=ft.border.BorderSide(1, ft.colors.GREY_400),
                sort_ascending=True,
            )

            # Adicionar linhas à tabela
            logging.info(f"Obtendo dados da página {data_manager.current_page}")
            page_data = data_manager.get_page_data()
            logging.info(f"Adicionando {len(page_data)} linhas à tabela")
            
            for idx, row in page_data.iterrows():
                cells = [
                    ft.DataCell(
                        ft.Container(
                            content=ft.Text(
                                str(idx + 1),
                                size=10,
                                text_align=ft.TextAlign.CENTER
                            ),
                            alignment=ft.alignment.center
                        )
                    )
                ]
                for col in data_manager.filtered_df.columns:
                    value = str(row[col]) if pd.notna(row[col]) else ""
                    # Verificar se a coluna é editável
                    is_editable = (col in data_manager.editable_columns or col not in data_manager.df.columns[:len(data_manager.editable_columns)]) and col not in data_manager.never_editable
                    
                    if is_editable:
                        cell_content = ft.Container(
                            content=ft.TextField(
                                value=value,
                                border=ft.InputBorder.NONE,
                                height=30,
                                width=120,
                                text_size=10,
                                text_align=ft.TextAlign.CENTER,
                                tooltip=value,  # Mostra o texto completo ao passar o mouse
                                on_submit=lambda e, i=idx, c=col: (
                                    data_manager.update_cell(i, c, e.control.value.upper() if e.control.value else ""),
                                    update_table()  # Atualiza a tabela após a edição
                                ),
                                on_blur=lambda e, i=idx, c=col: (
                                    data_manager.update_cell(i, c, e.control.value.upper() if e.control.value else ""),
                                    update_table()  # Atualiza a tabela quando perder o foco
                                )
                            ),
                            alignment=ft.alignment.center
                        )
                    else:
                        cell_content = ft.Container(
                            content=ft.Text(
                                value,
                                size=10,
                                width=150,
                                tooltip=value,  # Mostra o texto completo ao passar o mouse
                                overflow=ft.TextOverflow.ELLIPSIS,
                                no_wrap=True,
                                selectable=True,
                                text_align=ft.TextAlign.CENTER,
                                color=ft.colors.BLUE
                            ),
                            alignment=ft.alignment.center
                        )
                    
                    cells.append(ft.DataCell(cell_content))
                table.rows.append(ft.DataRow(cells=cells))
            
            logging.info("Tabela criada com sucesso")
            return table

        def update_table():
            logging.info("Atualizando tabela...")
            page_info.value = f"Página {data_manager.current_page + 1} de {data_manager.total_pages()}"
            table_container.content = create_table()
            page.update()
            logging.info("Tabela atualizada")
            
        def next_page(e, direction):
            new_page = data_manager.current_page + direction
            if 0 <= new_page < data_manager.total_pages():
                data_manager.current_page = new_page
                update_table()
        
        # Função para mudar o número de itens por página
        def change_page_size(e):
            # Desmarca os outros checkboxes
            for checkbox in page_size_checkboxes:
                if checkbox != e.control:
                    checkbox.value = False
            
            if e.control.value:  # Se foi marcado
                data_manager.page_size = int(e.control.data)
                data_manager.current_page = 0  # Volta para a primeira página
                update_table()
            else:  # Se foi desmarcado, volta para o valor padrão (50)
                e.control.value = True  # Mantém marcado
                page.update()
        
        # Checkboxes para selecionar número de itens por página
        page_size_options = [5, 10, 25, 50, 100]
        page_size_checkboxes = [
            ft.Checkbox(
                label=str(size),
                value=size == data_manager.page_size,
                data=size,  # Guarda o valor numérico
                on_change=change_page_size
            ) for size in page_size_options
        ]
        
        page_size_row = ft.Row(
            [
                ft.Text("Itens por página:", size=12),
                *page_size_checkboxes
            ],
            spacing=5
        )
        
        # Controles de paginação
        prev_btn = ft.ElevatedButton(
            "Anterior",
            on_click=lambda e: next_page(e, -1),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            )
        )
        next_btn = ft.ElevatedButton(
            "Próxima",
            on_click=lambda e: next_page(e, 1),
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            )
        )
        page_info = ft.Text(f"Página {data_manager.current_page + 1} de {data_manager.total_pages()}")
        
        def go_to_page(e):
            try:
                page_number = int(page_number_input.value)
                if 1 <= page_number <= data_manager.total_pages():
                    data_manager.current_page = page_number - 1
                    update_table()
                else:
                    page.show_snack_bar(
                        ft.SnackBar(content=ft.Text(f"Página deve estar entre 1 e {data_manager.total_pages()}"))
                    )
            except ValueError:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Por favor, digite um número válido"))
                )

        # Campo para ir para página específica
        page_number_input = ft.TextField(
            label="Página",
            width=100,
            height=35,
            text_size=10,
            on_submit=go_to_page
        )
        
        go_btn = ft.ElevatedButton(
            "Ir",
            on_click=go_to_page,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            )
        )
        
        pagination = ft.Row(
            [
                page_size_row,  # Adicionando a linha de checkboxes
                ft.VerticalDivider(width=20),  # Separador
                prev_btn,
                page_info,
                next_btn,
                ft.VerticalDivider(width=20),  # Separador
                page_number_input,
                go_btn
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        )

        # Campo de busca
        search_term = ft.TextField(
            ref=search_field,
            label="Buscar por unidade ou razão social",
            width=400,
            height=35,
            on_submit=lambda e: (data_manager.search_data(e.control.value), update_table())
        )
        
        def search_data(e):
            data_manager.search_data(search_term.value)
            update_table()
            page.update()

        search_btn = ft.ElevatedButton(
            "Buscar",
            on_click=search_data,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
            )
        )

        # Controles
        new_column_name = ft.TextField(
            ref=new_column_name,
            label="Nome da nova coluna",
            width=200,
            height=35
        )
        
        def save_changes(e=None):
            """Salva as alterações no arquivo"""
            try:
                data_manager.save_data()
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Dados salvos com sucesso!"))
                )
            except Exception as ex:
                logging.error(f"Erro ao salvar dados: {str(ex)}")
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Erro ao salvar dados: {str(ex)}"))
                )
        
        def generate_kml():
            try:
                if data_manager.has_changes:
                    # Mostra diálogo de confirmação
                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text("Existem alterações não salvas. Por favor, salve as alterações antes de gerar o KML."),
                            action="Salvar",
                            action_color=ft.colors.BLUE,
                            on_action=lambda e: save_changes()
                        )
                    )
                    return
                
                # Gera os KMLs por tipo
                arquivos_tipo = gerar_kml_por_tipo_unidade(data_manager.df)
                
                # Gera o KML unificado
                arquivo_unificado = gerar_kml_unificado(data_manager.df)
                
                # Lista todos os arquivos gerados
                arquivos = [os.path.basename(f) for f in arquivos_tipo + [arquivo_unificado]]
                arquivos_str = "\n".join(arquivos)
                
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"KMLs gerados com sucesso!\nArquivos gerados:\n{arquivos_str}"))
                )
            except Exception as e:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Erro ao gerar KML: {str(e)}"))
                )

        def export_to_excel(e):
            try:
                # Obter o caminho da pasta Downloads
                downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
                
                # Criar nome do arquivo com timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_filename = os.path.join(downloads_path, f'exportacao_{timestamp}.xlsx')
                
                # Exportar o DataFrame atual (filtrado ou não)
                current_df = data_manager.filtered_df if len(data_manager.filtered_df) < len(data_manager.df) else data_manager.df
                current_df.to_excel(export_filename, index=False)
                
                page.show_snack_bar(
                    ft.SnackBar(
                        content=ft.Text(f"Dados exportados para Downloads: {os.path.basename(export_filename)}"),
                        action="OK"
                    )
                )
            except Exception as e:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Erro ao exportar: {str(e)}"))
                )

        # Linha 1: Busca
        search_row = ft.Row(
            [
                search_term,
                search_btn
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        # Linha 2: Adicionar coluna e salvar
        edit_row = ft.Row(
            [
                new_column_name,
                ft.ElevatedButton(
                    "Adicionar Coluna",
                    on_click=lambda e: add_column(e),
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                ),
                ft.ElevatedButton(
                    "Salvar Alterações",
                    on_click=save_changes,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=10),
                    )
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        # Linha 3: Botões KML e Exportar
        action_row = ft.Row(
            [
                ft.ElevatedButton(
                    "Gerar KML",
                    ref=kml_button,
                    on_click=lambda e: generate_kml(),
                ),
                ft.ElevatedButton(
                    "Exportar para Excel",
                    on_click=export_to_excel,
                    icon=ft.icons.FILE_DOWNLOAD,
                    tooltip="Exportar dados atuais para Excel"
                )
            ],
            alignment=ft.MainAxisAlignment.START,
            spacing=10
        )

        def add_column(e):
            if new_column_name.value:
                # Converter nome da coluna para maiúsculas
                column_name = new_column_name.value.upper()
                data_manager.add_column(column_name)
                
                # Limpar o campo e atualizar a tabela
                new_column_name.value = ""
                update_table()
                page.update()

        def delete_column(column_name):
            if data_manager.is_deletable_column(column_name):
                # Excluir a coluna
                data_manager.delete_column(column_name)
                
                # Atualizar a tabela
                update_table()
                page.update()
                
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text(f"Coluna '{column_name}' excluída com sucesso!"))
                )
            else:
                page.show_snack_bar(
                    ft.SnackBar(content=ft.Text("Esta coluna não pode ser excluída!"))
                )
        
        # Container dos controles
        controls = ft.Column(
            [
                search_row,
                edit_row,
                action_row  # Adicionando a nova linha de botões
            ],
            spacing=20
        )
        
        # Container para a tabela
        table_container = ft.Container(
            content=create_table(),
            padding=20,
            border=ft.border.all(1, "grey"),
            border_radius=10,
            margin=ft.margin.only(top=20),
            expand=True
        )

        # Primeiro envolver em um Row para scroll horizontal
        horizontal_scroll = ft.Row(
            [table_container],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True
        )

        # Depois envolver em uma Column com altura fixa para scroll vertical
        scrollable_container = ft.Column(
            [horizontal_scroll],
            scroll=ft.ScrollMode.ALWAYS,
            expand=True,
            height=500
        )

        # Remover indicador de carregamento
        if loading_container in page.controls:
            page.controls.remove(loading_container)
        
        # Adicionar todos os elementos
        page.controls.append(controls)
        page.controls.append(scrollable_container)
        page.controls.append(pagination)
        page.update()
        
    except Exception as e:
        # Em caso de erro, remover o loading e mostrar a mensagem de erro
        if loading_container in page.controls:
            page.controls.remove(loading_container)
        status_text = ft.Text(f"Erro ao carregar dados: {str(e)}")
        page.controls.append(status_text)
        page.update()

if __name__ == "__main__":
    ft.app(target=main)
