from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QSpinBox,
                           QDoubleSpinBox, QDialog, QFrame)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

class EstoqueWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_dados()
    
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título da página
        titulo = QLabel("Controle de Estoque")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Área de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar produto...")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.pesquisar_produtos)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(9)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Quantidade", "Preço Compra", 
                                              "Preço Venda", "Validade", "Localização", 
                                              "Fornecedor", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Produto")
        self.add_button.clicked.connect(self.abrir_formulario_produto)
        action_layout.addWidget(self.add_button)
        layout.addLayout(action_layout)
    
    def carregar_dados(self):
        """Carrega os produtos do banco de dados para a tabela."""
        produtos = self.db.listar_produtos()
        self.atualizar_tabela(produtos)
    
    def pesquisar_produtos(self):
        """Pesquisa produtos pelo termo digitado."""
        termo = self.search_input.text()
        if termo:
            produtos = self.db.listar_produtos(filtro=termo)
        else:
            produtos = self.db.listar_produtos()
        
        self.atualizar_tabela(produtos)
    
    def atualizar_tabela(self, produtos):
        """Atualiza a tabela com os produtos fornecidos."""
        self.tabela.setRowCount(0)
        
        for row, produto in enumerate(produtos):
            self.tabela.insertRow(row)
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(produto['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(str(produto['quantidade'])))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"R$ {produto['preco_compra']:.2f}"))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}"))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(produto['data_validade'])))
            self.tabela.setItem(row, 6, QTableWidgetItem(produto['localizacao']))
            
            fornecedor_nome = produto['fornecedor_nome'] if produto['fornecedor_nome'] else "N/A"
            self.tabela.setItem(row, 7, QTableWidgetItem(fornecedor_nome))
            
            # Botões de ação
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            
            editar_btn = QPushButton("Editar")
            editar_btn.clicked.connect(lambda _, p_id=produto['id']: self.abrir_formulario_produto(p_id))
            
            excluir_btn = QPushButton("Excluir")
            excluir_btn.clicked.connect(lambda _, p_id=produto['id']: self.excluir_produto(p_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            self.tabela.setCellWidget(row, 8, acoes_widget)
    
    def abrir_formulario_produto(self, produto_id=None):
        """Abre o formulário para adicionar ou editar um produto."""
        dialog = FormularioProduto(self.db, produto_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_produto(self, produto_id):
        """Exclui um produto após confirmação."""
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este produto?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_produto(produto_id):
                QMessageBox.information(self, "Sucesso", "Produto excluído com sucesso!")
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir o produto.")


class FormularioProduto(QDialog):
    def __init__(self, db, produto_id=None):
        super().__init__()
        self.db = db
        self.produto_id = produto_id
        self.produto = None
        
        if produto_id:
            self.produto = self.db.obter_produto(produto_id)
            if not self.produto:
                QMessageBox.warning(self, "Erro", "Produto não encontrado!")
                self.reject()
        
        self.initUI()
        
        if self.produto:
            self.carregar_dados_produto()
    
    def initUI(self):
        # Configurar janela
        self.setWindowTitle("Cadastro de Produto")
        self.setFixedWidth(600)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        # Campos do formulário
        self.nome_input = QLineEdit()
        self.descricao_input = QLineEdit()
        self.quantidade_input = QSpinBox()
        self.quantidade_input.setRange(0, 99999)
        self.preco_compra_input = QDoubleSpinBox()
        self.preco_compra_input.setRange(0, 99999.99)
        self.preco_compra_input.setPrefix("R$ ")
        self.preco_compra_input.setDecimals(2)
        self.preco_venda_input = QDoubleSpinBox()
        self.preco_venda_input.setRange(0, 99999.99)
        self.preco_venda_input.setPrefix("R$ ")
        self.preco_venda_input.setDecimals(2)
        
        self.data_validade_input = QDateEdit()
        self.data_validade_input.setDisplayFormat("dd/MM/yyyy")
        self.data_validade_input.setCalendarPopup(True)
        self.data_validade_input.setDate(QDate.currentDate().addDays(30))  # Default para 30 dias
        
        self.localizacao_input = QLineEdit()
        
        self.fornecedor_combo = QComboBox()
        self.carregar_fornecedores()
        
        # Adicionar campos ao formulário
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Descrição:", self.descricao_input)
        form_layout.addRow("Quantidade:", self.quantidade_input)
        form_layout.addRow("Preço de Compra:", self.preco_compra_input)
        form_layout.addRow("Preço de Venda:", self.preco_venda_input)
        form_layout.addRow("Data de Validade:", self.data_validade_input)
        form_layout.addRow("Localização:", self.localizacao_input)
        form_layout.addRow("Fornecedor:", self.fornecedor_combo)
        
        layout.addLayout(form_layout)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar_produto)
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        
        layout.addLayout(button_layout)
    
    def carregar_fornecedores(self):
        """Carrega a lista de fornecedores para o combobox."""
        self.fornecedor_combo.clear()
        self.fornecedor_combo.addItem("Selecione um fornecedor", None)
        
        fornecedores = self.db.listar_fornecedores()
        for fornecedor in fornecedores:
            self.fornecedor_combo.addItem(fornecedor['nome'], fornecedor['id'])
    
    def carregar_dados_produto(self):
        """Carrega os dados do produto nos campos do formulário."""
        self.nome_input.setText(self.produto['nome'])
        self.descricao_input.setText(self.produto['descricao'] or "")
        self.quantidade_input.setValue(self.produto['quantidade'])
        self.preco_compra_input.setValue(self.produto['preco_compra'])
        self.preco_venda_input.setValue(self.produto['preco_venda'])
        
        if self.produto['data_validade']:
            data_validade = QDate.fromString(self.produto['data_validade'], "yyyy-MM-dd")
            self.data_validade_input.setDate(data_validade)
        
        self.localizacao_input.setText(self.produto['localizacao'] or "")
        
        # Selecionar o fornecedor
        if self.produto['fornecedor_id']:
            index = self.fornecedor_combo.findData(self.produto['fornecedor_id'])
            if index != -1:
                self.fornecedor_combo.setCurrentIndex(index)
    
    # Continuação do arquivo ui/estoque_window.py - Método salvar_produto da classe FormularioProduto

    def salvar_produto(self):
        """Salva os dados do produto no banco de dados."""
        # Validar campos obrigatórios
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do produto é obrigatório!")
            return
        
        # Coletar dados do formulário
        nome = self.nome_input.text().strip()
        descricao = self.descricao_input.text().strip()
        quantidade = self.quantidade_input.value()
        preco_compra = self.preco_compra_input.value()
        preco_venda = self.preco_venda_input.value()
        data_validade = self.data_validade_input.date().toString("yyyy-MM-dd")
        localizacao = self.localizacao_input.text().strip()
        
        fornecedor_id = self.fornecedor_combo.currentData()
        if fornecedor_id == "":
            fornecedor_id = None
        
        try:
            # Inserir ou atualizar produto
            if self.produto_id:
                sucesso = self.db.atualizar_produto(
                    self.produto_id, nome, descricao, quantidade, preco_compra, 
                    preco_venda, data_validade, localizacao, fornecedor_id
                )
                mensagem = "Produto atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_produto(
                    nome, descricao, quantidade, preco_compra, 
                    preco_venda, data_validade, localizacao, fornecedor_id
                )
                mensagem = "Produto cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o produto.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar produto: {str(e)}")