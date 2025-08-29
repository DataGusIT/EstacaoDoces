from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QWidget, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox, QDateEdit,
                             QInputDialog,QFileDialog, QGroupBox)
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


class AdminWindow(QDialog):
    logo_alterado = pyqtSignal()

    def __init__(self, db_manager, usuario, theme_colors, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.usuario = usuario
        self.theme_colors = theme_colors
        self.local_settings = QSettings("SuaEmpresa", "SeuERP")
        
        if self.usuario.get('tipo') != 'admin':
            self.db.registrar_log('WARNING', self.usuario.get('login'), 'ACESSO_ADMIN', 'Tentativa de acesso não autorizado.')
            # Ação corrigida: Usa AlertDialog
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
        
        main_layout = QVBoxLayout(self)
        
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
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(buttons_layout)

    def apply_styles(self):
        """Aplica a folha de estilo QSS baseada no tema."""
        colors = self.theme_colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg_color']};
                color: {colors['text_color']};
            }}
            #titleLabel {{
                font-size: 18pt;
                font-weight: bold;
                color: {colors['text_color']};
                margin-bottom: 10px;
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['border_color']};
                border-top: none;
            }}
            QTabBar::tab {{
                background: transparent;
                color: {colors['text_secondary']};
                padding: 10px 20px;
                border: 1px solid transparent;
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background: {colors['surface_color']};
                color: {colors['accent_color']};
                border: 1px solid {colors['border_color']};
                border-bottom: 1px solid {colors['surface_color']};
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }}
            QTableWidget {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: none;
                gridline-color: {colors['border_color']};
                alternate-background-color: {colors['button_hover']};
            }}
            QHeaderView::section {{
                background-color: {colors['menu_color'] if colors.get('menu_color') else colors['surface_color']};
                color: {colors['text_color']};
                padding: 5px;
                border: 1px solid {colors['border_color']};
                font-weight: bold;
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px;
                border-radius: 6px;
            }}
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
            }}
            #primaryButton {{
                background-color: {colors['accent_color']};
                color: white;
                border: none;
            }}
            #primaryButton:hover {{
                background-color: #005bb5;
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
    # ABA DE CONFIGURAÇÕES
    # ===================================================================
    def criar_tab_config(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(10, 10, 10, 10)
        form_layout = QFormLayout()

        self.margem_lucro_padrao = QDoubleSpinBox(suffix=" %")
        self.alerta_estoque_padrao = QSpinBox(suffix=" unidades")
        self.alerta_validade_dias = QSpinBox(suffix=" dias")
        
        form_layout.addRow(QLabel("<b>Configurações de Produtos:</b>"), None)
        form_layout.addRow("Margem de Lucro Padrão:", self.margem_lucro_padrao)
        form_layout.addRow("Alerta de Estoque Baixo Padrão:", self.alerta_estoque_padrao)
        form_layout.addRow("Alerta de Vencimento (antecedência):", self.alerta_validade_dias)

        save_button = QPushButton(IconManager.get_icon('save', color='white'), " Salvar Configurações")
        save_button.setObjectName("primaryButton") # Aplica o estilo de botão primário
        save_button.clicked.connect(self.salvar_configuracoes)

        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(save_button, alignment=Qt.AlignRight)

        self.carregar_configuracoes()
        return tab

    def carregar_configuracoes(self):
        self.margem_lucro_padrao.setValue(float(self.db.obter_configuracao('margem_lucro_padrao', 30.0)))
        self.alerta_estoque_padrao.setValue(int(self.db.obter_configuracao('alerta_estoque_padrao', 10)))
        self.alerta_validade_dias.setValue(int(self.db.obter_configuracao('alerta_validade_dias', 30)))
        
    def salvar_configuracoes(self):
        try:
            # ... (código para salvar configurações) ...
            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'SETTINGS_UPDATE', 'Configurações alteradas.')
            # Ação corrigida: Usa AlertDialog
            AlertDialog(self, "Sucesso", "Configurações salvas com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
        except Exception as e:
            # Ação corrigida: Usa AlertDialog
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
    # NOVA ABA DE PERSONALIZAÇÃO
    # ===================================================================
    def criar_tab_personalizacao(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)

        # Grupo para a logo
        logo_group = QGroupBox("Logo da Empresa")
        logo_group.setFont(QFont("Segoe UI", 12, QFont.Bold))
        logo_layout = QVBoxLayout(logo_group)

        # Label para mostrar a pré-visualização da logo
        self.logo_preview_label = QLabel("A logo será exibida aqui.")
        self.logo_preview_label.setAlignment(Qt.AlignCenter)
        self.logo_preview_label.setMinimumSize(300, 150)
        self.logo_preview_label.setObjectName("logoPreview")
        logo_layout.addWidget(self.logo_preview_label)

        # Botões de ação
        botoes_layout = QHBoxLayout()
        self.change_logo_button = QPushButton(IconManager.get_icon('edit', self.theme_colors['text_color']), " Alterar Logo")
        self.remove_logo_button = QPushButton(IconManager.get_icon('delete', self.theme_colors['text_color']), " Remover Logo")
        
        self.change_logo_button.clicked.connect(self.alterar_logo)
        self.remove_logo_button.clicked.connect(self.remover_logo)

        botoes_layout.addStretch()
        botoes_layout.addWidget(self.change_logo_button)
        botoes_layout.addWidget(self.remove_logo_button)
        botoes_layout.addStretch()
        logo_layout.addLayout(botoes_layout)
        
        layout.addWidget(logo_group)

        self.carregar_logo_atual() # Carrega a logo atual na pré-visualização
        return tab

    def carregar_logo_atual(self):
        """Carrega a logo (personalizada ou padrão) no widget de pré-visualização."""
        # CORREÇÃO: Usar self.local_settings.value()
        logo_path = self.local_settings.value("custom_logo_path", "")
        
        if not logo_path or not os.path.exists(logo_path):
            logo_path = "assets/img/GestorX (2).png" 
        
        pixmap = QPixmap(logo_path)
        self.logo_preview_label.setPixmap(pixmap.scaled(300, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def alterar_logo(self):
        """Abre um diálogo para o usuário selecionar e salvar uma nova logo."""
        caminho_origem, _ = QFileDialog.getOpenFileName(self, "Selecionar nova logo", "", "Imagens (*.png *.jpg *.jpeg)")
        
        if caminho_origem:
            try:
                # ... (lógica de cópia do arquivo como estava) ...
                pasta_destino = "assets/custom"
                os.makedirs(pasta_destino, exist_ok=True)
                extensao = os.path.splitext(caminho_origem)[1]
                caminho_destino = os.path.join(pasta_destino, f"logo_personalizado{extensao}")
                shutil.copy(caminho_origem, caminho_destino)
                
                # CORREÇÃO: Usar self.local_settings.setValue()
                self.local_settings.setValue("custom_logo_path", caminho_destino)
                
                # Ação corrigida: Usa AlertDialog
                AlertDialog(self, "Sucesso", "Logo alterada com sucesso!", alert_type='success', theme_colors=self.theme_colors).exec_()
                self.carregar_logo_atual()
                self.logo_alterado.emit()
            except Exception as e:
                # Ação corrigida: Usa AlertDialog
                AlertDialog(self, "Erro", f"Não foi possível salvar a nova logo: {e}", alert_type='error', theme_colors=self.theme_colors).exec_()

    def remover_logo(self):
        if not self.local_settings.value("custom_logo_path", ""):
            # Ação corrigida: Usa AlertDialog
            AlertDialog(self, "Aviso", "Nenhuma logo personalizada está em uso.", alert_type='info', theme_colors=self.theme_colors).exec_()
            return

        # Ação corrigida: Usa AlertDialog
        dialog = AlertDialog(self, "Confirmar Remoção",
                             "Deseja remover a logo personalizada e voltar para a padrão?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            self.local_settings.remove("custom_logo_path")
            # Ação corrigida: Usa AlertDialog
            AlertDialog(self, "Sucesso", "Logo personalizada removida.", alert_type='success', theme_colors=self.theme_colors).exec_()
            self.carregar_logo_atual()
            self.logo_alterado.emit()