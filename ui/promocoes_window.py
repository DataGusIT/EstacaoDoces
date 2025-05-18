from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QDoubleSpinBox,
                           QDialog, QFrame, QTabWidget, QRadioButton, QButtonGroup)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta

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
        self.tabela.setColumnCount(8)  # Adicionado uma coluna para taxa de desconto
        self.tabela.setHorizontalHeaderLabels(["ID", "Produto", "Preço Antigo", 
                                             "Taxa de Desconto", "Preço Promocional", "Início", "Fim", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Promoção")
        self.add_button.clicked.connect(self.abrir_formulario_promocao)
        
        self.produtos_especiais_button = QPushButton("Gerenciar Promoções Especiais")
        self.produtos_especiais_button.clicked.connect(self.abrir_promocoes_especiais)
        
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.produtos_especiais_button)
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
            
            # Calcular a taxa de desconto
            preco_antigo = promocao['preco_antigo']
            preco_promocional = promocao['preco_promocional']
            taxa_desconto = 0
            if preco_antigo > 0:
                taxa_desconto = ((preco_antigo - preco_promocional) / preco_antigo) * 100
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(promocao['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(promocao['produto_nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"R$ {promocao['preco_antigo']:.2f}"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{taxa_desconto:.1f}%"))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"R$ {promocao['preco_promocional']:.2f}"))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(promocao['data_inicio'])))
            self.tabela.setItem(row, 6, QTableWidgetItem(str(promocao['data_fim'])))
            
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
            
            self.tabela.setCellWidget(row, 7, acoes_widget)
    
    def abrir_formulario_promocao(self, promocao_id=None):
        """Abre o formulário para adicionar ou editar uma promoção."""
        dialog = FormularioPromocao(self.db, promocao_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def abrir_promocoes_especiais(self):
        """Abre a janela de promoções especiais para produtos com estoque baixo ou próximos ao vencimento."""
        dialog = PromocoesEspeciaisDialog(self.db)
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


class PromocoesEspeciaisDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_produtos_especiais()
    
    def initUI(self):
        self.setWindowTitle("Promoções Especiais")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout(self)
        
        # Abas para os diferentes tipos de produtos
        self.tabs = QTabWidget()
        self.tab_estoque_baixo = QWidget()
        self.tab_vencimento = QWidget()
        
        self.setup_tab_estoque_baixo()
        self.setup_tab_vencimento()
        
        self.tabs.addTab(self.tab_estoque_baixo, "Estoque Baixo")
        self.tabs.addTab(self.tab_vencimento, "Próximos ao Vencimento")
        
        layout.addWidget(self.tabs)
        
        # Configurações de desconto
        desconto_group = QFrame()
        desconto_layout = QHBoxLayout(desconto_group)
        
        desconto_label = QLabel("Taxa de Desconto Padrão:")
        self.taxa_desconto_input = QDoubleSpinBox()
        self.taxa_desconto_input.setRange(0, 100)
        self.taxa_desconto_input.setSuffix("%")
        self.taxa_desconto_input.setValue(10)  # 10% de desconto padrão
        self.taxa_desconto_input.valueChanged.connect(self.atualizar_precos_promocionais)
        
        desconto_layout.addWidget(desconto_label)
        desconto_layout.addWidget(self.taxa_desconto_input)
        desconto_layout.addStretch()
        
        layout.addWidget(desconto_group)
        
        # Botões
        buttons_layout = QHBoxLayout()
        self.aplicar_button = QPushButton("Aplicar Promoções Selecionadas")
        self.aplicar_button.clicked.connect(self.aplicar_promocoes)
        self.cancelar_button = QPushButton("Cancelar")
        self.cancelar_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.aplicar_button)
        buttons_layout.addWidget(self.cancelar_button)
        
        layout.addLayout(buttons_layout)
    
    def setup_tab_estoque_baixo(self):
        layout = QVBoxLayout(self.tab_estoque_baixo)
        
        # Tabela de produtos com estoque baixo
        self.tabela_estoque_baixo = QTableWidget()
        self.tabela_estoque_baixo.setColumnCount(8)
        self.tabela_estoque_baixo.setHorizontalHeaderLabels([
            "Selecionar", "ID", "Produto", "Quantidade", "Estoque Mínimo", 
            "Preço Atual", "Taxa de Desconto", "Preço Promocional"
        ])
        self.tabela_estoque_baixo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_estoque_baixo.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabela_estoque_baixo)
    
    def setup_tab_vencimento(self):
        layout = QVBoxLayout(self.tab_vencimento)
        
        periodo_layout = QHBoxLayout()
        periodo_label = QLabel("Considerar produtos que vencem em:")
        self.periodo_combo = QComboBox()
        self.periodo_combo.addItem("7 dias", 7)
        self.periodo_combo.addItem("15 dias", 15)
        self.periodo_combo.addItem("30 dias", 30)
        self.periodo_combo.addItem("60 dias", 60)
        self.periodo_combo.setCurrentIndex(2)  # 30 dias como padrão
        self.periodo_combo.currentIndexChanged.connect(self.carregar_produtos_vencimento)
        
        periodo_layout.addWidget(periodo_label)
        periodo_layout.addWidget(self.periodo_combo)
        periodo_layout.addStretch()
        
        layout.addLayout(periodo_layout)
        
        # Tabela de produtos próximos ao vencimento
        self.tabela_vencimento = QTableWidget()
        self.tabela_vencimento.setColumnCount(9)
        self.tabela_vencimento.setHorizontalHeaderLabels([
            "Selecionar", "ID", "Produto", "Data Validade", "Dias Restantes", "Quantidade",
            "Preço Atual", "Taxa de Desconto", "Preço Promocional"
        ])
        self.tabela_vencimento.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabela_vencimento.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.tabela_vencimento)
    
    def carregar_produtos_especiais(self):
        """Carrega os produtos com estoque baixo e próximos ao vencimento."""
        self.carregar_produtos_estoque_baixo()
        self.carregar_produtos_vencimento()
    
    def carregar_produtos_estoque_baixo(self):
        """Carrega os produtos com estoque abaixo do mínimo."""
        produtos = self.db.verificar_produtos_estoque_baixo()
        
        self.tabela_estoque_baixo.setRowCount(0)
        for row, produto in enumerate(produtos):
            self.tabela_estoque_baixo.insertRow(row)
            
            # Checkbox para selecionar
            checkbox = QWidget()
            checkbox_layout = QHBoxLayout(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            check = QRadioButton()
            check.setChecked(False)
            checkbox_layout.addWidget(check)
            
            # Calcular preço promocional com o desconto atual
            preco_atual = produto['preco_venda']
            taxa_desconto = self.taxa_desconto_input.value()
            preco_promocional = preco_atual * (1 - taxa_desconto / 100)
            
            # Adicionar itens à tabela
            self.tabela_estoque_baixo.setCellWidget(row, 0, checkbox)
            self.tabela_estoque_baixo.setItem(row, 1, QTableWidgetItem(str(produto['id'])))
            self.tabela_estoque_baixo.setItem(row, 2, QTableWidgetItem(produto['nome']))
            self.tabela_estoque_baixo.setItem(row, 3, QTableWidgetItem(str(produto['quantidade'])))
            self.tabela_estoque_baixo.setItem(row, 4, QTableWidgetItem(str(produto['estoque_minimo'])))
            self.tabela_estoque_baixo.setItem(row, 5, QTableWidgetItem(f"R$ {preco_atual:.2f}"))
            
            # Adicionar spin box para taxa de desconto personalizada
            taxa_desconto_widget = QWidget()
            taxa_layout = QHBoxLayout(taxa_desconto_widget)
            taxa_layout.setContentsMargins(0, 0, 0, 0)
            
            taxa_spin = QDoubleSpinBox()
            taxa_spin.setRange(0, 100)
            taxa_spin.setSuffix("%")
            taxa_spin.setValue(taxa_desconto)
            taxa_spin.valueChanged.connect(lambda value, r=row: self.atualizar_preco_promocional_item(r, value))
            
            taxa_layout.addWidget(taxa_spin)
            self.tabela_estoque_baixo.setCellWidget(row, 6, taxa_desconto_widget)
            
            self.tabela_estoque_baixo.setItem(row, 7, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
    
    def carregar_produtos_vencimento(self):
        """Carrega os produtos próximos ao vencimento."""
        dias = self.periodo_combo.currentData()
        produtos = self.db.verificar_produtos_vencendo(dias)
        
        self.tabela_vencimento.setRowCount(0)
        hoje = datetime.now().date()
        
        for row, produto in enumerate(produtos):
            self.tabela_vencimento.insertRow(row)
            
            # Checkbox para selecionar
            checkbox = QWidget()
            checkbox_layout = QHBoxLayout(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            
            check = QRadioButton()
            check.setChecked(False)
            checkbox_layout.addWidget(check)
            
            # Calcular dias restantes até o vencimento
            data_validade = datetime.strptime(produto['data_validade'], '%Y-%m-%d').date()
            dias_restantes = (data_validade - hoje).days
            
            # Calcular taxa de desconto sugerida com base nos dias restantes
            # Quanto mais próximo do vencimento, maior o desconto
            taxa_desconto_sugerida = min(50, int(50 * (1 - dias_restantes / dias))) if dias_restantes > 0 else 50
            
            # Calcular preço promocional
            preco_atual = produto['preco_venda']
            preco_promocional = preco_atual * (1 - taxa_desconto_sugerida / 100)
            
            # Adicionar itens à tabela
            self.tabela_vencimento.setCellWidget(row, 0, checkbox)
            self.tabela_vencimento.setItem(row, 1, QTableWidgetItem(str(produto['id'])))
            self.tabela_vencimento.setItem(row, 2, QTableWidgetItem(produto['nome']))
            self.tabela_vencimento.setItem(row, 3, QTableWidgetItem(produto['data_validade']))
            self.tabela_vencimento.setItem(row, 4, QTableWidgetItem(str(dias_restantes)))
            self.tabela_vencimento.setItem(row, 5, QTableWidgetItem(str(produto['quantidade'])))
            self.tabela_vencimento.setItem(row, 6, QTableWidgetItem(f"R$ {preco_atual:.2f}"))
            
            # Adicionar spin box para taxa de desconto personalizada
            taxa_desconto_widget = QWidget()
            taxa_layout = QHBoxLayout(taxa_desconto_widget)
            taxa_layout.setContentsMargins(0, 0, 0, 0)
            
            taxa_spin = QDoubleSpinBox()
            taxa_spin.setRange(0, 100)
            taxa_spin.setSuffix("%")
            taxa_spin.setValue(taxa_desconto_sugerida)
            taxa_spin.valueChanged.connect(lambda value, r=row: self.atualizar_preco_promocional_vencimento(r, value))
            
            taxa_layout.addWidget(taxa_spin)
            self.tabela_vencimento.setCellWidget(row, 7, taxa_desconto_widget)
            
            self.tabela_vencimento.setItem(row, 8, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
    
    def atualizar_precos_promocionais(self):
        """Atualiza os preços promocionais com base na taxa de desconto padrão."""
        # Atualiza tabela de estoque baixo
        for row in range(self.tabela_estoque_baixo.rowCount()):
            taxa_widget = self.tabela_estoque_baixo.cellWidget(row, 6)
            if taxa_widget:
                taxa_spin = taxa_widget.findChild(QDoubleSpinBox)
                if taxa_spin:
                    taxa_spin.setValue(self.taxa_desconto_input.value())
        
        # Não atualiza a tabela de vencimento, pois ela tem taxas personalizadas por dias restantes
    
    def atualizar_preco_promocional_item(self, row, taxa_desconto):
        """Atualiza o preço promocional de um item específico na tabela de estoque baixo."""
        preco_texto = self.tabela_estoque_baixo.item(row, 5).text().replace('R$', '').strip()
        try:
            preco_atual = float(preco_texto)
            preco_promocional = preco_atual * (1 - taxa_desconto / 100)
            self.tabela_estoque_baixo.setItem(row, 7, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
        except ValueError:
            pass
    
    def atualizar_preco_promocional_vencimento(self, row, taxa_desconto):
        """Atualiza o preço promocional de um item específico na tabela de vencimento."""
        preco_texto = self.tabela_vencimento.item(row, 6).text().replace('R$', '').strip()
        try:
            preco_atual = float(preco_texto)
            preco_promocional = preco_atual * (1 - taxa_desconto / 100)
            self.tabela_vencimento.setItem(row, 8, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
        except ValueError:
            pass
    
    def aplicar_promocoes(self):
        """Aplica as promoções para os produtos selecionados."""
        produtos_selecionados = []
        
        # Verificar produtos selecionados na aba de estoque baixo
        if self.tabs.currentIndex() == 0:
            for row in range(self.tabela_estoque_baixo.rowCount()):
                checkbox_widget = self.tabela_estoque_baixo.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QRadioButton)
                    if checkbox and checkbox.isChecked():
                        produto_id = int(self.tabela_estoque_baixo.item(row, 1).text())
                        preco_antigo = float(self.tabela_estoque_baixo.item(row, 5).text().replace('R$', '').strip())
                        taxa_widget = self.tabela_estoque_baixo.cellWidget(row, 6)
                        taxa_spin = taxa_widget.findChild(QDoubleSpinBox)
                        taxa_desconto = taxa_spin.value()
                        preco_promocional = float(self.tabela_estoque_baixo.item(row, 7).text().replace('R$', '').strip())
                        
                        produtos_selecionados.append({
                            'produto_id': produto_id,
                            'preco_antigo': preco_antigo,
                            'preco_promocional': preco_promocional,
                            'descricao': f"Promoção por estoque baixo - {taxa_desconto:.1f}% de desconto"
                        })
        
        # Verificar produtos selecionados na aba de vencimento
        elif self.tabs.currentIndex() == 1:
            for row in range(self.tabela_vencimento.rowCount()):
                checkbox_widget = self.tabela_vencimento.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QRadioButton)
                    if checkbox and checkbox.isChecked():
                        produto_id = int(self.tabela_vencimento.item(row, 1).text())
                        data_validade = self.tabela_vencimento.item(row, 3).text()
                        preco_antigo = float(self.tabela_vencimento.item(row, 6).text().replace('R$', '').strip())
                        taxa_widget = self.tabela_vencimento.cellWidget(row, 7)
                        taxa_spin = taxa_widget.findChild(QDoubleSpinBox)
                        taxa_desconto = taxa_spin.value()
                        preco_promocional = float(self.tabela_vencimento.item(row, 8).text().replace('R$', '').strip())
                        
                        produtos_selecionados.append({
                            'produto_id': produto_id,
                            'preco_antigo': preco_antigo,
                            'preco_promocional': preco_promocional,
                            'descricao': f"Promoção por vencimento em {data_validade} - {taxa_desconto:.1f}% de desconto"
                        })
        
        # Se não há produtos selecionados, mostrar aviso
        if not produtos_selecionados:
            QMessageBox.warning(self, "Aviso", "Nenhum produto selecionado!")
            return
        
        # Confirmar aplicação das promoções
        confirmacao = QMessageBox.question(
            self,
            "Confirmar Promoções",
            f"Deseja aplicar promoções para {len(produtos_selecionados)} produtos?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            # Data atual e data fim (30 dias por padrão)
            data_inicio = datetime.now().strftime('%Y-%m-%d')
            data_fim = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            
            # Cadastrar as promoções
            sucesso = True
            for produto in produtos_selecionados:
                resultado = self.db.adicionar_promocao(
                    produto['produto_id'],
                    produto['preco_antigo'],
                    produto['preco_promocional'],
                    data_inicio,
                    data_fim,
                    produto['descricao']
                )
                if not resultado:
                    sucesso = False
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", "Promoções aplicadas com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Ocorreu um erro ao aplicar algumas promoções.")


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
        
        self.preco_antigo_input = QDoubleSpinBox()
        self.preco_antigo_input.setRange(0, 99999.99)
        self.preco_antigo_input.setPrefix("R$ ")
        self.preco_antigo_input.setDecimals(2)
        
        # Nova taxa de desconto
        self.taxa_desconto_input = QDoubleSpinBox()
        self.taxa_desconto_input.setRange(0, 100)
        self.taxa_desconto_input.setSuffix("%")
        self.taxa_desconto_input.setValue(10)  # 10% de desconto padrão
        self.taxa_desconto_input.valueChanged.connect(self.calcular_preco_promocional)
        
        self.preco_promocional_input = QDoubleSpinBox()
        self.preco_promocional_input.setRange(0, 99999.99)
        self.preco_promocional_input.setPrefix("R$ ")
        self.preco_promocional_input.setDecimals(2)
        self.preco_promocional_input.valueChanged.connect(self.calcular_taxa_desconto)
        
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
        form_layout.addRow("Taxa de Desconto:", self.taxa_desconto_input)
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
    
    def calcular_preco_promocional(self):
        """Calcula o preço promocional com base na taxa de desconto."""
        preco_antigo = self.preco_antigo_input.value()
        taxa_desconto = self.taxa_desconto_input.value()
        
        # Cálculo do preço promocional com base no desconto
        preco_promocional = preco_antigo * (1 - taxa_desconto / 100)
        
        # Atualiza o campo do preço promocional bloqueando temporariamente o sinal
        # para evitar recursão infinita com calcular_taxa_desconto
        self.preco_promocional_input.blockSignals(True)
        self.preco_promocional_input.setValue(preco_promocional)
        self.preco_promocional_input.blockSignals(False)

    def calcular_taxa_desconto(self):
        """Calcula a taxa de desconto com base no preço promocional."""
        preco_antigo = self.preco_antigo_input.value()
        preco_promocional = self.preco_promocional_input.value()
        
        # Evitar divisão por zero
        if preco_antigo > 0:
            # Cálculo da taxa de desconto
            taxa_desconto = ((preco_antigo - preco_promocional) / preco_antigo) * 100
            
            # Atualiza o campo da taxa de desconto bloqueando temporariamente o sinal
            # para evitar recursão infinita com calcular_preco_promocional
            self.taxa_desconto_input.blockSignals(True)
            self.taxa_desconto_input.setValue(taxa_desconto)
            self.taxa_desconto_input.blockSignals(False)

    def atualizar_preco_antigo(self):
        """Atualiza o preço antigo do produto quando um produto é selecionado."""
        produto_id = self.produto_combo.currentData()
        
        if produto_id:
            # Obter o preço atual do produto do banco de dados
            produto = self.db.obter_produto(produto_id)
            if produto:
                self.preco_antigo_input.setValue(produto['preco_venda'])
                # Recalcular o preço promocional com base na taxa de desconto atual
                self.calcular_preco_promocional()
        else:
            # Limpar o campo se nenhum produto estiver selecionado
            self.preco_antigo_input.setValue(0)
            self.preco_promocional_input.setValue(0)
    
    def salvar_promocao(self):
        """Salva a promoção no banco de dados."""
        # Obter os valores dos campos
        produto_id = self.produto_combo.currentData()
        preco_antigo = self.preco_antigo_input.value()
        preco_promocional = self.preco_promocional_input.value()
        data_inicio = self.data_inicio_input.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim_input.date().toString("yyyy-MM-dd")
        descricao = self.descricao_input.text()
        
        # Validar os campos
        if not produto_id:
            QMessageBox.warning(self, "Erro", "Selecione um produto!")
            return
        
        if preco_antigo <= 0:
            QMessageBox.warning(self, "Erro", "O preço antigo deve ser maior que zero!")
            return
        
        if preco_promocional <= 0:
            QMessageBox.warning(self, "Erro", "O preço promocional deve ser maior que zero!")
            return
        
        if preco_promocional >= preco_antigo:
            QMessageBox.warning(self, "Erro", "O preço promocional deve ser menor que o preço antigo!")
            return
        
        # Pegar as datas como objetos QDate
        data_inicio_qdate = self.data_inicio_input.date()
        data_fim_qdate = self.data_fim_input.date()
        
        # Validar datas
        if data_inicio_qdate > data_fim_qdate:
            QMessageBox.warning(self, "Erro", "A data de início deve ser anterior à data de fim!")
            return
        
        # Salvar promoção no banco de dados
        if self.promocao_id:
            # Atualizar promoção existente
            resultado = self.db.atualizar_promocao(
                self.promocao_id,
                produto_id,
                preco_antigo,
                preco_promocional,
                data_inicio,
                data_fim,
                descricao
            )
            mensagem = "Promoção atualizada com sucesso!" if resultado else "Erro ao atualizar promoção!"
        else:
            # Adicionar nova promoção
            resultado = self.db.adicionar_promocao(
                produto_id,
                preco_antigo,
                preco_promocional,
                data_inicio,
                data_fim,
                descricao
            )
            mensagem = "Promoção adicionada com sucesso!" if resultado else "Erro ao adicionar promoção!"
        
        if resultado:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()  # Fecha o diálogo com código de sucesso
        else:
            QMessageBox.warning(self, "Erro", mensagem)

    def carregar_dados_promocao(self):
        """Carrega os dados da promoção para edição."""
        if not self.promocao:
            return
        
        # Encontrar e selecionar o produto
        index = self.produto_combo.findData(self.promocao['produto_id'])
        if index >= 0:
            self.produto_combo.setCurrentIndex(index)
        
        # Definir os valores nos campos
        self.preco_antigo_input.setValue(self.promocao['preco_antigo'])
        self.preco_promocional_input.setValue(self.promocao['preco_promocional'])
        
        # Calcular a taxa de desconto
        self.calcular_taxa_desconto()
        
        # Definir datas
        data_inicio = QDate.fromString(self.promocao['data_inicio'], "yyyy-MM-dd")
        data_fim = QDate.fromString(self.promocao['data_fim'], "yyyy-MM-dd")
        
        self.data_inicio_input.setDate(data_inicio)
        self.data_fim_input.setDate(data_fim)
        
        # Definir descrição
        self.descricao_input.setText(self.promocao['descricao'])

    def carregar_produtos(self):
        """Carrega a lista de produtos para o combobox."""
        self.produto_combo.clear()
        self.produto_combo.addItem("Selecione um produto", None)
        
        # Primeiro adicionar produtos com estoque baixo
        produtos_estoque_baixo = self.db.verificar_produtos_estoque_baixo()
        if produtos_estoque_baixo:
            self.produto_combo.insertSeparator(1)
            self.produto_combo.addItem("--- PRODUTOS COM ESTOQUE BAIXO ---", None)
            for produto in produtos_estoque_baixo:
                self.produto_combo.addItem(f"{produto['nome']} (Estoque: {produto['quantidade']})", produto['id'])
        
        # Depois adicionar produtos próximos ao vencimento (30 dias)
        produtos_vencendo = self.db.verificar_produtos_vencendo(30)
        if produtos_vencendo:
            self.produto_combo.insertSeparator(self.produto_combo.count())
            self.produto_combo.addItem("--- PRODUTOS PRÓXIMOS AO VENCIMENTO ---", None)
            for produto in produtos_vencendo:
                data_validade = produto['data_validade']
                self.produto_combo.addItem(f"{produto['nome']} (Validade: {data_validade})", produto['id'])
        
        # Adicionar todos os outros produtos
        self.produto_combo.insertSeparator(self.produto_combo.count())
        self.produto_combo.addItem("--- TODOS OS PRODUTOS ---", None)
        produtos = self.db.listar_produtos()
        for produto in produtos:
            if not any(p['id'] == produto['id'] for p in produtos_estoque_baixo) and \
               not any(p['id'] == produto['id'] for p in produtos_vencendo):
                self.produto_combo.addItem(produto['nome'], produto['id'])