from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class ClientesWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_dados()
    
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título da página
        titulo = QLabel("Cadastro de Clientes")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Área de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar cliente...")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.pesquisar_clientes)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Tabela de clientes
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Documento", "Telefone", 
                                              "Email", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Cliente")
        self.add_button.clicked.connect(self.abrir_formulario_cliente)
        action_layout.addWidget(self.add_button)
        layout.addLayout(action_layout)
    
    def carregar_dados(self):
        """Carrega os clientes do banco de dados para a tabela."""
        clientes = self.db.listar_clientes()
        self.atualizar_tabela(clientes)
    
    def pesquisar_clientes(self):
        """Pesquisa clientes pelo termo digitado."""
        termo = self.search_input.text()
        if termo:
            clientes = self.db.listar_clientes(filtro=termo)
        else:
            clientes = self.db.listar_clientes()
        
        self.atualizar_tabela(clientes)
    
    def atualizar_tabela(self, clientes):
        """Atualiza a tabela com os clientes fornecidos."""
        self.tabela.setRowCount(0)
        
        for row, cliente in enumerate(clientes):
            self.tabela.insertRow(row)
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(cliente['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(cliente['documento'] or ""))
            self.tabela.setItem(row, 3, QTableWidgetItem(cliente['telefone'] or ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(cliente['email'] or ""))
            
            # Botões de ação
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            
            editar_btn = QPushButton("Editar")
            editar_btn.clicked.connect(lambda _, c_id=cliente['id']: self.abrir_formulario_cliente(c_id))
            
            excluir_btn = QPushButton("Excluir")
            excluir_btn.clicked.connect(lambda _, c_id=cliente['id']: self.excluir_cliente(c_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            self.tabela.setCellWidget(row, 5, acoes_widget)
    
    def abrir_formulario_cliente(self, cliente_id=None):
        """Abre o formulário para adicionar ou editar um cliente."""
        dialog = FormularioCliente(self.db, cliente_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_cliente(self, cliente_id):
        """Exclui um cliente após confirmação."""
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este cliente?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_cliente(cliente_id):
                QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso!")
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir o cliente.")


class FormularioCliente(QDialog):
    def __init__(self, db, cliente_id=None):
        super().__init__()
        self.db = db
        self.cliente_id = cliente_id
        self.cliente = None
        
        if cliente_id:
            self.cliente = self.db.obter_cliente(cliente_id)
            if not self.cliente:
                QMessageBox.warning(self, "Erro", "Cliente não encontrado!")
                self.reject()
        
        self.initUI()
        
        if self.cliente:
            self.carregar_dados_cliente()
    
    def initUI(self):
        # Configurar janela
        self.setWindowTitle("Cadastro de Cliente")
        self.setFixedWidth(500)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        # Campos do formulário
        self.nome_input = QLineEdit()
        self.documento_input = QLineEdit()
        self.documento_input.setPlaceholderText("CPF")
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        
        # Adicionar campos ao formulário
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Documento:", self.documento_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Endereço:", self.endereco_input)
        
        layout.addLayout(form_layout)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar_cliente)
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        
        layout.addLayout(button_layout)
    
    def carregar_dados_cliente(self):
        """Carrega os dados do cliente nos campos do formulário."""
        self.nome_input.setText(self.cliente['nome'])
        self.documento_input.setText(self.cliente['documento'] or "")
        self.telefone_input.setText(self.cliente['telefone'] or "")
        self.email_input.setText(self.cliente['email'] or "")
        self.endereco_input.setText(self.cliente['endereco'] or "")
    
    def salvar_cliente(self):
        """Salva os dados do cliente no banco de dados."""
        # Validar campos obrigatórios
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do cliente é obrigatório!")
            return
        
        # Coletar dados do formulário
        nome = self.nome_input.text().strip()
        documento = self.documento_input.text().strip()
        telefone = self.telefone_input.text().strip()
        email = self.email_input.text().strip()
        endereco = self.endereco_input.text().strip()
        
        try:
            # Inserir ou atualizar cliente
            if self.cliente_id:
                sucesso = self.db.atualizar_cliente(
                    self.cliente_id, nome, documento, telefone, email, endereco
                )
                mensagem = "Cliente atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_cliente(
                    nome, documento, telefone, email, endereco
                )
                mensagem = "Cliente cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o cliente.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cliente: {str(e)}")