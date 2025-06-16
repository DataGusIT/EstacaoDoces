from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QCheckBox, QFormLayout, QFrame,
                             QGraphicsDropShadowEffect, QSizePolicy, QToolButton)
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QSettings
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont
import base64

class LoginWindow(QDialog):
    # Definir sinal para login bem-sucedido
    login_success_signal = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        
        self.db = db_manager
        self.usuario = None
        self.offset = None
        
        # Configurações para salvar dados do usuário
        self.settings = QSettings("SuaEmpresa", "SeuERP")
        
        self.init_ui()
        self.load_saved_credentials()
    
    def init_ui(self):
        """Inicializa a interface de usuário"""
        self.setWindowTitle("Login")
        self.setMinimumWidth(420)
        self.setMinimumHeight(480)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        
        # Aplicar estilo minimalista inspirado na Apple
        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                color: #1d1d1f;
                border-radius: 12px;
            }
            QLabel {
                color: #1d1d1f;
                font-family: -apple-system, system-ui, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue";
            }
            QLineEdit {
                padding: 14px;
                border: none;
                border-radius: 8px;
                background-color: #f5f5f7;
                color: #1d1d1f;
                font-size: 14px;
                selection-background-color: #06c;
            }
            QLineEdit:focus {
                background-color: #ebebeb;
            }
            QPushButton {
                padding: 14px;
                border-radius: 10px;
                font-weight: medium;
                font-size: 14px;
            }
            QPushButton#loginButton {
                background-color: #1d1d1f;
                color: white;
                min-height: 44px;
            }
            QPushButton#loginButton:hover {
                background-color: #333333;
            }
            QPushButton#loginButton:pressed {
                background-color: #000000;
            }
            QPushButton#loginButton:disabled {
                background-color: #ccc;
                color: #f5f5f7;
            }
            QToolButton#closeButton {
                background-color: transparent;
                border: none;
                border-radius: 15px;
                padding: 5px;
            }
            QToolButton#closeButton:hover {
                background-color: #f0f0f0;
            }
            QToolButton#closeButton:pressed {
                background-color: #e0e0e0;
            }
            QCheckBox {
                color: #86868b;
                font-size: 13px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 1px solid #d2d2d7;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #06c;
                border: 1px solid #06c;
                image: url('assets/check.png');
            }
            #loginContainer {
                background-color: #ffffff;
                border-radius: 12px;
            }
            #titleLabel {
                font-size: 28px;
                font-weight: 500;
                color: #1d1d1f;
            }
            #subtitleLabel {
                font-size: 16px;
                color: #86868b;
                margin-bottom: 15px;
            }
            #fieldLabel {
                color: #86868b;
                font-size: 13px;
                font-weight: 500;
                padding-left: 2px;
                margin-bottom: 6px;
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Container superior para botão fechar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 10)
        
        # Botão de fechar com ícone personalizado
        close_button = QToolButton()
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)
        
        # Carregar e configurar o ícone
        close_icon = QPixmap("assets/icons/marca-x.png")
        if not close_icon.isNull():
            # Redimensionar o ícone para tamanho adequado
            close_icon = close_icon.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            close_button.setIcon(QIcon(close_icon))
            close_button.setIconSize(QSize(16, 16))
        else:
            # Fallback para texto se o ícone não for encontrado
            close_button.setText("×")
            close_button.setStyleSheet("""
                QToolButton#closeButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 15px;
                    padding: 5px;
                    color: #86868b;
                    font-size: 16px;
                    font-weight: bold;
                }
                QToolButton#closeButton:hover {
                    background-color: #f0f0f0;
                    color: #1d1d1f;
                }
                QToolButton#closeButton:pressed {
                    background-color: #e0e0e0;
                }
            """)
        
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        
        # Área do logo centralizada
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(12)
        logo_layout.setContentsMargins(0, 20, 0, 30)  # Espaçamento superior e inferior
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/img/GestorX.png")
        if not logo_pixmap.isNull():
            # Redimensionar para tamanho adequado
            logo_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            # Texto alternativo se não tiver logo
            logo_label.setText("ERP")
            logo_label.setStyleSheet("font-size: 32px; font-weight: 500; color: #06c; margin-bottom: 20px;")
            logo_label.setAlignment(Qt.AlignCenter)
        
        # Adicionar título e subtítulo
        title_label = QLabel("Bem-vindo")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Acesse sua conta")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Adicionar ao layout do logo
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        
        # Form de login com layout personalizado
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        form_layout.setContentsMargins(0, 0, 0, 30)
        
        # Campo de usuário com ícone
        user_icon = QPixmap("assets/icons/usuario.png")
        if not user_icon.isNull():
            user_icon = user_icon.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Criar um layout horizontal para ícone + texto
            user_label_layout = QHBoxLayout()
            user_label_layout.setContentsMargins(0, 0, 0, 0)
            user_label_layout.setSpacing(5)
            
            icon_label = QLabel()
            icon_label.setPixmap(user_icon)
            text_label = QLabel("USUÁRIO")
            text_label.setStyleSheet("color: #86868b; font-size: 13px; font-weight: 500;")
            
            user_label_layout.addWidget(icon_label)
            user_label_layout.addWidget(text_label)
            user_label_layout.addStretch()
            
            user_label_widget = QFrame()
            user_label_widget.setLayout(user_label_layout)
        else:
            user_label_widget = QLabel("USUÁRIO")
            user_label_widget.setObjectName("fieldLabel")

        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Digite seu usuário")
        self.login_edit.setMinimumHeight(44)
        self.login_edit.textChanged.connect(self.validate_inputs)

        # Campo de senha com ícone
        senha_icon = QPixmap("assets/icons/cadeado.png")
        if not senha_icon.isNull():
            senha_icon = senha_icon.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # Criar um layout horizontal para ícone + texto
            senha_label_layout = QHBoxLayout()
            senha_label_layout.setContentsMargins(0, 0, 0, 0)
            senha_label_layout.setSpacing(5)
            
            icon_label = QLabel()
            icon_label.setPixmap(senha_icon)
            text_label = QLabel("SENHA")
            text_label.setStyleSheet("color: #86868b; font-size: 13px; font-weight: 500;")
            
            senha_label_layout.addWidget(icon_label)
            senha_label_layout.addWidget(text_label)
            senha_label_layout.addStretch()
            
            senha_label_widget = QFrame()
            senha_label_widget.setLayout(senha_label_layout)
        else:
            senha_label_widget = QLabel("SENHA")
            senha_label_widget.setObjectName("fieldLabel")

        # Container da senha com botão toggle
        senha_input_container = QHBoxLayout()
        senha_input_container.setContentsMargins(0, 0, 0, 0)
        senha_input_container.setSpacing(0)

        self.senha_edit = QLineEdit()
        self.senha_edit.setPlaceholderText("Digite sua senha")
        self.senha_edit.setEchoMode(QLineEdit.Password)
        self.senha_edit.setMinimumHeight(44)
        self.senha_edit.textChanged.connect(self.validate_inputs)

        # Botão toggle para mostrar/ocultar senha
        self.toggle_password_button = QToolButton()
        self.toggle_password_button.setFixedSize(44, 44)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        self.password_visible = False
        self.update_password_toggle_icon()

        # Estilo do botão toggle
        self.toggle_password_button.setStyleSheet("""
            QToolButton {
                border: none;
                background-color: #f5f5f7;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 8px;
            }
            QToolButton:hover {
                background-color: #ebebeb;
            }
        """)

        # Ajustar o QLineEdit para não ter borda direita
        self.senha_edit.setStyleSheet("""
            QLineEdit {
                padding: 14px;
                border: none;
                border-top-left-radius: 8px;
                border-bottom-left-radius: 8px;
                background-color: #f5f5f7;
                color: #1d1d1f;
                font-size: 14px;
                selection-background-color: #06c;
            }
            QLineEdit:focus {
                background-color: #ebebeb;
            }
        """)

        senha_input_container.addWidget(self.senha_edit)
        senha_input_container.addWidget(self.toggle_password_button)

        # Widget container para o layout
        senha_input_widget = QFrame()
        senha_input_widget.setLayout(senha_input_container)
        senha_input_widget.setStyleSheet("QFrame { border-radius: 8px; }")
        
        # Lembrar senha com layout específico
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Lembrar usuário")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        # Adicionar campos ao formulário
        user_field_layout = QVBoxLayout()
        user_field_layout.setSpacing(5)
        user_field_layout.addWidget(user_label_widget)
        user_field_layout.addWidget(self.login_edit)
        
        senha_field_layout = QVBoxLayout()
        senha_field_layout.setSpacing(5)
        senha_field_layout.addWidget(senha_label_widget)
        senha_field_layout.addWidget(senha_input_widget)

        form_layout.addLayout(user_field_layout)
        form_layout.addLayout(senha_field_layout)
        form_layout.addLayout(remember_layout)
        
        # Botão de login
        button_layout = QVBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_button = QPushButton("ENTRAR")
        self.login_button.setObjectName("loginButton")
        self.login_button.setEnabled(False)  # Inicialmente desabilitado
        self.login_button.clicked.connect(self.try_login)
        
        button_layout.addWidget(self.login_button)
        
        # Rodapé
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 20, 0, 5)
        
        version_label = QLabel("Versão 1.0.0")
        version_label.setStyleSheet("color: #86868b; font-size: 12px;")
        version_label.setAlignment(Qt.AlignCenter)
        
        footer_layout.addStretch()
        footer_layout.addWidget(version_label)
        footer_layout.addStretch()
        
        # Montar layout principal
        main_layout.addLayout(header_layout)
        main_layout.addLayout(logo_layout)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addLayout(footer_layout)
        
        self.setLayout(main_layout)
        
        # Focar no campo de login
        self.login_edit.setFocus()
    
    def load_saved_credentials(self):
        """Carrega as credenciais salvas se existirem"""
        # Verifica se há credenciais salvas
        if self.settings.value("remember_user", False, type=bool):
            saved_username = self.settings.value("username", "")
            saved_password = self.settings.value("password", "")
            
            if saved_username and saved_password:
                # Decodifica a senha (simples codificação base64)
                try:
                    decoded_password = base64.b64decode(saved_password.encode()).decode()
                    
                    # Preenche os campos
                    self.login_edit.setText(saved_username)
                    self.senha_edit.setText(decoded_password)
                    self.remember_checkbox.setChecked(True)
                    
                    # Atualiza o estado do botão
                    self.validate_inputs()
                    
                    # Se há credenciais salvas, foca no botão de login
                    self.login_button.setFocus()
                    
                except Exception as e:
                    # Se houver erro na decodificação, limpa as credenciais salvas
                    self.clear_saved_credentials()
    
    def save_credentials(self, username, password):
        """Salva as credenciais do usuário"""
        if self.remember_checkbox.isChecked():
            # Codifica a senha (simples codificação base64)
            encoded_password = base64.b64encode(password.encode()).decode()
            
            self.settings.setValue("remember_user", True)
            self.settings.setValue("username", username)
            self.settings.setValue("password", encoded_password)
        else:
            self.clear_saved_credentials()
    
    def clear_saved_credentials(self):
        """Remove as credenciais salvas"""
        self.settings.setValue("remember_user", False)
        self.settings.remove("username")
        self.settings.remove("password")
    
    # Implementar função para permitir arrastar a janela
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)
    
    def validate_inputs(self):
        """Valida os campos de entrada para habilitar o botão de login"""
        login = self.login_edit.text().strip()
        senha = self.senha_edit.text().strip()
        
        self.login_button.setEnabled(bool(login and senha))
    
    def try_login(self):
        """Tenta fazer login com as credenciais fornecidas"""
        login = self.login_edit.text().strip()
        senha = self.senha_edit.text().strip()
        
        usuario = self.db.autenticar_usuario(login, senha)
        
        if usuario:
            # Login bem-sucedido
            self.usuario = usuario
            
            # Salvar credenciais se solicitado
            self.save_credentials(login, senha)
            
            # Emitir sinal de login bem-sucedido
            self.login_success_signal.emit(usuario)
            
            # Aceitar o diálogo (fecha com status de sucesso)
            self.accept()
        else:
            # Login falhou - limpar credenciais salvas se houver
            if self.settings.value("remember_user", False, type=bool):
                self.clear_saved_credentials()
                self.remember_checkbox.setChecked(False)
            
            error_dialog = QMessageBox(self)
            error_dialog.setWindowTitle("Não foi possível entrar")
            error_dialog.setText("Usuário ou senha incorretos.")
            error_dialog.setInformativeText("Por favor, verifique suas informações e tente novamente.")
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                    color: #1d1d1f;
                }
                QPushButton {
                    background-color: #06c;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: medium;
                }
                QPushButton:hover {
                    background-color: #005bb5;
                }
            """)
            error_dialog.exec_()

    def update_password_toggle_icon(self):
        """Atualiza o ícone do botão toggle de senha"""
        if self.password_visible:
            icon_path = "assets/icons/olho_fechado.png"
        else:
            icon_path = "assets/icons/olho.png"
        
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon = QIcon(pixmap)
            self.toggle_password_button.setIcon(icon)
            self.toggle_password_button.setIconSize(QSize(20, 20))

    def toggle_password_visibility(self):
        """Alterna a visibilidade da senha"""
        self.password_visible = not self.password_visible
        
        if self.password_visible:
            self.senha_edit.setEchoMode(QLineEdit.Normal)
        else:
            self.senha_edit.setEchoMode(QLineEdit.Password)
        
        self.update_password_toggle_icon()