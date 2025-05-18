from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
                            QMessageBox, QDialog, QFormLayout, QTextEdit, QDoubleSpinBox,
                            QSpinBox, QHeaderView, QCheckBox, QGroupBox, QGridLayout, QFrame,
                            QSplitter, QApplication)
from PyQt5.QtCore import Qt, QDate, QDateTime
from PyQt5.QtGui import QIcon, QColor, QFont
import datetime
import sys
import random  # Para dados de exemplo

# Importações para os gráficos
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

# Configurações globais para todos os gráficos
def set_modern_style():
    plt.style.use('seaborn-v0_8-whitegrid')
    
    # Cores modernas
    colors = {
        'primary': '#3498db',        # Azul
        'success': '#2ecc71',        # Verde
        'warning': '#f39c12',        # Laranja
        'danger': '#e74c3c',         # Vermelho
        'info': '#9b59b6',           # Roxo
        'secondary': '#1abc9c',      # Turquesa
        'light': '#ecf0f1',          # Cinza claro
        'dark': '#34495e'            # Cinza escuro
    }
    
    # Definir estilo de texto
    font = {'family': 'sans-serif', 
            'weight': 'normal',
            'size': 10}
    matplotlib.rc('font', **font)
    
    # Estilo de grade mais suave
    matplotlib.rc('grid', linestyle='--', alpha=0.3)
    
    return colors

# Classe MplCanvas modificada para melhor qualidade visual
class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=120):  # Aumentado o DPI para melhor resolução
        self.fig = Figure(figsize=(width, height), dpi=dpi, facecolor='white')
        self.axes = self.fig.add_subplot(111)
        
        # Definir estilo
        set_modern_style()
        
        # Inicializar o canvas
        super(MplCanvas, self).__init__(self.fig)
        
        # Configurações para melhor estética
        self.fig.tight_layout(pad=2.5)  # Maior padding para evitar cortes
        self.setStyleSheet("background-color:transparent;")  # Fundo transparente


class DashboardWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.chartCanvases = {}  # Dicionário para guardar referências aos gráficos
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
        card_faturamento = self.criar_card("Faturamento", "R$ 0,00", "#28a745")  # verde
        grid_cards.addWidget(card_faturamento, 0, 0)
        
        # Lucro
        card_lucro = self.criar_card("Lucro", "R$ 0,00", "#007bff")  # azul
        grid_cards.addWidget(card_lucro, 0, 1)
        
        # Nº de Vendas
        card_vendas = self.criar_card("Nº de Vendas", "0", "#6f42c1")  # roxo
        grid_cards.addWidget(card_vendas, 1, 0)
        
        # Ticket Médio
        card_ticket = self.criar_card("Ticket Médio", "R$ 0,00", "#fd7e14")  # laranja
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
        frame_grafico.setMinimumHeight(250)
        
        grafico_layout = QVBoxLayout(frame_grafico)
        titulo_grafico = QLabel("Vendas por Dia")
        titulo_grafico.setStyleSheet("font-weight: bold; font-size: 14px;")
        grafico_layout.addWidget(titulo_grafico)
        
        # Adicionar o canvas do matplotlib para o gráfico de vendas
        self.chart_vendas = MplCanvas(width=5, height=2.5, dpi=100)
        grafico_layout.addWidget(self.chart_vendas)
        self.chartCanvases['vendas_diarias'] = self.chart_vendas
        
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
        
        # Layout dividido para tabela e gráfico
        produtos_splitter = QSplitter(Qt.Vertical)
        
        # Frame para a tabela
        frame_tabela_produtos = QFrame()
        layout_tabela_produtos = QVBoxLayout(frame_tabela_produtos)
        
        self.tabela_produtos = QTableWidget()
        self.tabela_produtos.setColumnCount(4)
        self.tabela_produtos.setHorizontalHeaderLabels(['Produto', 'Qtde Vendida', 'Valor Total', '% Participação'])
        self.tabela_produtos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout_tabela_produtos.addWidget(self.tabela_produtos)
        
        produtos_splitter.addWidget(frame_tabela_produtos)
        
        # Frame para o gráfico de produtos
        frame_grafico_produtos = QFrame()
        frame_grafico_produtos.setMinimumHeight(250)
        frame_grafico_produtos.setFrameShape(QFrame.StyledPanel)
        frame_grafico_produtos.setStyleSheet("background-color: white;")
        
        layout_grafico_produtos = QVBoxLayout(frame_grafico_produtos)
        titulo_produtos = QLabel("Top 5 Produtos por Valor")
        titulo_produtos.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout_grafico_produtos.addWidget(titulo_produtos)
        
        self.chart_produtos = MplCanvas(width=5, height=2.5, dpi=100)
        layout_grafico_produtos.addWidget(self.chart_produtos)
        self.chartCanvases['produtos'] = self.chart_produtos
        
        produtos_splitter.addWidget(frame_grafico_produtos)
        
        tab_produtos_layout.addWidget(produtos_splitter)
        tabs.addTab(tab_produtos, "Produtos Mais Vendidos")
        
        # Tab de Formas de Pagamento
        tab_pagamentos = QWidget()
        tab_pagamentos_layout = QVBoxLayout(tab_pagamentos)
        
        # Layout dividido para tabela e gráfico
        pagamentos_splitter = QSplitter(Qt.Vertical)
        
        # Frame para a tabela
        frame_tabela_pagamentos = QFrame()
        layout_tabela_pagamentos = QVBoxLayout(frame_tabela_pagamentos)
        
        self.tabela_pagamentos = QTableWidget()
        self.tabela_pagamentos.setColumnCount(3)
        self.tabela_pagamentos.setHorizontalHeaderLabels(['Forma de Pagamento', 'Valor Total', '% Participação'])
        self.tabela_pagamentos.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout_tabela_pagamentos.addWidget(self.tabela_pagamentos)
        
        pagamentos_splitter.addWidget(frame_tabela_pagamentos)
        
        # Frame para o gráfico de pagamentos
        frame_grafico_pagamentos = QFrame()
        frame_grafico_pagamentos.setMinimumHeight(250)
        frame_grafico_pagamentos.setFrameShape(QFrame.StyledPanel)
        frame_grafico_pagamentos.setStyleSheet("background-color: white;")
        
        layout_grafico_pagamentos = QVBoxLayout(frame_grafico_pagamentos)
        titulo_pagamentos = QLabel("Distribuição por Forma de Pagamento")
        titulo_pagamentos.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout_grafico_pagamentos.addWidget(titulo_pagamentos)
        
        self.chart_pagamentos = MplCanvas(width=5, height=2.5, dpi=100)
        layout_grafico_pagamentos.addWidget(self.chart_pagamentos)
        self.chartCanvases['pagamentos'] = self.chart_pagamentos
        
        pagamentos_splitter.addWidget(frame_grafico_pagamentos)
        
        tab_pagamentos_layout.addWidget(pagamentos_splitter)
        tabs.addTab(tab_pagamentos, "Formas de Pagamento")
        
        # Tab de Clientes
        tab_clientes = QWidget()
        tab_clientes_layout = QVBoxLayout(tab_clientes)
        
        # Layout dividido para tabela e gráfico
        clientes_splitter = QSplitter(Qt.Vertical)
        
        # Frame para a tabela
        frame_tabela_clientes = QFrame()
        layout_tabela_clientes = QVBoxLayout(frame_tabela_clientes)
        
        self.tabela_clientes = QTableWidget()
        self.tabela_clientes.setColumnCount(4)
        self.tabela_clientes.setHorizontalHeaderLabels(['Cliente', 'Qtde Compras', 'Valor Total', 'Ticket Médio'])
        self.tabela_clientes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout_tabela_clientes.addWidget(self.tabela_clientes)
        
        clientes_splitter.addWidget(frame_tabela_clientes)
        
        # Frame para o gráfico de clientes
        frame_grafico_clientes = QFrame()
        frame_grafico_clientes.setMinimumHeight(250)
        frame_grafico_clientes.setFrameShape(QFrame.StyledPanel)
        frame_grafico_clientes.setStyleSheet("background-color: white;")
        
        layout_grafico_clientes = QVBoxLayout(frame_grafico_clientes)
        titulo_clientes = QLabel("Top 5 Clientes por Valor")
        titulo_clientes.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout_grafico_clientes.addWidget(titulo_clientes)
        
        self.chart_clientes = MplCanvas(width=5, height=2.5, dpi=100)
        layout_grafico_clientes.addWidget(self.chart_clientes)
        self.chartCanvases['clientes'] = self.chart_clientes
        
        clientes_splitter.addWidget(frame_grafico_clientes)
        
        tab_clientes_layout.addWidget(clientes_splitter)
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
        card.setStyleSheet(f"background-color: {cor}; color: white; border-radius: 8px;")
        
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
            
            # Atualizar gráfico de produtos (top 5)
            self.atualizar_grafico_produtos(dados['produtos'][:5] if len(dados['produtos']) > 5 else dados['produtos'])
            
            # Atualizar tabela de formas de pagamento
            self.tabela_pagamentos.setRowCount(0)
            
            for i, pagamento in enumerate(dados['pagamentos']):
                self.tabela_pagamentos.insertRow(i)
                
                self.tabela_pagamentos.setItem(i, 0, QTableWidgetItem(pagamento['forma']))
                self.tabela_pagamentos.setItem(i, 1, QTableWidgetItem(f"R$ {pagamento['valor_total']:.2f}"))
                
                participacao = (pagamento['valor_total'] / dados['faturamento'] * 100) if dados['faturamento'] > 0 else 0
                self.tabela_pagamentos.setItem(i, 2, QTableWidgetItem(f"{participacao:.2f}%"))
            
            # Atualizar gráfico de formas de pagamento
            self.atualizar_grafico_pagamentos(dados['pagamentos'])
            
            # Atualizar tabela de clientes
            self.tabela_clientes.setRowCount(0)
            
            for i, cliente in enumerate(dados['clientes']):
                self.tabela_clientes.insertRow(i)
                
                self.tabela_clientes.setItem(i, 0, QTableWidgetItem(cliente['nome']))
                self.tabela_clientes.setItem(i, 1, QTableWidgetItem(str(cliente['compras'])))
                self.tabela_clientes.setItem(i, 2, QTableWidgetItem(f"R$ {cliente['valor_total']:.2f}"))
                
                ticket = cliente['valor_total'] / cliente['compras'] if cliente['compras'] > 0 else 0
                self.tabela_clientes.setItem(i, 3, QTableWidgetItem(f"R$ {ticket:.2f}"))
            
            # Atualizar gráfico de clientes (top 5)
            self.atualizar_grafico_clientes(dados['clientes'][:5] if len(dados['clientes']) > 5 else dados['clientes'])
            
            # Atualizar gráfico de vendas por dia
            self.atualizar_grafico_vendas_diarias(dados['vendas_diarias'] if 'vendas_diarias' in dados else [])
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar dados: {str(e)}")
    
    # Modificações nos métodos de atualização de gráficos
    def atualizar_grafico_vendas_diarias(self, vendas_diarias):
        """Atualiza o gráfico de linha de vendas diárias com estilo moderno"""
        # Configurar estilo
        colors = set_modern_style()
        
        # Se não temos dados de vendas diárias, criar alguns de exemplo
        if not vendas_diarias:
            data_inicio = self.dt_inicio.date()
            data_fim = self.dt_fim.date()
            
            # Cria datas entre início e fim
            datas = []
            data_atual = data_inicio
            while data_atual <= data_fim:
                datas.append(data_atual.toString("dd/MM"))  # Formato mais curto para as datas
                data_atual = data_atual.addDays(1)
            
            # Gera valores aleatórios para exemplo
            valores = [random.uniform(100, 5000) for _ in range(len(datas))]
            
            vendas_diarias = [{'data': data, 'valor': valor} for data, valor in zip(datas, valores)]
        else:
            # Formatando datas para exibição mais limpa
            for item in vendas_diarias:
                if 'data' in item and len(item['data']) == 10:  # Formato yyyy-MM-dd
                    try:
                        year, month, day = item['data'].split('-')
                        item['data_display'] = f"{day}/{month}"
                    except:
                        item['data_display'] = item['data']
                else:
                    item['data_display'] = item['data']
        
        # Limpa o gráfico
        self.chart_vendas.axes.clear()
        
        # Extrai datas e valores
        datas = [item.get('data_display', item['data']) for item in vendas_diarias]
        valores = [item['valor'] for item in vendas_diarias]
        
        # Cria o gráfico de linha com estilo mais moderno
        self.chart_vendas.axes.plot(
            datas, 
            valores, 
            marker='o',
            markersize=6, 
            markerfacecolor='white',
            markeredgecolor=colors['primary'],
            markeredgewidth=1.5,
            linestyle='-', 
            linewidth=2.5,
            color=colors['primary'],
            alpha=0.8
        )
        
        # Preencher área sob a linha
        self.chart_vendas.axes.fill_between(
            datas, 
            valores, 
            color=colors['primary'], 
            alpha=0.1
        )
        
        # Configurações visuais
        self.chart_vendas.axes.set_ylabel('Valor (R$)', fontsize=11, fontweight='bold')
        self.chart_vendas.axes.spines['top'].set_visible(False)
        self.chart_vendas.axes.spines['right'].set_visible(False)
        self.chart_vendas.axes.spines['left'].set_color('#cccccc')
        self.chart_vendas.axes.spines['bottom'].set_color('#cccccc')
        
        # Rotaciona as datas para melhor visualização
        if len(datas) > 3:
            self.chart_vendas.axes.tick_params(axis='x', rotation=30)
        
        # Definir limites do eixo Y começando de zero
        self.chart_vendas.axes.set_ylim(bottom=0)
        
        # Formatando valores do eixo Y
        self.chart_vendas.axes.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}')
        )
        
        # Ajusta o layout
        self.chart_vendas.fig.tight_layout()
        
        # Redesenha o canvas
        self.chart_vendas.draw()


    def atualizar_grafico_produtos(self, produtos):
        """Atualiza o gráfico de barras dos produtos mais vendidos com estilo moderno"""
        # Configurar estilo
        colors = set_modern_style()
        
        # Limpa o gráfico
        self.chart_produtos.axes.clear()
        
        if not produtos:
            self.chart_produtos.draw()
            return
        
        # Extrai nomes e valores
        nomes = [item['nome'] for item in produtos]
        valores = [item['valor_total'] for item in produtos]
        
        # Encurtar nomes muito longos
        nomes_display = []
        for nome in nomes:
            if len(nome) > 15:
                nomes_display.append(nome[:12] + '...')
            else:
                nomes_display.append(nome)
        
        # Cria o gráfico de barras horizontais com gradiente de cores
        color_map = matplotlib.cm.get_cmap('Blues')
        num_bars = len(nomes)
        bar_colors = [color_map(0.3 + 0.7 * i / num_bars) for i in range(num_bars)]
        
        bars = self.chart_produtos.axes.barh(
            nomes_display, 
            valores, 
            color=bar_colors,
            height=0.65,  # Barras um pouco mais finas
            edgecolor='white',
            linewidth=0.5
        )
        
        # Adiciona os valores no final das barras
        for bar in bars:
            width = bar.get_width()
            self.chart_produtos.axes.text(
                width * 1.01, 
                bar.get_y() + bar.get_height()/2, 
                f'R$ {width:,.2f}',
                ha='left', 
                va='center',
                fontsize=9,
                alpha=0.8
            )
        
        # Formata o gráfico
        self.chart_produtos.axes.set_xlabel('Valor Total (R$)', fontsize=11, fontweight='bold')
        
        # Remover bordas desnecessárias
        self.chart_produtos.axes.spines['top'].set_visible(False)
        self.chart_produtos.axes.spines['right'].set_visible(False)
        self.chart_produtos.axes.spines['left'].set_color('#cccccc')
        self.chart_produtos.axes.spines['bottom'].set_color('#cccccc')
        
        # Definir limites do eixo X começando de zero
        self.chart_produtos.axes.set_xlim(left=0)
        
        # Formatando valores do eixo X
        self.chart_produtos.axes.xaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}')
        )
        
        # Ajusta o layout
        self.chart_produtos.fig.tight_layout()
        
        # Redesenha o canvas
        self.chart_produtos.draw()


    def atualizar_grafico_pagamentos(self, pagamentos):
        """Atualiza o gráfico de pizza das formas de pagamento com estilo moderno"""
        # Configurar estilo
        colors = set_modern_style()
        
        # Limpa o gráfico
        self.chart_pagamentos.axes.clear()
        
        if not pagamentos:
            self.chart_pagamentos.draw()
            return
        
        # Extrai labels e valores
        labels = [item['forma'] for item in pagamentos]
        valores = [item['valor_total'] for item in pagamentos]
        
        # Cores modernas para o gráfico de pizza
        pie_colors = [
            '#3498db', '#2ecc71', '#f39c12', '#e74c3c', 
            '#9b59b6', '#1abc9c', '#34495e', '#7f8c8d'
        ]
        
        # Total para calcular percentuais
        total = sum(valores)
        
        # Cria o gráfico de pizza
        wedges, texts, autotexts = self.chart_pagamentos.axes.pie(
            valores, 
            labels=None,
            autopct=lambda pct: f"{pct:.1f}%" if pct > 3 else "",
            startangle=90,
            colors=pie_colors[:len(pagamentos)],
            wedgeprops={'edgecolor': 'white', 'linewidth': 1.5, 'antialiased': True},
            textprops={'fontsize': 9, 'color': 'white'}
        )
        
        # Configurar textos de porcentagens
        for autotext in autotexts:
            autotext.set_fontsize(9)
            autotext.set_fontweight('bold')
        
        # Adiciona um círculo branco no meio (estilo donut)
        centre_circle = plt.Circle((0, 0), 0.5, fc='white', edgecolor='none')
        self.chart_pagamentos.axes.add_patch(centre_circle)
        
        # Adiciona a legenda com valores e percentuais
        legend_labels = [
            f"{label}\nR$ {valor:,.2f} ({valor/total*100:.1f}%)" 
            for label, valor in zip(labels, valores)
        ]
        
        self.chart_pagamentos.axes.legend(
            wedges, 
            legend_labels, 
            loc="center left", 
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9,
            frameon=False
        )
        
        # Iguala os aspectos para ter um círculo perfeito
        self.chart_pagamentos.axes.set_aspect('equal')
        
        # Ajusta o layout
        self.chart_pagamentos.fig.tight_layout()
        
        # Redesenha o canvas
        self.chart_pagamentos.draw()


    def atualizar_grafico_clientes(self, clientes):
        """Atualiza o gráfico de barras dos melhores clientes com estilo moderno"""
        # Configurar estilo
        colors = set_modern_style()
        
        # Limpa o gráfico
        self.chart_clientes.axes.clear()
        
        if not clientes:
            self.chart_clientes.draw()
            return
        
        # Extrai nomes e valores
        nomes = [item['nome'] for item in clientes]
        valores = [item['valor_total'] for item in clientes]
        
        # Encurtar nomes muito longos
        nomes_display = []
        for nome in nomes:
            if len(nome) > 12:
                nomes_display.append(nome[:10] + '...')
            else:
                nomes_display.append(nome)
        
        # Gradiente de cores para as barras
        color_map = matplotlib.cm.get_cmap('Purples')
        num_bars = len(nomes)
        bar_colors = [color_map(0.4 + 0.6 * i / num_bars) for i in range(num_bars)]
        
        # Cria o gráfico de barras verticais
        bars = self.chart_clientes.axes.bar(
            nomes_display, 
            valores, 
            color=bar_colors,
            width=0.7,
            edgecolor='white',
            linewidth=1
        )
        
        # Adiciona os valores em cima das barras
        for bar in bars:
            height = bar.get_height()
            self.chart_clientes.axes.text(
                bar.get_x() + bar.get_width()/2, 
                height * 1.01,
                f'R$ {height:,.0f}', 
                ha='center', 
                va='bottom', 
                fontsize=9,
                alpha=0.8
            )
        
        # Formata o gráfico
        self.chart_clientes.axes.set_ylabel('Valor Total (R$)', fontsize=11, fontweight='bold')
        
        # Remover bordas desnecessárias
        self.chart_clientes.axes.spines['top'].set_visible(False)
        self.chart_clientes.axes.spines['right'].set_visible(False)
        self.chart_clientes.axes.spines['left'].set_color('#cccccc')
        self.chart_clientes.axes.spines['bottom'].set_color('#cccccc')
        
        # Definir limites do eixo Y começando de zero
        self.chart_clientes.axes.set_ylim(bottom=0)
        
        # Formatando valores do eixo Y
        self.chart_clientes.axes.yaxis.set_major_formatter(
            matplotlib.ticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}')
        )
        
        # Rotaciona os nomes para melhor visualização
        self.chart_clientes.axes.tick_params(axis='x', rotation=30)
        
        # Ajusta o layout
        self.chart_clientes.fig.tight_layout()
        
        # Redesenha o canvas
        self.chart_clientes.draw()