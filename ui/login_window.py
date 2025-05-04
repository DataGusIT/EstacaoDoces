from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QFormLayout, QGroupBox, QCheckBox, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QColor, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QSize, pyqtSignal


class LoginWindow(QDialog):
    loginSuccess = pyqtSignal(dict)  # Sinal para informar login bem-sucedido
    
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Login - Sistema de Estoque")
        self.setFixedSize(400, 450)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setup_ui()
        
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo/título
        title_layout = QHBoxLayout()
        logo_label = QLabel()
        # Substitua pelo caminho real da sua logo
        # logo_pixmap = QPixmap("assets/icons/logo.png")
        # logo_label.setPixmap(logo_pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        title_label = QLabel("Sistema ERP")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        
        # title_layout.addWidget(logo_label)
        title_layout.addWidget(title_label)
        title_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(title_layout)
        
        subtitle = QLabel("Controle de Estoque e Vendas")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        main_layout.addWidget(subtitle)
        
        # Linha separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ecf0f1;")
        main_layout.addWidget(separator)
        
        # Formulário de login
        login_group = QGroupBox("Login")
        login_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #ecf0f1;
                border: 1px solid #555;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 15px;
                background-color: #2c3e50;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }
        """)

        login_layout = QFormLayout(login_group)
        login_layout.setSpacing(10)
        login_layout.setContentsMargins(20, 20, 20, 20)

        # Campos de login
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nome de usuário")
        self.username_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #555;
                border-radius: 4px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: #3d566e;
            }
        """)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Senha")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet(self.username_edit.styleSheet())

        # Adicionar campos ao layout
        login_layout.addRow("Usuário:", self.username_edit)
        login_layout.addRow("Senha:", self.password_edit)

        # Lembrar usuário
        self.remember_checkbox = QCheckBox("Lembrar usuário")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: #bdc3c7;
            }
            QCheckBox::indicator {
                width: 15px;
                height: 15px;
            }
        """)
        login_layout.addRow("", self.remember_checkbox)

        main_layout.addWidget(login_group)

        # Botões
        buttons_layout = QHBoxLayout()

        self.login_button = QPushButton("Entrar")
        self.login_button.setFixedHeight(40)
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #2471a3;
            }
        """)

        self.register_button = QPushButton("Cadastrar")
        self.register_button.setFixedHeight(40)
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)

        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.register_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Adicionar texto de rodapé
        footer = QLabel("© 2025 Sistema de Estoque")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #95a5a6; font-size: 12px;")
        main_layout.addWidget(footer)
        
        # Adicionar espaçador para empurrar widgets para cima
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)
        
        # Conectar sinais
        self.login_button.clicked.connect(self.handle_login)
        self.register_button.clicked.connect(self.open_register)
        self.password_edit.returnPressed.connect(self.handle_login)  # Permitir login com Enter
    
    def handle_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Campos vazios", "Por favor, preencha todos os campos.")
            return
        
        # Autenticar usuário
        usuario = self.db.autenticar_usuario(username, password)

        if usuario:
            self.loginSuccess.emit(usuario)  # Emitir sinal com os dados do usuário
            self.accept()  # Fechar diálogo com código de sucesso
        else:
            QMessageBox.critical(self, "Login falhou", "Usuário ou senha incorretos.")
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def open_register(self):
        # Abrir a janela de cadastro
        from ui.register_window import RegisterWindow
        register_dialog = RegisterWindow(self.db)
        register_dialog.exec_()
        
    def paintEvent(self, event):
        """Personaliza o fundo da janela com um gradiente suave"""
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#f5f6fa"))
        gradient.setColorAt(1, QColor("#dfe6e9"))
        painter.fillRect(self.rect(), QBrush(gradient))