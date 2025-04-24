from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
                            QMessageBox, QDialog, QFormLayout, QTextEdit, QDoubleSpinBox,
                            QSpinBox, QHeaderView, QCheckBox, QGroupBox, QGridLayout, QFrame,
                            QSplitter, QApplication)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon, QColor, QFont
import datetime

class CaixaWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.caixa_atual = None
        self.itens_venda = []
        self.total_venda = 0.0
        self.initUI()
        self.verificar_caixa_aberto()
        self.carregar_clientes()
        self.carregar_produtos()
    
    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Status do caixa
        self.frame_status = QFrame()
        self.frame_status.setFrameShape(QFrame.StyledPanel)
        self.frame_status.setFrameShadow(QFrame.Raised)
        self.frame_status.setStyleSheet("background-color: #f5f5f5; padding: 10px;")
        
        status_layout = QHBoxLayout(self.frame_status)
        
        self.lbl_status = QLabel("Status do Caixa: Fechado")
        self.lbl_status.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.lbl_status)
        
        self.lbl_saldo = QLabel("Saldo Atual: R$ 0,00")
        self.lbl_saldo.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.lbl_saldo)
        
        self.btn_abrir_caixa = QPushButton("Abrir Caixa")
        self.btn_abrir_caixa.clicked.connect(self.abrir_caixa)
        status_layout.addWidget(self.btn_abrir_caixa)
        
        self.btn_fechar_caixa = QPushButton("Fechar Caixa")
        self.btn_fechar_caixa.setEnabled(False)
        self.btn_fechar_caixa.clicked.connect(self.fechar_caixa)
        status_layout.addWidget(self.btn_fechar_caixa)
        
        main_layout.addWidget(self.frame_status)
        
        # Tabs para operações
        self.tabs = QTabWidget()
        
        # Tab de Vendas (PDV)
        self.tab_vendas = QWidget()
        self.setup_vendas_tab()
        self.tabs.addTab(self.tab_vendas, "Vendas (PDV)")
        
        # Tab de Movimentações
        self.tab_movimentos = QWidget()
        self.setup_movimentos_tab()
        self.tabs.addTab(self.tab_movimentos, "Movimentações")
        
        # Tab de Relatórios
        self.tab_relatorios = QWidget()
        self.setup_relatorios_tab()
        self.tabs.addTab(self.tab_relatorios, "Relatórios de Caixa")
        
        main_layout.addWidget(self.tabs)
    
    def setup_vendas_tab(self):
        layout = QVBoxLayout(self.tab_vendas)
        
        # Frame superior com informações da venda
        frame_info = QFrame()
        frame_info.setFrameShape(QFrame.StyledPanel)
        frame_info_layout = QGridLayout(frame_info)
        
        # Cliente
        frame_info_layout.addWidget(QLabel("Cliente:"), 0, 0)
        self.cb_cliente = QComboBox()
        self.cb_cliente.setMinimumWidth(200)
        frame_info_layout.addWidget(self.cb_cliente, 0, 1)
        
        # Adicionar cliente
        btn_add_cliente = QPushButton("+")
        btn_add_cliente.setMaximumWidth(30)
        btn_add_cliente.clicked.connect(self.adicionar_novo_cliente)
        frame_info_layout.addWidget(btn_add_cliente, 0, 2)
        
        # Busca de produtos
        frame_info_layout.addWidget(QLabel("Produto:"), 1, 0)
        self.cb_produto = QComboBox()
        self.cb_produto.setMinimumWidth(200)
        self.cb_produto.setEditable(True)
        self.cb_produto.setInsertPolicy(QComboBox.NoInsert)
        frame_info_layout.addWidget(self.cb_produto, 1, 1, 1, 2)
        
        # Quantidade
        frame_info_layout.addWidget(QLabel("Quantidade:"), 0, 3)
        self.spin_quantidade = QSpinBox()
        self.spin_quantidade.setMinimum(1)
        self.spin_quantidade.setMaximum(9999)
        frame_info_layout.addWidget(self.spin_quantidade, 0, 4)
        
        # Preço unitário
        frame_info_layout.addWidget(QLabel("Preço Unitário:"), 1, 3)
        self.spin_preco = QDoubleSpinBox()
        self.spin_preco.setMinimum(0)
        self.spin_preco.setMaximum(999999.99)
        self.spin_preco.setDecimals(2)
        self.spin_preco.setSingleStep(0.10)
        self.spin_preco.setPrefix("R$ ")
        frame_info_layout.addWidget(self.spin_preco, 1, 4)
        
        # Botão adicionar item
        self.btn_adicionar_item = QPushButton("Adicionar Item")
        self.btn_adicionar_item.clicked.connect(self.adicionar_item)
        frame_info_layout.addWidget(self.btn_adicionar_item, 0, 5, 2, 1)
        
        layout.addWidget(frame_info)
        
        # Tabela de itens
        self.tabela_itens = QTableWidget()
        self.tabela_itens.setColumnCount(6)
        self.tabela_itens.setHorizontalHeaderLabels(['Cód.', 'Produto', 'Qtde', 'Preço Unit.', 'Subtotal', 'Remover'])
        self.tabela_itens.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela_itens.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_itens.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_itens)
        
        # Frame inferior com total e finalização
        frame_total = QFrame()
        frame_total.setFrameShape(QFrame.StyledPanel)
        frame_total_layout = QHBoxLayout(frame_total)
        
        # Total da venda
        self.lbl_total = QLabel("Total: R$ 0,00")
        self.lbl_total.setStyleSheet("font-size: 18px; font-weight: bold;")
        frame_total_layout.addWidget(self.lbl_total)
        
        # Botões de ação
        frame_total_layout.addStretch()
        
        self.btn_limpar = QPushButton("Limpar Venda")
        self.btn_limpar.clicked.connect(self.limpar_venda)
        frame_total_layout.addWidget(self.btn_limpar)
        
        self.btn_finalizar = QPushButton("Finalizar Venda")
        self.btn_finalizar.clicked.connect(self.finalizar_venda)
        self.btn_finalizar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        frame_total_layout.addWidget(self.btn_finalizar)
        
        layout.addWidget(frame_total)
        
        # Conectar sinais
        self.cb_produto.currentIndexChanged.connect(self.produto_selecionado)
    
    def setup_movimentos_tab(self):
        layout = QVBoxLayout(self.tab_movimentos)
        
        # Frame superior com botões de ação
        frame_acoes = QFrame()
        frame_acoes_layout = QHBoxLayout(frame_acoes)
        
        self.btn_nova_entrada = QPushButton("Nova Entrada")
        self.btn_nova_entrada.clicked.connect(lambda: self.novo_movimento("Entrada"))
        frame_acoes_layout.addWidget(self.btn_nova_entrada)
        
        self.btn_nova_saida = QPushButton("Nova Saída")
        self.btn_nova_saida.clicked.connect(lambda: self.novo_movimento("Saída"))
        frame_acoes_layout.addWidget(self.btn_nova_saida)
        
        frame_acoes_layout.addStretch()
        
        # Filtros
        frame_acoes_layout.addWidget(QLabel("Data Início:"))
        self.dt_inicio = QDateEdit(QDate.currentDate())
        self.dt_inicio.setCalendarPopup(True)
        frame_acoes_layout.addWidget(self.dt_inicio)
        
        frame_acoes_layout.addWidget(QLabel("Data Fim:"))
        self.dt_fim = QDateEdit(QDate.currentDate())
        self.dt_fim.setCalendarPopup(True)
        frame_acoes_layout.addWidget(self.dt_fim)
        
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.filtrar_movimentos)
        frame_acoes_layout.addWidget(self.btn_filtrar)
        
        layout.addWidget(frame_acoes)
        
        # Tabela de movimentos
        self.tabela_movimentos = QTableWidget()
        self.tabela_movimentos.setColumnCount(6)
        self.tabela_movimentos.setHorizontalHeaderLabels(['ID', 'Data/Hora', 'Tipo', 'Descrição', 'Forma Pgto', 'Valor'])
        self.tabela_movimentos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.tabela_movimentos.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_movimentos.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_movimentos)
        
        # Frame de totais
        frame_totais = QFrame()
        frame_totais.setFrameShape(QFrame.StyledPanel)
        frame_totais.setStyleSheet("background-color: #f5f5f5;")
        frame_totais_layout = QHBoxLayout(frame_totais)
        
        self.lbl_total_entradas = QLabel("Total Entradas: R$ 0,00")
        self.lbl_total_entradas.setStyleSheet("color: green; font-weight: bold;")
        frame_totais_layout.addWidget(self.lbl_total_entradas)
        
        self.lbl_total_saidas = QLabel("Total Saídas: R$ 0,00")
        self.lbl_total_saidas.setStyleSheet("color: red; font-weight: bold;")
        frame_totais_layout.addWidget(self.lbl_total_saidas)
        
        self.lbl_saldo_periodo = QLabel("Saldo do Período: R$ 0,00")
        self.lbl_saldo_periodo.setStyleSheet("font-weight: bold;")
        frame_totais_layout.addWidget(self.lbl_saldo_periodo)
        
        layout.addWidget(frame_totais)
    
    def setup_relatorios_tab(self):
        layout = QVBoxLayout(self.tab_relatorios)
        
        # Frame superior com filtros
        frame_filtros = QFrame()
        frame_filtros.setFrameShape(QFrame.StyledPanel)
        frame_filtros_layout = QHBoxLayout(frame_filtros)
        
        frame_filtros_layout.addWidget(QLabel("Período:"))
        self.cb_periodo = QComboBox()
        self.cb_periodo.addItems(["Hoje", "Última Semana", "Último Mês", "Personalizado"])
        frame_filtros_layout.addWidget(self.cb_periodo)
        
        frame_filtros_layout.addWidget(QLabel("De:"))
        self.dt_rel_inicio = QDateEdit(QDate.currentDate())
        self.dt_rel_inicio.setCalendarPopup(True)
        frame_filtros_layout.addWidget(self.dt_rel_inicio)
        
        frame_filtros_layout.addWidget(QLabel("Até:"))
        self.dt_rel_fim = QDateEdit(QDate.currentDate())
        self.dt_rel_fim.setCalendarPopup(True)
        frame_filtros_layout.addWidget(self.dt_rel_fim)
        
        self.btn_gerar_relatorio = QPushButton("Gerar Relatório")
        self.btn_gerar_relatorio.clicked.connect(self.gerar_relatorio)
        frame_filtros_layout.addWidget(self.btn_gerar_relatorio)
        
        layout.addWidget(frame_filtros)
        
        # Tabs para relatórios específicos
        rel_tabs = QTabWidget()
        
        # Tab de resumo
        tab_resumo = QWidget()
        tab_resumo_layout = QVBoxLayout(tab_resumo)
        
        self.text_resumo = QTextEdit()
        self.text_resumo.setReadOnly(True)
        tab_resumo_layout.addWidget(self.text_resumo)
        
        rel_tabs.addTab(tab_resumo, "Resumo")
        
        # Tab de movimentos detalhados
        tab_detalhes = QWidget()
        tab_detalhes_layout = QVBoxLayout(tab_detalhes)
        
        self.tabela_rel_movimentos = QTableWidget()
        self.tabela_rel_movimentos.setColumnCount(6)
        self.tabela_rel_movimentos.setHorizontalHeaderLabels(['ID', 'Data/Hora', 'Tipo', 'Descrição', 'Forma Pgto', 'Valor'])
        self.tabela_rel_movimentos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        tab_detalhes_layout.addWidget(self.tabela_rel_movimentos)
        
        rel_tabs.addTab(tab_detalhes, "Movimentos Detalhados")
        
        # Tab de vendas
        tab_vendas = QWidget()
        tab_vendas_layout = QVBoxLayout(tab_vendas)
        
        self.tabela_rel_vendas = QTableWidget()
        self.tabela_rel_vendas.setColumnCount(6)
        self.tabela_rel_vendas.setHorizontalHeaderLabels(['ID', 'Data/Hora', 'Cliente', 'Valor Total', 'Desconto', 'Forma Pgto'])
        self.tabela_rel_vendas.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        tab_vendas_layout.addWidget(self.tabela_rel_vendas)
        
        rel_tabs.addTab(tab_vendas, "Vendas")
        
        layout.addWidget(rel_tabs)
        
        # Conectar sinais
        self.cb_periodo.currentIndexChanged.connect(self.periodo_alterado)
    
    def verificar_caixa_aberto(self):
        self.caixa_atual = self.db.obter_caixa_aberto()
        
        if self.caixa_atual:
            self.lbl_status.setText(f"Status do Caixa: Aberto (ID: {self.caixa_atual['id']})")
            self.lbl_status.setStyleSheet("font-weight: bold; color: green;")
            
            saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
            self.lbl_saldo.setText(f"Saldo Atual: R$ {saldo_atual:.2f}")
            
            self.btn_abrir_caixa.setEnabled(False)
            self.btn_fechar_caixa.setEnabled(True)
            
            # Carregar movimentos do caixa atual
            self.carregar_movimentos()
        else:
            self.lbl_status.setText("Status do Caixa: Fechado")
            self.lbl_status.setStyleSheet("font-weight: bold; color: red;")
            self.lbl_saldo.setText("Saldo Atual: R$ 0,00")
            
            self.btn_abrir_caixa.setEnabled(True)
            self.btn_fechar_caixa.setEnabled(False)
    
    def carregar_clientes(self):
        self.cb_cliente.clear()
        self.cb_cliente.addItem("Cliente Não Identificado", None)
        
        clientes = self.db.listar_clientes()
        for cliente in clientes:
            self.cb_cliente.addItem(cliente['nome'], cliente['id'])
    
    def carregar_produtos(self):
        self.cb_produto.clear()
        
        produtos = self.db.listar_produtos()
        for produto in produtos:
            # Adicionar produto com nome e seu ID
            self.cb_produto.addItem(produto['nome'], produto)
    
    def produto_selecionado(self, index):
        if index > 0:
            produto = self.cb_produto.itemData(index)
            if produto:
                self.spin_preco.setValue(produto['preco_venda'] if produto['preco_venda'] else 0)
                
                # Verificar se o produto está em promoção
                promocoes = self.db.listar_promocoes_ativas()
                for promocao in promocoes:
                    if promocao['produto_id'] == produto['id']:
                        self.spin_preco.setValue(promocao['preco_promocional'])
                        break
    
    def adicionar_item(self):
        index = self.cb_produto.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Erro", "Selecione um produto")
            return
        
        produto = self.cb_produto.itemData(index)
        if not produto:
            QMessageBox.warning(self, "Erro", "Produto inválido")
            return
        
        quantidade = self.spin_quantidade.value()
        preco = self.spin_preco.value()
        subtotal = quantidade * preco
        
        # Verificar estoque
        if quantidade > produto['quantidade']:
            QMessageBox.warning(self, "Estoque Insuficiente", 
                               f"Estoque disponível: {produto['quantidade']} unidades")
            return
        
        # Adicionar à lista de itens
        item = {
            'produto_id': produto['id'],
            'produto_nome': produto['nome'],
            'quantidade': quantidade,
            'preco_unitario': preco,
            'subtotal': subtotal
        }
        
        self.itens_venda.append(item)
        self.atualizar_tabela_itens()
        self.calcular_total()
        
        # Limpar seleção
        self.cb_produto.setCurrentIndex(0)
        self.spin_quantidade.setValue(1)
        self.spin_preco.setValue(0)
    
    def atualizar_tabela_itens(self):
        self.tabela_itens.setRowCount(0)
        
        for i, item in enumerate(self.itens_venda):
            self.tabela_itens.insertRow(i)
            
            # Adicionar dados
            self.tabela_itens.setItem(i, 0, QTableWidgetItem(str(item['produto_id'])))
            self.tabela_itens.setItem(i, 1, QTableWidgetItem(item['produto_nome']))
            self.tabela_itens.setItem(i, 2, QTableWidgetItem(str(item['quantidade'])))
            self.tabela_itens.setItem(i, 3, QTableWidgetItem(f"R$ {item['preco_unitario']:.2f}"))
            self.tabela_itens.setItem(i, 4, QTableWidgetItem(f"R$ {item['subtotal']:.2f}"))
            
            # Botão remover
            btn_remover = QPushButton("✕")
            btn_remover.setStyleSheet("color: red;")
            btn_remover.clicked.connect(lambda checked, row=i: self.remover_item(row))
            self.tabela_itens.setCellWidget(i, 5, btn_remover)
    
    def remover_item(self, row):
        if 0 <= row < len(self.itens_venda):
            del self.itens_venda[row]
            self.atualizar_tabela_itens()
            self.calcular_total()
    
    def calcular_total(self):
        self.total_venda = sum(item['subtotal'] for item in self.itens_venda)
        self.lbl_total.setText(f"Total: R$ {self.total_venda:.2f}")
    
    def limpar_venda(self):
        if self.itens_venda:
            confirma = QMessageBox.question(self, "Confirmar", 
                                           "Deseja realmente limpar a venda atual?",
                                           QMessageBox.Yes | QMessageBox.No)
            if confirma == QMessageBox.Yes:
                self.itens_venda = []
                self.atualizar_tabela_itens()
                self.calcular_total()
                self.cb_cliente.setCurrentIndex(0)
    
    def finalizar_venda(self):
        if not self.caixa_atual:
            QMessageBox.warning(self, "Caixa Fechado", "Abra o caixa antes de realizar vendas")
            return
        
        if not self.itens_venda:
            QMessageBox.warning(self, "Venda Vazia", "Adicione itens para finalizar a venda")
            return
        
        # Diálogo de finalização
        dialog = QDialog(self)
        dialog.setWindowTitle("Finalizar Venda")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        lbl_total = QLabel(f"R$ {self.total_venda:.2f}")
        lbl_total.setStyleSheet("font-size: 16px; font-weight: bold;")
        form_layout.addRow("Total da Venda:", lbl_total)
        
        spin_desconto = QDoubleSpinBox()
        spin_desconto.setPrefix("R$ ")
        spin_desconto.setMaximum(self.total_venda)
        spin_desconto.setDecimals(2)
        form_layout.addRow("Desconto:", spin_desconto)
        
        cb_forma_pagamento = QComboBox()
        cb_forma_pagamento.addItems(["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Boleto"])
        form_layout.addRow("Forma de Pagamento:", cb_forma_pagamento)
        
        spin_parcelas = QSpinBox()
        spin_parcelas.setMinimum(1)
        spin_parcelas.setMaximum(12)
        form_layout.addRow("Parcelas:", spin_parcelas)
        
        text_observacao = QTextEdit()
        text_observacao.setMaximumHeight(80)
        form_layout.addRow("Observação:", text_observacao)
        
        layout.addLayout(form_layout)
        
        btn_confirmar = QPushButton("Confirmar Venda")
        btn_confirmar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        layout.addWidget(btn_confirmar)
        
        # Total após desconto
        lbl_total_final = QLabel(f"Total a Pagar: R$ {self.total_venda:.2f}")
        lbl_total_final.setStyleSheet("font-size: 18px; font-weight: bold; color: #2196F3;")
        layout.addWidget(lbl_total_final)
        
        # Atualizar total ao alterar desconto
        def atualizar_total_final():
            desconto = spin_desconto.value()
            total_final = self.total_venda - desconto
            lbl_total_final.setText(f"Total a Pagar: R$ {max(0, total_final):.2f}")
        
        spin_desconto.valueChanged.connect(atualizar_total_final)
        
        # Atualizar parcelas disponíveis conforme forma de pagamento
        def atualizar_parcelas():
            forma_pgto = cb_forma_pagamento.currentText()
            if forma_pgto == "Cartão de Crédito":
                spin_parcelas.setEnabled(True)
            else:
                spin_parcelas.setValue(1)
                spin_parcelas.setEnabled(False)
        
        cb_forma_pagamento.currentIndexChanged.connect(atualizar_parcelas)
        atualizar_parcelas()
        
        # Processar venda ao confirmar
        def processar_venda():
            cliente_id = self.cb_cliente.currentData()
            desconto = spin_desconto.value()
            forma_pagamento = cb_forma_pagamento.currentText()
            parcelas = spin_parcelas.value()
            observacao = text_observacao.toPlainText()
            total_final = self.total_venda - desconto
            
            # Registrar venda
            venda_id = self.db.registrar_venda(
                cliente_id, total_final, desconto, forma_pagamento, 
                parcelas, observacao, "Concluída", "Sistema"
            )
            
            if venda_id:
                # Registrar itens da venda
                for item in self.itens_venda:
                    self.db.registrar_item_venda(
                        venda_id, item['produto_id'], item['quantidade'], 
                        item['preco_unitario'], item['subtotal']
                    )
                
                # Registrar entrada no caixa
                self.db.registrar_movimento_caixa(
                    self.caixa_atual['id'], "Entrada", f"Venda #{venda_id}", 
                    total_final, forma_pagamento, venda_id, "Venda", "Sistema"
                )
                
                # Atualizar saldo
                saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
                self.lbl_saldo.setText(f"Saldo Atual: R$ {saldo_atual:.2f}")
                
                QMessageBox.information(self, "Sucesso", "Venda finalizada com sucesso!")
                
                # Limpar venda atual
                self.itens_venda = []
                self.atualizar_tabela_itens()
                self.calcular_total()
                self.cb_cliente.setCurrentIndex(0)
                
                # Recarregar movimentos
                self.carregar_movimentos()
                
                dialog.accept()
            else:
                QMessageBox.critical(self, "Erro", "Erro ao registrar venda")
        
        btn_confirmar.clicked.connect(processar_venda)
        
        dialog.exec_()
    
    def abrir_caixa(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Abrir Caixa")
        dialog.setMinimumWidth(300)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Saldo inicial
        spin_saldo = QDoubleSpinBox()
        spin_saldo.setPrefix("R$ ")
        spin_saldo.setMaximum(999999.99)
        spin_saldo.setDecimals(2)
        form_layout.addRow("Saldo Inicial:", spin_saldo)
        
        # Observação
        text_obs = QTextEdit()
        text_obs.setMaximumHeight(80)
        form_layout.addRow("Observação:", text_obs)
        
        layout.addLayout(form_layout)
        
        btn_confirmar = QPushButton("Abrir Caixa")
        layout.addWidget(btn_confirmar)
        
        def confirmar_abertura():
            saldo_inicial = spin_saldo.value()
            observacao = text_obs.toPlainText()
            
            caixa_id = self.db.abrir_caixa(saldo_inicial, "Sistema", observacao)
            if caixa_id:
                dialog.accept()
                self.verificar_caixa_aberto()
                QMessageBox.information(self, "Sucesso", "Caixa aberto com sucesso!")
            else:
                QMessageBox.critical(self, "Erro", "Erro ao abrir o caixa")
        
        btn_confirmar.clicked.connect(confirmar_abertura)
        
        dialog.exec_()
    
    def fechar_caixa(self):
        if not self.caixa_atual:
            return
        
        saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Fechar Caixa")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        layout.addWidget(QLabel(f"Saldo do Sistema: R$ {saldo_atual:.2f}"))
        
        form_layout = QFormLayout()
        
        spin_saldo_final = QDoubleSpinBox()
        spin_saldo_final.setPrefix("R$ ")
        spin_saldo_final.setMaximum(999999.99)
        spin_saldo_final.setValue(saldo_atual)
        spin_saldo_final.setDecimals(2)
        form_layout.addRow("Saldo em Caixa:", spin_saldo_final)
        
        lbl_diferenca = QLabel("Diferença: R$ 0,00")
        form_layout.addRow("", lbl_diferenca)

        text_obs_fechamento = QTextEdit()
        text_obs_fechamento.setMaximumHeight(80)
        form_layout.addRow("Observação:", text_obs_fechamento)

        layout.addLayout(form_layout)

        btn_confirmar = QPushButton("Fechar Caixa")
        btn_confirmar.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")
        layout.addWidget(btn_confirmar)

        # Atualizar diferença ao alterar saldo final
        def atualizar_diferenca():
            saldo_informado = spin_saldo_final.value()
            diferenca = saldo_informado - saldo_atual
            lbl_diferenca.setText(f"Diferença: R$ {diferenca:.2f}")
            if diferenca < 0:
                lbl_diferenca.setStyleSheet("color: red; font-weight: bold;")
            elif diferenca > 0:
                lbl_diferenca.setStyleSheet("color: green; font-weight: bold;")
            else:
                lbl_diferenca.setStyleSheet("color: black; font-weight: bold;")

        spin_saldo_final.valueChanged.connect(atualizar_diferenca)

        def confirmar_fechamento():
            saldo_informado = spin_saldo_final.value()
            diferenca = saldo_informado - saldo_atual
            observacao = text_obs_fechamento.toPlainText()
            
            # Confirmar fechamento
            confirma = QMessageBox.question(dialog, "Confirmar Fechamento", 
                                        f"Deseja realmente fechar o caixa?\nDiferença: R$ {diferenca:.2f}",
                                        QMessageBox.Yes | QMessageBox.No)
            
            if confirma == QMessageBox.Yes:
                sucesso = self.db.fechar_caixa(
                    self.caixa_atual['id'], saldo_informado, diferenca, 
                    "Sistema", observacao
                )
                
                if sucesso:
                    dialog.accept()
                    self.verificar_caixa_aberto()
                    self.gerar_relatorio_fechamento(self.caixa_atual['id'])
                    QMessageBox.information(self, "Sucesso", "Caixa fechado com sucesso!")
                else:
                    QMessageBox.critical(self, "Erro", "Erro ao fechar o caixa")

        btn_confirmar.clicked.connect(confirmar_fechamento)
        dialog.exec_()

    def gerar_relatorio_fechamento(self, caixa_id):
        detalhes = self.db.obter_detalhes_caixa(caixa_id)
        if not detalhes:
            return
        
        # Criar diálogo com relatório
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Relatório de Fechamento - Caixa #{caixa_id}")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        text_relatorio = QTextEdit()
        text_relatorio.setReadOnly(True)
        
        # Gerar HTML do relatório
        html = f"""
        <h2>Relatório de Fechamento - Caixa #{caixa_id}</h2>
        <hr>
        <p><b>Data de Abertura:</b> {detalhes['data_abertura']}</p>
        <p><b>Data de Fechamento:</b> {detalhes['data_fechamento']}</p>
        <p><b>Operador:</b> {detalhes['operador']}</p>
        <p><b>Saldo Inicial:</b> R$ {detalhes['saldo_inicial']:.2f}</p>
        <p><b>Saldo Final (Sistema):</b> R$ {detalhes['saldo_final_sistema']:.2f}</p>
        <p><b>Saldo Final (Informado):</b> R$ {detalhes['saldo_final_informado']:.2f}</p>
        <p><b>Diferença:</b> <span style="color: {'red' if detalhes['diferenca'] < 0 else 'green'};">
            R$ {detalhes['diferenca']:.2f}
        </span></p>
        <hr>
        <h3>Resumo de Operações</h3>
        <p><b>Total de Vendas:</b> {detalhes['total_vendas']} (R$ {detalhes['valor_vendas']:.2f})</p>
        <p><b>Total de Entradas:</b> R$ {detalhes['total_entradas']:.2f}</p>
        <p><b>Total de Saídas:</b> R$ {detalhes['total_saidas']:.2f}</p>
        <hr>
        <p><b>Observação:</b> {detalhes['observacao']}</p>
        """
        
        text_relatorio.setHtml(html)
        layout.addWidget(text_relatorio)
        
        btn_imprimir = QPushButton("Imprimir")
        layout.addWidget(btn_imprimir)
        
        dialog.exec_()

    def adicionar_novo_cliente(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Adicionar Novo Cliente")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Nome
        edit_nome = QLineEdit()
        form_layout.addRow("Nome:", edit_nome)
        
        # CPF/CNPJ
        edit_cpf_cnpj = QLineEdit()
        form_layout.addRow("CPF/CNPJ:", edit_cpf_cnpj)
        
        # Telefone
        edit_telefone = QLineEdit()
        form_layout.addRow("Telefone:", edit_telefone)
        
        # Email
        edit_email = QLineEdit()
        form_layout.addRow("Email:", edit_email)
        
        layout.addLayout(form_layout)
        
        btn_salvar = QPushButton("Salvar")
        layout.addWidget(btn_salvar)
        
        def salvar_cliente():
            nome = edit_nome.text().strip()
            cpf_cnpj = edit_cpf_cnpj.text().strip()
            telefone = edit_telefone.text().strip()
            email = edit_email.text().strip()
            
            if not nome:
                QMessageBox.warning(dialog, "Campos Obrigatórios", "O campo Nome é obrigatório")
                return
            
            # Registrar cliente
            cliente_id = self.db.adicionar_cliente(nome, cpf_cnpj, telefone, email)
            
            if cliente_id:
                dialog.accept()
                self.carregar_clientes()
                # Definir cliente recém-criado como selecionado
                index = self.cb_cliente.findData(cliente_id)
                if index >= 0:
                    self.cb_cliente.setCurrentIndex(index)
            else:
                QMessageBox.critical(dialog, "Erro", "Erro ao cadastrar cliente")
        
        btn_salvar.clicked.connect(salvar_cliente)
        
        dialog.exec_()

    def carregar_movimentos(self):
        if not self.caixa_atual:
            self.tabela_movimentos.setRowCount(0)
            self.lbl_total_entradas.setText("Total Entradas: R$ 0,00")
            self.lbl_total_saidas.setText("Total Saídas: R$ 0,00")
            self.lbl_saldo_periodo.setText("Saldo do Período: R$ 0,00")
            return
        
        movimentos = self.db.listar_movimentos_caixa(self.caixa_atual['id'])
        
        self.tabela_movimentos.setRowCount(0)
        
        total_entradas = 0
        total_saidas = 0
        
        for i, movimento in enumerate(movimentos):
            self.tabela_movimentos.insertRow(i)
            
            tipo = movimento['tipo']
            valor = movimento['valor']
            
            if tipo == "Entrada":
                cor_valor = QColor(0, 128, 0)  # Verde
                total_entradas += valor
            else:
                cor_valor = QColor(255, 0, 0)  # Vermelho
                total_saidas += valor
            
            self.tabela_movimentos.setItem(i, 0, QTableWidgetItem(str(movimento['id'])))
            self.tabela_movimentos.setItem(i, 1, QTableWidgetItem(movimento['data_hora']))
            
            tipo_item = QTableWidgetItem(tipo)
            tipo_item.setForeground(cor_valor)
            self.tabela_movimentos.setItem(i, 2, tipo_item)
            
            self.tabela_movimentos.setItem(i, 3, QTableWidgetItem(movimento['descricao']))
            self.tabela_movimentos.setItem(i, 4, QTableWidgetItem(movimento['forma_pagamento']))
            
            valor_item = QTableWidgetItem(f"R$ {valor:.2f}")
            valor_item.setForeground(cor_valor)
            self.tabela_movimentos.setItem(i, 5, valor_item)
        
        # Atualizar totais
        self.lbl_total_entradas.setText(f"Total Entradas: R$ {total_entradas:.2f}")
        self.lbl_total_saidas.setText(f"Total Saídas: R$ {total_saidas:.2f}")
        
        saldo_periodo = total_entradas - total_saidas
        self.lbl_saldo_periodo.setText(f"Saldo do Período: R$ {saldo_periodo:.2f}")
        
        # Estilizar cor do saldo
        if saldo_periodo >= 0:
            self.lbl_saldo_periodo.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.lbl_saldo_periodo.setStyleSheet("font-weight: bold; color: red;")

    def filtrar_movimentos(self):
        if not self.caixa_atual:
            return
        
        data_inicio = self.dt_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.dt_fim.date().toString("yyyy-MM-dd")
        
        movimentos = self.db.listar_movimentos_por_periodo(
            self.caixa_atual['id'], data_inicio, data_fim
        )
        
        self.tabela_movimentos.setRowCount(0)
        
        total_entradas = 0
        total_saidas = 0
        
        for i, movimento in enumerate(movimentos):
            self.tabela_movimentos.insertRow(i)
            
            tipo = movimento['tipo']
            valor = movimento['valor']
            
            if tipo == "Entrada":
                cor_valor = QColor(0, 128, 0)  # Verde
                total_entradas += valor
            else:
                cor_valor = QColor(255, 0, 0)  # Vermelho
                total_saidas += valor
            
            self.tabela_movimentos.setItem(i, 0, QTableWidgetItem(str(movimento['id'])))
            self.tabela_movimentos.setItem(i, 1, QTableWidgetItem(movimento['data_hora']))
            
            tipo_item = QTableWidgetItem(tipo)
            tipo_item.setForeground(cor_valor)
            self.tabela_movimentos.setItem(i, 2, tipo_item)
            
            self.tabela_movimentos.setItem(i, 3, QTableWidgetItem(movimento['descricao']))
            self.tabela_movimentos.setItem(i, 4, QTableWidgetItem(movimento['forma_pagamento']))
            
            valor_item = QTableWidgetItem(f"R$ {valor:.2f}")
            valor_item.setForeground(cor_valor)
            self.tabela_movimentos.setItem(i, 5, valor_item)
        
        # Atualizar totais
        self.lbl_total_entradas.setText(f"Total Entradas: R$ {total_entradas:.2f}")
        self.lbl_total_saidas.setText(f"Total Saídas: R$ {total_saidas:.2f}")
        
        saldo_periodo = total_entradas - total_saidas
        self.lbl_saldo_periodo.setText(f"Saldo do Período: R$ {saldo_periodo:.2f}")
        
        # Estilizar cor do saldo
        if saldo_periodo >= 0:
            self.lbl_saldo_periodo.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.lbl_saldo_periodo.setStyleSheet("font-weight: bold; color: red;")

    def novo_movimento(self, tipo):
        if not self.caixa_atual:
            QMessageBox.warning(self, "Caixa Fechado", "Abra o caixa antes de realizar movimentações")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Nova {tipo}")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        form_layout = QFormLayout()
        
        # Descrição
        edit_descricao = QLineEdit()
        form_layout.addRow("Descrição:", edit_descricao)
        
        # Valor
        spin_valor = QDoubleSpinBox()
        spin_valor.setPrefix("R$ ")
        spin_valor.setMaximum(999999.99)
        spin_valor.setDecimals(2)
        form_layout.addRow("Valor:", spin_valor)
        
        # Forma de pagamento
        cb_forma_pagamento = QComboBox()
        cb_forma_pagamento.addItems(["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Outro"])
        form_layout.addRow("Forma de Pagamento:", cb_forma_pagamento)
        
        # Observação
        text_obs = QTextEdit()
        text_obs.setMaximumHeight(80)
        form_layout.addRow("Observação:", text_obs)
        
        layout.addLayout(form_layout)
        
        btn_confirmar = QPushButton(f"Confirmar {tipo}")
        if tipo == "Entrada":
            btn_confirmar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        else:
            btn_confirmar.setStyleSheet("background-color: #F44336; color: white; font-weight: bold;")
        layout.addWidget(btn_confirmar)
        
        def confirmar_movimento():
            descricao = edit_descricao.text().strip()
            valor = spin_valor.value()
            forma_pagamento = cb_forma_pagamento.currentText()
            observacao = text_obs.toPlainText()
            
            if not descricao:
                QMessageBox.warning(dialog, "Campos Obrigatórios", "O campo Descrição é obrigatório")
                return
            
            if valor <= 0:
                QMessageBox.warning(dialog, "Valor Inválido", "O valor deve ser maior que zero")
                return
            
            # Registrar movimento
            sucesso = self.db.registrar_movimento_caixa(
                self.caixa_atual['id'], tipo, descricao, valor, 
                forma_pagamento, None, "Manual", "Sistema", observacao
            )
            
            if sucesso:
                dialog.accept()
                
                # Atualizar saldo
                saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
                self.lbl_saldo.setText(f"Saldo Atual: R$ {saldo_atual:.2f}")
                
                # Recarregar movimentos
                self.carregar_movimentos()
                
                QMessageBox.information(self, "Sucesso", f"{tipo} registrada com sucesso!")
            else:
                QMessageBox.critical(dialog, "Erro", f"Erro ao registrar {tipo.lower()}")
        
        btn_confirmar.clicked.connect(confirmar_movimento)
        
        dialog.exec_()

    def periodo_alterado(self, index):
        periodo = self.cb_periodo.currentText()
        hoje = QDate.currentDate()
        
        if periodo == "Hoje":
            self.dt_rel_inicio.setDate(hoje)
            self.dt_rel_fim.setDate(hoje)
        elif periodo == "Última Semana":
            self.dt_rel_inicio.setDate(hoje.addDays(-7))
            self.dt_rel_fim.setDate(hoje)
        elif periodo == "Último Mês":
            self.dt_rel_inicio.setDate(hoje.addMonths(-1))
            self.dt_rel_fim.setDate(hoje)
        
        # Ativar/desativar campos de data
        personalizado = periodo == "Personalizado"
        self.dt_rel_inicio.setEnabled(personalizado)
        self.dt_rel_fim.setEnabled(personalizado)

    def gerar_relatorio(self):
        data_inicio = self.dt_rel_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.dt_rel_fim.date().toString("yyyy-MM-dd")
        
        # Buscar dados
        dados = self.db.gerar_relatorio_periodo(data_inicio, data_fim)
        
        if not dados:
            QMessageBox.information(self, "Sem Dados", "Não foram encontrados dados para o período selecionado")
            return
        
        # Preencher resumo
        resumo = f"""
        <h2>Resumo Financeiro - {data_inicio} a {data_fim}</h2>
        <hr>
        <h3>Movimentação de Caixa</h3>
        <ul>
            <li><b>Total de Entradas:</b> R$ {dados['total_entradas']:.2f}</li>
            <li><b>Total de Saídas:</b> R$ {dados['total_saidas']:.2f}</li>
            <li><b>Saldo do Período:</b> R$ {dados['saldo_periodo']:.2f}</li>
        </ul>
        
        <h3>Vendas</h3>
        <ul>
            <li><b>Quantidade de Vendas:</b> {dados['qtd_vendas']}</li>
            <li><b>Valor Total de Vendas:</b> R$ {dados['valor_vendas']:.2f}</li>
            <li><b>Valor Médio por Venda:</b> R$ {dados['valor_medio_venda']:.2f}</li>
            <li><b>Total de Descontos:</b> R$ {dados['total_descontos']:.2f}</li>
        </ul>
        
        <h3>Formas de Pagamento</h3>
        <ul>
        """
        
        for forma, valor in dados['pagamentos'].items():
            resumo += f"<li><b>{forma}:</b> R$ {valor:.2f}</li>"
        
        resumo += f"""
        </ul>
        
        <h3>Produtos Mais Vendidos</h3>
        <ol>
        """
        
        for produto in dados['produtos_mais_vendidos'][:5]:
            resumo += f"<li><b>{produto['nome']}:</b> {produto['quantidade']} unidades (R$ {produto['valor_total']:.2f})</li>"
        
        resumo += """
        </ol>
        """
        
        self.text_resumo.setHtml(resumo)
        
        # Preencher tabela de movimentos
        self.tabela_rel_movimentos.setRowCount(0)
        
        for i, movimento in enumerate(dados['movimentos']):
            self.tabela_rel_movimentos.insertRow(i)
            
            tipo = movimento['tipo']
            valor = movimento['valor']
            
            if tipo == "Entrada":
                cor_valor = QColor(0, 128, 0)  # Verde
            else:
                cor_valor = QColor(255, 0, 0)  # Vermelho
            
            self.tabela_rel_movimentos.setItem(i, 0, QTableWidgetItem(str(movimento['id'])))
            self.tabela_rel_movimentos.setItem(i, 1, QTableWidgetItem(movimento['data_hora']))
            
            tipo_item = QTableWidgetItem(tipo)
            tipo_item.setForeground(cor_valor)
            self.tabela_rel_movimentos.setItem(i, 2, tipo_item)
            
            self.tabela_rel_movimentos.setItem(i, 3, QTableWidgetItem(movimento['descricao']))
            self.tabela_rel_movimentos.setItem(i, 4, QTableWidgetItem(movimento['forma_pagamento']))
            
            valor_item = QTableWidgetItem(f"R$ {valor:.2f}")
            valor_item.setForeground(cor_valor)
            self.tabela_rel_movimentos.setItem(i, 5, valor_item)
        
        # Preencher tabela de vendas
        self.tabela_rel_vendas.setRowCount(0)
        
        for i, venda in enumerate(dados['vendas']):
            self.tabela_rel_vendas.insertRow(i)
            
            self.tabela_rel_vendas.setItem(i, 0, QTableWidgetItem(str(venda['id'])))
            self.tabela_rel_vendas.setItem(i, 1, QTableWidgetItem(venda['data_hora']))
            self.tabela_rel_vendas.setItem(i, 2, QTableWidgetItem(venda['cliente']))
            self.tabela_rel_vendas.setItem(i, 3, QTableWidgetItem(f"R$ {venda['valor_total']:.2f}"))
            self.tabela_rel_vendas.setItem(i, 4, QTableWidgetItem(f"R$ {venda['desconto']:.2f}"))
            self.tabela_rel_vendas.setItem(i, 5, QTableWidgetItem(venda['forma_pagamento']))