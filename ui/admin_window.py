# admin_window.py

from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QWidget, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
                             QSpinBox, QDoubleSpinBox, QLineEdit, QComboBox, QDateEdit,
                             QInputDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QIcon
import hashlib

class AdminWindow(QDialog):
    """Janela de administração do sistema"""
    
    def __init__(self, db_manager, usuario):
        super().__init__()
        
        self.db = db_manager
        self.usuario = usuario
        
        if self.usuario.get('tipo') != 'admin':
            # Registrar tentativa de acesso indevido
            self.db.registrar_log('WARNING', self.usuario.get('login'), 
                                 'ACESSO_ADMIN', 'Tentativa de acesso não autorizado ao painel.')
            QMessageBox.warning(self, "Acesso Negado", "Você não tem permissão para acessar esta área.")
            self.reject()
            return
        
        self.init_ui()
        # Registrar acesso bem-sucedido
        self.db.registrar_log('ADMIN', self.usuario.get('login'), 'ACESSO_ADMIN', 'Acessou o painel de administração.')

    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Painel de Administração")
        self.setMinimumSize(900, 700)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        title_label = QLabel("Painel de Administração")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        
        self.tab_widget = QTabWidget()
        
        self.usuarios_tab = self.criar_tab_usuarios()
        self.tab_widget.addTab(self.usuarios_tab, "Gerenciar Usuários")
        
        self.config_tab = self.criar_tab_config()
        self.tab_widget.addTab(self.config_tab, "Configurações do Sistema")
        
        self.logs_tab = self.criar_tab_logs()
        self.tab_widget.addTab(self.logs_tab, "Logs de Atividades")
        
        buttons_layout = QHBoxLayout()
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(buttons_layout)

    # ===================================================================
    # ABA DE USUÁRIOS
    # ===================================================================
    def criar_tab_usuarios(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.usuarios_table = QTableWidget()
        self.usuarios_table.setColumnCount(6)
        self.usuarios_table.setHorizontalHeaderLabels(["ID", "Nome", "Login", "Email", "Tipo", "Status"])
        self.usuarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.usuarios_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.usuarios_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.usuarios_table.setAlternatingRowColors(True)
        self.usuarios_table.doubleClicked.connect(self.editar_usuario)

        action_layout = QHBoxLayout()
        self.add_user_button = QPushButton(QIcon.fromTheme("list-add"), " Adicionar")
        self.edit_user_button = QPushButton(QIcon.fromTheme("document-edit"), " Editar")
        self.toggle_user_button = QPushButton(QIcon.fromTheme("process-stop"), " Ativar/Desativar")
        self.reset_pass_button = QPushButton(QIcon.fromTheme("dialog-password"), " Resetar Senha")
        self.refresh_users_button = QPushButton(QIcon.fromTheme("view-refresh"), " Atualizar")

        self.add_user_button.clicked.connect(self.adicionar_usuario)
        self.edit_user_button.clicked.connect(self.editar_usuario)
        self.toggle_user_button.clicked.connect(self.alternar_status_usuario)
        self.reset_pass_button.clicked.connect(self.resetar_senha_usuario)
        self.refresh_users_button.clicked.connect(self.carregar_usuarios)
        
        action_layout.addWidget(self.add_user_button)
        action_layout.addWidget(self.edit_user_button)
        action_layout.addWidget(self.toggle_user_button)
        action_layout.addWidget(self.reset_pass_button)
        action_layout.addStretch()
        action_layout.addWidget(self.refresh_users_button)
        
        layout.addLayout(action_layout)
        layout.addWidget(self.usuarios_table)
        
        self.carregar_usuarios()
        return tab
    
    def carregar_usuarios(self):
        try:
            self.usuarios_table.setRowCount(0)
            usuarios = self.db.listar_usuarios()
            for i, usuario in enumerate(usuarios):
                self.usuarios_table.insertRow(i)
                self.usuarios_table.setItem(i, 0, QTableWidgetItem(str(usuario['id'])))
                self.usuarios_table.setItem(i, 1, QTableWidgetItem(usuario['nome']))
                self.usuarios_table.setItem(i, 2, QTableWidgetItem(usuario['login']))
                self.usuarios_table.setItem(i, 3, QTableWidgetItem(usuario['email'] or ""))
                self.usuarios_table.setItem(i, 4, QTableWidgetItem(usuario['tipo']))
                
                status = "Ativo" if usuario['ativo'] == 1 else "Inativo"
                status_item = QTableWidgetItem(status)
                status_item.setForeground(QColor('green') if usuario['ativo'] else QColor('red'))
                self.usuarios_table.setItem(i, 5, status_item)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar usuários: {str(e)}")

    def get_selected_user_info(self):
        selected_rows = self.usuarios_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Por favor, selecione um usuário na tabela.")
            return None, None
        row = selected_rows[0].row()
        user_id = int(self.usuarios_table.item(row, 0).text())
        user_info = self.db.obter_usuario_por_id(user_id)
        return user_id, user_info

    def adicionar_usuario(self):
        # Este método depende da sua UserDialogWindow. Verifique o nome da classe.
        from ui.user_dialog_window import UserDialogWindow
        dialog = UserDialogWindow(self.db)
        if dialog.exec_() == QDialog.Accepted:
            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'USER_CREATE', f"Usuário '{dialog.get_username()}' criado.")
            self.carregar_usuarios()

    def editar_usuario(self):
        user_id, _ = self.get_selected_user_info()
        if not user_id: return
        
        from ui.user_dialog_window import UserDialogWindow
        dialog = UserDialogWindow(self.db, user_id)
        if dialog.exec_() == QDialog.Accepted:
            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'USER_UPDATE', f"Dados do usuário ID {user_id} atualizados.")
            self.carregar_usuarios()

    def alternar_status_usuario(self):
        user_id, user_info = self.get_selected_user_info()
        if not user_id: return

        if user_id == self.usuario['id']:
            QMessageBox.warning(self, "Ação Inválida", "Você não pode desativar seu próprio usuário.")
            return

        novo_status = 0 if user_info['ativo'] == 1 else 1
        status_texto = "desativar" if novo_status == 0 else "ativar"
        
        reply = QMessageBox.question(self, "Confirmar Ação",
                                     f"Deseja realmente {status_texto} o usuário '{user_info['nome']}'?",
                                     QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            success, msg = self.db.atualizar_usuario(user_id, user_info['nome'], user_info['login'], user_info['email'], user_info['tipo'], novo_status)
            if success:
                action = 'USER_DEACTIVATE' if novo_status == 0 else 'USER_ACTIVATE'
                self.db.registrar_log('ADMIN', self.usuario.get('login'), action, f"Usuário ID {user_id} ({user_info['nome']}) teve seu status alterado.")
                self.carregar_usuarios()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def resetar_senha_usuario(self):
        user_id, user_info = self.get_selected_user_info()
        if not user_id: return

        nova_senha, ok = QInputDialog.getText(self, "Resetar Senha", f"Digite a nova senha para '{user_info['nome']}':", QLineEdit.Password)
        if ok and nova_senha:
            if len(nova_senha) < 6:
                QMessageBox.warning(self, "Senha Inválida", "A senha deve ter pelo menos 6 caracteres.")
                return

            success, msg = self.db.alterar_senha_usuario(user_id, nova_senha)
            if success:
                self.db.registrar_log('ADMIN', self.usuario.get('login'), 'USER_PASS_RESET', f"Senha do usuário ID {user_id} resetada.")
                QMessageBox.information(self, "Sucesso", "Senha do usuário resetada com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", msg)

    # ===================================================================
    # ABA DE CONFIGURAÇÕES
    # ===================================================================
    def criar_tab_config(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        form_layout = QFormLayout()

        # Configurações de Produto
        self.margem_lucro_padrao = QDoubleSpinBox(suffix=" %")
        self.alerta_estoque_padrao = QSpinBox(suffix=" unidades")
        self.alerta_validade_dias = QSpinBox(suffix=" dias")
        
        form_layout.addRow(QLabel("<b>Configurações de Produtos:</b>"), None)
        form_layout.addRow("Margem de Lucro Padrão:", self.margem_lucro_padrao)
        form_layout.addRow("Alerta de Estoque Baixo Padrão:", self.alerta_estoque_padrao)
        form_layout.addRow("Alerta de Vencimento (antecedência):", self.alerta_validade_dias)

        save_button = QPushButton(QIcon.fromTheme("document-save"), " Salvar Configurações")
        save_button.clicked.connect(self.salvar_configuracoes)

        layout.addLayout(form_layout)
        layout.addStretch()
        layout.addWidget(save_button, alignment=Qt.AlignRight)

        self.carregar_configuracoes()
        return tab

    def carregar_configuracoes(self):
        self.margem_lucro_padrao.setValue(float(self.db.obter_configuracao('margem_lucro_padrao', 30.0)))
        self.alerta_estoque_padrao.setValue(int(self.db.obter_configuracao('alerta_estoque_padrao', 10)))
        self.alerta_validade_dias.setValue(int(self.db.obter_configuracao('alerta_validade_dias', 30)))
        
    def salvar_configuracoes(self):
        try:
            self.db.definir_configuracao('margem_lucro_padrao', self.margem_lucro_padrao.value())
            self.db.definir_configuracao('alerta_estoque_padrao', self.alerta_estoque_padrao.value())
            self.db.definir_configuracao('alerta_validade_dias', self.alerta_validade_dias.value())

            self.db.registrar_log('ADMIN', self.usuario.get('login'), 'SETTINGS_UPDATE', 'Configurações do sistema foram alteradas.')
            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar configurações: {str(e)}")


    # ===================================================================
    # ABA DE LOGS
    # ===================================================================
    def criar_tab_logs(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # Filtros
        filter_layout = QHBoxLayout()
        self.log_data_inicio = QDateEdit(QDate.currentDate().addMonths(-1))
        self.log_data_fim = QDateEdit(QDate.currentDate())
        self.log_usuario_input = QLineEdit()
        self.log_level_combo = QComboBox()
        
        self.log_data_inicio.setCalendarPopup(True)
        self.log_data_fim.setCalendarPopup(True)
        self.log_usuario_input.setPlaceholderText("Filtrar por usuário...")
        self.log_level_combo.addItems(["Todos", "ADMIN", "INFO", "WARNING", "ERROR"])

        filter_button = QPushButton(QIcon.fromTheme("edit-find"), " Filtrar")
        filter_button.clicked.connect(self.carregar_logs)

        filter_layout.addWidget(QLabel("De:"))
        filter_layout.addWidget(self.log_data_inicio)
        filter_layout.addWidget(QLabel("Até:"))
        filter_layout.addWidget(self.log_data_fim)
        filter_layout.addWidget(self.log_usuario_input)
        filter_layout.addWidget(self.log_level_combo)
        filter_layout.addWidget(filter_button)

        # Tabela de logs
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels(["Timestamp", "Nível", "Usuário", "Ação", "Detalhes"])
        self.logs_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.logs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.logs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.logs_table.setEditTriggers(QTableWidget.NoEditTriggers)

        layout.addLayout(filter_layout)
        layout.addWidget(self.logs_table)
        
        self.carregar_logs()
        return tab

    def carregar_logs(self):
        try:
            data_inicio = self.log_data_inicio.date().toString("yyyy-MM-dd")
            data_fim = self.log_data_fim.date().toString("yyyy-MM-dd")
            usuario = self.log_usuario_input.text()
            level = self.log_level_combo.currentText()

            logs = self.db.listar_logs(data_inicio, data_fim, usuario, level)

            self.logs_table.setRowCount(0)
            for i, log in enumerate(logs):
                self.logs_table.insertRow(i)
                self.logs_table.setItem(i, 0, QTableWidgetItem(log['timestamp']))
                self.logs_table.setItem(i, 1, QTableWidgetItem(log['level']))
                self.logs_table.setItem(i, 2, QTableWidgetItem(log['usuario_login']))
                self.logs_table.setItem(i, 3, QTableWidgetItem(log['action']))
                self.logs_table.setItem(i, 4, QTableWidgetItem(log['details']))
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar logs: {str(e)}")