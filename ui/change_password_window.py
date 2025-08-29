# Arquivo: ui/change_password_window.py (VERSÃO PROFISSIONAL ATUALIZADA)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QFrame, 
                             QWidget, QTextEdit)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QColor
import hashlib

from .icon_manager import IconManager

# --- INÍCIO DA ADIÇÃO: CLASSE AlertDialog E DEPENDÊNCIAS ---
# Adicionamos a classe de diálogo customizada para manter a consistência visual.

class AlertDialog(QDialog):
    """Dialog customizado, integrado ao tema e visualmente aprimorado para alertas."""
    
    def __init__(self, parent, title, message, alert_type="info", theme_colors=None):
        super().__init__(parent)
        self.alert_type = alert_type
        self.theme_colors = theme_colors or self._get_default_colors()
        self.title_text = title
        
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self._setup_alert_info()
        self.setup_ui(message)

        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def _get_default_colors(self):
        return {
            'bg_color': "#ffffff", 'surface_color': "#f2f2f7", 'text_color': "#000000",
            'text_secondary': "#6d6d70", 'border_color': "#d1d1d6"
        }

    def _setup_alert_info(self):
        alerts = {
            "critical": {"icon": "delete", "color": "#d73a49", "prefix": "Erro"},
            "warning":  {"icon": "estoque_baixo", "color": "#ffc107", "prefix": "Atenção"},
            "info":     {"icon": "check", "color": "#28a745", "prefix": "Sucesso"}
        }
        self.alert_info = alerts.get(self.alert_type, alerts["info"])

    def setup_ui(self, message):
        container = QFrame(self)
        container.setObjectName("alertDialogContainer")
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(container)
        self.layout().setContentsMargins(0,0,0,0)

        header = QFrame()
        header.setObjectName("alertHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel(self.alert_info['prefix'])
        title_label.setObjectName("alertTitle")
        
        header_layout.addWidget(title_label, 1)

        body = QFrame()
        body.setObjectName("alertBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 15, 20, 20)
        
        subtitle_label = QLabel(self.title_text)
        subtitle_label.setObjectName("alertSubtitle")

        message_label = QLabel(message)
        message_label.setWordWrap(True)
        message_label.setObjectName("alertMessage")
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("OK")
        ok_button.setObjectName("okButton")
        ok_button.clicked.connect(self.accept)
        ok_button.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(ok_button)

        body_layout.addWidget(subtitle_label)
        body_layout.addSpacing(5)
        body_layout.addWidget(message_label)
        body_layout.addSpacing(15)
        body_layout.addLayout(button_layout)
        
        main_layout.addWidget(header)
        main_layout.addWidget(body)

        self.apply_style(self.alert_info['color'])

    def apply_style(self, border_color):
        style = f"""
        #alertDialogContainer {{
            background-color: {self.theme_colors['surface_color']};
            border: 1px solid {border_color};
            border-radius: 12px;
        }}
        #alertHeader {{
            background-color: {self.theme_colors['surface_color']};
            border-bottom: 1px solid {self.theme_colors['border_color']};
            border-top-left-radius: 11px;
            border-top-right-radius: 11px;
        }}
        #alertTitle {{
            color: {self.theme_colors['text_color']};
            font-size: 11pt;
            font-weight: bold;
        }}
        #alertBody {{
            background-color: {self.theme_colors['surface_color']};
            border-bottom-left-radius: 11px;
            border-bottom-right-radius: 11px;
        }}
        #alertSubtitle {{
             color: {self.theme_colors['text_color']};
             font-size: 12pt;
             font-weight: bold;
        }}
        #alertMessage {{
             color: {self.theme_colors['text_secondary']};
             font-size: 10pt;
        }}
        #okButton {{
            background-color: {border_color};
            color: white;
            font-weight: bold;
            font-size: 10pt;
            padding: 8px 25px;
            border-radius: 6px;
            border: none;
            min-width: 90px;
        }}
        #okButton:hover {{
            opacity: 0.9;
        }}
        """
        self.setStyleSheet(style)
        self.setMinimumWidth(400)
# --- FIM DA ADIÇÃO ---


class ChangePasswordWindow(QDialog):
    """Janela para alterar senha com design profissional e adaptada ao tema."""

    def __init__(self, db, usuario_id, theme_colors, logo_pixmap=None):
        super().__init__()
        self.db = db
        self.usuario_id = usuario_id
        self.theme_colors = theme_colors
        self.logo_pixmap = logo_pixmap
        self.drag_position = None

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(480, 450)
        self.setModal(True)
        
        container = QFrame(self)
        container.setObjectName("mainContainer")

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.header = self._create_header()
        main_layout.addWidget(self.header)

        main_layout.addWidget(self._create_content())

        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.addWidget(container)

        self.apply_styles()

    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f"""
            #mainContainer {{
                background-color: {colors['bg_color']};
                border-radius: 16px;
                border: 1px solid {colors['border_color']};
            }}
            #header {{
                background-color: {colors['surface_color']};
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                border-bottom: 1px solid {colors['border_color']};
            }}
            #controlButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }}
            #controlButton:hover {{
                background-color: {colors['button_hover']};
            }}
            #titleLabel {{
                font-size: 24px;
                font-weight: 600;
                color: {colors['text_color']};
            }}
            #subtitleLabel {{
                font-size: 14px;
                color: {colors['text_secondary']};
            }}
            QLabel {{
                color: {colors['text_secondary']};
                font-size: 14px;
                font-weight: 500;
            }}
            QLineEdit {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 12px;
                border-radius: 12px;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border: 2px solid {colors['accent_color']};
            }}
        """)

    def _create_header(self):
        header_widget = QFrame()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(50)
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        
        if self.logo_pixmap:
            logo_label = QLabel()
            logo_label.setPixmap(self.logo_pixmap.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            layout.addWidget(logo_label)

        title_label = QLabel("Alterar Senha")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {self.theme_colors['text_color']};")
        
        close_button = QPushButton()
        close_button.setObjectName("controlButton")
        close_button.setFixedSize(30, 30)
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors['text_secondary']))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(close_button)
        return header_widget

    def _create_content(self):
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(30, 20, 30, 30)
        layout.setSpacing(15)

        title_label = QLabel("Alterar Senha")
        title_label.setObjectName("titleLabel")
        
        subtitle_label = QLabel("Para sua segurança, por favor, escolha uma nova senha forte.")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addSpacing(15)

        layout.addWidget(QLabel("Senha Atual"))
        self.current_password = QLineEdit()
        self.current_password.setPlaceholderText("Digite sua senha atual")
        self.current_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.current_password)
        
        layout.addWidget(QLabel("Nova Senha"))
        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Mínimo de 6 caracteres")
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password)
        
        layout.addWidget(QLabel("Confirmar Nova Senha"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("Confirme a nova senha")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)
        
        layout.addStretch()

        from .profile_window import ThemedButton
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        
        self.cancel_button = ThemedButton("Cancelar", self.theme_colors, "secondary")
        self.save_button = ThemedButton("Salvar Alterações", self.theme_colors, "primary", icon_name='save')
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        layout.addLayout(buttons_layout)
        
        self.save_button.clicked.connect(self.save_password)
        self.cancel_button.clicked.connect(self.reject)
        
        return content_widget

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.header.underMouse():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def save_password(self):
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

        self.db.cursor.execute("SELECT senha FROM usuarios WHERE id = ?", (self.usuario_id,))
        result = self.db.cursor.fetchone()
        if not result:
            self.show_message("Erro Crítico", "Usuário não encontrado.", "critical")
            return
            
        senha_hash_db = result['senha']
        current_pass_hash = hashlib.sha256(current_pass_plain.encode('utf-8')).hexdigest()

        if current_pass_hash != senha_hash_db:
            self.show_message("Senha Incorreta", "A sua senha atual está incorreta.", "critical")
            return

        success, msg = self.db.alterar_senha_usuario(self.usuario_id, new_pass_plain)
        
        if success:
            self.show_message("Sucesso", msg, "info")
            self.accept()
        else:
            self.show_message("Erro ao Salvar", msg, "critical")
    
    # --- CORREÇÃO APLICADA AQUI ---
    # Substituímos o QMessageBox pelo AlertDialog customizado.
    def show_message(self, title, message, level="info"):
        """Exibe uma mensagem usando o diálogo customizado AlertDialog."""
        
        alert_type_map = {
            "info": "info",
            "warning": "warning",
            "critical": "critical"
        }
        alert_type = alert_type_map.get(level, "info")

        alert_dialog = AlertDialog(self, title, message, alert_type=alert_type, theme_colors=self.theme_colors)
        alert_dialog.exec_()