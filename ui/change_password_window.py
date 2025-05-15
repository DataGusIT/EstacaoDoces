from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QSize, QRegExp


class ChangePasswordWindow(QDialog):
    def __init__(self, db, usuario_id):
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.setWindowTitle("Alterar Senha")
        self.setFixedSize(400, 300)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_label = QLabel("Alterar Senha")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
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
        
        # Campos de senha
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Digite sua senha atual")
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setStyleSheet(input_style)
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Digite a nova senha")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet(input_style)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirme a nova senha")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet(input_style)
        
        # Adicionar campos ao formulário
        form_layout.addRow("Senha atual:", self.current_password)
        form_layout.addRow("Nova senha:", self.new_password)
        form_layout.addRow("Confirmar nova senha:", self.confirm_password)
        
        main_layout.addLayout(form_layout)
        
        # Informação sobre senha
        password_info = QLabel("A senha deve ter pelo menos 6 caracteres, incluindo letras e números.")
        password_info.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        password_info.setWordWrap(True)
        main_layout.addWidget(password_info)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Salvar")
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
        buttons_layout.addWidget(self.cancel_button)
        
        main_layout.addLayout(buttons_layout)
        
        # Conectar sinais
        self.save_button.clicked.connect(self.save_password)
        self.cancel_button.clicked.connect(self.reject)
    
    def save_password(self):
        """Salvar nova senha no banco de dados"""
        current = self.current_password.text()
        new_password = self.new_password.text()
        confirm = self.confirm_password.text()
        
        # Validações
        if not current or not new_password or not confirm:
            QMessageBox.warning(self, "Campos vazios", "Por favor, preencha todos os campos.")
            return
        
        if len(new_password) < 6:
            QMessageBox.warning(self, "Senha inválida", "A nova senha deve ter pelo menos 6 caracteres.")
            return
        
        if new_password != confirm:
            QMessageBox.warning(self, "Senha diferente", "As senhas não coincidem.")
            return
        
        # Verificar senha atual
        import hashlib
        senha_hash = hashlib.sha256(current.encode()).hexdigest()
        
        self.db.cursor.execute('''
        SELECT id FROM usuarios WHERE id = ? AND senha = ?
        ''', (self.usuario_id, senha_hash))
        
        if not self.db.cursor.fetchone():
            QMessageBox.critical(self, "Senha incorreta", "A senha atual está incorreta.")
            return
        
        # Atualizar senha
        nova_senha_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        try:
            self.db.cursor.execute('''
            UPDATE usuarios SET senha = ? WHERE id = ?
            ''', (nova_senha_hash, self.usuario_id))
            
            self.db.conn.commit()
            QMessageBox.information(self, "Senha atualizada", "Sua senha foi alterada com sucesso.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Não foi possível alterar a senha: {str(e)}")
    
    def paintEvent(self, event):
        """Personaliza o fundo da janela com um gradiente suave"""
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#f5f6fa"))
        gradient.setColorAt(1, QColor("#dfe6e9"))
        painter.fillRect(self.rect(), QBrush(gradient))