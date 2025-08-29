# Arquivo: ui/user_dialog_window.py (VERSÃO CORRIGIDA E APRIMORADA)

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QFormLayout, QComboBox, QGroupBox, 
                             QRadioButton, QCheckBox)
from PyQt5.QtCore import Qt
import hashlib

# Importa o AlertDialog que já definimos em outros arquivos
# Certifique-se que o caminho do import esteja correto para sua estrutura
from .admin_window import AlertDialog 
from .icon_manager import IconManager

class UserDialogWindow(QDialog):
    """Diálogo aprimorado para adicionar ou editar usuários."""
    
    def __init__(self, db_manager, theme_colors, usuario_id=None, parent=None):
        super().__init__(parent)
        self.db = db_manager
        self.theme_colors = theme_colors
        self.usuario_id = usuario_id
        self.is_edit_mode = usuario_id is not None
        
        self.init_ui()
        self.apply_styles()
        
        if self.is_edit_mode:
            self.carregar_dados_usuario()
    
    def init_ui(self):
        self.setWindowTitle("Adicionar Novo Usuário" if not self.is_edit_mode else "Editar Usuário")
        self.setMinimumWidth(450)
        
        main_layout = QVBoxLayout(self)
        form_group = QGroupBox("Dados do Usuário")
        form_layout = QFormLayout(form_group)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        self.nome_edit = QLineEdit()
        self.login_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Comum", "Admin"]) # Corrigido para "Admin" para consistência
        
        form_layout.addRow("Nome Completo:", self.nome_edit)
        form_layout.addRow("Nome de Usuário (login):", self.login_edit)
        form_layout.addRow("E-mail:", self.email_edit)
        form_layout.addRow("Tipo de Conta:", self.tipo_combo)

        # --- CORREÇÃO 1: ADICIONANDO O CAMPO DE STATUS ---
        status_group = QGroupBox("Status")
        status_layout = QHBoxLayout(status_group)
        self.ativo_radio = QRadioButton("Ativo")
        self.inativo_radio = QRadioButton("Inativo")
        self.ativo_radio.setChecked(True) # Padrão
        status_layout.addWidget(self.ativo_radio)
        status_layout.addWidget(self.inativo_radio)
        form_layout.addRow(status_group)
        # --- FIM DA CORREÇÃO 1 ---
        
        senha_group = QGroupBox("Senha" if not self.is_edit_mode else "Alterar Senha")
        senha_layout = QFormLayout(senha_group)
        self.senha_edit = QLineEdit(); self.senha_edit.setEchoMode(QLineEdit.Password)
        self.confirmar_senha_edit = QLineEdit(); self.confirmar_senha_edit.setEchoMode(QLineEdit.Password)
        
        if self.is_edit_mode:
            self.alterar_senha_check = QCheckBox("Marque para alterar a senha")
            self.alterar_senha_check.toggled.connect(self.toggle_senha_fields)
            senha_layout.addRow(self.alterar_senha_check)
            self.toggle_senha_fields(False)

        senha_layout.addRow("Nova Senha:", self.senha_edit)
        senha_layout.addRow("Confirmar Senha:", self.confirmar_senha_edit)
        
        buttons_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton("Salvar")
        self.save_button.setObjectName("primaryButton")
        self.save_button.clicked.connect(self.salvar_usuario)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addWidget(form_group)
        main_layout.addWidget(senha_group)
        main_layout.addLayout(buttons_layout)

    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f"""
            QDialog {{ background-color: {colors['bg_color']}; color: {colors['text_color']}; }}
            QGroupBox, QLabel, QRadioButton, QCheckBox {{ color: {colors['text_color']}; }}
            QLineEdit, QComboBox {{ background-color: {colors['surface_color']}; color: {colors['text_color']}; border: 1px solid {colors['border_color']}; padding: 8px; border-radius: 6px; }}
            QLineEdit:focus, QComboBox:focus {{ border: 1px solid {colors['accent_color']}; }}
            QGroupBox {{ border: 1px solid {colors['border_color']}; border-radius: 6px; margin-top: 10px; padding: 10px; }}
            QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top left; padding: 0 5px; left: 10px; }}
            QPushButton {{ background-color: {colors['surface_color']}; color: {colors['text_color']}; border: 1px solid {colors['border_color']}; padding: 8px 16px; border-radius: 6px; font-weight: bold; }}
            QPushButton:hover {{ border-color: {colors['accent_color']}; }}
            #primaryButton {{ background-color: {colors['accent_color']}; color: white; border: none; }}
        """)
        self.save_button.setIcon(IconManager.get_icon('save', 'white'))
        self.cancel_button.setIcon(IconManager.get_icon('cancel', colors['text_color']))

    def toggle_senha_fields(self, checked):
        self.senha_edit.setEnabled(checked)
        self.confirmar_senha_edit.setEnabled(checked)
        if not checked:
            self.senha_edit.clear(); self.confirmar_senha_edit.clear()
    
    def carregar_dados_usuario(self):
        usuario = self.db.obter_usuario_por_id(self.usuario_id)
        if not usuario:
            AlertDialog(self, "Erro", "Usuário não encontrado.", alert_type='error', theme_colors=self.theme_colors).exec_()
            self.reject(); return
        
        self.nome_edit.setText(usuario['nome'])
        self.login_edit.setText(usuario['login'])
        self.email_edit.setText(usuario.get('email', ''))
        
        index = self.tipo_combo.findText(usuario['tipo'], Qt.MatchFixedString)
        if index >= 0: self.tipo_combo.setCurrentIndex(index)
        
        # --- CORREÇÃO 2: CARREGANDO O STATUS CORRETO ---
        if usuario.get('ativo', 1) == 1:
            self.ativo_radio.setChecked(True)
        else:
            self.inativo_radio.setChecked(True)
        # --- FIM DA CORREÇÃO 2 ---
    
    def salvar_usuario(self):
        nome = self.nome_edit.text().strip()
        login = self.login_edit.text().strip()
        
        if not nome or not login:
            AlertDialog(self, "Campos Obrigatórios", "Nome e Login são obrigatórios.", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        dados = {
            'nome': nome,
            'login': login,
            'email': self.email_edit.text().strip(),
            'tipo': self.tipo_combo.currentText(),
            # --- CORREÇÃO 3: LENDO O STATUS DOS RADIO BUTTONS ---
            'ativo': 1 if self.ativo_radio.isChecked() else 0
        }
        
        senha = self.senha_edit.text()
        alterar_senha = not self.is_edit_mode or self.alterar_senha_check.isChecked()

        if alterar_senha:
            if len(senha) < 6:
                AlertDialog(self, "Senha Inválida", "A senha deve ter no mínimo 6 caracteres.", alert_type='warning', theme_colors=self.theme_colors).exec_()
                return
            if senha != self.confirmar_senha_edit.text():
                AlertDialog(self, "Senhas Diferentes", "As senhas não coincidem.", alert_type='warning', theme_colors=self.theme_colors).exec_()
                return

        try:
            if self.is_edit_mode:
                sucesso, msg = self.db.atualizar_usuario(self.usuario_id, **dados)
                if sucesso and alterar_senha:
                    # Altera a senha separadamente se necessário
                    sucesso, msg = self.db.alterar_senha_usuario(self.usuario_id, senha)
                mensagem_sucesso = "Usuário atualizado com sucesso!"
            else:
                dados['senha'] = senha # Adiciona a senha para o novo usuário
                sucesso, msg = self.db.adicionar_usuario(**dados)
                mensagem_sucesso = "Usuário cadastrado com sucesso!"

            if sucesso:
                AlertDialog(self, "Sucesso", mensagem_sucesso, alert_type='success', theme_colors=self.theme_colors).exec_()
                self.accept()
            else:
                AlertDialog(self, "Erro no Banco de Dados", msg, alert_type='error', theme_colors=self.theme_colors).exec_()

        except Exception as e:
            AlertDialog(self, "Erro Inesperado", f"Ocorreu um erro: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()