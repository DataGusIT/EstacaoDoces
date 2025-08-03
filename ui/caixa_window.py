from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
                            QMessageBox, QDialog, QFormLayout, QTextEdit, QDoubleSpinBox,
                            QSpinBox, QHeaderView, QCheckBox, QGroupBox, QGridLayout, QFrame,
                            QSplitter, QApplication,  QFileDialog, QMessageBox, QHBoxLayout, QLayout, QRadioButton, QCompleter)
from PyQt5.QtCore import Qt, QDate, QDateTime, QMarginsF
from PyQt5.QtGui import QIcon, QColor, QFont, QTextDocument, QPageSize, QPageLayout, QIcon, QPixmap
from PyQt5.QtPrintSupport import QPrinter
import os
from ui.icon_manager import IconManager
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from collections import defaultdict
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

import datetime

class AutoPopupComboBox(QComboBox):
    """
    Um QComboBox que exibe sua lista de itens automaticamente
    ao ser clicado.
    """
    def mousePressEvent(self, event):
        # Primeiro, executa o evento de clique padrão
        super().mousePressEvent(event)
        # Em seguida, força a exibição do popup com a lista
        self.showPopup()

class CaixaWindow(QWidget):
    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.caixa_atual = None
        self.itens_venda = []
        self.total_venda = 0.0
        self.dados_relatorio_atual = None # <-- ADICIONE ESTA LINHA

        # --- CONFIGURAÇÕES DO RELATÓRIO (ADICIONADAS) ---
        self.logo_path = "assets/img/GestorX (2).png"
        self.company_info = {
            "nome": "Estação Doces",
            "endereco": "Rua do Comércio, 123 - Centro",
            "contato": "Telefone: (11) 99999-8888 | Email: contato@estacaodoces.com"
        }
        self.initUI()
        self.verificar_caixa_aberto()
        self.carregar_clientes()
        self.carregar_produtos()
        self.setup_codigo_barras()

    def _update_icons(self):
        """Define ou atualiza todos os ícones da janela usando o IconManager."""
        # Define as cores principais com base no tema
        text_color = self.theme_colors.get('text_color', '#000000')
        text_secondary = self.theme_colors.get('text_secondary', '#6d6d70')
        accent_color = self.theme_colors.get('accent_color', '#007AFF')
        
        # Cores específicas para ações
        success_color = "#28a745"
        danger_color = "#dc3545"
        warning_color = "#ffc107"

        # --- Abas Principais ---
        self.tabs.setTabIcon(0, IconManager.get_icon('caixa', color=accent_color))
        self.tabs.setTabIcon(1, IconManager.get_icon('relatorio', color=accent_color))
        self.tabs.setTabIcon(2, IconManager.get_icon('report', color=accent_color))

        # --- Status do Caixa ---
        self.btn_abrir_caixa.setIcon(IconManager.get_icon('unlock', color=text_color))
        self.btn_fechar_caixa.setIcon(IconManager.get_icon('lock', color=text_color))
        
        # --- Tab de Vendas (PDV) ---
        self.btn_add_cliente.setIcon(IconManager.get_icon('add', color=text_color))
        # self.btn_atualizar_cliente.setIcon(IconManager.get_icon('atualizar', color=text_secondary))
        # self.btn_atualizar_produto.setIcon(IconManager.get_icon('atualizar', color=text_secondary))
        self.btn_adicionar_item.setIcon(IconManager.get_icon('add', color=text_color))
        self.btn_limpar.setIcon(IconManager.get_icon('clear', color=warning_color))
        self.btn_finalizar.setIcon(IconManager.get_icon('check', color='white')) # Fundo verde, ícone branco

        # --- Tab de Movimentações ---
        self.btn_nova_entrada.setIcon(IconManager.get_icon('add', color=success_color))
        self.btn_nova_saida.setIcon(IconManager.get_icon('send', color=danger_color))
        self.btn_filtrar.setIcon(IconManager.get_icon('filter', color=text_color))

        # --- Tab de Relatórios ---
        self.btn_gerar_relatorio.setIcon(IconManager.get_icon('report', color=text_color))

    def set_theme(self, theme_colors):
        """Aplica as cores do tema e atualiza os ícones."""
        self.theme_colors = theme_colors
        self._update_icons()

        if hasattr(self, 'lbl_imagem_produto'):
            bg_color = self.theme_colors.get('surface_color', '#f0f0f0')
            border_color = self.theme_colors.get('border_color', '#ccc')
            text_color = self.theme_colors.get('text_secondary', '#6d6d70')
            
            self.lbl_imagem_produto.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color};
                    border: 2px dashed {border_color};
                    border-radius: 8px;
                    color: {text_color};
                    font-style: italic;
                    font-size: 10pt;
                    padding: 10px;
                }}
            """)
        # Força a reavaliação da folha de estilo herdada
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def initUI(self):
        # Layout principal
        main_layout = QVBoxLayout(self)
        
        # Status do caixa
        self.frame_status = QFrame()
        self.frame_status.setFrameShape(QFrame.StyledPanel)
        self.frame_status.setFrameShadow(QFrame.Raised)        
        status_layout = QHBoxLayout(self.frame_status)
        
        self.lbl_status = QLabel("Status do Caixa: Fechado")
        self.lbl_status.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.lbl_status)
        
        self.lbl_saldo = QLabel("Saldo Atual: R$ 0,00")
        self.lbl_saldo.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.lbl_saldo)
        
        self.btn_abrir_caixa = QPushButton(" Abrir Caixa") # Espaço para o ícone
        self.btn_abrir_caixa.clicked.connect(self.abrir_caixa)
        status_layout.addWidget(self.btn_abrir_caixa)
        
        self.btn_fechar_caixa = QPushButton(" Fechar Caixa") # Espaço para o ícone
        self.btn_fechar_caixa.setEnabled(False)
        self.btn_fechar_caixa.clicked.connect(self.fechar_caixa)
        status_layout.addWidget(self.btn_fechar_caixa)
        
        main_layout.addWidget(self.frame_status)
        
        # Tabs para operações
        self.tabs = QTabWidget()
        
        # Tab de Vendas (PDV)
        self.tab_vendas = QWidget()
        self.setup_vendas_tab()
        self.tabs.addTab(self.tab_vendas, " Vendas (PDV)")
        
        # Tab de Movimentações
        self.tab_movimentos = QWidget()
        self.setup_movimentos_tab()
        self.tabs.addTab(self.tab_movimentos, " Movimentações")
        
        # Tab de Relatórios
        self.tab_relatorios = QWidget()
        self.setup_relatorios_tab()
        self.tabs.addTab(self.tab_relatorios, " Relatórios de Caixa")
        
        main_layout.addWidget(self.tabs)

        # CHAMA O MÉTODO PARA CONFIGURAR OS ÍCONES
        self._update_icons()
    
    def _create_combobox_with_icon(self, combobox, icon_name):
        """
        Cria um widget composto que parece um QComboBox com um ícone à direita.
        """
        # Cores e ícone
        border_color = self.theme_colors.get('border_color', '#ccc')
        surface_color = self.theme_colors.get('surface_color', '#f0f0f0')
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        
        # 1. Widget contêiner principal com borda
        container = QWidget()
        container.setStyleSheet(f"""
            QWidget {{
                border: 1px solid {border_color};
                border-radius: 4px;
                background-color: {surface_color};
            }}
        """)

        # 2. Layout para organizar o ComboBox e o ícone
        layout = QHBoxLayout(container)
        layout.setContentsMargins(5, 0, 5, 0) # Espaçamento interno
        layout.setSpacing(0)

        # 3. Remover a borda do ComboBox original para que ele se misture
        combobox.setStyleSheet("border: none; background-color: transparent;")
        
        # 4. Label para o ícone
        icon_label = QLabel()
        icon_pixmap = IconManager.get_icon(icon_name, color=icon_color).pixmap(12, 12)
        icon_label.setPixmap(icon_pixmap)
        
        # 5. Adicionar widgets ao layout
        layout.addWidget(combobox) # O ComboBox ocupa a maior parte do espaço
        layout.addWidget(icon_label) # O ícone fica no final

        return container
    
    def setup_vendas_tab(self):
        # Layout principal da aba de vendas
        main_layout = QHBoxLayout(self.tab_vendas)
        splitter = QSplitter(Qt.Horizontal)
        left_panel_widget = QWidget()
        layout_esquerda = QVBoxLayout(left_panel_widget)
        layout_esquerda.setContentsMargins(0, 0, 0, 0)
        frame_info = QFrame()
        frame_info.setFrameShape(QFrame.StyledPanel)
        frame_info_layout = QGridLayout(frame_info)
        
        # ===== INÍCIO DA MUDANÇA =====

        # Obter o caminho do ícone uma vez
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        dropdown_icon_path = IconManager.get_icon_path('chevron_down', color=icon_color, size=12)
        # É crucial usar barras normais '/' no caminho para CSS
        dropdown_icon_path = dropdown_icon_path.replace('\\', '/')

        # Definir o estilo que será aplicado a ambos os ComboBox
        combobox_style = f"""
            QComboBox {{
                padding-right: 20px; /* Deixa espaço para o ícone */
            }}
            QComboBox::drop-down {{
                border: none; /* Remove a borda do botão de dropdown */
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: url({dropdown_icon_path}); /* Usa o nosso ícone */
            }}
        """

        # --- Cliente ---
        frame_info_layout.addWidget(QLabel("Cliente:"), 0, 0)
        self.cb_cliente = QComboBox() # ComboBox padrão
        self.cb_cliente.setMinimumWidth(200)
        self.cb_cliente.setStyleSheet(combobox_style) # Aplica o estilo
        frame_info_layout.addWidget(self.cb_cliente, 0, 1)

         # --- INÍCIO DA REMOÇÃO (CLIENTE) ---
        
        # O layout btn_container_cliente não é mais necessário para um único botão.
        # btn_container_cliente = QHBoxLayout() 
        
        self.btn_add_cliente = QPushButton()
        self.btn_add_cliente.setFixedSize(30, 30)
        self.btn_add_cliente.setToolTip("Adicionar Novo Cliente")
        self.btn_add_cliente.clicked.connect(self.adicionar_novo_cliente)
        
        # A PARTIR DAQUI, REMOVA OU COMENTE AS LINHAS DO BOTÃO DE ATUALIZAR
        # self.btn_atualizar_cliente = QPushButton()
        # self.btn_atualizar_cliente.setFixedSize(30, 30)
        # self.btn_atualizar_cliente.setToolTip("Atualizar lista de clientes")
        # self.btn_atualizar_cliente.clicked.connect(self.carregar_clientes)
        
        # Adicione o btn_add_cliente diretamente ao layout principal
        # btn_container_cliente.addWidget(self.btn_add_cliente)
        # btn_container_cliente.addWidget(self.btn_atualizar_cliente) # LINHA REMOVIDA
        # frame_info_layout.addLayout(btn_container_cliente, 0, 2)
        
        # SUBSTITUA as linhas acima por esta, que adiciona apenas o botão de "Adicionar":
        frame_info_layout.addWidget(self.btn_add_cliente, 0, 2)

        # --- FIM DA REMOÇÃO (CLIENTE) ---

        # --- Produto ---
        frame_info_layout.addWidget(QLabel("Produto/Código:"), 1, 0)
        self.cb_produto = AutoPopupComboBox() # Usando a classe que auto-abre
        self.cb_produto.setEditable(True)
        # ... (código de configuração do cb_produto) ...
        self.cb_produto.setStyleSheet(combobox_style) # Aplica o mesmo estilo
        frame_info_layout.addWidget(self.cb_produto, 1, 1)

        # --- INÍCIO DA REMOÇÃO (PRODUTO) ---
        
        # REMOVA OU COMENTE AS LINHAS A SEGUIR
        # self.btn_atualizar_produto = QPushButton()
        # self.btn_atualizar_produto.setFixedSize(30, 30)
        # self.btn_atualizar_produto.setToolTip("Atualizar lista de produtos")
        # self.btn_atualizar_produto.clicked.connect(self.carregar_produtos)
        # frame_info_layout.addWidget(self.btn_atualizar_produto, 1, 2)
        
        # --- FIM DA REMOÇÃO (PRODUTO) ---

        #self.btn_atualizar_produto = QPushButton()
        #self.btn_atualizar_produto.setFixedSize(30, 30)
        #self.btn_atualizar_produto.setToolTip("Atualizar lista de produtos")
        #self.btn_atualizar_produto.clicked.connect(self.carregar_produtos)
        #frame_info_layout.addWidget(self.btn_atualizar_produto, 1, 2)
        
        # ===== FIM DA MUDANÇA =====
        
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
        self.btn_adicionar_item = QPushButton(" Adicionar Item")
        self.btn_adicionar_item.clicked.connect(self.adicionar_item)
        frame_info_layout.addWidget(self.btn_adicionar_item, 0, 5, 2, 1)
        
        layout_esquerda.addWidget(frame_info)
        
        # Tabela de itens
        self.tabela_itens = QTableWidget()
        self.tabela_itens.setColumnCount(6)
        self.tabela_itens.setHorizontalHeaderLabels(['Cód.', 'Produto', 'Qtde', 'Preço Unit.', 'Subtotal', ''])
        self.tabela_itens.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela_itens.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_itens.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_itens.setColumnWidth(5, 40)
        layout_esquerda.addWidget(self.tabela_itens)
        
        # Frame inferior com total e finalização
        frame_total = QFrame()
        frame_total.setFrameShape(QFrame.StyledPanel)
        frame_total_layout = QHBoxLayout(frame_total)
        self.lbl_total = QLabel("Total: R$ 0,00")
        self.lbl_total.setStyleSheet("font-size: 18px; font-weight: bold;")
        frame_total_layout.addWidget(self.lbl_total)
        frame_total_layout.addStretch()
        self.btn_limpar = QPushButton(" Limpar Venda")
        self.btn_limpar.clicked.connect(self.limpar_venda)
        frame_total_layout.addWidget(self.btn_limpar)
        self.btn_finalizar = QPushButton(" Finalizar Venda")
        self.btn_finalizar.clicked.connect(self.finalizar_venda)
        self.btn_finalizar.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        frame_total_layout.addWidget(self.btn_finalizar)
        
        layout_esquerda.addWidget(frame_total)
        splitter.addWidget(left_panel_widget)

        # -- PAINEL DIREITO (IMAGEM DO PRODUTO) --
        right_panel_widget = QWidget()
        layout_direita = QVBoxLayout(right_panel_widget)
        
        self.lbl_imagem_produto = QLabel("Selecione um produto para ver a imagem")
        self.lbl_imagem_produto.setAlignment(Qt.AlignCenter)
        self.lbl_imagem_produto.setMinimumSize(250, 250)
        layout_direita.addWidget(self.lbl_imagem_produto, 1)
        
        splitter.addWidget(right_panel_widget)
        
        # Configurar tamanhos do splitter
        splitter.setSizes([700, 300]) # Tamanho inicial (esquerda, direita)
        main_layout.addWidget(splitter)
    

    def adicionar_item_pelo_codigo(self):
        """Busca um produto pelo código de barras e o adiciona ao carrinho."""
        codigo_ou_nome = self.cb_produto.currentText().strip()
        if not codigo_ou_nome:
            return

        # Procura no ComboBox pelo código de barras ou nome
        index_encontrado = -1
        for i in range(self.cb_produto.count()):
            produto_data = self.cb_produto.itemData(i)
            if produto_data and (produto_data.get('codigo_barras') == codigo_ou_nome or produto_data.get('nome').lower() == codigo_ou_nome.lower()):
                index_encontrado = i
                break
        
        if index_encontrado != -1:
            # Seleciona o produto encontrado no ComboBox, que vai disparar produto_selecionado
            self.cb_produto.setCurrentIndex(index_encontrado)
            # Chama a função de adicionar item
            self.adicionar_item()
        else:
            QMessageBox.warning(self, "Produto não encontrado", f"Nenhum produto com o código ou nome '{codigo_ou_nome}' foi encontrado.")
            self.cb_produto.setCurrentText("") # Limpa para a próxima leitura
            self.cb_produto.setFocus()
            
    def buscar_produto(self):
        """
        Busca um produto pelo código de barras digitado e o adiciona ao carrinho.
        Este método é acionado ao pressionar Enter no campo de produto.
        """
        codigo_barras = self.cb_produto.currentText().strip()
        if not codigo_barras:
            return

        # Procura o produto no ComboBox pelo código de barras
        index_encontrado = -1
        for i in range(self.cb_produto.count()):
            produto_data = self.cb_produto.itemData(i)
            if produto_data and produto_data.get('codigo_barras') == codigo_barras:
                index_encontrado = i
                break
        
        if index_encontrado != -1:
            # Seleciona o produto encontrado no ComboBox
            self.cb_produto.setCurrentIndex(index_encontrado)
            # Chama imediatamente a função de adicionar, simulando "scan and add"
            self.adicionar_item()
        else:
            QMessageBox.warning(self, "Produto não encontrado", f"Nenhum produto com o código de barras '{codigo_barras}' foi encontrado.")
            # Limpa o campo para a próxima leitura
            self.cb_produto.setCurrentText("")
            self.cb_produto.setFocus()
    
    
    def verificar_promocoes(self, produto):
        """Verifica e aplica promoções ativas"""
        promocoes = self.db.listar_promocoes_ativas()
        for promocao in promocoes:
            if promocao['produto_id'] == produto['id']:
                self.spin_preco.setValue(promocao['preco_promocional'])
                break
    
    def setup_movimentos_tab(self):
        layout = QVBoxLayout(self.tab_movimentos)
        
        # Frame superior com botões de ação
        frame_acoes = QFrame()
        frame_acoes_layout = QHBoxLayout(frame_acoes)
        
        self.btn_nova_entrada = QPushButton(" Nova Entrada")        
        self.btn_nova_entrada.clicked.connect(lambda: self.novo_movimento("Entrada"))
        frame_acoes_layout.addWidget(self.btn_nova_entrada)
        
        self.btn_nova_saida = QPushButton(" Nova Saída")
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
        
        self.btn_filtrar = QPushButton(" Filtrar")
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
        # O layout principal agora é um QVBoxLayout para empilhar os widgets
        main_layout = QVBoxLayout(self.tab_relatorios)
        
        # Frame superior com filtros
        frame_filtros = QFrame()
        frame_filtros.setFrameShape(QFrame.StyledPanel)
        frame_filtros_layout = QHBoxLayout(frame_filtros)
        frame_filtros_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        self.btn_gerar_relatorio = QPushButton(" Gerar Relatório")
        self.btn_gerar_relatorio.clicked.connect(self.gerar_relatorio)
        frame_filtros_layout.addStretch()
        frame_filtros_layout.addWidget(self.btn_gerar_relatorio)
        
        # Adiciona o grupo de filtros ao layout principal
        main_layout.addWidget(frame_filtros)
        
        # Tabs para relatórios específicos
        self.rel_tabs = QTabWidget() # Renomeado para não conflitar com self.tabs
        
        # Tab de resumo
        tab_resumo = QWidget()
        tab_resumo_layout = QVBoxLayout(tab_resumo)
        self.text_resumo = QTextEdit()
        self.text_resumo.setReadOnly(True)
        tab_resumo_layout.addWidget(self.text_resumo)
        self.rel_tabs.addTab(tab_resumo, "Resumo Financeiro")
        
        # Tab de movimentos detalhados
        tab_detalhes = QWidget()
        tab_detalhes_layout = QVBoxLayout(tab_detalhes)
        self.tabela_rel_movimentos = QTableWidget()
        self.tabela_rel_movimentos.setColumnCount(6)
        self.tabela_rel_movimentos.setHorizontalHeaderLabels(['ID', 'Data/Hora', 'Tipo', 'Descrição', 'Forma Pgto', 'Valor'])
        self.tabela_rel_movimentos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        tab_detalhes_layout.addWidget(self.tabela_rel_movimentos)
        self.rel_tabs.addTab(tab_detalhes, "Movimentos Detalhados")
        
        # Tab de vendas
        tab_vendas = QWidget()
        tab_vendas_layout = QVBoxLayout(tab_vendas)
        self.tabela_rel_vendas = QTableWidget()
        self.tabela_rel_vendas.setColumnCount(6)
        self.tabela_rel_vendas.setHorizontalHeaderLabels(['ID', 'Data/Hora', 'Cliente', 'Valor Total', 'Desconto', 'Forma Pgto'])
        self.tabela_rel_vendas.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        tab_vendas_layout.addWidget(self.tabela_rel_vendas)
        self.rel_tabs.addTab(tab_vendas, "Vendas Realizadas")
        
        # Adiciona o QTabWidget ao layout principal
        main_layout.addWidget(self.rel_tabs, 1) # O 1 faz com que ele estique
        
        # --- CORREÇÃO: Layout para o botão de exportar ---
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        self.btn_exportar_pdf = QPushButton(" Exportar para PDF")
        self.btn_exportar_pdf.setIcon(IconManager.get_icon('report', color=self.theme_colors.get('text_color', '#000000')))
        
        # O botão começa escondido
        self.btn_exportar_pdf.setVisible(False)
        export_layout.addWidget(self.btn_exportar_pdf)
        
        # Adiciona o layout do botão de exportação ao final
        main_layout.addLayout(export_layout)
        
        # Conectar sinais
        self.cb_periodo.currentIndexChanged.connect(self.periodo_alterado)
    
    def setup_codigo_barras(self):
        # Focar no campo de produto ao iniciar, que agora também é usado para código de barras
        self.cb_produto.setFocus()
    
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
        texto_atual = self.cb_produto.currentText()
        
        self.cb_produto.clear()
        self.cb_produto.addItem("", None) # Item vazio para placeholder
        
        produtos = self.db.listar_produtos_com_fracionamento()
        for produto_row in produtos:
            produto = dict(produto_row)
            
            # Adiciona apenas UMA entrada por produto
            # O itemData agora contém toda a informação do produto
            self.cb_produto.addItem(produto['nome'], produto)

        self.cb_produto.setCurrentText(texto_atual)
        self.cb_produto.setFocus()
    
    def carregar_dados(self):
        """
        Método unificado que recarrega todos os dados da janela de caixa.
        """
        print("DEBUG: CaixaWindow.carregar_dados() foi chamado pelo botão Atualizar.")
        self.carregar_clientes()
        self.carregar_produtos()
        self.verificar_caixa_aberto()
    
    def produto_selecionado(self, index):
        # Limpa a imagem anterior e o texto
        self.lbl_imagem_produto.clear()
        self.lbl_imagem_produto.setText("Selecione um produto...")

        if index <= 0:  # Índice 0 ou -1 (nenhum item selecionado)
            self.spin_preco.setValue(0)
            return
        
        produto = self.cb_produto.itemData(index)
        if not produto:
            return

        # Define o preço de venda padrão
        self.spin_preco.setValue(produto['preco_venda'] if produto.get('preco_venda') else 0)
        
        # ===== INÍCIO DA CORREÇÃO DA IMAGEM =====
        imagem_path = produto.get('imagem_path')
        if imagem_path and os.path.exists(imagem_path):
            pixmap = QPixmap(imagem_path)
            # Escala a imagem para caber no label, mantendo a proporção
            self.lbl_imagem_produto.setPixmap(pixmap.scaled(
                self.lbl_imagem_produto.size(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
        else:
            self.lbl_imagem_produto.setText("Produto sem imagem")
        # ===== FIM DA CORREÇÃO DA IMAGEM =====

        # Verifica se há promoções ativas para este produto
        self.verificar_promocoes(produto)
    
    def obter_estoque_disponivel(self, produto):
        """Retorna o estoque disponível baseado no tipo de venda"""
        if produto.get('tipo_venda') == 'embalagem':
            return produto.get('quantidade', 0)  # Embalagens inteiras
        elif produto.get('tipo_venda') == 'fracao':
            return produto.get('estoque_fracionado', 0)  # Estoque fracionado
        else:
            return produto.get('quantidade', 0)  # Produto normal
    
    def adicionar_item(self):
        index = self.cb_produto.currentIndex()
        if index <= 0:
            QMessageBox.warning(self, "Seleção Inválida", "Selecione um produto válido.")
            return

        produto = self.cb_produto.itemData(index)
        sale_details = None
        
        # Se o produto é fracionado, abre o diálogo de escolha
        if produto['fracionado']:
            dialog = DialogVendaFracionada(produto, self)
            if dialog.exec_() == QDialog.Accepted:
                sale_details = dialog.get_sale_details()
            else:
                return  # Usuário cancelou
        else:
            # Lógica para produto não fracionado
            quantidade = self.spin_quantidade.value()
            
            # APENAS VERIFICA o estoque, não deduz
            if quantidade > produto['quantidade']:
                QMessageBox.warning(self, "Estoque Insuficiente", f"Estoque disponível: {produto['quantidade']} unidades.")
                return

            sale_details = {
                "quantidade": quantidade,
                "preco_unitario": self.spin_preco.value(),
                "is_embalagem": True,
                "produto_nome": produto['nome']
            }

        if not sale_details:
            return

        # ===== CORREÇÃO PRINCIPAL: REMOVIDA A DEDUÇÃO DE ESTOQUE DAQUI =====
        # A dedução de estoque foi movida para o método finalizar_venda.

        # Adiciona o item à lista do carrinho na memória
        item_carrinho = {
            'produto_id': produto['id'],
            'produto_nome': sale_details['produto_nome'],
            'quantidade': sale_details['quantidade'],
            'preco_unitario': sale_details['preco_unitario'],
            'subtotal': sale_details['quantidade'] * sale_details['preco_unitario'],
            'is_embalagem': sale_details['is_embalagem']
        }
        
        self.itens_venda.append(item_carrinho)
        self.atualizar_tabela_itens()
        self.calcular_total()
        
        # Limpar campos para a próxima adição
        self.cb_produto.setCurrentText("") # <-- MUDANÇA AQUI: Limpa apenas o texto, mantendo a imagem.
        self.spin_quantidade.setValue(1)
        self.spin_preco.setValue(0)
        self.cb_produto.setFocus()
    
    def atualizar_tabela_itens(self):
        self.tabela_itens.setRowCount(0)
        
        for i, item in enumerate(self.itens_venda):
            self.tabela_itens.insertRow(i)
            
            # Adicionar dados
            self.tabela_itens.setItem(i, 0, QTableWidgetItem(str(item['produto_id'])))
            self.tabela_itens.setItem(i, 1, QTableWidgetItem(item['produto_nome']))
            
            if item.get('tipo_venda') == 'fracao':
                qtd_display = f"{item['quantidade']} {item.get('unidade_medida', 'un')}"
            else:
                qtd_display = str(item['quantidade'])
            
            self.tabela_itens.setItem(i, 2, QTableWidgetItem(qtd_display))
            self.tabela_itens.setItem(i, 3, QTableWidgetItem(f"R$ {item['preco_unitario']:.2f}"))
            self.tabela_itens.setItem(i, 4, QTableWidgetItem(f"R$ {item['subtotal']:.2f}"))
            
            # Botão remover com ícone
            btn_remover = QPushButton()
            btn_remover.setIcon(IconManager.get_icon('delete', color='#dc3545'))
            btn_remover.setToolTip("Remover item")
            btn_remover.setFlat(True) # Remove bordas para parecer mais integrado
            btn_remover.setCursor(Qt.PointingHandCursor)
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
                self.lbl_imagem_produto.clear()
                # Define o texto inicial novamente
                self.lbl_imagem_produto.setText("Selecione um produto para ver a imagem")
    
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
        
        # Criar labels para os rótulos dos campos de troco
        lbl_valor_recebido_text = QLabel("Valor Recebido:")
        lbl_troco_text = QLabel("Troco:")
        
        # Campos de valor recebido e troco
        spin_valor_recebido = QDoubleSpinBox()
        spin_valor_recebido.setPrefix("R$ ")
        spin_valor_recebido.setMaximum(999999.99)
        spin_valor_recebido.setDecimals(2)
        spin_valor_recebido.setValue(self.total_venda)  # Inicialmente igual ao total
        
        lbl_troco = QLabel("R$ 0,00")
        lbl_troco.setStyleSheet("font-size: 14px; font-weight: bold; color: #FF5722;")
        
        # Adicionar ao layout
        form_layout.addRow(lbl_valor_recebido_text, spin_valor_recebido)
        form_layout.addRow(lbl_troco_text, lbl_troco)
        
        # Inicialmente ocultar campos relacionados ao troco
        lbl_valor_recebido_text.setVisible(False)
        spin_valor_recebido.setVisible(False)
        lbl_troco_text.setVisible(False)
        lbl_troco.setVisible(False)
        
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
            total_final = max(0, total_final)
            lbl_total_final.setText(f"Total a Pagar: R$ {total_final:.2f}")
            
            # Atualizar valor recebido para corresponder ao novo total
            if cb_forma_pagamento.currentText() == "Dinheiro":
                # Apenas atualiza se for menor que o valor atual
                if spin_valor_recebido.value() < total_final:
                    spin_valor_recebido.setValue(total_final)
                calcular_troco()
                
        def calcular_troco():
            desconto = spin_desconto.value()
            total_final = max(0, self.total_venda - desconto)
            valor_recebido = spin_valor_recebido.value()
            troco = max(0, valor_recebido - total_final)
            lbl_troco.setText(f"R$ {troco:.2f}")
            
            # Mudar cor conforme o valor do troco
            if troco > 0:
                lbl_troco.setStyleSheet("font-size: 14px; font-weight: bold; color: #4CAF50;")  # Verde se positivo
            else:
                lbl_troco.setStyleSheet("font-size: 14px; font-weight: bold; color: #F44336;")  # Vermelho se zero
        
        spin_desconto.valueChanged.connect(atualizar_total_final)
        spin_valor_recebido.valueChanged.connect(calcular_troco)
        
        # Atualizar campos visíveis conforme forma de pagamento
        def atualizar_campos_forma_pagamento():
            forma_pgto = cb_forma_pagamento.currentText()
            
            # Configurar visibilidade e estado para forma de pagamento
            if forma_pgto == "Cartão de Crédito":
                spin_parcelas.setEnabled(True)
            else:
                spin_parcelas.setValue(1)
                spin_parcelas.setEnabled(False)
            
            # Mostrar campos de troco apenas para pagamento em dinheiro
            mostrar_campos_troco = (forma_pgto == "Dinheiro")
            lbl_valor_recebido_text.setVisible(mostrar_campos_troco)
            spin_valor_recebido.setVisible(mostrar_campos_troco)
            lbl_troco_text.setVisible(mostrar_campos_troco)
            lbl_troco.setVisible(mostrar_campos_troco)
            
            # Inicializar o valor recebido com o total da venda
            if mostrar_campos_troco:
                desconto = spin_desconto.value()
                total_final = max(0, self.total_venda - desconto)
                spin_valor_recebido.setValue(total_final)
                calcular_troco()
        
        cb_forma_pagamento.currentIndexChanged.connect(atualizar_campos_forma_pagamento)
        atualizar_campos_forma_pagamento()  # Inicializar com os valores corretos
        
        # Processar venda ao confirmar
        def processar_venda():
            cliente_id = self.cb_cliente.currentData()
            desconto = spin_desconto.value()
            forma_pagamento = cb_forma_pagamento.currentText()
            parcelas = spin_parcelas.value()
            observacao = text_observacao.toPlainText()
            total_final = max(0, self.total_venda - desconto)
            
            # Verificar se é pagamento em dinheiro e se o valor recebido é suficiente
            if forma_pagamento == "Dinheiro" and spin_valor_recebido.value() < total_final:
                QMessageBox.warning(dialog, "Valor Insuficiente", 
                                f"O valor recebido (R$ {spin_valor_recebido.value():.2f}) é menor que o total a pagar (R$ {total_final:.2f}).")
                return
            
            # Se tudo estiver certo, registrar a venda e os dados de pagamento
            valor_recebido = spin_valor_recebido.value() if forma_pagamento == "Dinheiro" else total_final
            troco = max(0, valor_recebido - total_final) if forma_pagamento == "Dinheiro" else 0
            
            # Adicionar informações de troco à observação se for pagamento em dinheiro
            if forma_pagamento == "Dinheiro" and troco > 0:
                if observacao:
                    observacao += f"\nValor recebido: R$ {valor_recebido:.2f}. Troco: R$ {troco:.2f}"
                else:
                    observacao = f"Valor recebido: R$ {valor_recebido:.2f}. Troco: R$ {troco:.2f}"
            
            # Registrar venda
            venda_id = self.db.registrar_venda(
            cliente_id, total_final, desconto, forma_pagamento, 
            parcelas, observacao, "Concluída", "Sistema"
            )
            
            if venda_id:
                # ===== INÍCIO DA CORREÇÃO =====
                # AGORA SIM, DEDUZ O ESTOQUE DE CADA ITEM VENDIDO
                for item in self.itens_venda:
                    sucesso_estoque, msg_estoque = self.db.atualizar_estoque_venda(
                        item['produto_id'],
                        item['quantidade'],
                        item['is_embalagem']
                    )
                    if not sucesso_estoque:
                        # Idealmente, aqui deveria haver um tratamento de erro, 
                        # como cancelar a venda ou registrar a falha.
                        QMessageBox.critical(self, "Erro Crítico de Estoque", 
                                            f"Não foi possível atualizar o estoque para o produto {item['produto_nome']}.\n"
                                            f"Erro: {msg_estoque}\n"
                                            "A venda foi registrada, mas o estoque precisa ser ajustado manualmente!")
                # ===== FIM DA CORREÇÃO =====

                # Registrar itens da venda na tabela itens_venda
                for item in self.itens_venda:
                    self.db.registrar_item_venda(
                        venda_id, 
                        item['produto_id'], 
                        item['quantidade'], 
                        item['preco_unitario'], 
                        item['subtotal']
                    )
                
                # Registrar entrada no caixa
                self.db.registrar_movimento_caixa(
                    self.caixa_atual['id'], "Entrada", f"Venda #{venda_id}", 
                    total_final, forma_pagamento, venda_id, "Venda", "Sistema"
                )
                
                # Atualizar saldo
                saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
                self.lbl_saldo.setText(f"Saldo Atual: R$ {saldo_atual:.2f}")
                
                # Mensagem de sucesso com informações do troco para pagamento em dinheiro
                if forma_pagamento == "Dinheiro" and troco > 0:
                    QMessageBox.information(self, "Venda Finalizada", 
                                        f"Venda finalizada com sucesso!\nTotal: R$ {total_final:.2f}\nRecebido: R$ {valor_recebido:.2f}\nTroco: R$ {troco:.2f}")
                else:
                    QMessageBox.information(self, "Sucesso", "Venda finalizada com sucesso!")
                
                # Limpar venda atual
                self.itens_venda = []
                self.atualizar_tabela_itens()
                self.calcular_total()
                self.cb_cliente.setCurrentIndex(0)
                
                # ===== INÍCIO DA MUDANÇA =====
                self.lbl_imagem_produto.clear()
                self.lbl_imagem_produto.setText("Selecione um produto para ver a imagem")
                # ===== FIM DA MUDANÇA =====
                
                # Recarregar movimentos
                self.carregar_movimentos()
                
                dialog.accept()
            else:
                QMessageBox.critical(self, "Erro", "Erro ao registrar venda")
        
        btn_confirmar.clicked.connect(processar_venda)
        
        dialog.exec_()
    
    def reduzir_estoque_itens(self, venda_id):
        """Reduz o estoque dos itens vendidos considerando fracionamento"""
        for item in self.itens_venda:
            produto_id = item['produto_id']
            quantidade = item['quantidade']
            tipo_venda = item.get('tipo_venda', 'normal')
            
            if tipo_venda == 'embalagem':
                # Reduzir embalagens inteiras
                self.db.reduzir_estoque_embalagem(produto_id, quantidade)
            elif tipo_venda == 'fracao':
                # Reduzir estoque fracionado
                self.db.reduzir_estoque_fracionado(produto_id, quantidade)
            else:
                # Produto normal
                self.db.reduzir_estoque_produto(produto_id, quantidade)
            
            # Registrar item da venda
            preco_unitario = item['preco_unitario']
            subtotal = item['subtotal']
            self.db.adicionar_item_venda(venda_id, produto_id, quantidade, preco_unitario, subtotal)
    
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
            
            # Usar o nome do usuário logado em vez de "Sistema"
            usuario_logado = self.usuario_atual['nome'] if hasattr(self, 'usuario_atual') else "Sistema"
            
            caixa_id = self.db.abrir_caixa(saldo_inicial, usuario_logado, observacao)
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

        # CORREÇÃO: Definir a função realizar_backup ANTES de usar
        def realizar_backup():
            """
            Realiza um backup completo do banco de dados do sistema.
            Retorna True se o backup foi bem-sucedido, False caso contrário.
            """
            import os
            import datetime
            import shutil
            import sqlite3

            try:
                # Configurações do backup
                data_hora = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                nome_arquivo = f"backup_sistema_{data_hora}.db"

                # Diretório para salvar os backups na unidade C:
                diretorio_backup = os.path.join("C:\\backups_sistema")

                # Criar o diretório de backups se não existir
                if not os.path.exists(diretorio_backup):
                    os.makedirs(diretorio_backup)

                caminho_backup = os.path.join(diretorio_backup, nome_arquivo)

                # Caminho do banco de dados atual
                caminho_db = self.db.db_path  # Ajuste conforme sua implementação

                # Método 1: Cópia direta do arquivo (se SQLite)
                if hasattr(self.db, 'db_path'):
                    shutil.copy2(caminho_db, caminho_backup)
                    print(f"Backup realizado com sucesso em: {caminho_backup}")
                    return True

                # Método 2: Backup via SQL (alternativa para outros SGBDs)
                else:
                    conexao = sqlite3.connect(caminho_backup)

                    with sqlite3.connect(caminho_db) as con:
                        con.backup(conexao)

                    conexao.close()
                    print(f"Backup realizado com sucesso em: {caminho_backup}")
                    return True

            except Exception as e:
                print(f"Erro ao realizar backup: {str(e)}")
                return False

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
            if not self.caixa_atual:
                QMessageBox.critical(self, "Erro", "Nenhum caixa está aberto.")
                return

            saldo_informado = spin_saldo_final.value()
            diferenca = saldo_informado - saldo_atual
            observacao = text_obs_fechamento.toPlainText()
            
            # Usar o nome do usuário logado em vez de "Sistema"
            usuario_logado = self.usuario_atual['nome'] if hasattr(self, 'usuario_atual') else "Sistema"
            
            confirma = QMessageBox.question(dialog, "Confirmar Fechamento", 
                                            f"Deseja realmente fechar o caixa?\nDiferença: R$ {diferenca:.2f}",
                                            QMessageBox.Yes | QMessageBox.No)
            
            if confirma == QMessageBox.Yes:
                sucesso = self.db.fechar_caixa(
                    self.caixa_atual['id'], saldo_informado, diferenca, 
                    usuario_logado, observacao
                )
                
                if sucesso:
                    # Realizar backup dos dados após o fechamento do caixa
                    backup_sucesso = realizar_backup()  # Agora funciona corretamente
                    
                    dialog.accept()
                    self.verificar_caixa_aberto()
                    if self.caixa_atual:  # Verificar novamente antes de chamar o relatório
                        self.gerar_relatorio_fechamento(self.caixa_atual['id'])
                    
                    msg = "Caixa fechado com sucesso!"
                    if backup_sucesso:
                        msg += "\nBackup dos dados realizado com sucesso."
                    else:
                        msg += "\nAtenção: Não foi possível realizar o backup dos dados."
                    
                    QMessageBox.information(self, "Sucesso", msg)
                else:
                    QMessageBox.critical(self, "Erro", "Erro ao fechar o caixa")

        btn_confirmar.clicked.connect(confirmar_fechamento)
        dialog.exec_()

    # ===================================================================== #
    #       FUNÇÕES AUXILIARES DE RELATÓRIO (COPIADAS DE ESTOQUE)         #
    # ===================================================================== #

    def _criar_kpi_boxes(self, kpi_data, doc_width):
        """Cria uma tabela formatada como caixas de KPI."""
        styles = getSampleStyleSheet()
        style_label = ParagraphStyle('kpi_label', parent=styles['Normal'], fontSize=9, textColor=colors.dimgrey, alignment=TA_LEFT)
        style_value = ParagraphStyle('kpi_value', parent=styles['Normal'], fontSize=16, fontName='Helvetica-Bold', alignment=TA_LEFT)

        data = []
        for kpi in kpi_data:
            p_label = Paragraph(kpi['label'], style_label)
            
            kpi_value = kpi['value']
            if isinstance(kpi_value, Paragraph):
                p_value = kpi_value
                p_value.style.alignment = TA_LEFT 
            else:
                p_value = Paragraph(str(kpi_value), style_value)
            
            data.append([p_label, p_value])
        
        tabela_data = [list(i) for i in zip(*data)]

        kpi_table = Table(tabela_data, colWidths=[doc_width / len(kpi_data)] * len(kpi_data))
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#F2F2F2")),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor("#E0E0E0")),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        return kpi_table

    def _gerar_pdf_com_template(self, file_path, report_title, elementos):
        """Gera um PDF com um cabeçalho e rodapé profissional e estruturado."""
        try:
            def header_footer(canvas, doc):
                canvas.saveState()
                if os.path.exists(self.logo_path):
                    canvas.drawImage(self.logo_path, doc.leftMargin, doc.height + doc.topMargin,
                                     width=120, height=45, preserveAspectRatio=True, mask='auto')
                
                canvas.setFont('Helvetica', 9)
                canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin + 20, self.company_info['nome'])
                canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin + 5, self.company_info['endereco'])
                canvas.drawRightString(doc.width + doc.leftMargin, doc.height + doc.topMargin - 10, self.company_info['contato'])

                canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
                canvas.line(doc.leftMargin, doc.height + doc.topMargin - 20, doc.width + doc.leftMargin, doc.height + doc.topMargin - 20)
                
                canvas.setFont('Helvetica-Oblique', 8)
                canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 20, f"Página {canvas.getPageNumber()} | {report_title}")
                canvas.restoreState()

            doc = SimpleDocTemplate(file_path, pagesize=A4, topMargin=3*cm, bottomMargin=1.5*cm, leftMargin=2*cm, rightMargin=2*cm)
            doc.build(elementos, onFirstPage=header_footer, onLaterPages=header_footer)
            
            QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso em:\n{file_path}")

        except FileNotFoundError:
            QMessageBox.critical(self, "Erro de Logo", f"Arquivo de logo não encontrado em:\n{self.logo_path}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Gerar PDF", f"Ocorreu um erro inesperado: {str(e)}")

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
        
        # Data de Nascimento
        edit_data_nascimento = QDateEdit()
        edit_data_nascimento.setCalendarPopup(True)
        edit_data_nascimento.setDate(QDate.currentDate().addYears(-18))  # Data padrão: 18 anos atrás
        edit_data_nascimento.setDisplayFormat("dd/MM/yyyy")
        form_layout.addRow("Data de Nascimento:", edit_data_nascimento)
        
        # Telefone
        edit_telefone = QLineEdit()
        form_layout.addRow("Telefone:", edit_telefone)
        
        # Email
        edit_email = QLineEdit()
        form_layout.addRow("Email:", edit_email)
        
        # Endereço
        edit_endereco = QLineEdit()
        form_layout.addRow("Endereço:", edit_endereco)
        
        layout.addLayout(form_layout)
        
        btn_salvar = QPushButton("Salvar")
        layout.addWidget(btn_salvar)
        
        def salvar_cliente():
            nome = edit_nome.text().strip()
            data_nascimento = edit_data_nascimento.date().toString("yyyy-MM-dd")
            telefone = edit_telefone.text().strip()
            email = edit_email.text().strip()
            endereco = edit_endereco.text().strip()
            
            if not nome:
                QMessageBox.warning(dialog, "Campos Obrigatórios", "O campo Nome é obrigatório")
                return
            
            # Registrar cliente com todos os parâmetros necessários
            cliente_id = self.db.adicionar_cliente(nome, data_nascimento, telefone, email, endereco)
            
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
        # PASSO 1: Coletar datas e buscar os dados
        data_inicio = self.dt_rel_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.dt_rel_fim.date().toString("yyyy-MM-dd")
        
        dados = self.db.gerar_relatorio_periodo(data_inicio, data_fim)
        
        # Se não houver dados, limpa a tela e esconde o botão de exportar
        if not dados:
            QMessageBox.information(self, "Sem Dados", "Não foram encontrados dados para o período selecionado.")
            self.btn_exportar_pdf.setVisible(False)
            self.text_resumo.clear()
            self.tabela_rel_movimentos.setRowCount(0)
            self.tabela_rel_vendas.setRowCount(0)
            return
            
        # PASSO 2: Armazenar os dados para uso na exportação
        self.dados_relatorio_atual = dados
        
        # PASSO 3: Conectar o botão de exportar
        try:
            self.btn_exportar_pdf.clicked.disconnect()
        except TypeError:
            pass  # Ignora erro se não houver conexão
        
        self.btn_exportar_pdf.clicked.connect(
            lambda: self.abrir_dialogo_exportacao(data_inicio, data_fim, self.dados_relatorio_atual)
        )
        
        # ================================================================= #
        #       PASSO 4: PREENCHER A INTERFACE GRÁFICA (UI)                 #
        # ================================================================= #

        # --- 4.1: Preencher a NOVA Aba de Resumo Visual ---
        self.preencher_resumo_visual(dados, data_inicio, data_fim)

        # --- 4.2: Preencher a Tabela de Movimentos Detalhados (CORRIGIDO) ---
        self.tabela_rel_movimentos.setRowCount(0)
        movimentos = dados.get('movimentos', [])
        for i, movimento in enumerate(movimentos):
            self.tabela_rel_movimentos.insertRow(i)
            
            tipo = movimento['tipo']
            valor = movimento['valor']
            
            # Define a cor baseada no tipo de movimento
            cor_valor = QColor(self.theme_colors.get('accent_color', '#28a745')) if tipo == "Entrada" else QColor("#dc3545")
            
            self.tabela_rel_movimentos.setItem(i, 0, QTableWidgetItem(str(movimento['id'])))
            self.tabela_rel_movimentos.setItem(i, 1, QTableWidgetItem(movimento['data_hora']))
            
            tipo_item = QTableWidgetItem(tipo)
            tipo_item.setForeground(cor_valor)
            self.tabela_rel_movimentos.setItem(i, 2, tipo_item)
            
            self.tabela_rel_movimentos.setItem(i, 3, QTableWidgetItem(movimento['descricao']))
            self.tabela_rel_movimentos.setItem(i, 4, QTableWidgetItem(movimento['forma_pagamento']))
            
            valor_item = QTableWidgetItem(f"R$ {valor:.2f}")
            valor_item.setForeground(cor_valor)
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_rel_movimentos.setItem(i, 5, valor_item)

        # --- 4.3: Preencher a Tabela de Vendas Realizadas (CORRIGIDO) ---
        self.tabela_rel_vendas.setRowCount(0)
        vendas = dados.get('vendas', [])
        for i, venda in enumerate(vendas):
            self.tabela_rel_vendas.insertRow(i)
            
            self.tabela_rel_vendas.setItem(i, 0, QTableWidgetItem(str(venda['id'])))
            self.tabela_rel_vendas.setItem(i, 1, QTableWidgetItem(venda['data_hora']))
            self.tabela_rel_vendas.setItem(i, 2, QTableWidgetItem(venda['cliente']))
            
            valor_total_item = QTableWidgetItem(f"R$ {venda['valor_total']:.2f}")
            valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_rel_vendas.setItem(i, 3, valor_total_item)

            desconto_item = QTableWidgetItem(f"R$ {venda['desconto']:.2f}")
            desconto_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_rel_vendas.setItem(i, 4, desconto_item)

            self.tabela_rel_vendas.setItem(i, 5, QTableWidgetItem(venda['forma_pagamento']))
            
        # PASSO 5: Tornar o botão de exportar visível
        self.btn_exportar_pdf.setVisible(True)

    def preencher_resumo_visual(self, dados, data_inicio, data_fim):
        """Gera um HTML elaborado para a aba de resumo, herdando as cores do tema."""
        
        # Herda as cores do tema da MainWindow
        theme = self.theme_colors
        cor_fundo_body = theme.get('bg_color', '#ffffff')
        cor_fundo_card = theme.get('surface_color', '#f2f2f7')
        cor_borda = theme.get('border_color', '#e1e8f3')
        cor_titulo_principal = theme.get('text_color', '#34495e')
        cor_subtitulo = theme.get('text_secondary', '#7f8c8d')
        cor_titulo_kpi = theme.get('text_secondary', '#6c757d')
        cor_valor_kpi = theme.get('text_color', '#2c3e50')
        cor_entrada = "#28a745"  # Verde para consistência
        cor_saida = "#dc3545"    # Vermelho para consistência
        cor_saldo = theme.get('accent_color', '#17a2b8')
        
        # --- Montagem do HTML ---
        html = f"""
        <html>
        <head>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    background-color: {cor_fundo_body}; 
                    color: {cor_titulo_principal};
                    margin: 0;
                    padding: 0;
                }}
                .container {{ padding: 25px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h2 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 5px; color: {cor_subtitulo}; font-size: 14px; }}
                
                .kpi-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; 
                    margin-bottom: 35px; 
                }}
                .kpi-card {{ 
                    background-color: {cor_fundo_card}; 
                    border: 1px solid {cor_borda}; 
                    border-left: 5px solid {cor_saldo};
                    border-radius: 8px; 
                    padding: 20px; 
                    text-align: left; 
                }}
                .kpi-card .label {{ 
                    font-size: 12px; 
                    color: {cor_titulo_kpi}; 
                    text-transform: uppercase; 
                    margin-bottom: 8px; 
                    font-weight: bold;
                }}
                .kpi-card .value {{ 
                    font-size: 28px; 
                    font-weight: bold; 
                    color: {cor_valor_kpi}; 
                }}
                
                .section-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                }}
                .section h3 {{ 
                    color: {cor_titulo_principal}; 
                    border-bottom: 2px solid {cor_borda}; 
                    padding-bottom: 8px; 
                    margin-top: 0;
                }}
                
                ol, ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 10px; color: {cor_subtitulo}; }}
                li b {{ color: {cor_titulo_principal}; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Resumo Financeiro</h2>
                    <p>Período de {data_inicio} a {data_fim}</p>
                </div>

                <div class="kpi-grid">
                    <div class="kpi-card" style="border-left-color: {cor_saldo};">
                        <div class="label">Faturamento (Vendas)</div>
                        <div class="value">R$ {dados.get('valor_vendas', 0):.2f}</div>
                    </div>
                    <div class="kpi-card" style="border-left-color: {cor_entrada};">
                        <div class="label">Total de Entradas</div>
                        <div class="value" style="color: {cor_entrada};">R$ {dados.get('total_entradas', 0):.2f}</div>
                    </div>
                    <div class="kpi-card" style="border-left-color: {cor_saida};">
                        <div class="label">Total de Saídas</div>
                        <div class="value" style="color: {cor_saida};">R$ {dados.get('total_saidas', 0):.2f}</div>
                    </div>
                </div>

                <div class="section-grid">
                    <div class="section">
                        <h3>Top 5 Produtos Vendidos</h3>
                        <ol>
        """
        
        top_produtos = dados.get('produtos_mais_vendidos', [])[:5]
        if not top_produtos:
            html += "<li>Nenhum produto vendido no período.</li>"
        for produto in top_produtos:
            html += f"<li><b>{produto['nome']}</b>: {produto['quantidade']} un. (R$ {produto['valor_total']:.2f})</li>"
        
        html += """
                        </ol>
                    </div>

                    <div class="section">
                        <h3>Vendas por Pagamento</h3>
                        <ul>
        """
        
        pagamentos = dados.get('pagamentos', {})
        if not pagamentos:
            html += "<li>Nenhuma venda registrada no período.</li>"
        for forma, valor in pagamentos.items():
            html += f"<li><b>{forma}:</b> R$ {valor:.2f}</li>"
            
        html += """
                        </ul>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        self.text_resumo.setHtml(html)

    def abrir_dialogo_exportacao(self, data_inicio, data_fim, dados):
        """
        Abre o QFileDialog para o usuário escolher onde salvar o PDF.
        """
        if not dados:
            QMessageBox.warning(self, "Erro", "Não há dados de relatório para exportar.")
            return

        nome_arquivo = f"Relatorio_Financeiro_{data_inicio}_a_{data_fim}.pdf"
        caminho_arquivo, _ = QFileDialog.getSaveFileName(
            self, "Salvar Relatório Financeiro",
            os.path.join(os.path.expanduser("~"), "Downloads", nome_arquivo),
            "Arquivos PDF (*.pdf)"
        )

        if caminho_arquivo:
            # Chama a função que realmente cria o PDF
            self.exportar_relatorio_pdf(data_inicio, data_fim, dados, caminho_arquivo)
            
    def exportar_relatorio_pdf(self, data_inicio, data_fim, dados, file_path):
        """
        Gera o conteúdo específico para o relatório financeiro e usa o template padrão.
        """
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

        styles = getSampleStyleSheet()
        elementos = []
        
        # --- Título ---
        elementos.append(Paragraph("Relatório Financeiro Detalhado", styles['h1']))
        elementos.append(Paragraph(f"Período de Análise: {data_inicio} a {data_fim}", styles['Normal']))
        elementos.append(Spacer(1, 0.8 * cm))
        
        # --- KPIs Financeiros ---
        left_margin = 2*cm
        right_margin = 2*cm
        doc_width = A4[0] - left_margin - right_margin

        kpi_data = [
            {'label': 'FATURAMENTO BRUTO', 'value': f"R$ {dados.get('valor_vendas', 0):.2f}"},
            {'label': 'TOTAL ENTRADAS', 'value': f"<font color='green'>R$ {dados.get('total_entradas', 0):.2f}</font>"},
            {'label': 'TOTAL SAÍDAS', 'value': f"<font color='red'>R$ {dados.get('total_saidas', 0):.2f}</font>"},
            {'label': 'SALDO DO PERÍODO', 'value': f"R$ {dados.get('saldo_periodo', 0):.2f}"},
            {'label': 'TICKET MÉDIO', 'value': f"R$ {dados.get('valor_medio_venda', 0):.2f}"},
        ]
        elementos.append(self._criar_kpi_boxes(kpi_data, doc_width))
        elementos.append(Spacer(1, 1*cm))

        # --- Tabela de Vendas ---
        elementos.append(Paragraph("Vendas Realizadas no Período", styles['h2']))
        vendas_data = [['ID', 'Data/Hora', 'Cliente', 'Valor', 'Desconto', 'Pagamento']]
        for v in dados.get('vendas', []):
            vendas_data.append([
                v['id'], v['data_hora'], Paragraph(v['cliente'], styles['Normal']),
                f"R$ {v['valor_total']:.2f}", f"R$ {v['desconto']:.2f}", v['forma_pagamento']
            ])
            
        tabela_vendas = Table(vendas_data, colWidths=[1.5*cm, 3.5*cm, 4.5*cm, 2.5*cm, 2.5*cm, 3*cm], repeatRows=1)
        style_vendas = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ])
        tabela_vendas.setStyle(style_vendas)
        elementos.append(tabela_vendas)
        elementos.append(Spacer(1, 1*cm))
        
        # --- Tabela de Movimentos do Caixa ---
        elementos.append(Paragraph("Movimentações Manuais do Caixa", styles['h2']))
        mov_data = [['ID', 'Data/Hora', 'Tipo', 'Descrição', 'Valor']]
        for m in dados.get('movimentos', []):
            # Ignorar movimentos que são de Vendas, pois já estão na tabela acima
            if m.get('tipo_referencia') == 'Venda':
                continue
            mov_data.append([
                m['id'], m['data_hora'], m['tipo'], Paragraph(m['descricao'], styles['Normal']), f"R$ {m['valor']:.2f}"
            ])
            
        tabela_mov = Table(mov_data, colWidths=[1.5*cm, 3.5*cm, 2*cm, 7.5*cm, 3*cm], repeatRows=1)
        style_mov = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#C0504D")), # Vermelho corporativo
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ])
        # Colorir linhas de entrada/saída
        for i, row in enumerate(mov_data):
            if i == 0: continue
            if row[2] == 'Entrada': style_mov.add('TEXTCOLOR', (0, i), (-1, i), colors.green)
            elif row[2] == 'Saída': style_mov.add('TEXTCOLOR', (0, i), (-1, i), colors.red)
        tabela_mov.setStyle(style_mov)
        elementos.append(tabela_mov)

        # Chama a função de template para gerar o PDF
        self._gerar_pdf_com_template(file_path, "Relatório Financeiro", elementos)

class DialogOpcoesFracionado(QDialog):
    def __init__(self, produto, parent=None):
        super().__init__(parent)
        self.produto = produto
        self.opcao_selecionada = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Opções de Venda")
        self.setFixedSize(400, 250)
        
        layout = QVBoxLayout(self)
        
        # Título
        titulo = QLabel(f"Como deseja vender: {self.produto['nome']}?")
        titulo.setStyleSheet("font-weight: bold; font-size: 14px;")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Opções
        opcoes_group = QGroupBox("Selecione uma opção:")
        opcoes_layout = QVBoxLayout(opcoes_group)
        
        # Botão para embalagem
        if self.produto['quantidade'] > 0:
            btn_embalagem = QPushButton(
                f"Embalagem Completa\n"
                f"Preço: R$ {self.produto['preco_venda']:.2f}\n"
                f"Estoque: {self.produto['quantidade']} embalagem(ns)\n"
                f"Contém: {self.produto['qtd_por_embalagem']} {self.produto['unidade_medida']}"
            )
            btn_embalagem.setMinimumHeight(60)
            btn_embalagem.clicked.connect(lambda: self.selecionar_opcao('embalagem'))
            opcoes_layout.addWidget(btn_embalagem)
        
        # Botão para fração
        if self.produto['estoque_fracionado'] > 0:
            btn_fracao = QPushButton(
                f"Venda Fracionada\n"
                f"Preço: R$ {self.produto['preco_unitario_fracao']:.2f} por {self.produto['unidade_medida']}\n"
                f"Estoque: {self.produto['estoque_fracionado']} {self.produto['unidade_medida']}"
            )
            btn_fracao.setMinimumHeight(60)
            btn_fracao.clicked.connect(lambda: self.selecionar_opcao('fracao'))
            opcoes_layout.addWidget(btn_fracao)
        
        layout.addWidget(opcoes_group)
        
        # Botão cancelar
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.clicked.connect(self.reject)
        layout.addWidget(btn_cancelar)
    
    def selecionar_opcao(self, opcao):
        self.opcao_selecionada = opcao
        self.accept()
    
    def get_opcao_selecionada(self):
        return self.opcao_selecionada

class DialogVendaFracionada(QDialog):
    def __init__(self, produto, parent=None):
        super().__init__(parent)
        self.produto = produto
        self.sale_details = None

        self.setWindowTitle("Opção de Venda")
        self.setFixedWidth(400)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        titulo = QLabel(f"<b>{produto['nome']}</b>")
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        # Opções de Venda
        self.radio_embalagem = QRadioButton("Vender Embalagem Inteira")
        self.radio_unidade = QRadioButton("Vender Unidade Avulsa")
        self.radio_embalagem.toggled.connect(self.update_info)
        
        btn_group_layout = QHBoxLayout()
        btn_group_layout.addWidget(self.radio_embalagem)
        btn_group_layout.addWidget(self.radio_unidade)
        form_layout.addRow("Tipo de Venda:", btn_group_layout)

        # Informações
        self.lbl_info_preco = QLabel()
        self.lbl_info_estoque = QLabel()
        form_layout.addRow("Preço Unitário:", self.lbl_info_preco)
        form_layout.addRow("Estoque Disponível:", self.lbl_info_estoque)

        # Quantidade - CORRIGIDO PARA QDoubleSpinBox
        self.spin_quantidade = QDoubleSpinBox()
        self.spin_quantidade.setMinimum(0.001) # Mínimo para venda fracionada
        self.spin_quantidade.setDecimals(3) # Para kg (ex: 0.250)
        self.spin_quantidade.setSingleStep(0.1)
        form_layout.addRow("Quantidade:", self.spin_quantidade)

        layout.addLayout(form_layout)

        # Botões de confirmação
        button_box = QHBoxLayout()
        self.confirmar_btn = QPushButton("Confirmar")
        self.confirmar_btn.clicked.connect(self.confirmar)
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        button_box.addStretch()
        button_box.addWidget(cancelar_btn)
        button_box.addWidget(self.confirmar_btn)
        layout.addLayout(button_box)

        self.radio_embalagem.setChecked(True)

    def update_info(self):
        if self.radio_embalagem.isChecked():
            self.spin_quantidade.setDecimals(0) # Embalagem é inteira
            self.spin_quantidade.setMinimum(1)
            self.spin_quantidade.setValue(1)
            self.lbl_info_preco.setText(f"R$ {self.produto['preco_venda']:.2f}")
            self.lbl_info_estoque.setText(f"{self.produto['quantidade']} embalagens")
            self.spin_quantidade.setMaximum(self.produto['quantidade'])
        else:
            self.spin_quantidade.setDecimals(3) # Fração pode ter decimais
            self.spin_quantidade.setMinimum(0.001)
            self.spin_quantidade.setValue(1)
            self.lbl_info_preco.setText(f"R$ {self.produto['preco_unitario_fracao']:.2f}")
            self.lbl_info_estoque.setText(f"{self.produto['estoque_fracionado']} {self.produto['unidade_medida']}")
            # estoque_fracionado é float, setMaximum aceita float em QDoubleSpinBox
            self.spin_quantidade.setMaximum(self.produto['estoque_fracionado'])

    def confirmar(self):
        quantidade = self.spin_quantidade.value()
        if quantidade > self.spin_quantidade.maximum() or quantidade == 0:
            QMessageBox.warning(self, "Estoque Insuficiente", "A quantidade solicitada excede o estoque disponível.")
            return

        is_embalagem = self.radio_embalagem.isChecked()
        preco_unitario = self.produto['preco_venda'] if is_embalagem else self.produto['preco_unitario_fracao']
        unidade = "emb." if is_embalagem else self.produto['unidade_medida']
        
        self.sale_details = {
            "quantidade": quantidade,
            "preco_unitario": preco_unitario,
            "is_embalagem": is_embalagem,
            "produto_nome": f"{self.produto['nome']} ({unidade})"
        }
        self.accept()

    def get_sale_details(self):
        return self.sale_details