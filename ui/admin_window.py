from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QWidget, QMessageBox, 
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt

class AdminWindow(QDialog):
    """Janela de administração do sistema"""
    
    def __init__(self, db_manager, usuario):
        super().__init__()
        
        self.db = db_manager
        self.usuario = usuario
        
        # Verificar se o usuário tem permissão
        if self.usuario['tipo'] != 'admin':
            QMessageBox.warning(self, "Acesso Negado", 
                               "Você não tem permissão para acessar esta área.")
            self.reject()
            return
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.setWindowTitle("Painel de Administração")
        self.setMinimumSize(800, 600)
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Título da janela
        title_label = QLabel("Painel de Administração")
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        
        # Criar tabs para diferentes seções
        self.tab_widget = QTabWidget()
        
        # Tab de usuários
        self.usuarios_tab = self.criar_tab_usuarios()
        self.tab_widget.addTab(self.usuarios_tab, "Gerenciar Usuários")
        
        # Tab de configurações do sistema
        self.config_tab = self.criar_tab_config()
        self.tab_widget.addTab(self.config_tab, "Configurações")
        
        # Tab de logs do sistema
        self.logs_tab = self.criar_tab_logs()
        self.tab_widget.addTab(self.logs_tab, "Logs do Sistema")
        
        # Botões de ação
        buttons_layout = QHBoxLayout()
        
        self.close_button = QPushButton("Fechar")
        self.close_button.clicked.connect(self.close)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_button)
        
        # Adicionar elementos ao layout principal
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.tab_widget)
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def criar_tab_usuarios(self):
        """Cria a tab de gerenciamento de usuários"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Tabela de usuários
        self.usuarios_table = QTableWidget()
        self.usuarios_table.setColumnCount(6)
        self.usuarios_table.setHorizontalHeaderLabels(["ID", "Nome", "Login", "Email", "Tipo", "Status"])
        self.usuarios_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        # Botões para ações com usuários
        action_layout = QHBoxLayout()
        
        self.add_user_button = QPushButton("Adicionar Usuário")
        self.add_user_button.clicked.connect(self.adicionar_usuario)
        
        self.edit_user_button = QPushButton("Editar Usuário")
        self.edit_user_button.clicked.connect(self.editar_usuario)
        
        self.delete_user_button = QPushButton("Excluir Usuário")
        self.delete_user_button.clicked.connect(self.excluir_usuario)
        
        action_layout.addWidget(self.add_user_button)
        action_layout.addWidget(self.edit_user_button)
        action_layout.addWidget(self.delete_user_button)
        
        # Adicionar ao layout
        layout.addWidget(QLabel("Lista de Usuários"))
        layout.addWidget(self.usuarios_table)
        layout.addLayout(action_layout)
        
        tab.setLayout(layout)
        
        # Carregar dados
        self.carregar_usuarios()
        
        return tab
    
    def criar_tab_config(self):
        """Cria a tab de configurações do sistema"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Adicione seus widgets de configuração aqui
        layout.addWidget(QLabel("Configurações do Sistema"))
        layout.addWidget(QLabel("Esta seção está em desenvolvimento"))
        
        tab.setLayout(layout)
        return tab
    
    def criar_tab_logs(self):
        """Cria a tab de logs do sistema"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Adicione seus widgets de logs aqui
        layout.addWidget(QLabel("Logs do Sistema"))
        layout.addWidget(QLabel("Esta seção está em desenvolvimento"))
        
        tab.setLayout(layout)
        return tab
    
    def carregar_usuarios(self):
        """Carrega a lista de usuários do banco de dados"""
        try:
            # Limpar tabela
            self.usuarios_table.setRowCount(0)
            
            # Execute uma consulta para obter todos os usuários
            usuarios = self.db.listar_usuarios()
            
            # Preencher tabela
            for i, usuario in enumerate(usuarios):
                self.usuarios_table.insertRow(i)
                
                # Adicionar dados às células
                self.usuarios_table.setItem(i, 0, QTableWidgetItem(str(usuario['id'])))
                self.usuarios_table.setItem(i, 1, QTableWidgetItem(usuario['nome']))
                self.usuarios_table.setItem(i, 2, QTableWidgetItem(usuario['login']))
                self.usuarios_table.setItem(i, 3, QTableWidgetItem(usuario['email'] or ""))
                self.usuarios_table.setItem(i, 4, QTableWidgetItem(usuario['tipo']))
                
                status = "Ativo" if usuario['ativo'] == 1 else "Inativo"
                self.usuarios_table.setItem(i, 5, QTableWidgetItem(status))
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar lista de usuários: {str(e)}")
    
    def adicionar_usuario(self):
        """Abre o diálogo para adicionar um novo usuário"""
        from ui.user_dialog_window import UserDialogWindow
        
        dialog = UserDialogWindow(self.db)
        if dialog.exec_():
            # Se usuário foi adicionado, atualizar lista
            self.carregar_usuarios()
    
    def editar_usuario(self):
        """Edita o usuário selecionado"""
        # Obter o índice da linha selecionada
        selected_rows = self.usuarios_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário para editar.")
            return
        
        # Obter o ID do usuário da primeira coluna
        row = selected_rows[0].row()
        user_id = int(self.usuarios_table.item(row, 0).text())
        
        # Abrir diálogo de edição
        from ui.user_dialog_window import UserDialog
        
        dialog = UserDialog(self.db, user_id)
        if dialog.exec_():
            # Se usuário foi editado, atualizar lista
            self.carregar_usuarios()
    
    def excluir_usuario(self):
        """Exclui o usuário selecionado"""
        # Obter o índice da linha selecionada
        selected_rows = self.usuarios_table.selectedIndexes()
        if not selected_rows:
            QMessageBox.warning(self, "Aviso", "Selecione um usuário para excluir.")
            return
        
        # Obter o ID do usuário da primeira coluna
        row = selected_rows[0].row()
        user_id = int(self.usuarios_table.item(row, 0).text())
        user_name = self.usuarios_table.item(row, 1).text()
        
        # Confirmar exclusão
        reply = QMessageBox.question(self, "Confirmar Exclusão", 
                                    f"Deseja realmente excluir o usuário '{user_name}'?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Excluir o usuário
            resultado, mensagem = self.db.excluir_usuario(user_id)
            
            if resultado:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.carregar_usuarios()
            else:
                QMessageBox.critical(self, "Erro", mensagem)