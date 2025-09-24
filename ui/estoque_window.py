from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QSpinBox,
                           QDoubleSpinBox, QDialog, QFrame, QToolButton, QGroupBox,
                           QFileDialog, QCheckBox, QProgressDialog, QGridLayout, QProgressBar, QCompleter)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush, QPixmap
from PyQt5.QtMultimedia import QSoundEffect
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import Image 
from collections import defaultdict
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
import csv
import qtawesome as qta
import math
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager 

class AlertDialog(QDialog):
    """Caixa de diálogo com o estilo sutil da tela de perfil."""
    
    # --- NOVO: Player de som como atributo de classe ---
    # Isso garante que o arquivo de som seja carregado apenas uma vez.
    success_sound_player = None

    def __init__(self, parent, title, message, alert_type='info', buttons=QMessageBox.Ok, theme_colors=None):
        super().__init__(parent)
        
        # --- LÓGICA DE EFEITO SONORO ---
        # Toca um som se a mensagem for de sucesso.
        if alert_type == 'success':
            # Inicializa o player na primeira vez que for necessário.
            if AlertDialog.success_sound_player is None:
                # IMPORTANTE: Crie esta pasta e coloque um arquivo de som nela.
                # O caminho deve ser: 'assets/sounds/success.wav'
                sound_file_path = "assets/sounds/success.wav"
                
                if os.path.exists(sound_file_path):
                    AlertDialog.success_sound_player = QSoundEffect()
                    AlertDialog.success_sound_player.setSource(QUrl.fromLocalFile(sound_file_path))
                    # Ajuste o volume conforme necessário (0.0 a 1.0)
                    AlertDialog.success_sound_player.setVolume(0.4) 
                else:
                    # Imprime um aviso no console se o arquivo não for encontrado.
                    print(f"Aviso: Arquivo de som de sucesso não encontrado em '{sound_file_path}'")
                    # Marca como 'False' para não tentar carregar de novo.
                    AlertDialog.success_sound_player = False

            # Se o player foi carregado com sucesso, toca o som.
            if AlertDialog.success_sound_player:
                AlertDialog.success_sound_player.play()
        # --- FIM DA LÓGICA DE EFEITO SONORO ---

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

class CsvImportWorker(QThread):
    progress = pyqtSignal(int)
    # Adicionamos 'atualizados' ao sinal de conclusão
    finished = pyqtSignal(int, int, int, list) # importados, atualizados, erros, detalhes

    def __init__(self, db_path, file_path):
        super().__init__()
        self.db_path = db_path
        self.file_path = file_path
        self.local_db = None

    # --- FUNÇÕES AUXILIARES (sem alteração) ---
    def _extrair_preco(self, value_str, default=0.0):
        try:
            if isinstance(value_str, (int, float)): return float(value_str)
            s = str(value_str).strip().replace("R$", "").strip()
            if not s: return default
            if ',' in s and '.' in s:
                if s.rfind(',') > s.rfind('.'): s = s.replace('.', '').replace(',', '.')
                else: s = s.replace(',', '')
            else: s = s.replace(',', '.')
            return float(s)
        except (ValueError, TypeError): return default
            
    def _extrair_margem(self, value_str, default=0.0):
        s = str(value_str).replace('%', '').strip()
        return self._extrair_preco(s, default)

    def _parse_int(self, value_str, default=0):
        try:
            if isinstance(value_str, (int, float)): return int(value_str)
            import re
            match = re.match(r'\d+', str(value_str).strip())
            return int(match.group(0)) if match else default
        except (ValueError, TypeError): return default

    def _formatar_codigo_barras(self, value_str):
        try:
            s = str(value_str).strip()
            if 'e' not in s.lower(): return s
            s_corrigido = s.replace(',', '.')
            numero_completo = int(float(s_corrigido))
            return str(numero_completo)
        except (ValueError, TypeError):
            return str(value_str).strip()

    def _get_column_mapping(self, fieldnames):
        POSSIBLE_MAPPINGS = { 'nome': ['nome', 'Nome', 'produto', 'Produto', 'Descrição do Produto'], 'codigo_barras': ['codigo_barras', 'Código de Barras', 'EAN', 'codigo'], 'descricao': ['descricao', 'Descrição'], 'quantidade': ['quantidade', 'Quantidade', 'estoque', 'Estoque', 'estoque_detalhado'], 'estoque_minimo': ['estoque_minimo', 'Estoque Mínimo', 'Estoque Minimo'], 'preco_compra': ['preco_compra', 'Preço de Compra', 'Preco de Compra', 'Custo'], 'margem_lucro': ['margem_lucro', 'margem', 'Margem', 'Margem de Lucro (%)'], 'preco_venda': ['preco_venda', 'Preço de Venda', 'Preco de Venda'], 'data_validade': ['data_validade', 'validade', 'Validade', 'Data de Validade'], 'localizacao': ['localizacao', 'Localização', 'Localizacao'], 'categoria': ['categoria', 'Categoria'], 'fracionado': ['fracionado', 'Fracionado'], 'unidade_medida': ['unidade_medida', 'Unidade de Medida'], 'qtd_por_embalagem': ['qtd_por_embalagem', 'Qtd por Embalagem', 'Quantidade por Embalagem', '_por_embalagem'], 'preco_unitario_fracao': ['preco_unitario_fracao', 'Preço Unitário Fração', 'Preco Unitario Fracao', '_unitario_fracao'], 'estoque_fracionado': ['estoque_fracionado', 'Estoque Fracionado'] }
        header_map = {}
        lower_fieldnames = {name.lower().strip(): name for name in fieldnames}
        for internal_key, possible_names in POSSIBLE_MAPPINGS.items():
            for name in possible_names:
                if name.lower() in lower_fieldnames: header_map[internal_key] = lower_fieldnames[name.lower()]; break
        if 'nome' not in header_map: raise ValueError("A coluna 'nome' do produto é obrigatória no CSV.")
        return header_map

    def _formatar_data_validade(self, data_str):
        if not data_str or not str(data_str).strip(): return None
        try:
            data_str = str(data_str).strip()
            if '/' in data_str: return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            return datetime.strptime(data_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except: return None

    def run(self):
        importados, atualizados, erros = 0, 0, 0
        erros_detalhes = []
        total_linhas = 0
        try:
            self.local_db = DatabaseManager(self.db_path)
            
            with open(self.file_path, 'r', encoding='utf-8-sig') as f:
                sample_lines = [next(f, '') for _ in range(10)]
                f.seek(0)
                total_linhas = max(1, sum(1 for line in f) - 1)
                sample = "".join(sample_lines)
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=',;')
            except csv.Error:
                header_line = sample.splitlines()[0] if sample.splitlines() else ""
                if ';' in header_line:
                    dialect = csv.excel; dialect.delimiter = ';'
                else:
                    dialect = csv.excel; dialect.delimiter = ','

            with open(self.file_path, 'r', encoding='utf-8-sig') as csvfile:
                reader = csv.DictReader(csvfile, dialect=dialect)
                header_map = self._get_column_mapping(reader.fieldnames)
                get_val = lambda row_data, key, default='': row_data.get(header_map.get(key), default)
                
                self.local_db.begin_transaction()
                for i, row in enumerate(reader):
                    try:
                        nome_produto = get_val(row, 'nome').strip()
                        if not nome_produto and not any(row.values()): continue
                        if not nome_produto: raise ValueError("Nome do produto é obrigatório")
                        
                        produto_data = {
                            'codigo_barras': self._formatar_codigo_barras(get_val(row, 'codigo_barras')), 'nome': nome_produto, 'descricao': get_val(row, 'descricao'), 'quantidade': self._parse_int(get_val(row, 'quantidade', '0')), 'estoque_minimo': self._parse_int(get_val(row, 'estoque_minimo', '0')), 'preco_compra': self._extrair_preco(get_val(row, 'preco_compra', '0')), 'margem_lucro': self._extrair_margem(get_val(row, 'margem_lucro', '0')), 'preco_venda': self._extrair_preco(get_val(row, 'preco_venda', '0')), 'data_validade': self._formatar_data_validade(get_val(row, 'data_validade', '')), 'localizacao': get_val(row, 'localizacao').strip() or None, 'fornecedor_id': None, 'categoria': get_val(row, 'categoria').strip() or None, 'fracionado': self._parse_int(get_val(row, 'fracionado', '0')), 'unidade_medida': get_val(row, 'unidade_medida', 'unidade').strip(), 'qtd_por_embalagem': self._parse_int(get_val(row, 'qtd_por_embalagem', '1'), 1), 'preco_unitario_fracao': self._extrair_preco(get_val(row, 'preco_unitario_fracao', '0')), 'estoque_fracionado': self._extrair_preco(get_val(row, 'estoque_fracionado', '0.0'))
                        }

                        produto_existente = None
                        codigo_barras_atual = produto_data.get('codigo_barras')
                        
                        if codigo_barras_atual:
                            produto_existente = self.local_db.buscar_produto_por_codigo_barras(codigo_barras_atual)

                        if produto_existente:
                            self.local_db.atualizar_produto(produto_existente['id'], **produto_data)
                            atualizados += 1
                        else:
                            self.local_db.adicionar_produto(**produto_data)
                            importados += 1
                        
                    except Exception as e:
                        erros += 1
                        erros_detalhes.append(f"Linha {i+2}: {get_val(row, 'nome', 'N/A')} - {str(e)}")
                    
                    if total_linhas > 0: self.progress.emit(int(((i + 1) / total_linhas) * 100))
                
                self.local_db.commit_transaction()
        except Exception as e:
            if self.local_db: self.local_db.rollback_transaction()
            erros_detalhes.append(f"Erro crítico na importação: {str(e)}")
        finally:
            if self.local_db: self.local_db.fechar()
        
        self.finished.emit(importados, atualizados, erros, erros_detalhes)
    
class EstoqueWindow(QWidget):
    dados_produtos_alterados = pyqtSignal()
    def __init__(self, db, theme_colors, settings, logo_pixmap=None):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.settings = settings  # Armazena o objeto de configurações corretamente
        self.logo_pixmap = logo_pixmap
        self.pagina_atual = 1
        self.itens_por_pagina = 100 
        self.total_paginas = 1

        # O resto do seu método __init__ continua igual...
        self.logo_path = "assets/img/Logo2.png"
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
        estoque_baixo_label = QLabel("Estoque Baixo"); estoque_baixo_label.setObjectName("legendaEstoqueBaixo")
        vencimento_30_label = QLabel("Vence em 30 dias"); vencimento_30_label.setObjectName("legendaVence30")
        vencimento_15_label = QLabel("Vence em 15 dias"); vencimento_15_label.setObjectName("legendaVence15")
        legenda_layout.addWidget(estoque_baixo_label)
        legenda_layout.addWidget(vencimento_30_label)
        legenda_layout.addWidget(vencimento_15_label)
        legenda_layout.addStretch()
        layout.addLayout(legenda_layout)
        
        self.tabela = QTableWidget()
        
        # --- CORREÇÃO APLICADA AQUI ---
        self.tabela.setColumnCount(13)
        self.tabela.setHorizontalHeaderLabels([
            "Código de Barras", "Nome", "Categoria", "Estoque Detalhado", 
            "Estoque Mín.", "Estoque Máx.", # Colunas Corrigidas
            "Preço Compra", "Margem %", "Preço Venda", "Validade", 
            "Localização", "Fornecedor", "Ações"
        ])
        # --- FIM DA CORREÇÃO ---
        
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        paginacao_layout = QHBoxLayout()
        paginacao_layout.setAlignment(Qt.AlignCenter)
        self.prev_page_btn = QPushButton(" Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
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
        hoje = datetime.now().date()

        for row, produto in enumerate(produtos):
            self.tabela.insertRow(row)
            
            # --- CORREÇÃO PRINCIPAL APLICADA AQUI ---
            # Agora usamos produto.get() de forma segura, pois 'produto' é um dicionário.
            # E os índices das colunas estão corrigidos.
            
            # Coluna 0: Código de Barras
            self.tabela.setItem(row, 0, QTableWidgetItem(produto.get('codigo_barras', '')))
            
            # Coluna 1: Nome
            nome_produto = produto.get('nome', 'N/A')
            if produto.get('fracionado'):
                nome_produto += f" (Frac. - {produto.get('unidade_medida', 'un')})"
            self.tabela.setItem(row, 1, QTableWidgetItem(nome_produto))
            
            # Coluna 2: Categoria
            self.tabela.setItem(row, 2, QTableWidgetItem(produto.get('categoria', "N/A")))
            
            # Coluna 3: Estoque Detalhado
            quantidade = produto.get('quantidade', 0)
            estoque_minimo = produto.get('estoque_minimo', 0)
            quantidade_display = str(quantidade)
            if produto.get('fracionado'):
                quantidade_display = f"{quantidade} emb. + {produto.get('estoque_fracionado', 0)} {produto.get('unidade_medida', 'un')}"
            
            quantidade_item = QTableWidgetItem(quantidade_display)
            if estoque_minimo > 0 and quantidade <= estoque_minimo:
                quantidade_item.setForeground(QBrush(QColor('red')))
                quantidade_item.setToolTip("ESTOQUE ABAIXO DO MÍNIMO!")
            self.tabela.setItem(row, 3, quantidade_item)
            
            # Coluna 4: Estoque Mínimo (Calculado)
            self.tabela.setItem(row, 4, QTableWidgetItem(str(estoque_minimo)))
            
            # Coluna 5: Estoque Máximo (Calculado) - NOVA
            self.tabela.setItem(row, 5, QTableWidgetItem(str(produto.get('estoque_maximo', 0))))
            
            # Colunas restantes com índices ajustados
            self.tabela.setItem(row, 6, QTableWidgetItem(f"R$ {produto.get('preco_compra', 0):.2f}"))
            self.tabela.setItem(row, 7, QTableWidgetItem(f"{produto.get('margem_lucro', 0):.2f}%"))
            
            preco_venda_display = f"R$ {produto.get('preco_venda', 0):.2f}"
            if produto.get('fracionado') and produto.get('preco_unitario_fracao', 0):
                preco_venda_display = f"Emb: {preco_venda_display} | Un: R$ {produto.get('preco_unitario_fracao', 0):.2f}"
            self.tabela.setItem(row, 8, QTableWidgetItem(preco_venda_display))
            
            # Lógica de validade (sem alteração, mas com índice corrigido)
            validade_str = produto.get('data_validade', '')
            validade_item = QTableWidgetItem(validade_str)
            if validade_str:
                try:
                    data_validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
                    dias = (data_validade - hoje).days
                    if dias <= 0: validade_item.setForeground(QBrush(QColor('darkred')))
                    elif dias <= 15: validade_item.setForeground(QBrush(QColor('red')))
                    elif dias <= 30: validade_item.setForeground(QBrush(QColor('orange')))
                except ValueError: pass # Ignora datas mal formatadas
            self.tabela.setItem(row, 9, validade_item)

            self.tabela.setItem(row, 10, QTableWidgetItem(produto.get('localizacao', '')))
            self.tabela.setItem(row, 11, QTableWidgetItem(produto.get('fornecedor_nome', "N/A")))
            
            # Coluna 12: Ações (sem alteração na lógica, apenas no índice)
            self.tabela.setCellWidget(row, 12, self.criar_botoes_acao(produto))

    def criar_botoes_acao(self, produto):
        """Função auxiliar para criar os botões de ação para a tabela."""
        acoes_widget = QWidget()
        acoes_layout = QHBoxLayout(acoes_widget)
        acoes_layout.setContentsMargins(0, 0, 0, 0)
        acoes_layout.setSpacing(5)
        
        icon_color = self.theme_colors.get('text_color', '#000')
        hover_color = self.theme_colors.get('button_hover', '#555555')
        
        editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), "")
        editar_btn.setToolTip("Editar Produto")
        editar_btn.clicked.connect(lambda _, p_id=produto['id']: self.abrir_formulario_produto(p_id))
        
        excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), "")
        excluir_btn.setToolTip("Excluir Produto")
        excluir_btn.clicked.connect(lambda _, p_id=produto['id']: self.excluir_produto(p_id))
        
        for btn in [editar_btn, excluir_btn]:
            btn.setFixedSize(30, 30); btn.setFlat(True); btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"QPushButton:hover {{ background-color: {hover_color}; }}")
        
        acoes_layout.addWidget(editar_btn)
        acoes_layout.addWidget(excluir_btn)
        
        if produto.get('fracionado') and produto.get('quantidade', 0) > 0:
            quebrar_btn = QPushButton(IconManager.get_icon('break', icon_color), "")
            quebrar_btn.setToolTip("Quebrar embalagem")
            quebrar_btn.setFixedSize(30, 30); quebrar_btn.setFlat(True); quebrar_btn.setCursor(Qt.PointingHandCursor)
            quebrar_btn.setStyleSheet(f"QPushButton:hover {{ background-color: {hover_color}; }}")
            quebrar_btn.clicked.connect(lambda _, p_id=produto['id']: self.abrir_dialog_quebrar_embalagem(p_id))
            acoes_layout.addWidget(quebrar_btn)
            
        return acoes_widget
    
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

    def _gerar_pdf_com_template(self, file_path, report_title, elementos, company_info, custom_logo_path):
        try:
            left_margin, right_margin, top_margin, bottom_margin = 2*cm, 2*cm, 3.5*cm, 1.5*cm

            def header_footer(canvas, doc):
                canvas.saveState()
                
                # --- INÍCIO DA CORREÇÃO: Lógica de Cabeçalho com Tabela ---
                
                # 1. Prepara os elementos para o cabeçalho
                styles = getSampleStyleSheet()
                style_info = ParagraphStyle(name='Info', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=9, leading=12)
                
                # Elemento 1: Logo do Sistema
                system_logo_path = "assets/img/Logo2.png"
                logo_sistema = Image(system_logo_path, width=2.5*cm, height=1.2*cm, kind='proportional') if os.path.exists(system_logo_path) else Spacer(0,0)
                
                # Elemento 2: Logo Personalizada
                logo_cliente = Image(custom_logo_path, width=2.5*cm, height=1.2*cm, kind='proportional') if custom_logo_path and os.path.exists(custom_logo_path) else Spacer(0,0)

                # Elemento 3: Bloco de Informações da Empresa (como Parágrafos)
                info_elements = []
                if company_info.get('empresa_nome'):
                    info_elements.append(Paragraph(company_info['empresa_nome'], style_info))
                if company_info.get('empresa_endereco'):
                    info_elements.append(Paragraph(company_info['empresa_endereco'], style_info))
                if company_info.get('empresa_telefone') or company_info.get('empresa_email'):
                    contato_str = f"Telefone: {company_info.get('empresa_telefone', '')} | Email: {company_info.get('empresa_email', '')}"
                    info_elements.append(Paragraph(contato_str, style_info))
                if company_info.get('empresa_cnpj'):
                    info_elements.append(Paragraph(f"CNPJ: {company_info.get('empresa_cnpj')}", style_info))

                # 2. Monta a tabela do cabeçalho com 3 colunas
                header_data = [[logo_sistema, logo_cliente, info_elements]]
                
                # A largura total disponível é a largura da página menos as margens
                available_width = doc.width
                
                header_table = Table(header_data, colWidths=[3*cm, 3*cm, available_width - 6*cm])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # ALINHAMENTO VERTICAL CENTRALIZADO
                    ('ALIGN', (0, 0), (1, 0), 'LEFT'),      # Logos alinhadas à esquerda
                    ('ALIGN', (2, 0), (2, 0), 'RIGHT'),     # Bloco de texto alinhado à direita
                ]))
                
                # 3. Desenha a tabela no canvas
                w, h = header_table.wrap(doc.width, doc.topMargin)
                header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h + 0.5*cm) # Ajuste fino da posição vertical
                
                # 4. Desenha a linha ABAIXO da tabela
                line_y = doc.height + doc.topMargin - h
                canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
                canvas.line(doc.leftMargin, line_y, doc.width + doc.leftMargin, line_y)

                # --- FIM DA CORREÇÃO ---

                # Rodapé (sem alteração)
                canvas.setFont('Helvetica-Oblique', 8)
                canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 20, f"Página {canvas.getPageNumber()} | {report_title}")
                canvas.restoreState()

            doc = SimpleDocTemplate(file_path, pagesize=A4, topMargin=top_margin, bottomMargin=bottom_margin, leftMargin=left_margin, rightMargin=right_margin)
            doc.build(elementos, onFirstPage=header_footer, onLaterPages=header_footer)
            
            AlertDialog(self, "Sucesso", f"Relatório salvo com sucesso em:\n{file_path}", alert_type='success', theme_colors=self.theme_colors).exec_()

        except Exception as e:
            AlertDialog(self, "Erro ao Gerar PDF", f"Ocorreu um erro inesperado: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()


    def relatorio_vencimentos(self):
        produtos = self.db.verificar_produtos_vencendo(dias=30)
        if not produtos:
            AlertDialog(self, "Relatório", "Não há produtos vencendo nos próximos 30 dias.", 
                        alert_type='info', theme_colors=self.theme_colors).exec_()
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório...", os.path.expanduser("~/relatorio_vencimentos.pdf"), "PDF Files (*.pdf)")
        if file_path:
            # Passa os novos dados para a função de geração
            company_info = self.db.obter_informacoes_empresa()
            custom_logo_path = self.settings.get_value("custom_logo_path", "")
            self.gerar_pdf_vencimentos(produtos, file_path, company_info, custom_logo_path)

    def gerar_pdf_vencimentos(self, produtos, file_path, company_info, custom_logo_path):
        styles = getSampleStyleSheet()
        elementos = []

        elementos.append(Paragraph("Relatório de Análise de Vencimentos", styles['h1']))
        elementos.append(Paragraph(f"Período de Análise: Próximos 30 dias (a partir de {datetime.now().strftime('%d/%m/%Y')})", styles['Normal']))
        elementos.append(Spacer(1, 0.8 * cm))
        
        hoje = datetime.now().date()
        total_unidades = sum(p['quantidade'] for p in produtos)
        valor_custo_risco = sum(p['quantidade'] * (p['preco_compra'] or 0) for p in produtos)
        
        # Garante que a lista de produtos não está vazia antes de usar min()
        if not produtos:
            # Se por algum motivo a função for chamada com uma lista vazia, evitamos um erro.
            # Idealmente, a verificação anterior já impede isso.
            return 
            
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
        
        # A chamada final agora passa corretamente todos os parâmetros recebidos
        self._gerar_pdf_com_template(file_path, "Relatório de Vencimentos", elementos, company_info, custom_logo_path)

    def relatorio_estoque_baixo(self):
        produtos = self.db.verificar_produtos_estoque_baixo()
        if not produtos:
            AlertDialog(self, "Relatório", "Não há produtos com estoque abaixo do mínimo.", 
                        alert_type='info', theme_colors=self.theme_colors).exec_()
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar Relatório...", os.path.expanduser("~/relatorio_estoque_baixo.pdf"), "PDF Files (*.pdf)")
        if file_path:
            self.gerar_pdf_estoque_baixo(produtos, file_path) # Este já chama o template corretamente

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
        
         # --- LÓGICA CORRIGIDA E PERSONALIZÁVEL ---
        fator_reposicao = int(self.db.obter_configuracao('fator_reposicao_estoque', 5))
        
        produtos_por_fornecedor = defaultdict(list)
        for p in produtos: produtos_por_fornecedor[p['fornecedor_nome'] or "Fornecedor Não Definido"].append(p)
        
        # Recalcula o custo com base na nova sugestão de compra
        custo_reposicao = sum(
            p['preco_compra'] * (max(0, (p['estoque_minimo'] + fator_reposicao) - p['quantidade']))
            for p in produtos if p['preco_compra']
        )
        # --- FIM DA CORREÇÃO ---

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
                # --- LÓGICA CORRIGIDA AQUI ---
                qtd_sugerida = max(0, (p['estoque_minimo'] + fator_reposicao) - p['quantidade'])
                # --- FIM DA CORREÇÃO ---
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
            
        # Pega as informações e a logo para passar para o template
        company_info = self.db.obter_informacoes_empresa()
        custom_logo_path = self.settings.get_value("custom_logo_path", "")
        self._gerar_pdf_com_template(file_path, "Plano de Reposição de Estoque", elementos, company_info, custom_logo_path)

    def exportar_csv(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Estoque para CSV", 
                os.path.expanduser(f"~/estoque_{datetime.now().strftime('%Y%m%d')}.csv"),
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return
            
            produtos = self.db.listar_produtos()
            if not produtos:
                AlertDialog(self, "Exportação", "Não há produtos para exportar.", 
                            alert_type='info', theme_colors=self.theme_colors).exec_()
                return

            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'nome', 'codigo_barras', 'descricao', 'categoria', 'quantidade', 'estoque_minimo',
                    'preco_compra', 'margem_lucro', 'preco_venda', 'data_validade', 'localizacao', 
                    'fornecedor_nome', 'fracionado', 'unidade_medida', 'qtd_por_embalagem', 
                    'preco_unitario_fracao', 'estoque_fracionado'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for produto in produtos:
                    produto_dict = dict(produto)
                    row_data = {}
                    for key in fieldnames:
                        value = produto_dict.get(key)
                        # --- CORREÇÃO PRINCIPAL DA EXPORTAÇÃO ---
                        # Formata explicitamente os campos de preço/float para usar ponto.
                        if key in ['preco_compra', 'margem_lucro', 'preco_venda', 'preco_unitario_fracao', 'estoque_fracionado']:
                            # Usa f-string para formatar com 2 casas decimais
                            row_data[key] = f"{float(value or 0.0):.2f}"
                        else:
                            row_data[key] = value if value is not None else ''
                    
                    writer.writerow(row_data)
            
            AlertDialog(self, "Sucesso", f"Dados exportados com sucesso para:\n{file_path}", 
                        alert_type='success', theme_colors=self.theme_colors).exec_()
            
        except Exception as e:
            AlertDialog(self, "Erro", f"Erro ao exportar CSV: {str(e)}", 
                        alert_type='error', theme_colors=self.theme_colors).exec_()

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

    def importacao_concluida(self, importados, atualizados, erros, detalhes_erros):
        self.progress_dialog.close()
        self.atualizar_visualizacao_dados()

        if importados > 0 or atualizados > 0:
            print("DEBUG: Importação CSV concluída. Emitindo sinal 'dados_produtos_alterados'.")
            self.dados_produtos_alterados.emit()

        mensagem = (f"Importação concluída!\n\n"
                    f"✔ Produtos novos criados: {importados}\n"
                    f"✔ Produtos existentes atualizados: {atualizados}\n"
                    f"❌ Linhas com erro: {erros}")
        
        if detalhes_erros:
            detalhes = "\n\nDetalhes dos problemas:\n" + "\n".join(detalhes_erros[:5])
            mensagem += detalhes
            
            alert_type = 'warning' if (importados > 0 or atualizados > 0) else 'error'
            titulo = "Importação Finalizada com Avisos" if alert_type == 'warning' else "Importação Falhou"
            AlertDialog(self, titulo, mensagem, alert_type=alert_type, theme_colors=self.theme_colors).exec_()
        else:
            AlertDialog(self, "Importação Concluída com Sucesso", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()

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
    
    def selecionar_item_por_id(self, item_id):
        """Encontra e seleciona um item na tabela com base no seu ID."""
        for row in range(self.tabela.rowCount()):
            item = self.tabela.item(row, 0)
            if item: # Garante que a célula não está vazia
                id_na_tabela = item.data(Qt.UserRole)
                if id_na_tabela == item_id:
                    self.tabela.selectRow(row)
                    self.tabela.scrollToItem(item, QTableWidget.ScrollHint.PositionAtCenter)
                    break

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
        
        container = QFrame(self)
        container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.header = self._create_header()
        main_layout.addWidget(self.header)
        main_layout.addWidget(self._create_content())

        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(container)

        self.preco_compra_input.valueChanged.connect(self.calcular_preco_venda)
        self.margem_lucro_input.valueChanged.connect(self.calcular_preco_venda)
        self.preco_venda_input.valueChanged.connect(self.calcular_margem_lucro)

    def _create_header(self):
        # Este método permanece o mesmo
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
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {self.theme_colors.get('text_color', '#000')};")
        
        close_button = QPushButton(IconManager.get_icon('fechar', color=self.theme_colors.get('text_secondary', '#666')), "")
        close_button.setObjectName("controlButton")
        close_button.setFixedSize(30, 30)
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        return header_widget

    def _create_content(self):
        content_container = QWidget()
        main_layout = QVBoxLayout(content_container)
        main_layout.setContentsMargins(20, 15, 20, 20)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # Coluna 1: Informações do Produto
        info_group = QGroupBox("Informações do Produto")
        info_form = QFormLayout(info_group)
        self.codigo_barras_input = QLineEdit()
        self.nome_input = QLineEdit()
        self.descricao_input = QLineEdit()
        self.categoria_combo = QComboBox(); self.categoria_combo.setEditable(True); self.carregar_categorias()
        self.fornecedor_combo = QComboBox(); self.carregar_fornecedores()
        self.localizacao_input = QComboBox(); self.localizacao_input.setEditable(True); self.carregar_localizacoes()
        info_form.addRow("Código de Barras:", self.codigo_barras_input)
        info_form.addRow("Nome do Produto:", self.nome_input)
        info_form.addRow("Descrição:", self.descricao_input)
        info_form.addRow("Categoria:", self.categoria_combo)
        info_form.addRow("Fornecedor:", self.fornecedor_combo)
        info_form.addRow("Localização:", self.localizacao_input)

        # Coluna 2: Precificação e Validade
        preco_group = QGroupBox("Precificação e Validade")
        preco_form = QFormLayout(preco_group)
        self.preco_compra_input = QDoubleSpinBox(); self.preco_compra_input.setRange(0, 99999.99); self.preco_compra_input.setPrefix("R$ ")
        self.margem_lucro_input = QDoubleSpinBox(); self.margem_lucro_input.setRange(0, 999.99); self.margem_lucro_input.setSuffix(" %")
        self.preco_venda_input = QDoubleSpinBox(); self.preco_venda_input.setRange(0, 99999.99); self.preco_venda_input.setPrefix("R$ ")
        self.data_validade_input = QDateEdit(calendarPopup=True); self.data_validade_input.setDisplayFormat("dd/MM/yyyy")
        preco_form.addRow("Preço de Compra:", self.preco_compra_input)
        preco_form.addRow("Margem de Lucro:", self.margem_lucro_input)
        preco_form.addRow("Preço de Venda:", self.preco_venda_input)
        preco_form.addRow("Data de Validade:", self.data_validade_input)

        # Coluna 3: Imagem
        imagem_group = QGroupBox("Imagem do Produto")
        imagem_layout = QVBoxLayout(imagem_group)
        self.imagem_preview_label = QLabel("Nenhuma imagem"); self.imagem_preview_label.setAlignment(Qt.AlignCenter); self.imagem_preview_label.setMinimumSize(200, 200); self.imagem_preview_label.setObjectName("imagePreview")
        self.selecionar_imagem_btn = QPushButton("Selecionar Imagem"); self.selecionar_imagem_btn.clicked.connect(self.selecionar_imagem)
        imagem_layout.addWidget(self.imagem_preview_label); imagem_layout.addWidget(self.selecionar_imagem_btn)

        grid_layout.addWidget(info_group, 0, 0)
        grid_layout.addWidget(preco_group, 0, 1)
        grid_layout.addWidget(imagem_group, 0, 2)

        # --- NOVA SEÇÃO: GESTÃO DE ESTOQUE ---
        estoque_group = QGroupBox("Gestão de Estoque")
        estoque_layout = QGridLayout(estoque_group)
        
        # Estoque Atual (Manual)
        estoque_layout.addWidget(QLabel("Estoque Atual:"), 0, 0)
        self.quantidade_input = QSpinBox(); self.quantidade_input.setRange(0, 99999)
        estoque_layout.addWidget(self.quantidade_input, 0, 1)
        
        # Parâmetros para cálculo (Manual)
        estoque_layout.addWidget(QLabel("Tempo de Reposição:"), 1, 0)
        self.tempo_reposicao_input = QSpinBox(); self.tempo_reposicao_input.setRange(1, 365); self.tempo_reposicao_input.setSuffix(" dias")
        estoque_layout.addWidget(self.tempo_reposicao_input, 1, 1)

        estoque_layout.addWidget(QLabel("Lote de Reposição:"), 2, 0)
        self.lote_reposicao_input = QSpinBox(); self.lote_reposicao_input.setRange(1, 9999); self.lote_reposicao_input.setSuffix(" un.")
        estoque_layout.addWidget(self.lote_reposicao_input, 2, 1)

        # Campos Calculados (Apenas Display)
        label_style = "font-weight: bold; font-style: italic;"
        self.consumo_label = QLabel("0.0 un/dia"); self.consumo_label.setStyleSheet(label_style)
        self.estoque_min_label = QLabel("0"); self.estoque_min_label.setStyleSheet(label_style)
        self.estoque_max_label = QLabel("0"); self.estoque_max_label.setStyleSheet(label_style)
        
        estoque_layout.addWidget(QLabel("Consumo Médio Diário (Calculado):"), 0, 2)
        estoque_layout.addWidget(self.consumo_label, 0, 3)
        estoque_layout.addWidget(QLabel("Estoque Mínimo (Calculado):"), 1, 2)
        estoque_layout.addWidget(self.estoque_min_label, 1, 3)
        estoque_layout.addWidget(QLabel("Estoque Máximo (Calculado):"), 2, 2)
        estoque_layout.addWidget(self.estoque_max_label, 2, 3)
        
        grid_layout.addWidget(estoque_group, 1, 0, 1, 2)
        
        # Grupo de fracionamento
        self.fracionado_group = QGroupBox("Produto Fracionado"); self.fracionado_group.setCheckable(True); self.fracionado_group.setChecked(False)
        fracionado_form = QFormLayout(self.fracionado_group)
        self.unidade_medida_input = QLineEdit(); self.unidade_medida_input.setPlaceholderText("Ex: kg, L, m")
        self.qtd_por_embalagem_input = QSpinBox(); self.qtd_por_embalagem_input.setRange(1, 9999)
        self.preco_unitario_fracao_input = QDoubleSpinBox(); self.preco_unitario_fracao_input.setRange(0, 99999.99); self.preco_unitario_fracao_input.setPrefix("R$ ")
        self.estoque_fracionado_input = QSpinBox(); self.estoque_fracionado_input.setRange(0, 99999)
        fracionado_form.addRow("Unidade de Medida:", self.unidade_medida_input)
        fracionado_form.addRow("Unidades por Embalagem:", self.qtd_por_embalagem_input)
        fracionado_form.addRow("Preço Unitário (Fração):", self.preco_unitario_fracao_input)
        fracionado_form.addRow("Estoque Fracionado Atual:", self.estoque_fracionado_input)
        
        grid_layout.addWidget(self.fracionado_group, 1, 2)

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(" Salvar Produto"); self.salvar_btn.setObjectName("primaryActionButton"); self.salvar_btn.clicked.connect(self.salvar_produto)
        self.cancelar_btn = QPushButton(" Cancelar"); self.cancelar_btn.clicked.connect(self.reject)
        button_layout.addStretch(); button_layout.addWidget(self.cancelar_btn); button_layout.addWidget(self.salvar_btn)
        main_layout.addLayout(button_layout)
        
        return content_container

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
            # Passando os novos parâmetros
            'tempo_reposicao_dias': self.tempo_reposicao_input.value(),
            'lote_reposicao': self.lote_reposicao_input.value()
        }
        
        try:
            produto_salvo_id = None
            if self.produto_id:
                sucesso = self.db.atualizar_produto(self.produto_id, **dados)
                produto_salvo_id = self.produto_id
                mensagem = "Produto atualizado com sucesso!"
            else:
                produto_salvo_id = self.db.adicionar_produto(**dados)
                sucesso = produto_salvo_id is not None
                mensagem = "Produto cadastrado com sucesso!"
            
            if sucesso:
                # --- PASSO CRÍTICO: ATUALIZAR OS NÍVEIS APÓS SALVAR ---
                self.db.atualizar_niveis_estoque_calculado(produto_salvo_id)
                
                AlertDialog(self, "Sucesso", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()
                self.accept()
            else:
                AlertDialog(self, "Erro no Banco de Dados", "Não foi possível salvar o produto.", alert_type='error', theme_colors=self.theme_colors).exec_()
        except Exception as e:
            AlertDialog(self, "Erro Inesperado", f"Ocorreu um erro: {e}", alert_type='error', theme_colors=self.theme_colors).exec_()

    def carregar_dados_produto(self):
        # Carrega dados normais
        self.codigo_barras_input.setText(self.produto.get('codigo_barras', ""))
        self.nome_input.setText(self.produto['nome'])
        self.descricao_input.setText(self.produto.get('descricao', ""))
        self.quantidade_input.setValue(self.produto['quantidade'])
        self.preco_compra_input.setValue(self.produto['preco_compra'])
        self.margem_lucro_input.setValue(self.produto.get('margem_lucro', 30.0))
        self.preco_venda_input.setValue(self.produto['preco_venda'])
        if self.produto['data_validade']:
            self.data_validade_input.setDate(QDate.fromString(self.produto['data_validade'], "yyyy-MM-dd"))
        if self.produto['localizacao']:
            self.localizacao_input.setCurrentText(self.produto['localizacao'])
        
        # Carrega dados dos combos
        if self.produto['fornecedor_id']:
            index = self.fornecedor_combo.findData(self.produto['fornecedor_id'])
            if index != -1: self.fornecedor_combo.setCurrentIndex(index)
        if self.produto['categoria']:
            index = self.categoria_combo.findText(self.produto['categoria'])
            if index != -1: self.categoria_combo.setCurrentIndex(index)
            else: self.categoria_combo.addItem(self.produto['categoria']); self.categoria_combo.setCurrentText(self.produto['categoria'])
        
        # Carrega dados de fracionamento
        is_fracionado = bool(self.produto['fracionado'])
        self.fracionado_group.setChecked(is_fracionado)
        if is_fracionado:
            self.unidade_medida_input.setText(self.produto.get('unidade_medida', ""))
            self.qtd_por_embalagem_input.setValue(int(self.produto.get('qtd_por_embalagem', 1)))
            self.preco_unitario_fracao_input.setValue(self.produto.get('preco_unitario_fracao', 0.0))
            self.estoque_fracionado_input.setValue(int(self.produto.get('estoque_fracionado', 0)))
        
        # Carrega imagem
        if 'imagem_path' in self.produto.keys() and self.produto['imagem_path']:
            self.imagem_path = self.produto['imagem_path']
            self.carregar_preview_imagem(self.imagem_path)

        # --- CARREGA OS NOVOS DADOS DE ESTOQUE DINÂMICO ---
        self.tempo_reposicao_input.setValue(self.produto.get('tempo_reposicao_dias', 7))
        self.lote_reposicao_input.setValue(self.produto.get('lote_reposicao', 10))
        
        # Exibe os valores calculados
        self.consumo_label.setText(f"{self.produto.get('consumo_medio_diario', 0.0):.2f} un/dia")
        self.estoque_min_label.setText(str(self.produto.get('estoque_minimo', 0)))
        self.estoque_max_label.setText(str(self.produto.get('estoque_maximo', 0)))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.header.underMouse():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    # Mantenha os métodos abaixo como estão no seu código original
    def apply_styles(self):
        theme = self.theme_colors
        if not theme: return
        self.setStyleSheet(f"""
            #mainContainer {{ background-color: {theme.get('bg_color', '#fff')}; border-radius: 16px; border: 1px solid {theme.get('border_color', '#ccc')}; }}
            #header {{ background-color: {theme.get('surface_color', '#f0f0f0')}; border-top-left-radius: 16px; border-top-right-radius: 16px; border-bottom: 1px solid {theme.get('border_color', '#ccc')}; }}
            #controlButton:hover {{ background-color: {theme.get('button_hover', '#e0e0e0')}; }}
            QGroupBox {{ font-size: 11pt; border: 1px solid {theme.get('border_color', '#ccc')}; border-radius: 8px; margin-top: 15px; padding: 15px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 10px; margin-left: 10px; background-color: {theme.get('bg_color', '#fff')}; color: {theme.get('text_secondary', '#333')}; }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{ background-color: {theme.get('surface_color', '#f2f2f7')}; color: {theme.get('text_color', '#000')}; border: 1px solid {theme.get('border_color', '#ccc')}; border-radius: 4px; padding: 8px; min-height: 20px; }}
            QPushButton#primaryActionButton {{ background-color: {theme.get('accent_color', '#007aff')}; color: white; border: none; padding: 10px 15px; border-radius: 6px; font-weight: bold; }}
            #imagePreview {{ border: 1px dashed {theme.get('border_color', '#ccc')}; border-radius: 8px; color: {theme.get('text_secondary', '#666')}; }}
        """)
        self.salvar_btn.setIcon(IconManager.get_icon('save', 'white'))
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', theme.get('text_color', '#000')))

    def carregar_categorias(self):
        self.categoria_combo.clear(); self.categoria_combo.addItem("Selecione ou crie", ""); self.categoria_combo.addItems(self.db.listar_categorias_unicas())
    def carregar_fornecedores(self):
        self.fornecedor_combo.clear(); self.fornecedor_combo.addItem("Selecione", None)
        for f in self.db.listar_fornecedores(): self.fornecedor_combo.addItem(f['empresa'], f['id'])
    def carregar_localizacoes(self):
        self.localizacao_input.clear(); self.localizacao_input.addItem(""); self.localizacao_input.addItems(self.db.listar_localizacoes_unicas())
        self.localizacao_input.setCompleter(QCompleter(self.db.listar_localizacoes_unicas(), self))
    def calcular_preco_venda(self):
        preco_venda = self.preco_compra_input.value() * (1 + self.margem_lucro_input.value() / 100)
        self.preco_venda_input.blockSignals(True); self.preco_venda_input.setValue(preco_venda); self.preco_venda_input.blockSignals(False)
    def calcular_margem_lucro(self):
        if self.preco_compra_input.value() > 0:
            margem = ((self.preco_venda_input.value() / self.preco_compra_input.value()) - 1) * 100
            self.margem_lucro_input.blockSignals(True); self.margem_lucro_input.setValue(margem); self.margem_lucro_input.blockSignals(False)
    def selecionar_imagem(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar Imagem", os.path.expanduser("~"), "Imagens (*.png *.jpg *.jpeg)")
        if file_path: self.imagem_path = file_path; self.carregar_preview_imagem(file_path)
    def carregar_preview_imagem(self, path):
        if path and os.path.exists(path): self.imagem_preview_label.setPixmap(QPixmap(path).scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else: self.imagem_preview_label.setText("Nenhuma imagem"); self.imagem_preview_label.setPixmap(QPixmap())

# ================================================================= #
#       CLASSE DIALOGQUEBRAREMBALAGEM TOTALMENTE CORRIGIDA          #
# ================================================================= #

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