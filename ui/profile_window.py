from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout,
                             QGroupBox, QFrame)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QPixmap, QRegExpValidator, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QRegExp

class ProfileWindow(QDialog):
    def __init__(self, db, usuario):
        super().__init__()
        self.db = db
        self.usuario = usuario
        self.setWindowTitle("Meu Perfil")
        self.setFixedSize(500, 450)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Cabeçalho
        header_layout = QHBoxLayout()
        
        # Avatar (placeholder)
        avatar_frame = QFrame()
        avatar_frame.setFixedSize(80, 80)
        avatar_frame.setStyleSheet("""
            background-color: #3498db;
            border-radius: 40px;
            border: 2px solid #2980b9;
        """)
        
        avatar_layout = QVBoxLayout(avatar_frame)
        avatar_layout.setAlignment(Qt.AlignCenter)
        
        # Iniciais do usuário
        iniciais = "".join([nome[0].upper() for nome in self.usuario['nome'].split()[:2]])
        iniciais_label = QLabel(iniciais)
        iniciais_label.setFont(QFont("Arial", 24, QFont.Bold))
        iniciais_label.setStyleSheet("color: white;")
        avatar_layout.addWidget(iniciais_label)
        
        # Informações do usuário
        info_layout = QVBoxLayout()
        
        nome_label = QLabel(self.usuario['nome'])
        nome_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        nome_label.setStyleSheet("color: #2c3e50;")
        
        tipo_label = QLabel(f"Perfil: {self.usuario['tipo'].capitalize()}")
        tipo_label.setFont(QFont("Segoe UI", 12))
        tipo_label.setStyleSheet("color: #7f8c8d;")
        
        info_layout.addWidget(nome_label)
        info_layout.addWidget(tipo_label)
        
        header_layout.addWidget(avatar_frame)
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #ecf0f1;")
        main_layout.addWidget(separator)
        
        # Formulário de informações pessoais
        profile_group = QGroupBox("Informações Pessoais")
        profile_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #dcdde1;
                border-radius: 5px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
            }
        """)
        
        profile_layout = QFormLayout(profile_group)
        profile_layout.setSpacing(10)
        profile_layout.setContentsMargins(20, 20, 20, 20)
        
        # Estilo para os campos
        input_style = """
            QLineEdit {
                padding: 8px;
                border: 1px solid #dcdde1;
                border-radius: 4px;
                background-color: #f5f6fa;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                background-color: white;
            }
        """
        
        # Campos de perfil
        self.name_edit = QLineEdit(self.usuario['nome'])
        self.name_edit.setStyleSheet(input_style)
        
        self.login_edit = QLineEdit(self.usuario['login'])
        self.login_edit.setReadOnly(True)  # Nome de usuário não pode ser alterado
        self.login_edit.setStyleSheet(input_style + "background-color: #ecf0f1;")
        
        self.email_edit = QLineEdit(self.usuario['email'] if self.usuario['email'] else "")
        self.email_edit.setStyleSheet(input_style)
        
        # Email regex validation
        email_regex = QRegExp(r"[^@]+@[^@]+\.[a-zA-Z]{2,}")
        email_validator = QRegExpValidator(email_regex)
        self.email_edit.setValidator(email_validator)
        
        # Adicionar campos ao formulário
        profile_layout.addRow("Nome completo:", self.name_edit)
        profile_layout.addRow("Nome de usuário:", self.login_edit)
        profile_layout.addRow("E-mail:", self.email_edit)
        
        main_layout.addWidget(profile_group)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar Alterações")
        self.save_button.setFixedHeight(40)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        
        self.change_password_button = QPushButton("Alterar Senha")
        self.change_password_button.setFixedHeight(40)
        self.change_password_button.setCursor(Qt.PointingHandCursor)
        self.change_password_button.setStyleSheet("""
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
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #707b7c;
            }
        """)
        
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.change_password_button)
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Conectar sinais
        self.save_button.clicked.connect(self.save_profile)
        self.change_password_button.clicked.connect(self.open_change_password)
        self.cancel_button.clicked.connect(self.reject)
    
    def save_profile(self):
        """Salvar alterações no perfil"""
        nome = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        
        # Validações
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "O nome não pode ficar em branco.")
            return
        
        if email and not self.email_edit.hasAcceptableInput():
            QMessageBox.warning(self, "Email inválido", "Por favor, insira um email válido.")
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
            
            QMessageBox.information(self, "Perfil atualizado", "Suas informações foram atualizadas com sucesso.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar perfil: {str(e)}")
    
    def open_change_password(self):
        """Abrir diálogo para alterar senha"""
        from ui.change_password_window import ChangePasswordWindow
        password_dialog = ChangePasswordWindow(self.db, self.usuario['id'])
        password_dialog.exec_()
    
    def paintEvent(self, event):
        """Personaliza o fundo da janela com um gradiente suave"""
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#f5f6fa"))
        gradient.setColorAt(1, QColor("#dfe6e9"))
        painter.fillRect(self.rect(), QBrush(gradient))