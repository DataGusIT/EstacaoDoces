from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame, QComboBox, QFileDialog,
                           QTextEdit, QSpinBox, QCheckBox, QGroupBox, QProgressDialog, QSizePolicy, QProgressBar, QApplication) # QProgressDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon,  QColor
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import math # Adicionado para paginação

# Importações necessárias
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager # Importante para a thread

# --- CLASSE 1: DIÁLOGO DE ALERTA (ESTILO PERFIL) ---
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
        container = QFrame(self); container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(container); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)

        self.header = QFrame(); self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header); header_layout.setContentsMargins(20, 15, 10, 15)
        header_title_label = QLabel(title); header_title_label.setObjectName("headerTitleLabel")
        close_button = QPushButton(); close_button.setObjectName("controlButton"); close_button.setFixedSize(28, 28)
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors.get('text_secondary', '#666')))
        close_button.clicked.connect(self.reject)
        header_layout.addWidget(header_title_label); header_layout.addStretch(); header_layout.addWidget(close_button)
        main_layout.addWidget(self.header)

        body = QWidget(); body_layout = QVBoxLayout(body); body_layout.setContentsMargins(25, 20, 25, 25); body_layout.setSpacing(20)
        subtitle_layout = QHBoxLayout()
        icon_label = QLabel(); icon_label.setPixmap(IconManager.get_icon(self.icon_name, color=self.accent_color).pixmap(24, 24))
        subtitle_label = QLabel(title); subtitle_label.setObjectName("subtitleLabel")
        subtitle_layout.addWidget(icon_label); subtitle_layout.addWidget(subtitle_label); subtitle_layout.addStretch()
        
        message_label = QLabel(message); message_label.setWordWrap(True); message_label.setObjectName("messageLabel")
        
        button_layout = QHBoxLayout(); button_layout.addStretch()
        if buttons & QMessageBox.Yes: button_layout.addWidget(self._create_button("Sim", lambda: self.done(QMessageBox.Yes), is_primary=True))
        if buttons & QMessageBox.Ok: button_layout.addWidget(self._create_button("OK", self.accept, is_primary=True))
        if buttons & QMessageBox.No: button_layout.addWidget(self._create_button("Não", self.reject))
        if buttons & QMessageBox.Cancel: button_layout.addWidget(self._create_button("Cancelar", self.reject))
        
        body_layout.addLayout(subtitle_layout); body_layout.addWidget(message_label); body_layout.addLayout(button_layout)
        main_layout.addWidget(body)
        
        base_layout = QVBoxLayout(self); base_layout.addWidget(container)
        self.apply_styles()

    def _create_button(self, text, on_click, is_primary=False):
        btn = QPushButton(text); btn.clicked.connect(on_click); btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("primaryButton" if is_primary else "secondaryButton")
        return btn
        
    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f"""
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
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

# --- CLASSE 2: DIÁLOGO DE PROGRESSO TEMÁTICO ---
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
        container = QFrame(self); container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(container); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)

        self.header = QFrame(); self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header); header_layout.setContentsMargins(20, 15, 10, 15)
        title_label = QLabel(title); title_label.setObjectName("headerTitleLabel")
        header_layout.addWidget(title_label)
        main_layout.addWidget(self.header)

        body = QWidget(); body_layout = QVBoxLayout(body); body_layout.setContentsMargins(25, 20, 25, 25); body_layout.setSpacing(15)
        message_label = QLabel(message); message_label.setWordWrap(True); message_label.setObjectName("messageLabel")
        self.progress_bar = QProgressBar(); self.progress_bar.setTextVisible(True); self.progress_bar.setAlignment(Qt.AlignCenter)
        
        button_layout = QHBoxLayout(); button_layout.addStretch()
        cancel_button = QPushButton("Cancelar"); cancel_button.setObjectName("secondaryButton"); cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        body_layout.addWidget(message_label); body_layout.addWidget(self.progress_bar); body_layout.addLayout(button_layout)
        main_layout.addWidget(body)
        
        base_layout = QVBoxLayout(self); base_layout.addWidget(container)

    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f"""
            #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }}
            #header {{ border-bottom: 1px solid {colors.get('border_color', '#ccc')}; }}
            #headerTitleLabel {{ color: {colors.get('text_color', '#000')}; font-weight: bold; }}
            #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }}
            QPushButton#secondaryButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }}
            QPushButton#secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }}
            QProgressBar {{ border: 1px solid {colors.get('border_color', '#ccc')}; border-radius: 8px; padding: 1px; text-align: center; background-color: {colors.get('bg_color', '#eee')}; color: {colors.get('text_color', '#000')}; }}
            QProgressBar::chunk {{ background-color: {colors.get('accent_color', '#007AFF')}; border-radius: 7px; }}
        """)

    def setValue(self, value): self.progress_bar.setValue(value)
    def reject(self): self.canceled.emit(); super().reject()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)


class FornecedorCsvImportWorker(QThread):
    """Executa a importação de CSV de fornecedores em uma thread, com suporte a atualização."""
    progress = pyqtSignal(int)
    # Adicionamos o contador 'atualizados' ao sinal de conclusão
    finished = pyqtSignal(int, int, int, list)  # importados, atualizados, erros, detalhes

    def __init__(self, db_path, file_path):
        super().__init__()
        self.db_path = db_path
        self.file_path = file_path
        self.local_db = None

    def run(self):
        importados = 0
        atualizados = 0
        erros = 0
        detalhes_erros = []
        try:
            self.local_db = DatabaseManager(self.db_path)
            
            # Otimização: Carrega IDs de fornecedores existentes para busca rápida
            fornecedores_existentes = {f['id'] for f in self.local_db.listar_fornecedores()}

            # Lógica de leitura de arquivo robusta
            with open(self.file_path, mode='r', encoding='utf-8-sig') as csvfile:
                leitor = csv.reader(csvfile)
                try:
                    todas_as_linhas = list(leitor)
                except csv.Error as e:
                    detalhes_erros.append(f"Erro de formatação no CSV: {e}")
                    self.finished.emit(0, 0, 1, detalhes_erros)
                    return

            if len(todas_as_linhas) < 2:
                detalhes_erros.append("Arquivo CSV vazio ou com apenas o cabeçalho.")
                self.finished.emit(0, 0, 0, detalhes_erros)
                return

            cabecalho_raw = todas_as_linhas[0]
            linhas_de_dados = todas_as_linhas[1:]
            cabecalho = [str(h).lower().strip() for h in cabecalho_raw]
            total_linhas = len(linhas_de_dados)

            self.local_db.begin_transaction()
            
            for i, valores_linha in enumerate(linhas_de_dados):
                try:
                    row_dict = dict(zip(cabecalho, valores_linha))
                    
                    empresa_nome = row_dict.get('empresa', '').strip()
                    if not empresa_nome:
                        raise ValueError("A coluna 'empresa' é obrigatória.")
                    
                    dados_fornecedor = {
                        'empresa': empresa_nome,
                        'representante': row_dict.get('representante', '').strip(),
                        'frequencia_compra': row_dict.get('frequencia_compra', '').strip(),
                        'telefone': row_dict.get('telefone', '').strip(),
                        'email': row_dict.get('email', '').strip(),
                        'endereco': row_dict.get('endereco', '').strip(),
                        'contato': row_dict.get('contato', '').strip()
                    }

                    id_para_atualizar = None
                    csv_id_str = row_dict.get('id', '').strip()
                    if csv_id_str.isdigit():
                        csv_id = int(csv_id_str)
                        if csv_id in fornecedores_existentes:
                            id_para_atualizar = csv_id

                    if id_para_atualizar is not None:
                        self.local_db.atualizar_fornecedor(id_para_atualizar, **dados_fornecedor)
                        atualizados += 1
                    else:
                        self.local_db.adicionar_fornecedor(**dados_fornecedor)
                        importados += 1
                except Exception as e:
                    erros += 1
                    detalhes_erros.append(f"Linha {i+2}: {str(e)}")
                
                self.progress.emit(int(((i + 1) / total_linhas) * 100))
            
            self.local_db.commit_transaction()
        except Exception as e:
            if self.local_db: self.local_db.rollback_transaction()
            detalhes_erros.append(f"Erro Crítico na Importação: {str(e)}")
        finally:
            if self.local_db: self.local_db.fechar()
        
        self.finished.emit(importados, atualizados, erros, detalhes_erros)

class FornecedorWindow(QWidget):
    dados_fornecedores_alterados = pyqtSignal()
    
    def __init__(self, db, theme_colors, settings):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.settings = settings
        self.pagina_atual = 1
        self.itens_por_pagina = 100
        self.total_paginas = 1

        self.initUI()
        self.set_theme(self.theme_colors)
        # A chamada carregar_dados() é feita dentro de set_theme, então não é necessária aqui.

    # ================================================================= #
    #       CORREÇÃO PRINCIPAL 1: MÉTODO set_theme REFEITO              #
    # ================================================================= #
    def set_theme(self, theme_colors):
        """
        Atualiza as cores do tema e aplica um stylesheet completo para toda a janela,
        incluindo componentes aninhados como labels e scrollbars.
        """
        self.theme_colors = theme_colors
        self.update_button_icons()

        style = f"""
            /* Estilo geral da janela e dos labels */
            QWidget, QLabel {{
                background-color: transparent;
                color: {self.theme_colors.get('text_color', '#000')};
            }}

            /* --- CORREÇÃO: Estilo específico para o label de paginação --- */
            #paginationLabel {{
                font-size: 10pt;
            }}

            /* Cabeçalho da tabela */
            QHeaderView::section {{
                background-color: {self.theme_colors.get('surface_color', '#e0e0e0')};
                color: {self.theme_colors.get('text_color', '#000')};
                padding: 4px;
                border: 1px solid {self.theme_colors.get('border_color', '#c0c0c0')};
                font-weight: bold;
            }}

            /* --- CORREÇÃO: Estilo para a barra de rolagem da tabela --- */
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
            QTableWidget QScrollBar::add-line, QTableWidget QScrollBar::sub-line {{
                height: 0px;
                width: 0px;
            }}

            /* Botões de ação */
            #primaryActionButton {{
                background-color: {self.theme_colors.get('accent_color', '#007bff')};
                color: white; border: none; padding: 10px 15px;
                border-radius: 6px; font-weight: bold;
            }}
            #primaryActionButton:hover {{ background-color: #0069d9; }}
        """
        self.setStyleSheet(style)
        
        # O estilo dos botões secundários é aplicado diretamente para garantir a atualização
        flat_style = self._get_flat_button_style()
        self.importar_csv_btn.setStyleSheet(flat_style)
        self.exportar_csv_btn.setStyleSheet(flat_style)
        self.verificar_estoque_btn.setStyleSheet(flat_style)

        # Recarrega os dados para que os ícones internos da tabela (editar/excluir) sejam redesenhados com a cor certa
        self.carregar_dados()
        
    def _get_flat_button_style(self):
        """Retorna uma string de estilo CSS para botões secundários."""
        return f"""
            QPushButton {{
                background-color: {self.theme_colors.get('surface_color', '#fff')};
                color: {self.theme_colors.get('text_color', '#000')};
                border: 1px solid {self.theme_colors.get('border_color', '#ccc')};
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {self.theme_colors.get('button_hover', '#eee')};
                border-color: {self.theme_colors.get('accent_color', '#007aff')};
            }}
        """

    def update_button_icons(self):
        """Atualiza apenas os ícones dos botões."""
        icon_color = self.theme_colors.get('text_color', '#000')
        self.search_button.setIcon(IconManager.get_icon('search', icon_color))
        self.add_button.setIcon(IconManager.get_icon('add', 'white'))
        self.importar_csv_btn.setIcon(IconManager.get_icon('import', icon_color))
        self.exportar_csv_btn.setIcon(IconManager.get_icon('export', icon_color))
        self.verificar_estoque_btn.setIcon(IconManager.get_icon('check_stock', icon_color))
        self.prev_page_btn.setIcon(IconManager.get_icon('angle-left', icon_color))
        self.next_page_btn.setIcon(IconManager.get_icon('angle-right', icon_color))
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        search_group = QGroupBox("Pesquisa e Filtros")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por empresa, representante ou email...")
        self.search_input.returnPressed.connect(self.pesquisar_fornecedores)
        
        self.frequencia_filter_combo = QComboBox()
        self.frequencia_filter_combo.addItems(["Todas as Frequências", "Alta", "Média", "Baixa"])
        self.frequencia_filter_combo.currentIndexChanged.connect(self.pesquisar_fornecedores)

        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar Fornecedor")
        self.search_button.clicked.connect(self.pesquisar_fornecedores)
        search_layout.addWidget(self.search_input, 2)
        search_layout.addWidget(self.frequencia_filter_combo, 1)
        search_layout.addWidget(self.search_button)
        layout.addWidget(search_group)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["ID", "Empresa", "Representante", "Frequência", "Telefone", "Email", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        paginacao_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton(" Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
        
        # --- CORREÇÃO: Adicionando objectName para estilização ---
        self.page_label = QLabel(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.page_label.setObjectName("paginationLabel")

        self.next_page_btn = QPushButton("Próxima ")
        self.next_page_btn.setLayoutDirection(Qt.RightToLeft)
        self.next_page_btn.clicked.connect(self.ir_proxima_pagina)
        
        paginacao_layout.addWidget(self.prev_page_btn)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.page_label)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.next_page_btn)
        layout.addLayout(paginacao_layout)

        action_layout = QHBoxLayout()
        self.add_button = QPushButton(" Adicionar Fornecedor")
        self.add_button.setObjectName("primaryActionButton")
        self.add_button.clicked.connect(self.abrir_formulario_fornecedor)

        self.importar_csv_btn = QPushButton(" Importar CSV")
        self.importar_csv_btn.clicked.connect(self.importar_csv)

        self.exportar_csv_btn = QPushButton(" Exportar CSV")
        self.exportar_csv_btn.clicked.connect(self.exportar_csv)

        self.verificar_estoque_btn = QPushButton(" Verificar Estoque Baixo")
        self.verificar_estoque_btn.clicked.connect(self.verificar_estoque_baixo)
        
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.importar_csv_btn)
        action_layout.addWidget(self.exportar_csv_btn)
        action_layout.addWidget(self.verificar_estoque_btn)
        layout.addLayout(action_layout)
    
    def ir_pagina_anterior(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_visualizacao_dados()

    def ir_proxima_pagina(self):
        if self.pagina_atual < self.total_paginas:
            self.pagina_atual += 1
            self.atualizar_visualizacao_dados()
            
    def carregar_dados(self):
        self.pagina_atual = 1
        self.search_input.clear()
        self.frequencia_filter_combo.setCurrentIndex(0) # Reseta o filtro
        self.atualizar_visualizacao_dados()

    def pesquisar_fornecedores(self):
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
        
    def atualizar_visualizacao_dados(self):
        """Função central que busca, filtra e pagina os dados."""
        
        # --- INÍCIO DA MODIFICAÇÃO: Adicionar filtro de frequência aos parâmetros ---
        frequencia_selecionada = self.frequencia_filter_combo.currentText()
        if frequencia_selecionada == "Todas as Frequências":
            frequencia_selecionada = None # Envia None para o DB se "Todas" for selecionado

        filtros = {
            'termo_pesquisa': self.search_input.text(),
            'frequencia': frequencia_selecionada 
        }
        # --- FIM DA MODIFICAÇÃO ---
        
        total_itens = self.db.contar_fornecedores_filtrados(filtros)
        fornecedores = self.db.listar_fornecedores_paginado_e_filtrado(
            filtros, self.pagina_atual, self.itens_por_pagina
        )
        
        self.atualizar_tabela(fornecedores)
        
        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina) or 1
        self.page_label.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.prev_page_btn.setEnabled(self.pagina_atual > 1)
        self.next_page_btn.setEnabled(self.pagina_atual < self.total_paginas)
    
    def atualizar_tabela(self, fornecedores):
        self.tabela.setRowCount(0)
        icon_color = self.theme_colors.get('text_color', '#000')

        # Dicionário de cores para a frequência
        cores_frequencia = {
            "Alta": QColor("#28a745"),  # Verde
            "Média": QColor("#ffc107"), # Amarelo
            "Baixa": QColor("#dc3545")  # Vermelho
        }

        for row, fornecedor in enumerate(fornecedores):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(fornecedor['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(fornecedor['empresa']))
            self.tabela.setItem(row, 2, QTableWidgetItem(fornecedor['representante'] or ""))
            
            # --- INÍCIO DA MODIFICAÇÃO: Aplicar Cor na Frequência ---
            frequencia_texto = fornecedor['frequencia_compra'] or ""
            item_frequencia = QTableWidgetItem(frequencia_texto)
            
            # Aplica a cor se a frequência estiver no dicionário
            if frequencia_texto in cores_frequencia:
                item_frequencia.setForeground(cores_frequencia[frequencia_texto])
                # Opcional: Deixar a fonte em negrito para destacar
                font = QFont()
                font.setBold(True)
                item_frequencia.setFont(font)
            
            self.tabela.setItem(row, 3, item_frequencia)
            # --- FIM DA MODIFICAÇÃO ---

            self.tabela.setItem(row, 4, QTableWidgetItem(fornecedor['telefone'] or ""))
            self.tabela.setItem(row, 5, QTableWidgetItem(fornecedor['email'] or ""))

            # ... (código das ações continua igual) ...
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(5, 2, 5, 2)
            acoes_layout.setSpacing(5)

            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), " ")
            editar_btn.setToolTip("Editar Fornecedor")
            editar_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            editar_btn.clicked.connect(lambda _, f_id=fornecedor['id']: self.abrir_formulario_fornecedor(f_id))

            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), "")
            excluir_btn.setToolTip("Excluir Fornecedor")
            excluir_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            excluir_btn.clicked.connect(lambda _, f_id=fornecedor['id']: self.excluir_fornecedor(f_id))

            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)

            self.tabela.setCellWidget(row, 6, acoes_widget)
    
    def abrir_formulario_fornecedor(self, fornecedor_id=None):
        # Passe self.theme_colors e self (parent) para o diálogo
        dialog = FormularioFornecedor(self.db, self.theme_colors, fornecedor_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_visualizacao_dados()

    def excluir_fornecedor(self, fornecedor_id):
        dialog = AlertDialog(self, "Confirmar Exclusão",
                             "Tem certeza que deseja excluir este fornecedor e todos os produtos associados a ele?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            if self.db.excluir_fornecedor(fornecedor_id):
                AlertDialog(self, "Sucesso", "Fornecedor excluído com sucesso.", alert_type='success', theme_colors=self.theme_colors).exec_()
                self.atualizar_visualizacao_dados()
            else:
                AlertDialog(self, "Erro", "Não foi possível excluir o fornecedor.", alert_type='error', theme_colors=self.theme_colors).exec_()

    # ... O restante do código de FornecedorWindow permanece o mesmo (importar, exportar, etc.) ...
    def importar_csv(self):
        arquivo, _ = QFileDialog.getOpenFileName(self, "Importar Fornecedores CSV", "", "CSV Files (*.csv)")
        if not arquivo:
            return

        dialog = AlertDialog(self, "Confirmar Importação",
                             "A importação será executada em segundo plano.\nDeseja continuar?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        if dialog.exec_() != QMessageBox.Yes:
            return

        self.progress_dialog = ThemedProgressDialog(self, "Importando Fornecedores", "Aguarde enquanto os dados são processados...", self.theme_colors)
        self.progress_dialog.canceled.connect(self.cancelar_importacao)

        self.import_thread = FornecedorCsvImportWorker(self.db.db_path, arquivo)
        self.import_thread.progress.connect(self.progress_dialog.setValue)
        self.import_thread.finished.connect(self.importacao_concluida)
        
        self.import_thread.start()
        self.progress_dialog.exec_()
    
     # NOVO MÉTODO (adicionar abaixo de importar_csv)
    def importacao_concluida(self, importados, atualizados, erros, detalhes_erros):
        self.progress_dialog.close()
        self.carregar_dados() # Recarrega tudo para mostrar as atualizações
        
        mensagem = (f"Importação concluída!\n\n"
                    f"✔ Fornecedores novos criados: {importados}\n"
                    f"✔ Fornecedores existentes atualizados: {atualizados}\n"
                    f"❌ Linhas com erro: {erros}")
        
        if detalhes_erros:
            mensagem += "\n\nDetalhes dos problemas:\n" + "\n".join(detalhes_erros[:5])
            alert_type = 'warning' if (importados > 0 or atualizados > 0) else 'error'
            titulo = "Importação Finalizada com Avisos"
            AlertDialog(self, titulo, mensagem, alert_type=alert_type, theme_colors=self.theme_colors).exec_()
        else:
            AlertDialog(self, "Importação Concluída com Sucesso", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()

    # NOVO MÉTODO (adicionar abaixo de importacao_concluida)
    def cancelar_importacao(self):
        if hasattr(self, 'import_thread') and self.import_thread.isRunning():
            self.import_thread.terminate()
            AlertDialog(self, "Cancelado", "A importação foi cancelada pelo usuário.", alert_type='info', theme_colors=self.theme_colors).exec_()

    
    def exportar_csv(self):
        arquivo, _ = QFileDialog.getSaveFileName(self, "Exportar Fornecedores CSV", f"fornecedores_{datetime.now().strftime('%Y%m%d')}.csv", "CSV Files (*.csv)")
        if not arquivo:
            return
            
        try:
            fornecedores = self.db.listar_fornecedores()
            if not fornecedores:
                AlertDialog(self, "Exportar", "Não há fornecedores para exportar.", alert_type='info', theme_colors=self.theme_colors).exec_()
                return

            with open(arquivo, 'w', newline='', encoding='utf-8') as file:
                # Adicionamos 'id' como o primeiro campo do cabeçalho
                fieldnames = ['id', 'empresa', 'representante', 'frequencia_compra', 'telefone', 'email', 'endereco', 'contato']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for f_row in fornecedores:
                    f_dict = dict(f_row)
                    writer.writerow({k: f_dict.get(k, '') for k in fieldnames})
            
            AlertDialog(self, "Exportação Concluída", f"Fornecedores exportados com sucesso para:\n{arquivo}", alert_type='success', theme_colors=self.theme_colors).exec_()
                
        except Exception as e:
            AlertDialog(self, "Erro na Exportação", f"Ocorreu um erro ao exportar o arquivo:\n{e}", alert_type='error', theme_colors=self.theme_colors).exec_()
                
        except Exception as e:
            # O erro que você viu será capturado aqui.
            AlertDialog(self, "Erro na Exportação", f"Ocorreu um erro ao exportar o arquivo:\n{e}", alert_type='error', theme_colors=self.theme_colors).exec_()

    
    def verificar_estoque_baixo(self):
        produtos_baixo = self.db.verificar_produtos_estoque_baixo()
        
        if not produtos_baixo:
            QMessageBox.information(self, "Estoque OK", "Não há produtos com estoque baixo no momento.")
            return
        
        produtos_por_fornecedor = {}
        for produto in produtos_baixo:
            fornecedor_nome = produto['fornecedor_nome'] or 'Sem fornecedor'
            if fornecedor_nome not in produtos_por_fornecedor:
                produtos_por_fornecedor[fornecedor_nome] = []
            produtos_por_fornecedor[fornecedor_nome].append(produto)
        
        # CORREÇÃO: Passe o self.settings para o diálogo
        dialog = DialogEstoqueBaixo(self.db, produtos_por_fornecedor, self.theme_colors, self.settings, self)
        dialog.exec_()

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

class DialogEstoqueBaixo(QDialog):
    def __init__(self, db, produtos_por_fornecedor, theme_colors, settings, parent=None):
        super().__init__(parent)
        self.db = db
        self.produtos_por_fornecedor = produtos_por_fornecedor
        self.theme_colors = theme_colors
        self.settings = settings

        self.initUI()
        self.apply_styles() # Aplica os estilos na inicialização
        self.popular_tabela_fornecedores()

    def initUI(self):
        self.setWindowTitle("Notificar Fornecedores sobre Estoque Baixo")
        self.setMinimumSize(900, 750)
        
        layout = QVBoxLayout(self)
        
        fornecedores_group = QGroupBox("1. Selecione os Fornecedores para Notificar")
        fornecedores_layout = QVBoxLayout(fornecedores_group)
        
        self.tabela_fornecedores = QTableWidget()
        self.tabela_fornecedores.setColumnCount(3)
        self.tabela_fornecedores.setHorizontalHeaderLabels(["Enviar?", "Fornecedor", "Produtos com Estoque Baixo"])
        self.tabela_fornecedores.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tabela_fornecedores.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.tabela_fornecedores.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.tabela_fornecedores.setSelectionMode(QHeaderView.NoSelection)
        self.tabela_fornecedores.setEditTriggers(QTableWidget.NoEditTriggers)
        
        fornecedores_layout.addWidget(self.tabela_fornecedores)
        layout.addWidget(fornecedores_group)

        template_group = QGroupBox("2. Escreva a Mensagem")
        template_layout = QVBoxLayout(template_group)
        
        info_label = QLabel("Use as variáveis <b>{fornecedor_nome}</b> e <b>{lista_produtos}</b>. Elas serão substituídas automaticamente para cada e-mail.")
        info_label.setWordWrap(True)
        
        self.assunto_email = QLineEdit("Solicitação de Reposição de Estoque")

        self.corpo_email = QTextEdit()
        template_padrao = """Prezado(a) {fornecedor_nome},

Espero que esta mensagem o(a) encontre bem.

Gostaríamos de solicitar a cotação e o prazo de entrega para os seguintes produtos que estão com estoque baixo em nosso sistema:

{lista_produtos}

Agradecemos a sua atenção e aguardamos o seu breve retorno.

Atenciosamente,
[Nome da Sua Empresa]
"""
        self.corpo_email.setPlainText(template_padrao)
        
        form_template_layout = QFormLayout()
        form_template_layout.addRow("Assunto:", self.assunto_email)
        
        template_layout.addWidget(info_label)
        template_layout.addLayout(form_template_layout)
        template_layout.addWidget(self.corpo_email)
        layout.addWidget(template_group)

        email_group = QGroupBox("3. Suas Credenciais de Envio")
        email_layout = QFormLayout(email_group)
        
        self.email_usuario = QLineEdit()
        self.email_usuario.setPlaceholderText("seu.email@exemplo.com")
        self.email_senha = QLineEdit()
        self.email_senha.setEchoMode(QLineEdit.Password)
        self.email_senha.setPlaceholderText("Sua senha de e-mail ou 'senha de app'")
        
        smtp_config = self.settings.get_smtp_config()
        if smtp_config and smtp_config.get('user'):
            self.email_usuario.setText(smtp_config['user'])

        email_layout.addRow("Seu Email:", self.email_usuario)
        email_layout.addRow("Sua Senha:", self.email_senha)
        
        layout.addWidget(email_group)

        button_layout = QHBoxLayout()
        self.enviar_emails_btn = QPushButton(" Enviar Emails Selecionados")
        self.enviar_emails_btn.setObjectName("primaryButton")
        self.enviar_emails_btn.clicked.connect(self.enviar_emails)

        self.fechar_btn = QPushButton(" Fechar")
        self.fechar_btn.setObjectName("secondaryButton")
        self.fechar_btn.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(self.fechar_btn)
        button_layout.addWidget(self.enviar_emails_btn)
        layout.addLayout(button_layout)

    # ================================================================= #
    #       CORREÇÃO PRINCIPAL 2: MÉTODO apply_styles REFEITO           #
    # ================================================================= #
    def apply_styles(self):
        """Aplica uma folha de estilos completa para o diálogo, incluindo scrollbars."""
        colors = self.theme_colors
        self.setStyleSheet(f"""
            QDialog {{ background-color: {colors['bg_color']}; }}
            QGroupBox, QLabel, QCheckBox {{ color: {colors['text_color']}; }}
            QGroupBox {{ font-weight: bold; border: 1px solid {colors['border_color']}; border-radius: 6px; margin-top: 10px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; }}
            QLineEdit, QTextEdit, QTableWidget {{ 
                background-color: {colors['surface_color']}; 
                color: {colors['text_color']}; 
                border: 1px solid {colors['border_color']}; 
                padding: 6px; 
                border-radius: 4px; 
            }}
            QHeaderView::section {{ 
                background-color: {colors.get('menu_color', colors['surface_color'])}; 
                padding: 5px; border: 1px solid {colors['border_color']}; 
                font-weight: bold; 
            }}
            QLineEdit:focus, QTextEdit:focus {{ border: 1px solid {colors['accent_color']}; }}
            
            /* --- CORREÇÃO: Estilo para as scrollbars da tabela e da caixa de texto --- */
            QTableWidget QScrollBar:vertical, QTextEdit QScrollBar:vertical {{
                border: none;
                background: {colors.get('surface_color', '#f0f0f0')};
                width: 12px;
            }}
            QTableWidget QScrollBar::handle:vertical, QTextEdit QScrollBar::handle:vertical {{
                background: {colors.get('border_color', '#cccccc')};
                min-height: 20px;
                border-radius: 6px;
            }}
            QTableWidget QScrollBar::handle:vertical:hover, QTextEdit QScrollBar::handle:vertical:hover {{
                background: {colors.get('accent_color', '#007bff')};
            }}
            QTableWidget QScrollBar::add-line, QTableWidget QScrollBar::sub-line,
            QTextEdit QScrollBar::add-line, QTextEdit QScrollBar::sub-line {{
                height: 0px; width: 0px;
            }}
            /* --- FIM DA CORREÇÃO --- */

            #primaryButton {{ background-color: {colors['accent_color']}; color: white; border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold; }}
            #primaryButton:hover {{ background-color: #005bb5; }}
            #secondaryButton {{ background-color: {colors['surface_color']}; color: {colors['text_color']}; border: 1px solid {colors['border_color']}; padding: 8px 16px; border-radius: 4px; font-weight: bold; }}
            #secondaryButton:hover {{ border-color: {colors['accent_color']}; }}
        """)
        # Atualiza os ícones dos botões
        self.enviar_emails_btn.setIcon(IconManager.get_icon('send', 'white'))
        self.fechar_btn.setIcon(IconManager.get_icon('cancel', self.theme_colors['text_color']))

    def popular_tabela_fornecedores(self):
        self.tabela_fornecedores.setRowCount(0)
        for i, (fornecedor, produtos) in enumerate(self.produtos_por_fornecedor.items()):
            if fornecedor == 'Sem fornecedor': continue # Pula produtos sem fornecedor
            
            self.tabela_fornecedores.insertRow(i)
            
            # Checkbox
            checkbox_widget = QWidget()
            checkbox_layout = QHBoxLayout(checkbox_widget)
            checkbox = QCheckBox()
            checkbox.setChecked(True) # Inicia marcado por padrão
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            self.tabela_fornecedores.setCellWidget(i, 0, checkbox_widget)
            
            # Nome do Fornecedor
            self.tabela_fornecedores.setItem(i, 1, QTableWidgetItem(fornecedor))
            
            # Lista de produtos
            nomes_produtos = [p['nome'] for p in produtos]
            self.tabela_fornecedores.setItem(i, 2, QTableWidgetItem(", ".join(nomes_produtos)))
        
        self.tabela_fornecedores.resizeRowsToContents()

    def enviar_emails(self):
        usuario = self.email_usuario.text().strip()
        senha = self.email_senha.text().strip()
        
        if not usuario or not senha:
            AlertDialog(self, "Credenciais Faltando", "Por favor, preencha seu e-mail e senha para enviar.", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        smtp_config = self.settings.get_smtp_config()
        if not smtp_config or not smtp_config.get('host') or not smtp_config.get('port'):
            AlertDialog(self, "Erro de Configuração", "As configurações de servidor SMTP não foram encontradas.", alert_type='error', theme_colors=self.theme_colors).exec_()
            return

        fornecedores_selecionados = [self.tabela_fornecedores.item(i, 1).text() for i in range(self.tabela_fornecedores.rowCount()) if self.tabela_fornecedores.cellWidget(i, 0).layout().itemAt(0).widget().isChecked()]
        
        if not fornecedores_selecionados:
            AlertDialog(self, "Nenhuma Seleção", "Por favor, selecione pelo menos um fornecedor para notificar.", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        progress = ThemedProgressDialog(self, "Enviando E-mails", "Conectando ao servidor...", self.theme_colors)
        progress.show()
        QApplication.processEvents() # Garante que o diálogo apareça

        try:
            server = smtplib.SMTP(smtp_config['host'], smtp_config['port'])
            server.starttls()
            server.login(usuario, senha)
            
            enviados, falhas = 0, 0
            for i, nome_fornecedor in enumerate(fornecedores_selecionados):
                progress.setValue(int((i / len(fornecedores_selecionados)) * 100))
                email_fornecedor = self.obter_email_fornecedor(nome_fornecedor)
                if not email_fornecedor:
                    falhas += 1; continue
                
                produtos = self.produtos_por_fornecedor[nome_fornecedor]
                lista_produtos_str = "".join([f"  • {p['nome']} (Estoque: {p['quantidade']})\n" for p in produtos])
                corpo_final = self.corpo_email.toPlainText().format(fornecedor_nome=nome_fornecedor, lista_produtos=lista_produtos_str)
                
                msg = MIMEMultipart(); msg['From'] = usuario; msg['To'] = email_fornecedor; msg['Subject'] = self.assunto_email.text()
                msg.attach(MIMEText(corpo_final, 'plain'))
                
                try:
                    server.sendmail(usuario, email_fornecedor, msg.as_string()); enviados += 1
                except Exception: falhas += 1
            
            server.quit()
            progress.close()
            AlertDialog(self, "Envio Concluído", f"E-mails enviados com sucesso: {enviados}\nFalhas: {falhas}", alert_type='success', theme_colors=self.theme_colors).exec_()

        except Exception as e:
            progress.close()
            AlertDialog(self, "Erro de Conexão", f"Não foi possível conectar ou enviar e-mails:\n{e}", alert_type='error', theme_colors=self.theme_colors).exec_()
    
    def obter_email_fornecedor(self, fornecedor_nome):
        # Este método permanece o mesmo
        try:
            fornecedores = self.db.listar_fornecedores()
            for fornecedor in fornecedores:
                if fornecedor['empresa'] == fornecedor_nome:
                    return fornecedor['email']
            return None
        except:
            return None

class FormularioFornecedor(QDialog):
    # 1. Construtor modificado para aceitar theme_colors
    def __init__(self, db, theme_colors, fornecedor_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.theme_colors = theme_colors
        self.fornecedor_id = fornecedor_id
        self.fornecedor = None
        
        if fornecedor_id:
            self.fornecedor = self.db.obter_fornecedor(fornecedor_id)
            if not self.fornecedor:
                QMessageBox.warning(self, "Erro", "Fornecedor não encontrado!")
                self.reject()
        
        self.initUI()
        self.apply_styles() # 2. Aplica os estilos do tema

        if self.fornecedor:
            self.carregar_dados_fornecedor()
    
    def initUI(self):
        self.setWindowTitle("Cadastro de Fornecedor")
        self.setFixedWidth(500)

        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Dados do Fornecedor")
        form_layout = QFormLayout(form_group)

        self.empresa_input = QLineEdit()
        self.representante_input = QLineEdit()
        self.frequencia_input = QComboBox()
        self.frequencia_input.addItems(["", "Alta", "Média", "Baixa"])
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        self.contato_input = QLineEdit()

        form_layout.addRow("Empresa (*):", self.empresa_input)
        form_layout.addRow("Representante:", self.representante_input)
        form_layout.addRow("Frequência de Compra:", self.frequencia_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Endereço:", self.endereco_input)
        form_layout.addRow("Contato:", self.contato_input)
        layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        # 3. Ícones agora usam as cores do tema
        self.salvar_btn = QPushButton(IconManager.get_icon('save', 'white'), " Salvar")
        self.salvar_btn.setObjectName("primaryButton") # Estilo primário
        self.salvar_btn.clicked.connect(self.salvar_fornecedor)

        self.cancelar_btn = QPushButton(IconManager.get_icon('cancel', self.theme_colors['text_color']), " Cancelar")
        self.cancelar_btn.setObjectName("secondaryButton") # Estilo secundário
        self.cancelar_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        layout.addLayout(button_layout)

    # 4. NOVO MÉTODO para aplicar o estilo do tema
    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg_color']};
            }}
            QGroupBox {{
                font-weight: bold;
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 6px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }}
            QLabel, QComboBox {{
                color: {colors['text_color']};
            }}
            QLineEdit, QComboBox {{
                background-color: {colors['surface_color']};
                border: 1px solid {colors['border_color']};
                padding: 6px;
                border-radius: 4px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {colors['accent_color']};
            }}
            /* Botão Primário (Salvar) */
            #primaryButton {{
                background-color: {colors['accent_color']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            #primaryButton:hover {{
                background-color: #005bb5; /* Um tom mais escuro */
            }}
            /* Botão Secundário (Cancelar) */
            #secondaryButton {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            #secondaryButton:hover {{
                border-color: {colors['accent_color']};
            }}
        """)

    def carregar_dados_fornecedor(self):
        """Carrega os dados do fornecedor nos campos do formulário."""
        self.empresa_input.setText(self.fornecedor['empresa'])
        self.representante_input.setText(self.fornecedor['representante'] or "")
        
        frequencia = self.fornecedor['frequencia_compra']
        if frequencia:
            index = self.frequencia_input.findText(frequencia, Qt.MatchFixedString)
            if index >= 0:
                self.frequencia_input.setCurrentIndex(index)
        
        self.telefone_input.setText(self.fornecedor['telefone'] or "")
        self.email_input.setText(self.fornecedor['email'] or "")
        self.endereco_input.setText(self.fornecedor['endereco'] or "")
        self.contato_input.setText(self.fornecedor['contato'] or "")
    
    def salvar_fornecedor(self):
        if not self.empresa_input.text().strip():
            AlertDialog(self, "Campo Obrigatório", "O nome da empresa é obrigatório!", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return
        
        dados = {
            'empresa': self.empresa_input.text().strip(),
            'representante': self.representante_input.text().strip(),
            'frequencia_compra': self.frequencia_input.currentText(),
            'telefone': self.telefone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'endereco': self.endereco_input.text().strip(),
            'contato': self.contato_input.text().strip()
        }
        
        try:
            if self.fornecedor_id:
                sucesso = self.db.atualizar_fornecedor(self.fornecedor_id, **dados)
                mensagem = "Fornecedor atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_fornecedor(**dados)
                mensagem = "Fornecedor cadastrado com sucesso!"
            
            if sucesso:
                AlertDialog(self, "Sucesso", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()
                self.accept()
            else:
                AlertDialog(self, "Erro", "Não foi possível salvar o fornecedor.", alert_type='error', theme_colors=self.theme_colors).exec_()
        
        except Exception as e:
            AlertDialog(self, "Erro Crítico", f"Ocorreu um erro inesperado ao salvar:\n{e}", alert_type='error', theme_colors=self.theme_colors).exec_()