from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QDoubleSpinBox,
                           QDialog, QFrame)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

class PromocoesWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_dados()
    
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título da página
        titulo = QLabel("Cadastro de Promoções")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Área de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar promoção...")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.pesquisar_promocoes)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Tabela de promoções
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["ID", "Produto", "Preço Antigo", 
                                             "Preço Promocional", "Início", "Fim", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Promoção")
        self.add_button.clicked.connect(self.abrir_formulario_promocao)
        action_layout.addWidget(self.add_button)
        layout.addLayout(action_layout)
    
    def carregar_dados(self):
        """Carrega as promoções do banco de dados para a tabela."""
        promocoes = self.db.listar_promocoes()
        self.atualizar_tabela(promocoes)
    
    def pesquisar_promocoes(self):
        """Pesquisa promoções pelo termo digitado."""
        termo = self.search_input.text()
        if termo:
            promocoes = self.db.listar_promocoes(filtro=termo)
        else:
            promocoes = self.db.listar_promocoes()
        
        self.atualizar_tabela(promocoes)
    
    def atualizar_tabela(self, promocoes):
        """Atualiza a tabela com as promoções fornecidas."""
        self.tabela.setRowCount(0)
        
        for row, promocao in enumerate(promocoes):
            self.tabela.insertRow(row)
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(promocao['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(promocao['produto_nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"R$ {promocao['preco_antigo']:.2f}"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"R$ {promocao['preco_promocional']:.2f}"))
            self.tabela.setItem(row, 4, QTableWidgetItem(str(promocao['data_inicio'])))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(promocao['data_fim'])))
            
            # Botões de ação
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            
            editar_btn = QPushButton("Editar")
            editar_btn.clicked.connect(lambda _, p_id=promocao['id']: self.abrir_formulario_promocao(p_id))
            
            excluir_btn = QPushButton("Excluir")
            excluir_btn.clicked.connect(lambda _, p_id=promocao['id']: self.excluir_promocao(p_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            self.tabela.setCellWidget(row, 6, acoes_widget)
    
    def abrir_formulario_promocao(self, promocao_id=None):
        """Abre o formulário para adicionar ou editar uma promoção."""
        dialog = FormularioPromocao(self.db, promocao_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_promocao(self, promocao_id):
        """Exclui uma promoção após confirmação."""
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir esta promoção?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_promocao(promocao_id):
                QMessageBox.information(self, "Sucesso", "Promoção excluída com sucesso!")
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir a promoção.")


class FormularioPromocao(QDialog):
    def __init__(self, db, promocao_id=None):
        super().__init__()
        self.db = db
        self.promocao_id = promocao_id
        self.promocao = None
        
        if promocao_id:
            self.promocao = self.db.obter_promocao(promocao_id)
            if not self.promocao:
                QMessageBox.warning(self, "Erro", "Promoção não encontrada!")
                self.reject()
        
        self.initUI()
        
        if self.promocao:
            self.carregar_dados_promocao()
    
    def initUI(self):
        # Configurar janela
        self.setWindowTitle("Cadastro de Promoção")
        self.setFixedWidth(500)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        # Campos do formulário
        self.produto_combo = QComboBox()
        self.carregar_produtos()
        
       # Continuação do arquivo ui/promocoes_window.py - Classe FormularioPromocao

        self.preco_antigo_input = QDoubleSpinBox()
        self.preco_antigo_input.setRange(0, 99999.99)
        self.preco_antigo_input.setPrefix("R$ ")
        self.preco_antigo_input.setDecimals(2)
        
        self.preco_promocional_input = QDoubleSpinBox()
        self.preco_promocional_input.setRange(0, 99999.99)
        self.preco_promocional_input.setPrefix("R$ ")
        self.preco_promocional_input.setDecimals(2)
        
        self.data_inicio_input = QDateEdit()
        self.data_inicio_input.setDisplayFormat("dd/MM/yyyy")
        self.data_inicio_input.setCalendarPopup(True)
        self.data_inicio_input.setDate(QDate.currentDate())
        
        self.data_fim_input = QDateEdit()
        self.data_fim_input.setDisplayFormat("dd/MM/yyyy")
        self.data_fim_input.setCalendarPopup(True)
        self.data_fim_input.setDate(QDate.currentDate().addDays(30))  # Default para 30 dias
        
        self.descricao_input = QLineEdit()
        
        # Adicionar campos ao formulário
        form_layout.addRow("Produto:", self.produto_combo)
        form_layout.addRow("Preço Antigo:", self.preco_antigo_input)
        form_layout.addRow("Preço Promocional:", self.preco_promocional_input)
        form_layout.addRow("Data de Início:", self.data_inicio_input)
        form_layout.addRow("Data de Fim:", self.data_fim_input)
        form_layout.addRow("Descrição:", self.descricao_input)
        
        layout.addLayout(form_layout)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar_promocao)
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        
        layout.addLayout(button_layout)
        
        # Conectar sinal de alteração do produto
        self.produto_combo.currentIndexChanged.connect(self.atualizar_preco_antigo)
    
    def carregar_produtos(self):
        """Carrega a lista de produtos para o combobox."""
        self.produto_combo.clear()
        self.produto_combo.addItem("Selecione um produto", None)
        
        produtos = self.db.listar_produtos()
        for produto in produtos:
            self.produto_combo.addItem(produto['nome'], produto['id'])
    
    def atualizar_preco_antigo(self):
        """Atualiza o preço antigo com base no produto selecionado."""
        produto_id = self.produto_combo.currentData()
        if produto_id:
            produto = self.db.obter_produto(produto_id)
            if produto:
                self.preco_antigo_input.setValue(produto['preco_venda'])
    
    def carregar_dados_promocao(self):
        """Carrega os dados da promoção nos campos do formulário."""
        # Selecionar o produto
        if self.promocao['produto_id']:
            index = self.produto_combo.findData(self.promocao['produto_id'])
            if index != -1:
                self.produto_combo.setCurrentIndex(index)
        
        self.preco_antigo_input.setValue(self.promocao['preco_antigo'])
        self.preco_promocional_input.setValue(self.promocao['preco_promocional'])
        
        if self.promocao['data_inicio']:
            data_inicio = QDate.fromString(self.promocao['data_inicio'], "yyyy-MM-dd")
            self.data_inicio_input.setDate(data_inicio)
        
        if self.promocao['data_fim']:
            data_fim = QDate.fromString(self.promocao['data_fim'], "yyyy-MM-dd")
            self.data_fim_input.setDate(data_fim)
        
        self.descricao_input.setText(self.promocao['descricao'] or "")
    
    def salvar_promocao(self):
        """Salva os dados da promoção no banco de dados."""
        # Validar campos obrigatórios
        produto_id = self.produto_combo.currentData()
        if not produto_id:
            QMessageBox.warning(self, "Erro", "Selecione um produto!")
            return
        
        # Validar datas
        data_inicio = self.data_inicio_input.date()
        data_fim = self.data_fim_input.date()
        
        if data_inicio > data_fim:
            QMessageBox.warning(self, "Erro", "A data de início não pode ser posterior à data de fim!")
            return
        
        # Coletar dados do formulário
        preco_antigo = self.preco_antigo_input.value()
        preco_promocional = self.preco_promocional_input.value()
        data_inicio_str = data_inicio.toString("yyyy-MM-dd")
        data_fim_str = data_fim.toString("yyyy-MM-dd")
        descricao = self.descricao_input.text().strip()
        
        try:
            # Inserir ou atualizar promoção
            if self.promocao_id:
                sucesso = self.db.atualizar_promocao(
                    self.promocao_id, produto_id, preco_antigo, preco_promocional,
                    data_inicio_str, data_fim_str, descricao
                )
                mensagem = "Promoção atualizada com sucesso!"
            else:
                sucesso = self.db.adicionar_promocao(
                    produto_id, preco_antigo, preco_promocional,
                    data_inicio_str, data_fim_str, descricao
                )
                mensagem = "Promoção cadastrada com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar a promoção.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar promoção: {str(e)}")