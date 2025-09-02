from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QSpinBox,
                           QDoubleSpinBox, QDialog, QFrame, QToolButton, QGroupBox,
                           QFileDialog, QCheckBox, QProgressDialog, QGridLayout, QProgressBar, QCompleter)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush, QPixmap
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from collections import defaultdict
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import csv
import qtawesome as qta
import math
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager 

# Coloque esta nova classe no início do arquivo estoque_window.py

# Coloque esta nova classe no início do seu arquivo estoque_window.py
# (Substitua a classe CustomMessageBox existente)

# Cole esta classe no início do seu arquivo ui/estoque_window.py, 
# substituindo a versão anterior da AlertDialog.

class AlertDialog(QDialog):
    """Caixa de diálogo com o estilo sutil da tela de perfil."""
    def __init__(self, parent, title, message, alert_type='info', buttons=QMessageBox.Ok, theme_colors=None):
        super().__init__(parent)
        self.theme_colors = theme_colors if theme_colors is not None else {}
        self.drag_position = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        type_info = {
            'success':  {'icon': 'check', 'color': '#28a745'},
            'warning':  {'icon': 'estoque_baixo', 'color': '#ffc107'},
            'error':    {'icon': 'delete', 'color': '#dc3545'},
            'question': {'icon': 'question', 'color': '#17a2b8'},
            'info':     {'icon': 'sobre', 'color': self.theme_colors.get('accent_color', '#007AFF')},
        }.get(alert_type, {'icon': 'sobre', 'color': '#007AFF'})

        self.accent_color = type_info['color']
        self.icon_name = type_info['icon']
        
        self._setup_ui(title, message, buttons)

    def _setup_ui(self, title, message, buttons):
        self.setMinimumWidth(400)
        
        container = QFrame(self)
        container.setObjectName("mainContainer")
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Cabeçalho Sutil
        self.header = QFrame(); self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 15, 10, 15)
        
        header_title_label = QLabel(title)
        header_title_label.setObjectName("headerTitleLabel")
        
        close_button = QPushButton()
        close_button.setObjectName("controlButton")
        close_button.setFixedSize(28, 28)
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors.get('text_secondary', '#666')))
        close_button.clicked.connect(self.reject)
        
        header_layout.addWidget(header_title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        main_layout.addWidget(self.header)

        # Corpo
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(25, 20, 25, 25)
        body_layout.setSpacing(20)

        # Ícone e Subtítulo
        subtitle_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(IconManager.get_icon(self.icon_name, color=self.accent_color).pixmap(24, 24))
        subtitle_label = QLabel(title)
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_layout.addWidget(icon_label)
        subtitle_layout.addWidget(subtitle_label)
        subtitle_layout.addStretch()
        
        # Mensagem Principal
        message_label = QLabel(message); message_label.setWordWrap(True); message_label.setObjectName("messageLabel")
        
        # Botões
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if buttons & QMessageBox.Yes:
            button_layout.addWidget(self._create_button("Sim", lambda: self.done(QMessageBox.Yes), is_primary=True))
        if buttons & QMessageBox.Ok:
            button_layout.addWidget(self._create_button("OK", self.accept, is_primary=True))
        if buttons & QMessageBox.No:
            button_layout.addWidget(self._create_button("Não", self.reject))
        if buttons & QMessageBox.Cancel:
            button_layout.addWidget(self._create_button("Cancelar", self.reject))
        
        body_layout.addLayout(subtitle_layout)
        body_layout.addWidget(message_label)
        body_layout.addLayout(button_layout)
        main_layout.addWidget(body)
        
        base_layout = QVBoxLayout(self)
        base_layout.addWidget(container)
        self.apply_styles()

    def _create_button(self, text, on_click, is_primary=False):
        btn = QPushButton(text)
        btn.clicked.connect(on_click)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("primaryButton" if is_primary else "secondaryButton")
        return btn
        
    def apply_styles(self):
        colors = self.theme_colors
        style = f"""
            #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }}
            #header {{ border-bottom: 1px solid {colors.get('border_color', '#ccc')}; }}
            #headerTitleLabel {{ color: {colors.get('text_color', '#000')}; font-weight: bold; }}
            #subtitleLabel {{ color: {colors.get('text_color', '#000')}; font-size: 14pt; font-weight: bold; }}
            #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }}
            #controlButton {{ background: transparent; border: none; border-radius: 14px; }}
            #controlButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }}
            QPushButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; min-width: 90px;}}
            #primaryButton {{ background-color: {self.accent_color}; color: white; border: none; }}
            #secondaryButton {{ background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }}
            #secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }}
        """
        self.setStyleSheet(style)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

# Adicione esta importação extra no topo do seu arquivo, junto com as outras
from PyQt5.QtWidgets import QProgressBar

# Cole esta nova classe abaixo da classe AlertDialog
class ThemedProgressDialog(QDialog):
    """Um diálogo de progresso customizado e temático."""
    canceled = pyqtSignal()

    def __init__(self, parent, title, message, theme_colors):
        super().__init__(parent)
        self.theme_colors = theme_colors if theme_colors is not None else {}
        self.drag_position = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self._setup_ui(title, message)
        self.apply_styles()

    def _setup_ui(self, title, message):
        self.setMinimumWidth(400)
        
        container = QFrame(self)
        container.setObjectName("mainContainer")
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Cabeçalho
        self.header = QFrame(); self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(20, 15, 10, 15)
        title_label = QLabel(title); title_label.setObjectName("headerTitleLabel")
        header_layout.addWidget(title_label)
        main_layout.addWidget(self.header)

        # Corpo
        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(25, 20, 25, 25)
        body_layout.setSpacing(15)

        message_label = QLabel(message); message_label.setWordWrap(True); message_label.setObjectName("messageLabel")
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject) # Usar reject para fechar e sinalizar
        button_layout.addWidget(cancel_button)

        body_layout.addWidget(message_label)
        body_layout.addWidget(self.progress_bar)
        body_layout.addLayout(button_layout)
        main_layout.addWidget(body)
        
        base_layout = QVBoxLayout(self)
        base_layout.addWidget(container)

    def apply_styles(self):
        colors = self.theme_colors
        style = f"""
            #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }}
            #header {{ border-bottom: 1px solid {colors.get('border_color', '#ccc')}; }}
            #headerTitleLabel {{ color: {colors.get('text_color', '#000')}; font-weight: bold; }}
            #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }}
            QPushButton#secondaryButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }}
            QPushButton#secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }}
            QProgressBar {{ border: 1px solid {colors.get('border_color', '#ccc')}; border-radius: 8px; padding: 1px; text-align: center; background-color: {colors.get('bg_color', '#eee')}; color: {colors.get('text_color', '#000')}; }}
            QProgressBar::chunk {{ background-color: {colors.get('accent_color', '#007AFF')}; border-radius: 7px; }}
        """
        self.setStyleSheet(style)

    def setValue(self, value):
        self.progress_bar.setValue(value)

    def reject(self):
        self.canceled.emit() # Emite o sinal de cancelamento
        super().reject() # Fecha a janela

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

# ================================================================= #
#       CLASSE CSV IMPORT WORKER TOTALMENTE IMPLEMENTADA            #
# ================================================================= #
# ================================================================= #
#       CLASSE CSV IMPORT WORKER - CORREÇÃO FINAL (FLOAT)           #
# ================================================================= #
# Substitua a sua classe CsvImportWorker inteira por esta

class CsvImportWorker(QThread):
    """
    Executa a importação de CSV em uma thread para não congelar a UI.
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, int, list)

    def __init__(self, db_path, file_path):
        super().__init__()
        self.db_path = db_path
        self.file_path = file_path
        self.local_db = None

    def run(self):
        produtos_importados = 0
        produtos_erro = 0
        erros_detalhes = []

        try:
            self.local_db = DatabaseManager(self.db_path)

            with open(self.file_path, 'r', encoding='utf-8') as f:
                linhas = list(f)
                total_linhas = max(1, len(linhas) - 1)

            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                self.local_db.begin_transaction() 

                for i, row in enumerate(reader):
                    try:
                        if not row.get('nome', '').strip():
                            raise ValueError("Nome do produto é obrigatório")

                        is_fracionado = int(row.get('fracionado', '0') or 0)
                        
                        produto_data = {
                            'codigo_barras': row.get('codigo_barras', '').strip(),
                            'nome': row.get('nome', '').strip(),
                            'descricao': row.get('descricao', ''),
                            'quantidade': self._extrair_quantidade_do_estoque_detalhado(row.get('estoque_detalhado', '0')),
                            'estoque_minimo': int(row.get('estoque_minimo', '0') or 0),
                            'preco_compra': self._extrair_preco(row.get('preco_compra', '0')),
                            'margem_lucro': self._extrair_margem(row.get('margem', '0')),
                            'preco_venda': self._extrair_preco(row.get('preco_venda', '0')),
                            'data_validade': self._formatar_data_validade(row.get('validade', '')),
                            'localizacao': row.get('localizacao', '').strip() or None,
                            'fornecedor_id': None,
                            'categoria': row.get('categoria', '').strip() or None,
                            'fracionado': is_fracionado,
                            'unidade_medida': row.get('unidade_medida', 'unidade').strip() if is_fracionado else 'unidade',
                            'qtd_por_embalagem': int(row.get('qtd_por_embalagem', '1') or 1) if is_fracionado else 1,
                            'preco_unitario_fracao': self._extrair_preco(row.get('preco_unitario_fracao', '0')) if is_fracionado else 0.0,
                            
                            # --- A CORREÇÃO ESTÁ AQUI ---
                            # Trocamos int() por float() para aceitar números decimais como 0.5
                            'estoque_fracionado': float(row.get('estoque_fracionado', '0.0') or 0.0) if is_fracionado else 0.0
                        }
                        
                        produto_existente = None
                        if produto_data['codigo_barras']:
                            produto_existente = self.local_db.buscar_produto_por_codigo_barras(produto_data['codigo_barras'])
                        if not produto_existente:
                            produto_existente = self.local_db.buscar_produto_por_nome_exato(produto_data['nome'])

                        if produto_existente:
                            self.local_db.atualizar_produto(produto_existente['id'], **produto_data)
                        else:
                            self.local_db.adicionar_produto(**produto_data)
                        
                        produtos_importados += 1
                    except Exception as e:
                        produtos_erro += 1
                        erros_detalhes.append(f"Linha {i+2}: {row.get('nome', 'N/A')} - {str(e)}")
                    
                    self.progress.emit(int(((i + 1) / total_linhas) * 100))
                
                self.local_db.commit_transaction()

        except Exception as e:
            if self.local_db:
                self.local_db.rollback_transaction()
            erros_detalhes.append(f"Erro geral: {str(e)}")
        finally:
            if self.local_db:
                self.local_db.fechar()

        self.finished.emit(produtos_importados, produtos_erro, erros_detalhes)
    
    # Métodos auxiliares (sem alterações)
    def _extrair_quantidade_do_estoque_detalhado(self, estoque_str):
        try:
            if estoque_str.isdigit(): return int(estoque_str)
            import re
            numeros = re.findall(r'\d+', estoque_str)
            return int(numeros[0]) if numeros else 0
        except: return 0

    def _extrair_preco(self, preco_str):
        try:
            return float(preco_str.replace('R$', '').replace(' ', '').replace(',', '.'))
        except: return 0.0

    def _extrair_margem(self, margem_str):
        try:
            return float(margem_str.replace('%', '').replace(' ', '').replace(',', '.'))
        except: return 0.0

    def _formatar_data_validade(self, data_str):
        if not data_str or not data_str.strip(): return None
        try:
            if '/' in data_str: return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            return datetime.strptime(data_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except: return None
    
# Substitua a classe EstoqueWindow inteira em seu arquivo.
class EstoqueWindow(QWidget):
    dados_produtos_alterados = pyqtSignal()
    def __init__(self, db, theme_colors, logo_pixmap=None): 
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.logo_pixmap = logo_pixmap
        self.pagina_atual = 1
        self.itens_por_pagina = 100 
        self.total_paginas = 1

        self.logo_path = "assets/img/GestorX (2).png"
        self.company_info = {
            "nome": "Estação Doces",
            "endereco": "Rua do Comércio, 123 - Centro",
            "contato": "Telefone: (11) 99999-8888 | Email: contato@estacaodoces.com"
        }

        self.initUI()
        self.set_theme(self.theme_colors) 
        self.atualizar_visualizacao_dados()

    # ================================================================= #
    #       CORREÇÃO PRINCIPAL: MÉTODO set_theme REFEITO                #
    # ================================================================= #
    def set_theme(self, theme_colors):
        """
        Aplica um stylesheet completo e unificado para toda a janela de estoque,
        garantindo que todos os componentes, incluindo labels e scrollbars, sejam atualizados.
        """
        self.theme_colors = theme_colors
        
        # Atualiza os ícones de todos os botões primeiro
        self.update_button_icons()
        
        # Estilo unificado para toda a janela
        style = f"""
            /* Estilo geral para a janela */
            QWidget {{
                background-color: {self.theme_colors.get('bg_color', '#ffffff')};
            }}

            /* --- CORREÇÃO 1: Estilo para os labels dentro dos grupos de filtro e paginação --- */
            QGroupBox QLabel, #paginationLabel {{
                color: {self.theme_colors.get('text_color', '#000000')};
                background: transparent; /* Garante fundo transparente */
                font-size: 10pt;
            }}

            /* Legenda de cores para os alertas de estoque/vencimento */
            #legendaEstoqueBaixo {{ color: #dc3545; }} /* Vermelho */
            #legendaVence30 {{ color: #fd7e14; }} /* Laranja */
            #legendaVence15 {{ color: #dc3545; }} /* Vermelho */

            /* Estilo para o cabeçalho da tabela */
            QHeaderView::section {{
                background-color: {self.theme_colors.get('surface_color', '#e0e0e0')};
                color: {self.theme_colors.get('text_color', '#000000')};
                padding: 4px;
                border: 1px solid {self.theme_colors.get('border_color', '#c0c0c0')};
                font-weight: bold;
            }}

            /* --- CORREÇÃO 2: Estilo para as barras de rolagem da tabela --- */
            QTableWidget QScrollBar:vertical {{
                border: none;
                background: {self.theme_colors.get('surface_color', '#f0f0f0')};
                width: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QTableWidget QScrollBar::handle:vertical {{
                background: {self.theme_colors.get('border_color', '#cccccc')};
                min-height: 20px;
                border-radius: 6px;
            }}
            QTableWidget QScrollBar::handle:vertical:hover {{
                background: {self.theme_colors.get('accent_color', '#007bff')};
            }}
            QTableWidget QScrollBar:horizontal {{
                border: none;
                background: {self.theme_colors.get('surface_color', '#f0f0f0')};
                height: 12px;
                margin: 0px 0px 0px 0px;
            }}
            QTableWidget QScrollBar::handle:horizontal {{
                background: {self.theme_colors.get('border_color', '#cccccc')};
                min-width: 20px;
                border-radius: 6px;
            }}
            QTableWidget QScrollBar::handle:horizontal:hover {{
                background: {self.theme_colors.get('accent_color', '#007bff')};
            }}
            QTableWidget QScrollBar::add-line, QTableWidget QScrollBar::sub-line {{
                height: 0px;
                width: 0px;
            }}
            /* --- FIM DA CORREÇÃO 2 --- */

            /* Estilo para os botões de ação inferiores */
            #primaryActionButton {{
                background-color: {self.theme_colors.get('accent_color', '#007bff')};
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }}
            #primaryActionButton:hover {{
                background-color: #0069d9;
            }}
            
            #secondaryActionButton {{
                background-color: {self.theme_colors.get('surface_color', '#ffffff')};
                color: {self.theme_colors.get('text_color', '#000000')};
                border: 1px solid {self.theme_colors.get('border_color', '#cccccc')};
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }}
            #secondaryActionButton:hover {{
                background-color: {self.theme_colors.get('button_hover', '#f0f0f0')};
            }}
        """
        self.setStyleSheet(style)
        self.atualizar_visualizacao_dados()
    
    def update_button_icons(self):
        """Atualiza todos os ícones da interface para refletir o novo tema."""
        text_color = self.theme_colors.get('text_color', '#000')
        
        self.search_button.setIcon(IconManager.get_icon('search', text_color))
        self.aplicar_filtro_btn.setIcon(IconManager.get_icon('filter', text_color))
        self.limpar_filtro_btn.setIcon(IconManager.get_icon('clear', text_color))
        self.prev_page_btn.setIcon(IconManager.get_icon('angle-left', text_color))
        self.next_page_btn.setIcon(IconManager.get_icon('angle-right', text_color))
        
        self.add_button.setIcon(IconManager.get_icon('add', 'white'))
        self.relatorio_btn.setIcon(IconManager.get_icon('report', text_color))
        self.relatorio_estoque_btn.setIcon(IconManager.get_icon('report', text_color))
        self.exportar_csv_btn.setIcon(IconManager.get_icon('export', text_color))
        self.importar_csv_btn.setIcon(IconManager.get_icon('import', text_color))

    def initUI(self):
        layout = QVBoxLayout(self)
        
        search_group = QGroupBox("Pesquisa e Filtros")
        search_layout = QVBoxLayout(search_group)
        
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar produto por nome, descrição ou código de barras...")
        
        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar")
        self.search_button.clicked.connect(self.pesquisar_produtos)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)
        search_layout.addLayout(search_input_layout)
        
        filter_layout = QHBoxLayout()
        self.estoque_combo = QComboBox()
        self.estoque_combo.addItem("Todos os níveis", "todos")
        self.estoque_combo.addItem("Estoque Baixo", "baixo")
        self.estoque_combo.addItem("Estoque Médio", "medio")
        self.estoque_combo.addItem("Estoque Alto", "alto")
        filter_layout.addWidget(QLabel("Nível de Estoque:"))
        filter_layout.addWidget(self.estoque_combo)
        
        self.vencimento_combo = QComboBox()
        self.vencimento_combo.addItem("Todos", "todos")
        self.vencimento_combo.addItem("Vence em 30 dias", "30")
        self.vencimento_combo.addItem("Vence em 15 dias", "15")
        self.vencimento_combo.addItem("Vencidos", "vencidos")
        filter_layout.addWidget(QLabel("Vencimento:"))
        filter_layout.addWidget(self.vencimento_combo)

        self.categoria_combo = QComboBox()
        self.categoria_combo.addItem("Todas as categorias", "todas")
        self.carregar_categorias()
        filter_layout.addWidget(QLabel("Categoria:"))
        filter_layout.addWidget(self.categoria_combo)
        
        self.aplicar_filtro_btn = QPushButton()
        self.aplicar_filtro_btn.setToolTip("Aplicar Filtros")
        self.aplicar_filtro_btn.clicked.connect(self.aplicar_filtros)
        
        self.limpar_filtro_btn = QPushButton()
        self.limpar_filtro_btn.setToolTip("Limpar Filtros")
        self.limpar_filtro_btn.clicked.connect(self.limpar_filtros)
        
        filter_layout.addWidget(self.aplicar_filtro_btn)
        filter_layout.addWidget(self.limpar_filtro_btn)
        
        search_layout.addLayout(filter_layout)
        layout.addWidget(search_group)
        
        legenda_layout = QHBoxLayout()
        # --- CORREÇÃO: Adicionando objectName para estilização ---
        estoque_baixo_label = QLabel("Estoque Baixo"); estoque_baixo_label.setObjectName("legendaEstoqueBaixo")
        vencimento_30_label = QLabel("Vence em 30 dias"); vencimento_30_label.setObjectName("legendaVence30")
        vencimento_15_label = QLabel("Vence em 15 dias"); vencimento_15_label.setObjectName("legendaVence15")
        
        legenda_layout.addWidget(estoque_baixo_label)
        legenda_layout.addWidget(vencimento_30_label)
        legenda_layout.addWidget(vencimento_15_label)
        legenda_layout.addStretch()
        layout.addLayout(legenda_layout)
        
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(12)
        self.tabela.setHorizontalHeaderLabels([
            "Código de Barras", "Nome", "Categoria", "Estoque Detalhado", "Estoque Mín.", 
            "Preço Compra", "Margem %", "Preço Venda", "Validade", 
            "Localização", "Fornecedor", "Ações"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        paginacao_layout = QHBoxLayout()
        paginacao_layout.setAlignment(Qt.AlignCenter)
        
        self.prev_page_btn = QPushButton(" Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
        
        # --- CORREÇÃO: Adicionando objectName para estilização ---
        self.page_label = QLabel(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.page_label.setObjectName("paginationLabel")

        self.next_page_btn = QPushButton("Próxima")
        self.next_page_btn.setLayoutDirection(Qt.RightToLeft)
        self.next_page_btn.clicked.connect(self.ir_proxima_pagina)

        paginacao_layout.addWidget(self.prev_page_btn)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.page_label)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.next_page_btn)
        layout.addLayout(paginacao_layout)
        
        action_layout = QHBoxLayout()
        self.add_button = QPushButton(" Adicionar Produto")
        self.add_button.setObjectName("primaryActionButton") 
        self.add_button.clicked.connect(self.abrir_formulario_produto)

        self.relatorio_btn = QPushButton(" Relatório de Vencimentos")
        self.relatorio_btn.setObjectName("secondaryActionButton")
        self.relatorio_btn.clicked.connect(self.relatorio_vencimentos)

        self.relatorio_estoque_btn = QPushButton(" Relatório de Estoque Baixo")
        self.relatorio_estoque_btn.setObjectName("secondaryActionButton")
        self.relatorio_estoque_btn.clicked.connect(self.relatorio_estoque_baixo)
        
        self.exportar_csv_btn = QPushButton(" Exportar CSV")
        self.exportar_csv_btn.setObjectName("secondaryActionButton")
        self.exportar_csv_btn.clicked.connect(self.exportar_csv)

        self.importar_csv_btn = QPushButton(" Importar CSV")
        self.importar_csv_btn.setObjectName("secondaryActionButton")
        self.importar_csv_btn.clicked.connect(self.importar_csv)

        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.relatorio_btn)
        action_layout.addWidget(self.relatorio_estoque_btn)
        action_layout.addWidget(self.exportar_csv_btn)
        action_layout.addWidget(self.importar_csv_btn)
        layout.addLayout(action_layout)
        
        self.update_button_icons()

    # O resto da classe EstoqueWindow continua exatamente igual ao que você já tinha.
    # ... (cole todos os outros métodos de EstoqueWindow aqui, sem nenhuma alteração) ...
    def ir_pagina_anterior(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_visualizacao_dados()

    def ir_proxima_pagina(self):
        if self.pagina_atual < self.total_paginas:
            self.pagina_atual += 1
            self.atualizar_visualizacao_dados()

    def atualizar_categorias_filtro(self):
        categoria_selecionada = self.categoria_combo.currentData()
        self.carregar_categorias()
        if categoria_selecionada and categoria_selecionada != "todas":
            index = self.categoria_combo.findData(categoria_selecionada)
            if index >= 0:
                self.categoria_combo.setCurrentIndex(index)
    
    def carregar_dados(self):
        """Agora é apenas uma chamada para a função central."""
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
        self.carregar_categorias()
    
    def carregar_categorias(self):
        # ... (seu método está correto, mas vamos garantir que o dado 'todas' exista) ...
        current_data = self.categoria_combo.currentData()
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Todas as categorias", "todas")
        categorias = self.db.listar_categorias_unicas()
        for categoria in categorias:
            if categoria and categoria.strip():
                self.categoria_combo.addItem(categoria, categoria)
        
        index = self.categoria_combo.findData(current_data)
        if index != -1:
            self.categoria_combo.setCurrentIndex(index)
    
    def pesquisar_produtos(self):
        """Apenas reseta a página e atualiza a visualização."""
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()

    def aplicar_filtros(self):
        """Apenas reseta a página e atualiza a visualização."""
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
    
    def limpar_filtros(self):
        """Limpa os campos, reseta a página e atualiza a visualização."""
        self.estoque_combo.setCurrentIndex(0)
        self.vencimento_combo.setCurrentIndex(0)
        self.categoria_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
        self.carregar_categorias() # Recarrega as categorias após limpar
    
    def atualizar_visualizacao_dados(self):
        """
        Função central que busca os filtros da UI, consulta o banco de dados
        com paginação e filtros, e atualiza a tabela e os controles de paginação.
        """
        filtros = {
            'termo_pesquisa': self.search_input.text(),
            'estoque': self.estoque_combo.currentData(),
            'vencimento': self.vencimento_combo.currentData(),
            'categoria': self.categoria_combo.currentData(),
        }

        produtos = self.db.listar_produtos_paginado_e_filtrado(
            filtros=filtros,
            pagina=self.pagina_atual,
            itens_por_pagina=self.itens_por_pagina
        )
        total_itens = self.db.contar_produtos_filtrados(filtros=filtros)
        self.atualizar_tabela(produtos)

        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina) or 1
        
        self.page_label.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.prev_page_btn.setEnabled(self.pagina_atual > 1)
        self.next_page_btn.setEnabled(self.pagina_atual < self.total_paginas)
    
    def atualizar_tabela(self, produtos):
        self.tabela.setRowCount(0)
        icon_color = self.theme_colors.get('text_color', '#000')
        hoje = datetime.now().date()

        try:
            bg_color_hex = self.theme_colors.get('bg_color', '#ffffff')
            color = QColor(bg_color_hex)
            luminance = (0.299 * color.red() + 0.587 * color.green() + 0.114 * color.blue()) / 255
            is_dark_theme = luminance < 0.5
        except Exception:
            is_dark_theme = True 
        
        dar_baixa_icon_color = '#ffffff' if is_dark_theme else '#000000'
        icon_color = self.theme_colors.get('text_color', '#000000')

        def get_value(key, default=""):
            return produto[key] if key in produto.keys() else default

        for row, produto in enumerate(produtos):
            self.tabela.insertRow(row)
            
            self.tabela.setItem(row, 0, QTableWidgetItem(get_value('codigo_barras', '')))
            
            nome_produto = get_value('nome', 'Produto Desconhecido')
            is_fracionado = bool(get_value('fracionado', False))
            if is_fracionado:
                nome_produto += f" (Frac. - {get_value('unidade_medida', 'un')})"
            self.tabela.setItem(row, 1, QTableWidgetItem(nome_produto))

            self.tabela.setItem(row, 2, QTableWidgetItem(get_value('categoria', "Sem categoria")))
            
            quantidade = get_value('quantidade', 0)
            estoque_fracionado = get_value('estoque_fracionado', 0)
            if is_fracionado:
                estoque_total_unidades = get_value('estoque_total_calculado', 0)
                quantidade_display = f"{quantidade} emb. + {estoque_fracionado} {get_value('unidade_medida', 'un')} (Total: {estoque_total_unidades})"
                tooltip_text = f"Embalagens: {quantidade}\nFracionado: {estoque_fracionado} {get_value('unidade_medida', 'un')}\nTotal em unidades: {estoque_total_unidades}"
            else:
                quantidade_display = str(quantidade)
                tooltip_text = f"Quantidade: {quantidade}"

            quantidade_item = QTableWidgetItem(quantidade_display)
            quantidade_item.setToolTip(tooltip_text)
            
            estoque_minimo = get_value('estoque_minimo', 0)
            
            if estoque_minimo > 0 and quantidade <= estoque_minimo:
                quantidade_item.setForeground(QBrush(QColor('red')))
                quantidade_item.setToolTip(quantidade_item.toolTip() + "\nESTOQUE ABAIXO DO MÍNIMO!")

            self.tabela.setItem(row, 3, quantidade_item)
            
            self.tabela.setItem(row, 4, QTableWidgetItem(str(estoque_minimo)))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {get_value('preco_compra', 0):.2f}"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{get_value('margem_lucro', 0):.2f}%"))
            
            if is_fracionado and get_value('preco_unitario_fracao', 0):
                preco_display = f"Emb: R$ {get_value('preco_venda', 0):.2f} | Un: R$ {get_value('preco_unitario_fracao', 0):.2f}"
            else:
                preco_display = f"R$ {get_value('preco_venda', 0):.2f}"
            self.tabela.setItem(row, 7, QTableWidgetItem(preco_display))
            
            validade_str = get_value('data_validade', '')
            validade_item = QTableWidgetItem(validade_str)
            
            dias_para_vencer = 999 
            if validade_str:
                try:
                    data_validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
                    dias_para_vencer = (data_validade - hoje).days
                    
                    if dias_para_vencer <= 0:
                        validade_item.setForeground(QBrush(QColor('darkred')))
                        validade_item.setToolTip("Produto VENCIDO!")
                    elif dias_para_vencer <= 15:
                        validade_item.setForeground(QBrush(QColor('red')))
                        validade_item.setToolTip(f"Vence em {dias_para_vencer} dias!")
                    elif dias_para_vencer <= 30:
                        validade_item.setForeground(QBrush(QColor('orange')))
                        validade_item.setToolTip(f"Vence em {dias_para_vencer} dias!")

                except ValueError as e:
                    print(f"AVISO: Data em formato inválido para o produto '{nome_produto}': {validade_str}. Erro: {e}")

            self.tabela.setItem(row, 8, validade_item)

            self.tabela.setItem(row, 9, QTableWidgetItem(get_value('localizacao', '')))
            self.tabela.setItem(row, 10, QTableWidgetItem(get_value('fornecedor_nome', "N/A")))
            
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            acoes_layout.setSpacing(5)
            
            hover_color = self.theme_colors.get('button_hover', '#555555')
            
            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), "")
            editar_btn.setToolTip("Editar Produto")
            
            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), "")
            excluir_btn.setToolTip("Excluir Produto")

            editar_btn.clicked.connect(lambda _, p_id=get_value('id'): self.abrir_formulario_produto(p_id))
            excluir_btn.clicked.connect(lambda _, p_id=get_value('id'): self.excluir_produto(p_id))

            for btn in [editar_btn, excluir_btn]:
                btn.setFixedSize(30, 30)
                btn.setFlat(True)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet(f"""
                    QPushButton {{ border-radius: 4px; }}
                    QPushButton:hover {{ background-color: {hover_color}; }}
                """)
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            validade_str = get_value('data_validade', '')
            dias_para_vencer = 999
            if validade_str:
                try:
                    data_validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
                    dias_para_vencer = (data_validade - hoje).days
                except ValueError:
                    pass
            
            produto_tem_estoque = get_value('quantidade', 0) > 0 or get_value('estoque_fracionado', 0) > 0
            
            if dias_para_vencer <= 0 and produto_tem_estoque:
                dar_baixa_btn = QPushButton(IconManager.get_icon('thumb-down', dar_baixa_icon_color), "")
                dar_baixa_btn.setToolTip("Dar Baixa por Vencimento (Registrar Perda)")
                dar_baixa_btn.setFixedSize(30, 30)
                dar_baixa_btn.setFlat(True)
                dar_baixa_btn.setCursor(Qt.PointingHandCursor)
                dar_baixa_btn.setStyleSheet("""
                    QPushButton { border-radius: 4px; }
                    QPushButton:hover { background-color: #dc3545; }
                """)
                dar_baixa_btn.clicked.connect(lambda _, p_id=get_value('id'): self.dar_baixa_produto(p_id))
                acoes_layout.addWidget(dar_baixa_btn)
            
            if bool(get_value('fracionado', False)) and get_value('quantidade', 0) > 0:
                quebrar_btn = QPushButton(IconManager.get_icon('break', icon_color), "")
                quebrar_btn.setToolTip("Quebrar embalagem em unidades")
                quebrar_btn.setFixedSize(30, 30)
                quebrar_btn.setFlat(True)
                quebrar_btn.setCursor(Qt.PointingHandCursor)
                quebrar_btn.setStyleSheet(f"""
                    QPushButton {{ border-radius: 4px; }}
                    QPushButton:hover {{ background-color: {hover_color}; }}
                """)
                quebrar_btn.clicked.connect(lambda _, p_id=get_value('id'): self.abrir_dialog_quebrar_embalagem(p_id))
                acoes_layout.addWidget(quebrar_btn)
            
            self.tabela.setCellWidget(row, 11, acoes_widget)

    def abrir_dialog_quebrar_embalagem(self, produto_id):
        produto_info = self.db.obter_info_estoque_fracionado(produto_id)
        if not produto_info or not produto_info['fracionado']:
            QMessageBox.warning(self, "Erro", "Este produto não é fracionado!")
            return
        
        dialog = DialogQuebrarEmbalagem(self.db, produto_info, self.theme_colors, self.logo_pixmap)
        
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
            print("DEBUG: Embalagem quebrada. Emitindo sinal 'dados_produtos_alterados'.")
            self.dados_produtos_alterados.emit()
    
    def dar_baixa_produto(self, produto_id):
        produto = self.db.obter_produto(produto_id)
        if not produto:
            AlertDialog(self, "Erro", "Produto não encontrado.", alert_type='error', theme_colors=self.theme_colors).exec_()
            return

        valor_perda = (produto['quantidade'] or 0) * (produto['preco_compra'] or 0)
        
        mensagem = (f"Você está prestes a dar baixa no produto '{produto['nome']}'.\n"
                    f"O estoque será zerado e será registrada uma perda de R$ {valor_perda:.2f}.\n\n"
                    "Esta ação não pode ser desfeita. Deseja continuar?")

        dialog = AlertDialog(self, "Confirmar Baixa por Perda", mensagem,
                            alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            sucesso, msg_retorno = self.db.registrar_perda_produto(produto_id, operador="Usuário do Estoque")
            
            if sucesso:
                AlertDialog(self, "Sucesso", msg_retorno, alert_type='success', theme_colors=self.theme_colors).exec_()
                self.atualizar_visualizacao_dados()
                self.dados_produtos_alterados.emit()
            else:
                AlertDialog(self, "Erro", msg_retorno, alert_type='error', theme_colors=self.theme_colors).exec_()

    def abrir_formulario_produto(self, produto_id=None):
        dialog = FormularioProduto(self.db, produto_id, self.theme_colors, self.logo_pixmap)
        dialog.showMaximized() 

        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
            self.atualizar_categorias_filtro()
            print("DEBUG: Formulário de produto salvo. Emitindo sinal 'dados_produtos_alterados'.")
            self.dados_produtos_alterados.emit()
    
    def excluir_produto(self, produto_id):
        dialog = AlertDialog(self, "Confirmar Exclusão", 
                                "Tem certeza que deseja excluir este produto?\nEsta ação não pode ser desfeita.",
                                alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            if self.db.excluir_produto(produto_id):
                AlertDialog(self, "Sucesso", "Produto excluído com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
                self.carregar_dados()
                self.dados_produtos_alterados.emit()
            else:
                AlertDialog(self, "Erro", "Não foi possível excluir o produto.", alert_type='error', theme_colors=self.theme_colors).exec_()
    
    def _criar_kpi_boxes(self, kpi_data, doc_width):
        styles = getSampleStyleSheet()
        style_label = ParagraphStyle('kpi_label', parent=styles['Normal'], fontSize=9, textColor=colors.dimgrey, alignment=TA_LEFT)
        style_value = ParagraphStyle('kpi_value', parent=styles['Normal'], fontSize=16, fontName='Helvetica-Bold', alignment=TA_LEFT)

        data = []
        for kpi in kpi_data:
            p_label = Paragraph(kpi['label'], style_label)
            kpi_value = kpi['value']
            if isinstance(kpi_value, Paragraph):
                p_value = kpi_value
                p_value.style.alignment = TA_LEFT 
            else:
                p_value = Paragraph(str(kpi_value), style_value)
            
            data.append([p_label, p_value])
        
        tabela_data = [list(i) for i in zip(*data)]

        kpi_table = Table(tabela_data, colWidths=[doc_width / len(kpi_data)] * len(kpi_data))
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F2F2F2")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E0E0E0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        return kpi_table

    def _gerar_pdf_com_template(self, file_path, report_title, elementos):
        try:
            left_margin = 2*cm
            right_margin = 2*cm
            top_margin = 3*cm
            bottom_margin = 1.5*cm

            def header_footer(canvas, doc):
                canvas.saveState()
                
                if os.path.exists(self.logo_path):
                    canvas.drawImage(self.logo_path, doc.leftMargin, doc.height + doc.topMargin,
                                     width=120, height=45, preserveAspectRatio=True, mask='auto')
                
                canvas.setFont('Helvetica', 9)
                canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin + 20, self.company_info['nome'])
                canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin + 5, self.company_info['endereco'])
                canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin - 10, self.company_info['contato'])

                canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
                canvas.line(doc.leftMargin, doc.height + doc.topMargin - 20, doc.width + doc.leftMargin, doc.height + doc.topMargin - 20)
                
                canvas.setFont('Helvetica-Oblique', 8)
                canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 20, f"Página {canvas.getPageNumber()} | {report_title}")
                canvas.restoreState()

            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                topMargin=top_margin,
                bottomMargin=bottom_margin,
                leftMargin=left_margin,
                rightMargin=right_margin
            )
            
            doc.build(elementos, onFirstPage=header_footer, onLaterPages=header_footer)
            
            AlertDialog(self, "Sucesso", f"Relatório salvo com sucesso em:\n{file_path}", 
                        alert_type='success', theme_colors=self.theme_colors).exec_()

        except FileNotFoundError:
            AlertDialog(self, "Erro de Logo", f"Arquivo de logo não encontrado em:\n{self.logo_path}", 
                        alert_type='error', theme_colors=self.theme_colors).exec_()
        except Exception as e:
            AlertDialog(self, "Erro ao Gerar PDF", f"Ocorreu um erro inesperado: {str(e)}", 
                        alert_type='error', theme_colors=self.theme_colors).exec_()

    def relatorio_vencimentos(self):
        produtos = self.db.verificar_produtos_vencendo(dias=30)
        if not produtos:
            AlertDialog(self, "Relatório", "Não há produtos vencendo nos próximos 30 dias.", 
                        alert_type='info', theme_colors=self.theme_colors).exec_()
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório de Vencimentos", os.path.expanduser("~/relatorio_vencimentos.pdf"), "PDF Files (*.pdf)")
        if file_path:
            self.gerar_pdf_vencimentos(produtos, file_path)

    def gerar_pdf_vencimentos(self, produtos, file_path):
        styles = getSampleStyleSheet()
        elementos = []

        elementos.append(Paragraph("Relatório de Análise de Vencimentos", styles['h1']))
        elementos.append(Paragraph(f"Período de Análise: Próximos 30 dias (a partir de {datetime.now().strftime('%d/%m/%Y')})", styles['Normal']))
        elementos.append(Spacer(1, 0.8 * cm))
        
        hoje = datetime.now().date()
        total_unidades = sum(p['quantidade'] for p in produtos)
        valor_custo_risco = sum(p['quantidade'] * (p['preco_compra'] or 0) for p in produtos)
        produto_mais_critico = min(produtos, key=lambda p: (datetime.strptime(p['data_validade'], "%Y-%m-%d").date() - hoje).days)

        left_margin, right_margin = 2*cm, 2*cm
        doc_width = A4[0] - left_margin - right_margin
        
        kpi_data = [
            {'label': 'PRODUTOS MAPEADOS', 'value': str(len(produtos))},
            {'label': 'UNIDADES EM RISCO', 'value': str(total_unidades)},
            {'label': 'VALOR DE CUSTO EM RISCO', 'value': f"R$ {self._format_currency_brl(valor_custo_risco)}"},
            {'label': 'ITEM MAIS CRÍTICO', 'value': Paragraph(produto_mais_critico['nome'], styles['Normal'])}
        ]
        elementos.append(self._criar_kpi_boxes(kpi_data, doc_width))
        elementos.append(Spacer(1, 1 * cm))

        elementos.append(Paragraph("Detalhamento dos Produtos", styles['h2']))
        produtos_ordenados = sorted(produtos, key=lambda p: datetime.strptime(p['data_validade'], "%Y-%m-%d").date())
        
        data = [["Produto", "Validade", "Dias Rest.", "Estoque", "Preço Custo", "Fornecedor"]]
        for p in produtos_ordenados:
            data_validade = datetime.strptime(p['data_validade'], "%Y-%m-%d").date()
            dias_para_vencer = (data_validade - hoje).days
            data.append([
                Paragraph(p['nome'], styles['Normal']), 
                data_validade.strftime("%d/%m/%Y"), 
                str(dias_para_vencer),
                str(p['quantidade']), 
                f"R$ {self._format_currency_brl(p['preco_compra'] or 0)}", 
                Paragraph(p['fornecedor_nome'] or "N/A", styles['Normal'])
            ])
        
        tabela = Table(data, colWidths=[5*cm, 2.5*cm, 2*cm, 2*cm, 2.5*cm, 3.5*cm], repeatRows=1)
        
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#002060")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ])
        tabela.setStyle(style)

        for i in range(1, len(data)):
            bgColor = colors.HexColor("#DDEBF7") if i % 2 != 0 else colors.white
            tabela.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), bgColor)]))
            
            dias_para_vencer = (datetime.strptime(produtos_ordenados[i-1]['data_validade'], "%Y-%m-%d").date() - hoje).days
            if dias_para_vencer <= 0:
                tabela.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.HexColor("#FFC7CE"))]))
            elif dias_para_vencer <= 15:
                tabela.setStyle(TableStyle([('BACKGROUND', (0, i), (-1, i), colors.HexColor("#FFEB9C"))]))

        elementos.append(tabela)
        
        self._gerar_pdf_com_template(file_path, "Relatório de Vencimentos", elementos)

    def relatorio_estoque_baixo(self):
        produtos = self.db.verificar_produtos_estoque_baixo()
        if not produtos:
            AlertDialog(self, "Relatório", "Não há produtos com estoque abaixo do mínimo.", 
                        alert_type='info', theme_colors=self.theme_colors).exec_()
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório de Estoque Baixo", os.path.expanduser("~/relatorio_estoque_baixo.pdf"), "PDF Files (*.pdf)")
        if file_path:
            self.gerar_pdf_estoque_baixo(produtos, file_path)

    def _format_currency_brl(self, value):
        """Formata um número float para o padrão monetário brasileiro (1.234,56)."""
        try:
            return f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except (ValueError, TypeError):
            return "0,00"

    def gerar_pdf_estoque_baixo(self, produtos, file_path):
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='RightAlign', parent=styles['Normal'], alignment=TA_RIGHT))
        styles.add(ParagraphStyle(name='CenterAlign', parent=styles['Normal'], alignment=TA_CENTER))
        elementos = []

        elementos.append(Paragraph("Plano de Ação de Reposição de Estoque", styles['h1']))
        elementos.append(Paragraph(f"Relatório gerado em: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        elementos.append(Spacer(1, 0.8 * cm))
        
        produtos_por_fornecedor = defaultdict(list)
        for p in produtos: produtos_por_fornecedor[p['fornecedor_nome'] or "Fornecedor Não Definido"].append(p)
        custo_reposicao = sum(p['preco_compra'] * ((p['estoque_minimo'] * 2) - p['quantidade']) for p in produtos if p['preco_compra'] and (p['estoque_minimo'] * 2) > p['quantidade'])
        
        left_margin, right_margin = 2*cm, 2*cm
        doc_width = A4[0] - left_margin - right_margin

        kpi_data = [
            {'label': 'PRODUTOS CRÍTICOS', 'value': str(len(produtos))},
            {'label': 'CUSTO TOTAL DE REPOSIÇÃO', 'value': f"R$ {self._format_currency_brl(custo_reposicao)}"},
            {'label': 'FORNECEDORES ACIONADOS', 'value': str(len(produtos_por_fornecedor))}
        ]
        elementos.append(self._criar_kpi_boxes(kpi_data, doc_width))
        elementos.append(Spacer(1, 1 * cm))

        elementos.append(Paragraph("Listas de Compras por Fornecedor", styles['h2']))
        
        for fornecedor, itens in sorted(produtos_por_fornecedor.items()):
            elementos.append(Spacer(1, 0.5 * cm))
            elementos.append(Paragraph(f"<b>Fornecedor:</b> {fornecedor}", styles['h3']))
            
            data = [["Produto", "Est. Atual", "Est. Mínimo", "Sugestão Compra", "Custo (Est.)"]]
            total_custo_fornecedor = 0
            
            for p in sorted(itens, key=lambda i: i['nome']):
                qtd_sugerida = max(0, (p['estoque_minimo'] * 2) - p['quantidade'])
                custo_item = qtd_sugerida * (p['preco_compra'] or 0)
                total_custo_fornecedor += custo_item
                
                data.append([
                    Paragraph(p['nome'], styles['Normal']), 
                    str(p['quantidade']), 
                    str(p['estoque_minimo']),
                    Paragraph(str(qtd_sugerida), styles['CenterAlign']),
                    f"R$ {self._format_currency_brl(custo_item)}"
                ])
            
            data.append([
                '', '', 
                Paragraph("<b>Total do Pedido:</b>", styles['RightAlign']),
                '', 
                Paragraph(f"<b>R$ {self._format_currency_brl(total_custo_fornecedor)}</b>", styles['Normal'])
            ])

            tabela = Table(data, colWidths=[6.5*cm, 2.5*cm, 2.5*cm, 3*cm, 3*cm], repeatRows=1)
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke), 
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), 
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), 
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#C5D9F1")),
                ('ALIGN', (2, -1), (2, -1), 'RIGHT'),
                ('SPAN', (0, -1), (1, -1)),
            ])
            tabela.setStyle(style)
            elementos.append(tabela)
            
        self._gerar_pdf_com_template(file_path, "Plano de Reposição de Estoque", elementos)

    def exportar_csv(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Estoque para CSV", 
                os.path.expanduser("~/estoque_export.csv"),
                "CSV Files (*.csv)"
            )
            
            if not file_path: return
            
            produtos = []
            for row in range(self.tabela.rowCount()):
                produto = {}
                produto['id'] = self.tabela.item(row, 0).text() if self.tabela.item(row, 0) else ""
                produto['codigo_barras'] = self.tabela.item(row, 1).text() if self.tabela.item(row, 1) else ""
                produto['nome'] = self.tabela.item(row, 2).text() if self.tabela.item(row, 2) else ""
                produto['categoria'] = self.tabela.item(row, 3).text() if self.tabela.item(row, 3) else ""
                produto['estoque_detalhado'] = self.tabela.item(row, 4).text() if self.tabela.item(row, 4) else ""
                produto['estoque_minimo'] = self.tabela.item(row, 5).text() if self.tabela.item(row, 5) else ""
                produto['preco_compra'] = self.tabela.item(row, 6).text() if self.tabela.item(row, 6) else ""
                produto['margem'] = self.tabela.item(row, 7).text() if self.tabela.item(row, 7) else ""
                produto['preco_venda'] = self.tabela.item(row, 8).text() if self.tabela.item(row, 8) else ""
                produto['validade'] = self.tabela.item(row, 9).text() if self.tabela.item(row, 9) else ""
                produto['localizacao'] = self.tabela.item(row, 10).text() if self.tabela.item(row, 10) else ""
                produto['fornecedor'] = self.tabela.item(row, 11).text() if self.tabela.item(row, 11) else ""
                produtos.append(produto)
            
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'codigo_barras', 'nome', 'categoria', 'estoque_detalhado', 
                            'estoque_minimo', 'preco_compra', 'margem', 'preco_venda', 
                            'validade', 'localizacao', 'fornecedor']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for produto in produtos: writer.writerow(produto)
            
            QMessageBox.information(self, "Sucesso", f"Dados exportados com sucesso para:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar CSV: {str(e)}")

    def importar_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar CSV para Estoque", os.path.expanduser("~"), "CSV Files (*.csv)"
        )
        if not file_path: return

        dialog = AlertDialog(self, "Confirmar Importação",
                             "A importação será executada em segundo plano.\nDeseja continuar?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() != QMessageBox.Yes: return

        self.progress_dialog = ThemedProgressDialog(self, 
                                                    "Importando Dados", 
                                                    "Aguarde enquanto os produtos do arquivo CSV são processados...", 
                                                    self.theme_colors)
        
        self.progress_dialog.canceled.connect(self.cancelar_importacao)
        self.import_thread = CsvImportWorker(self.db.db_path, file_path)
        self.import_thread.progress.connect(self.progress_dialog.setValue)
        self.import_thread.finished.connect(self.importacao_concluida)
        self.import_thread.start()
        self.progress_dialog.exec_()

    def cancelar_importacao(self):
        if self.import_thread and self.import_thread.isRunning():
            self.import_thread.terminate()
            QMessageBox.warning(self, "Cancelado", "A importação foi cancelada pelo usuário.")

    def importacao_concluida(self, importados, erros, detalhes_erros):
        self.progress_dialog.close()
        self.atualizar_visualizacao_dados()

        if importados > 0:
            print("DEBUG: Importação CSV concluída. Emitindo sinal 'dados_produtos_alterados'.")
            self.dados_produtos_alterados.emit()

        mensagem = f"Importação concluída!\n\n- Produtos importados/atualizados: {importados}\n- Linhas com erro: {erros}"
        
        if erros > 0:
            detalhes = "\n\nDetalhes dos erros:\n" + "\n".join(detalhes_erros[:5])
            mensagem += detalhes
            AlertDialog(self, "Importação Concluída com Erros", mensagem, alert_type='warning', theme_colors=self.theme_colors).exec_()
        else:
            AlertDialog(self, "Importação Concluída", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()

    def _extrair_quantidade_do_estoque_detalhado(self, estoque_str):
        try:
            if estoque_str.isdigit(): return int(estoque_str)
            import re
            numeros = re.findall(r'\d+', estoque_str)
            if numeros: return int(numeros[0])
            return 0
        except: return 0

    def _extrair_preco(self, preco_str):
        try:
            preco_limpo = preco_str.replace('R$', '').replace(' ', '').replace(',', '.')
            return float(preco_limpo)
        except: return 0.0

    def _extrair_margem(self, margem_str):
        try:
            margem_limpa = margem_str.replace('%', '').replace(' ', '').replace(',', '.')
            return float(margem_limpa)
        except: return 0.0

    def _formatar_data_validade(self, data_str):
        if not data_str or data_str.strip() == "": return None
        try:
            from datetime import datetime
            if len(data_str) == 10 and data_str.count('-') == 2:
                datetime.strptime(data_str, "%Y-%m-%d")
                return data_str
            if len(data_str) == 10 and data_str.count('/') == 2:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                return data_obj.strftime("%Y-%m-%d")
            if len(data_str) == 10 and data_str.count('-') == 2:
                data_obj = datetime.strptime(data_str, "%d-%m-%Y")
                return data_obj.strftime("%Y-%m-%d")
            return None
        except: return None

# Nenhuma alteração necessária nas classes FormularioProduto e DialogQuebrarEmbalagem
# Substitua a classe FormularioProduto inteira em estoque_window.py

class FormularioProduto(QDialog):
    def __init__(self, db, produto_id=None, theme_colors=None, logo_pixmap=None):
        super().__init__()
        self.db = db
        self.produto_id = produto_id
        self.theme_colors = theme_colors if theme_colors else {}
        self.logo_pixmap = logo_pixmap
        self.produto = None
        self.imagem_path = None
        self.drag_position = None

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        if produto_id:
            self.produto = self.db.obter_produto(produto_id)
            if not self.produto:
                QMessageBox.warning(self, "Erro", "Produto não encontrado!")
                self.reject()
                return

        self.initUI()
        self.apply_styles()
        
        if self.produto:
            self.carregar_dados_produto()

    def initUI(self):
        self.setWindowTitle("Formulário de Produto")
        
        # Container principal para o estilo
        container = QFrame(self)
        container.setObjectName("mainContainer")

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Adiciona o cabeçalho customizado
        self.header = self._create_header()
        main_layout.addWidget(self.header)

        # Conteúdo do formulário (agora dentro de um widget separado)
        content_widget = self._create_content()
        main_layout.addWidget(content_widget)

        # Adiciona o container ao layout do QDialog
        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(container)

        # Conexões de sinais
        self.preco_compra_input.valueChanged.connect(self.calcular_preco_venda)
        self.margem_lucro_input.valueChanged.connect(self.calcular_preco_venda)
        self.preco_venda_input.valueChanged.connect(self.calcular_margem_lucro)

    def _create_header(self):
        header_widget = QFrame()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(50)
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        
        if self.logo_pixmap:
            logo_label = QLabel()
            logo_label.setPixmap(self.logo_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(logo_label)

        title_label = QLabel("Formulário de Produto")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {self.theme_colors['text_color']};")
        
        help_button = QPushButton()
        help_button.setObjectName("controlButton")
        help_button.setFixedSize(30, 30)
        help_button.setIcon(IconManager.get_icon('sobre', color=self.theme_colors['text_secondary']))
        help_button.setCursor(Qt.PointingHandCursor)
        
        close_button = QPushButton()
        close_button.setObjectName("controlButton")
        close_button.setFixedSize(30, 30)
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors['text_secondary']))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(help_button)
        layout.addWidget(close_button)
        return header_widget

    def _create_content(self):
        content_container = QWidget()
        main_layout = QVBoxLayout(content_container)
        main_layout.setContentsMargins(20, 15, 20, 20)

        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # --- COLUNA 1: INFORMAÇÕES DO PRODUTO ---
        info_group = QGroupBox("Informações do Produto")
        info_form_layout = QFormLayout(info_group)
        info_form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        
        self.codigo_barras_input = QLineEdit()
        self.nome_input = QLineEdit()
        self.descricao_input = QLineEdit()
        self.categoria_combo = QComboBox(); self.categoria_combo.setEditable(True); self.carregar_categorias()
        self.fornecedor_combo = QComboBox(); self.carregar_fornecedores()
         
        # --- MUDANÇA 1: Localização agora é um ComboBox editável ---
        self.localizacao_input = QComboBox()
        self.localizacao_input.setEditable(True)
        self.carregar_localizacoes()
        # --- FIM DA MUDANÇA 1 ---

        info_form_layout.addRow("Código de Barras:", self._create_input_with_icon('barcode', self.codigo_barras_input))
        info_form_layout.addRow("Nome do Produto:", self._create_input_with_icon('box', self.nome_input))
        info_form_layout.addRow("Descrição:", self._create_input_with_icon('comment-alt', self.descricao_input))
        info_form_layout.addRow("Categoria:", self._create_input_with_icon('tags', self.categoria_combo))
        info_form_layout.addRow("Fornecedor:", self._create_input_with_icon('truck', self.fornecedor_combo))
        info_form_layout.addRow("Localização:", self._create_input_with_icon('map-marker-alt', self.localizacao_input))

        # --- COLUNA 2: ESTOQUE E PRECIFICAÇÃO ---
        preco_group = QGroupBox("Estoque e Precificação")
        preco_form_layout = QFormLayout(preco_group)
        preco_form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.quantidade_input = QSpinBox(); self.quantidade_input.setRange(0, 99999)
        self.estoque_minimo_input = QSpinBox(); self.estoque_minimo_input.setRange(0, 99999)
        self.preco_compra_input = QDoubleSpinBox(); self.preco_compra_input.setRange(0, 99999.99); self.preco_compra_input.setPrefix("R$ ")
        self.margem_lucro_input = QDoubleSpinBox(); self.margem_lucro_input.setRange(0, 999.99); self.margem_lucro_input.setSuffix(" %")
        self.preco_venda_input = QDoubleSpinBox(); self.preco_venda_input.setRange(0, 99999.99); self.preco_venda_input.setPrefix("R$ ")
        self.data_validade_input = QDateEdit(calendarPopup=True); self.data_validade_input.setDisplayFormat("dd/MM/yyyy")

        preco_form_layout.addRow("Quantidade:", self._create_input_with_icon('estoque', self.quantidade_input))
        preco_form_layout.addRow("Estoque Mínimo:", self._create_input_with_icon('estoque_baixo', self.estoque_minimo_input))
        preco_form_layout.addRow("Preço de Compra:", self._create_input_with_icon('dollar-sign', self.preco_compra_input))
        preco_form_layout.addRow("Margem de Lucro:", self._create_input_with_icon('percentage', self.margem_lucro_input))
        preco_form_layout.addRow("Preço de Venda:", self._create_input_with_icon('caixa', self.preco_venda_input))
        preco_form_layout.addRow("Data de Validade:", self._create_input_with_icon('vencimentos', self.data_validade_input))

        # --- COLUNA 3: IMAGEM DO PRODUTO ---
        imagem_group = QGroupBox("Imagem do Produto")
        imagem_layout = QVBoxLayout(imagem_group)
        
        self.imagem_preview_label = QLabel("Nenhuma imagem selecionada")
        self.imagem_preview_label.setAlignment(Qt.AlignCenter)
        self.imagem_preview_label.setMinimumSize(200, 200)
        self.imagem_preview_label.setObjectName("imagePreview")
        imagem_layout.addWidget(self.imagem_preview_label)
        
        self.selecionar_imagem_btn = QPushButton("Selecionar Imagem")
        self.selecionar_imagem_btn.clicked.connect(self.selecionar_imagem)
        imagem_layout.addWidget(self.selecionar_imagem_btn)

        grid_layout.addWidget(info_group, 0, 0)
        grid_layout.addWidget(preco_group, 0, 1)
        grid_layout.addWidget(imagem_group, 0, 2)

        # --- LINHA 2: GRUPO DE FRACIONAMENTO ---
        self.fracionado_group = QGroupBox("Produto Fracionado")
        self.fracionado_group.setCheckable(True)
        self.fracionado_group.setChecked(False)
        fracionado_layout = QFormLayout(self.fracionado_group)
        
        self.unidade_medida_input = QLineEdit(); self.unidade_medida_input.setPlaceholderText("Ex: kg, L, m")
        self.qtd_por_embalagem_input = QSpinBox(); self.qtd_por_embalagem_input.setRange(1, 9999)
        self.preco_unitario_fracao_input = QDoubleSpinBox(); self.preco_unitario_fracao_input.setRange(0, 99999.99); self.preco_unitario_fracao_input.setPrefix("R$ ")
        self.estoque_fracionado_input = QSpinBox(); self.estoque_fracionado_input.setRange(0, 99999)
        
        fracionado_layout.addRow("Unidade de Medida:", self._create_input_with_icon('ruler', self.unidade_medida_input))
        fracionado_layout.addRow("Unidades por Embalagem:", self._create_input_with_icon('box-open', self.qtd_por_embalagem_input))
        fracionado_layout.addRow("Preço Unitário (Fração):", self._create_input_with_icon('tag', self.preco_unitario_fracao_input))
        fracionado_layout.addRow("Estoque Fracionado Atual:", self._create_input_with_icon('cubes', self.estoque_fracionado_input))
        
        grid_layout.addWidget(self.fracionado_group, 1, 0, 1, 3)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(" Salvar Produto")
        self.salvar_btn.setObjectName("primaryActionButton")
        self.salvar_btn.clicked.connect(self.salvar_produto)
        
        self.cancelar_btn = QPushButton(" Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        
        main_layout.addLayout(button_layout)
        return content_container

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.header.underMouse():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    # O restante dos métodos (apply_styles, _create_input_with_icon, salvar_produto, etc.)
    # podem ser copiados da sua versão original, mas a apply_styles precisa de um ajuste.
    # Abaixo está a versão completa e corrigida dos métodos restantes.

    def apply_styles(self):
        theme = self.theme_colors
        if not theme: return

        style = f"""
            #mainContainer {{
                background-color: {theme.get('bg_color', '#fff')};
                border-radius: 16px;
                border: 1px solid {theme.get('border_color', '#ccc')};
            }}
            #header {{
                background-color: {theme.get('surface_color', '#f0f0f0')};
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid {theme.get('border_color', '#ccc')};
            }}
            #controlButton {{
                background-color: transparent; border: none; border-radius: 8px;
            }}
            #controlButton:hover {{
                background-color: {theme.get('button_hover', '#e0e0e0')};
            }}
            QGroupBox {{
                font-size: 11pt; border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 8px; margin-top: 15px; padding: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 10px; margin-left: 10px;
                background-color: {theme.get('bg_color', '#fff')};
                color: {theme.get('text_secondary', '#333')};
            }}
            QGroupBox:checked {{
                border-color: {theme.get('accent_color', '#007aff')};
            }}
            QLabel {{
                color: {theme.get('text_color', '#000')}; font-size: 10pt;
            }}
            #imagePreview {{
                border: 1px dashed {theme.get('border_color', '#ccc')};
                border-radius: 8px;
                color: {theme.get('text_secondary', '#666')};
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {theme.get('surface_color', '#f2f2f7')};
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 4px; padding: 8px; min-height: 20px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 2px solid {theme.get('accent_color', '#007aff')};
            }}
            QPushButton {{
                padding: 10px 15px; border-radius: 6px; font-weight: bold;
            }}
            #primaryActionButton {{
                background-color: {theme.get('accent_color', '#007aff')};
                color: white; border: none;
            }}
            #primaryActionButton:hover {{
                background-color: #0069d9;
            }}
             /* ESTILO PARA O DROPDOWN (POPUP) DO QCOMBOBOX */
            QComboBox QAbstractItemView {{
                background-color: {theme.get('surface_color', '#333')};
                color: {theme.get('text_color', '#fff')};
                border: 1px solid {theme.get('border_color', '#555')};
                selection-background-color: {theme.get('accent_color', '#007aff')};
                selection-color: white;
                outline: 0px; /* Remove a borda pontilhada de foco */
            }}

            /* ESTILO PARA A BARRA DE ROLAGEM DENTRO DO DROPDOWN */
            QComboBox QScrollBar:vertical {{
                border: none;
                background: {theme.get('surface_color', '#333')};
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QComboBox QScrollBar::handle:vertical {{
                background: {theme.get('border_color', '#555')};
                min-height: 20px;
                border-radius: 5px;
            }}
            QComboBox QScrollBar::add-line:vertical, QComboBox QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        self.setStyleSheet(style)
        
        self.salvar_btn.setIcon(IconManager.get_icon('save', 'white'))
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', theme.get('text_color', '#000')))

    def _create_input_with_icon(self, icon_name, widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        icon_label.setPixmap(IconManager.get_icon(icon_name, color=icon_color).pixmap(16, 16))
        
        layout.addWidget(icon_label)
        layout.addWidget(widget, 1)
        return container

    def carregar_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Selecione ou crie uma categoria", "")
        categorias = self.db.listar_categorias_unicas()
        for categoria in categorias:
            self.categoria_combo.addItem(categoria, categoria)
    
    def carregar_fornecedores(self):
        self.fornecedor_combo.clear()
        self.fornecedor_combo.addItem("Selecione um fornecedor", None)
        fornecedores = self.db.listar_fornecedores()
        for fornecedor in fornecedores:
            self.fornecedor_combo.addItem(fornecedor['empresa'], fornecedor['id'])
    
    # --- MUDANÇA 3: Novo método para carregar e autocompletar localizações ---
    def carregar_localizacoes(self):
        """Carrega as localizações e configura o autocompletar."""
        self.localizacao_input.clear()
        self.localizacao_input.addItem("") # Item vazio para o placeholder
        
        localizacoes = self.db.listar_localizacoes_unicas()
        self.localizacao_input.addItems(localizacoes)
        
        # Configura o autocompletar
        completer = QCompleter(localizacoes, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        self.localizacao_input.setCompleter(completer)
    # --- FIM DA MUDANÇA 3 ---

    def calcular_preco_venda(self):
        preco_compra = self.preco_compra_input.value()
        margem = self.margem_lucro_input.value() / 100
        preco_venda = preco_compra * (1 + margem)
        self.preco_venda_input.blockSignals(True)
        self.preco_venda_input.setValue(preco_venda)
        self.preco_venda_input.blockSignals(False)

    def calcular_margem_lucro(self):
        preco_compra = self.preco_compra_input.value()
        preco_venda = self.preco_venda_input.value()
        if preco_compra > 0:
            margem = ((preco_venda / preco_compra) - 1) * 100
            self.margem_lucro_input.blockSignals(True)
            self.margem_lucro_input.setValue(margem)
            self.margem_lucro_input.blockSignals(False)
    
    def carregar_dados_produto(self):
        self.codigo_barras_input.setText(self.produto['codigo_barras'] or "")
        self.nome_input.setText(self.produto['nome'])
        self.descricao_input.setText(self.produto['descricao'] or "")
        self.quantidade_input.setValue(self.produto['quantidade'])
        self.estoque_minimo_input.setValue(self.produto['estoque_minimo'] or 0)
        self.preco_compra_input.setValue(self.produto['preco_compra'])
        self.margem_lucro_input.setValue(self.produto['margem_lucro'] or 30.0)
        self.preco_venda_input.setValue(self.produto['preco_venda'])
        if self.produto['data_validade']:
            self.data_validade_input.setDate(QDate.fromString(self.produto['data_validade'], "yyyy-MM-dd"))
         # --- MUDANÇA 4: Atualizar a forma de carregar a localização ---
        if self.produto['localizacao']:
            self.localizacao_input.setCurrentText(self.produto['localizacao'])
        # --- FIM DA MUDANÇA 4 ---
        
        if self.produto['fornecedor_id']:
            index = self.fornecedor_combo.findData(self.produto['fornecedor_id'])
            if index != -1: self.fornecedor_combo.setCurrentIndex(index)
        
        if self.produto['categoria']:
            index = self.categoria_combo.findText(self.produto['categoria'])
            if index != -1: self.categoria_combo.setCurrentIndex(index)
            else:
                self.categoria_combo.addItem(self.produto['categoria'])
                self.categoria_combo.setCurrentText(self.produto['categoria'])
        
        is_fracionado = bool(self.produto['fracionado'])
        self.fracionado_group.setChecked(is_fracionado)
        
        if is_fracionado:
            self.unidade_medida_input.setText(self.produto['unidade_medida'] or "")
            self.qtd_por_embalagem_input.setValue(int(self.produto['qtd_por_embalagem'] or 1))
            self.preco_unitario_fracao_input.setValue(self.produto['preco_unitario_fracao'] or 0.0)
            self.estoque_fracionado_input.setValue(int(self.produto['estoque_fracionado'] or 0))
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Substituímos o uso de .get() pela verificação das chaves do objeto sqlite3.Row
        if 'imagem_path' in self.produto.keys() and self.produto['imagem_path']:
            self.imagem_path = self.produto['imagem_path']
            self.carregar_preview_imagem(self.imagem_path)

    def salvar_produto(self):
        if not self.nome_input.text().strip():
            AlertDialog(self, "Campo Obrigatório", "O nome do produto é obrigatório!", alert_type='warning', theme_colors=self.theme_colors).exec_()           
            return
            
        dados = {
            'codigo_barras': self.codigo_barras_input.text().strip(),
            'nome': self.nome_input.text().strip(),
            'descricao': self.descricao_input.text().strip(),
            'categoria': self.categoria_combo.currentText().strip() if self.categoria_combo.currentText() != "Selecione ou crie uma categoria" else None,
            'fornecedor_id': self.fornecedor_combo.currentData(),
            'quantidade': self.quantidade_input.value(),
            'estoque_minimo': self.estoque_minimo_input.value(),
            'preco_compra': self.preco_compra_input.value(),
            'margem_lucro': self.margem_lucro_input.value(),
            'preco_venda': self.preco_venda_input.value(),
            'data_validade': self.data_validade_input.date().toString("yyyy-MM-dd"),
            'localizacao': self.localizacao_input.currentText().strip(),
            'imagem_path': self.imagem_path,
            'fracionado': self.fracionado_group.isChecked(),
            'unidade_medida': self.unidade_medida_input.text().strip() if self.fracionado_group.isChecked() else 'unidade',
            'qtd_por_embalagem': self.qtd_por_embalagem_input.value() if self.fracionado_group.isChecked() else 1,
            'preco_unitario_fracao': self.preco_unitario_fracao_input.value() if self.fracionado_group.isChecked() else 0.0,
            'estoque_fracionado': self.estoque_fracionado_input.value() if self.fracionado_group.isChecked() else 0,
        }
        
        try:
            if self.produto_id:
                sucesso = self.db.atualizar_produto(self.produto_id, **dados)
                mensagem = "Produto atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_produto(**dados)
                mensagem = "Produto cadastrado com sucesso!"
            
            if sucesso:
                # Chamada corrigida (a que causou o primeiro erro)
                AlertDialog(self, "Sucesso", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()
                self.accept()
            else:
                # Chamada corrigida
                AlertDialog(self, "Erro no Banco de Dados", "Não foi possível salvar o produto.", alert_type='error', theme_colors=self.theme_colors).exec_()
        except Exception as e:
            # Chamada corrigida (a que causou o segundo erro)
            AlertDialog(self, "Erro Inesperado", f"Ocorreu um erro: {e}", alert_type='error', theme_colors=self.theme_colors).exec_()

    def selecionar_imagem(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Imagem do Produto", os.path.expanduser("~"),
            "Arquivos de Imagem (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path:
            self.imagem_path = file_path
            self.carregar_preview_imagem(self.imagem_path)

    def carregar_preview_imagem(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            self.imagem_preview_label.setPixmap(pixmap.scaled(
                200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))
        else:
            self.imagem_preview_label.setText("Nenhuma imagem")
            self.imagem_preview_label.setPixmap(QPixmap())

# ================================================================= #
#       CLASSE DIALOGQUEBRAREMBALAGEM TOTALMENTE CORRIGIDA          #
# ================================================================= #
# Substitua a classe DialogQuebrarEmbalagem inteira em estoque_window.py

class DialogQuebrarEmbalagem(QDialog):
    def __init__(self, db, produto_info, theme_colors=None, logo_pixmap=None):
        super().__init__()
        self.db = db
        self.produto_info = produto_info
        self.theme_colors = theme_colors if theme_colors else {}
        self.logo_pixmap = logo_pixmap
        self.drag_position = None

        # Tornar a janela sem borda
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.initUI()
        self.apply_styles()

    def initUI(self):
        self.setWindowTitle("Quebrar Embalagem")
        self.setMinimumWidth(500)
        
        # Container principal para o estilo
        container = QFrame(self)
        container.setObjectName("mainContainer")

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Adiciona o cabeçalho customizado
        self.header = self._create_header()
        main_layout.addWidget(self.header)
        
        # Conteúdo do formulário
        main_layout.addWidget(self._create_content())

        # Adiciona o container ao layout do QDialog
        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(container)
    
    def _create_header(self):
        header_widget = QFrame()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(50)
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        
        if self.logo_pixmap:
            logo_label = QLabel()
            logo_label.setPixmap(self.logo_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(logo_label)

        title_label = QLabel("Quebrar Embalagem")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {self.theme_colors['text_color']};")
        
        close_button = QPushButton()
        close_button.setObjectName("controlButton")
        close_button.setFixedSize(30, 30)
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors['text_secondary']))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        return header_widget

    def _create_content(self):
        content_container = QWidget()
        layout = QVBoxLayout(content_container)
        layout.setContentsMargins(20, 15, 20, 20)

        info_group = QGroupBox("Informações do Produto")
        info_layout = QFormLayout(info_group)
        info_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        info_layout.setSpacing(15)

        info_layout.addRow(self._create_info_row('box', "Produto:", self.produto_info['nome']))
        info_layout.addRow(self._create_info_row('estoque', "Embalagens disponíveis:", str(self.produto_info['embalagens_inteiras'])))
        info_layout.addRow(self._create_info_row('box-open', "Unidades por embalagem:", str(self.produto_info['qtd_por_embalagem'])))
        info_layout.addRow(self._create_info_row('cubes', "Estoque fracionado atual:", f"{self.produto_info['estoque_fracionado']} {self.produto_info['unidade_medida']}"))
        
        layout.addWidget(info_group)
        
        quebrar_group = QGroupBox("Quebrar Embalagens")
        quebrar_layout = QFormLayout(quebrar_group)
        quebrar_layout.setSpacing(15)
        
        self.quantidade_input = QSpinBox()
        self.quantidade_input.setRange(1, self.produto_info['embalagens_inteiras'])
        self.quantidade_input.setValue(1)
        self.quantidade_input.valueChanged.connect(self.atualizar_preview)
        
        quebrar_layout.addRow("Quantidade a quebrar:", self._create_input_with_icon('break', self.quantidade_input))
        
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("font-style: italic;")
        self.atualizar_preview()
        quebrar_layout.addRow("Resultado:", self._create_info_row('check', "Novo estoque:", self.preview_label))
        
        layout.addWidget(quebrar_group)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.confirmar_btn = QPushButton(" Confirmar")
        self.confirmar_btn.setObjectName("primaryActionButton")
        self.confirmar_btn.clicked.connect(self.quebrar_embalagem)
        
        self.cancelar_btn = QPushButton(" Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.confirmar_btn)
    
        layout.addLayout(button_layout)
        return content_container

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.header.underMouse():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def apply_styles(self):
        theme = self.theme_colors
        if not theme: return

        style = f"""
            #mainContainer {{
                background-color: {theme.get('bg_color', '#fff')};
                border-radius: 16px;
                border: 1px solid {theme.get('border_color', '#ccc')};
            }}
            #header {{
                background-color: {theme.get('surface_color', '#f0f0f0')};
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid {theme.get('border_color', '#ccc')};
            }}
            #controlButton {{
                background-color: transparent; border: none; border-radius: 8px;
            }}
            #controlButton:hover {{
                background-color: {theme.get('button_hover', '#e0e0e0')};
            }}
            QGroupBox {{
                font-size: 10pt; border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 8px; margin-top: 15px; padding: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 10px; margin-left: 10px;
                background-color: {theme.get('bg_color', '#fff')};
                color: {theme.get('text_secondary', '#333')};
            }}
            QLabel {{ color: {theme.get('text_color', '#000')}; font-size: 10pt; }}
            QSpinBox {{
                background-color: {theme.get('surface_color', '#f2f2f7')};
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 4px; padding: 8px; min-height: 20px;
            }}
            QSpinBox:focus {{ border: 2px solid {theme.get('accent_color', '#007aff')}; }}
            QPushButton {{ padding: 10px 15px; border-radius: 6px; font-weight: bold; }}
            #primaryActionButton {{
                background-color: {theme.get('accent_color', '#007aff')}; color: white; border: none;
            }}
            #primaryActionButton:hover {{ background-color: #0069d9; }}
        """
        self.setStyleSheet(style)
        
        self.confirmar_btn.setIcon(IconManager.get_icon('confirm', 'white'))
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', theme.get('text_color', '#000')))

    def atualizar_preview(self):
        qtd_quebrar = self.quantidade_input.value()
        unidades_geradas = qtd_quebrar * self.produto_info['qtd_por_embalagem']
        novo_estoque_fracionado = self.produto_info['estoque_fracionado'] + unidades_geradas
        novas_embalagens = self.produto_info['embalagens_inteiras'] - qtd_quebrar
        
        preview_text = (f"{novas_embalagens} emb. + {novo_estoque_fracionado} {self.produto_info['unidade_medida']}"
                        f"\n(Serão geradas +{unidades_geradas} unidades)")
        self.preview_label.setText(preview_text)
        
    def _create_input_with_icon(self, icon_name, widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        icon_label.setPixmap(IconManager.get_icon(icon_name, color=icon_color).pixmap(16, 16))
        
        layout.addWidget(icon_label)
        layout.addWidget(widget, 1)
        return container

    def _create_info_row(self, icon_name, label_text, info_text_or_widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        icon_label.setPixmap(IconManager.get_icon(icon_name, color=icon_color).pixmap(16, 16))
        
        field_label = QLabel(label_text)
        field_label.setStyleSheet("font-weight: bold;")
        
        layout.addWidget(icon_label)
        layout.addWidget(field_label)
        
        if isinstance(info_text_or_widget, QWidget):
            layout.addWidget(info_text_or_widget, 1)
        else:
            info_label = QLabel(str(info_text_or_widget))
            info_label.setWordWrap(True)
            layout.addWidget(info_label, 1)
            
        return container
    
    def quebrar_embalagem(self):
        qtd_quebrar = self.quantidade_input.value()
        # Chamada corrigida
        dialog = AlertDialog(self, "Confirmar Quebra",
                                f"Confirma quebrar {qtd_quebrar} embalagem(ns) em unidades?",
                                alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            if self.db.quebrar_embalagem(self.produto_info['produto_id'], qtd_quebrar):
                # Chamada corrigida
                AlertDialog(self, "Sucesso", "Embalagem quebrada com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
                self.accept()
            else:
                # Chamada corrigida
                AlertDialog(self, "Erro", "Não foi possível quebrar a embalagem.", alert_type='error', theme_colors=self.theme_colors).exec_()