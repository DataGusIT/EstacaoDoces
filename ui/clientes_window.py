from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame, QDateEdit, QFileDialog, 
                           QGroupBox, QSizePolicy, QProgressDialog)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
import csv
import os
import math

# Importações necessárias
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager

from PyQt5.QtWidgets import QProgressBar, QFrame
from PyQt5.QtCore import Qt

from PyQt5.QtMultimedia import QSoundEffect
from PyQt5.QtCore import QUrl

# --- CLASSE 1: DIÁLOGO DE ALERTA (ESTILO PERFIL) ---
class AlertDialog(QDialog):
    """Caixa de diálogo com o estilo sutil da tela de perfil."""
    
    # Atributo de classe para garantir que o som seja carregado apenas uma vez
    success_sound_player = None

    def __init__(self, parent, title, message, alert_type='info', buttons=QMessageBox.Ok, theme_colors=None):
        super().__init__(parent)
        
        if alert_type == 'success':
            # Inicializa o player de som na primeira vez que for necessário
            if AlertDialog.success_sound_player is None:
                sound_file_path = "assets/sounds/success.wav"
                
                if os.path.exists(sound_file_path):
                    AlertDialog.success_sound_player = QSoundEffect()
                    AlertDialog.success_sound_player.setSource(QUrl.fromLocalFile(sound_file_path))
                    AlertDialog.success_sound_player.setVolume(0.4) # Volume de 0.0 a 1.0
                else:
                    # Imprime um aviso no console se o arquivo não for encontrado
                    print(f"Aviso: Arquivo de som de sucesso não encontrado em '{sound_file_path}'")
                    # Marca como False para não tentar carregar de novo
                    AlertDialog.success_sound_player = False

            # Toca o som se o player foi carregado com sucesso
            if AlertDialog.success_sound_player:
                AlertDialog.success_sound_player.play()
        
        self.theme_colors = theme_colors if theme_colors is not None else {}
        self.drag_position = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        type_info = { 'success':  {'icon': 'check', 'color': '#28a745'}, 'warning':  {'icon': 'estoque_baixo', 'color': '#ffc107'}, 'error':    {'icon': 'delete', 'color': '#dc3545'}, 'question': {'icon': 'question', 'color': '#17a2b8'}, 'info':     {'icon': 'sobre', 'color': self.theme_colors.get('accent_color', '#007AFF')}, }.get(alert_type, {'icon': 'sobre', 'color': '#007AFF'})
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
        self.setStyleSheet(f""" #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }} #header {{ border-bottom: 1px solid {colors.get('border_color', '#ccc')}; }} #headerTitleLabel {{ color: {colors.get('text_color', '#000')}; font-weight: bold; }} #subtitleLabel {{ color: {colors.get('text_color', '#000')}; font-size: 14pt; font-weight: bold; }} #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }} #controlButton {{ background: transparent; border: none; border-radius: 14px; }} #controlButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }} QPushButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; min-width: 90px;}} #primaryButton {{ background-color: {self.accent_color}; color: white; border: none; }} #secondaryButton {{ background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }} #secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }} """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
        
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

# --- CLASSE 2: DIÁLOGO DE PROGRESSO TEMÁTICO ---
class ThemedProgressDialog(QDialog):
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
        self.setStyleSheet(f""" #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }} #header {{ border-bottom: 1px solid {colors.get('border_color', '#ccc')}; }} #headerTitleLabel {{ color: {colors.get('text_color', '#000')}; font-weight: bold; }} #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }} QPushButton#secondaryButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }} QPushButton#secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }} QProgressBar {{ border: 1px solid {colors.get('border_color', '#ccc')}; border-radius: 8px; padding: 1px; text-align: center; background-color: {colors.get('bg_color', '#eee')}; color: {colors.get('text_color', '#000')}; }} QProgressBar::chunk {{ background-color: {colors.get('accent_color', '#007AFF')}; border-radius: 7px; }} """)
    def setValue(self, value): self.progress_bar.setValue(value)
    def reject(self): self.canceled.emit(); super().reject()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

class ClienteCsvImportWorker(QThread):
    progress = pyqtSignal(int)
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
            
            # Otimização: Carrega clientes existentes usando o método correto do db_manager
            todos_clientes = self.local_db.listar_clientes() 
            clientes_por_id = {cliente['id']: cliente for cliente in todos_clientes}
            clientes_por_email = {str(cliente.get('email', '')).lower(): cliente['id'] for cliente in todos_clientes if cliente and cliente.get('email')}

            # Lógica de leitura do arquivo (já estava correta na sua versão final)
            with open(self.file_path, mode='r', encoding='utf-8-sig') as csvfile:
                leitor = csv.reader(csvfile)
                try:
                    todas_as_linhas = list(leitor)
                except csv.Error as e:
                    detalhes_erros.append(f"Erro de formatação no CSV: {e}")
                    self.finished.emit(0, 0, 1, detalhes_erros)
                    return

            if not todas_as_linhas or len(todas_as_linhas) < 2:
                detalhes_erros.append("O arquivo CSV está vazio ou contém apenas o cabeçalho.")
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
                    
                    nome = row_dict.get('nome', '').strip()
                    if not nome:
                        raise ValueError("A coluna 'nome' está vazia.")
                    
                    email = row_dict.get('email', '').strip()
                    email_lower = email.lower()
                    csv_id_str = row_dict.get('id', '').strip()

                    data_nascimento_str = row_dict.get('data_nascimento', '')
                    data_nascimento_db = None
                    if data_nascimento_str:
                        try: data_nascimento_db = datetime.strptime(data_nascimento_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                        except ValueError: data_nascimento_db = datetime.strptime(data_nascimento_str, '%Y-%m-%d').strftime('%Y-%m-%d')
                    
                    dados_cliente = {
                        'nome': nome, 'data_nascimento': data_nascimento_db,
                        'telefone': row_dict.get('telefone', '').strip(), 'email': email,
                        'endereco': row_dict.get('endereco', '').strip()
                    }

                    id_para_atualizar = None
                    if csv_id_str.isdigit():
                        csv_id = int(csv_id_str)
                        if csv_id in clientes_por_id: id_para_atualizar = csv_id

                    if id_para_atualizar is None and email and email_lower in clientes_por_email:
                        id_para_atualizar = clientes_por_email[email_lower]

                    if id_para_atualizar is not None:
                        self.local_db.atualizar_cliente(id_para_atualizar, **dados_cliente)
                        atualizados += 1
                    else:
                        self.local_db.adicionar_cliente(**dados_cliente)
                        importados += 1
                except Exception as e:
                    erros += 1
                    detalhes_erros.append(f"Linha {i+2}: {str(e)}")
                
                self.progress.emit(int(((i + 1) / total_linhas) * 100))
            
            self.local_db.commit_transaction()
        except Exception as e:
            if self.local_db: self.local_db.rollback_transaction()
            # Este erro crítico agora será exibido corretamente na interface
            detalhes_erros.append(f"Erro Crítico na Importação: {str(e)}")
        finally:
            if self.local_db: self.local_db.fechar()
        
        self.finished.emit(importados, atualizados, erros, detalhes_erros)

class ClientesWindow(QWidget):
    dados_clientes_alterados = pyqtSignal()

    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.pagina_atual = 1
        self.itens_por_pagina = 50
        self.total_paginas = 1
        
        self.initUI()
        self.set_theme(self.theme_colors)

    def set_theme(self, theme_colors):
        self.theme_colors = theme_colors
        self.update_button_icons()

        style = f"""
            QWidget, QLabel {{
                background-color: {self.theme_colors.get('bg_color', '#fff')};
                color: {self.theme_colors.get('text_color', '#000')};
            }}
            #paginationLabel {{ font-size: 10pt; }}
            QHeaderView::section {{
                background-color: {self.theme_colors.get('surface_color', '#e0e0e0')};
                color: {self.theme_colors.get('text_color', '#000')};
                padding: 4px;
                border: 1px solid {self.theme_colors.get('border_color', '#c0c0c0')};
                font-weight: bold;
            }}
            QTableWidget QScrollBar:vertical {{
                border: none; background: {self.theme_colors.get('surface_color', '#f0f0f0')};
                width: 12px; margin: 0px;
            }}
            QTableWidget QScrollBar::handle:vertical {{
                background: {self.theme_colors.get('border_color', '#cccccc')};
                min-height: 20px; border-radius: 6px;
            }}
            QTableWidget QScrollBar::handle:vertical:hover {{
                background: {self.theme_colors.get('accent_color', '#007bff')};
            }}
            QTableWidget QScrollBar::add-line, QTableWidget QScrollBar::sub-line {{ height: 0px; width: 0px; }}
            #primaryActionButton {{
                background-color: {self.theme_colors.get('accent_color', '#007bff')};
                color: white; border: none; padding: 10px 15px;
                border-radius: 6px; font-weight: bold;
            }}
            #primaryActionButton:hover {{ background-color: #0069d9; }}
            #secondaryActionButton {{
                background-color: {self.theme_colors.get('surface_color', '#fff')};
                color: {self.theme_colors.get('text_color', '#000')};
                border: 1px solid {self.theme_colors.get('border_color', '#ccc')};
                padding: 10px 15px; border-radius: 6px; font-weight: bold;
            }}
             #secondaryActionButton:hover {{
                background-color: {self.theme_colors.get('button_hover', '#eee')};
                border-color: {self.theme_colors.get('accent_color', '#007aff')};
            }}
        """
        self.setStyleSheet(style)
        self.atualizar_visualizacao_dados()

    def update_button_icons(self):
        icon_color = self.theme_colors.get('text_color', '#000') 
        self.search_button.setIcon(IconManager.get_icon('search', icon_color))
        self.add_button.setIcon(IconManager.get_icon('add', 'white'))
        self.importar_csv_button.setIcon(IconManager.get_icon('import', icon_color))
        self.exportar_csv_button.setIcon(IconManager.get_icon('export', icon_color))
        self.prev_page_btn.setIcon(IconManager.get_icon('angle-left', icon_color))
        self.next_page_btn.setIcon(IconManager.get_icon('angle-right', icon_color))

    def initUI(self):
        layout = QVBoxLayout(self)

        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar cliente por nome, telefone ou email...")
        self.search_input.returnPressed.connect(self.pesquisar_clientes)
        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar")
        self.search_button.clicked.connect(self.pesquisar_clientes)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addWidget(search_group)

        self.tabela = QTableWidget()
        # MODIFICAÇÃO: Aumentado para 7 colunas
        self.tabela.setColumnCount(7)
        # MODIFICAÇÃO: Adicionada a coluna "Endereço"
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Nascimento (Idade)", "Telefone", "Email", "Endereço", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        paginacao_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton(" Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
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
        self.add_button = QPushButton(" Adicionar Cliente")
        self.add_button.setObjectName("primaryActionButton")
        self.add_button.clicked.connect(self.abrir_formulario_cliente)
        self.importar_csv_button = QPushButton(" Importar CSV")
        self.importar_csv_button.setObjectName("secondaryActionButton")
        self.importar_csv_button.clicked.connect(self.importar_csv)
        self.exportar_csv_button = QPushButton(" Exportar CSV")
        self.exportar_csv_button.setObjectName("secondaryActionButton")
        self.exportar_csv_button.clicked.connect(self.exportar_csv)
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.importar_csv_button)
        action_layout.addWidget(self.exportar_csv_button)
        layout.addLayout(action_layout)
        
    def atualizar_tabela(self, clientes):
        self.tabela.setRowCount(0)
        icon_color = self.theme_colors.get('text_color', '#000')
        
        for row, cliente in enumerate(clientes):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(cliente['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(self.formatar_data_nascimento(cliente['data_nascimento'])))
            self.tabela.setItem(row, 3, QTableWidgetItem(cliente['telefone'] or ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(cliente['email'] or ""))
            # MODIFICAÇÃO: Adicionada a célula de endereço na coluna 5
            self.tabela.setItem(row, 5, QTableWidgetItem(cliente.get('endereco', ''))) # .get() para segurança
            
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(5, 2, 5, 2); acoes_layout.setSpacing(5)
            
            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), " ")
            editar_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            editar_btn.clicked.connect(lambda _, c_id=cliente['id']: self.abrir_formulario_cliente(c_id))
            
            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), " ")
            excluir_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            excluir_btn.clicked.connect(lambda _, c_id=cliente['id']: self.excluir_cliente(c_id))
            
            acoes_layout.addWidget(editar_btn); acoes_layout.addWidget(excluir_btn)
            
            # MODIFICAÇÃO: Widget de ações movido para a coluna 6
            self.tabela.setCellWidget(row, 6, acoes_widget)
            
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
        self.atualizar_visualizacao_dados()
    
    def pesquisar_clientes(self):
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()

    def atualizar_visualizacao_dados(self):
        filtros = {'termo_pesquisa': self.search_input.text()}
        total_itens = self.db.contar_clientes_filtrados(filtros)
        clientes = self.db.listar_clientes_paginado_e_filtrado(
            filtros, self.pagina_atual, self.itens_por_pagina
        )
        self.atualizar_tabela(clientes)
        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina) or 1
        self.page_label.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.prev_page_btn.setEnabled(self.pagina_atual > 1)
        self.next_page_btn.setEnabled(self.pagina_atual < self.total_paginas)

    def formatar_data_nascimento(self, data_nascimento):
        if not data_nascimento: return ""
        try:
            data = datetime.strptime(str(data_nascimento), '%Y-%m-%d')
            hoje = datetime.now()
            idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
            return f"{data.strftime('%d/%m/%Y')} ({idade} anos)"
        except (ValueError, TypeError):
            return str(data_nascimento)

    def abrir_formulario_cliente(self, cliente_id=None):
        dialog = FormularioCliente(self.db, self.theme_colors, cliente_id, self)
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_visualizacao_dados()
            self.dados_clientes_alterados.emit()

    def excluir_cliente(self, cliente_id):
        dialog = AlertDialog(self, "Confirmar Exclusão", 
                             "Tem certeza que deseja excluir este cliente?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        if dialog.exec_() == QMessageBox.Yes:
            if self.db.excluir_cliente(cliente_id):
                AlertDialog(self, "Sucesso", "Cliente excluído com sucesso.", alert_type='success', theme_colors=self.theme_colors).exec_()
                self.atualizar_visualizacao_dados()
                self.dados_clientes_alterados.emit()
            else:
                AlertDialog(self, "Erro", "Não foi possível excluir o cliente.", alert_type='error', theme_colors=self.theme_colors).exec_()
    
    def exportar_csv(self):
        try:
            arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar arquivo CSV", "clientes.csv", "Arquivos CSV (*.csv)")
            if not arquivo: return
            
            clientes = self.db.listar_clientes()
            if not clientes:
                AlertDialog(self, "Exportar CSV", "Não há clientes cadastrados para exportar.", alert_type='info', theme_colors=self.theme_colors).exec_()
                return
            
            with open(arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'nome', 'data_nascimento', 'telefone', 'email', 'endereco']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for cliente in clientes:
                    writer.writerow({k: cliente.get(k, '') for k in fieldnames})
            
            AlertDialog(self, "Sucesso", f"Dados exportados com sucesso para:\n{arquivo}", alert_type='success', theme_colors=self.theme_colors).exec_()

        except Exception as e:
            AlertDialog(self, "Erro", f"Erro ao exportar CSV: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()
    
    def importar_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importar Clientes CSV", "", "CSV Files (*.csv)")
        if not file_path: return

        self.progress_dialog = ThemedProgressDialog(self, "Importando Clientes", "Aguarde enquanto os dados são processados...", self.theme_colors)
        
        self.import_thread = ClienteCsvImportWorker(self.db.db_path, file_path)
        self.import_thread.progress.connect(self.progress_dialog.setValue)
        self.import_thread.finished.connect(self.importacao_concluida)
        self.progress_dialog.canceled.connect(self.import_thread.terminate)
        
        self.import_thread.start()
        self.progress_dialog.exec_()

    def importacao_concluida(self, importados, atualizados, erros, detalhes):
        self.progress_dialog.close()
        self.atualizar_visualizacao_dados()
        if importados > 0 or atualizados > 0:
            self.dados_clientes_alterados.emit()
        msg = (f"Importação concluída!\n\n✔ Clientes novos: {importados}\n✔ Clientes atualizados: {atualizados}\n❌ Linhas com erro: {erros}")
        if detalhes:
            msg += "\n\nDetalhes dos problemas:\n" + "\n".join(detalhes[:5])
            alert_type = 'warning' if (importados > 0 or atualizados > 0) else 'error'
            title = "Importação Finalizada com Avisos"
            AlertDialog(self, title, msg, alert_type=alert_type, theme_colors=self.theme_colors).exec_()
        else:
            AlertDialog(self, "Importação Concluída", msg, alert_type='success', theme_colors=self.theme_colors).exec_()

    def selecionar_item_por_id(self, item_id):
        for row in range(self.tabela.rowCount()):
            item = self.tabela.item(row, 0)
            if item and item.data(Qt.UserRole) == item_id:
                self.tabela.selectRow(row)
                self.tabela.scrollToItem(item, QTableWidget.ScrollHint.PositionAtCenter)
                break

class FormularioCliente(QDialog):
    def __init__(self, db, theme_colors, cliente_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.theme_colors = theme_colors
        self.cliente_id = cliente_id
        self.cliente = None
        self.drag_position = None # Para arrastar a janela

        # MODIFICAÇÃO: Configurações para janela sem bordas
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        if cliente_id:
            self.cliente = self.db.obter_cliente(cliente_id)
            if not self.cliente:
                # Use o AlertDialog para consistência
                AlertDialog(parent, "Erro", "Cliente não encontrado!", alert_type='error', theme_colors=theme_colors).exec_()
                self.reject()
                return
        
        self.initUI()
        self.apply_styles()
        
        if self.cliente:
            self.carregar_dados_cliente()
    
    def initUI(self):
        self.setFixedWidth(500)
        
        # MODIFICAÇÃO: Estrutura principal para janela sem bordas
        main_container = QFrame(self)
        main_container.setObjectName("mainContainer")

        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(main_container)

        container_layout = QVBoxLayout(main_container)
        container_layout.setContentsMargins(1, 1, 1, 1)
        container_layout.setSpacing(0)

        # --- Cabeçalho Customizado ---
        header = self._criar_cabecalho()
        
        # --- Corpo do Formulário ---
        body = self._criar_corpo()

        container_layout.addWidget(header)
        container_layout.addWidget(body)

    def _criar_cabecalho(self):
        """Cria o widget de cabeçalho da janela."""
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 10, 10)
        
        title_label = QLabel("Cadastro de Cliente")
        title_label.setObjectName("headerTitleLabel")

        help_button = QPushButton(IconManager.get_icon('ajuda', color=self.theme_colors.get('text_secondary')), "")
        help_button.setObjectName("controlButton")
        help_button.setFixedSize(28, 28)

        close_button = QPushButton(IconManager.get_icon('fechar', color=self.theme_colors.get('text_secondary')), "")
        close_button.setObjectName("controlButton")
        close_button.setFixedSize(28, 28)
        close_button.clicked.connect(self.reject)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(help_button)
        header_layout.addWidget(close_button)
        return header

    def _criar_corpo(self):
        """Cria o widget de corpo com todos os campos do formulário."""
        body = QWidget()
        layout = QVBoxLayout(body)
        layout.setContentsMargins(20, 15, 20, 20)

        form_group = QGroupBox("Dados do Cliente")
        form_layout = QFormLayout(form_group)
        
        self.nome_input = QLineEdit()
        self.data_nascimento_input = QDateEdit(calendarPopup=True)
        self.data_nascimento_input.setDate(QDate.currentDate().addYears(-18))
        self.data_nascimento_input.setDisplayFormat("dd/MM/yyyy")

        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        
        form_layout.addRow("Nome (*):", self.nome_input)
        form_layout.addRow("Data de Nascimento:", self.data_nascimento_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Endereço:", self.endereco_input)
        layout.addWidget(form_group)
        
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(IconManager.get_icon('save', 'white'), " Salvar")
        self.salvar_btn.setObjectName("primaryButton")
        self.salvar_btn.clicked.connect(self.salvar_cliente)
        
        self.cancelar_btn = QPushButton(IconManager.get_icon('cancel', self.theme_colors['text_color']), " Cancelar")
        self.cancelar_btn.setObjectName("secondaryButton")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        layout.addLayout(button_layout)
        return body

    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f"""
            #mainContainer {{
                background-color: {colors['bg_color']};
                border-radius: 12px;
                border: 1px solid {colors['border_color']};
            }}
            #header {{
                border-bottom: 1px solid {colors['border_color']};
            }}
            #headerTitleLabel {{
                color: {colors.get('text_color', '#000')};
                font-weight: bold; font-size: 11pt;
            }}
            #controlButton {{ background: transparent; border: none; border-radius: 14px; }}
            #controlButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }}
            QGroupBox {{
                font-weight: bold; color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 6px; margin-top: 10px;
                padding: 15px 10px 10px 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 5px; left: 10px;
            }}
            QLabel, QDateEdit {{ color: {colors['text_color']}; }}
            QLineEdit, QDateEdit {{
                background-color: {colors['surface_color']};
                border: 1px solid {colors['border_color']};
                padding: 6px; border-radius: 4px;
            }}
            QLineEdit:focus, QDateEdit:focus {{ border: 1px solid {colors['accent_color']}; }}
            QCalendarWidget QWidget {{ alternate-background-color: {colors['button_hover']}; }}
            #qt_calendar_navigationbar {{ background-color: {colors['surface_color']}; }}
            QPushButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; min-width: 90px;}}
            #primaryButton {{ background-color: {colors['accent_color']}; color: white; border: none; }}
            #secondaryButton {{
                background-color: transparent; color: {colors.get('text_color', '#000')};
                border: 1px solid {colors['border_color']};
            }}
            #secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }}
        """)

    def carregar_dados_cliente(self):
        self.nome_input.setText(self.cliente['nome'])
        if self.cliente.get('data_nascimento'):
            try:
                data = datetime.strptime(str(self.cliente['data_nascimento']), '%Y-%m-%d')
                self.data_nascimento_input.setDate(QDate(data.year, data.month, data.day))
            except (ValueError, TypeError): pass
        self.telefone_input.setText(self.cliente.get('telefone', ''))
        self.email_input.setText(self.cliente.get('email', ''))
        self.endereco_input.setText(self.cliente.get('endereco', ''))

    def salvar_cliente(self):
        nome = self.nome_input.text().strip()
        if not nome:
            AlertDialog(self, "Campo Obrigatório", "O nome do cliente é obrigatório!", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return
        
        dados = {
            'nome': nome,
            'data_nascimento': self.data_nascimento_input.date().toString("yyyy-MM-dd"),
            'telefone': self.telefone_input.text().strip(),
            'email': self.email_input.text().strip(),
            'endereco': self.endereco_input.text().strip()
        }
        
        try:
            if self.cliente_id:
                sucesso = self.db.atualizar_cliente(self.cliente_id, **dados)
                mensagem = "Cliente atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_cliente(**dados)
                mensagem = "Cliente cadastrado com sucesso!"
            
            if sucesso:
                AlertDialog(self, "Sucesso", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()
                self.accept()
            else:
                AlertDialog(self, "Erro", "Não foi possível salvar o cliente.", alert_type='error', theme_colors=self.theme_colors).exec_()
        except Exception as e:
            AlertDialog(self, "Erro Crítico", f"Ocorreu um erro inesperado:\n{str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()

    # --- Eventos para mover a janela ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()