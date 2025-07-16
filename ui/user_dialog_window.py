from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFormLayout, QComboBox,
                             QCheckBox, QGroupBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
import hashlib 

class UserDialogWindow(QDialog):
    """Diálogo para adicionar ou editar usuários"""
    
    def __init__(self, db_manager, theme_colors, usuario_id=None):
        super().__init__()
        self.db = db_manager
        self.theme_colors = theme_colors
        self.usuario_id = usuario_id
        self.is_edit_mode = usuario_id is not None
        
        self.init_ui()
        self.apply_styles() # Aplica o tema
        
        if self.is_edit_mode:
            self.carregar_dados_usuario()
    
    def init_ui(self):
        self.setWindowTitle("Adicionar Usuário" if not self.is_edit_mode else "Editar Usuário")
        self.setMinimumWidth(450)
        
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setSpacing(10)
        
        self.nome_edit = QLineEdit()
        self.login_edit = QLineEdit()
        self.email_edit = QLineEdit()
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Comum", "Administrador"])
        
        form_layout.addRow("Nome Completo:", self.nome_edit)
        form_layout.addRow("Nome de Usuário (login):", self.login_edit)
        form_layout.addRow("E-mail:", self.email_edit)
        form_layout.addRow("Tipo de Conta:", self.tipo_combo)

        senha_group = QGroupBox("Senha" if not self.is_edit_mode else "Alterar Senha")
        senha_layout = QFormLayout()
        self.senha_edit = QLineEdit()
        self.senha_edit.setEchoMode(QLineEdit.Password)
        self.confirmar_senha_edit = QLineEdit()
        self.confirmar_senha_edit.setEchoMode(QLineEdit.Password)
        senha_layout.addRow("Nova Senha:", self.senha_edit)
        senha_layout.addRow("Confirmar Senha:", self.confirmar_senha_edit)
        senha_group.setLayout(senha_layout)
        
        if self.is_edit_mode:
            self.alterar_senha_check = QCheckBox("Marque para alterar a senha")
            self.alterar_senha_check.toggled.connect(self.toggle_senha_fields)
            senha_layout.insertRow(0, self.alterar_senha_check)
            self.toggle_senha_fields(False)
        
        buttons_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        self.save_button = QPushButton("Salvar")
        self.save_button.setObjectName("primaryButton") # Para estilo especial
        self.save_button.clicked.connect(self.salvar_usuario)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        main_layout.addLayout(form_layout)
        main_layout.addWidget(senha_group)
        main_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        self.setLayout(main_layout)

    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg_color']};
                color: {colors['text_color']};
                font-size: 10pt;
            }}
            QLineEdit, QComboBox {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px;
                border-radius: 6px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border: 1px solid {colors['accent_color']};
            }}
            QGroupBox {{
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 6px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }}
            QPushButton {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px 16px;
                border-radius: 6px;
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

    def toggle_senha_fields(self, checked):
        self.senha_edit.setEnabled(checked)
        self.confirmar_senha_edit.setEnabled(checked)
        if not checked:
            self.senha_edit.clear()
            self.confirmar_senha_edit.clear()
    
    def carregar_dados_usuario(self):
        """Carrega os dados do usuário para edição"""
        usuario = self.db.obter_usuario_por_id(self.usuario_id)
        
        if not usuario:
            QMessageBox.critical(self, "Erro", "Usuário não encontrado.")
            self.reject()
            return
        
        # Preencher os campos
        self.nome_edit.setText(usuario['nome'])
        self.login_edit.setText(usuario['login'])
        self.email_edit.setText(usuario['email'] if usuario['email'] else "")
        
        # Selecionar o tipo
        index = self.tipo_combo.findData(usuario['tipo'])
        if index >= 0:
            self.tipo_combo.setCurrentIndex(index)
        
        # Selecionar o status
        if hasattr(self, 'ativo_radio'):
            if usuario.get('ativo', 1) == 1:
                self.ativo_radio.setChecked(True)
            else:
                self.inativo_radio.setChecked(True)
    
    def validar_campos(self):
        """Valida os campos do formulário"""
        nome = self.nome_edit.text().strip()
        login = self.login_edit.text().strip()
        senha = self.senha_edit.text()
        confirmar_senha = self.confirmar_senha_edit.text()
        
        # Validar campos obrigatórios
        if not nome:
            QMessageBox.warning(self, "Campos obrigatórios", "O nome é obrigatório.")
            return False
        
        if not login:
            QMessageBox.warning(self, "Campos obrigatórios", "O login é obrigatório.")
            return False
        
        # Validar senha no modo de adicionar ou se escolheu alterar senha
        if not self.is_edit_mode or (self.is_edit_mode and hasattr(self, 'alterar_senha_check') and self.alterar_senha_check.isChecked()):
            if not senha:
                QMessageBox.warning(self, "Campos obrigatórios", "A senha é obrigatória.")
                return False
            
            if senha != confirmar_senha:
                QMessageBox.warning(self, "Senhas diferentes", "As senhas não coincidem.")
                return False
        
        return True
    
    def salvar_usuario(self):
        """Salva o usuário no banco de dados"""
        if not self.validar_campos():
            return

        nome = self.nome_edit.text().strip()
        login = self.login_edit.text().strip()
        email = self.email_edit.text().strip()
        tipo = self.tipo_combo.currentData()
        
        try:
            if self.is_edit_mode:
                # ... (a lógica de edição já está correta, pois chama `alterar_senha_usuario` que já faz o hash)
                # O código abaixo permanece o mesmo
                ativo = 1 if self.ativo_radio.isChecked() else 0
                result, message = self.db.atualizar_usuario(self.usuario_id, nome, login, email, tipo, ativo)

                if not result:
                    QMessageBox.critical(self, "Erro", message)
                    return
                
                if hasattr(self, 'alterar_senha_check') and self.alterar_senha_check.isChecked():
                    senha = self.senha_edit.text()
                    senha_result, senha_message = self.db.alterar_senha_usuario(self.usuario_id, senha)
                    
                    if not senha_result:
                        QMessageBox.warning(self, "Aviso", f"Dados salvos, mas houve um erro ao alterar a senha: {senha_message}")
            else:
                # ###########################################################
                # ## AQUI ESTÁ A CORREÇÃO PRINCIPAL ##
                # ###########################################################
                
                # Adicionar novo usuário
                senha_plana = self.senha_edit.text()
                
                # 1. Faz o hash da senha antes de enviar para o banco
                senha_hash = hashlib.sha256(senha_plana.encode('utf-8')).hexdigest()

                # 2. Passa o hash para a função do banco de dados
                result, message = self.db.cadastrar_usuario(nome, login, senha_hash, email, tipo)
                
                if not result:
                    QMessageBox.critical(self, "Erro", message)
                    return

            # Se tudo ocorreu bem
            QMessageBox.information(self, "Sucesso", "Operação realizada com sucesso!")
            self.accept()

        except Exception as e:
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro: {str(e)}")
    
    def get_username(self):
        """Função auxiliar para retornar o nome de usuário após o cadastro."""
        return self.login_edit.text().strip()
            
# Adicionar alias para compatibilidade
UserDialog = UserDialogWindow