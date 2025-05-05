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
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface de usuário"""
        self.setWindowTitle("Login - Sistema")
        self.setMinimumWidth(450)
        self.setMinimumHeight(500)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)  # Janela sem bordas para aparência moderna
        
        # Aplicar estilo dark moderno
        self.setStyleSheet("""
            QDialog {
                background-color: #121212;
                color: #f0f0f0;
                border-radius: 10px;
            }
            QLabel {
                color: #f0f0f0;
            }
            QLineEdit {
                padding: 12px;
                border: 1px solid #444;
                border-radius: 6px;
                background-color: #2c2c2c;
                color: #f0f0f0;
                font-size: 11pt;
                selection-background-color: #0d6efd;
            }
            QLineEdit:focus {
                border: 1px solid #0d6efd;
            }
            QPushButton {
                padding: 12px;
                border-radius: 6px;
                color: white;
                font-weight: bold;
                font-size: 11pt;
            }
            QPushButton#loginButton {
                background-color: #0d6efd;
                min-height: 40px;
            }
            QPushButton#loginButton:hover {
                background-color: #0b5ed7;
            }
            QPushButton#loginButton:pressed {
                background-color: #0a58ca;
            }
            QPushButton#cancelButton {
                background-color: transparent;
                border: 1px solid #e84118;
                color: #e84118;
                min-height: 40px;
            }
            QPushButton#cancelButton:hover {
                background-color: #e84118;
                color: white;
            }
            QCheckBox {
                color: #f0f0f0;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #444;
                background-color: #2c2c2c;
            }
            QCheckBox::indicator:checked {
                background-color: #0d6efd;
                border: 1px solid #0d6efd;
                image: url('assets/check.png'); /* Você precisará de uma imagem de check branco */
            }
            #loginContainer {
                background-color: #1e1e1e;
                border-radius: 10px;
            }
            #titleLabel {
                font-size: 20pt;
                font-weight: bold;
                color: #ffffff;
            }
            #subtitleLabel {
                font-size: 11pt;
                color: #888;
            }
            #closeButton {
                background-color: transparent;
                color: #888;
                border: none;
                font-size: 14pt;
                font-weight: bold;
            }
            #closeButton:hover {
                color: #e84118;
            }
            #fieldLabel {
                color: #888;
                font-size: 10pt;
                padding-left: 5px;
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container superior para título e botão fechar
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(15, 15, 15, 5)
        
        # Botão de fechar
        close_button = QPushButton("×")
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        
        # Área do logo centralizada
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(15)
        logo_layout.setContentsMargins(30, 40, 30, 20)
        
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/logo.png")
        if not logo_pixmap.isNull():
            # Redimensionar para tamanho adequado
            logo_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
        else:
            # Texto alternativo se não tiver logo
            logo_label.setText("SISTEMA ERP")
            logo_label.setStyleSheet("font-size: 24pt; font-weight: bold; color: #0d6efd; margin-bottom: 20px;")
            logo_label.setAlignment(Qt.AlignCenter)
        
        # Adicionar título e subtítulo
        title_label = QLabel("Bem-vindo(a)")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        
        subtitle_label = QLabel("Faça login para acessar o sistema")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        
        # Adicionar ao layout do logo
        logo_layout.addWidget(logo_label)
        logo_layout.addWidget(title_label)
        logo_layout.addWidget(subtitle_label)
        
        # Container principal para o formulário
        form_container = QFrame()
        form_container.setObjectName("loginContainer")
        form_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Adicionar sombra ao container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 0)
        form_container.setGraphicsEffect(shadow)
        
        # Layout do container
        container_layout = QVBoxLayout(form_container)
        container_layout.setContentsMargins(30, 30, 30, 30)
        container_layout.setSpacing(25)
        
        # Adicionar cabeçalho ao container
        container_layout.addLayout(logo_layout)
        
        # Form de login com layout personalizado
        form_layout = QVBoxLayout()
        form_layout.setSpacing(5)
        
        # Campo de usuário
        user_label = QLabel("USUÁRIO")
        user_label.setObjectName("fieldLabel")
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Digite seu usuário")
        self.login_edit.textChanged.connect(self.validate_inputs)
        
        # Campo de senha
        senha_label = QLabel("SENHA")
        senha_label.setObjectName("fieldLabel")
        self.senha_edit = QLineEdit()
        self.senha_edit.setPlaceholderText("Digite sua senha")
        self.senha_edit.setEchoMode(QLineEdit.Password)
        self.senha_edit.textChanged.connect(self.validate_inputs)
        
        # Lembrar senha com layout específico
        remember_layout = QHBoxLayout()
        self.remember_checkbox = QCheckBox("Lembrar usuário")
        remember_layout.addWidget(self.remember_checkbox)
        remember_layout.addStretch()
        
        # Adicionar campos ao formulário
        form_layout.addWidget(user_label)
        form_layout.addWidget(self.login_edit)
        form_layout.addSpacing(15)
        form_layout.addWidget(senha_label)
        form_layout.addWidget(self.senha_edit)
        form_layout.addSpacing(15)
        form_layout.addLayout(remember_layout)
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("CANCELAR")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        self.login_button = QPushButton("ENTRAR")
        self.login_button.setObjectName("loginButton")
        self.login_button.setEnabled(False)  # Inicialmente desabilitado
        self.login_button.clicked.connect(self.try_login)
        
        # Adicionar os botões com proporções adequadas
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.login_button)
        
        # Adicionar form e botões ao container
        container_layout.addLayout(form_layout)
        container_layout.addSpacing(10)
        container_layout.addLayout(buttons_layout)
        
        # Rodapé
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 15, 0, 15)
        
        version_label = QLabel("v1.0.0")
        version_label.setStyleSheet("color: #555; font-size: 9pt;")
        version_label.setAlignment(Qt.AlignCenter)
        
        footer_layout.addStretch()
        footer_layout.addWidget(version_label)
        footer_layout.addStretch()
        
        # Montar layout principal
        main_layout.addLayout(header_layout)
        main_layout.addWidget(form_container, 1)
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
            error_dialog.setWindowTitle("Erro de Login")
            error_dialog.setText("Usuário ou senha incorretos.")
            error_dialog.setInformativeText("Por favor, tente novamente.")
            error_dialog.setIcon(QMessageBox.Warning)
            error_dialog.setStyleSheet("""
                QMessageBox {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                }
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #0b5ed7;
                }
            """)
            error_dialog.exec_()