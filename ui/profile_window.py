from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QMessageBox, QFormLayout,
                             QGroupBox, QFrame, QWidget, QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QPixmap, QRegExpValidator, QLinearGradient, QPainterPath, QFontDatabase
from PyQt5.QtCore import Qt, QSize, QRegExp, QPropertyAnimation, QEasingCurve, pyqtProperty, QPoint

class CustomLineEdit(QLineEdit):
    """Widget personalizado para campos de texto com animação de foco"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._highlight_color = QColor("#4361ee")
        self._normal_color = QColor("#dcdde1")
        self._current_color = self._normal_color
        
        # Configurações de estilo
        self.setFixedHeight(46)
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                background-color: white;
                font-size: 14px;
                color: #333333;
                selection-background-color: #4361ee33;
                selection-color: #333333;
            }
            QLineEdit:focus {
                border: 1px solid #4361ee;
                background-color: #f8faff;
            }
            QLineEdit:hover:!focus {
                border: 1px solid #c0c0c0;
            }
        """)
        
    def focusInEvent(self, event):
        """Animação ao receber foco"""
        super().focusInEvent(event)
        self._animate_border(self._highlight_color)
        
    def focusOutEvent(self, event):
        """Animação ao perder foco"""
        super().focusOutEvent(event)
        self._animate_border(self._normal_color)
        
    def _animate_border(self, target_color):
        """Anima a cor da borda"""
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {target_color.name()};
                border-radius: 8px;
                padding: 12px 16px;
                background-color: {QColor('#f8faff').name() if self.hasFocus() else 'white'};
                font-size: 14px;
                color: #333333;
                selection-background-color: #4361ee33;
                selection-color: #333333;
            }}
            QLineEdit:hover:!focus {{
                border: 1px solid #c0c0c0;
            }}
        """)


class FieldWidget(QWidget):
    """Widget personalizado para agrupar label e campo de entrada"""
    def __init__(self, label_text, edit_widget, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 12))
        label.setStyleSheet("color: #2d3748; font-weight: 500;")
        
        layout.addWidget(label)
        layout.addWidget(edit_widget)


class ProfileWindow(QDialog):
    def __init__(self, db, usuario):
        super().__init__()
        self.db = db
        self.usuario = usuario
        self.setWindowTitle("Meu Perfil")
        self.setFixedSize(650, 680)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # Card de perfil com efeito de sombra
        profile_card = QWidget()
        profile_card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        profile_card.setFixedHeight(160)
        profile_card.setObjectName("profileCard")
        profile_card.setStyleSheet("""
            #profileCard {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4361ee, stop:1 #3a0ca3);
                border-radius: 16px;
            }
        """)
        
        card_layout = QHBoxLayout(profile_card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        
        # Avatar (círculo com gradiente)
        avatar_container = QWidget()
        avatar_container.setFixedSize(120, 120)
        avatar_container.setObjectName("avatarContainer")
        avatar_container.setStyleSheet("""
            #avatarContainer {
                background-color: transparent;
            }
        """)
        
        avatar_layout = QVBoxLayout(avatar_container)
        avatar_layout.setAlignment(Qt.AlignCenter)
        avatar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Círculo do avatar com gradiente
        avatar_circle = QFrame(avatar_container)
        avatar_circle.setFixedSize(110, 110)
        avatar_circle.setObjectName("avatarCircle")
        avatar_circle.setStyleSheet("""
            #avatarCircle {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4cc9f0, stop:1 #4895ef);
                border-radius: 55px;
                border: 4px solid white;
            }
        """)
        
        # Iniciais do usuário
        iniciais = "".join([nome[0].upper() for nome in self.usuario['nome'].split()[:2]])
        iniciais_label = QLabel(iniciais, avatar_circle)
        iniciais_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        iniciais_label.setStyleSheet("color: white;")
        iniciais_label.setAlignment(Qt.AlignCenter)
        iniciais_label.resize(avatar_circle.size())
        
        # Informações do usuário
        info_container = QWidget()
        info_layout = QVBoxLayout(info_container)
        info_layout.setContentsMargins(10, 8, 0, 8)
        info_layout.setSpacing(8)
        
        nome_label = QLabel(self.usuario['nome'])
        nome_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        nome_label.setStyleSheet("color: white;")
        
        tipo_label = QLabel(f"Perfil: {self.usuario['tipo'].capitalize()}")
        tipo_label.setFont(QFont("Segoe UI", 15))
        tipo_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        login_label = QLabel(f"@{self.usuario['login']}")
        login_label.setFont(QFont("Segoe UI", 13))
        login_label.setStyleSheet("color: rgba(255, 255, 255, 0.85);")
        
        info_layout.addWidget(nome_label)
        info_layout.addWidget(tipo_label)
        info_layout.addWidget(login_label)
        
        card_layout.addWidget(avatar_container)
        card_layout.addWidget(info_container, 1)
        
        main_layout.addWidget(profile_card)
        
        # Título da seção
        section_title = QLabel("Informações Pessoais")
        section_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        section_title.setStyleSheet("color: #2d3748; margin-top: 8px;")
        section_title.setAlignment(Qt.AlignLeft)
        main_layout.addWidget(section_title)
        
        # Linha decorativa com gradiente
        decorative_line = QFrame()
        decorative_line.setFrameShape(QFrame.HLine)
        decorative_line.setFrameShadow(QFrame.Sunken)
        decorative_line.setFixedHeight(3)
        decorative_line.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4361ee, stop:1 #3a0ca3);
            border: none;
            margin-bottom: 16px;
        """)
        main_layout.addWidget(decorative_line)
        
        # Formulário de informações
        form_container = QWidget()
        form_container.setObjectName("formContainer")
        form_container.setStyleSheet("""
            #formContainer {
                background-color: white;
                border-radius: 12px;
                margin: 0;
                padding: 0;
                border: 1px solid #e0e0e0;
            }
        """)
        
        form_layout = QVBoxLayout(form_container)
        form_layout.setSpacing(24)
        form_layout.setContentsMargins(25, 25, 25, 25)
        
        # Campo Nome
        self.name_edit = CustomLineEdit(self.usuario['nome'])
        self.name_edit.setPlaceholderText("Digite seu nome completo")
        nome_field = FieldWidget("Nome completo:", self.name_edit)
        
        # Campo Login
        self.login_edit = CustomLineEdit(self.usuario['login'])
        self.login_edit.setReadOnly(True)
        self.login_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 12px 16px;
                background-color: #f5f5f5;
                font-size: 14px;
                color: #777777;
            }
        """)
        login_field = FieldWidget("Nome de usuário:", self.login_edit)
        
        # Campo Email
        self.email_edit = CustomLineEdit(self.usuario.get('email', ''))
        self.email_edit.setPlaceholderText("Digite seu email")
        
        # Email regex validation
        email_regex = QRegExp(r"[^@]+@[^@]+\.[a-zA-Z]{2,}")
        email_validator = QRegExpValidator(email_regex)
        self.email_edit.setValidator(email_validator)
        email_field = FieldWidget("E-mail:", self.email_edit)
        
        # Adicionar campos ao formulário
        form_layout.addWidget(nome_field)
        form_layout.addWidget(login_field)
        form_layout.addWidget(email_field)
        
        main_layout.addWidget(form_container)
        
        # Estrutura para botões
        buttons_container = QWidget()
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        buttons_layout.setSpacing(15)
        
        # Botões de ação com design moderno
        # 1. Cancelar
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setFixedHeight(50)
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.setStyleSheet("""
            #cancelButton {
                background-color: #f8f9fa;
                color: #e53e3e;
                border: 1px solid #e53e3e;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 25px;
            }
            #cancelButton:hover {
                background-color: #fff5f5;
            }
            #cancelButton:pressed {
                background-color: #fed7d7;
            }
        """)
        
        # 2. Alterar senha
        self.change_password_button = QPushButton("Alterar Senha")
        self.change_password_button.setFixedHeight(50)
        self.change_password_button.setCursor(Qt.PointingHandCursor)
        self.change_password_button.setObjectName("changePasswordButton")
        self.change_password_button.setStyleSheet("""
            #changePasswordButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 25px;
            }
            #changePasswordButton:hover {
                background-color: #00c6fb;
            }
            #changePasswordButton:pressed {
                background-color: #0093e9;
            }
        """)
        
        # 3. Salvar
        self.save_button = QPushButton("Salvar Alterações")
        self.save_button.setFixedHeight(50)
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setObjectName("saveButton")
        self.save_button.setStyleSheet("""
            #saveButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4361ee, stop:1 #3a0ca3);
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                padding: 0 25px;
            }
            #saveButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3a56e8, stop:1 #2f0a87);
            }
            #saveButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #304cce, stop:1 #260873);
            }
        """)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.change_password_button)
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addWidget(buttons_container)
        
        # Adicionar um espaçador flexível para alinhar o conteúdo
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
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
            self.show_message("Campo obrigatório", "O nome não pode ficar em branco.", QMessageBox.Warning)
            return
        
        if email and not self.email_edit.hasAcceptableInput():
            self.show_message("Email inválido", "Por favor, insira um email válido.", QMessageBox.Warning)
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
            
            self.show_message("Perfil atualizado", "Suas informações foram atualizadas com sucesso.")
            self.accept()
        except Exception as e:
            self.show_message("Erro", f"Erro ao atualizar perfil: {str(e)}", QMessageBox.Critical)
    
    def open_change_password(self):
        """Abrir diálogo para alterar senha"""
        from ui.change_password_window import ChangePasswordWindow
        password_dialog = ChangePasswordWindow(self.db, self.usuario['id'])
        password_dialog.exec_()
    
    def show_message(self, title, message, icon=QMessageBox.Information):
        """Exibir mensagem personalizada"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setIcon(icon)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: white;
                color: #333333;
                border-radius: 8px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4361ee, stop:1 #3a0ca3);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                min-width: 80px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3a56e8, stop:1 #2f0a87);
            }
        """)
        msg_box.exec_()
    
    def paintEvent(self, event):
        """Personaliza o fundo da janela com um gradiente moderno"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Gradiente de fundo
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor("#f9f9ff"))
        gradient.setColorAt(1, QColor("#f0f0ff"))
        painter.fillRect(self.rect(), QBrush(gradient))