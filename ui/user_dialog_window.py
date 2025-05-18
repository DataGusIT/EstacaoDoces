from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFormLayout, QComboBox,
                             QCheckBox, QGroupBox, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt
import hashlib

class UserDialogWindow(QDialog):
    """Diálogo para adicionar ou editar usuários"""
    
    def __init__(self, db_manager, usuario_id=None):
        super().__init__()
        
        self.db = db_manager
        self.usuario_id = usuario_id
        self.is_edit_mode = usuario_id is not None
        
        self.init_ui()
        
        if self.is_edit_mode:
            self.carregar_dados_usuario()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Adicionar Usuário" if not self.is_edit_mode else "Editar Usuário")
        self.setMinimumWidth(400)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Formulário
        form_layout = QFormLayout()
        
        # Campos do formulário
        self.nome_edit = QLineEdit()
        self.login_edit = QLineEdit()
        
        # Campos de senha - só obrigatórios em modo de adicionar
        senha_group = QGroupBox("Senha" if not self.is_edit_mode else "Alterar Senha")
        senha_layout = QVBoxLayout()
        
        self.senha_edit = QLineEdit()
        self.senha_edit.setEchoMode(QLineEdit.Password)
        self.confirmar_senha_edit = QLineEdit()
        self.confirmar_senha_edit.setEchoMode(QLineEdit.Password)
        
        senha_form = QFormLayout()
        senha_form.addRow("Senha:", self.senha_edit)
        senha_form.addRow("Confirmar Senha:", self.confirmar_senha_edit)
        
        # Checkbox para indicar se quer alterar a senha no modo de edição
        if self.is_edit_mode:
            self.alterar_senha_check = QCheckBox("Alterar senha")
            self.alterar_senha_check.setChecked(False)
            self.alterar_senha_check.toggled.connect(self.toggle_senha_fields)
            senha_layout.addWidget(self.alterar_senha_check)
            self.senha_edit.setEnabled(False)
            self.confirmar_senha_edit.setEnabled(False)
        
        senha_layout.addLayout(senha_form)
        senha_group.setLayout(senha_layout)
        
        # Outros campos
        self.email_edit = QLineEdit()
        
        # Tipo de usuário
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Comum", "comum")
        self.tipo_combo.addItem("Administrador", "admin")
        
        # Status (apenas no modo de edição)
        if self.is_edit_mode:
            self.status_group = QGroupBox("Status")
            status_layout = QHBoxLayout()
            
            self.ativo_radio = QRadioButton("Ativo")
            self.inativo_radio = QRadioButton("Inativo")
            
            status_layout.addWidget(self.ativo_radio)
            status_layout.addWidget(self.inativo_radio)
            
            self.status_group.setLayout(status_layout)
        
        # Adicionar campos ao formulário
        form_layout.addRow("Nome:", self.nome_edit)
        form_layout.addRow("Login:", self.login_edit)
        form_layout.addRow("Email:", self.email_edit)
        form_layout.addRow("Tipo:", self.tipo_combo)
        
        if self.is_edit_mode:
            form_layout.addRow(self.status_group)
        
        # Botões
        buttons_layout = QHBoxLayout()
        
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject)
        
        self.save_button = QPushButton("Salvar")
        self.save_button.clicked.connect(self.salvar_usuario)
        
        buttons_layout.addWidget(self.cancel_button)
        buttons_layout.addWidget(self.save_button)
        
        # Adicionar ao layout principal
        main_layout.addLayout(form_layout)
        main_layout.addWidget(senha_group)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def toggle_senha_fields(self, checked):
        """Habilita/desabilita os campos de senha no modo de edição"""
        self.senha_edit.setEnabled(checked)
        self.confirmar_senha_edit.setEnabled(checked)
        
        if not checked:
            self.senha_edit.setText("")
            self.confirmar_senha_edit.setText("")
    
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
        
        # No modo de edição
        if self.is_edit_mode:
            # Determinar status
            ativo = 1 if self.ativo_radio.isChecked() else 0
            
            # Atualizar dados básicos
            result, message = self.db.atualizar_usuario(
                self.usuario_id, nome, login, email, tipo, ativo
            )
            
            # Se escolheu alterar senha
            if result and hasattr(self, 'alterar_senha_check') and self.alterar_senha_check.isChecked():
                senha = self.senha_edit.text()
                senha_result, senha_message = self.db.alterar_senha_usuario(self.usuario_id, senha)
                
                if not senha_result:
                    QMessageBox.warning(self, "Aviso", f"Dados salvos, mas houve um erro ao alterar a senha: {senha_message}")
        else:
            # Adicionar novo usuário
            senha = self.senha_edit.text()
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            
            result, message = self.db.cadastrar_usuario(nome, login, senha_hash, email, tipo)
        
        if result:
            QMessageBox.information(self, "Sucesso", message)
            self.accept()
        else:
            QMessageBox.critical(self, "Erro", message)
            
# Adicionar alias para compatibilidade
UserDialog = UserDialogWindow