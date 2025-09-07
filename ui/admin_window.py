from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QWidget, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox, QDateEdit,
                             QInputDialog,QFileDialog, QGroupBox, QFrame)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QSettings, QTimer
from PyQt5.QtGui import QColor, QIcon, QFont, QPixmap
import hashlib
import os
import shutil

from .icon_manager import IconManager


# Adicione estas importações extras no topo do seu arquivo
from PyQt5.QtWidgets import QFrame, QLineEdit
from PyQt5.QtCore import Qt

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

# --- CLASSE 2: DIÁLOGO DE ENTRADA DE TEXTO TEMÁTICO ---
class ThemedInputDialog(QDialog):
    """Substituto temático para QInputDialog.getText()."""
    def __init__(self, parent, title, message, echo_mode=QLineEdit.Normal, theme_colors=None):
        super().__init__(parent)
        self.theme_colors = theme_colors if theme_colors is not None else {}
        self.drag_position = None
        self.text_value = ""
        
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        
        self._setup_ui(title, message, echo_mode)
        self.apply_styles()

    def _setup_ui(self, title, message, echo_mode):
        self.setMinimumWidth(400)
        container = QFrame(self); container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(container); main_layout.setContentsMargins(20, 20, 20, 20); main_layout.setSpacing(15)
        
        title_label = QLabel(title); title_label.setObjectName("subtitleLabel")
        message_label = QLabel(message); message_label.setObjectName("messageLabel")
        
        self.line_edit = QLineEdit()
        self.line_edit.setEchoMode(echo_mode)
        
        button_layout = QHBoxLayout(); button_layout.addStretch()
        cancel_button = QPushButton("Cancelar"); cancel_button.setObjectName("secondaryButton")
        ok_button = QPushButton("OK"); ok_button.setObjectName("primaryButton")
        
        cancel_button.clicked.connect(self.reject)
        ok_button.clicked.connect(self.accept_input)
        
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(message_label)
        main_layout.addWidget(self.line_edit)
        main_layout.addLayout(button_layout)
        
        base_layout = QVBoxLayout(self); base_layout.addWidget(container)

    def accept_input(self):
        self.text_value = self.line_edit.text()
        self.accept()

    def getText(self):
        # Método estático para conveniência, imitando QInputDialog
        if self.exec_() == QDialog.Accepted:
            return self.text_value, True
        return "", False

    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f""" #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }} #subtitleLabel {{ color: {colors.get('text_color', '#000')}; font-size: 14pt; font-weight: bold; }} #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }} QLineEdit {{ background-color: {colors.get('bg_color', '#fff')}; border: 1px solid {colors.get('border_color', '#ccc')}; border-radius: 6px; padding: 8px; }} QPushButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; min-width: 90px;}} #primaryButton {{ background-color: {colors.get('accent_color', '#007AFF')}; color: white; border: none; }} #secondaryButton {{ background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }} """)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)


# ===================================================================
#       NOVA CLASSE BASE PARA DIÁLOGOS TEMÁTICOS
# ===================================================================
class ThemedDialog(QDialog):
    """
    Uma classe base para todos os diálogos que terão um cabeçalho
    customizado e temático, sem a barra de título padrão do Windows.
    """
    def __init__(self, parent, title, theme_colors, logo_pixmap=None):
        super().__init__(parent)
        self.theme_colors = theme_colors
        self.drag_position = None

        # Remove a barra de título padrão e permite fundo transparente
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        # --- Estrutura Principal ---
        # Container geral para aplicar bordas e cantos arredondados
        self.container = QFrame(self)
        self.container.setObjectName("mainContainer")

        base_layout = QVBoxLayout(self.container)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)
        
        # 1. Cabeçalho
        self.header = self._create_header(title, logo_pixmap)
        base_layout.addWidget(self.header)

        # 2. Conteúdo (um layout que as classes filhas irão preencher)
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(15, 10, 15, 15)
        self.content_layout.setSpacing(10)
        base_layout.addLayout(self.content_layout)

        # Layout final que contém o container principal
        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0,0,0,0)
        final_layout.addWidget(self.container)
    
    def _create_header(self, title, logo_pixmap):
        """Cria o widget de cabeçalho temático."""
        header_widget = QFrame()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(45)
        
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(15, 0, 5, 0)
        
        if logo_pixmap:
            logo_label = QLabel()
            logo_label.setPixmap(logo_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(logo_label)

        title_label = QLabel(title)
        title_label.setObjectName("headerTitleLabel")
        
        close_button = QPushButton()
        close_button.setObjectName("controlButton")
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors.get('text_secondary')))
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        return header_widget

    def apply_base_styles(self):
        """Aplica os estilos essenciais para a janela base."""
        theme = self.theme_colors
        style = f"""
            #mainContainer {{
                background-color: {theme.get('bg_color', '#fff')};
                border-radius: 8px;
                border: 1px solid {theme.get('border_color', '#555')};
            }}
            #header {{
                background-color: {theme.get('surface_color', '#333')};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid {theme.get('border_color', '#555')};
            }}
            #headerTitleLabel {{
                color: {theme.get('text_color', '#fff')};
                font-weight: bold;
                font-size: 11pt;
            }}
            #controlButton {{
                background-color: transparent; border: none; border-radius: 4px;
            }}
            #controlButton:hover {{
                background-color: {theme.get('button_hover', '#555')};
            }}
        """
        self.container.setStyleSheet(style)

    # Métodos para arrastar a janela
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.header.underMouse():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

class AdminWindow(ThemedDialog):
    logo_alterado = pyqtSignal()

    def __init__(self, db_manager, usuario, settings, theme_colors, parent=None):
        super().__init__(parent, "Painel de Administração", theme_colors)
        
        self.db = db_manager
        self.usuario = usuario
        self.settings = settings  # <-- A LINHA CRUCIAL QUE FALTAVA
        # self.local_settings = QSettings("SuaEmpresa", "SeuERP")
        
        if self.usuario.get('tipo') != 'admin':
            self.db.registrar_log('WARNING', self.usuario.get('login'), 'ACESSO_ADMIN', 'Tentativa de acesso não autorizado.')
            QTimer.singleShot(0, self.show_access_denied_and_close)
            return
        
        self.init_ui()
        self.apply_styles()
        self.db.registrar_log('ADMIN', self.usuario.get('login'), 'ACESSO_ADMIN', 'Acessou o painel de administração.')

    # NOVO MÉTODO (adicionar abaixo de __init__)
    def show_access_denied_and_close(self):
        AlertDialog(None, "Acesso Negado", "Você não tem permissão para acessar esta área.", alert_type='error', theme_colors=self.theme_colors).exec_()
        self.reject()

    def init_ui(self):
        """Inicializa a interface do usuário (sem estilos fixos)."""
        self.setWindowTitle("Painel de Administração")
        self.setMinimumSize(900, 700)
                
        title_label = QLabel("Painel de Administração")
        title_label.setObjectName("titleLabel") # Para estilização
        
        self.tab_widget = QTabWidget()
        
        self.usuarios_tab = self.criar_tab_usuarios()
        self.tab_widget.addTab(self.usuarios_tab, IconManager.get_icon('clientes', self.theme_colors['text_secondary']), "Gerenciar Usuários")
        
        self.config_tab = self.criar_tab_config()
        self.tab_widget.addTab(self.config_tab, IconManager.get_icon('config', self.theme_colors['text_secondary']), "Configurações")
        
        self.logs_tab = self.criar_tab_logs()
        self.tab_widget.addTab(self.logs_tab, IconManager.get_icon('relatorio', self.theme_colors['text_secondary']), "Logs de Atividades")
        
        self.personalizacao_tab = self.criar_tab_personalizacao()
        self.tab_widget.addTab(self.personalizacao_tab, IconManager.get_icon('dashboard', self.theme_colors['text_secondary']), "Personalização")
        
        buttons_layout = QHBoxLayout()
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        # Adiciona os widgets principais ao layout de conteúdo da classe base
        self.content_layout.addWidget(self.tab_widget)
        self.content_layout.addLayout(buttons_layout)

    def apply_styles(self):
        """Aplica a folha de estilo QSS baseada no tema."""
        
        # PASSO 1: Chama o método da classe pai (ThemedDialog) para estilizar
        # o container principal, o cabeçalho e os botões de controle.
        self.apply_base_styles()

        # PASSO 2: Define os estilos específicos APENAS para o conteúdo desta janela
        # (abas, tabelas, botões internos, etc.).
        colors = self.theme_colors
        
        # Usamos self.setStyleSheet() para adicionar o novo estilo.
        # O estilo da classe base já foi aplicado ao self.container, então não será sobrescrito.
        self.setStyleSheet(f"""
            /* --- ESTILOS GERAIS PARA A JANELA ADMIN (HERDADOS) --- */
            /*
            * A cor de fundo principal e as bordas já foram definidas por apply_base_styles().
            * Aqui, definimos estilos para os widgets DENTRO da janela.
            */

            /* --- ABAS (TABS) --- */
            QTabWidget::pane {{
                border: 1px solid {colors['border_color']};
                border-top: none;
                background-color: {colors['bg_color']}; /* Fundo da área da aba */
            }}
            QTabBar::tab {{
                background: transparent;
                color: {colors['text_secondary']};
                padding: 10px 20px;
                border: 1px solid transparent;
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background: {colors['bg_color']}; /* A aba selecionada tem o fundo da janela */
                color: {colors['accent_color']};
                border: 1px solid {colors['border_color']};
                border-bottom: 1px solid {colors['bg_color']}; /* Esconde a borda inferior */
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}

            /* --- TABELAS --- */
            QTableWidget {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: none;
                gridline-color: {colors['border_color']};
                alternate-background-color: {colors['button_hover']};
            }}
            QHeaderView::section {{
                background-color: {colors.get('menu_color', colors['surface_color'])};
                color: {colors['text_color']};
                padding: 5px;
                border: 1px solid {colors['border_color']};
                font-weight: bold;
            }}

            /* --- CAMPOS DE FORMULÁRIO --- */
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px;
                border-radius: 6px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border-color: {colors['accent_color']};
            }}
            QGroupBox {{
                color: {colors['text_secondary']};
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

            /* --- BOTÕES --- */
            QPushButton {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                border-color: {colors['accent_color']};
                background-color: {colors['button_hover']};
            }}
            #primaryButton {{
                background-color: {colors['accent_color']};
                color: white;
                border: none;
            }}
            #primaryButton:hover {{
                background-color: #005bb5; /* Cor de hover fixa mais escura */
            }}
        """)

    # ===================================================================
    # ABA DE USUÁRIOS
    # ===================================================================
    def criar_tab_usuarios(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 10, 0, 0)
        
        self.usuarios_table = QTableWidget()
        self.usuarios_table.setColumnCount(6)
        self.usuarios_table.setHorizontalHeaderLabels(["ID", "Nome", "Login", "Email", "Tipo", "Status"])
        self.usuarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usuarios_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.usuarios_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.usuarios_table.setAlternatingRowColors(True)
        self.usuarios_table.doubleClicked.connect(self.editar_usuario)

        action_layout = QHBoxLayout()
        icon_color = self.theme_colors.get('text_color', '#000000')

        self.add_user_button = QPushButton(IconManager.get_icon('add', color=icon_color), " Adicionar")
        self.edit_user_button = QPushButton(IconManager.get_icon('edit', color=icon_color), " Editar")
        self.toggle_user_button = QPushButton(IconManager.get_icon('unlock', color=icon_color), " Ativar/Desativar")
        self.reset_pass_button = QPushButton(IconManager.get_icon('password', color=icon_color), " Resetar Senha")
        self.refresh_users_button = QPushButton(IconManager.get_icon('atualizar', color=icon_color), " Atualizar")

        self.add_user_button.clicked.connect(self.adicionar_usuario)
        self.edit_user_button.clicked.connect(self.editar_usuario)
        self.toggle_user_button.clicked.connect(self.alternar_status_usuario)
        self.reset_pass_button.clicked.connect(self.resetar_senha_usuario)
        self.refresh_users_button.clicked.connect(self.carregar_usuarios)
        
        action_layout.addWidget(self.add_user_button)
        action_layout.addWidget(self.edit_user_button)
        action_layout.addWidget(self.toggle_user_button)
        action_layout.addWidget(self.reset_pass_button)
        action_layout.addStretch()
        action_layout.addWidget(self.refresh_users_button)
        
        layout.addLayout(action_layout)
        layout.addWidget(self.usuarios_table)
        
        self.carregar_usuarios()
        return tab

    # 2. Atualizar a chamada da UserDialogWindow
    def adicionar_usuario(self):
        from ui.user_dialog_window import UserDialogWindow
        # PASSA O TEMA PARA O DIÁLOGO
        dialog = UserDialogWindow(self.db, self.theme_colors)
        if dialog.exec_() == QDialog.Accepted:
            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'USER_CREATE', f"Usuário criado.")
            self.carregar_usuarios()

    def editar_usuario(self):
        user_id, _ = self.get_selected_user_info()
        if not user_id: return
        
        from ui.user_dialog_window import UserDialogWindow
        # PASSA O TEMA PARA O DIÁLOGO
        dialog = UserDialogWindow(self.db, self.theme_colors, user_id)
        if dialog.exec_() == QDialog.Accepted:
            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'USER_UPDATE', f"Dados do usuário ID {user_id} atualizados.")
            self.carregar_usuarios()
    
    def carregar_usuarios(self):
        try:
            self.usuarios_table.setRowCount(0)
            usuarios = self.db.listar_usuarios()
            for i, usuario in enumerate(usuarios):
                self.usuarios_table.insertRow(i)
                self.usuarios_table.setItem(i, 0, QTableWidgetItem(str(usuario['id'])))
                self.usuarios_table.setItem(i, 1, QTableWidgetItem(usuario['nome']))
                self.usuarios_table.setItem(i, 2, QTableWidgetItem(usuario['login']))
                self.usuarios_table.setItem(i, 3, QTableWidgetItem(usuario['email'] or ""))
                self.usuarios_table.setItem(i, 4, QTableWidgetItem(usuario['tipo']))
                
                status = "Ativo" if usuario['ativo'] == 1 else "Inativo"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('green') if usuario['ativo'] else QColor('red'))
                self.usuarios_table.setItem(i, 5, status_item)
        except Exception as e:
            AlertDialog(self, "Erro", f"Erro ao carregar usuários: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()

    def get_selected_user_info(self):
        selected_rows = self.usuarios_table.selectedIndexes()
        if not selected_rows:
            # Ação corrigida: Usa AlertDialog
            AlertDialog(self, "Aviso", "Por favor, selecione um usuário na tabela.", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return None, None
        row = selected_rows[0].row()
        user_id = int(self.usuarios_table.item(row, 0).text())
        user_info = self.db.obter_usuario_por_id(user_id)
        return user_id, user_info

    def alternar_status_usuario(self):
        user_id, user_info = self.get_selected_user_info()
        if not user_id: return

        if user_id == self.usuario['id']:
            # Ação corrigida: Usa AlertDialog
            AlertDialog(self, "Ação Inválida", "Você não pode desativar seu próprio usuário.", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        novo_status = 0 if user_info['ativo'] == 1 else 1
        status_texto = "desativar" if novo_status == 0 else "ativar"
        
        # Ação corrigida: Usa AlertDialog para confirmação
        dialog = AlertDialog(self, "Confirmar Ação",
                             f"Deseja realmente {status_texto} o usuário '{user_info['nome']}'?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            success, msg = self.db.atualizar_usuario(user_id, user_info['nome'], user_info['login'], user_info['email'], user_info['tipo'], novo_status)
            if success:
                action = 'USER_DEACTIVATE' if novo_status == 0 else 'USER_ACTIVATE'
                self.db.registrar_log('ADMIN', self.usuario.get('login'), action, f"Usuário ID {user_id} ({user_info['nome']}) teve seu status alterado.")
                self.carregar_usuarios()
            else:
                # Ação corrigida: Usa AlertDialog
                AlertDialog(self, "Erro", msg, alert_type='error', theme_colors=self.theme_colors).exec_()

    def resetar_senha_usuario(self):
        user_id, user_info = self.get_selected_user_info()
        if not user_id: return

        # Ação corrigida: Usa ThemedInputDialog
        dialog = ThemedInputDialog(self, "Resetar Senha", f"Digite a nova senha para '{user_info['nome']}':",
                                   QLineEdit.Password, self.theme_colors)
        nova_senha, ok = dialog.getText()

        if ok and nova_senha:
            if len(nova_senha) < 6:
                # Ação corrigida: Usa AlertDialog
                AlertDialog(self, "Senha Inválida", "A senha deve ter pelo menos 6 caracteres.", alert_type='warning', theme_colors=self.theme_colors).exec_()
                return

            success, msg = self.db.alterar_senha_usuario(user_id, nova_senha)
            if success:
                self.db.registrar_log('ADMIN', self.usuario.get('login'), 'USER_PASS_RESET', f"Senha do usuário ID {user_id} resetada.")
                # Ação corrigida: Usa AlertDialog
                AlertDialog(self, "Sucesso", "Senha do usuário resetada com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
            else:
                # Ação corrigida: Usa AlertDialog
                AlertDialog(self, "Erro", msg, alert_type='error', theme_colors=self.theme_colors).exec_()

     # ===================================================================
    # ABA DE CONFIGURAÇÕES (CORRIGIDA E FINAL)
    # ===================================================================
    def criar_tab_config(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignTop)
        
        group_produtos = QGroupBox("Configurações de Produtos e Estoque")
        group_produtos_layout = QFormLayout(group_produtos)
        
        self.margem_lucro_padrao = QDoubleSpinBox(suffix=" %")
        self.alerta_estoque_padrao = QSpinBox(suffix=" unidades")
        self.alerta_validade_dias = QSpinBox(suffix=" dias")
        self.fator_reposicao_estoque = QSpinBox(prefix="+ ", suffix=" unidades")
        self.fator_reposicao_estoque.setToolTip("Valor a ser somado ao estoque mínimo para a sugestão de compra no relatório.")
        
        group_produtos_layout.addRow("Margem de Lucro Padrão:", self.margem_lucro_padrao)
        group_produtos_layout.addRow("Alerta de Estoque Baixo Padrão:", self.alerta_estoque_padrao)
        group_produtos_layout.addRow("Alerta de Vencimento (antecedência):", self.alerta_validade_dias)
        group_produtos_layout.addRow("Fator de Reposição (Sugestão de Compra):", self.fator_reposicao_estoque)

        layout.addWidget(group_produtos)
        
        save_button = QPushButton(IconManager.get_icon('save', color='white'), " Salvar Configurações")
        save_button.setObjectName("primaryButton")
        save_button.clicked.connect(self.salvar_configuracoes)

        layout.addStretch()
        layout.addWidget(save_button, alignment=Qt.AlignRight)

        self.carregar_configuracoes()
        return tab

    def carregar_configuracoes(self):
        self.margem_lucro_padrao.setValue(float(self.db.obter_configuracao('margem_lucro_padrao', 30.0)))
        self.alerta_estoque_padrao.setValue(int(self.db.obter_configuracao('alerta_estoque_padrao', 10)))
        self.alerta_validade_dias.setValue(int(self.db.obter_configuracao('alerta_validade_dias', 30)))
        self.fator_reposicao_estoque.setValue(int(self.db.obter_configuracao('fator_reposicao_estoque', 5)))
        
    def salvar_configuracoes(self):
        try:
            self.db.definir_configuracao('margem_lucro_padrao', self.margem_lucro_padrao.value())
            self.db.definir_configuracao('alerta_estoque_padrao', self.alerta_estoque_padrao.value())
            self.db.definir_configuracao('alerta_validade_dias', self.alerta_validade_dias.value())
            self.db.definir_configuracao('fator_reposicao_estoque', self.fator_reposicao_estoque.value())
            
            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'SETTINGS_UPDATE', 'Configurações gerais alteradas.')
            AlertDialog(self, "Sucesso", "Configurações salvas com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
        except Exception as e:
            AlertDialog(self, "Erro", f"Erro ao salvar configurações: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()


    # ===================================================================
    # ABA DE LOGS
    # ===================================================================
    def criar_tab_logs(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 10, 0, 0)

        filter_layout = QHBoxLayout()
        self.log_data_inicio = QDateEdit(QDate.currentDate().addMonths(-1))
        self.log_data_fim = QDateEdit(QDate.currentDate())
        self.log_usuario_input = QLineEdit()
        self.log_level_combo = QComboBox()
        
        self.log_data_inicio.setCalendarPopup(True)
        self.log_data_fim.setCalendarPopup(True)
        self.log_usuario_input.setPlaceholderText("Filtrar por usuário...")
        self.log_level_combo.addItems(["Todos", "ADMIN", "INFO", "WARNING", "ERROR"])

        filter_button = QPushButton(IconManager.get_icon('filter', color=self.theme_colors['text_color']), " Filtrar")
        filter_button.clicked.connect(self.carregar_logs)

        filter_layout.addWidget(QLabel("De:"))
        filter_layout.addWidget(self.log_data_inicio)
        filter_layout.addWidget(QLabel("Até:"))
        filter_layout.addWidget(self.log_data_fim)
        filter_layout.addWidget(self.log_usuario_input)
        filter_layout.addWidget(self.log_level_combo)
        filter_layout.addWidget(filter_button)

        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "Nível", "Usuário", "Ação", "Detalhes"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addLayout(filter_layout)
        layout.addWidget(self.logs_table)
        
        self.carregar_logs()
        return tab

    def carregar_logs(self):
        try:
            data_inicio = self.log_data_inicio.date().toString("yyyy-MM-dd")
            data_fim = self.log_data_fim.date().toString("yyyy-MM-dd")
            usuario = self.log_usuario_input.text()
            level = self.log_level_combo.currentText()

            logs = self.db.listar_logs(data_inicio, data_fim, usuario, level)

            self.logs_table.setRowCount(0)
            for i, log in enumerate(logs):
                self.logs_table.insertRow(i)
                self.logs_table.setItem(i, 0, QTableWidgetItem(log['timestamp']))
                self.logs_table.setItem(i, 1, QTableWidgetItem(log['level']))
                self.logs_table.setItem(i, 2, QTableWidgetItem(log['usuario_login']))
                self.logs_table.setItem(i, 3, QTableWidgetItem(log['action']))
                self.logs_table.setItem(i, 4, QTableWidgetItem(log['details']))
        except Exception as e:
            AlertDialog(self, "Erro", f"Erro ao carregar logs: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()

      # ===================================================================
    # ABA DE PERSONALIZAÇÃO (VERSÃO ÚNICA E CORRETA)
    # ===================================================================
    def criar_tab_personalizacao(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Bloco 1: Grupo para a logo
        logo_group = QGroupBox("Logo da Empresa para Relatórios")
        logo_layout = QVBoxLayout(logo_group)

        self.logo_preview_label = QLabel("A logo será exibida aqui.")
        self.logo_preview_label.setAlignment(Qt.AlignCenter)
        self.logo_preview_label.setMinimumSize(300, 150)
        self.logo_preview_label.setObjectName("logoPreview")
        logo_layout.addWidget(self.logo_preview_label)

        botoes_logo_layout = QHBoxLayout()
        self.change_logo_button = QPushButton(IconManager.get_icon('edit', self.theme_colors['text_color']), " Alterar Logo")
        self.remove_logo_button = QPushButton(IconManager.get_icon('delete', self.theme_colors['text_color']), " Remover Logo")
        self.change_logo_button.clicked.connect(self.alterar_logo)
        self.remove_logo_button.clicked.connect(self.remover_logo)
        botoes_logo_layout.addStretch()
        botoes_logo_layout.addWidget(self.change_logo_button)
        botoes_logo_layout.addWidget(self.remove_logo_button)
        botoes_logo_layout.addStretch()
        logo_layout.addLayout(botoes_logo_layout)
        
        # Bloco 2: Grupo de informações da empresa
        info_group = QGroupBox("Informações da Empresa para Relatórios")
        info_layout = QFormLayout(info_group)
        
        self.empresa_nome_input = QLineEdit()
        self.empresa_endereco_input = QLineEdit()
        self.empresa_telefone_input = QLineEdit()
        self.empresa_email_input = QLineEdit()
        self.empresa_cnpj_input = QLineEdit()

        info_layout.addRow("Nome da Empresa:", self.empresa_nome_input)
        info_layout.addRow("Endereço:", self.empresa_endereco_input)
        info_layout.addRow("Telefone:", self.empresa_telefone_input)
        info_layout.addRow("Email:", self.empresa_email_input)
        info_layout.addRow("CNPJ:", self.empresa_cnpj_input)

        self.save_info_button = QPushButton(IconManager.get_icon('save', 'white'), " Salvar Informações")
        self.save_info_button.setObjectName("primaryButton")
        self.save_info_button.clicked.connect(self.salvar_informacoes_empresa)
        info_layout.addRow("", self.save_info_button)

        layout.addWidget(logo_group)
        layout.addWidget(info_group)

        self.carregar_logo_atual()
        self.carregar_informacoes_empresa()
        return tab

    def carregar_informacoes_empresa(self):
        info = self.db.obter_informacoes_empresa()
        self.empresa_nome_input.setText(info.get('empresa_nome', ''))
        self.empresa_endereco_input.setText(info.get('empresa_endereco', ''))
        self.empresa_telefone_input.setText(info.get('empresa_telefone', ''))
        self.empresa_email_input.setText(info.get('empresa_email', ''))
        self.empresa_cnpj_input.setText(info.get('empresa_cnpj', ''))

    def salvar_informacoes_empresa(self):
        try:
            self.db.definir_configuracao('empresa_nome', self.empresa_nome_input.text())
            self.db.definir_configuracao('empresa_endereco', self.empresa_endereco_input.text())
            self.db.definir_configuracao('empresa_telefone', self.empresa_telefone_input.text())
            self.db.definir_configuracao('empresa_email', self.empresa_email_input.text())
            self.db.definir_configuracao('empresa_cnpj', self.empresa_cnpj_input.text())
            
            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'COMPANY_INFO_UPDATE', 'Informações da empresa alteradas.')
            AlertDialog(self, "Sucesso", "Informações da empresa salvas com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
        except Exception as e:
            AlertDialog(self, "Erro", f"Erro ao salvar informações: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()

    def carregar_logo_atual(self):
        logo_path = self.settings.get_value("custom_logo_path", "")
        
        if not logo_path or not os.path.exists(logo_path):
            logo_path = "assets/img/Logo2.png" 
        
        pixmap = QPixmap(logo_path)
        self.logo_preview_label.setPixmap(pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def alterar_logo(self):
        caminho_origem, _ = QFileDialog.getOpenFileName(self, "Selecionar nova logo", "", "Imagens (*.png *.jpg *.jpeg)")
        
        if caminho_origem:
            try:
                pasta_destino = "assets/custom"
                os.makedirs(pasta_destino, exist_ok=True)
                extensao = os.path.splitext(caminho_origem)[1]
                caminho_destino = os.path.join(pasta_destino, f"logo_personalizado{extensao}")
                shutil.copy(caminho_origem, caminho_destino)
                
                self.settings.set_value("custom_logo_path", caminho_destino)
                
                AlertDialog(self, "Sucesso", "Logo alterada com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
                self.carregar_logo_atual()
                self.logo_alterado.emit()
            except Exception as e:
                AlertDialog(self, "Erro", f"Não foi possível salvar a nova logo: {e}", alert_type='error', theme_colors=self.theme_colors).exec_()

    def remover_logo(self):
        if not self.settings.get_value("custom_logo_path", ""):
            AlertDialog(self, "Aviso", "Nenhuma logo personalizada está em uso.", alert_type='info', theme_colors=self.theme_colors).exec_()
            return

        dialog = AlertDialog(self, "Confirmar Remoção",
                             "Deseja remover a logo personalizada e voltar para a padrão?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            self.settings.remove("custom_logo_path")
            AlertDialog(self, "Sucesso", "Logo personalizada removida.", alert_type='success', theme_colors=self.theme_colors).exec_()
            self.carregar_logo_atual()
            self.logo_alterado.emit()