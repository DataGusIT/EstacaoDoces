from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QFrame, QMessageBox,
                             QFormLayout, QGroupBox, QComboBox, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPainter, QColor, QBrush, QRegExpValidator, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QRegExp

class RegisterWindow(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setWindowTitle("Novo Cadastro - Sistema de Estoque")
        self.setFixedSize(450, 550)
        self.setWindowFlags(Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_label = QLabel("Criar Nova Conta")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        subtitle = QLabel("Preencha os dados abaixo para criar sua conta")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #7f8c8d; font-size: 14px;")
        main_layout.addWidget(subtitle)
        
        # Linha separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ecf0f1;")
        main_layout.addWidget(separator)
        
        # Formulário de cadastro
        register_group = QGroupBox("Informações da Conta")
        register_group.setStyleSheet("""
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
        
        register_layout = QFormLayout(register_group)
        register_layout.setSpacing(10)
        register_layout.setContentsMargins(20, 20, 20, 20)
        
        # Campos de cadastro
        input_style = """
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
        """
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Seu nome completo")
        self.name_edit.setStyleSheet(input_style)
        
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nome para login")
        self.username_edit.setStyleSheet(input_style)
        # Aceitar apenas letras, números e underscores
        regex = QRegExp("[a-zA-Z0-9_]+")
        self.username_edit.setValidator(QRegExpValidator(regex))
        
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("seu.email@exemplo.com")
        self.email_edit.setStyleSheet(input_style)
        
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Mínimo 6 caracteres")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet(input_style)
        
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setPlaceholderText("Confirme sua senha")
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit.setStyleSheet(input_style)
        
        self.user_type = QComboBox()
        self.user_type.addItems(["Comum", "Administrador"])
        self.user_type.setStyleSheet(input_style)
        
        # Adicionar campos ao layout
        register_layout.addRow("Nome completo:", self.name_edit)
        register_layout.addRow("Nome de usuário:", self.username_edit)
        register_layout.addRow("E-mail:", self.email_edit)
        register_layout.addRow("Senha:", self.password_edit)
        register_layout.addRow("Confirmar senha:", self.confirm_password_edit)
        register_layout.addRow("Tipo de usuário:", self.user_type)
        
        main_layout.addWidget(register_group)
        
        # Informação sobre senha
        password_info = QLabel("A senha deve ter pelo menos 6 caracteres, incluindo letras e números.")
        password_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        password_info.setWordWrap(True)
        main_layout.addWidget(password_info)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.register_button = QPushButton("Cadastrar")
        self.register_button.setFixedHeight(40)
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219653;
            }
        """)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        
        buttons_layout.addWidget(self.register_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Adicionar espaçador
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)
        
        # Conectar sinais
        self.register_button.clicked.connect(self.handle_register)
        self.cancel_button.clicked.connect(self.reject)
    
    def handle_register(self):
        # Validar formulário
        nome = self.name_edit.text().strip()
        login = self.username_edit.text().strip()
        email = self.email_edit.text().strip()
        senha = self.password_edit.text()
        confirmar_senha = self.confirm_password_edit.text()
        tipo = "admin" if self.user_type.currentText() == "Administrador" else "comum"
        
        # Validações básicas
        if not nome or not login or not email or not senha:
            QMessageBox.warning(self, "Campos vazios", "Por favor, preencha todos os campos obrigatórios.")
            return
        
        if len(senha) < 6:
            QMessageBox.warning(self, "Senha inválida", "A senha deve ter pelo menos 6 caracteres.")
            return
        
        if senha != confirmar_senha:
            QMessageBox.warning(self, "Senha diferente", "As senhas não coincidem.")
            return
        
        # Validar email com regex básico
        email_regex = QRegExp(r"[^@]+@[^@]+\.[a-zA-Z]{2,}")
        if not email_regex.exactMatch(email):
            QMessageBox.warning(self, "Email inválido", "Por favor, insira um email válido.")
            return
        
        # Tentar cadastrar no banco de dados
        success, result = self.db.cadastrar_usuario(nome, login, senha, email, tipo)
        
        if success:
            QMessageBox.information(self, "Cadastro realizado", 
                                   f"Usuário {nome} cadastrado com sucesso!\nFaça login para acessar o sistema.")
            self.accept()
        else:
            QMessageBox.critical(self, "Erro no cadastro", f"Não foi possível completar o cadastro: {result}")
    
    def paintEvent(self, event):
        """Personaliza o fundo da janela com um gradiente suave"""
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#f5f6fa"))
        gradient.setColorAt(1, QColor("#dfe6e9"))
        painter.fillRect(self.rect(), QBrush(gradient))