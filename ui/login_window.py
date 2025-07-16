import base64
import random
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QCheckBox, QFrame,
                             QGraphicsDropShadowEffect, QToolButton, QStackedWidget)
from PyQt5.QtCore import (Qt, pyqtSignal, QSize, QSettings, QPropertyAnimation,
                          QSequentialAnimationGroup, QPoint, QEasingCurve)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont, QCursor

# Remova o CHECK_ICON_BASE64, pois usaremos um ícone dinâmico

# Importe o IconManager da sua UI. 
# Certifique-se que o caminho do import está correto para a sua estrutura de pastas.
from ui.icon_manager import IconManager

#==============================================================================
# CLASSE DA JANELA DE LOGIN PRINCIPAL
#==============================================================================
class LoginWindow(QDialog):
    login_success_signal = pyqtSignal(dict)

    # Modificação 1: Receber 'settings' e 'theme_colors' no construtor
    def __init__(self, db_manager, theme_colors):
        super().__init__()
        self.db = db_manager
        self.theme_colors = theme_colors # Recebemos o tema, que é o que importa
        self.usuario = None
        self.offset = None
        
        # CRIAMOS UMA INSTÂNCIA DE QSETTINGS APENAS PARA ESTA JANELA
        # Isso resolve o erro, pois agora self.settings é do tipo correto (QSettings).
        self.settings = QSettings("SuaEmpresa", "SeuERP") 

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.init_ui()
        self.load_saved_credentials()

    def showEvent(self, event):
        super().showEvent(event)
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(400)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_in_animation.start()

    def shake_window(self):
        original_pos = self.pos()
        self.shake_animation_group = QSequentialAnimationGroup(self)
        movements = [
            (50, QPoint(original_pos.x() - 10, original_pos.y())),
            (50, QPoint(original_pos.x() + 20, original_pos.y())),
            (50, QPoint(original_pos.x() - 20, original_pos.y())),
            (50, QPoint(original_pos.x() + 10, original_pos.y())),
            (50, original_pos)
        ]
        last_pos = original_pos
        for duration, end_pos in movements:
            anim = QPropertyAnimation(self, b"pos")
            anim.setDuration(duration)
            anim.setStartValue(last_pos)
            anim.setEndValue(end_pos)
            anim.setEasingCurve(QEasingCurve.InOutSine)
            self.shake_animation_group.addAnimation(anim)
            last_pos = end_pos
        self.shake_animation_group.start()

    def init_ui(self):
        self.setMinimumWidth(420)
        self.setMinimumHeight(640)
        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(25, 25, 25, 25)
        login_container = QFrame(self)
        login_container.setObjectName("loginContainer")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(35)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 60))
        login_container.setGraphicsEffect(shadow)
        main_layout = QVBoxLayout(login_container)
        main_layout.setContentsMargins(40, 30, 40, 40)
        main_layout.setSpacing(15)
        
        # Modificação 2: Aplicar o stylesheet dinâmico
        self.setStyleSheet(self.get_stylesheet()) 

        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        close_button = QToolButton()
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(28, 28)
        # Modificação 3: Usar IconManager
        close_button.setIcon(IconManager.get_icon('fechar', self.theme_colors['text_secondary']))
        close_button.setIconSize(QSize(12, 12))
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        close_button.setToolTip("Fechar")
        close_button.clicked.connect(self.reject)
        header_layout.addWidget(close_button)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        title_layout.setContentsMargins(0, 0, 0, 30)
        logo_label = QLabel()
        # Usar IconManager para a logo também, para consistência
        logo_icon = IconManager.get_icon('estoque', color=self.theme_colors['accent_color'])
        logo_label.setPixmap(logo_icon.pixmap(QSize(80, 80)))
        logo_label.setAlignment(Qt.AlignCenter)
        title_label = QLabel("Bem-vindo de volta")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        subtitle_label = QLabel("Acesse sua conta para continuar")
        subtitle_label.setObjectName("subtitleLabel")
        subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(logo_label)
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(18)
        # Modificação 4: Passar o nome do ícone para o método helper
        user_label_widget = self._create_field_label_with_icon("user", "USUÁRIO")
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Digite seu nome de usuário")
        self.login_edit.textChanged.connect(self.validate_inputs)
        
        senha_label_widget = self._create_field_label_with_icon("password", "SENHA")
        senha_container = QFrame()
        senha_container.setObjectName("inputContainer")
        senha_container_layout = QHBoxLayout(senha_container)
        senha_container_layout.setContentsMargins(0, 0, 0, 0)
        senha_container_layout.setSpacing(0)
        self.senha_edit = QLineEdit()
        self.senha_edit.setEchoMode(QLineEdit.Password)
        self.senha_edit.setPlaceholderText("Digite sua senha")
        self.senha_edit.textChanged.connect(self.validate_inputs)
        self.toggle_password_button = QToolButton(self)
        self.toggle_password_button.setObjectName("togglePasswordButton")
        self.toggle_password_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggle_password_button.setFixedSize(44, 44)
        self.toggle_password_button.clicked.connect(self.toggle_password_visibility)
        self.password_visible = False
        self.update_password_toggle_icon()
        senha_container_layout.addWidget(self.senha_edit)
        senha_container_layout.addWidget(self.toggle_password_button)
        
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 5, 0, 5)
        self.remember_checkbox = QCheckBox("Lembrar-me")
        forgot_password_label = QLabel("<a href='#'>Esqueci minha senha</a>")
        forgot_password_label.setObjectName("forgotPasswordLabel")
        forgot_password_label.setCursor(QCursor(Qt.PointingHandCursor))
        forgot_password_label.linkActivated.connect(self.handle_forgot_password)
        options_layout.addWidget(self.remember_checkbox)
        options_layout.addStretch()
        options_layout.addWidget(forgot_password_label)
        
        form_layout.addWidget(user_label_widget)
        form_layout.addWidget(self.login_edit)
        form_layout.addSpacing(5)
        form_layout.addWidget(senha_label_widget)
        form_layout.addWidget(senha_container)
        form_layout.addLayout(options_layout)
        
        button_layout = QVBoxLayout()
        button_layout.setContentsMargins(0, 20, 0, 0)
        self.login_button = QPushButton("ENTRAR")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.login_button.setEnabled(False)
        self.login_button.clicked.connect(self.try_login)
        button_layout.addWidget(self.login_button)
        
        main_layout.addLayout(header_layout)
        main_layout.addLayout(title_layout)
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
        base_layout.addWidget(login_container)

    # Modificação 5: Método _create_field_label_with_icon atualizado
    def _create_field_label_with_icon(self, icon_name, text):
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(6)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6e6e73')
        icon = IconManager.get_icon(icon_name, color=icon_color)
        icon_label.setPixmap(icon.pixmap(QSize(14, 14)))
        
        text_label = QLabel(text)
        text_label.setObjectName("fieldLabel")
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        return widget

    # Modificação 6: Stylesheet agora é dinâmico com base no tema
    def get_stylesheet(self):
        # Extrai cores do dicionário de tema com valores padrão para segurança
        bg_color = self.theme_colors.get('bg_color', '#ffffff')
        surface_color = self.theme_colors.get('surface_color', '#f5f5f7')
        text_color = self.theme_colors.get('text_color', '#1d1d1f')
        text_secondary = self.theme_colors.get('text_secondary', '#86868b')
        field_label_color = self.theme_colors.get('text_secondary', '#6e6e73')
        border_color = self.theme_colors.get('border_color', '#e5e5e5')
        accent_color = self.theme_colors.get('accent_color', '#007AFF')
        
        # O ícone do checkmark agora também pode ser temático se necessário
        check_icon = IconManager.get_icon('check', color='white').pixmap(QSize(16, 16))
        check_icon_path = "assets/temp_check_icon.png"
        check_icon.save(check_icon_path) # Salva temporariamente para usar na URL

        return f"""
            #loginContainer {{ 
                background-color: {bg_color}; 
                border-radius: 16px; 
            }}
            #titleLabel {{ 
                font-family: -apple-system, system-ui, sans-serif; 
                font-size: 26px; font-weight: 600; 
                color: {text_color}; 
            }}
            #subtitleLabel {{ 
                font-family: -apple-system, system-ui, sans-serif; 
                font-size: 15px; 
                color: {text_secondary}; 
            }}
            #fieldLabel {{ 
                font-family: -apple-system, system-ui, sans-serif; 
                font-size: 11px; font-weight: 600; 
                color: {field_label_color}; 
                padding-left: 3px; 
                letter-spacing: 0.5px; 
            }}
            QLineEdit {{ 
                background-color: {surface_color}; 
                border: 1.5px solid {border_color}; 
                border-radius: 10px; 
                padding: 13px 15px; 
                font-size: 15px; 
                color: {text_color}; 
            }}
            QLineEdit:focus {{ 
                border-color: {accent_color}; 
                background-color: {bg_color}; 
            }}
            #inputContainer {{ 
                border-radius: 10px; 
                background-color: {surface_color}; 
                border: 1.5px solid {border_color}; 
            }}
            #inputContainer:focus-within {{ 
                border-color: {accent_color}; 
                background-color: {bg_color}; 
            }}
            #inputContainer QLineEdit {{ 
                border: none; 
                background-color: transparent; 
            }}
            #togglePasswordButton {{ 
                background-color: transparent; 
                border: none; padding: 8px; 
            }}
            #loginButton {{ 
                background: {accent_color}; 
                color: #ffffff; 
                font-size: 14px; 
                font-weight: 600; 
                padding: 16px; 
                border-radius: 12px; 
                border: none; 
            }}
            #loginButton:hover {{ 
                background: #005bb5; /* Cor de hover para o accent color */
            }}
            #loginButton:pressed {{ 
                background-color: #004c99; 
            }}
            #loginButton:disabled {{ 
                background: {border_color}; 
                color: {text_secondary}; 
            }}
            #closeButton {{ 
                background-color: {surface_color}; 
                border: none; border-radius: 14px; 
            }}
            #closeButton:hover {{ background-color: {border_color}; }}
            #closeButton:pressed {{ background-color: #d0d0d0; }}
            QCheckBox {{ 
                font-size: 13px; 
                color: {text_color}; 
                spacing: 8px; 
            }}
            QCheckBox::indicator {{ 
                width: 18px; height: 18px; 
                border: 1.5px solid {border_color}; 
                border-radius: 6px; 
                background-color: {bg_color}; 
            }}
            QCheckBox::indicator:hover {{ border-color: {text_secondary}; }}
            QCheckBox::indicator:checked {{ 
                background-color: {accent_color}; 
                border-color: {accent_color}; 
                image: url({check_icon_path}); 
            }}
            #forgotPasswordLabel a {{ 
                color: {accent_color}; 
                text-decoration: none; 
                font-size: 13px; 
                font-weight: 500; 
            }}
            #forgotPasswordLabel a:hover {{ text-decoration: underline; }}
        """

    def try_login(self):
        login = self.login_edit.text().strip()
        senha = self.senha_edit.text().strip()
        usuario = self.db.autenticar_usuario(login, senha)
        if usuario:
            self.usuario = usuario
            self.save_credentials(login, senha)
            self.login_success_signal.emit(usuario)
            self.accept()
        else:
            self.shake_window()
            if self.settings.value("remember_user", False, type=bool):
                self.clear_saved_credentials()
                self.remember_checkbox.setChecked(False)
            self.show_error_message("Falha no Login", "Usuário ou senha incorretos. Verifique e tente novamente.")

    def handle_forgot_password(self):
        """Lida com o clique no link 'Esqueci minha senha'."""
        # Modificação 7: Passar o tema para a janela de recuperação
        recovery_dialog = PasswordRecoveryDialog(self.db, self.theme_colors, self)
        recovery_dialog.exec_()
    
    def load_saved_credentials(self):
        if self.settings.value("remember_user", False, type=bool):
            saved_username = self.settings.value("username", "")
            saved_password_b64 = self.settings.value("password", "")
            if saved_username and saved_password_b64:
                try:
                    decoded_password = base64.b64decode(saved_password_b64.encode()).decode()
                    self.login_edit.setText(saved_username)
                    self.senha_edit.setText(decoded_password)
                    self.remember_checkbox.setChecked(True)
                    self.validate_inputs()
                    self.login_button.setFocus()
                except Exception:
                    self.clear_saved_credentials()

    def save_credentials(self, username, password):
        if self.remember_checkbox.isChecked():
            encoded_password = base64.b64encode(password.encode()).decode()
            self.settings.setValue("remember_user", True)
            self.settings.setValue("username", username)
            self.settings.setValue("password", encoded_password)
        else:
            self.clear_saved_credentials()

    def clear_saved_credentials(self):
        self.settings.remove("remember_user")
        self.settings.remove("username")
        self.settings.remove("password")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.offset = event.pos()
        else: super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == Qt.LeftButton: self.move(self.pos() + event.pos() - self.offset)
        else: super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.offset = None
        super().mouseReleaseEvent(event)

    def validate_inputs(self):
        self.login_button.setEnabled(bool(self.login_edit.text().strip() and self.senha_edit.text().strip()))
        
    def show_error_message(self, title, text):
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(text)
        error_dialog.setIcon(QMessageBox.Warning)
        # Estilo do QMessageBox também pode usar as cores do tema
        bg_color = self.theme_colors.get('bg_color', '#ffffff')
        text_color = self.theme_colors.get('text_color', '#1d1d1f')
        accent_color = self.theme_colors.get('accent_color', '#007AFF')
        border_color = self.theme_colors.get('border_color', '#d2d2d7')
        
        error_dialog.setStyleSheet(f"""
            QMessageBox {{ background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 8px; }}
            QMessageBox QLabel {{ color: {text_color}; font-family: -apple-system, system-ui, sans-serif; font-size: 14px; }}
            QPushButton {{ background-color: {accent_color}; color: white; border: none; border-radius: 6px; padding: 8px 20px; font-weight: 500; min-width: 80px; }}
            QPushButton:hover {{ background-color: #005bb5; }}
        """)
        error_dialog.exec_()

    # Modificação 8: Atualizar ícones de olho com IconManager
    def update_password_toggle_icon(self):
        icon_color = self.theme_colors.get('text_secondary', '#6e6e73')
        icon_name = "eye-off" if self.password_visible else "eye"
        icon = IconManager.get_icon(icon_name, color=icon_color)
        self.toggle_password_button.setIcon(icon)
        self.toggle_password_button.setIconSize(QSize(20, 20))

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        self.senha_edit.setEchoMode(QLineEdit.Normal if self.password_visible else QLineEdit.Password)
        self.update_password_toggle_icon()


#==============================================================================
# CLASSE DA JANELA DE RECUPERAÇÃO DE SENHA
#==============================================================================
class PasswordRecoveryDialog(QDialog):
    # Recebe theme_colors
    def __init__(self, db_manager, theme_colors, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.theme_colors = theme_colors
        self.username_to_recover = None
        self.recovery_code = None

        self.setWindowTitle("Recuperação de Senha")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(400, 450)
        # Aplica stylesheet dinâmico
        self.setStyleSheet(self.get_stylesheet())

        base_layout = QVBoxLayout(self)
        base_layout.setContentsMargins(20, 20, 20, 20)
        container = QFrame(self)
        container.setObjectName("container")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30); shadow.setXOffset(0); shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 80))
        container.setGraphicsEffect(shadow)
        base_layout.addWidget(container)
        
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(30, 20, 30, 30)

        header_layout = QHBoxLayout()
        title_label = QLabel("Recuperar Senha")
        title_label.setObjectName("titleLabel")
        close_button = QToolButton()
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(28, 28)
        # Usa IconManager
        close_button.setIcon(IconManager.get_icon('fechar', self.theme_colors['text_secondary']))
        close_button.setIconSize(QSize(12, 12))
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        close_button.clicked.connect(self.reject)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_button)
        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.addWidget(self._create_step1_widget())
        self.stacked_widget.addWidget(self._create_step2_widget())
        self.stacked_widget.addWidget(self._create_step3_widget())
        main_layout.addWidget(self.stacked_widget)

    # ... (o resto da PasswordRecoveryDialog segue a mesma lógica de adaptação) ...
    # ... (omiti o resto para brevidade, mas você deve adaptar os métodos _create_stepX_widget)

    def get_stylesheet(self):
        bg_color = self.theme_colors.get('bg_color', '#ffffff')
        surface_color = self.theme_colors.get('surface_color', '#f5f5f7')
        text_color = self.theme_colors.get('text_color', '#1d1d1f')
        border_color = self.theme_colors.get('border_color', '#e5e5e5')
        accent_color = self.theme_colors.get('accent_color', '#007AFF')
        
        return f"""
            QDialog {{ background-color: transparent; }}
            #container {{ background-color: {bg_color}; border-radius: 12px; }}
            #titleLabel {{ font-size: 18px; font-weight: 600; color: {text_color}; }}
            #closeButton {{ background-color: {surface_color}; border-radius: 14px; }}
            QLabel {{ font-size: 14px; color: {text_color}; }}
            QLineEdit {{ 
                background-color: {surface_color}; 
                border: 1.5px solid {border_color}; 
                border-radius: 10px; padding: 12px; 
                font-size: 14px; color: {text_color};
            }}
            QLineEdit:focus {{ border-color: {accent_color}; }}
            #actionButton {{ 
                background-color: {accent_color}; 
                color: white; font-weight: 600; 
                padding: 12px; border-radius: 10px; border: none; 
            }}
            #actionButton:hover {{ background-color: #005bb5; }}
        """
    # Restante da classe PasswordRecoveryDialog...