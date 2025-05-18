from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame, QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class FornecedorWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_dados()
    
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título da página
        titulo = QLabel("Cadastro de Fornecedores")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Área de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar fornecedor...")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.pesquisar_fornecedores)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Tabela de fornecedores
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Representante", "Frequência", "Telefone", 
                                              "Email", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Fornecedor")
        self.add_button.clicked.connect(self.abrir_formulario_fornecedor)
        action_layout.addWidget(self.add_button)
        layout.addLayout(action_layout)
    
    def carregar_dados(self):
        """Carrega os fornecedores do banco de dados para a tabela."""
        fornecedores = self.db.listar_fornecedores()
        self.atualizar_tabela(fornecedores)
    
    def pesquisar_fornecedores(self):
        """Pesquisa fornecedores pelo termo digitado."""
        termo = self.search_input.text()
        if termo:
            fornecedores = self.db.listar_fornecedores(filtro=termo)
        else:
            fornecedores = self.db.listar_fornecedores()
        
        self.atualizar_tabela(fornecedores)
    
    def atualizar_tabela(self, fornecedores):
        """Atualiza a tabela com os fornecedores fornecidos."""
        self.tabela.setRowCount(0)
        
        for row, fornecedor in enumerate(fornecedores):
            self.tabela.insertRow(row)
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(fornecedor['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(fornecedor['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(fornecedor['representante'] or ""))
            self.tabela.setItem(row, 3, QTableWidgetItem(fornecedor['frequencia_compra'] or ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(fornecedor['telefone'] or ""))
            self.tabela.setItem(row, 5, QTableWidgetItem(fornecedor['email'] or ""))
            
            # Botões de ação
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            
            editar_btn = QPushButton("Editar")
            editar_btn.clicked.connect(lambda _, f_id=fornecedor['id']: self.abrir_formulario_fornecedor(f_id))
            
            excluir_btn = QPushButton("Excluir")
            excluir_btn.clicked.connect(lambda _, f_id=fornecedor['id']: self.excluir_fornecedor(f_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            self.tabela.setCellWidget(row, 6, acoes_widget)
    
    def abrir_formulario_fornecedor(self, fornecedor_id=None):
        """Abre o formulário para adicionar ou editar um fornecedor."""
        dialog = FormularioFornecedor(self.db, fornecedor_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_fornecedor(self, fornecedor_id):
        """Exclui um fornecedor após confirmação."""
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este fornecedor? Isso pode afetar produtos associados.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_fornecedor(fornecedor_id):
                QMessageBox.information(self, "Sucesso", "Fornecedor excluído com sucesso!")
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir o fornecedor.")


class FormularioFornecedor(QDialog):
    def __init__(self, db, fornecedor_id=None):
        super().__init__()
        self.db = db
        self.fornecedor_id = fornecedor_id
        self.fornecedor = None
        
        if fornecedor_id:
            self.fornecedor = self.db.obter_fornecedor(fornecedor_id)
            if not self.fornecedor:
                QMessageBox.warning(self, "Erro", "Fornecedor não encontrado!")
                self.reject()
        
        self.initUI()
        
        if self.fornecedor:
            self.carregar_dados_fornecedor()
    
    def initUI(self):
        # Configurar janela
        self.setWindowTitle("Cadastro de Fornecedor")
        self.setFixedWidth(500)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        # Campos do formulário
        self.nome_input = QLineEdit()
        self.representante_input = QLineEdit()
        self.representante_input.setPlaceholderText("Nome do representante")
        
        # ComboBox para frequência de compra
        self.frequencia_input = QComboBox()
        self.frequencia_input.addItems(["Alta", "Média", "Baixa"])
        
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        self.contato_input = QLineEdit()
        self.contato_input.setPlaceholderText("Nome do contato")
        
        # Adicionar campos ao formulário
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Representante:", self.representante_input)
        form_layout.addRow("Frequência de Compra:", self.frequencia_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Endereço:", self.endereco_input)
        form_layout.addRow("Contato:", self.contato_input)
        
        layout.addLayout(form_layout)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar_fornecedor)
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        
        layout.addLayout(button_layout)
    
    def carregar_dados_fornecedor(self):
        """Carrega os dados do fornecedor nos campos do formulário."""
        self.nome_input.setText(self.fornecedor['nome'])
        self.representante_input.setText(self.fornecedor['representante'] or "")
        
        # Definir o item selecionado no ComboBox
        frequencia = self.fornecedor['frequencia_compra']
        if frequencia:
            index = self.frequencia_input.findText(frequencia, Qt.MatchFixedString)
            if index >= 0:
                self.frequencia_input.setCurrentIndex(index)
        
        self.telefone_input.setText(self.fornecedor['telefone'] or "")
        self.email_input.setText(self.fornecedor['email'] or "")
        self.endereco_input.setText(self.fornecedor['endereco'] or "")
        self.contato_input.setText(self.fornecedor['contato'] or "")
    
    def salvar_fornecedor(self):
        """Salva os dados do fornecedor no banco de dados."""
        # Validar campos obrigatórios
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do fornecedor é obrigatório!")
            return
        
        # Coletar dados do formulário
        nome = self.nome_input.text().strip()
        representante = self.representante_input.text().strip()
        frequencia_compra = self.frequencia_input.currentText()
        telefone = self.telefone_input.text().strip()
        email = self.email_input.text().strip()
        endereco = self.endereco_input.text().strip()
        contato = self.contato_input.text().strip()
        
        try:
            # Inserir ou atualizar fornecedor
            if self.fornecedor_id:
                sucesso = self.db.atualizar_fornecedor(
                    self.fornecedor_id, nome, representante, frequencia_compra, telefone, email, endereco, contato
                )
                mensagem = "Fornecedor atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_fornecedor(
                    nome, representante, frequencia_compra, telefone, email, endereco, contato
                )
                mensagem = "Fornecedor cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o fornecedor.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar fornecedor: {str(e)}")