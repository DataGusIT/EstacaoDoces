from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QWidget, 
                             QSizePolicy, QSpacerItem, QScrollArea, QFrame)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QRegExpValidator, QLinearGradient
from PyQt5.QtCore import Qt, QRegExp

class MinimalLineEdit(QLineEdit):
    """Campo de texto minimalista"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_style()
        
    def setup_style(self):
        self.setFixedHeight(56)
        self.setStyleSheet("""
            QLineEdit {
                padding: 16px 20px;
                border: 1px solid #e8e8ed;
                border-radius: 16px;
                background-color: #ffffff;
                color: #1d1d1f;
                font-size: 16px;
                font-weight: 400;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                selection-background-color: #007AFF;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
                background-color: #ffffff;
                outline: none;
            }
            QLineEdit:read-only {
                background-color: #fbfbfd;
                border: 1px solid #f2f2f7;
                color: #8e8e93;
            }
            QLineEdit::placeholder {
                color: #c7c7cc;
            }
        """)

class MinimalFieldGroup(QWidget):
    """Grupo de campo minimalista"""
    
    def __init__(self, label_text, input_widget):
        super().__init__()
        self.setup_ui(label_text, input_widget)
        
    def setup_ui(self, label_text, input_widget):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)  # Aumentado de 8 para 10
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                color: #1d1d1f;
                font-size: 15px;
                font-weight: 500;
                padding-left: 4px;
                padding-top: 4px;
                padding-bottom: 6px;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
        """)
        label.setMinimumHeight(28)  # Aumentado de 24 para 28
        label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        
        layout.addWidget(label)
        layout.addWidget(input_widget)

class MinimalButton(QPushButton):
    """Botão minimalista"""
    
    def __init__(self, text, button_type="primary"):
        super().__init__(text)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        self.setFixedHeight(56)
        self.setCursor(Qt.PointingHandCursor)
        
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #1d1d1f;
                    color: white;
                    border: none;
                    border-radius: 16px;
                    font-weight: 500;
                    font-size: 16px;
                    font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                }
                QPushButton:hover {
                    background-color: #2c2c2e;
                }
                QPushButton:pressed {
                    background-color: #48484a;
                }
                QPushButton:disabled {
                    background-color: #f2f2f7;
                    color: #c7c7cc;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #8e8e93;
                    border: 1px solid #e8e8ed;
                    border-radius: 16px;
                    font-weight: 500;
                    font-size: 16px;
                    font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                }
                QPushButton:hover {
                    background-color: #f9f9f9;
                    color: #1d1d1f;
                    border: 1px solid #d1d1d6;
                }
                QPushButton:pressed {
                    background-color: #f2f2f7;
                }
            """)
        elif self.button_type == "close":
            self.setFixedSize(40, 40)
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #8e8e93;
                    border: none;
                    border-radius: 20px;
                    font-size: 16px;
                    font-weight: 300;
                    font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                }
                QPushButton:hover {
                    background-color: #f2f2f7;
                    color: #1d1d1f;
                }
            """)

class MinimalAvatar(QWidget):
    """Avatar minimalista"""
    
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedSize(80, 80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignCenter)
        
        # Container do avatar
        avatar_container = QWidget()
        avatar_container.setFixedSize(80, 80)
        avatar_container.setStyleSheet("""
            background-color: #f2f2f7;
            border-radius: 40px;
            border: 3px solid #ffffff;
        """)
        
        # Iniciais
        iniciais = "".join([nome[0].upper() for nome in self.usuario['nome'].split()[:2]])
        iniciais_label = QLabel(iniciais, avatar_container)
        iniciais_label.setFont(QFont("SF Pro Display", 24, QFont.Medium))
        iniciais_label.setStyleSheet("""
            color: #8e8e93;
            background-color: transparent;
            border: none;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        iniciais_label.setAlignment(Qt.AlignCenter)
        iniciais_label.resize(avatar_container.size())
        
        layout.addWidget(avatar_container)

class ProfileWindow(QDialog):
    """Janela de perfil minimalista"""
    
    def __init__(self, db, usuario):
        super().__init__()
        self.db = db
        self.usuario = usuario
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        self.setWindowTitle("Perfil")
        self.setFixedSize(520, 740)  # Aumentado de 720 para 740
        self.setModal(True)
        
        # Estilo da janela
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border: 1px solid #e8e8ed;
                border-radius: 20px;
            }
        """)
        
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Conteúdo principal
        content_widget = self.create_content()
        main_layout.addWidget(content_widget)
        
    def create_header(self):
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_widget.setStyleSheet("background-color: transparent;")
        
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(32, 20, 32, 20)
        
        # Título minimalista
        title_label = QLabel("Perfil")
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: 600;
            color: #1d1d1f;
            background-color: transparent;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        
        # Botão de fechar minimalista
        close_button = MinimalButton("✕", "close")
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        
        return header_widget
        
    def create_content(self):
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(32, 0, 32, 32)
        layout.setSpacing(0)
        
        # Avatar centralizado
        avatar_layout = QHBoxLayout()
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar = MinimalAvatar(self.usuario)
        avatar_layout.addWidget(avatar)
        layout.addLayout(avatar_layout)
        
        # Espaçamento
        layout.addItem(QSpacerItem(20, 16, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Nome do usuário centralizado
        name_label = QLabel(self.usuario['nome'])
        name_label.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #1d1d1f;
            background-color: transparent;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(name_label)
        
        # Tipo de usuário
        tipo_label = QLabel(f"{self.usuario['tipo'].capitalize()}")
        tipo_label.setStyleSheet("""
            font-size: 16px;
            color: #8e8e93;
            background-color: transparent;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        tipo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(tipo_label)
        
        # Espaçamento
        layout.addItem(QSpacerItem(20, 32, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Reduzido de 48 para 32
        
        # Formulário
        form_layout = self.create_form()
        layout.addLayout(form_layout)
        
        # Espaçamento
        layout.addItem(QSpacerItem(20, 24, QSizePolicy.Minimum, QSizePolicy.Fixed))  # Reduzido de 32 para 24
        
        # Botões
        buttons_layout = self.create_buttons()
        layout.addLayout(buttons_layout)
        
        return content_widget
        
    def create_form(self):
        layout = QVBoxLayout()
        layout.setSpacing(28)  # Aumentado de 24 para 28
        
        # Campo Nome
        self.name_edit = MinimalLineEdit(self.usuario['nome'])
        self.name_edit.setPlaceholderText("Digite seu nome completo")
        name_field = MinimalFieldGroup("Nome", self.name_edit)
        
        # Campo Login (somente leitura)
        self.login_edit = MinimalLineEdit(f"@{self.usuario['login']}")
        self.login_edit.setReadOnly(True)
        login_field = MinimalFieldGroup("Nome de usuário", self.login_edit)
        
        # Campo Email
        self.email_edit = MinimalLineEdit(self.usuario.get('email', ''))
        self.email_edit.setPlaceholderText("seu.email@exemplo.com")
        
        # Validação do email
        email_regex = QRegExp(r"[^@]+@[^@]+\.[a-zA-Z]{2,}")
        email_validator = QRegExpValidator(email_regex)
        self.email_edit.setValidator(email_validator)
        email_field = MinimalFieldGroup("E-mail", self.email_edit)
        
        layout.addWidget(name_field)
        layout.addWidget(login_field)
        layout.addWidget(email_field)
        
        return layout
        
    def create_buttons(self):
        layout = QVBoxLayout()
        layout.setSpacing(16)
        
        # Botão salvar (primário)
        self.save_button = MinimalButton("Salvar", "primary")
        self.save_button.clicked.connect(self.save_profile)
        
        # Layout horizontal para botões secundários
        secondary_layout = QHBoxLayout()
        secondary_layout.setSpacing(16)
        
        # Botão alterar senha
        self.change_password_button = MinimalButton("Alterar Senha", "secondary")
        self.change_password_button.clicked.connect(self.open_change_password)
        
        # Botão cancelar
        self.cancel_button = MinimalButton("Cancelar", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        
        secondary_layout.addWidget(self.change_password_button)
        secondary_layout.addWidget(self.cancel_button)
        
        layout.addWidget(self.save_button)
        layout.addLayout(secondary_layout)
        
        return layout
        
    def save_profile(self):
        """Salvar alterações no perfil"""
        nome = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        
        # Validações
        if not nome:
            self.show_message("Campo obrigatório", "O nome não pode ficar em branco.", QMessageBox.Warning)
            return
        
        if email and not self.email_edit.hasAcceptableInput():
            self.show_message("Email inválido", "Por favor, insira um email válido.", QMessageBox.Warning)
            return
        
        try:
            # Atualizar no banco de dados
            self.db.cursor.execute('''
            UPDATE usuarios SET nome = ?, email = ? WHERE id = ?
            ''', (nome, email, self.usuario['id']))
            
            self.db.conn.commit()
            
            # Atualizar dados do usuário na memória
            self.usuario['nome'] = nome
            self.usuario['email'] = email
            
            self.show_message("Sucesso", "Suas informações foram atualizadas com sucesso.")
            self.accept()
        except Exception as e:
            self.show_message("Erro", f"Erro ao atualizar perfil: {str(e)}", QMessageBox.Critical)
    
    def open_change_password(self):
        """Abrir diálogo para alterar senha"""
        from ui.change_password_window import ChangePasswordWindow
        password_dialog = ChangePasswordWindow(self.db, self.usuario['id'])
        password_dialog.exec_()
    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """Exibir mensagem minimalista"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #1d1d1f;
                border: 1px solid #e8e8ed;
                border-radius: 16px;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
            QMessageBox QPushButton {
                background-color: #1d1d1f;
                color: white;
                border: none;
                border-radius: 12px;
                padding: 12px 24px;
                min-width: 80px;
                font-weight: 500;
                font-size: 14px;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
            QMessageBox QPushButton:hover {
                background-color: #2c2c2e;
            }
        """)
        msg_box.exec_()