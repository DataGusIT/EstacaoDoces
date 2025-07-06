import base64
import random
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QCheckBox, QFrame,
                             QGraphicsDropShadowEffect, QToolButton, QStackedWidget)
from PyQt5.QtCore import (Qt, pyqtSignal, QSize, QSettings, QPropertyAnimation, 
                          QSequentialAnimationGroup, QPoint, QEasingCurve)
from PyQt5.QtGui import QIcon, QPixmap, QColor, QFont, QCursor

# Ícone de checkmark (SVG branco) codificado em Base64 para o QCheckBox
CHECK_ICON_BASE64 = "data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjMiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI+PHBvbHlsaW5lIHBvaW50cz0iMjAgNiA5IDE3IDQgMTIiPjwvcG9seWxpbmU+PC9zdmc+"


#==============================================================================
# CLASSE DA JANELA DE LOGIN PRINCIPAL
#==============================================================================
class LoginWindow(QDialog):
    login_success_signal = pyqtSignal(dict)

    def __init__(self, db_manager):
        super().__init__()
        self.db = db_manager
        self.usuario = None
        self.offset = None
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
        self.setStyleSheet(self.get_stylesheet())
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignTop | Qt.AlignRight)
        close_button = QToolButton()
        close_button.setObjectName("closeButton")
        close_button.setFixedSize(28, 28)
        close_button.setIcon(QIcon("assets/icons/marca-x.png"))
        close_button.setIconSize(QSize(12, 12))
        close_button.setCursor(QCursor(Qt.PointingHandCursor))
        close_button.setToolTip("Fechar")
        close_button.clicked.connect(self.reject)
        header_layout.addWidget(close_button)
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        title_layout.setContentsMargins(0, 0, 0, 30)
        logo_label = QLabel()
        logo_pixmap = QPixmap("assets/img/GestorX.png")
        if not logo_pixmap.isNull():
            logo_pixmap = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("GX")
            logo_label.setFont(QFont("Arial", 40, QFont.Bold))
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
        user_label_widget = self._create_field_label_with_icon("assets/icons/usuario.png", "USUÁRIO")
        self.login_edit = QLineEdit()
        self.login_edit.setPlaceholderText("Digite seu nome de usuário")
        self.login_edit.textChanged.connect(self.validate_inputs)
        senha_label_widget = self._create_field_label_with_icon("assets/icons/cadeado.png", "SENHA")
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

    def _create_field_label_with_icon(self, icon_path, text):
        widget = QFrame()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(6)
        icon_label = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon_label.setPixmap(pixmap.scaled(14, 14, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        text_label = QLabel(text)
        text_label.setObjectName("fieldLabel")
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        return widget

    def get_stylesheet(self):
        return f"""
            #loginContainer {{ background-color: #ffffff; border-radius: 16px; }}
            #titleLabel {{ font-family: -apple-system, system-ui, sans-serif; font-size: 26px; font-weight: 600; color: #1d1d1f; }}
            #subtitleLabel {{ font-family: -apple-system, system-ui, sans-serif; font-size: 15px; color: #86868b; }}
            #fieldLabel {{ font-family: -apple-system, system-ui, sans-serif; font-size: 11px; font-weight: 600; color: #6e6e73; padding-left: 3px; letter-spacing: 0.5px; }}
            QLineEdit {{ background-color: #f5f5f7; border: 1.5px solid #e5e5e5; border-radius: 10px; padding: 13px 15px; font-size: 15px; color: #1d1d1f; }}
            QLineEdit:focus {{ border-color: #007AFF; background-color: #ffffff; }}
            #inputContainer {{ border-radius: 10px; background-color: #f5f5f7; border: 1.5px solid #e5e5e5; }}
            #inputContainer:focus-within {{ border-color: #007AFF; background-color: #ffffff; }}
            #inputContainer QLineEdit {{ border: none; background-color: transparent; }}
            #togglePasswordButton {{ background-color: transparent; border: none; padding: 8px; }}
            #loginButton {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #2c2c2e, stop:1 #000000); color: #ffffff; font-size: 14px; font-weight: 600; padding: 16px; border-radius: 12px; border: none; }}
            #loginButton:hover {{ background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3d3d3f, stop:1 #111111); }}
            #loginButton:pressed {{ background-color: #000000; }}
            #loginButton:disabled {{ background: #e5e5e5; color: #b0b0b0; }}
            #closeButton {{ background-color: #f0f0f0; border: none; border-radius: 14px; }}
            #closeButton:hover {{ background-color: #e0e0e0; }}
            #closeButton:pressed {{ background-color: #d0d0d0; }}
            QCheckBox {{ font-size: 13px; color: #333333; spacing: 8px; }}
            QCheckBox::indicator {{ width: 18px; height: 18px; border: 1.5px solid #d2d2d7; border-radius: 6px; background-color: #ffffff; }}
            QCheckBox::indicator:hover {{ border-color: #b0b0b0; }}
            QCheckBox::indicator:checked {{ background-color: #007AFF; border-color: #007AFF; image: url({CHECK_ICON_BASE64}); }}
            #forgotPasswordLabel a {{ color: #007AFF; text-decoration: none; font-size: 13px; font-weight: 500; }}
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

    # ###########################################################
    # ## AQUI ESTÁ A CORREÇÃO PRINCIPAL ##
    # ###########################################################
    def handle_forgot_password(self):
        """Lida com o clique no link 'Esqueci minha senha'."""
        recovery_dialog = PasswordRecoveryDialog(self.db, self)
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
        error_dialog.setStyleSheet("""
            QMessageBox { background-color: #ffffff; border: 1px solid #d2d2d7; border-radius: 8px; }
            QMessageBox QLabel { color: #1d1d1f; font-family: -apple-system, system-ui, sans-serif; font-size: 14px; }
            QPushButton { background-color: #007AFF; color: white; border: none; border-radius: 6px; padding: 8px 20px; font-weight: 500; min-width: 80px; }
            QPushButton:hover { background-color: #005bb5; }
        """)
        error_dialog.exec_()

    def update_password_toggle_icon(self):
        icon_path = "assets/icons/olho_fechado.png" if self.password_visible else "assets/icons/olho.png"
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            self.toggle_password_button.setIcon(QIcon(pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)))
            self.toggle_password_button.setIconSize(QSize(20, 20))

    def toggle_password_visibility(self):
        self.password_visible = not self.password_visible
        self.senha_edit.setEchoMode(QLineEdit.Normal if self.password_visible else QLineEdit.Password)
        self.update_password_toggle_icon()


#==============================================================================
# CLASSE DA JANELA DE RECUPERAÇÃO DE SENHA
#==============================================================================
class PasswordRecoveryDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.username_to_recover = None
        self.recovery_code = None

        self.setWindowTitle("Recuperação de Senha")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMinimumSize(400, 450)
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
        close_button.setIcon(QIcon("assets/icons/marca-x.png"))
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

    def _create_step1_widget(self):
        widget = QFrame()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)
        info_label = QLabel("Digite seu nome de usuário ou e-mail para iniciar a recuperação.")
        info_label.setWordWrap(True)
        self.step1_username_edit = QLineEdit()
        self.step1_username_edit.setPlaceholderText("Usuário ou e-mail")
        continue_button = QPushButton("Continuar")
        continue_button.setObjectName("actionButton")
        continue_button.setCursor(QCursor(Qt.PointingHandCursor))
        continue_button.clicked.connect(self._handle_step1_continue)
        layout.addWidget(info_label)
        layout.addWidget(self.step1_username_edit)
        layout.addStretch()
        layout.addWidget(continue_button)
        return widget

    def _handle_step1_continue(self):
        identificador = self.step1_username_edit.text().strip()
        if not identificador:
            self.show_message("Atenção", "Por favor, insira um nome de usuário ou e-mail.")
            return
        username_encontrado = self.db.verificar_usuario_por_login_ou_email(identificador)
        if username_encontrado:
            self.username_to_recover = username_encontrado
            self.recovery_code = str(random.randint(100000, 999999))
            QMessageBox.information(self, "Código de Recuperação", 
                                    f"Um código de recuperação foi gerado para o usuário '{self.username_to_recover}'.\n\n"
                                    f"Seu código é: {self.recovery_code}\n\n"
                                    f"(Em um aplicativo real, isso seria enviado para seu e-mail.)")
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.show_message("Erro", "Nenhum usuário ativo encontrado com este login ou e-mail.")

    def _create_step2_widget(self):
        widget = QFrame()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)
        info_label = QLabel("Um código de 6 dígitos foi gerado. Por favor, insira-o abaixo.")
        info_label.setWordWrap(True)
        self.step2_code_edit = QLineEdit()
        self.step2_code_edit.setPlaceholderText("Código de 6 dígitos")
        verify_button = QPushButton("Verificar Código")
        verify_button.setObjectName("actionButton")
        verify_button.setCursor(QCursor(Qt.PointingHandCursor))
        verify_button.clicked.connect(self._handle_step2_verify)
        layout.addWidget(info_label)
        layout.addWidget(self.step2_code_edit)
        layout.addStretch()
        layout.addWidget(verify_button)
        return widget

    def _handle_step2_verify(self):
        code = self.step2_code_edit.text().strip()
        if code == self.recovery_code:
            self.stacked_widget.setCurrentIndex(2)
            self.step3_new_password_edit.setFocus()
        else:
            self.show_message("Erro", "Código de recuperação incorreto.")
    
    def _create_step3_widget(self):
        widget = QFrame()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 10, 0, 0)
        layout.setSpacing(10)
        info_label = QLabel("Ótimo! Agora, defina sua nova senha.")
        self.step3_new_password_edit = QLineEdit()
        self.step3_new_password_edit.setPlaceholderText("Nova senha")
        self.step3_new_password_edit.setEchoMode(QLineEdit.Password)
        self.step3_confirm_password_edit = QLineEdit()
        self.step3_confirm_password_edit.setPlaceholderText("Confirme a nova senha")
        self.step3_confirm_password_edit.setEchoMode(QLineEdit.Password)
        reset_button = QPushButton("Redefinir Senha")
        reset_button.setObjectName("actionButton")
        reset_button.setCursor(QCursor(Qt.PointingHandCursor))
        reset_button.clicked.connect(self._handle_step3_reset)
        layout.addWidget(info_label)
        layout.addWidget(QLabel("Nova Senha:"))
        layout.addWidget(self.step3_new_password_edit)
        layout.addWidget(QLabel("Confirmar Senha:"))
        layout.addWidget(self.step3_confirm_password_edit)
        layout.addStretch()
        layout.addWidget(reset_button)
        return widget

    def _handle_step3_reset(self):
        new_pass = self.step3_new_password_edit.text()
        confirm_pass = self.step3_confirm_password_edit.text()
        if not new_pass or not confirm_pass:
            self.show_message("Atenção", "Ambos os campos de senha devem ser preenchidos.")
            return
        if new_pass != confirm_pass:
            self.show_message("Erro", "As senhas não coincidem.")
            return
        if len(new_pass) < 6:
            self.show_message("Atenção", "A senha deve ter pelo menos 6 caracteres.")
            return
        if self.db.atualizar_senha_por_login(self.username_to_recover, new_pass):
            self.show_message("Sucesso!", "Sua senha foi redefinida. Você já pode fazer login.", icon=QMessageBox.Information)
            self.accept()
        else:
            self.show_message("Erro Crítico", "Não foi possível atualizar a senha. Contate o suporte.")

    def show_message(self, title, text, icon=QMessageBox.Warning):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(text)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox { background-color: #ffffff; }
            QLabel { color: #1d1d1f; font-size: 14px; }
            QPushButton { background-color: #007AFF; color: white; border-radius: 6px; padding: 8px 20px; }
        """)
        msg_box.exec_()
    
    def get_stylesheet(self):
        return """
            QDialog { background-color: transparent; }
            #container { background-color: #ffffff; border-radius: 12px; }
            #titleLabel { font-size: 18px; font-weight: 600; color: #1d1d1f; }
            #closeButton { background-color: #f0f0f0; border-radius: 14px; }
            QLabel { font-size: 14px; color: #333333; }
            QLineEdit { background-color: #f5f5f7; border: 1.5px solid #e5e5e5; border-radius: 10px; padding: 12px; font-size: 14px; }
            QLineEdit:focus { border-color: #007AFF; }
            #actionButton { background-color: #007AFF; color: white; font-weight: 600; padding: 12px; border-radius: 10px; border: none; }
            #actionButton:hover { background-color: #005bb5; }
        """