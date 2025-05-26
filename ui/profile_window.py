from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QWidget, 
                             QSizePolicy, QSpacerItem, QScrollArea)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QRegExpValidator, QLinearGradient
from PyQt5.QtCore import Qt, QRegExp

class ModernLineEdit(QLineEdit):
    """Campo de texto moderno estilo Apple"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_style()
        
    def setup_style(self):
        self.setFixedHeight(48)
        self.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                border: none;
                border-radius: 12px;
                background-color: #f5f5f7;
                color: #1d1d1f;
                font-size: 16px;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                selection-background-color: #06c;
            }
            QLineEdit:focus {
                background-color: #ebebeb;
                outline: none;
            }
            QLineEdit:read-only {
                background-color: #f0f0f0;
                color: #86868b;
            }
        """)

class FieldGroup(QWidget):
    """Grupo de campo com label estilo Apple"""
    
    def __init__(self, label_text, input_widget):
        super().__init__()
        self.setup_ui(label_text, input_widget)
        
    def setup_ui(self, label_text, input_widget):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                color: #86868b;
                font-size: 14px;
                font-weight: 500;
                padding-left: 4px;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
        """)
        
        layout.addWidget(label)
        layout.addWidget(input_widget)

class ModernButton(QPushButton):
    """Botão moderno estilo Apple"""
    
    def __init__(self, text, button_type="primary"):
        super().__init__(text)
        self.button_type = button_type
        self.setup_style()
        
    def setup_style(self):
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        
        if self.button_type == "primary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #007AFF;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: 600;
                    font-size: 16px;
                    font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004494;
                }
                QPushButton:disabled {
                    background-color: #c7c7cc;
                    color: #ffffff;
                }
            """)
        elif self.button_type == "secondary":
            self.setStyleSheet("""
                QPushButton {
                    background-color: #f2f2f7;
                    color: #007AFF;
                    border: none;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 16px;
                    font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                }
                QPushButton:hover {
                    background-color: #e5e5ea;
                }
                QPushButton:pressed {
                    background-color: #d1d1d6;
                }
            """)
        elif self.button_type == "close":
            self.setFixedSize(32, 32)
            self.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #8e8e93;
                    border: none;
                    border-radius: 16px;
                    font-size: 18px;
                    font-weight: 400;
                    font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
                }
                QPushButton:hover {
                    background-color: #f2f2f7;
                    color: #1d1d1f;
                }
            """)

class ProfileCard(QWidget):
    """Card do perfil do usuário"""
    
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setup_ui()
        
    def setup_ui(self):
        self.setFixedHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Avatar
        avatar_container = self.create_avatar()
        
        # Informações do usuário
        info_container = self.create_user_info()
        
        layout.addWidget(avatar_container)
        layout.addWidget(info_container, 1)
        
    def create_avatar(self):
        avatar_container = QWidget()
        avatar_container.setFixedSize(64, 64)
        
        # Círculo do avatar
        avatar_circle = QWidget(avatar_container)
        avatar_circle.setFixedSize(64, 64)
        avatar_circle.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                      stop:0 #007AFF, stop:1 #0056b3);
            border-radius: 32px;
        """)
        
        # Iniciais
        iniciais = "".join([nome[0].upper() for nome in self.usuario['nome'].split()[:2]])
        iniciais_label = QLabel(iniciais, avatar_circle)
        iniciais_label.setFont(QFont("SF Pro Display", 20, QFont.Bold))
        iniciais_label.setStyleSheet("""
            color: white;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        iniciais_label.setAlignment(Qt.AlignCenter)
        iniciais_label.resize(avatar_circle.size())
        
        return avatar_container
        
    def create_user_info(self):
        info_container = QWidget()
        layout = QVBoxLayout(info_container)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(4)
        
        # Nome
        nome_label = QLabel(self.usuario['nome'])
        nome_label.setStyleSheet("""
            font-size: 20px;
            font-weight: 600;
            color: #1d1d1f;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        
        # Tipo de usuário
        tipo_label = QLabel(f"{self.usuario['tipo'].capitalize()} • @{self.usuario['login']}")
        tipo_label.setStyleSheet("""
            font-size: 14px;
            color: #8e8e93;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        
        layout.addWidget(nome_label)
        layout.addWidget(tipo_label)
        layout.addStretch()
        
        return info_container

class ProfileWindow(QDialog):
    """Janela de perfil com design limpo e moderno"""
    
    def __init__(self, db, usuario):
        super().__init__()
        self.db = db
        self.usuario = usuario
        self.setup_window()
        self.setup_ui()
        
    def setup_window(self):
        self.setWindowTitle("Perfil")
        self.setFixedSize(480, 720)
        self.setModal(True)
        
        # Estilo da janela
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 16px;
            }
            QLabel {
                color: #1d1d1f;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
        """)
        
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header com botão de fechar
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Scroll area para o conteúdo
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #c7c7cc;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #aeaeb2;
            }
        """)
        
        # Conteúdo principal
        content_widget = self.create_content()
        scroll_area.setWidget(content_widget)
        
        main_layout.addWidget(scroll_area)
        
    def create_header(self):
        header_widget = QWidget()
        header_widget.setFixedHeight(60)
        header_widget.setStyleSheet("background-color: #ffffff; border-bottom: 1px solid #f2f2f7;")
        
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(20, 14, 20, 14)
        
        # Título do header
        title_label = QLabel("Meu Perfil")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: 600;
            color: #1d1d1f;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        
        # Botão de fechar
        close_button = ModernButton("✕", "close")
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        
        return header_widget
        
    def create_content(self):
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(24, 32, 24, 32)
        layout.setSpacing(0)
        
        # Subtítulo
        subtitle_label = QLabel("Gerencie suas informações pessoais")
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: #8e8e93;
            font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
        """)
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)
        
        # Espaçamento
        layout.addItem(QSpacerItem(20, 32, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Card do perfil
        profile_card = ProfileCard(self.usuario)
        layout.addWidget(profile_card)
        
        # Espaçamento
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Formulário
        form_layout = self.create_form()
        layout.addLayout(form_layout)
        
        # Espaçamento
        layout.addItem(QSpacerItem(20, 32, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        # Botões
        buttons_layout = self.create_buttons()
        layout.addLayout(buttons_layout)
        
        # Espaçamento final
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        
        return content_widget
        
    def create_form(self):
        layout = QVBoxLayout()
        layout.setSpacing(24)
        
        # Campo Nome
        self.name_edit = ModernLineEdit(self.usuario['nome'])
        self.name_edit.setPlaceholderText("Digite seu nome completo")
        name_field = FieldGroup("Nome", self.name_edit)
        
        # Campo Login (somente leitura)
        self.login_edit = ModernLineEdit(self.usuario['login'])
        self.login_edit.setReadOnly(True)
        login_field = FieldGroup("Nome de usuário", self.login_edit)
        
        # Campo Email
        self.email_edit = ModernLineEdit(self.usuario.get('email', ''))
        self.email_edit.setPlaceholderText("seu.email@exemplo.com")
        
        # Validação do email
        email_regex = QRegExp(r"[^@]+@[^@]+\.[a-zA-Z]{2,}")
        email_validator = QRegExpValidator(email_regex)
        self.email_edit.setValidator(email_validator)
        email_field = FieldGroup("E-mail", self.email_edit)
        
        layout.addWidget(name_field)
        layout.addWidget(login_field)
        layout.addWidget(email_field)
        
        return layout
        
    def create_buttons(self):
        layout = QVBoxLayout()
        layout.setSpacing(12)
        
        # Botão salvar (primário)
        self.save_button = ModernButton("Salvar Alterações", "primary")
        self.save_button.clicked.connect(self.save_profile)
        
        # Botão alterar senha (secundário)
        self.change_password_button = ModernButton("Alterar Senha", "secondary")
        self.change_password_button.clicked.connect(self.open_change_password)
        
        # Botão cancelar (secundário)
        self.cancel_button = ModernButton("Cancelar", "secondary")
        self.cancel_button.clicked.connect(self.reject)
        
        layout.addWidget(self.save_button)
        layout.addWidget(self.change_password_button)
        layout.addWidget(self.cancel_button)
        
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
        """Exibir mensagem personalizada"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #ffffff;
                color: #1d1d1f;
                border-radius: 12px;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
            QMessageBox QPushButton {
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 80px;
                font-weight: 500;
                font-size: 14px;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
            QMessageBox QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        msg_box.exec_()