from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
                            QMessageBox, QDialog, QFormLayout, QTextEdit, QDoubleSpinBox,
                            QSpinBox, QHeaderView, QCheckBox, QGroupBox, QGridLayout, QFrame,
                            QSplitter, QApplication)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon, QColor, QFont
import datetime

class DashboardWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.periodo_alterado(0)  # Inicializa com o período padrão (Hoje)
        self.carregar_dados()
    
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Frame superior com filtros
        frame_filtros = QFrame()
        frame_filtros.setFrameShape(QFrame.StyledPanel)
        frame_filtros_layout = QHBoxLayout(frame_filtros)
        
        frame_filtros_layout.addWidget(QLabel("Período:"))
        self.cb_periodo = QComboBox()
        self.cb_periodo.addItems(["Hoje", "Última Semana", "Último Mês", "Último Ano", "Personalizado"])
        self.cb_periodo.currentIndexChanged.connect(self.periodo_alterado)
        frame_filtros_layout.addWidget(self.cb_periodo)
        
        frame_filtros_layout.addWidget(QLabel("De:"))
        self.dt_inicio = QDateEdit(QDate.currentDate())
        self.dt_inicio.setCalendarPopup(True)
        self.dt_inicio.dateChanged.connect(self.data_alterada)
        frame_filtros_layout.addWidget(self.dt_inicio)
        
        frame_filtros_layout.addWidget(QLabel("Até:"))
        self.dt_fim = QDateEdit(QDate.currentDate())
        self.dt_fim.setCalendarPopup(True)
        self.dt_fim.dateChanged.connect(self.data_alterada)
        frame_filtros_layout.addWidget(self.dt_fim)
        
        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self.carregar_dados)
        frame_filtros_layout.addWidget(self.btn_atualizar)
        
        layout.addWidget(frame_filtros)
        
        # Split principal em duas colunas
        splitter = QSplitter(Qt.Horizontal)
        
        # Coluna esquerda (indicadores principais)
        frame_indicadores = QFrame()
        frame_indicadores.setFrameShape(QFrame.StyledPanel)
        indicadores_layout = QVBoxLayout(frame_indicadores)
        
        # Cards de indicadores
        grid_cards = QGridLayout()
        
        # Faturamento
        card_faturamento = self.criar_card("Faturamento", "R$ 0,00", "green")
        grid_cards.addWidget(card_faturamento, 0, 0)
        
        # Lucro
        card_lucro = self.criar_card("Lucro", "R$ 0,00", "blue")
        grid_cards.addWidget(card_lucro, 0, 1)
        
        # Nº de Vendas
        card_vendas = self.criar_card("Nº de Vendas", "0", "purple")
        grid_cards.addWidget(card_vendas, 1, 0)
        
        # Ticket Médio
        card_ticket = self.criar_card("Ticket Médio", "R$ 0,00", "orange")
        grid_cards.addWidget(card_ticket, 1, 1)
        
        indicadores_layout.addLayout(grid_cards)
        
        # Salvar referências aos labels de valores
        self.lbl_faturamento = card_faturamento.findChild(QLabel, "valor")
        self.lbl_lucro = card_lucro.findChild(QLabel, "valor")
        self.lbl_num_vendas = card_vendas.findChild(QLabel, "valor")
        self.lbl_ticket_medio = card_ticket.findChild(QLabel, "valor")
        
        # Gráfico de vendas por dia
        frame_grafico = QFrame()
        frame_grafico.setFrameShape(QFrame.StyledPanel)
        frame_grafico.setStyleSheet("background-color: white;")
        frame_grafico.setMinimumHeight(200)
        
        grafico_layout = QVBoxLayout(frame_grafico)
        grafico_layout.addWidget(QLabel("Gráfico de Vendas por Dia"))
        
        indicadores_layout.addWidget(frame_grafico)
        
        splitter.addWidget(frame_indicadores)
        
        # Coluna direita (detalhes)
        frame_detalhes = QFrame()
        frame_detalhes.setFrameShape(QFrame.StyledPanel)
        detalhes_layout = QVBoxLayout(frame_detalhes)
        
        # Tabs para diferentes visões
        tabs = QTabWidget()
        
        # Tab de Produtos mais vendidos
        tab_produtos = QWidget()
        tab_produtos_layout = QVBoxLayout(tab_produtos)
        
        self.tabela_produtos = QTableWidget()
        self.tabela_produtos.setColumnCount(4)
        self.tabela_produtos.setHorizontalHeaderLabels(['Produto', 'Qtde Vendida', 'Valor Total', '% Participação'])
        self.tabela_produtos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tab_produtos_layout.addWidget(self.tabela_produtos)
        
        tabs.addTab(tab_produtos, "Produtos Mais Vendidos")
        
        # Tab de Formas de Pagamento
        tab_pagamentos = QWidget()
        tab_pagamentos_layout = QVBoxLayout(tab_pagamentos)
        
        self.tabela_pagamentos = QTableWidget()
        self.tabela_pagamentos.setColumnCount(3)
        self.tabela_pagamentos.setHorizontalHeaderLabels(['Forma de Pagamento', 'Valor Total', '% Participação'])
        self.tabela_pagamentos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tab_pagamentos_layout.addWidget(self.tabela_pagamentos)
        
        tabs.addTab(tab_pagamentos, "Formas de Pagamento")
        
        # Tab de Clientes
        tab_clientes = QWidget()
        tab_clientes_layout = QVBoxLayout(tab_clientes)
        
        self.tabela_clientes = QTableWidget()
        self.tabela_clientes.setColumnCount(4)
        self.tabela_clientes.setHorizontalHeaderLabels(['Cliente', 'Qtde Compras', 'Valor Total', 'Ticket Médio'])
        self.tabela_clientes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        tab_clientes_layout.addWidget(self.tabela_clientes)
        
        tabs.addTab(tab_clientes, "Melhores Clientes")
        
        detalhes_layout.addWidget(tabs)
        
        splitter.addWidget(frame_detalhes)
        
        # Ajustar proporção inicial do splitter
        splitter.setSizes([int(self.width() * 0.4), int(self.width() * 0.6)])
        
        layout.addWidget(splitter)
    
    def criar_card(self, titulo, valor, cor):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setMinimumHeight(100)
        card.setStyleSheet(f"background-color: {cor}; color: white; border-radius: 5px;")
        
        layout_card = QVBoxLayout(card)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout_card.addWidget(lbl_titulo)
        
        lbl_valor = QLabel(valor)
        lbl_valor.setObjectName("valor")  # Para acessar facilmente depois
        lbl_valor.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout_card.addWidget(lbl_valor)
        
        return card
    
    def data_alterada(self):
        # Quando o usuário altera manualmente uma data, muda para o modo personalizado
        if self.dt_inicio.isEnabled() and self.dt_fim.isEnabled():
            # Verificar se data início é maior que data fim
            if self.dt_inicio.date() > self.dt_fim.date():
                # Ajustar data fim para ser igual data início
                self.dt_fim.setDate(self.dt_inicio.date())
        
        # Se estivermos em modo não personalizado, mudar para personalizado
        if self.cb_periodo.currentText() != "Personalizado":
            self.cb_periodo.blockSignals(True)
            self.cb_periodo.setCurrentText("Personalizado")
            self.cb_periodo.blockSignals(False)
    
    def periodo_alterado(self, index):
        periodo = self.cb_periodo.currentText()
        hoje = QDate.currentDate()
        
        # Bloquear sinais para evitar recursão
        self.dt_inicio.blockSignals(True)
        self.dt_fim.blockSignals(True)
        
        if periodo == "Hoje":
            self.dt_inicio.setDate(hoje)
            self.dt_fim.setDate(hoje)
        elif periodo == "Última Semana":
            self.dt_inicio.setDate(hoje.addDays(-7))
            self.dt_fim.setDate(hoje)
        elif periodo == "Último Mês":
            self.dt_inicio.setDate(hoje.addMonths(-1))
            self.dt_fim.setDate(hoje)
        elif periodo == "Último Ano":
            self.dt_inicio.setDate(hoje.addYears(-1))
            self.dt_fim.setDate(hoje)
        
        # Ativar/desativar campos de data
        personalizado = periodo == "Personalizado"
        self.dt_inicio.setEnabled(personalizado)
        self.dt_fim.setEnabled(personalizado)
        
        # Desbloquear sinais
        self.dt_inicio.blockSignals(False)
        self.dt_fim.blockSignals(False)
        
        # Carregar dados com o novo período, exceto quando for personalizado
        # porque aí o usuário precisa selecionar as datas primeiro
        if not personalizado:
            self.carregar_dados()
    
    def carregar_dados(self):
        data_inicio = self.dt_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.dt_fim.date().toString("yyyy-MM-dd")
        
        try:
            # Buscar dados no banco
            dados = self.db.obter_dados_dashboard(data_inicio, data_fim)
            
            if not dados:
                self.mostrar_sem_dados()
                return
            
            # Atualizar indicadores principais
            self.lbl_faturamento.setText(f"R$ {dados['faturamento']:.2f}")
            self.lbl_lucro.setText(f"R$ {dados['lucro']:.2f}")
            self.lbl_num_vendas.setText(str(dados['num_vendas']))
            
            ticket_medio = dados['faturamento'] / dados['num_vendas'] if dados['num_vendas'] > 0 else 0
            self.lbl_ticket_medio.setText(f"R$ {ticket_medio:.2f}")
            
            # Atualizar tabela de produtos
            self.tabela_produtos.setRowCount(0)
            
            for i, produto in enumerate(dados['produtos']):
                self.tabela_produtos.insertRow(i)
                
                self.tabela_produtos.setItem(i, 0, QTableWidgetItem(produto['nome']))
                self.tabela_produtos.setItem(i, 1, QTableWidgetItem(str(produto['quantidade'])))
                self.tabela_produtos.setItem(i, 2, QTableWidgetItem(f"R$ {produto['valor_total']:.2f}"))
                
                participacao = (produto['valor_total'] / dados['faturamento'] * 100) if dados['faturamento'] > 0 else 0
                self.tabela_produtos.setItem(i, 3, QTableWidgetItem(f"{participacao:.2f}%"))
            
            # Atualizar tabela de formas de pagamento
            self.tabela_pagamentos.setRowCount(0)
            
            for i, pagamento in enumerate(dados['pagamentos']):
                self.tabela_pagamentos.insertRow(i)
                
                self.tabela_pagamentos.setItem(i, 0, QTableWidgetItem(pagamento['forma']))
                self.tabela_pagamentos.setItem(i, 1, QTableWidgetItem(f"R$ {pagamento['valor_total']:.2f}"))
                
                participacao = (pagamento['valor_total'] / dados['faturamento'] * 100) if dados['faturamento'] > 0 else 0
                self.tabela_pagamentos.setItem(i, 2, QTableWidgetItem(f"{participacao:.2f}%"))
            
            # Atualizar tabela de clientes
            self.tabela_clientes.setRowCount(0)
            
            for i, cliente in enumerate(dados['clientes']):
                self.tabela_clientes.insertRow(i)
                
                self.tabela_clientes.setItem(i, 0, QTableWidgetItem(cliente['nome']))
                self.tabela_clientes.setItem(i, 1, QTableWidgetItem(str(cliente['compras'])))
                self.tabela_clientes.setItem(i, 2, QTableWidgetItem(f"R$ {cliente['valor_total']:.2f}"))
                
                ticket = cliente['valor_total'] / cliente['compras'] if cliente['compras'] > 0 else 0
                self.tabela_clientes.setItem(i, 3, QTableWidgetItem(f"R$ {ticket:.2f}"))
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {str(e)}")
    
    def mostrar_sem_dados(self):
        # Limpar indicadores
        self.lbl_faturamento.setText("R$ 0,00")
        self.lbl_lucro.setText("R$ 0,00")
        self.lbl_num_vendas.setText("0")
        self.lbl_ticket_medio.setText("R$ 0,00")
        
        # Limpar tabelas
        self.tabela_produtos.setRowCount(0)
        self.tabela_pagamentos.setRowCount(0)
        self.tabela_clientes.setRowCount(0)
        
        # Mostrar mensagem para o usuário
        QMessageBox.information(self, "Informação", "Não foram encontrados dados para o período selecionado.")