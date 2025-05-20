from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QGridLayout, QSpacerItem,
                             QSizePolicy)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve


class ChangePasswordWindow(QDialog):
    def __init__(self, db, usuario_id, dark_mode=False):
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.dark_mode = dark_mode
        self.setWindowTitle("Alterar Senha")
        self.setFixedSize(460, 380)  # Aumentei o tamanho da janela
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Definir cores conforme o tema
        self.setup_colors()
        self.setup_ui()
    
    def setup_colors(self):
        """Configura as cores com base no modo claro/escuro"""
        if self.dark_mode:
            self.bg_color = "#1c1c1e"
            self.surface_color = "#2c2c2e" 
            self.text_color = "#ffffff"
            self.text_secondary = "#8e8e93"
            self.border_color = "#3a3a3c"
            self.button_hover = "#3a3a3c"
            self.accent_color = "#007AFF"
        else:
            self.bg_color = "#ffffff"
            self.surface_color = "#f2f2f7"
            self.text_color = "#000000"
            self.text_secondary = "#6d6d70"
            self.border_color = "#d1d1d6"
            self.button_hover = "#e5e5ea"
            self.accent_color = "#007AFF"
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(18)  # Reduzi um pouco o espaçamento
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Estilo geral da janela
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {self.bg_color};
            }}
            QLabel {{
                color: {self.text_color};
            }}
        """)
        
        # Título
        title_label = QLabel("Alterar Senha")
        title_label.setFont(QFont("SF Pro Display", 22, QFont.DemiBold))
        title_label.setAlignment(Qt.AlignLeft)
        title_label.setStyleSheet(f"color: {self.text_color}; margin-bottom: 5px;")
        main_layout.addWidget(title_label)
        
        # Subtítulo
        subtitle = QLabel("Configure uma nova senha para sua conta")
        subtitle.setFont(QFont("SF Pro Text", 13))
        subtitle.setStyleSheet(f"color: {self.text_secondary};")
        main_layout.addWidget(subtitle)
        
        # Espaçador
        main_layout.addSpacing(8)
        
        # Usar Grid Layout em vez de Form Layout para maior controle
        grid_layout = QGridLayout()
        grid_layout.setSpacing(12)  # Espaçamento menor
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        # Estilo para os campos - reduzindo o padding para evitar cortes
        input_style = f"""
            QLineEdit {{
                padding: 8px 12px;
                border-radius: 8px;
                background-color: {self.surface_color};
                color: {self.text_color};
                border: none;
                font-size: 14px;
                selection-background-color: {self.accent_color}40;
            }}
            QLineEdit:focus {{
                border: 2px solid {self.accent_color};
                padding: 7px 11px;
            }}
        """
        
        # Estilo para as labels do formulário
        form_label_style = f"""
            QLabel {{
                font-size: 14px;
                font-weight: normal;
                color: {self.text_color};
                padding-right: 10px;
            }}
        """
        
        # Campos de senha
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Digite sua senha atual")
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setStyleSheet(input_style)
        self.current_password.setMinimumHeight(42)  # Ligeiramente menor
        self.current_password.setFixedHeight(42)    # Fixar altura
        
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Digite a nova senha")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet(input_style)
        self.new_password.setMinimumHeight(42)
        self.new_password.setFixedHeight(42)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirme a nova senha")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet(input_style)
        self.confirm_password.setMinimumHeight(42)
        self.confirm_password.setFixedHeight(42)
        
        # Labels do formulário
        current_label = QLabel("Senha atual")
        current_label.setStyleSheet(form_label_style)
        
        new_label = QLabel("Nova senha")
        new_label.setStyleSheet(form_label_style)
        
        confirm_label = QLabel("Confirmar senha")
        confirm_label.setStyleSheet(form_label_style)
        
        # Adicionar campos ao grid layout
        grid_layout.addWidget(current_label, 0, 0)
        grid_layout.addWidget(self.current_password, 0, 1)
        
        grid_layout.addWidget(new_label, 1, 0)
        grid_layout.addWidget(self.new_password, 1, 1)
        
        grid_layout.addWidget(confirm_label, 2, 0)
        grid_layout.addWidget(self.confirm_password, 2, 1)
        
        # Configurar proporções do grid
        grid_layout.setColumnStretch(0, 1)  # A coluna das labels terá peso 1
        grid_layout.setColumnStretch(1, 3)  # A coluna dos inputs terá peso 3
        
        main_layout.addLayout(grid_layout)
        
        # Informação sobre senha
        password_info = QLabel("A senha deve ter pelo menos 6 caracteres, incluindo letras e números.")
        password_info.setFont(QFont("SF Pro Text", 12))
        password_info.setStyleSheet(f"color: {self.text_secondary}; margin-top: 2px;")
        password_info.setWordWrap(True)
        main_layout.addWidget(password_info)
        
        # Espaçador expansível
        main_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Botões
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedSize(130, 42)  # Fixar tamanho
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setFont(QFont("SF Pro Text", 14))
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.surface_color};
                color: {self.accent_color};
                border: none;
                border-radius: 21px;
                font-weight: medium;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: {self.button_hover};
            }}
            QPushButton:pressed {{
                background-color: {self.button_hover};
                opacity: 0.8;
            }}
        """)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.setFixedSize(130, 42)  # Fixar tamanho
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setFont(QFont("SF Pro Text", 14))
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                border-radius: 21px;
                font-weight: medium;
                padding: 0 15px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_color}E6;
            }}
            QPushButton:pressed {{
                background-color: {self.accent_color}CC;
            }}
        """)
        
        # Adicionar espaçador antes dos botões para alinhá-los à direita
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
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
            self.show_message("Campos vazios", "Por favor, preencha todos os campos.")
            return
        
        if len(new_password) < 6:
            self.show_message("Senha inválida", "A nova senha deve ter pelo menos 6 caracteres.")
            return
        
        if new_password != confirm:
            self.show_message("Senha diferente", "As senhas não coincidem.")
            return
        
        # Verificar senha atual
        import hashlib
        senha_hash = hashlib.sha256(current.encode()).hexdigest()
        
        self.db.cursor.execute('''
        SELECT id FROM usuarios WHERE id = ? AND senha = ?
        ''', (self.usuario_id, senha_hash))
        
        if not self.db.cursor.fetchone():
            self.show_message("Senha incorreta", "A senha atual está incorreta.", icon=QMessageBox.Critical)
            return
        
        # Atualizar senha
        nova_senha_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        try:
            self.db.cursor.execute('''
            UPDATE usuarios SET senha = ? WHERE id = ?
            ''', (nova_senha_hash, self.usuario_id))
            
            self.db.conn.commit()
            self.show_message("Senha atualizada", "Sua senha foi alterada com sucesso.", icon=QMessageBox.Information)
            self.accept()
        except Exception as e:
            self.show_message("Erro", f"Não foi possível alterar a senha: {str(e)}", icon=QMessageBox.Critical)
    
    def show_message(self, title, message, icon=QMessageBox.Warning):
        """Exibe mensagens estilizadas"""
        msg_box = QMessageBox(self)
        msg_box.setIcon(icon)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setFont(QFont("SF Pro Text", 12))
        
        # Estilizar o QMessageBox - ajustado para melhor visualização
        msg_box.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.bg_color};
                color: {self.text_color};
            }}
            QLabel {{
                color: {self.text_color};
                min-width: 300px;
            }}
            QPushButton {{
                background-color: {self.accent_color};
                color: white;
                border: none;
                border-radius: 16px;
                padding: 6px 16px;
                font-weight: medium;
                min-width: 80px;
                min-height: 32px;
            }}
            QPushButton:hover {{
                background-color: {self.accent_color}E6;
            }}
        """)
        
        msg_box.exec_()
    
    def paintEvent(self, event):
        """Remove o gradiente e aplica fundo liso"""
        super().paintEvent(event)
        # O estilo do fundo já é aplicado via setStyleSheet