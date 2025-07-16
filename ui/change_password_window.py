# Arquivo: ui/change_password_window.py (VERSÃO TEMÁTICA)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QGridLayout)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import hashlib

# Importe o IconManager para usar ícones consistentes
from .icon_manager import IconManager

class ChangePasswordWindow(QDialog):
    """Janela para alterar senha, adaptada para herdar o tema."""

    # 1. Modificar o construtor para aceitar theme_colors
    def __init__(self, db, usuario_id, theme_colors):
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.theme_colors = theme_colors  # Armazena o dicionário de tema
        
        self.setWindowTitle("Alterar Senha")
        self.setFixedSize(480, 400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.setup_ui()
        self.apply_styles() # Aplica os estilos

    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 25, 25, 25)

        title_label = QLabel("Alterar Senha")
        title_label.setObjectName("titleLabel")
        
        subtitle_label = QLabel("Para sua segurança, por favor, escolha uma nova senha forte.")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setWordWrap(True)

        main_layout.addWidget(title_label)
        main_layout.addWidget(subtitle_label)
        main_layout.addSpacing(10)

        # Campos do formulário
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)
        
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Digite sua senha atual")
        self.current_password.setEchoMode(QLineEdit.Password)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Mínimo de 6 caracteres")
        self.new_password.setEchoMode(QLineEdit.Password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirme a nova senha")
        self.confirm_password.setEchoMode(QLineEdit.Password)

        form_layout.addWidget(QLabel("Senha Atual:"), 0, 0)
        form_layout.addWidget(self.current_password, 0, 1)
        form_layout.addWidget(QLabel("Nova Senha:"), 1, 0)
        form_layout.addWidget(self.new_password, 1, 1)
        form_layout.addWidget(QLabel("Confirmar Senha:"), 2, 0)
        form_layout.addWidget(self.confirm_password, 2, 1)
        
        form_layout.setColumnStretch(1, 1)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.cancel_button = QPushButton("Cancelar")
        self.save_button = QPushButton("Salvar Alterações")
        self.save_button.setObjectName("primaryButton")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        main_layout.addLayout(buttons_layout)
        
        # Conectar sinais
        self.save_button.clicked.connect(self.save_password)
        self.cancel_button.clicked.connect(self.reject)

    def apply_styles(self):
        """Aplica a folha de estilo QSS baseada no tema."""
        colors = self.theme_colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg_color']};
            }}
            #titleLabel {{
                font-size: 22pt;
                font-weight: bold;
                color: {colors['text_color']};
            }}
            #subtitleLabel {{
                font-size: 11pt;
                color: {colors['text_secondary']};
            }}
            QLabel {{
                color: {colors['text_color']};
                font-size: 10pt;
            }}
            QLineEdit {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 10px;
                border-radius: 8px;
            }}
            QLineEdit:focus {{
                border: 1px solid {colors['accent_color']};
            }}
            QPushButton {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 10px 20px;
                border-radius: 8px;
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

    def save_password(self):
        """Salva a nova senha no banco de dados, agora usando hash."""
        current_pass_plain = self.current_password.text()
        new_pass_plain = self.new_password.text()
        confirm_pass_plain = self.confirm_password.text()

        if not all([current_pass_plain, new_pass_plain, confirm_pass_plain]):
            self.show_message("Campos Vazios", "Por favor, preencha todos os campos.", "warning")
            return

        if len(new_pass_plain) < 6:
            self.show_message("Senha Inválida", "A nova senha deve ter pelo menos 6 caracteres.", "warning")
            return

        if new_pass_plain != confirm_pass_plain:
            self.show_message("Senhas Diferentes", "A nova senha e a confirmação não coincidem.", "warning")
            return

        # --- LÓGICA DE HASH CORRIGIDA ---
        # 1. Obter o usuário e sua senha HASHEADA do banco
        usuario_db = self.db.obter_usuario_por_id(self.usuario_id)
        if not usuario_db:
             self.show_message("Erro Crítico", "Usuário não encontrado no sistema.", "critical")
             return

        # 2. Obter a senha hasheada armazenada
        #    Precisamos buscar a senha diretamente, pois obter_usuario_por_id não a retorna.
        self.db.cursor.execute("SELECT senha FROM usuarios WHERE id = ?", (self.usuario_id,))
        senha_hash_db = self.db.cursor.fetchone()['senha']
        
        # 3. Fazer o hash da senha atual que o usuário digitou
        current_pass_hash = hashlib.sha256(current_pass_plain.encode('utf-8')).hexdigest()

        # 4. Comparar os dois hashes
        if current_pass_hash != senha_hash_db:
            self.show_message("Senha Incorreta", "A sua senha atual está incorreta.", "critical")
            return

        # 5. Se a senha atual estiver correta, chame o método do DB para alterar, que já faz o hash
        success, msg = self.db.alterar_senha_usuario(self.usuario_id, new_pass_plain)
        
        if success:
            self.show_message("Sucesso", msg, "info")
            self.accept()
        else:
            self.show_message("Erro ao Salvar", msg, "critical")
    
    def show_message(self, title, message, level="info"):
        icon_map = {"info": QMessageBox.Information, "warning": QMessageBox.Warning, "critical": QMessageBox.Critical}
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon_map.get(level, QMessageBox.Information))
        
        colors = self.theme_colors
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {colors['surface_color']};
                border-radius: 12px;
            }}
            QMessageBox QLabel {{
                color: {colors['text_color']};
                font-size: 10pt;
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {colors['accent_color']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                min-width: 80px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #005bb5;
            }}
        """)
        msg_box.exec_()