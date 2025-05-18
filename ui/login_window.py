from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QCheckBox, QFormLayout, QFrame,
                             QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont

class LoginWindow(QDialog):
    # Definir sinal para login bem-sucedido
    login_success_signal = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        
        self.db = db_manager
        self.usuario = None
        self.offset = None
        self.init_ui()
    
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
                background-color: #06c;
                color: white;
                min-height: 44px;
            }
            QPushButton#loginButton:hover {
                background-color: #005bb5;
            }
            QPushButton#loginButton:pressed {
                background-color: #004c99;
            }
            QPushButton#loginButton:disabled {
                background-color: #ccc;
                color: #f5f5f7;
            }
            QPushButton#closeButton {
                background-color: transparent;
                color: #86868b;
                border: none;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton#closeButton:hover {
                color: #1d1d1f;
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
        
        # Botão de fechar
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        
        # Área do logo centralizada
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(12)
        logo_layout.setContentsMargins(0, 20, 0, 30)  # Espaçamento superior e inferior
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            # Redimensionar para tamanho adequado
            logo_pixmap = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
        
        # Campo de usuário
        user_label = QLabel("USUÁRIO")
        user_label.setObjectName("fieldLabel")
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Digite seu usuário")
        self.login_edit.setMinimumHeight(44)
        self.login_edit.textChanged.connect(self.validate_inputs)
        
        # Campo de senha
        senha_label = QLabel("SENHA")
        senha_label.setObjectName("fieldLabel")
        self.senha_edit = QLineEdit()
        self.senha_edit.setPlaceholderText("Digite sua senha")
        self.senha_edit.setEchoMode(QLineEdit.Password)
        self.senha_edit.setMinimumHeight(44)
        self.senha_edit.textChanged.connect(self.validate_inputs)
        
        # Lembrar senha com layout específico
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Lembrar usuário")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        # Adicionar campos ao formulário
        user_field_layout = QVBoxLayout()
        user_field_layout.setSpacing(5)
        user_field_layout.addWidget(user_label)
        user_field_layout.addWidget(self.login_edit)
        
        senha_field_layout = QVBoxLayout()
        senha_field_layout.setSpacing(5)
        senha_field_layout.addWidget(senha_label)
        senha_field_layout.addWidget(self.senha_edit)
        
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
            
            # Emitir sinal de login bem-sucedido
            self.login_success_signal.emit(usuario)
            
            # Aceitar o diálogo (fecha com status de sucesso)
            self.accept()
        else:
            # Login falhou
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