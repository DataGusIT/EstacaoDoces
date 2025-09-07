from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel, QLineEdit,
                            QPushButton, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
                            QMessageBox, QDialog, QFormLayout, QTextEdit, QDoubleSpinBox,
                            QSpinBox, QHeaderView, QCheckBox, QGroupBox, QGridLayout, QFrame,
                            QSplitter, QApplication,  QFileDialog, QMessageBox, QHBoxLayout, QLayout, QRadioButton, QCompleter)
from PyQt5.QtCore import pyqtSignal, Qt, QDate, QDateTime, QMarginsF 
from PyQt5.QtGui import QIcon, QColor, QFont, QTextDocument, QPageSize, QPageLayout, QIcon, QPixmap
from PyQt5.QtPrintSupport import QPrinter
import os
from ui.icon_manager import IconManager
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from collections import defaultdict
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

import datetime

# =================================================================================
#  1. CLASSES BASE PARA JANELAS DE DIÁLOGO TEMÁTICAS (ADICIONADAS AQUI)
# =================================================================================

class ThemedDialog(QDialog):
    """Classe base para todos os diálogos com cabeçalho personalizado."""
    def __init__(self, parent, title, theme_colors):
        super().__init__(parent)
        self.theme_colors = theme_colors
        self.drag_position = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)

        self.container = QFrame(self)
        self.container.setObjectName("mainContainer")

        base_layout = QVBoxLayout(self.container)
        base_layout.setContentsMargins(0, 0, 0, 0)
        base_layout.setSpacing(0)
        
        self.header = self._create_header(title)
        base_layout.addWidget(self.header)

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(15, 10, 15, 15)
        self.content_layout.setSpacing(10)
        base_layout.addLayout(self.content_layout)

        final_layout = QVBoxLayout(self)
        final_layout.setContentsMargins(0,0,0,0)
        final_layout.addWidget(self.container)
        self.apply_base_styles()

    def _create_header(self, title):
        header_widget = QFrame()
        header_widget.setObjectName("header")
        header_widget.setFixedHeight(45)
        layout = QHBoxLayout(header_widget)
        layout.setContentsMargins(15, 0, 5, 0)
        
        title_label = QLabel(title)
        title_label.setObjectName("headerTitleLabel")
        
        # Adiciona um botão de ajuda/info opcional (pode ser usado no futuro)
        self.help_button = QPushButton()
        self.help_button.setObjectName("controlButton")
        self.help_button.setIcon(IconManager.get_icon('ajuda', color=self.theme_colors.get('text_secondary')))
        self.help_button.setFixedSize(30, 30)
        self.help_button.setVisible(False) # Escondido por padrão

        close_button = QPushButton()
        close_button.setObjectName("controlButton")
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors.get('text_secondary')))
        close_button.setFixedSize(30, 30)
        close_button.clicked.connect(self.reject)
        
        layout.addWidget(title_label)
        layout.addStretch()
        layout.addWidget(self.help_button)
        layout.addWidget(close_button)
        return header_widget

    def apply_base_styles(self):
        theme = self.theme_colors
        style = f"""
            #mainContainer {{ background-color: {theme.get('bg_color')}; border-radius: 8px; border: 1px solid {theme.get('border_color')}; }}
            #header {{ background-color: {theme.get('surface_color')}; border-top-left-radius: 8px; border-top-right-radius: 8px; border-bottom: 1px solid {theme.get('border_color')}; }}
            #headerTitleLabel {{ color: {theme.get('text_color')}; font-weight: bold; font-size: 11pt; }}
            #controlButton {{ background-color: transparent; border: none; border-radius: 4px; }}
            #controlButton:hover {{ background-color: {theme.get('button_hover')}; }}
        """
        self.container.setStyleSheet(style)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.header.underMouse(): self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

class AlertDialog(ThemedDialog):
    """Substituto para QMessageBox, com o cabeçalho temático."""
    def __init__(self, parent, title, message, alert_type='info', buttons=QMessageBox.Ok, theme_colors=None):
        super().__init__(parent, title, theme_colors)
        
        type_info = {
            'success':  {'icon': 'check', 'color': '#28a745'},
            'warning':  {'icon': 'estoque_baixo', 'color': '#ffc107'},
            'error':    {'icon': 'delete', 'color': '#dc3545'},
            'question': {'icon': 'question', 'color': '#17a2b8'},
            'info':     {'icon': 'sobre', 'color': self.theme_colors.get('accent_color', '#007AFF')},
        }.get(alert_type, {'icon': 'sobre', 'color': '#007AFF'})
        self.accent_color = type_info['color']
        
        self._setup_ui(message, buttons, type_info)
        self.apply_alert_styles()

    def _setup_ui(self, message, buttons, type_info):
        self.setMinimumWidth(400)
        
        body_layout = QHBoxLayout(); body_layout.setSpacing(15)
        icon_label = QLabel()
        icon_label.setPixmap(IconManager.get_icon(type_info['icon'], color=self.accent_color).pixmap(32, 32))
        message_label = QLabel(message); message_label.setWordWrap(True)
        body_layout.addWidget(icon_label, 0, Qt.AlignTop)
        body_layout.addWidget(message_label, 1)

        button_layout = QHBoxLayout(); button_layout.addStretch()
        if buttons & QMessageBox.Yes: button_layout.addWidget(self._create_button("Sim", lambda: self.done(QMessageBox.Yes), is_primary=True))
        if buttons & QMessageBox.Ok: button_layout.addWidget(self._create_button("OK", self.accept, is_primary=True))
        if buttons & QMessageBox.No: button_layout.addWidget(self._create_button("Não", self.reject))
        if buttons & QMessageBox.Cancel: button_layout.addWidget(self._create_button("Cancelar", self.reject))
        
        self.content_layout.addLayout(body_layout)
        self.content_layout.addLayout(button_layout)

    def _create_button(self, text, on_click, is_primary=False):
        btn = QPushButton(text); btn.clicked.connect(on_click)
        btn.setObjectName("primaryButton" if is_primary else "secondaryButton")
        return btn
        
    def apply_alert_styles(self):
        colors = self.theme_colors
        style = f"""
            QLabel {{ color: {colors.get('text_secondary')}; font-size: 11pt; }}
            QPushButton {{ font-weight: bold; padding: 8px 20px; border-radius: 6px; min-width: 80px;}}
            #primaryButton {{ background-color: {self.accent_color}; color: white; border: none; }}
            #secondaryButton {{ background-color: transparent; color: {colors.get('text_color')}; border: 1px solid {colors.get('border_color')}; }}
            #secondaryButton:hover {{ background-color: {colors.get('button_hover')}; }}
        """
        self.setStyleSheet(self.styleSheet() + style)

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
    venda_finalizada = pyqtSignal()

    movimento_manual_registrado = pyqtSignal()
    dados_clientes_alterados = pyqtSignal()  # <-- ADICIONE APENAS ESTA LINHA

    def __init__(self, db, theme_colors, settings): # Adicione 'settings'
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.settings = settings # Armazene
        self.caixa_atual = None
        self.itens_venda = []
        self.total_venda = 0.0
        self.dados_relatorio_atual = None

        self.logo_path = "assets/img/Logo2.png" # Caminho fixo do logo
        self.company_info = {
            "nome": "Estação Doces",
            "endereco": "Rua do Comércio, 123 - Centro",
            "contato": "Telefone: (11) 99999-8888 | Email: contato@estacaodoces.com"
        }
        self.initUI()
        self.set_theme(self.theme_colors) # Aplica o tema
        self.verificar_caixa_aberto()
        self.carregar_clientes()
        self.carregar_produtos()
        self.setup_codigo_barras()

    def _update_icons(self):
        text_color = self.theme_colors.get('text_color', '#000')
        success_color = "#28a745"
        danger_color = "#dc3545"
        warning_color = "#ffc107"

        # Abas Principais
        self.tabs.setTabIcon(0, IconManager.get_icon('caixa', color=text_color))
        self.tabs.setTabIcon(1, IconManager.get_icon('relatorio', color=text_color))
        self.tabs.setTabIcon(2, IconManager.get_icon('report', color=text_color))

        # Status do Caixa
        self.btn_abrir_caixa.setIcon(IconManager.get_icon('unlock', color=text_color))
        self.btn_fechar_caixa.setIcon(IconManager.get_icon('lock', color=text_color))
        
        # PDV
        self.btn_add_cliente.setIcon(IconManager.get_icon('add', color=text_color))
        self.btn_adicionar_item.setIcon(IconManager.get_icon('add', color=text_color))
        self.btn_limpar.setIcon(IconManager.get_icon('clear', color='black')) # Ícone preto no botão amarelo
        self.btn_finalizar.setIcon(IconManager.get_icon('check', color='white'))

        # Movimentações
        self.btn_nova_entrada.setIcon(IconManager.get_icon('add', color='white')) # Ícone branco no botão verde
        self.btn_nova_saida.setIcon(IconManager.get_icon('send', color='white')) # Ícone branco no botão vermelho
        self.btn_filtrar.setIcon(IconManager.get_icon('filter', color=text_color))

        # Relatórios
        self.btn_gerar_relatorio.setIcon(IconManager.get_icon('report', color=text_color))
        if hasattr(self, 'btn_exportar_pdf'):
            self.btn_exportar_pdf.setIcon(IconManager.get_icon('report', color=text_color))

        # ================================================================= #
    #       CORREÇÃO PRINCIPAL: MÉTODO set_theme REFEITO                #
    # ================================================================= #
    def set_theme(self, theme_colors):
        """Aplica as cores do tema a todos os componentes da janela."""
        self.theme_colors = theme_colors
        self._update_icons()

        # Folha de estilos (QSS) unificada para toda a janela
        style = f"""
            /* Estilo geral */
            QWidget, QLabel, QRadioButton, QGroupBox {{
                background-color: transparent;
                color: {self.theme_colors.get('text_color', '#000')};
            }}

            /* --- ESTILO DAS ABAS PRINCIPAIS E INTERNAS --- */
            QTabWidget::pane {{ border-top: 1px solid {self.theme_colors.get('border_color')}; }}
            QTabBar::tab {{
                background-color: {self.theme_colors.get('bg_color')};
                color: {self.theme_colors.get('text_secondary')};
                padding: 10px 15px; border: 1px solid {self.theme_colors.get('border_color')};
                border-bottom: none; border-top-left-radius: 6px; border-top-right-radius: 6px;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: {self.theme_colors.get('button_hover')};
                color: {self.theme_colors.get('text_color')};
            }}
            QTabBar::tab:selected {{
                background-color: {self.theme_colors.get('surface_color')};
                color: {self.theme_colors.get('accent_color')};
                border-bottom: 1px solid {self.theme_colors.get('surface_color')};
            }}
            
            /* --- ESTILO DE INPUTS E TABELAS --- */
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QTableWidget, QTextEdit {{
                background-color: {self.theme_colors.get('surface_color')};
                color: {self.theme_colors.get('text_color')};
                border: 1px solid {self.theme_colors.get('border_color')};
                border-radius: 4px; padding: 5px;
            }}
            QHeaderView::section {{
                background-color: {self.theme_colors.get('menu_color', '#333')};
                color: {self.theme_colors.get('text_color')};
                padding: 5px; border: 1px solid {self.theme_colors.get('border_color')};
                font-weight: bold;
            }}

            /* --- CORREÇÃO: SCROLLBARS PARA TABELAS, COMBOBOX E TEXTEDIT --- */
            QTableWidget QScrollBar:vertical, QComboBox QAbstractItemView QScrollBar:vertical, QTextEdit QScrollBar:vertical {{
                border: none; background: {self.theme_colors.get('surface_color')}; width: 12px;
            }}
            QTableWidget QScrollBar::handle:vertical, QComboBox QAbstractItemView QScrollBar::handle:vertical, QTextEdit QScrollBar::handle:vertical {{
                background: {self.theme_colors.get('border_color')}; min-height: 20px; border-radius: 6px;
            }}

            /* --- CORREÇÃO: DROPDOWN DO COMBOBOX --- */
            QComboBox QAbstractItemView {{
                background-color: {self.theme_colors.get('surface_color')};
                border: 1px solid {self.theme_colors.get('border_color')};
                selection-background-color: {self.theme_colors.get('accent_color')};
            }}

            /* --- ESTILO DE LABELS ESPECÍFICOS --- */
            #statusLabel {{ font-weight: bold; }}
            #saldoLabel {{ font-weight: bold; }}
            #totalLabel {{ font-size: 18px; font-weight: bold; }}

            /* --- BOTÕES --- */
            #successButton {{ background-color: #28a745; color: white; border: none; font-weight: bold; }}
            #dangerButton {{ background-color: #dc3545; color: white; border: none; font-weight: bold; }}
            #warningButton {{ background-color: #ffc107; color: black; border: none; font-weight: bold; }}
        """
        self.setStyleSheet(style)

        # Atualiza a imagem do produto placeholder, se existir
        if hasattr(self, 'lbl_imagem_produto'):
            bg_color = self.theme_colors.get('surface_color', '#f0f0f0')
            border_color = self.theme_colors.get('border_color', '#ccc')
            text_secondary_color = self.theme_colors.get('text_secondary', '#6d6d70')
            self.lbl_imagem_produto.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg_color}; border: 2px dashed {border_color};
                    border-radius: 8px; color: {text_secondary_color};
                    font-style: italic; font-size: 10pt; padding: 10px;
                }}
            """)
        
        self.verificar_caixa_aberto() # Atualiza as cores do status
        self.update() # Força o redesenho


    def initUI(self):
        # ... (seu método initUI sem alterações, mas adicionando objectNames) ...
        main_layout = QVBoxLayout(self)
        self.frame_status = QFrame(); self.frame_status.setFrameShape(QFrame.StyledPanel)
        status_layout = QHBoxLayout(self.frame_status)
        self.lbl_status = QLabel("Status do Caixa: Fechado"); self.lbl_status.setObjectName("statusLabel")
        self.lbl_saldo = QLabel("Saldo Atual: R$ 0,00"); self.lbl_saldo.setObjectName("saldoLabel")
        status_layout.addWidget(self.lbl_status); status_layout.addWidget(self.lbl_saldo)
        self.btn_abrir_caixa = QPushButton(" Abrir Caixa"); self.btn_abrir_caixa.clicked.connect(self.abrir_caixa)
        self.btn_fechar_caixa = QPushButton(" Fechar Caixa"); self.btn_fechar_caixa.setEnabled(False); self.btn_fechar_caixa.clicked.connect(self.fechar_caixa)
        status_layout.addWidget(self.btn_abrir_caixa); status_layout.addWidget(self.btn_fechar_caixa)
        main_layout.addWidget(self.frame_status)
        self.tabs = QTabWidget()
        self.tab_vendas = QWidget(); self.setup_vendas_tab(); self.tabs.addTab(self.tab_vendas, " Vendas (PDV)")
        self.tab_movimentos = QWidget(); self.setup_movimentos_tab(); self.tabs.addTab(self.tab_movimentos, " Movimentações")
        self.tab_relatorios = QWidget(); self.setup_relatorios_tab(); self.tabs.addTab(self.tab_relatorios, " Relatórios de Caixa")
        main_layout.addWidget(self.tabs)
    
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
        # ... (seu método setup_vendas_tab sem alterações, mas adicionando objectNames) ...
        main_layout = QHBoxLayout(self.tab_vendas); splitter = QSplitter(Qt.Horizontal)
        left_panel_widget = QWidget(); layout_esquerda = QVBoxLayout(left_panel_widget); layout_esquerda.setContentsMargins(0, 0, 0, 0)
        frame_info = QFrame(); frame_info.setFrameShape(QFrame.StyledPanel); frame_info_layout = QGridLayout(frame_info)
        frame_info_layout.addWidget(QLabel("Cliente:"), 0, 0)
        self.cb_cliente = QComboBox(); self.cb_cliente.setMinimumWidth(200)
        frame_info_layout.addWidget(self.cb_cliente, 0, 1)
        self.btn_add_cliente = QPushButton(); self.btn_add_cliente.setFixedSize(30, 30); self.btn_add_cliente.setToolTip("Adicionar Novo Cliente"); self.btn_add_cliente.clicked.connect(self.adicionar_novo_cliente)
        frame_info_layout.addWidget(self.btn_add_cliente, 0, 2)
        frame_info_layout.addWidget(QLabel("Produto/Código:"), 1, 0)
        self.cb_produto = AutoPopupComboBox(); self.cb_produto.setEditable(True); self.cb_produto.lineEdit().returnPressed.connect(self.buscar_produto)
        frame_info_layout.addWidget(self.cb_produto, 1, 1)
        frame_info_layout.addWidget(QLabel("Quantidade:"), 0, 3)
        self.spin_quantidade = QSpinBox(); self.spin_quantidade.setMinimum(1); self.spin_quantidade.setMaximum(9999)
        frame_info_layout.addWidget(self.spin_quantidade, 0, 4)
        frame_info_layout.addWidget(QLabel("Preço Unitário:"), 1, 3)
        self.spin_preco = QDoubleSpinBox(); self.spin_preco.setMinimum(0); self.spin_preco.setMaximum(999999.99); self.spin_preco.setDecimals(2); self.spin_preco.setSingleStep(0.10); self.spin_preco.setPrefix("R$ ")
        frame_info_layout.addWidget(self.spin_preco, 1, 4)
        self.btn_adicionar_item = QPushButton(" Adicionar Item"); self.btn_adicionar_item.clicked.connect(self.adicionar_item)
        frame_info_layout.addWidget(self.btn_adicionar_item, 0, 5, 2, 1)
        layout_esquerda.addWidget(frame_info)
        self.tabela_itens = QTableWidget(); self.tabela_itens.setColumnCount(6); self.tabela_itens.setHorizontalHeaderLabels(['Cód.', 'Produto', 'Qtde', 'Preço Unit.', 'Subtotal', ''])
        self.tabela_itens.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch); self.tabela_itens.setColumnWidth(5, 40)
        layout_esquerda.addWidget(self.tabela_itens)
        frame_total = QFrame(); frame_total.setFrameShape(QFrame.StyledPanel); frame_total_layout = QHBoxLayout(frame_total)
        self.lbl_total = QLabel("Total: R$ 0,00"); self.lbl_total.setObjectName("totalLabel") # Adicionado objectName
        frame_total_layout.addWidget(self.lbl_total); frame_total_layout.addStretch()
        self.btn_limpar = QPushButton(" Limpar Venda"); self.btn_limpar.setObjectName("warningButton"); self.btn_limpar.clicked.connect(self.limpar_venda)
        frame_total_layout.addWidget(self.btn_limpar)
        self.btn_finalizar = QPushButton(" Finalizar Venda"); self.btn_finalizar.setObjectName("successButton"); self.btn_finalizar.clicked.connect(self.finalizar_venda)
        frame_total_layout.addWidget(self.btn_finalizar)
        layout_esquerda.addWidget(frame_total); splitter.addWidget(left_panel_widget)
        right_panel_widget = QWidget(); layout_direita = QVBoxLayout(right_panel_widget)
        self.lbl_imagem_produto = QLabel("Selecione um produto para ver a imagem"); self.lbl_imagem_produto.setAlignment(Qt.AlignCenter); self.lbl_imagem_produto.setMinimumSize(250, 250)
        layout_direita.addWidget(self.lbl_imagem_produto, 1)
        splitter.addWidget(right_panel_widget); splitter.setSizes([700, 300]); main_layout.addWidget(splitter)
    

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
        Busca um produto pelo texto atual no ComboBox (código de barras OU nome),
        atualiza a UI e o adiciona ao carrinho.
        """
        texto_busca = self.cb_produto.currentText().strip()
        if not texto_busca:
            return

        # Procura o produto no ComboBox pelo código de barras OU pelo nome
        index_encontrado = -1
        for i in range(self.cb_produto.count()):
            produto_data = self.cb_produto.itemData(i)
            if not produto_data: continue

            # --- INÍCIO DA CORREÇÃO ---
            # Agora verifica se o texto corresponde ao código de barras OU ao nome exato
            if (produto_data.get('codigo_barras') == texto_busca or 
                produto_data.get('nome').lower() == texto_busca.lower()):
                index_encontrado = i
                break
            # --- FIM DA CORREÇÃO ---
        
        if index_encontrado != -1:
            produto_encontrado = self.cb_produto.itemData(index_encontrado)
            self.cb_produto.setCurrentIndex(index_encontrado)
            
            # ATUALIZA A UI (IMAGEM E PREÇO) IMEDIATAMENTE
            self._atualizar_info_produto_selecionado(produto_encontrado)
            
            # CHAMA A FUNÇÃO DE ADICIONAR
            self.adicionar_item()
        else:
            AlertDialog(self, "Produto não encontrado", 
                        f"Nenhum produto com o código ou nome '{texto_busca}' foi encontrado.",
                        alert_type='warning', theme_colors=self.theme_colors).exec_()
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
        # ... (seu método setup_movimentos_tab, mas adicionando objectNames aos botões)...
        layout = QVBoxLayout(self.tab_movimentos)
        frame_acoes = QFrame(); frame_acoes_layout = QHBoxLayout(frame_acoes)
        self.btn_nova_entrada = QPushButton(" Nova Entrada"); self.btn_nova_entrada.setObjectName("successButton"); self.btn_nova_entrada.clicked.connect(lambda: self.novo_movimento("Entrada"))
        frame_acoes_layout.addWidget(self.btn_nova_entrada)
        self.btn_nova_saida = QPushButton(" Nova Saída"); self.btn_nova_saida.setObjectName("dangerButton"); self.btn_nova_saida.clicked.connect(lambda: self.novo_movimento("Saída"))
        frame_acoes_layout.addWidget(self.btn_nova_saida)
        frame_acoes_layout.addStretch()
        # O resto do setup_movimentos_tab...
        frame_acoes_layout.addWidget(QLabel("Período:")); self.cb_periodo_mov = QComboBox(); self.cb_periodo_mov.addItems(["Hoje", "Última Semana", "Este Caixa", "Personalizado"]); self.cb_periodo_mov.currentIndexChanged.connect(self.periodo_movimentos_alterado); frame_acoes_layout.addWidget(self.cb_periodo_mov)
        self.dt_inicio = QDateEdit(QDate.currentDate()); self.dt_inicio.setCalendarPopup(True); frame_acoes_layout.addWidget(self.dt_inicio)
        self.dt_fim = QDateEdit(QDate.currentDate()); self.dt_fim.setCalendarPopup(True); frame_acoes_layout.addWidget(self.dt_fim)
        self.btn_filtrar = QPushButton(" Filtrar"); self.btn_filtrar.clicked.connect(self.filtrar_movimentos); frame_acoes_layout.addWidget(self.btn_filtrar)
        layout.addWidget(frame_acoes)
        self.tabela_movimentos = QTableWidget(); self.tabela_movimentos.setColumnCount(6); self.tabela_movimentos.setHorizontalHeaderLabels(['ID', 'Data/Hora', 'Tipo', 'Descrição', 'Forma Pgto', 'Valor']); self.tabela_movimentos.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        layout.addWidget(self.tabela_movimentos)
        frame_totais = QFrame(); frame_totais.setFrameShape(QFrame.StyledPanel); frame_totais_layout = QHBoxLayout(frame_totais)
        self.lbl_total_entradas = QLabel("Total Entradas: R$ 0,00"); self.lbl_total_saidas = QLabel("Total Saídas: R$ 0,00"); self.lbl_saldo_periodo = QLabel("Saldo do Período: R$ 0,00")
        frame_totais_layout.addWidget(self.lbl_total_entradas); frame_totais_layout.addWidget(self.lbl_total_saidas); frame_totais_layout.addWidget(self.lbl_saldo_periodo)
        layout.addWidget(frame_totais); self.periodo_movimentos_alterado()

    # Adicione este novo método dentro da classe CaixaWindow
    def periodo_movimentos_alterado(self):
        """Controla a UI de filtros e aplica o filtro selecionado."""
        periodo = self.cb_periodo_mov.currentText()
        hoje = QDate.currentDate()
        
        # Habilita ou desabilita os seletores de data
        personalizado = (periodo == "Personalizado")
        self.dt_inicio.setEnabled(personalizado)
        self.dt_fim.setEnabled(personalizado)
        
        if periodo == "Hoje":
            self.dt_inicio.setDate(hoje)
            self.dt_fim.setDate(hoje)
        elif periodo == "Última Semana":
            # Inclui hoje e os últimos 6 dias
            self.dt_inicio.setDate(hoje.addDays(-6))
            self.dt_fim.setDate(hoje)
        
        # Aplica o filtro imediatamente após a mudança
        # O botão "Filtrar" agora serve mais para o modo "Personalizado"
        if self.caixa_atual:
            self.filtrar_movimentos()
    
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
        # ... (seu método sem alterações, mas a cor agora vem do QSS) ...
        self.caixa_atual = self.db.obter_caixa_aberto()
        if self.caixa_atual:
            self.lbl_status.setText(f"Status do Caixa: Aberto (ID: {self.caixa_atual['id']})")
            self.lbl_status.setStyleSheet(f"font-weight: bold; color: {self.theme_colors.get('success_color', '#28a745')};")
            saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
            self.lbl_saldo.setText(f"Saldo Atual: R$ {saldo_atual:.2f}")
            self.btn_abrir_caixa.setEnabled(False); self.btn_fechar_caixa.setEnabled(True)
            self.filtrar_movimentos()
        else:
            self.lbl_status.setText("Status do Caixa: Fechado")
            self.lbl_status.setStyleSheet(f"font-weight: bold; color: {self.theme_colors.get('danger_color', '#dc3545')};")
            self.lbl_saldo.setText("Saldo Atual: R$ 0,00")
            self.btn_abrir_caixa.setEnabled(True); self.btn_fechar_caixa.setEnabled(False)
            self.tabela_movimentos.setRowCount(0)
    
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
        # O itemData pode ser None se o índice for inválido (ex: item vazio)
        produto = self.cb_produto.itemData(index)
        self._atualizar_info_produto_selecionado(produto)
    
    def _atualizar_info_produto_selecionado(self, produto):
        """
        Método auxiliar para atualizar a UI (preço e imagem) com base em um produto.
        Se o produto for None, limpa os campos.
        """
        if not produto:
            self.spin_preco.setValue(0)
            self.lbl_imagem_produto.clear()
            self.lbl_imagem_produto.setText("Selecione um produto...")
            return

        # Define o preço de venda (normal ou promocional)
        preco_final = self.obter_preco_final_produto(produto)
        self.spin_preco.setValue(preco_final if preco_final else 0)
        
        # Define a imagem
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
    
    def obter_estoque_disponivel(self, produto):
        """Retorna o estoque disponível baseado no tipo de venda"""
        if produto.get('tipo_venda') == 'embalagem':
            return produto.get('quantidade', 0)  # Embalagens inteiras
        elif produto.get('tipo_venda') == 'fracao':
            return produto.get('estoque_fracionado', 0)  # Estoque fracionado
        else:
            return produto.get('quantidade', 0)  # Produto normal
    
    def _atualizar_info_produto_selecionado(self, produto_base):
        """
        Método unificado para atualizar a UI (preço e imagem) com base em um produto.
        Se o produto for None, limpa os campos.
        """
        if not produto_base:
            self.spin_preco.setValue(0)
            self.lbl_imagem_produto.clear()
            self.lbl_imagem_produto.setText("Selecione um produto...")
            return

        # Busca o produto com o preço final (promocional ou não) para exibir na UI
        produto_com_preco_final = self.db.obter_produto_com_preco_promocional(produto_base['id'])
        if not produto_com_preco_final:
            # Em caso de erro, usa o preço de venda padrão como fallback
            self.spin_preco.setValue(produto_base.get('preco_venda', 0))
        else:
            # Exibe o preço de venda da EMBALAGEM (que pode ser o promocional)
            self.spin_preco.setValue(produto_com_preco_final.get('preco_venda', 0))
        
        # Lógica da imagem (permanece a mesma)
        imagem_path = produto_base.get('imagem_path')
        if imagem_path and os.path.exists(imagem_path):
            pixmap = QPixmap(imagem_path)
            self.lbl_imagem_produto.setPixmap(pixmap.scaled(
                self.lbl_imagem_produto.size(),
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            ))
        else:
            self.lbl_imagem_produto.setText("Produto sem imagem")

    def adicionar_item(self):
        # --- INÍCIO DA CORREÇÃO ---
        # Agora a função é inteligente. Ela primeiro busca o produto pelo texto
        # em vez de depender cegamente do índice selecionado.
        texto_busca = self.cb_produto.currentText().strip()
        produto_base = None

        if not texto_busca:
            AlertDialog(self, "Ação Necessária", "Selecione ou digite um produto para adicionar.", 'warning', theme_colors=self.theme_colors).exec_()
            return

        # Procura ativamente pelo produto correspondente ao texto
        for i in range(self.cb_produto.count()):
            produto_data = self.cb_produto.itemData(i)
            if not produto_data: continue
            
            if (produto_data.get('codigo_barras') == texto_busca or 
                produto_data.get('nome').lower() == texto_busca.lower()):
                produto_base = produto_data
                break
                
        if not produto_base:
            AlertDialog(self, "Produto não encontrado", 
                        f"Nenhum produto com o código ou nome '{texto_busca}' foi encontrado.",
                        alert_type='warning', theme_colors=self.theme_colors).exec_()
            return
        # --- FIM DA CORREÇÃO ---

        # 2. USA A FUNÇÃO CENTRAL DO DB PARA OBTER O PRODUTO COM O PREÇO FINAL JÁ APLICADO
        produto_com_preco_final = self.db.obter_produto_com_preco_promocional(produto_base['id'])
        if not produto_com_preco_final:
            QMessageBox.critical(self, "Erro", "Não foi possível obter os dados de preço do produto.")
            return

        sale_details = None
        
        # 3. A lógica de venda agora usa o objeto 'produto_com_preco_final', que contém os preços corretos
        if produto_com_preco_final.get('fracionado'):
             # CHAMA A NOVA CLASSE DE DIÁLOGO TEMÁTICA
            dialog = DialogVendaFracionada(self, produto_com_preco_final, self.theme_colors)
            if dialog.exec_() == QDialog.Accepted:
                sale_details = dialog.get_sale_details()
            else:
                return # O usuário cancelou
        else:
            # Lógica para produtos não fracionados
            quantidade = self.spin_quantidade.value()
            if quantidade > produto_com_preco_final['quantidade']:
                QMessageBox.warning(self, "Estoque Insuficiente", f"Estoque disponível: {produto_com_preco_final['quantidade']} unidades.")
                return

            sale_details = {
                "quantidade": quantidade,
                "preco_unitario": produto_com_preco_final['preco_venda'], # Usa o preço já corrigido
                "is_embalagem": True,
                "produto_nome": produto_com_preco_final['nome']
            }

        if not sale_details:
            return

        item_carrinho = {
            'produto_id': produto_com_preco_final['id'],
            # --- INÍCIO DA CORREÇÃO 2 ---
            # Adicionamos o código de barras ao item do carrinho
            'codigo_barras': produto_com_preco_final.get('codigo_barras', 'N/A'),
            # --- FIM DA CORREÇÃO 2 ---
            'produto_nome': sale_details['produto_nome'],
            'quantidade': sale_details['quantidade'],
            'preco_unitario': sale_details['preco_unitario'],
            'subtotal': sale_details['quantidade'] * sale_details['preco_unitario'],
            'is_embalagem': sale_details['is_embalagem']
        }
        
        self.itens_venda.append(item_carrinho)
        self.atualizar_tabela_itens()
        self.calcular_total()
        
        # Limpa os campos para a próxima adição
        self.cb_produto.setCurrentText("")
        self.spin_quantidade.setValue(1)
        self.spin_preco.setValue(0)
        self.cb_produto.setFocus()
    
    def atualizar_tabela_itens(self):
        self.tabela_itens.setRowCount(0)
        
        for i, item in enumerate(self.itens_venda):
            self.tabela_itens.insertRow(i)
            
            # --- INÍCIO DA CORREÇÃO 3 ---
            # Alterado para exibir o 'codigo_barras' em vez do 'produto_id'
            self.tabela_itens.setItem(i, 0, QTableWidgetItem(str(item['codigo_barras'])))
            # --- FIM DA CORREÇÃO 3 ---
            
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
            btn_remover.setFlat(True) 
            btn_remover.setCursor(Qt.PointingHandCursor)
            btn_remover.clicked.connect(lambda checked, row=i: self.remover_item(row))
            self.tabela_itens.setCellWidget(i, 5, btn_remover)
    
    def remover_item(self, row):
        if 0 <= row < len(self.itens_venda):
            del self.itens_venda[row]
            self.atualizar_tabela_itens()
            self.calcular_total()

            # --- INÍCIO DA CORREÇÃO ---
            # Ao remover um item, limpa a imagem e o preço, pois o contexto
            # do último produto selecionado foi perdido.
            self._atualizar_info_produto_selecionado(None)
            # --- FIM DA CORREÇÃO ---
            
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
            AlertDialog(self, "Caixa Fechado", "Abra o caixa antes de realizar vendas", 'warning', theme_colors=self.theme_colors).exec_()
            return
        
        if not self.itens_venda:
            AlertDialog(self, "Venda Vazia", "Adicione itens para finalizar a venda", 'warning', theme_colors=self.theme_colors).exec_()
            return

        taxa_debito = float(self.db.obter_configuracao('taxa_cartao_debito', '1.99'))
        taxa_credito = float(self.db.obter_configuracao('taxa_cartao_credito', '4.98'))
        
        dialog = DialogFinalizarVenda(self, self.total_venda, taxa_debito, taxa_credito, self.theme_colors)
        
        if dialog.exec_() != QDialog.Accepted:
            return

        venda_data = dialog.get_data()

        # --- Início da Lógica de Cálculo (sem alteração) ---
        if venda_data['salvar_taxas']:
            self.db.definir_configuracao('taxa_cartao_debito', str(venda_data['taxa_debito']))
            self.db.definir_configuracao('taxa_cartao_credito', str(venda_data['taxa_credito']))
        
        total_cliente_paga = max(0, self.total_venda - venda_data['desconto'])
        taxa_percentual = 0.0
        if venda_data['forma_pagamento'] == "Cartão de Débito":
            taxa_percentual = venda_data['taxa_debito']
        elif venda_data['forma_pagamento'] == "Cartão de Crédito":
            taxa_percentual = venda_data['taxa_credito']
        
        valor_da_taxa = total_cliente_paga * (taxa_percentual / 100.0)
        valor_para_faturamento = total_cliente_paga - valor_da_taxa

        if venda_data['forma_pagamento'] == "Dinheiro" and venda_data['valor_recebido'] < total_cliente_paga:
            AlertDialog(self, "Valor Insuficiente", "O valor recebido é menor que o total a pagar.", 'warning', theme_colors=self.theme_colors).exec_()
            return
        # --- Fim da Lógica de Cálculo ---

        # =================== INÍCIO DA TRANSAÇÃO ATÔMICA ===================
        try:
            self.db.begin_transaction()

            # 1. Registrar a Venda
            venda_id = self.db.registrar_venda(
                cliente_id=self.cb_cliente.currentData(),
                valor_total=total_cliente_paga,
                desconto=venda_data['desconto'],
                forma_pagamento=venda_data['forma_pagamento'],
                parcelas=venda_data['parcelas'],
                observacao=venda_data['observacao'],
                status="Concluída",
                operador="Sistema"  # Idealmente, seria o usuário logado
            )
            if not venda_id:
                raise Exception("Não foi possível obter o ID da venda registrada.")

            # 2. Registrar Itens e Atualizar Estoque
            for item in self.itens_venda:
                # 2a. Atualiza o estoque (agora sem commit interno)
                sucesso_estoque, msg_estoque = self.db.atualizar_estoque_venda(
                    item['produto_id'], item['quantidade'], item['is_embalagem']
                )
                if not sucesso_estoque:
                    raise Exception(msg_estoque) # Propaga o erro do estoque

                # 2b. Registra o item da venda
                vendido_como = 'Embalagem' if item['is_embalagem'] else 'Fração'
                sucesso_item = self.db.registrar_item_venda(
                    venda_id, item['produto_id'], item['quantidade'],
                    item['preco_unitario'], item['subtotal'], vendido_como
                )
                if not sucesso_item:
                    raise Exception(f"Falha ao registrar o item {item['produto_nome']}.")

            # 3. Registrar Movimento no Caixa
            movimento_id = self.db.registrar_movimento_caixa(
                self.caixa_atual['id'], "Entrada", f"Venda #{venda_id}",
                valor_para_faturamento,
                venda_data['forma_pagamento'], venda_id, "Venda", "Sistema"
            )
            if not movimento_id:
                raise Exception("Falha ao registrar a entrada no caixa.")

            # 4. Se tudo deu certo, confirma todas as operações
            self.db.commit_transaction()
            
            # --- Lógica de Sucesso (Executada apenas após o commit) ---
            saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
            self.lbl_saldo.setText(f"Saldo Atual: R$ {saldo_atual:.2f}")
            
            troco_final = venda_data['valor_recebido'] - total_cliente_paga
            msg_sucesso = "Venda finalizada com sucesso!"
            if venda_data['forma_pagamento'] == "Dinheiro" and troco_final > 0:
                msg_sucesso += f"\nTroco: R$ {troco_final:.2f}"
            
            AlertDialog(self, "Sucesso", msg_sucesso, 'success', theme_colors=self.theme_colors).exec_()
            
            # Limpa a interface para a próxima venda
            self.itens_venda = []
            self.atualizar_tabela_itens()
            self.calcular_total()
            self.cb_cliente.setCurrentIndex(0)
            self._atualizar_info_produto_selecionado(None)
            self.filtrar_movimentos()

            self.venda_finalizada.emit()


        except Exception as e:
            # 5. Se qualquer etapa falhou, desfaz tudo
            self.db.rollback_transaction()
            print(f"ERRO DE TRANSAÇÃO: {e}")
            AlertDialog(self, "Erro ao Salvar Venda",
                        f"Ocorreu um erro e a venda não foi salva. Todas as alterações foram desfeitas.\n\nDetalhe: {e}",
                        'error', theme_colors=self.theme_colors).exec_()
        # =================== FIM DA TRANSAÇÃO ATÔMICA ===================

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
        dialog = DialogAbrirCaixa(self, self.theme_colors)
        
        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_data()
            saldo_inicial = dados['saldo_inicial']
            observacao = dados['observacao']
            
            usuario_logado = "Sistema" # Você pode adaptar para pegar o usuário real
            
            caixa_id = self.db.abrir_caixa(saldo_inicial, usuario_logado, observacao)
            if caixa_id:
                self.verificar_caixa_aberto()
                AlertDialog(self, "Sucesso", "Caixa aberto com sucesso!", 'success', theme_colors=self.theme_colors).exec_()
            else:
                AlertDialog(self, "Erro", "Erro ao abrir o caixa.", 'error', theme_colors=self.theme_colors).exec_()

    def fechar_caixa(self):
        if not self.caixa_atual:
            return

        saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
        caixa_a_fechar_id = self.caixa_atual['id']

        dialog = DialogFecharCaixa(self, saldo_atual, self.theme_colors)

        if dialog.exec_() == QDialog.Accepted:
            dados = dialog.get_data()
            saldo_informado = dados['saldo_informado']
            observacao = dados['observacao']
            
            usuario_logado = "Sistema" # Adaptar para pegar o usuário real

            confirma = AlertDialog(self, "Confirmar Fechamento", 
                            f"Deseja realmente fechar o caixa?",
                            'question', QMessageBox.Yes | QMessageBox.No, self.theme_colors)
            
            # ================================================================= #
            #       CORREÇÃO APLICADA AQUI                                      #
            # ================================================================= #
            # Trocamos QDialog.Accepted por QMessageBox.Yes para corresponder
            # ao sinal que o botão "Sim" do AlertDialog emite.
            if confirma.exec_() == QMessageBox.Yes:
                sucesso = self.db.fechar_caixa(
                    caixa_a_fechar_id, 
                    saldo_informado, 
                    usuario_logado, 
                    observacao
                )
                
                if sucesso:
                    # A lógica de backup (se você tiver) pode ser chamada aqui
                    # backup_sucesso = self.realizar_backup() 
                    self.verificar_caixa_aberto()
                    
                    msg = "Caixa fechado com sucesso!"
                    # if backup_sucesso: msg += "\nBackup dos dados realizado com sucesso."
                    
                    AlertDialog(self, "Sucesso", msg, 'success', theme_colors=self.theme_colors).exec_()
                    
                else:
                    AlertDialog(self, "Erro", "Erro ao fechar o caixa no banco de dados.", 'error', theme_colors=self.theme_colors).exec_()

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

    # Em estoque_window.py E caixa_window.py
    # SUBSTITUA este método inteiro em AMBOS os arquivos

    def _gerar_pdf_com_template(self, file_path, report_title, elementos, company_info, custom_logo_path):
        try:
            left_margin, right_margin, top_margin, bottom_margin = 2*cm, 2*cm, 3.5*cm, 1.5*cm

            def header_footer(canvas, doc):
                canvas.saveState()
                
                # --- INÍCIO DA CORREÇÃO: Lógica de Cabeçalho com Tabela ---
                
                # 1. Prepara os elementos para o cabeçalho
                styles = getSampleStyleSheet()
                style_info = ParagraphStyle(name='Info', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=9, leading=12)
                
                # Elemento 1: Logo do Sistema
                system_logo_path = "assets/img/Logo2.png"
                logo_sistema = Image(system_logo_path, width=2.5*cm, height=1.2*cm, kind='proportional') if os.path.exists(system_logo_path) else Spacer(0,0)
                
                # Elemento 2: Logo Personalizada
                logo_cliente = Image(custom_logo_path, width=2.5*cm, height=1.2*cm, kind='proportional') if custom_logo_path and os.path.exists(custom_logo_path) else Spacer(0,0)

                # Elemento 3: Bloco de Informações da Empresa (como Parágrafos)
                info_elements = []
                if company_info.get('empresa_nome'):
                    info_elements.append(Paragraph(company_info['empresa_nome'], style_info))
                if company_info.get('empresa_endereco'):
                    info_elements.append(Paragraph(company_info['empresa_endereco'], style_info))
                if company_info.get('empresa_telefone') or company_info.get('empresa_email'):
                    contato_str = f"Telefone: {company_info.get('empresa_telefone', '')} | Email: {company_info.get('empresa_email', '')}"
                    info_elements.append(Paragraph(contato_str, style_info))
                if company_info.get('empresa_cnpj'):
                    info_elements.append(Paragraph(f"CNPJ: {company_info.get('empresa_cnpj')}", style_info))

                # 2. Monta a tabela do cabeçalho com 3 colunas
                header_data = [[logo_sistema, logo_cliente, info_elements]]
                
                # A largura total disponível é a largura da página menos as margens
                available_width = doc.width
                
                header_table = Table(header_data, colWidths=[3*cm, 3*cm, available_width - 6*cm])
                header_table.setStyle(TableStyle([
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'), # ALINHAMENTO VERTICAL CENTRALIZADO
                    ('ALIGN', (0, 0), (1, 0), 'LEFT'),      # Logos alinhadas à esquerda
                    ('ALIGN', (2, 0), (2, 0), 'RIGHT'),     # Bloco de texto alinhado à direita
                ]))
                
                # 3. Desenha a tabela no canvas
                w, h = header_table.wrap(doc.width, doc.topMargin)
                header_table.drawOn(canvas, doc.leftMargin, doc.height + doc.topMargin - h + 0.5*cm) # Ajuste fino da posição vertical
                
                # 4. Desenha a linha ABAIXO da tabela
                line_y = doc.height + doc.topMargin - h
                canvas.setStrokeColorRGB(0.9, 0.9, 0.9)
                canvas.line(doc.leftMargin, line_y, doc.width + doc.leftMargin, line_y)

                # --- FIM DA CORREÇÃO ---

                # Rodapé (sem alteração)
                canvas.setFont('Helvetica-Oblique', 8)
                canvas.drawRightString(doc.width + doc.leftMargin, doc.bottomMargin - 20, f"Página {canvas.getPageNumber()} | {report_title}")
                canvas.restoreState()

            doc = SimpleDocTemplate(file_path, pagesize=A4, topMargin=top_margin, bottomMargin=bottom_margin, leftMargin=left_margin, rightMargin=right_margin)
            doc.build(elementos, onFirstPage=header_footer, onLaterPages=header_footer)
            
            AlertDialog(self, "Sucesso", f"Relatório salvo com sucesso em:\n{file_path}", alert_type='success', theme_colors=self.theme_colors).exec_()

        except Exception as e:
            AlertDialog(self, "Erro ao Gerar PDF", f"Ocorreu um erro inesperado: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()

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
        # 1. CHAMA A NOVA CLASSE DE DIÁLOGO TEMÁTICA
        dialog = DialogAdicionarCliente(self, self.theme_colors)
        
        # 2. SE O USUÁRIO CONFIRMAR...
        if dialog.exec_() == QDialog.Accepted:
            # 3. Pega os dados do diálogo
            cliente_data = dialog.get_data()
            
            if not cliente_data['nome']:
                AlertDialog(self, "Campo Obrigatório", "O campo Nome é obrigatório", 'warning', theme_colors=self.theme_colors).exec_()
                return
            
            # 4. Adiciona o cliente ao banco de dados usando os dados retornados
            cliente_id = self.db.adicionar_cliente(
                nome=cliente_data['nome'],
                data_nascimento=cliente_data['data_nascimento'],
                telefone=cliente_data['telefone'],
                email=cliente_data['email'],
                endereco=cliente_data['endereco']
            )
            
            if cliente_id:
                # --- INÍCIO DA CORREÇÃO ---
                # Exibe a mensagem de sucesso para o usuário
                AlertDialog(self, "Sucesso", "Cliente cadastrado com sucesso!", 'success', theme_colors=self.theme_colors).exec_()
                # --- FIM DA CORREÇÃO ---

                # 5. Atualiza a lista de clientes e seleciona o novo cliente
                self.carregar_clientes()
                index = self.cb_cliente.findData(cliente_id)
                if index >= 0:
                    self.cb_cliente.setCurrentIndex(index)
                self.dados_clientes_alterados.emit() # Emite o sinal para outras janelas
            else:
                AlertDialog(self, "Erro", "Erro ao cadastrar cliente no banco de dados.", 'error', theme_colors=self.theme_colors).exec_()

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
            # Limpa os totais se não houver caixa aberto
            self.lbl_total_entradas.setText("Total Entradas: R$ 0,00")
            self.lbl_total_saidas.setText("Total Saídas: R$ 0,00")
            self.lbl_saldo_periodo.setText("Saldo do Período: R$ 0,00")
            return
        
        periodo = self.cb_periodo_mov.currentText()
        movimentos = []

        if periodo == "Este Caixa":
            # Reutiliza a função que busca tudo para o caixa atual
            movimentos = self.db.listar_movimentos_caixa(self.caixa_atual['id'])
        else:
            # Para "Hoje", "Última Semana" e "Personalizado", busca por período
            data_inicio = self.dt_inicio.date().toString("yyyy-MM-dd")
            data_fim = self.dt_fim.date().toString("yyyy-MM-dd")
            
            movimentos = self.db.listar_movimentos_por_periodo(
                self.caixa_atual['id'], data_inicio, data_fim
            )
        
        # O restante do código para preencher a tabela permanece o mesmo
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
            AlertDialog(self, "Caixa Fechado", "Abra o caixa antes de realizar movimentações", 'warning', theme_colors=self.theme_colors).exec_()
            return
        
        # USA A NOVA CLASSE DE DIÁLOGO TEMÁTICA
        dialog = DialogNovoMovimento(self, tipo, self.theme_colors)
        dialog.confirmar_btn.clicked.connect(lambda: self.confirmar_movimento(dialog, tipo))
        dialog.cancelar_btn.clicked.connect(dialog.reject)
        dialog.exec_()
        
    def confirmar_movimento(self, dialog, tipo):
        dados = dialog.get_data()
        if not dados["descricao"]:
            AlertDialog(self, "Campo Obrigatório", "O campo Descrição é obrigatório", 'warning', theme_colors=self.theme_colors).exec_()
            return
        if dados["valor"] <= 0:
            AlertDialog(self, "Valor Inválido", "O valor deve ser maior que zero", 'warning', theme_colors=self.theme_colors).exec_()
            return
            
        sucesso = self.db.registrar_movimento_caixa(
            self.caixa_atual['id'], tipo, dados["descricao"], dados["valor"], 
            dados["forma_pagamento"], None, "Manual", "Sistema", dados["observacao"],
            afeta_financeiro=dados["natureza"]
        )
            
        if sucesso:
            dialog.accept()
            saldo_atual = self.db.obter_saldo_atual(self.caixa_atual['id'])
            self.lbl_saldo.setText(f"Saldo Atual: R$ {saldo_atual:.2f}")
            
            # --- CORREÇÃO APLICADA AQUI ---
            # Trocamos carregar_movimentos() por filtrar_movimentos() para que o filtro
            # de período seja respeitado ao atualizar a tabela.
            self.filtrar_movimentos() 
            # --- FIM DA CORREÇÃO ---

            self.movimento_manual_registrado.emit()
            AlertDialog(self, "Sucesso", f"{tipo} registrada com sucesso!", 'success', theme_colors=self.theme_colors).exec_()
        else:
            AlertDialog(dialog, "Erro", f"Erro ao registrar {tipo.lower()}", 'error', theme_colors=self.theme_colors).exec_()

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

    # SUBSTITUA O MÉTODO gerar_relatorio INTEIRO PELA VERSÃO ABAIXO

    def gerar_relatorio(self):
        data_inicio = self.dt_rel_inicio.date().toString("yyyy-MM-dd")
        data_fim = self.dt_rel_fim.date().toString("yyyy-MM-dd")

        # ***** CORREÇÃO PRINCIPAL AQUI *****
        # Chamada direta para o método correto no DatabaseManager
        dados = self.db.gerar_relatorio_periodo(data_inicio, data_fim)
        
        if not dados or not dados.get('vendas'):
            QMessageBox.information(self, "Sem Dados", "Não foram encontradas vendas ou movimentos para o período selecionado.")
            self.btn_exportar_pdf.setVisible(False)
            self.text_resumo.clear()
            self.tabela_rel_movimentos.setRowCount(0)
            self.tabela_rel_vendas.setRowCount(0)
            return
            
        self.dados_relatorio_atual = dados
        
        try:
            self.btn_exportar_pdf.clicked.disconnect()
        except TypeError:
            pass
        
        self.btn_exportar_pdf.clicked.connect(
            lambda: self.abrir_dialogo_exportacao(data_inicio, data_fim, self.dados_relatorio_atual)
        )
        
        # Preencher a UI com os dados
        self.preencher_resumo_visual(dados, data_inicio, data_fim)

        self.tabela_rel_movimentos.setRowCount(0)
        movimentos = dados.get('movimentos', [])
        for i, movimento in enumerate(movimentos):
            self.tabela_rel_movimentos.insertRow(i)
            tipo, valor = movimento['tipo'], movimento['valor']
            cor_valor = QColor("#28a745") if tipo == "Entrada" else QColor("#dc3545")
            
            self.tabela_rel_movimentos.setItem(i, 0, QTableWidgetItem(str(movimento['id'])))
            self.tabela_rel_movimentos.setItem(i, 1, QTableWidgetItem(movimento['data_hora']))
            tipo_item = QTableWidgetItem(tipo); tipo_item.setForeground(cor_valor)
            self.tabela_rel_movimentos.setItem(i, 2, tipo_item)
            self.tabela_rel_movimentos.setItem(i, 3, QTableWidgetItem(movimento['descricao']))
            self.tabela_rel_movimentos.setItem(i, 4, QTableWidgetItem(movimento['forma_pagamento']))
            valor_item = QTableWidgetItem(f"R$ {valor:.2f}"); valor_item.setForeground(cor_valor)
            valor_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_rel_movimentos.setItem(i, 5, valor_item)

        self.tabela_rel_vendas.setRowCount(0)
        vendas = dados.get('vendas', [])
        for i, venda in enumerate(vendas):
            self.tabela_rel_vendas.insertRow(i)
            self.tabela_rel_vendas.setItem(i, 0, QTableWidgetItem(str(venda['id'])))
            self.tabela_rel_vendas.setItem(i, 1, QTableWidgetItem(venda['data_hora']))
            self.tabela_rel_vendas.setItem(i, 2, QTableWidgetItem(venda['cliente']))
            valor_total_item = QTableWidgetItem(f"R$ {venda['valor_total']:.2f}"); valor_total_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_rel_vendas.setItem(i, 3, valor_total_item)
            desconto_item = QTableWidgetItem(f"R$ {venda['desconto']:.2f}"); desconto_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.tabela_rel_vendas.setItem(i, 4, desconto_item)
            self.tabela_rel_vendas.setItem(i, 5, QTableWidgetItem(venda['forma_pagamento']))
            
        self.btn_exportar_pdf.setVisible(True)

    # --- INÍCIO DO CÓDIGO A SER ADICIONADO ---
    # Este método precisa estar INDENTADO para dentro da classe CaixaWindow
    def _buscar_dados_relatorio(self, data_inicio, data_fim):
        """
        Busca e consolida todos os dados necessários para os relatórios financeiros.
        """
        try:
            # Substituído para usar o método já existente no db manager
            dados = self.db.gerar_relatorio_periodo(data_inicio, data_fim)
            if dados:
                return dados
            else:
                raise Exception("A busca de dados no banco retornou None.")

        except Exception as e:
            print(f"Erro ao buscar dados para relatório na UI: {e}")
            QMessageBox.critical(self, "Erro de Banco de Dados", f"Não foi possível buscar os dados do relatório: {e}")
            return None
    # --- FIM DO CÓDIGO A SER ADICIONADO ---


    def preencher_resumo_visual(self, dados, data_inicio, data_fim):
        """Gera um HTML elaborado para a aba de resumo, usando os dados detalhados."""
        
        theme = self.theme_colors
        cor_fundo_body = theme.get('bg_color', '#ffffff')
        cor_fundo_card = theme.get('surface_color', '#f2f2f7')
        cor_borda = theme.get('border_color', '#e1e8f3')
        cor_titulo_principal = theme.get('text_color', '#34495e')
        cor_subtitulo = theme.get('text_secondary', '#7f8c8d')
        cor_titulo_kpi = theme.get('text_secondary', '#6c757d')
        cor_valor_kpi = theme.get('text_color', '#2c3e50')
        cor_entrada = "#28a745"
        cor_saida = "#dc3545"
        cor_saldo = theme.get('accent_color', '#17a2b8')
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: {cor_fundo_body}; color: {cor_titulo_principal}; margin: 0; padding: 0; }}
                .container {{ padding: 25px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .header h2 {{ margin: 0; font-size: 24px; }}
                .header p {{ margin: 5px; color: {cor_subtitulo}; font-size: 14px; }}
                .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin-bottom: 35px; }}
                .kpi-card {{ background-color: {cor_fundo_card}; border: 1px solid {cor_borda}; border-left: 5px solid {cor_saldo}; border-radius: 8px; padding: 20px; text-align: left; }}
                .kpi-card .label {{ font-size: 12px; color: {cor_titulo_kpi}; text-transform: uppercase; margin-bottom: 8px; font-weight: bold; }}
                .kpi-card .value {{ font-size: 26px; font-weight: bold; color: {cor_valor_kpi}; }}
                .kpi-card .sub-value {{ font-size: 11px; color: {cor_subtitulo}; margin-top: 5px; }}
                .section-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 30px; }}
                .section h3 {{ color: {cor_titulo_principal}; border-bottom: 2px solid {cor_borda}; padding-bottom: 8px; margin-top: 0; }}
                ol, ul {{ padding-left: 20px; }}
                li {{ margin-bottom: 10px; color: {cor_subtitulo}; }}
                li b {{ color: {cor_titulo_principal}; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Resumo Financeiro</h2>
                    <p>Período de {QDate.fromString(data_inicio, 'yyyy-MM-dd').toString('dd/MM/yyyy')} a {QDate.fromString(data_fim, 'yyyy-MM-dd').toString('dd/MM/yyyy')}</p>
                </div>

                <div class="kpi-grid">
                    <div class="kpi-card" style="border-left-color: {cor_saldo};">
                        <div class="label">Faturamento Bruto (Vendas)</div>
                        <div class="value">R$ {dados.get('faturamento_bruto', 0):.2f}</div>
                    </div>
                    <div class="kpi-card" style="border-left-color: {cor_entrada};">
                        <div class="label">Total de Entradas</div>
                        <div class="value" style="color: {cor_entrada};">R$ {dados.get('total_entradas', 0):.2f}</div>
                        <div class="sub-value">
                            (Vendas Líquidas: R$ {dados.get('faturamento_liquido', 0):.2f} + Outras: R$ {dados.get('outras_entradas', 0):.2f})
                        </div>
                    </div>
                    <div class="kpi-card" style="border-left-color: {cor_saida};">
                        <div class="label">Total de Saídas</div>
                        <div class="value" style="color: {cor_saida};">R$ {dados.get('total_saidas', 0):.2f}</div>
                    </div>
                     <div class="kpi-card" style="border-left-color: {cor_saldo};">
                        <div class="label">Saldo Final do Período</div>
                        <div class="value">R$ {dados.get('saldo_periodo', 0):.2f}</div>
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

    # No arquivo ui/caixa_window.py
# Encontre o método abrir_dialogo_exportacao e substitua-o por este

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
            # Pega as informações e a logo para passar para o template
            company_info = self.db.obter_informacoes_empresa()
            
            # --- INÍCIO DA CORREÇÃO ---
            # Trocamos .value() por .get_value() para usar o método correto da sua classe Settings
            custom_logo_path = self.settings.get_value("custom_logo_path", "")
            # --- FIM DA CORREÇÃO ---

            self.exportar_relatorio_pdf(data_inicio, data_fim, dados, caminho_arquivo, company_info, custom_logo_path)
            
    def exportar_relatorio_pdf(self, data_inicio, data_fim, dados, file_path, company_info, custom_logo_path):
        """
        Gera o conteúdo para o PDF financeiro usando os dados detalhados e o template padrão.
        """
        styles = getSampleStyleSheet()
        normal_style_right = ParagraphStyle(name='NormalRight', parent=styles['Normal'], alignment=TA_RIGHT)
        elementos = []
        
        elementos.append(Paragraph("Relatório Financeiro Detalhado", styles['h1']))
        elementos.append(Paragraph(f"Período de Análise: {QDate.fromString(data_inicio, 'yyyy-MM-dd').toString('dd/MM/yyyy')} a {QDate.fromString(data_fim, 'yyyy-MM-dd').toString('dd/MM/yyyy')}", styles['Normal']))
        elementos.append(Spacer(1, 0.8 * cm))
        
        left_margin, right_margin = 2*cm, 2*cm
        doc_width = A4[0] - left_margin - right_margin

        # Cria um parágrafo complexo para o KPI de Entradas
        entradas_paragraph_text = f"""
            <font color='green' size='14'><b>R$ {dados.get('total_entradas', 0):.2f}</b></font><br/>
            <font size='7' color='#36454F'>
                (Vendas líq.: {dados.get('faturamento_liquido', 0):.2f} + Outras: {dados.get('outras_entradas', 0):.2f})
            </font>
        """
        entradas_paragraph = Paragraph(entradas_paragraph_text, styles['Normal'])

        kpi_data = [
            {'label': 'FATURAMENTO BRUTO', 'value': f"R$ {dados.get('faturamento_bruto', 0):.2f}"},
            {'label': 'TOTAL ENTRADAS', 'value': entradas_paragraph},
            {'label': 'TOTAL SAÍDAS', 'value': f"<font color='red'>R$ {dados.get('total_saidas', 0):.2f}</font>"},
            {'label': 'SALDO DO PERÍODO', 'value': f"R$ {dados.get('saldo_periodo', 0):.2f}"}
        ]
        elementos.append(self._criar_kpi_boxes(kpi_data, doc_width))
        elementos.append(Spacer(1, 1*cm))

        elementos.append(Paragraph("Vendas Realizadas no Período", styles['h2']))
        vendas_data = [['ID', 'Data/Hora', 'Cliente', 'Valor', 'Desconto', 'Pagamento']]
        for v in dados.get('vendas', []):
            vendas_data.append([
                v['id'], v['data_hora'].split('.')[0], Paragraph(v['cliente'], styles['Normal']),
                Paragraph(f"R$ {v['valor_total']:.2f}", normal_style_right),
                Paragraph(f"R$ {v['desconto']:.2f}", normal_style_right),
                v['forma_pagamento']
            ])
            
        tabela_vendas = Table(vendas_data, colWidths=[1.5*cm, 3.5*cm, 4*cm, 2.5*cm, 2.5*cm, 3.5*cm], repeatRows=1)
        tabela_vendas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('ALIGN', (2, 1), (2, -1), 'LEFT'),
        ]))
        elementos.append(tabela_vendas)
        elementos.append(Spacer(1, 1*cm))
        
        elementos.append(Paragraph("Movimentações Manuais do Caixa", styles['h2']))
        mov_data = [['ID', 'Data/Hora', 'Tipo', 'Descrição', 'Valor']]
        # Filtra para não incluir vendas, que já estão na tabela acima
        movimentos_manuais = [m for m in dados.get('movimentos', []) if m.get('tipo_referencia') != 'Venda']
        for m in movimentos_manuais:
            valor_p = Paragraph(f"R$ {m['valor']:.2f}", normal_style_right)
            mov_data.append([
                m['id'], m['data_hora'].split('.')[0], m['tipo'], Paragraph(m['descricao'], styles['Normal']), valor_p
            ])
            
        tabela_mov = Table(mov_data, colWidths=[1.5*cm, 3.5*cm, 2*cm, 7*cm, 3.5*cm], repeatRows=1)
        style_mov = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#C0504D")), ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'), ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12), ('ALIGN', (3, 1), (3, -1), 'LEFT'),
        ])
        for i, row in enumerate(mov_data):
            if i > 0:
                cor = colors.green if row[2] == 'Entrada' else colors.red
                style_mov.add('TEXTCOLOR', (0, i), (-1, i), cor)
        tabela_mov.setStyle(style_mov)
        elementos.append(tabela_mov)

        self._gerar_pdf_com_template(file_path, "Relatório Financeiro", elementos, company_info, custom_logo_path)


    # COLE ESTE NOVO MÉTODO COMPLETO DENTRO DA CLASSE CaixaWindow

    def _buscar_dados_relatorio(self, data_inicio, data_fim):
        """
        Busca e consolida todos os dados necessários para os relatórios financeiros
        diretamente da UI, garantindo que os dados sejam consistentes com o Dashboard.
        """
        try:
            if not self.db.ensure_connection():
                raise Exception("Sem conexão com o banco de dados.")
                
            cursor = self.db.conn.cursor()

            # 1. Buscar todas as vendas no período
            cursor.execute("""
                SELECT
                    v.id,
                    v.data_hora,
                    COALESCE(c.nome, 'Cliente Não Identificado') as cliente,
                    v.valor_total,
                    v.desconto,
                    v.forma_pagamento
                FROM vendas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE date(v.data_hora, 'localtime') BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            vendas = [dict(row) for row in cursor.fetchall()]
            venda_ids = tuple(v['id'] for v in vendas) if vendas else ()

            # 2. Buscar todos os movimentos de caixa no período
            cursor.execute("""
                SELECT * FROM movimentos_caixa
                WHERE date(data_hora, 'localtime') BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            movimentos = [dict(row) for row in cursor.fetchall()]

            # 3. Calcular totais e agregações
            total_entradas = sum(m['valor'] for m in movimentos if m['tipo'] == 'Entrada')
            total_saidas = sum(m['valor'] for m in movimentos if m['tipo'] == 'Saída')
            valor_vendas = sum(v['valor_total'] for v in vendas)
            saldo_periodo = total_entradas - total_saidas
            valor_medio_venda = valor_vendas / len(vendas) if vendas else 0

            # 4. Top produtos e pagamentos (apenas se houver vendas)
            produtos_mais_vendidos = []
            pagamentos = defaultdict(float)
            if venda_ids:
                query_in_ids = f"IN {venda_ids}" if len(venda_ids) > 1 else f"= {venda_ids[0]}"
                cursor.execute(f"""
                    SELECT p.nome, SUM(i.quantidade) as quantidade, SUM(i.subtotal) as valor_total
                    FROM itens_venda i
                    JOIN produtos p ON i.produto_id = p.id
                    WHERE i.venda_id {query_in_ids}
                    GROUP BY p.id, p.nome ORDER BY valor_total DESC LIMIT 5
                """)
                produtos_mais_vendidos = [dict(row) for row in cursor.fetchall()]
                
                for venda in vendas:
                    pagamentos[venda['forma_pagamento']] += venda['valor_total']

            return {
                'vendas': vendas,
                'movimentos': movimentos,
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'valor_vendas': valor_vendas,
                'saldo_periodo': saldo_periodo,
                'valor_medio_venda': valor_medio_venda,
                'produtos_mais_vendidos': produtos_mais_vendidos,
                'pagamentos': dict(pagamentos) # Converte de volta para um dict normal
            }
        except Exception as e:
            print(f"Erro ao buscar dados para relatório: {e}")
            QMessageBox.critical(self, "Erro de Banco de Dados", f"Não foi possível buscar os dados do relatório: {e}")
            return None

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

        # O campo de quantidade continua sendo QDoubleSpinBox para flexibilidade,
        # mas vamos controlar suas propriedades (decimais, mínimo) dinamicamente.
        self.spin_quantidade = QDoubleSpinBox()
        self.spin_quantidade.setSingleStep(1) # Padrão para pular de 1 em 1
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

        # Inicia com a embalagem selecionada, se houver estoque
        if self.produto.get('quantidade', 0) > 0:
            self.radio_embalagem.setChecked(True)
        else:
            self.radio_unidade.setChecked(True)

    def update_info(self):
        if self.radio_embalagem.isChecked():
            # Configuração para Venda de Embalagem (Inteiros)
            self.spin_quantidade.setDecimals(0)
            self.spin_quantidade.setMinimum(1)
            self.spin_quantidade.setValue(1)
            
            self.lbl_info_preco.setText(f"R$ {self.produto['preco_venda']:.2f}")
            
            estoque_embalagem = int(self.produto.get('quantidade', 0))
            self.lbl_info_estoque.setText(f"{estoque_embalagem} embalagens")
            self.spin_quantidade.setMaximum(estoque_embalagem)
        else:
            # --- INÍCIO DA CORREÇÃO ---
            # Configuração para Venda de Unidade (Inteiros)
            self.spin_quantidade.setDecimals(0) 
            self.spin_quantidade.setMinimum(1)
            self.spin_quantidade.setValue(1)
            
            self.lbl_info_preco.setText(f"R$ {self.produto['preco_unitario_fracao']:.2f}")
            
            # Exibe o estoque fracionado como um número inteiro
            estoque_disponivel = int(self.produto.get('estoque_fracionado', 0))
            self.lbl_info_estoque.setText(f"{estoque_disponivel} {self.produto['unidade_medida']}")
            self.spin_quantidade.setMaximum(estoque_disponivel)
            # --- FIM DA CORREÇÃO ---

    def confirmar(self):
        quantidade = self.spin_quantidade.value()
        
        # A validação agora considera o máximo configurado dinamicamente
        if quantidade <= 0 or quantidade > self.spin_quantidade.maximum():
            QMessageBox.warning(self, "Estoque ou Quantidade Inválida", "A quantidade solicitada é inválida ou excede o estoque disponível.")
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


# Adicione esta nova classe ao seu arquivo, pode ser antes da classe CaixaWindow
class DialogNovoMovimento(ThemedDialog):
    def __init__(self, parent, tipo, theme_colors):
        super().__init__(parent, f"Nova {tipo}", theme_colors)
        self.setMinimumWidth(450)

        # --- UI WIDGETS ---
        form_layout = QFormLayout()
        self.edit_descricao = QLineEdit()
        self.spin_valor = QDoubleSpinBox()
        self.spin_valor.setPrefix("R$ ")
        self.spin_valor.setMaximum(999999.99)
        self.spin_valor.setDecimals(2)
        
        self.cb_forma_pagamento = QComboBox()
        self.cb_forma_pagamento.addItems(["Dinheiro", "Cartão de Crédito", "Cartão de Débito", "PIX", "Outro"])

        group_destino = QGroupBox("Natureza da Movimentação")
        group_destino_layout = QVBoxLayout(group_destino)
        self.radio_operacional = QRadioButton("Operacional (afeta o resultado/lucro)")
        self.radio_capital = QRadioButton("Capital/Não Operacional (não afeta o resultado)")
        self.radio_operacional.setChecked(True)
        self.radio_operacional.setToolTip("Use para despesas (aluguel, salários) ou outras receitas.")
        self.radio_capital.setToolTip("Use para aportes de sócio, retiradas (sangria) ou empréstimos.")
        group_destino_layout.addWidget(self.radio_operacional)
        group_destino_layout.addWidget(self.radio_capital)

        self.text_obs = QTextEdit()
        self.text_obs.setMaximumHeight(80)

        form_layout.addRow("Descrição:", self.edit_descricao)
        form_layout.addRow("Valor:", self.spin_valor)
        form_layout.addRow("Forma de Pagamento:", self.cb_forma_pagamento)
        form_layout.addRow(group_destino)
        form_layout.addRow("Observação:", self.text_obs)
        self.content_layout.addLayout(form_layout)

        # --- BOTÕES ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.setObjectName("secondaryButton")
        self.confirmar_btn = QPushButton(f"Confirmar {tipo}")
        self.confirmar_btn.setObjectName("primaryButton" if tipo == "Entrada" else "dangerButton")
        
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.confirmar_btn)
        self.content_layout.addLayout(button_layout)
        
        self.apply_movimento_styles(tipo)

    def apply_movimento_styles(self, tipo):
        theme = self.theme_colors
        success_color = "#28a745"
        danger_color = "#dc3545"
        
        style = f"""
            QGroupBox, QLabel, QRadioButton {{ color: {theme.get('text_color')}; }}
            QLineEdit, QDoubleSpinBox, QComboBox, QTextEdit {{
                background-color: {theme.get('surface_color')};
                color: {theme.get('text_color')};
                border: 1px solid {theme.get('border_color')};
                border-radius: 4px; padding: 6px;
            }}
            #primaryButton {{ background-color: {success_color}; color: white; border: none; }}
            #dangerButton {{ background-color: {danger_color}; color: white; border: none; }}
            #secondaryButton {{ background-color: transparent; color: {theme.get('text_color')}; border: 1px solid {theme.get('border_color')}; }}
        """
        self.setStyleSheet(self.styleSheet() + style)
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', theme.get('text_color')))
        self.confirmar_btn.setIcon(IconManager.get_icon('check' if tipo == "Entrada" else 'send', 'white'))

    def get_data(self):
        return {
            "descricao": self.edit_descricao.text().strip(),
            "valor": self.spin_valor.value(),
            "forma_pagamento": self.cb_forma_pagamento.currentText(),
            "observacao": self.text_obs.toPlainText(),
            "natureza": "Operacional" if self.radio_operacional.isChecked() else "Capital"
        }

# ================================================================= #
#       NOVA CLASSE: DialogVendaFracionada                          #
# ================================================================= #
class DialogVendaFracionada(ThemedDialog):
    def __init__(self, parent, produto, theme_colors):
        super().__init__(parent, "Opção de Venda", theme_colors)
        self.produto = produto
        self.sale_details = None
        self.setFixedWidth(400)
        
        # UI
        form_layout = QFormLayout()
        titulo = QLabel(f"<b>{produto['nome']}</b>"); titulo.setAlignment(Qt.AlignCenter)
        self.content_layout.addWidget(titulo)
        self.radio_embalagem = QRadioButton("Vender Embalagem Inteira")
        self.radio_unidade = QRadioButton("Vender Unidade Avulsa")
        self.radio_embalagem.toggled.connect(self.update_info)
        btn_group_layout = QHBoxLayout(); btn_group_layout.addWidget(self.radio_embalagem); btn_group_layout.addWidget(self.radio_unidade)
        form_layout.addRow("Tipo de Venda:", btn_group_layout)
        self.lbl_info_preco = QLabel(); self.lbl_info_estoque = QLabel()
        form_layout.addRow("Preço Unitário:", self.lbl_info_preco)
        form_layout.addRow("Estoque Disponível:", self.lbl_info_estoque)
        self.spin_quantidade = QDoubleSpinBox(); self.spin_quantidade.setSingleStep(1)
        form_layout.addRow("Quantidade:", self.spin_quantidade)
        self.content_layout.addLayout(form_layout)
        
        # Botões
        button_box = QHBoxLayout()
        self.confirmar_btn = QPushButton("Confirmar"); self.confirmar_btn.setObjectName("primaryButton"); self.confirmar_btn.clicked.connect(self.confirmar)
        cancelar_btn = QPushButton("Cancelar"); cancelar_btn.setObjectName("secondaryButton"); cancelar_btn.clicked.connect(self.reject)
        button_box.addStretch(); button_box.addWidget(cancelar_btn); button_box.addWidget(self.confirmar_btn)
        self.content_layout.addLayout(button_box)

        if self.produto.get('quantidade', 0) > 0: self.radio_embalagem.setChecked(True)
        else: self.radio_unidade.setChecked(True)
        
        self.apply_styles()

    def apply_styles(self):
        theme = self.theme_colors
        self.setStyleSheet(self.styleSheet() + f"""
            QLabel, QRadioButton {{ color: {theme.get('text_color')}; }}
            QDoubleSpinBox {{ background-color: {theme.get('surface_color')}; color: {theme.get('text_color')}; border: 1px solid {theme.get('border_color')}; padding: 6px; border-radius: 4px; }}
            #primaryButton {{ background-color: {theme.get('accent_color')}; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; }}
            #secondaryButton {{ background-color: transparent; color: {theme.get('text_color')}; border: 1px solid {theme.get('border_color')}; padding: 8px 16px; border-radius: 6px; font-weight: bold; }}
        """)

    def update_info(self):
        if self.radio_embalagem.isChecked():
            self.spin_quantidade.setDecimals(0); self.spin_quantidade.setMinimum(1); self.spin_quantidade.setValue(1)
            self.lbl_info_preco.setText(f"R$ {self.produto['preco_venda']:.2f}")
            estoque_embalagem = int(self.produto.get('quantidade', 0))
            self.lbl_info_estoque.setText(f"{estoque_embalagem} embalagens"); self.spin_quantidade.setMaximum(estoque_embalagem)
        else:
            self.spin_quantidade.setDecimals(0); self.spin_quantidade.setMinimum(1); self.spin_quantidade.setValue(1)
            self.lbl_info_preco.setText(f"R$ {self.produto['preco_unitario_fracao']:.2f}")
            estoque_disponivel = int(self.produto.get('estoque_fracionado', 0))
            self.lbl_info_estoque.setText(f"{estoque_disponivel} {self.produto['unidade_medida']}"); self.spin_quantidade.setMaximum(estoque_disponivel)

    def confirmar(self):
        if self.spin_quantidade.value() <= 0 or self.spin_quantidade.value() > self.spin_quantidade.maximum():
            AlertDialog(self, "Estoque Inválido", "A quantidade excede o estoque disponível.", 'warning', self.theme_colors).exec_()
            return
        is_embalagem = self.radio_embalagem.isChecked()
        self.sale_details = {
            "quantidade": self.spin_quantidade.value(),
            "preco_unitario": self.produto['preco_venda'] if is_embalagem else self.produto['preco_unitario_fracao'],
            "is_embalagem": is_embalagem,
            "produto_nome": f"{self.produto['nome']} ({'emb.' if is_embalagem else self.produto['unidade_medida']})"
        }
        self.accept()

    def get_sale_details(self): return self.sale_details

# Adicione esta classe ao seu arquivo ui/caixa_window.py

class DialogFinalizarVenda(ThemedDialog):
    def __init__(self, parent, total_venda, taxa_debito, taxa_credito, theme_colors):
        super().__init__(parent, "Finalizar Venda", theme_colors)
        self.total_venda_bruta = total_venda
        self.setMinimumWidth(550)

        self._setup_ui(taxa_debito, taxa_credito)
        self.apply_styles()
        self._connect_signals()
        self._update_ui()

    def _setup_ui(self, taxa_debito, taxa_credito):
        # --- SEÇÃO 1: FORMULÁRIO PRINCIPAL ---
        form_layout = QFormLayout()
        self.lbl_total_venda_bruta = QLabel(f"R$ {self.total_venda_bruta:.2f}")
        self.spin_desconto = QDoubleSpinBox(); self.spin_desconto.setPrefix("R$ "); self.spin_desconto.setMaximum(self.total_venda_bruta)
        self.cb_forma_pagamento = QComboBox(); self.cb_forma_pagamento.addItems(["Dinheiro", "Cartão de Débito", "Cartão de Crédito", "PIX", "Boleto"])
        form_layout.addRow("Total dos Itens:", self.lbl_total_venda_bruta)
        form_layout.addRow("Desconto:", self.spin_desconto)
        form_layout.addRow("Forma de Pagamento:", self.cb_forma_pagamento)
        self.content_layout.addLayout(form_layout)

        # --- SEÇÃO 2: TAXAS (COMEÇA OCULTO) ---
        self.group_taxas = QGroupBox("Taxas da Maquininha")
        group_taxas_layout = QFormLayout(self.group_taxas)
        self.spin_taxa_debito = QDoubleSpinBox(); self.spin_taxa_debito.setSuffix(" %"); self.spin_taxa_debito.setValue(taxa_debito)
        self.spin_taxa_credito = QDoubleSpinBox(); self.spin_taxa_credito.setSuffix(" %"); self.spin_taxa_credito.setValue(taxa_credito)
        self.chk_salvar_taxas = QCheckBox("Lembrar taxas para próximas vendas"); self.chk_salvar_taxas.setChecked(True)
        group_taxas_layout.addRow("Taxa Débito:", self.spin_taxa_debito)
        group_taxas_layout.addRow("Taxa Crédito:", self.spin_taxa_credito)
        group_taxas_layout.addRow(self.chk_salvar_taxas)
        self.content_layout.addWidget(self.group_taxas)

        # --- SEÇÃO 3: CAMPOS CONDICIONAIS ---
        form_layout_2 = QFormLayout()
        self.lbl_valor_recebido_text = QLabel("Valor Recebido:")
        self.spin_valor_recebido = QDoubleSpinBox(); self.spin_valor_recebido.setPrefix("R$ "); self.spin_valor_recebido.setMaximum(999999.99)
        
        # ================================================================= #
        #       CORREÇÃO APLICADA AQUI                                      #
        # ================================================================= #
        # Define o valor inicial do campo "Valor Recebido" como o total da venda.
        self.spin_valor_recebido.setValue(self.total_venda_bruta)

        form_layout_2.addRow(self.lbl_valor_recebido_text, self.spin_valor_recebido)
        self.lbl_troco_text = QLabel("Troco:"); self.lbl_troco = QLabel("R$ 0,00"); self.lbl_troco.setObjectName("trocoLabel")
        form_layout_2.addRow(self.lbl_troco_text, self.lbl_troco)
        self.spin_parcelas = QSpinBox(); self.spin_parcelas.setMinimum(1); self.spin_parcelas.setMaximum(12)
        self.lbl_parcelas = QLabel("Parcelas:")
        form_layout_2.addRow(self.lbl_parcelas, self.spin_parcelas)
        self.text_observacao = QTextEdit(); self.text_observacao.setMaximumHeight(80)
        form_layout_2.addRow("Observação:", self.text_observacao)
        self.content_layout.addLayout(form_layout_2)

        # --- SEÇÃO 4: CARDS DE TOTAIS ---
        cards_layout = QHBoxLayout()
        card_cliente = QFrame(); card_cliente.setObjectName("card"); card_cliente_layout = QVBoxLayout(card_cliente)
        lbl_cliente_title = QLabel("Cliente Paga"); lbl_cliente_title.setObjectName("cardTitle")
        self.lbl_total_cliente = QLabel(); self.lbl_total_cliente.setObjectName("totalClienteLabel")
        card_cliente_layout.addWidget(lbl_cliente_title); card_cliente_layout.addWidget(self.lbl_total_cliente)
        card_loja = QFrame(); card_loja.setObjectName("card"); card_loja_layout = QVBoxLayout(card_loja)
        lbl_loja_title = QLabel("Você Recebe"); lbl_loja_title.setObjectName("cardTitle")
        self.lbl_total_receber = QLabel(); self.lbl_total_receber.setObjectName("totalLojaLabel")
        card_loja_layout.addWidget(lbl_loja_title); card_loja_layout.addWidget(self.lbl_total_receber)
        cards_layout.addWidget(card_cliente); cards_layout.addWidget(card_loja)
        self.content_layout.addLayout(cards_layout)

        # --- SEÇÃO 5: BOTÕES FINAIS ---
        button_layout = QHBoxLayout()
        self.confirmar_btn = QPushButton("Confirmar Venda"); self.confirmar_btn.setObjectName("primaryButton")
        self.confirmar_btn.clicked.connect(self.accept)
        self.cancelar_btn = QPushButton("Cancelar"); self.cancelar_btn.setObjectName("secondaryButton")
        self.cancelar_btn.clicked.connect(self.reject)
        button_layout.addStretch(); button_layout.addWidget(self.cancelar_btn); button_layout.addWidget(self.confirmar_btn)
        self.content_layout.addLayout(button_layout)

    def _connect_signals(self):
        self.spin_desconto.valueChanged.connect(self._update_ui)
        self.spin_taxa_debito.valueChanged.connect(self._update_ui)
        self.spin_taxa_credito.valueChanged.connect(self._update_ui)
        self.spin_valor_recebido.valueChanged.connect(self._update_ui)
        self.cb_forma_pagamento.currentIndexChanged.connect(self._update_ui)

    def _update_ui(self):
        desconto = self.spin_desconto.value()
        total_cliente_paga = max(0, self.total_venda_bruta - desconto)
        forma_pgto = self.cb_forma_pagamento.currentText()
        taxa = self.spin_taxa_debito.value() if forma_pgto == "Cartão de Débito" else self.spin_taxa_credito.value() if forma_pgto == "Cartão de Crédito" else 0
        total_loja_recebe = total_cliente_paga * (1 - taxa / 100.0)

        self.lbl_total_cliente.setText(f"R$ {total_cliente_paga:.2f}")
        self.lbl_total_receber.setText(f"R$ {total_loja_recebe:.2f}")
        
        is_dinheiro = forma_pgto == "Dinheiro"
        self.lbl_valor_recebido_text.setVisible(is_dinheiro); self.spin_valor_recebido.setVisible(is_dinheiro)
        self.lbl_troco_text.setVisible(is_dinheiro); self.lbl_troco.setVisible(is_dinheiro)
        if is_dinheiro:
            troco = max(0, self.spin_valor_recebido.value() - total_cliente_paga)
            self.lbl_troco.setText(f"R$ {troco:.2f}")
        
        self.group_taxas.setVisible(forma_pgto in ["Cartão de Crédito", "Cartão de Débito"])
        self.lbl_parcelas.setVisible(forma_pgto == "Cartão de Crédito"); self.spin_parcelas.setVisible(forma_pgto == "Cartão de Crédito")

    def apply_styles(self):
        theme = self.theme_colors
        self.setStyleSheet(self.styleSheet() + f"""
            QLabel, QRadioButton, QCheckBox, QGroupBox {{ color: {theme.get('text_color')}; }}
            QLineEdit, QComboBox, QDoubleSpinBox, QSpinBox, QTextEdit {{
                background-color: {theme.get('surface_color')}; color: {theme.get('text_color')};
                border: 1px solid {theme.get('border_color')}; border-radius: 4px; padding: 6px;
            }}
            #card {{ background-color: {theme.get('surface_color')}; border: 1px solid {theme.get('border_color')}; border-radius: 6px; }}
            #cardTitle {{ color: {theme.get('text_secondary')}; font-size: 10pt; text-align: center; }}
            #totalClienteLabel {{ color: {theme.get('accent_color')}; font-size: 18px; font-weight: bold; text-align: center; }}
            #totalLojaLabel {{ color: #28a745; font-size: 18px; font-weight: bold; text-align: center; }}
            #trocoLabel {{ font-size: 14px; font-weight: bold; color: #FF5722; }}
            #primaryButton {{ background-color: #28a745; color: white; border: none; padding: 10px 20px; font-weight: bold; border-radius: 6px; }}
            #secondaryButton {{ background-color: transparent; color: {theme.get('text_color')}; border: 1px solid {theme.get('border_color')}; padding: 10px 20px; font-weight: bold; border-radius: 6px; }}
        """)

    def get_data(self):
        return {
            "desconto": self.spin_desconto.value(),
            "forma_pagamento": self.cb_forma_pagamento.currentText(),
            "taxa_debito": self.spin_taxa_debito.value(),
            "taxa_credito": self.spin_taxa_credito.value(),
            "salvar_taxas": self.chk_salvar_taxas.isChecked(),
            "valor_recebido": self.spin_valor_recebido.value(),
            "parcelas": self.spin_parcelas.value(),
            "observacao": self.text_observacao.toPlainText()
        }
# Adicione esta classe ao seu arquivo ui/caixa_window.py

class DialogAdicionarCliente(ThemedDialog):
    def __init__(self, parent, theme_colors):
        super().__init__(parent, "Adicionar Novo Cliente", theme_colors)
        self.setMinimumWidth(400)
        self._setup_ui()
        self.apply_styles()

    def _setup_ui(self):
        form_layout = QFormLayout()
        self.edit_nome = QLineEdit()
        self.edit_data_nascimento = QDateEdit(calendarPopup=True, date=QDate.currentDate().addYears(-18)); self.edit_data_nascimento.setDisplayFormat("dd/MM/yyyy")
        self.edit_telefone = QLineEdit()
        self.edit_email = QLineEdit()
        self.edit_endereco = QLineEdit()
        
        form_layout.addRow("Nome:", self.edit_nome)
        form_layout.addRow("Data de Nascimento:", self.edit_data_nascimento)
        form_layout.addRow("Telefone:", self.edit_telefone)
        form_layout.addRow("Email:", self.edit_email)
        form_layout.addRow("Endereço:", self.edit_endereco)
        self.content_layout.addLayout(form_layout)
        
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar"); self.salvar_btn.setObjectName("primaryButton"); self.salvar_btn.clicked.connect(self.accept)
        self.cancelar_btn = QPushButton("Cancelar"); self.cancelar_btn.setObjectName("secondaryButton"); self.cancelar_btn.clicked.connect(self.reject)
        button_layout.addStretch(); button_layout.addWidget(self.cancelar_btn); button_layout.addWidget(self.salvar_btn)
        self.content_layout.addLayout(button_layout)

    def apply_styles(self):
        theme = self.theme_colors
        self.setStyleSheet(self.styleSheet() + f"""
            QLabel {{ color: {theme.get('text_color')}; }}
            QLineEdit, QDateEdit {{
                background-color: {theme.get('surface_color')}; color: {theme.get('text_color')};
                border: 1px solid {theme.get('border_color')}; border-radius: 4px; padding: 6px;
            }}
            #primaryButton {{ background-color: {theme.get('accent_color')}; color: white; border: none; padding: 8px 16px; border-radius: 6px; font-weight: bold; }}
            #secondaryButton {{ background-color: transparent; color: {theme.get('text_color')}; border: 1px solid {theme.get('border_color')}; padding: 8px 16px; border-radius: 6px; font-weight: bold; }}
        """)

    def get_data(self):
        return {
            "nome": self.edit_nome.text().strip(),
            "data_nascimento": self.edit_data_nascimento.date().toString("yyyy-MM-dd"),
            "telefone": self.edit_telefone.text().strip(),
            "email": self.edit_email.text().strip(),
            "endereco": self.edit_endereco.text().strip()
        }
    
class DialogAbrirCaixa(ThemedDialog):
    def __init__(self, parent, theme_colors):
        super().__init__(parent, "Abrir Caixa", theme_colors)
        self.setMinimumWidth(350)
        self._setup_ui()
        self.apply_styles()

    def _setup_ui(self):
        form_layout = QFormLayout()
        self.spin_saldo = QDoubleSpinBox()
        self.spin_saldo.setPrefix("R$ ")
        self.spin_saldo.setMaximum(999999.99)
        self.spin_saldo.setDecimals(2)
        
        self.text_obs = QTextEdit()
        self.text_obs.setMaximumHeight(80)
        
        form_layout.addRow("Saldo Inicial:", self.spin_saldo)
        form_layout.addRow("Observação:", self.text_obs)
        self.content_layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.confirmar_btn = QPushButton("Abrir Caixa")
        self.confirmar_btn.setObjectName("primaryButton")
        self.confirmar_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.confirmar_btn)
        self.content_layout.addLayout(button_layout)

    def apply_styles(self):
        theme = self.theme_colors
        self.setStyleSheet(self.styleSheet() + f"""
            QLabel {{ color: {theme.get('text_color')}; }}
            QDoubleSpinBox, QTextEdit {{
                background-color: {theme.get('surface_color')}; color: {theme.get('text_color')};
                border: 1px solid {theme.get('border_color')}; border-radius: 4px; padding: 6px;
            }}
            #primaryButton {{
                background-color: {theme.get('accent_color')}; color: white; border: none;
                padding: 10px 20px; font-weight: bold; border-radius: 6px;
            }}
        """)
        self.confirmar_btn.setIcon(IconManager.get_icon('unlock', 'white'))

    def get_data(self):
        return {
            "saldo_inicial": self.spin_saldo.value(),
            "observacao": self.text_obs.toPlainText()
        }


class DialogFecharCaixa(ThemedDialog):
    def __init__(self, parent, saldo_atual, theme_colors):
        super().__init__(parent, "Fechar Caixa", theme_colors)
        self.saldo_sistema = saldo_atual
        self.setMinimumWidth(400)
        self._setup_ui()
        self.apply_styles()
        self._update_diferenca()

    def _setup_ui(self):
        self.content_layout.addWidget(QLabel(f"Saldo do Sistema: R$ {self.saldo_sistema:.2f}"))
        
        form_layout = QFormLayout()
        self.spin_saldo_final = QDoubleSpinBox()
        self.spin_saldo_final.setPrefix("R$ ")
        self.spin_saldo_final.setMaximum(999999.99)
        self.spin_saldo_final.setValue(self.saldo_sistema)
        self.spin_saldo_final.setDecimals(2)
        
        self.lbl_diferenca = QLabel("Diferença: R$ 0,00")
        self.lbl_diferenca.setObjectName("diferencaLabel")
        
        self.text_obs_fechamento = QTextEdit()
        self.text_obs_fechamento.setMaximumHeight(80)
        
        form_layout.addRow("Saldo em Caixa:", self.spin_saldo_final)
        form_layout.addRow("", self.lbl_diferenca)
        form_layout.addRow("Observação:", self.text_obs_fechamento)
        self.content_layout.addLayout(form_layout)

        self.spin_saldo_final.valueChanged.connect(self._update_diferenca)
        
        button_layout = QHBoxLayout()
        self.confirmar_btn = QPushButton("Fechar Caixa")
        self.confirmar_btn.setObjectName("dangerButton")
        self.confirmar_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(self.confirmar_btn)
        self.content_layout.addLayout(button_layout)

    def _update_diferenca(self):
        saldo_informado = self.spin_saldo_final.value()
        diferenca = saldo_informado - self.saldo_sistema
        self.lbl_diferenca.setText(f"Diferença: R$ {diferenca:.2f}")
        if diferenca < 0:
            self.lbl_diferenca.setStyleSheet(f"color: {self.theme_colors.get('danger_color', '#dc3545')}; font-weight: bold;")
        elif diferenca > 0:
            self.lbl_diferenca.setStyleSheet(f"color: {self.theme_colors.get('success_color', '#28a745')}; font-weight: bold;")
        else:
            self.lbl_diferenca.setStyleSheet(f"color: {self.theme_colors.get('text_color', '#000')}; font-weight: normal;")

    def apply_styles(self):
        theme = self.theme_colors
        self.setStyleSheet(self.styleSheet() + f"""
            QLabel {{ color: {theme.get('text_color')}; }}
            #diferencaLabel {{ font-weight: bold; }}
            QDoubleSpinBox, QTextEdit {{
                background-color: {theme.get('surface_color')}; color: {theme.get('text_color')};
                border: 1px solid {theme.get('border_color')}; border-radius: 4px; padding: 6px;
            }}
            #dangerButton {{
                background-color: {theme.get('danger_color', '#dc3545')}; color: white; border: none;
                padding: 10px 20px; font-weight: bold; border-radius: 6px;
            }}
        """)
        self.confirmar_btn.setIcon(IconManager.get_icon('lock', 'white'))

    def get_data(self):
        return {
            "saldo_informado": self.spin_saldo_final.value(),
            "observacao": self.text_obs_fechamento.toPlainText()
        }