from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QSpinBox,
                           QDoubleSpinBox, QDialog, QFrame, QToolButton, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush
import os
from datetime import datetime, timedelta

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
        
        # Área de pesquisa e filtros
        search_group = QGroupBox("Pesquisa e Filtros")
        search_layout = QVBoxLayout(search_group)
        
        # Linha de pesquisa
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar produto por nome, descrição ou código de barras...")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.pesquisar_produtos)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)
        search_layout.addLayout(search_input_layout)
        
        # Linha de filtros
        filter_layout = QHBoxLayout()
        
        # Filtro de estoque
        self.estoque_combo = QComboBox()
        self.estoque_combo.addItem("Todos os níveis", "todos")
        self.estoque_combo.addItem("Estoque Baixo", "baixo")
        self.estoque_combo.addItem("Estoque Médio", "medio")
        self.estoque_combo.addItem("Estoque Alto", "alto")
        filter_layout.addWidget(QLabel("Nível de Estoque:"))
        filter_layout.addWidget(self.estoque_combo)
        
        # Filtro de vencimento
        self.vencimento_combo = QComboBox()
        self.vencimento_combo.addItem("Todos", "todos")
        self.vencimento_combo.addItem("Vence em 30 dias", "30")
        self.vencimento_combo.addItem("Vence em 15 dias", "15")
        self.vencimento_combo.addItem("Vencidos", "vencidos")
        filter_layout.addWidget(QLabel("Vencimento:"))
        filter_layout.addWidget(self.vencimento_combo)
        
        # Botão de aplicar filtros
        self.aplicar_filtro_btn = QPushButton("Aplicar Filtros")
        self.aplicar_filtro_btn.clicked.connect(self.aplicar_filtros)
        filter_layout.addWidget(self.aplicar_filtro_btn)
        
        # Botão para limpar filtros
        self.limpar_filtro_btn = QPushButton("Limpar Filtros")
        self.limpar_filtro_btn.clicked.connect(self.limpar_filtros)
        filter_layout.addWidget(self.limpar_filtro_btn)
        
        search_layout.addLayout(filter_layout)
        layout.addWidget(search_group)
        
        # Legenda dos ícones
        legenda_layout = QHBoxLayout()
        
        # Ícone de estoque baixo
        estoque_baixo_label = QLabel("Estoque Baixo")
        estoque_baixo_label.setStyleSheet("color: red;")
        legenda_layout.addWidget(estoque_baixo_label)
        
        # Ícone de vencimento em 30 dias
        vencimento_30_label = QLabel("Vence em 30 dias")
        vencimento_30_label.setStyleSheet("color: orange;")
        legenda_layout.addWidget(vencimento_30_label)
        
        # Ícone de vencimento em 15 dias
        vencimento_15_label = QLabel("Vence em 15 dias")
        vencimento_15_label.setStyleSheet("color: red;")
        legenda_layout.addWidget(vencimento_15_label)
        
        legenda_layout.addStretch()
        layout.addLayout(legenda_layout)
        
        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(12)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Código de Barras", "Nome", "Quantidade", "Estoque Mín.", 
            "Preço Compra", "Margem %", "Preço Venda", "Validade", 
            "Localização", "Fornecedor", "Ações"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Produto")
        self.add_button.clicked.connect(self.abrir_formulario_produto)
        
        self.relatorio_btn = QPushButton("Relatório de Vencimentos")
        self.relatorio_btn.clicked.connect(self.relatorio_vencimentos)
        
        self.relatorio_estoque_btn = QPushButton("Relatório de Estoque Baixo")
        self.relatorio_estoque_btn.clicked.connect(self.relatorio_estoque_baixo)
        
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.relatorio_btn)
        action_layout.addWidget(self.relatorio_estoque_btn)
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
    
    def aplicar_filtros(self):
        """Aplica os filtros selecionados."""
        filtro_estoque = self.estoque_combo.currentData()
        filtro_vencimento = self.vencimento_combo.currentData()
        
        produtos = self.db.filtrar_produtos(filtro_estoque, filtro_vencimento)
        self.atualizar_tabela(produtos)
    
    def limpar_filtros(self):
        """Limpa todos os filtros aplicados."""
        self.estoque_combo.setCurrentIndex(0)
        self.vencimento_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.carregar_dados()
    
    def atualizar_tabela(self, produtos):
        """Atualiza a tabela com os produtos fornecidos."""
        self.tabela.setRowCount(0)
        
        hoje = datetime.now().date()
        
        for row, produto in enumerate(produtos):
            self.tabela.insertRow(row)
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(produto['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto['codigo_barras'] or ""))
            
            # Nome do produto
            nome_item = QTableWidgetItem(produto['nome'])
            self.tabela.setItem(row, 2, nome_item)
            
            # Quantidade
            quantidade_item = QTableWidgetItem(str(produto['quantidade']))
            estoque_minimo = produto['estoque_minimo'] or 0
            
            # Verificar se está abaixo do estoque mínimo
            if produto['quantidade'] <= estoque_minimo:
                quantidade_item.setForeground(QBrush(QColor('red')))
                quantidade_item.setToolTip("Estoque abaixo do mínimo!")
            
            self.tabela.setItem(row, 3, quantidade_item)
            self.tabela.setItem(row, 4, QTableWidgetItem(str(estoque_minimo)))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {produto['preco_compra']:.2f}"))
            
            # Margem de lucro
            margem = produto['margem_lucro'] or 0
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{margem:.2f}%"))
            
            self.tabela.setItem(row, 7, QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}"))
            
            # Data de validade
            validade_item = QTableWidgetItem(str(produto['data_validade'] or ""))
            
            # Verificar vencimento
            if produto['data_validade']:
                try:
                    data_validade = datetime.strptime(produto['data_validade'], "%Y-%m-%d").date()
                    dias_para_vencer = (data_validade - hoje).days
                    
                    if dias_para_vencer <= 0:
                        # Produto vencido
                        validade_item.setForeground(QBrush(QColor('darkred')))
                        validade_item.setToolTip("Produto VENCIDO!")
                    elif dias_para_vencer <= 15:
                        # Vence em 15 dias ou menos
                        validade_item.setForeground(QBrush(QColor('red')))
                        validade_item.setToolTip(f"Vence em {dias_para_vencer} dias!")
                    elif dias_para_vencer <= 30:
                        # Vence em 30 dias ou menos
                        validade_item.setForeground(QBrush(QColor('orange')))
                        validade_item.setToolTip(f"Vence em {dias_para_vencer} dias!")
                except:
                    pass
            
            self.tabela.setItem(row, 8, validade_item)
            self.tabela.setItem(row, 9, QTableWidgetItem(produto['localizacao'] or ""))
            
            fornecedor_nome = produto['fornecedor_nome'] if produto['fornecedor_nome'] else "N/A"
            self.tabela.setItem(row, 10, QTableWidgetItem(fornecedor_nome))
            
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
            
            self.tabela.setCellWidget(row, 11, acoes_widget)
    
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
    
    def relatorio_vencimentos(self):
        """Gera relatório de produtos próximos ao vencimento."""
        produtos = self.db.verificar_produtos_vencendo(dias=30)
        
        if not produtos:
            QMessageBox.information(self, "Relatório", "Não há produtos próximos do vencimento nos próximos 30 dias.")
            return
        
        msg = "Produtos que vencerão nos próximos 30 dias:\n\n"
        for produto in produtos:
            dias_para_vencer = (datetime.strptime(produto['data_validade'], "%Y-%m-%d").date() - datetime.now().date()).days
            msg += f"• {produto['nome']} - Vencimento: {produto['data_validade']} (em {dias_para_vencer} dias)\n"
        
        QMessageBox.information(self, "Relatório de Vencimentos", msg)
    
    def relatorio_estoque_baixo(self):
        """Gera relatório de produtos com estoque baixo."""
        produtos = self.db.verificar_produtos_estoque_baixo()
        
        if not produtos:
            QMessageBox.information(self, "Relatório", "Não há produtos com estoque abaixo do mínimo.")
            return
        
        msg = "Produtos com estoque abaixo do mínimo:\n\n"
        for produto in produtos:
            estoque_minimo = produto['estoque_minimo'] or 0
            msg += f"• {produto['nome']} - Quantidade: {produto['quantidade']} (Mínimo: {estoque_minimo})\n"
        
        QMessageBox.information(self, "Relatório de Estoque Baixo", msg)


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
        self.codigo_barras_input = QLineEdit()
        self.nome_input = QLineEdit()
        self.descricao_input = QLineEdit()
        
        # Quantidade
        self.quantidade_input = QSpinBox()
        self.quantidade_input.setRange(0, 99999)
        
        # Estoque mínimo
        self.estoque_minimo_input = QSpinBox()
        self.estoque_minimo_input.setRange(0, 99999)
        
        # Preço de compra
        self.preco_compra_input = QDoubleSpinBox()
        self.preco_compra_input.setRange(0, 99999.99)
        self.preco_compra_input.setPrefix("R$ ")
        self.preco_compra_input.setDecimals(2)
        self.preco_compra_input.valueChanged.connect(self.calcular_preco_venda)
        
        # Margem de lucro
        self.margem_lucro_input = QDoubleSpinBox()
        self.margem_lucro_input.setRange(0, 999.99)
        self.margem_lucro_input.setSuffix("%")
        self.margem_lucro_input.setDecimals(2)
        self.margem_lucro_input.setValue(30.0)  # Valor padrão de 30%
        self.margem_lucro_input.valueChanged.connect(self.calcular_preco_venda)
        
        # Preço de venda
        self.preco_venda_input = QDoubleSpinBox()
        self.preco_venda_input.setRange(0, 99999.99)
        self.preco_venda_input.setPrefix("R$ ")
        self.preco_venda_input.setDecimals(2)
        self.preco_venda_input.valueChanged.connect(self.calcular_margem_lucro)
        
        # Data de validade
        self.data_validade_input = QDateEdit()
        self.data_validade_input.setDisplayFormat("dd/MM/yyyy")
        self.data_validade_input.setCalendarPopup(True)
        self.data_validade_input.setDate(QDate.currentDate().addDays(30))  # Default para 30 dias
        
        self.localizacao_input = QLineEdit()
        
        self.fornecedor_combo = QComboBox()
        self.carregar_fornecedores()
        
        # Adicionar campos ao formulário
        form_layout.addRow("Código de Barras:", self.codigo_barras_input)
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Descrição:", self.descricao_input)
        form_layout.addRow("Quantidade:", self.quantidade_input)
        form_layout.addRow("Estoque Mínimo:", self.estoque_minimo_input)
        form_layout.addRow("Preço de Compra:", self.preco_compra_input)
        form_layout.addRow("Margem de Lucro:", self.margem_lucro_input)
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
    
    def calcular_preco_venda(self):
        """Calcula o preço de venda com base no preço de compra e margem de lucro."""
        preco_compra = self.preco_compra_input.value()
        margem = self.margem_lucro_input.value() / 100
        
        # Evitar sinal de mudança recursivo
        self.preco_venda_input.blockSignals(True)
        self.preco_venda_input.setValue(preco_compra * (1 + margem))
        self.preco_venda_input.blockSignals(False)
    
    def calcular_margem_lucro(self):
        """Calcula a margem de lucro com base no preço de compra e preço de venda."""
        preco_compra = self.preco_compra_input.value()
        preco_venda = self.preco_venda_input.value()
        
        if preco_compra > 0:
            margem = ((preco_venda / preco_compra) - 1) * 100
            
            # Evitar sinal de mudança recursivo
            self.margem_lucro_input.blockSignals(True)
            self.margem_lucro_input.setValue(margem)
            self.margem_lucro_input.blockSignals(False)
    
    def carregar_fornecedores(self):
        """Carrega a lista de fornecedores para o combobox."""
        self.fornecedor_combo.clear()
        self.fornecedor_combo.addItem("Selecione um fornecedor", None)
        
        fornecedores = self.db.listar_fornecedores()
        for fornecedor in fornecedores:
            self.fornecedor_combo.addItem(fornecedor['nome'], fornecedor['id'])
    
    def carregar_dados_produto(self):
        """Carrega os dados do produto nos campos do formulário."""
        self.codigo_barras_input.setText(self.produto['codigo_barras'] or "")
        self.nome_input.setText(self.produto['nome'])
        self.descricao_input.setText(self.produto['descricao'] or "")
        self.quantidade_input.setValue(self.produto['quantidade'])
        self.estoque_minimo_input.setValue(self.produto['estoque_minimo'] or 0)
        self.preco_compra_input.setValue(self.produto['preco_compra'])
        
        # Bloquear sinais para evitar cálculos em cascata durante o carregamento
        self.margem_lucro_input.blockSignals(True)
        self.preco_venda_input.blockSignals(True)
        
        self.margem_lucro_input.setValue(self.produto['margem_lucro'] or 30.0)
        self.preco_venda_input.setValue(self.produto['preco_venda'])
        
        # Desbloquear sinais
        self.margem_lucro_input.blockSignals(False)
        self.preco_venda_input.blockSignals(False)
        
        if self.produto['data_validade']:
            data_validade = QDate.fromString(self.produto['data_validade'], "yyyy-MM-dd")
            self.data_validade_input.setDate(data_validade)
        
        self.localizacao_input.setText(self.produto['localizacao'] or "")
        
        # Selecionar o fornecedor
        if self.produto['fornecedor_id']:
            index = self.fornecedor_combo.findData(self.produto['fornecedor_id'])
            if index != -1:
                self.fornecedor_combo.setCurrentIndex(index)
    
    def salvar_produto(self):
        """Salva os dados do produto no banco de dados."""
        # Validar campos obrigatórios
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do produto é obrigatório!")
            return
        
        # Coletar dados do formulário
        codigo_barras = self.codigo_barras_input.text().strip()
        nome = self.nome_input.text().strip()
        descricao = self.descricao_input.text().strip()
        quantidade = self.quantidade_input.value()
        estoque_minimo = self.estoque_minimo_input.value()
        preco_compra = self.preco_compra_input.value()
        margem_lucro = self.margem_lucro_input.value()
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
                    self.produto_id, codigo_barras, nome, descricao, quantidade, 
                    estoque_minimo, preco_compra, margem_lucro, preco_venda, 
                    data_validade, localizacao, fornecedor_id
                )
                mensagem = "Produto atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_produto(
                    codigo_barras, nome, descricao, quantidade, estoque_minimo,
                    preco_compra, margem_lucro, preco_venda, data_validade, 
                    localizacao, fornecedor_id
                )
                mensagem = "Produto cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o produto.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar produto: {str(e)}")