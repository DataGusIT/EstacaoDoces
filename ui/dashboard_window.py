# --- Importações necessárias ---
import sys
import random
import datetime

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
                             QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
                             QMessageBox, QGroupBox, QGridLayout, QFrame, QSplitter, QApplication,
                             QHeaderView)
from PyQt5.QtCore import Qt, QDate, QTimer
from PyQt5.QtGui import QFont

# Usaremos qtawesome para ícones modernos e fáceis de usar
import qtawesome as qta

# --- Importações e configuração do Matplotlib ---
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np


class MplCanvas(FigureCanvas):
    """Canvas Matplotlib customizado e ciente do tema."""
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.setParent(parent)

    def apply_theme(self, theme_colors):
        """Aplica as cores do tema ao gráfico."""
        self.fig.patch.set_facecolor(theme_colors['bg_color'])
        self.axes.set_facecolor(theme_colors['surface_color'])
        
        # Cor dos eixos e textos
        self.axes.spines['top'].set_color(theme_colors['border_color'])
        self.axes.spines['bottom'].set_color(theme_colors['border_color'])
        self.axes.spines['left'].set_color(theme_colors['border_color'])
        self.axes.spines['right'].set_color(theme_colors['border_color'])
        
        self.axes.tick_params(axis='x', colors=theme_colors['text_secondary'])
        self.axes.tick_params(axis='y', colors=theme_colors['text_secondary'])
        
        self.axes.yaxis.label.set_color(theme_colors['text_color'])
        self.axes.xaxis.label.set_color(theme_colors['text_color'])
        self.axes.title.set_color(theme_colors['text_color'])
        
        # Estilo de fonte global para os gráficos
        plt.rcParams.update({
            'font.family': 'sans-serif',
            'font.size': 9,
            'text.color': theme_colors['text_color'],
            'axes.labelcolor': theme_colors['text_secondary']
        })

class DashboardWindow(QWidget):
    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.chartCanvases = {}
        self._initialized = False
        
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self._delayed_update)
        
        self._setup_ui()
        self._apply_stylesheet()
        
        self._initialized = True
        QTimer.singleShot(100, self._initial_load)
    
    def set_theme(self, theme_colors):
        """Permite atualizar o tema dinamicamente."""
        self.theme_colors = theme_colors
        self._apply_stylesheet()
        for canvas in self.chartCanvases.values():
            canvas.apply_theme(self.theme_colors)
        self.carregar_dados() # Recarrega os dados para redesenhar gráficos com novas cores

    def _setup_ui(self):
        """Cria e organiza todos os widgets da UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Barra de filtros
        filter_group = self._create_filter_group()
        main_layout.addWidget(filter_group, 0) # Stretch 0: não cresce
        
        # Splitter principal
        splitter = QSplitter(Qt.Horizontal)
        
        # --- Coluna da Esquerda (KPIs, Alertas e Gráfico Principal) ---
        left_column_widget = QWidget()
        left_layout = QVBoxLayout(left_column_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # Indicadores Chave e Contagens Gerais
        kpi_group = self._create_kpi_group()
        
        # Grupo de Alertas
        alerts_group = self._create_alerts_group()

        # Gráfico Principal
        main_chart_group = QGroupBox("Evolução de Vendas no Período")
        main_chart_layout = QVBoxLayout()
        self.chart_vendas = MplCanvas(parent=main_chart_group, width=5, height=3, dpi=100)
        self.chartCanvases['vendas_diarias'] = self.chart_vendas
        main_chart_layout.addWidget(self.chart_vendas)
        main_chart_group.setLayout(main_chart_layout)
        
        # ======================= ALTERAÇÃO DE DESTAQUE AQUI =======================
        # Adiciona os widgets ao layout da esquerda COM fatores de estiramento
        
        # KPIs: Fator 1 -> Cresce um pouco para ter destaque
        left_layout.addWidget(kpi_group, 1)
        
        # Alertas: Fator 0 -> Não cresce, fica compacto
        left_layout.addWidget(alerts_group, 0)
        
        # Gráfico: Fator 4 -> Pega a maior parte do espaço vertical extra
        left_layout.addWidget(main_chart_group, 4)
        # ==========================================================================
        
        splitter.addWidget(left_column_widget)
        
        # --- Coluna da Direita (Abas com detalhes) ---
        right_column_widget = QWidget()
        right_layout = QVBoxLayout(right_column_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        tabs_group = QGroupBox("Análise Detalhada")
        tabs_layout = QVBoxLayout()
        tabs = self._create_charts_tabs(tabs_group)
        tabs_layout.addWidget(tabs)
        tabs_group.setLayout(tabs_layout)
        right_layout.addWidget(tabs_group)
        splitter.addWidget(right_column_widget)
        
        splitter.setSizes([int(self.width() * 0.45), int(self.width() * 0.55)])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        # Adiciona o splitter com stretch 1 para ocupar o resto do espaço
        main_layout.addWidget(splitter, 1)
    
    def _create_alerts_group(self):
        """Cria o QGroupBox para os alertas operacionais."""
        group = QGroupBox("Alertas Operacionais")
        layout = QHBoxLayout(group)
        layout.setSpacing(15)

        # Helper para criar um card de alerta
        def create_alert_card(title, icon_name, icon_bg_color, object_name):
            card = QFrame()
            card.setObjectName(object_name) # Para estilização dinâmica
            card.setMinimumWidth(120)
            
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(5)
            
            # Layout do Ícone e Título
            top_layout = QHBoxLayout()
            icon_label = QLabel()
            icon_label.setFixedSize(24, 24)
            icon = qta.icon(icon_name, color='white')
            icon_label.setPixmap(icon.pixmap(16, 16))
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setStyleSheet(f"background-color: {icon_bg_color}; border-radius: 12px;")
            
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet("font-weight: bold;")
            
            top_layout.addWidget(icon_label)
            top_layout.addWidget(lbl_title)
            top_layout.addStretch()
            
            # Label para o valor (contador)
            lbl_count = QLabel("0")
            lbl_count.setObjectName("alertCount")
            lbl_count.setAlignment(Qt.AlignCenter)
            
            card.setProperty("countLabel", lbl_count)

            card_layout.addLayout(top_layout)
            card_layout.addWidget(lbl_count)
            
            return card

        # Criar os cards de alerta
        self.card_estoque_baixo = create_alert_card("Estoque Baixo", 'fa5s.exclamation-triangle', '#ffc107', 'alertCardWarning')
        self.card_vencendo = create_alert_card("Vencendo em 30d", 'fa5s.calendar-alt', '#17a2b8', 'alertCardInfo')
        self.card_vencidos = create_alert_card("Produtos Vencidos", 'fa5s.calendar-times', '#dc3545', 'alertCardDanger')

        layout.addWidget(self.card_estoque_baixo)
        layout.addWidget(self.card_vencendo)
        layout.addWidget(self.card_vencidos)
        
        return group

    def _create_filter_group(self):
        """Cria o QGroupBox para os filtros de data."""
        group = QGroupBox("Filtros")
        group.setObjectName("filterGroup") 
        
        # 1. Criamos um layout vertical principal para o grupo
        main_v_layout = QVBoxLayout(group)
        main_v_layout.setContentsMargins(10, 5, 10, 5)
        main_v_layout.setSpacing(0) # O espaçamento agora é controlado pelo layout horizontal

        # 2. Nosso layout de filtros agora é um layout horizontal separado
        filter_h_layout = QHBoxLayout()
        filter_h_layout.setSpacing(8)

        filter_h_layout.addWidget(QLabel("Período:"))
        self.cb_periodo = QComboBox()
        self.cb_periodo.addItems(["Hoje", "Última Semana", "Último Mês", "Personalizado"])
        self.cb_periodo.currentIndexChanged.connect(self.periodo_alterado)
        filter_h_layout.addWidget(self.cb_periodo)
        
        self.dt_inicio = QDateEdit(QDate.currentDate())
        self.dt_inicio.setCalendarPopup(True)
        self.dt_inicio.dateChanged.connect(self.data_alterada)
        
        self.dt_fim = QDateEdit(QDate.currentDate())
        self.dt_fim.setCalendarPopup(True)
        self.dt_fim.dateChanged.connect(self.data_alterada)
        
        filter_h_layout.addSpacing(10)
        filter_h_layout.addWidget(QLabel("De:"))
        filter_h_layout.addWidget(self.dt_inicio)
        filter_h_layout.addWidget(QLabel("Até:"))
        filter_h_layout.addWidget(self.dt_fim)
        filter_h_layout.addStretch()

        self.btn_atualizar = QPushButton(" Atualizar")
        self.btn_atualizar.clicked.connect(self.schedule_update)
        filter_h_layout.addWidget(self.btn_atualizar)

        # 3. Adicionamos o layout horizontal ao layout vertical
        main_v_layout.addLayout(filter_h_layout)
        
        # 4. A MÁGICA ACONTECE AQUI: Adicionamos o espaçador flexível.
        # Ele vai "empurrar" o layout dos filtros para cima, ocupando todo o espaço vertical extra.
        # main_v_layout.addStretch(1) # <<-- Esta linha foi removida, pois o QGroupBox já faz esse controle.
                                    # O layout do próprio QGroupBox já será suficiente.
        
        # O group.setLayout(main_v_layout) já é feito automaticamente pelo construtor QVBoxLayout(group)
        return group

    def _create_kpi_group(self):
        """Cria o QGroupBox para os KPIs e as contagens gerais."""
        group = QGroupBox("Indicadores Chave do Período")
        group_layout = QVBoxLayout(group)
        
        # --- Grid dos KPIs ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(15)
        self.card_faturamento = self._create_kpi_card("Faturamento Total", "R$ 0,00", 'fa5s.dollar-sign', '#28a745')
        self.card_lucro = self._create_kpi_card("Lucro Líquido", "R$ 0,00", 'fa5s.chart-line', '#007bff')
        self.card_vendas = self._create_kpi_card("Nº de Vendas", "0", 'fa5s.shopping-cart', '#6f42c1')
        self.card_ticket = self._create_kpi_card("Ticket Médio", "R$ 0,00", 'fa5s.receipt', '#fd7e14')
        grid_layout.addWidget(self.card_faturamento, 0, 0)
        grid_layout.addWidget(self.card_lucro, 0, 1)
        grid_layout.addWidget(self.card_vendas, 1, 0)
        grid_layout.addWidget(self.card_ticket, 1, 1)
        group_layout.addLayout(grid_layout)

        # --- Separador ---
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("kpiSeparator")
        group_layout.addWidget(separator)
        
        # --- Layout das Contagens Gerais ---
        counts_layout = QHBoxLayout()
        counts_layout.setSpacing(20)
        
        self.lbl_total_produtos = QLabel("Produtos: 0")
        self.lbl_total_clientes = QLabel("Clientes: 0")
        self.lbl_total_fornecedores = QLabel("Fornecedores: 0")
        self.lbl_total_promocoes = QLabel("Promoções Ativas: 0")
        
        for label in [self.lbl_total_produtos, self.lbl_total_clientes, self.lbl_total_fornecedores, self.lbl_total_promocoes]:
            label.setObjectName("totalCountLabel")
            counts_layout.addWidget(label, 0, Qt.AlignCenter)
        
        group_layout.addLayout(counts_layout)
        return group

    def _create_kpi_card(self, title, value, icon_name, icon_bg_color):
        """Cria um widget de card individual."""
        card = QFrame()
        card.setObjectName("kpiCard")
        
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)

        # Ícone
        icon_label = QLabel()
        icon_label.setFixedSize(40, 40)
        icon = qta.icon(icon_name, color='white')
        icon_label.setPixmap(icon.pixmap(30, 30))
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet(f"""
            background-color: {icon_bg_color};
            border-radius: 20px;
        """)
        
        # Textos
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("kpiTitle")
        lbl_value = QLabel(value)
        lbl_value.setObjectName("kpiValue")
        
        # Salva referência ao label de valor para atualização futura
        card.setProperty("valueLabel", lbl_value)

        text_layout.addWidget(lbl_title)
        text_layout.addWidget(lbl_value)
        
        card_layout.addWidget(icon_label)
        card_layout.addSpacing(10)
        card_layout.addLayout(text_layout)
        
        return card

    def _create_charts_tabs(self, parent):
        """Cria o QTabWidget com as abas de gráficos e tabelas detalhadas."""
        tabs = QTabWidget()
        
        # Função helper para criar uma aba
        def create_tab(title, chart_name, columns):
            tab_widget = QWidget()
            layout = QVBoxLayout(tab_widget)
            layout.setContentsMargins(0, 5, 0, 0)
            
            splitter = QSplitter(Qt.Vertical)
            
            # Tabela
            table = QTableWidget()
            table.setColumnCount(len(columns))
            table.setHorizontalHeaderLabels(columns)
            table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
            table.verticalHeader().setVisible(False)
            splitter.addWidget(table)
            
            # Gráfico
            canvas = MplCanvas(parent=parent, width=5, height=2.5, dpi=100)
            self.chartCanvases[chart_name] = canvas
            splitter.addWidget(canvas)
            
            splitter.setSizes([150, 250])
            layout.addWidget(splitter)
            
            return tab_widget, table
        
        # Aba de Produtos
        tab_produtos, self.tabela_produtos = create_tab("Produtos", 'produtos', ['Produto', 'Qtde', 'Valor Total', '% Part.'])
        tabs.addTab(tab_produtos, qta.icon('fa5s.box', color=self.theme_colors['text_secondary']), "Produtos")
        
        # Aba de Pagamentos
        tab_pagamentos, self.tabela_pagamentos = create_tab("Pagamentos", 'pagamentos', ['Forma', 'Valor Total', '% Part.'])
        tabs.addTab(tab_pagamentos, qta.icon('fa5s.credit-card', color=self.theme_colors['text_secondary']), "Pagamentos")

        # Aba de Clientes
        tab_clientes, self.tabela_clientes = create_tab("Clientes", 'clientes', ['Cliente', 'Nº Compras', 'Valor Total', 'Ticket Médio'])
        tabs.addTab(tab_clientes, qta.icon('fa5s.users', color=self.theme_colors['text_secondary']), "Clientes")
        
        return tabs

    def _apply_stylesheet(self):
        """Aplica a folha de estilo QSS baseada no tema."""
        colors = self.theme_colors
        self.setStyleSheet(f"""
            DashboardWindow {{
                background-color: {colors['bg_color']};
            }}
            QGroupBox {{
                background-color: {colors['surface_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 8px;
                margin-top: 10px;
                font-weight: bold;
                color: {colors['text_color']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 10px;
                left: 10px;
                background-color: {colors['surface_color']};
            }}
            QLabel {{
                color: {colors['text_secondary']};
                background-color: transparent;
            }}
            #kpiCard {{
                background-color: {colors['surface_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 8px;
            }}
            #kpiCard:hover {{
                border: 1px solid {colors['accent_color']};
            }}
            #kpiTitle {{
                font-size: 12px;
                color: {colors['text_secondary']};
            }}
            #kpiValue {{
                font-size: 20px;
                font-weight: bold;
                color: {colors['text_color']};
            }}
            #kpiSeparator {{
                background-color: {colors['border_color']};
            }}
            #totalCountLabel {{
                font-size: 11px;
                color: {colors['text_secondary']};
            }}
            #alertCardWarning, #alertCardInfo, #alertCardDanger {{
                background-color: {colors['surface_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 8px;
                padding: 10px;
            }}
            #alertCount {{
                font-size: 24px;
                font-weight: bold;
                color: {colors['text_color']};
            }}
            /* Estilo dinâmico para quando um alerta está ativo */
            #alertCardWarning[hasAlert="true"] {{ border: 2px solid #ffc107; }}
            #alertCardInfo[hasAlert="true"] {{ border: 2px solid #17a2b8; }}
            #alertCardDanger[hasAlert="true"] {{ border: 2px solid #dc3545; }}

            QComboBox, QDateEdit {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 5px;
                border-radius: 4px;
            }}
            QComboBox::drop-down, QDateEdit::drop-down {{
                border: none;
            }}
            QPushButton {{
                background-color: {colors['accent_color']};
                color: white;
                border: none;
                padding: 6px 14px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #0056b3; /* Um pouco mais escuro no hover */
            }}
            QTabWidget::pane {{
                border: 1px solid {colors['border_color']};
                border-top: none;
                border-radius: 0 0 8px 8px;
                background-color: {colors['surface_color']};
            }}
            QTabBar::tab {{
                background: transparent;
                color: {colors['text_secondary']};
                padding: 8px 15px;
                border: 1px solid transparent;
                border-bottom: none;
            }}
            QTabBar::tab:selected {{
                background: {colors['surface_color']};
                color: {colors['accent_color']};
                border: 1px solid {colors['border_color']};
                border-bottom: 1px solid {colors['surface_color']};
                border-radius: 8px 8px 0 0;
            }}
            QTableWidget {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: none;
                gridline-color: {colors['border_color']};
            }}
            QHeaderView::section {{
                background-color: {colors['bg_color']};
                color: {colors['text_secondary']};
                padding: 4px;
                border: 1px solid {colors['border_color']};
                font-weight: bold;
            }}
            QSplitter::handle {{
                background-color: {colors['border_color']};
            }}
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            QSplitter::handle:vertical {{
                height: 1px;
            }}
             /* Estilos para o grupo de filtros ficar mais compacto */
            #filterGroup QComboBox,
            #filterGroup QDateEdit,
            #filterGroup QPushButton {{
                padding: 4px 8px; /* Menos preenchimento vertical */
                font-size: 9pt;   /* Fonte um pouco menor */
            }}
            
            #filterGroup QPushButton {{
                font-weight: normal; /* Botão sem negrito para ser mais sutil */
            }}
        """)
        
        # Força atualização dos ícones
        self.btn_atualizar.setIcon(qta.icon('fa5s.sync-alt', color='white'))
        
        # ======================= A CORREÇÃO CRÍTICA =========================
        # Força este widget e todos os seus filhos a relerem a folha de estilo,
        # aplicando as regras mais específicas que acabamos de definir.
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
        # ====================================================================== q

    # --- Métodos de Lógica (quase inalterados, mas agora atualizam nova UI) ---
    
    def _initial_load(self):
        if self._initialized:
            self.periodo_alterado(0)
    
    def _delayed_update(self):
        if self._initialized:
            self.carregar_dados()
            
    def schedule_update(self):
        if self._initialized:
            self.update_timer.start(50)

    def periodo_alterado(self, index):
        if not self._initialized: return
        periodo = self.cb_periodo.currentText()
        hoje = QDate.currentDate()
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
        
        personalizado = (periodo == "Personalizado")
        self.dt_inicio.setEnabled(personalizado)
        self.dt_fim.setEnabled(personalizado)
        
        self.dt_inicio.blockSignals(False)
        self.dt_fim.blockSignals(False)
        self.schedule_update()

    def data_alterada(self):
        if not self._initialized: return
        self.cb_periodo.blockSignals(True)
        self.cb_periodo.setCurrentText("Personalizado")
        self.cb_periodo.blockSignals(False)
        if self.dt_inicio.date() > self.dt_fim.date():
            self.dt_fim.setDate(self.dt_inicio.date())
        self.schedule_update()

    def carregar_dados(self):
        if not self._initialized: 
            return
        
        try:
            data_inicio = self.dt_inicio.date().toString("yyyy-MM-dd")
            data_fim = self.dt_fim.date().toString("yyyy-MM-dd")
            
            dados = self.db.obter_dados_dashboard(data_inicio, data_fim)
            
            if not dados:
                self.mostrar_sem_dados()
                return
            
            # --- Atualizar KPIs ---
            faturamento_valor = dados.get('faturamento', 0)
            num_vendas_valor = dados.get('num_vendas', 0)
            ticket_medio = faturamento_valor / num_vendas_valor if num_vendas_valor > 0 else 0
            
            self.card_faturamento.findChild(QLabel, "kpiValue").setText(f"R$ {faturamento_valor:.2f}")
            self.card_lucro.findChild(QLabel, "kpiValue").setText(f"R$ {dados.get('lucro', 0):.2f}")
            self.card_vendas.findChild(QLabel, "kpiValue").setText(str(num_vendas_valor))
            self.card_ticket.findChild(QLabel, "kpiValue").setText(f"R$ {ticket_medio:.2f}")

            # --- Atualizar Contagens Gerais ---
            self.lbl_total_produtos.setText(f"Produtos: <b>{dados.get('total_produtos', 0)}</b>")
            self.lbl_total_clientes.setText(f"Clientes: <b>{dados.get('total_clientes', 0)}</b>")
            self.lbl_total_fornecedores.setText(f"Fornecedores: <b>{dados.get('total_fornecedores', 0)}</b>")
            self.lbl_total_promocoes.setText(f"Promoções Ativas: <b>{dados.get('total_promocoes_ativas', 0)}</b>")

            # --- Atualizar Alertas ---
            alertas = dados.get('alertas', {})
            self.card_estoque_baixo.findChild(QLabel, "alertCount").setText(str(alertas.get('estoque_baixo', 0)))
            self.card_vencendo.findChild(QLabel, "alertCount").setText(str(alertas.get('vencendo_30d', 0)))
            self.card_vencidos.findChild(QLabel, "alertCount").setText(str(alertas.get('vencidos', 0)))

            # Atualizar estilo dos cards de alerta se houver alertas
            self.card_estoque_baixo.setProperty("hasAlert", alertas.get('estoque_baixo', 0) > 0)
            self.card_vencendo.setProperty("hasAlert", alertas.get('vencendo_30d', 0) > 0)
            self.card_vencidos.setProperty("hasAlert", alertas.get('vencidos', 0) > 0)

            # --- Atualizar Tabelas e Gráficos (sem alterações aqui) ---
            self._atualizar_tabela(self.tabela_produtos, dados.get('produtos', []), ['Produto', 'Qtde', 'Valor Total', '% Part.'], faturamento_valor)
            self._atualizar_tabela(self.tabela_pagamentos, dados.get('pagamentos', []), ['Forma', 'Valor Total', '% Part.'], faturamento_valor)
            self._atualizar_tabela(self.tabela_clientes, dados.get('clientes', []), ['Cliente', 'Nº Compras', 'Valor Total', 'Ticket Médio'])

            self.atualizar_grafico_vendas_diarias(dados.get('vendas_diarias', []))
            self.atualizar_grafico_produtos(dados.get('produtos', [])[:5])
            self.atualizar_grafico_pagamentos(dados.get('pagamentos', []))
            self.atualizar_grafico_clientes(dados.get('clientes', [])[:5])

            # Força a atualização do estilo dos cards
            for card in [self.card_estoque_baixo, self.card_vencendo, self.card_vencidos]:
                card.style().unpolish(card)
                card.style().polish(card)

        except Exception as e:
            QMessageBox.critical(self, "Erro na Interface", f"Ocorreu um erro ao exibir os dados do dashboard.\n\nErro: {e}")
            self.mostrar_sem_dados()

    def _atualizar_tabela(self, table, data, keys, total_faturamento=None):
        table.setRowCount(0)
        for i, row_data in enumerate(data):
            table.insertRow(i)
            for j, key in enumerate(keys):
                item_text = ""
                if key == 'valor_total' or key == 'ticket_medio':
                    item_text = f"R$ {row_data.get(key, 0):.2f}"
                elif key == '% part.':
                    participacao = (row_data['valor_total'] / total_faturamento * 100) if total_faturamento else 0
                    item_text = f"{participacao:.2f}%"
                else:
                    item_text = str(row_data.get(key, ''))
                
                table.setItem(i, j, QTableWidgetItem(item_text))
    
    def mostrar_sem_dados(self):
        """Limpa a UI quando não há dados."""
        self.card_faturamento.findChild(QLabel, "kpiValue").setText("R$ 0,00")
        self.card_lucro.findChild(QLabel, "kpiValue").setText("R$ 0,00")
        self.card_vendas.findChild(QLabel, "kpiValue").setText("0")
        self.card_ticket.findChild(QLabel, "kpiValue").setText("R$ 0,00")

        self.tabela_produtos.setRowCount(0)
        self.tabela_pagamentos.setRowCount(0)
        self.tabela_clientes.setRowCount(0)

        for canvas in self.chartCanvases.values():
            canvas.axes.clear()
            canvas.apply_theme(self.theme_colors) # Aplica fundo mesmo se vazio
            canvas.draw()
            
    # --- Funções de Geração de Gráficos (Atualizadas para usar tema) ---

    def atualizar_grafico_vendas_diarias(self, vendas_diarias):
        canvas = self.chartCanvases['vendas_diarias']
        canvas.axes.clear()
        canvas.apply_theme(self.theme_colors)
        
        if not vendas_diarias:
            canvas.draw()
            return
            
        datas = [item['data'] for item in vendas_diarias]
        valores = [item['valor'] for item in vendas_diarias]
        
        canvas.axes.plot(datas, valores, marker='o', linestyle='-', color=self.theme_colors['accent_color'])
        canvas.axes.fill_between(datas, valores, color=self.theme_colors['accent_color'], alpha=0.1)
        
        canvas.axes.set_ylabel('Valor (R$)')
        canvas.axes.set_ylim(bottom=0)
        canvas.axes.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
        canvas.fig.autofmt_xdate(rotation=20, ha='right')
        canvas.fig.tight_layout(pad=2.0)
        canvas.draw()

    def atualizar_grafico_produtos(self, produtos):
        canvas = self.chartCanvases['produtos']
        canvas.axes.clear()
        canvas.apply_theme(self.theme_colors)

        if not produtos:
            canvas.draw()
            return
        
        nomes = [p['nome'][:15] + '...' if len(p['nome']) > 15 else p['nome'] for p in produtos]
        valores = [p['valor_total'] for p in produtos]
        
        bars = canvas.axes.barh(nomes, valores, color=self.theme_colors['accent_color'], height=0.6)
        canvas.axes.invert_yaxis()
        canvas.axes.set_xlabel('Valor Total (R$)')
        canvas.axes.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
        
        canvas.fig.tight_layout(pad=2.0)
        canvas.draw()

    def atualizar_grafico_pagamentos(self, pagamentos):
        canvas = self.chartCanvases['pagamentos']
        canvas.axes.clear()
        canvas.apply_theme(self.theme_colors)
        
        if not pagamentos:
            canvas.draw()
            return
            
        labels = [p['forma'] for p in pagamentos]
        valores = [p['valor_total'] for p in pagamentos]
        
        pie_colors = ['#007AFF', '#34C759', '#FF9500', '#FF3B30', '#AF52DE', '#5856D6']
        
        wedges, texts, autotexts = canvas.axes.pie(valores, 
            autopct='%1.1f%%',
            startangle=90, 
            colors=pie_colors,
            wedgeprops={'edgecolor': self.theme_colors['surface_color'], 'linewidth': 2})
        
        plt.setp(autotexts, size=8, weight="bold", color="white")
        
        canvas.axes.legend(wedges, labels,
                  title="Formas",
                  loc="center left",
                  bbox_to_anchor=(0.95, 0, 0.5, 1),
                  frameon=False)
                  
        canvas.axes.set_title("Distribuição por Pagamento", color=self.theme_colors['text_color'])
        canvas.draw()


    def atualizar_grafico_clientes(self, clientes):
        canvas = self.chartCanvases['clientes']
        canvas.axes.clear()
        canvas.apply_theme(self.theme_colors)

        if not clientes:
            canvas.draw()
            return

        nomes = [c['nome'][:12] + '...' if len(c['nome']) > 12 else c['nome'] for c in clientes]
        valores = [c['valor_total'] for c in clientes]

        bars = canvas.axes.bar(nomes, valores, color=self.theme_colors['accent_color'], width=0.6)
        canvas.axes.set_ylabel('Valor Total (R$)')
        canvas.axes.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: f'R$ {x:,.0f}'))
        canvas.fig.autofmt_xdate(rotation=30, ha='right')

        canvas.fig.tight_layout(pad=2.0)
        canvas.draw()

   

