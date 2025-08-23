from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QWidget, 
                             QFrame)
from PyQt5.QtGui import QFont, QRegExpValidator, QPixmap
from PyQt5.QtCore import Qt, QRegExp

from .icon_manager import IconManager

# --- As classes de widgets temáticos (ThemedLineEdit, etc.) permanecem as mesmas ---
# (O código delas está correto e foi omitido aqui para focar na ProfileWindow)

class ThemedLineEdit(QLineEdit):
    """Campo de texto que se adapta ao tema."""
    def __init__(self, theme_colors, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.theme_colors = theme_colors
        self.apply_style()

    def apply_style(self):
        colors = self.theme_colors
        self.setFixedHeight(48)
        self.setStyleSheet(f"""
            QLineEdit {{
                padding: 12px 16px;
                border: 1px solid {colors['border_color']};
                border-radius: 12px;
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                font-size: 16px;
            }}
            QLineEdit:focus {{
                border: 2px solid {colors['accent_color']};
                background-color: {colors['bg_color']};
            }}
            QLineEdit:read-only {{
                background-color: {colors['border_color']};
                color: {colors['text_secondary']};
            }}
            QLineEdit::placeholder {{
                color: {colors['text_secondary']};
            }}
        """)

class ThemedFieldGroup(QWidget):
    """Grupo de campo que se adapta ao tema."""
    def __init__(self, label_text, input_widget, theme_colors):
        super().__init__()
        self.theme_colors = theme_colors
        self.setup_ui(label_text, input_widget)

    def setup_ui(self, label_text, input_widget):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setStyleSheet(f"""
            QLabel {{
                color: {self.theme_colors['text_color']};
                font-size: 14px;
                font-weight: 500;
                padding-left: 4px;
            }}
        """)
        layout.addWidget(label)
        layout.addWidget(input_widget)

class ThemedButton(QPushButton):
    """Botão que se adapta ao tema."""
    def __init__(self, text, theme_colors, button_type="primary", icon_name=None):
        super().__init__(text)
        self.theme_colors = theme_colors
        self.button_type = button_type
        self.icon_name = icon_name
        self.apply_style()

    def apply_style(self):
        colors = self.theme_colors
        self.setFixedHeight(50)
        self.setCursor(Qt.PointingHandCursor)
        
        icon_color = 'white'
        bg_color = colors['accent_color']
        hover_bg_color = '#005bb5' # Derivado do accent
        text_color = 'white'
        border_style = "border: none;"
        
        if self.button_type == "secondary":
            icon_color = colors['text_color']
            bg_color = colors['surface_color']
            hover_bg_color = colors['button_hover']
            text_color = colors['text_color']
            border_style = f"border: 1px solid {colors['border_color']};"
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                {border_style}
                border-radius: 12px;
                font-weight: 500;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {hover_bg_color};
            }}
            QPushButton:disabled {{
                background-color: {colors['border_color']};
                color: {colors['text_secondary']};
            }}
        """)
        
        if self.icon_name:
            self.setIcon(IconManager.get_icon(self.icon_name, color=icon_color))

class ThemedAvatar(QWidget):
    """Avatar que se adapta ao tema."""
    def __init__(self, usuario, theme_colors):
        super().__init__()
        self.usuario = usuario
        self.theme_colors = theme_colors
        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(80, 80)
        colors = self.theme_colors
        
        avatar_container = QLabel(self)
        avatar_container.setFixedSize(80, 80)
        avatar_container.setAlignment(Qt.AlignCenter)
        
        iniciais = "".join([nome[0].upper() for nome in self.usuario['nome'].split()[:2]])
        avatar_container.setText(iniciais)
        
        avatar_container.setStyleSheet(f"""
            QLabel {{
                background-color: {colors['accent_color']};
                color: white;
                border-radius: 40px;
                border: 3px solid {colors['bg_color']};
                font-size: 28px;
                font-weight: 600;
            }}
        """)


class ProfileWindow(QDialog):
    """Janela de perfil profissional, frameless e adaptada ao tema."""
    # --- CORREÇÃO: Construtor agora aceita o pixmap do logo ---
    def __init__(self, db, usuario, theme_colors, logo_pixmap=None):
        super().__init__()
        self.db = db
        self.usuario = usuario
        self.theme_colors = theme_colors
        self.logo_pixmap = logo_pixmap
        self.drag_position = None

        # --- CORREÇÃO: Janela sem borda e com fundo transparente para cantos arredondados ---
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setup_ui()

    def setup_ui(self):
        self.setFixedSize(480, 680)
        self.setModal(True)
        
        # --- CORREÇÃO: Container principal para aplicar o estilo (background, bordas) ---
        container = QFrame(self)
        container.setObjectName("mainContainer")

        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.header = self._create_header()
        main_layout.addWidget(self.header)

        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setObjectName("separator")
        main_layout.addWidget(separator)

        main_layout.addWidget(self._create_content())

        # Adiciona o container ao layout do QDialog
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
            }}
            #separator {{
                border-color: {colors['border_color']};
            }}
            #controlButton {{
                background-color: transparent;
                border: none;
                border-radius: 8px;
            }}
            #controlButton:hover {{
                background-color: {colors['button_hover']};
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

        title_label = QLabel("Meu Perfil")
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 600; color: {self.theme_colors['text_color']};")
        
        # Botão de ajuda (exemplo)
        help_button = QPushButton()
        help_button.setObjectName("controlButton")
        help_button.setFixedSize(30, 30)
        help_button.setIcon(IconManager.get_icon('sobre', color=self.theme_colors['text_secondary']))
        help_button.setCursor(Qt.PointingHandCursor)
        
        close_button = QPushButton()
        close_button.setObjectName("controlButton")
        close_button.setFixedSize(30, 30)
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors['text_secondary']))
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(help_button)
        layout.addWidget(close_button)
        return header_widget

    def _create_content(self):
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(40, 25, 40, 30)
        layout.setSpacing(20)

        # --- CORREÇÃO: Centralização do avatar ---
        # Colocamos o avatar dentro de um layout horizontal com spacers para forçar a centralização
        avatar_h_layout = QHBoxLayout()
        avatar_h_layout.addStretch()
        avatar_h_layout.addWidget(ThemedAvatar(self.usuario, self.theme_colors))
        avatar_h_layout.addStretch()
        
        # Agrupamos tudo relacionado ao avatar em um layout vertical
        avatar_area = QVBoxLayout()
        avatar_area.setSpacing(8)
        avatar_area.addLayout(avatar_h_layout) # Adiciona o layout horizontal aqui
        
        name_label = QLabel(self.usuario['nome'])
        name_label.setAlignment(Qt.AlignCenter)
        name_label.setStyleSheet(f"font-size: 22px; font-weight: 600; color: {self.theme_colors['text_color']};")
        
        tipo_label = QLabel(self.usuario['tipo'].capitalize())
        tipo_label.setAlignment(Qt.AlignCenter)
        tipo_label.setStyleSheet(f"font-size: 16px; color: {self.theme_colors['text_secondary']};")
        
        avatar_area.addWidget(name_label)
        avatar_area.addWidget(tipo_label)
        layout.addLayout(avatar_area)
        
        # Formulário (sem alterações)
        self.name_edit = ThemedLineEdit(self.theme_colors, self.usuario['nome'])
        layout.addWidget(ThemedFieldGroup("Nome Completo", self.name_edit, self.theme_colors))

        self.login_edit = ThemedLineEdit(self.theme_colors, f"@{self.usuario['login']}")
        self.login_edit.setReadOnly(True)
        layout.addWidget(ThemedFieldGroup("Nome de Usuário (não pode ser alterado)", self.login_edit, self.theme_colors))

        self.email_edit = ThemedLineEdit(self.theme_colors, self.usuario.get('email', ''))
        self.email_edit.setPlaceholderText("seu.email@exemplo.com")
        email_regex = QRegExp(r"[^@]+@[^@]+\.[a-zA-Z]{2,}")
        self.email_edit.setValidator(QRegExpValidator(email_regex))
        layout.addWidget(ThemedFieldGroup("E-mail", self.email_edit, self.theme_colors))

        layout.addStretch()

        # Botões (sem alterações)
        self.save_button = ThemedButton("Salvar Alterações", self.theme_colors, "primary", icon_name='save')
        self.save_button.clicked.connect(self.save_profile)
        
        self.change_password_button = ThemedButton("Alterar Senha", self.theme_colors, "secondary", icon_name='password')
        self.change_password_button.clicked.connect(self.open_change_password)
        
        layout.addWidget(self.save_button)
        layout.addWidget(self.change_password_button)
        
        return content_widget

    # --- CORREÇÃO: Métodos para arrastar a janela ---
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.header.underMouse():
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    # Métodos save_profile, open_change_password e show_message permanecem os mesmos
    def save_profile(self):
        nome = self.name_edit.text().strip()
        email = self.email_edit.text().strip()
        
        if not nome:
            self.show_message("Campo obrigatório", "O nome não pode ficar em branco.", "warning")
            return
        
        if email and not self.email_edit.hasAcceptableInput():
            self.show_message("E-mail inválido", "Por favor, insira um e-mail válido.", "warning")
            return
        
        try:
            self.db.atualizar_usuario(self.usuario['id'], nome, self.usuario['login'], email, self.usuario['tipo'], 1)
            self.usuario['nome'] = nome
            self.usuario['email'] = email
            self.show_message("Sucesso", "Suas informações foram atualizadas com sucesso.")
            self.accept()
        except Exception as e:
            self.show_message("Erro", f"Erro ao atualizar perfil: {e}", "critical")

    def open_change_password(self):
        """Abrir diálogo para alterar senha"""
        from ui.change_password_window import ChangePasswordWindow
        
        # --- CORREÇÃO APLICADA AQUI ---
        # Passa o logo que a ProfileWindow já recebeu para a ChangePasswordWindow
        password_dialog = ChangePasswordWindow(self.db, self.usuario['id'], self.theme_colors, self.logo_pixmap)
        password_dialog.exec_()

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
                font-size: 15px;
            }}
            QPushButton {{
                background-color: {colors['accent_color']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                min-width: 90px;
            }}
            QPushButton:hover {{
                background-color: #005bb5;
            }}
        """)
        msg_box.exec_()