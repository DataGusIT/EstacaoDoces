from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QStackedWidget, QHBoxLayout, QFrame,
                            QAction, QMenu, QToolBar, QDialog, QFormLayout,
                            QComboBox, QSpinBox, QMessageBox, QStatusBar, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QCursor, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QDate, QSize, QByteArray, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QApplication

from ui.estoque_window import EstoqueWindow
from ui.fornecedor_window import FornecedorWindow
from ui.promocoes_window import PromocoesWindow
from ui.clientes_window import ClientesWindow
from ui.caixa_window import CaixaWindow
from ui.dashboard_window import DashboardWindow

class MainWindow(QMainWindow):
    def __init__(self, db, settings):
        super().__init__()
        self.db = db
        self.settings = settings
        self.menu_collapsed = True
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)  # Janela sem bordas
        self.initUI()
        self.check_promocoes_ativas()
        self.aplicar_tema()
    
    def initUI(self):
        # Configurar janela principal
        self.setWindowTitle("Sistema de Estoque")
        self.setGeometry(100, 100, 1200, 700)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # ===== CABEÇALHO UNIFICADO =====
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(40)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 0, 10, 0)
        header_layout.setSpacing(10)
        
        # Título da aplicação (à esquerda)
        app_icon = QLabel("📦")
        app_icon.setFont(QFont("Segoe UI", 14))
        app_icon.setObjectName("appIcon")
        
        app_title = QLabel("Sistema de Estoque")
        app_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        app_title.setObjectName("appTitle")
        
        # Menu principal
        menu_frame = QFrame()
        menu_frame.setObjectName("mainMenuFrame")
        menu_layout = QHBoxLayout(menu_frame)
        menu_layout.setContentsMargins(20, 0, 20, 0)
        menu_layout.setSpacing(20)
        
        # Botões de menu principais
        arquivo_btn = QPushButton("Arquivo")
        arquivo_btn.setObjectName("headerMenuButton")
        arquivo_btn.setCursor(Qt.PointingHandCursor)
        arquivo_menu = QMenu(self)
        
        config_action = QAction('Configurações', self)
        config_action.triggered.connect(self.abrir_configuracoes)
        arquivo_menu.addAction(config_action)
        arquivo_menu.addSeparator()
        sair_action = QAction('Sair', self)
        sair_action.triggered.connect(self.close)
        arquivo_menu.addAction(sair_action)
        arquivo_btn.setMenu(arquivo_menu)
        
        relatorios_btn = QPushButton("Relatórios")
        relatorios_btn.setObjectName("headerMenuButton")
        relatorios_btn.setCursor(Qt.PointingHandCursor)
        relatorios_menu = QMenu(self)
        
        estoque_baixo_action = QAction('Produtos com Estoque Baixo', self)
        estoque_baixo_action.triggered.connect(self.relatorio_estoque_baixo)
        relatorios_menu.addAction(estoque_baixo_action)
        
        vencimentos_action = QAction('Produtos a Vencer', self)
        vencimentos_action.triggered.connect(self.relatorio_vencimentos)
        relatorios_menu.addAction(vencimentos_action)
        
        promocoes_action = QAction('Promoções Ativas', self)
        promocoes_action.triggered.connect(self.relatorio_promocoes)
        relatorios_menu.addAction(promocoes_action)
        relatorios_btn.setMenu(relatorios_menu)
        
        ajuda_btn = QPushButton("Ajuda")
        ajuda_btn.setObjectName("headerMenuButton")
        ajuda_btn.setCursor(Qt.PointingHandCursor)
        ajuda_menu = QMenu(self)
        
        sobre_action = QAction('Sobre', self)
        sobre_action.triggered.connect(self.mostrar_sobre)
        ajuda_menu.addAction(sobre_action)
        ajuda_btn.setMenu(ajuda_menu)
        
        # Adicionar botões ao menu
        menu_layout.addWidget(arquivo_btn)
        menu_layout.addWidget(relatorios_btn)
        menu_layout.addWidget(ajuda_btn)
        
        # Adicionar stretch para separar os menus do restante
        header_layout.addWidget(app_icon)
        header_layout.addWidget(app_title)
        header_layout.addWidget(menu_frame)
        header_layout.addStretch()
        
        # Área de informações e controles à direita
        controls_frame = QFrame()
        controls_frame.setObjectName("headerControlsFrame")
        controls_layout = QHBoxLayout(controls_frame)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(15)
        
        # Botão de atualizar
        refresh_button = QPushButton("Atualizar")
        refresh_button.setObjectName("refreshButton")
        refresh_button.setCursor(Qt.PointingHandCursor)
        refresh_button.clicked.connect(self.atualizar_dados)
        
        # Separador visual
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("headerSeparator")
        
        # Botões de controle da janela
        window_controls_frame = QFrame()
        window_controls_frame.setObjectName("windowControls")
        window_layout = QHBoxLayout(window_controls_frame)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(8)
        
        minimize_btn = QPushButton("─")
        minimize_btn.setObjectName("minimizeButton")
        minimize_btn.setFixedSize(22, 22)
        minimize_btn.setCursor(Qt.PointingHandCursor)
        minimize_btn.clicked.connect(self.showMinimized)
        
        maximize_btn = QPushButton("□")
        maximize_btn.setObjectName("maximizeButton")
        maximize_btn.setFixedSize(22, 22)
        maximize_btn.setCursor(Qt.PointingHandCursor)
        maximize_btn.clicked.connect(self.toggle_maximize)
        
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        
        window_layout.addWidget(minimize_btn)
        window_layout.addWidget(maximize_btn)
        window_layout.addWidget(close_btn)
        
        # Adicionar elementos aos controles
        controls_layout.addWidget(refresh_button)
        controls_layout.addWidget(separator)
        controls_layout.addWidget(window_controls_frame)
        
        header_layout.addWidget(controls_frame)
        main_layout.addWidget(header_frame)
        
        # Separador abaixo do cabeçalho
        header_separator = QFrame()
        header_separator.setFrameShape(QFrame.HLine)
        header_separator.setFrameShadow(QFrame.Sunken)
        header_separator.setObjectName("headerBottomLine")
        main_layout.addWidget(header_separator)
        
        # ===== CONTEÚDO PRINCIPAL =====
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Container do menu lateral
        self.menu_container = QFrame()
        self.menu_container.setObjectName("menuContainer")
        menu_container_layout = QVBoxLayout(self.menu_container)
        menu_container_layout.setContentsMargins(0, 0, 0, 0)
        menu_container_layout.setSpacing(0)
        
        # Cabeçalho do menu com botão hambúrguer
        menu_header = QFrame()
        menu_header.setObjectName("menuHeader")
        menu_header.setFixedHeight(50)
        menu_header_layout = QHBoxLayout(menu_header)
        menu_header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Botão hambúrguer
        self.hamburger_btn = QPushButton("☰")
        self.hamburger_btn.setObjectName("hamburgerButton")
        self.hamburger_btn.setFixedSize(30, 30)
        self.hamburger_btn.setCursor(Qt.PointingHandCursor)
        self.hamburger_btn.clicked.connect(self.toggle_menu)
        
        menu_header_layout.addWidget(self.hamburger_btn)
        menu_header_layout.addStretch()
        
        # Menu lateral
        self.menu_widget = QFrame()
        self.menu_widget.setObjectName("menuLateral")
        menu_widget_layout = QVBoxLayout(self.menu_widget)
        menu_widget_layout.setSpacing(5)
        menu_widget_layout.setContentsMargins(10, 20, 10, 20)
        
        # Botões do menu
        self.btn_dashboard = self.criar_botao_menu("Dashboard", "🏠")
        self.btn_estoque = self.criar_botao_menu("Controle de Estoque", "📦")
        self.btn_fornecedor = self.criar_botao_menu("Fornecedores", "🚚")
        self.btn_promocoes = self.criar_botao_menu("Promoções", "🏷️")
        self.btn_clientes = self.criar_botao_menu("Clientes", "👥")
        self.btn_caixa = self.criar_botao_menu("Controle de Caixa", "💰")
        
        # Lista de botões para facilitar a manipulação
        self.menu_buttons = [
            self.btn_dashboard,
            self.btn_estoque,
            self.btn_fornecedor,
            self.btn_promocoes,
            self.btn_clientes,
            self.btn_caixa
        ]
        
        # Adicionar botões ao menu
        for btn in self.menu_buttons:
            menu_widget_layout.addWidget(btn)
        
        menu_widget_layout.addStretch()
        
        # Separador antes das configurações
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        separador.setObjectName("separator")
        menu_widget_layout.addWidget(separador)
        
        # Botão de configurações
        self.btn_config = self.criar_botao_menu("Configurações", "⚙️")
        self.btn_config.clicked.connect(self.abrir_configuracoes)
        menu_widget_layout.addWidget(self.btn_config)
        
        # Créditos no final do menu
        self.creditos = QLabel("© 2025")
        self.creditos.setAlignment(Qt.AlignCenter)
        self.creditos.setObjectName("creditos")
        menu_widget_layout.addWidget(self.creditos)
        
        # Adicionar cabeçalho e menu ao container
        menu_container_layout.addWidget(menu_header)
        menu_container_layout.addWidget(self.menu_widget)
        
        # Área de conteúdo
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho da área de conteúdo
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.page_title.setObjectName("pageTitle")
        content_container_layout.addWidget(self.page_title)
        
        # Separador no conteúdo
        content_separator = QFrame()
        content_separator.setFrameShape(QFrame.HLine)
        content_separator.setFrameShadow(QFrame.Sunken)
        content_separator.setObjectName("contentSeparator")
        content_container_layout.addWidget(content_separator)
        content_container_layout.addSpacing(10)
        
        # Stack para as páginas
        self.stack = QStackedWidget()
        content_container_layout.addWidget(self.stack)
        
        # Criar as páginas e adicioná-las ao stack
        self.estoque_page = EstoqueWindow(self.db)
        self.fornecedor_page = FornecedorWindow(self.db)
        self.promocoes_page = PromocoesWindow(self.db)
        self.clientes_page = ClientesWindow(self.db)
        self.caixa_page = CaixaWindow(self.db)
        self.dashboard_page = DashboardWindow(self.db)
        
        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.estoque_page)
        self.stack.addWidget(self.fornecedor_page)
        self.stack.addWidget(self.promocoes_page)
        self.stack.addWidget(self.clientes_page)
        self.stack.addWidget(self.caixa_page)
        
        # Conectar sinais dos botões
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_estoque.clicked.connect(lambda: self.switch_page(1))
        self.btn_fornecedor.clicked.connect(lambda: self.switch_page(2))
        self.btn_promocoes.clicked.connect(lambda: self.switch_page(3))
        self.btn_clientes.clicked.connect(lambda: self.switch_page(4))
        self.btn_caixa.clicked.connect(lambda: self.switch_page(5))
        
        # Adicionar elementos ao layout de conteúdo principal
        content_layout.addWidget(self.menu_container)
        content_layout.addWidget(content_container)
        
        # Adicionar frame de conteúdo ao layout principal
        main_layout.addWidget(content_frame)
        
        # Status bar simplificado na parte inferior
        self.statusBar = QStatusBar()
        self.statusBar.setObjectName("statusBar")
        self.statusBar.setMaximumHeight(25)
        self.statusBar.showMessage("Sistema pronto", 3000)
        
        # Configurar widget central
        self.setCentralWidget(central_widget)
        
        # Configurar estado inicial do menu (expandido)
        self.menu_container.setMinimumWidth(70)
        self.menu_container.setMaximumWidth(70)
        self.creditos.setText("©")

        for btn in self.menu_buttons + [self.btn_config]:
            if hasattr(btn, 'text_label'):
                btn.text_label.hide()
        
        # Permitir arrastar a janela pelo cabeçalho
        header_frame.mousePressEvent = self.start_window_drag
        header_frame.mouseMoveEvent = self.window_drag
        self.drag_position = None
    
    def criar_botao_menu(self, texto, icone=None):
        """Cria um botão estilizado para o menu lateral."""
        btn = QPushButton()
        btn.setObjectName("menuButton")
        btn.setMinimumHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        
        # Layout para o botão
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(15, 8, 15, 8)
        layout.setSpacing(10)
        
        # Ícone (emoji ou símbolo)
        if icone:
            icon_label = QLabel(icone)
            icon_label.setFont(QFont("Segoe UI", 16))
            icon_label.setFixedSize(24, 24)
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setObjectName("buttonIcon")
            layout.addWidget(icon_label)
            # Guardar referência ao ícone no botão
            btn.icon_label = icon_label
        
        # Texto
        text_label = QLabel(texto)
        text_label.setFont(QFont("Segoe UI", 11))
        text_label.setObjectName("buttonText")
        layout.addWidget(text_label)
        layout.addStretch()
        
        # Guardar referência ao texto no botão
        btn.text_label = text_label
        btn.full_text = texto
        
        return btn
    
    def toggle_menu(self):
        """Alterna entre menu expandido e recolhido."""
        if self.menu_collapsed:
            # Expandir menu
            self.menu_container.setMinimumWidth(250)
            self.menu_container.setMaximumWidth(250)
            self.creditos.setText("© 2025")
            
            # Mostrar texto dos botões
            for btn in self.menu_buttons + [self.btn_config]:
                if hasattr(btn, 'text_label'):
                    btn.text_label.show()
            
            self.menu_collapsed = False
        else:
            # Recolher menu
            self.menu_container.setMinimumWidth(70)
            self.menu_container.setMaximumWidth(70)
            self.creditos.setText("©")
            
            # Esconder texto dos botões, manter apenas ícones
            for btn in self.menu_buttons + [self.btn_config]:
                if hasattr(btn, 'text_label'):
                    btn.text_label.hide()
            
            self.menu_collapsed = True
    
    def switch_page(self, index):
        """Muda para a página especificada e atualiza a interface."""
        self.stack.setCurrentIndex(index)
        
        # Atualizar título da página
        titles = ["Dashboard", "Controle de Estoque", "Fornecedores", 
                 "Promoções", "Clientes", "Controle de Caixa"]
        
        self.page_title.setText(titles[index])
        
        # Atualizar status bar com a página atual
        self.statusBar.showMessage(f"Área: {titles[index]}", 3000)
        
        # Destacar botão ativo
        buttons = [self.btn_dashboard, self.btn_estoque, self.btn_fornecedor, 
                  self.btn_promocoes, self.btn_clientes, self.btn_caixa]
        
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setProperty("active", True)
            else:
                btn.setProperty("active", False)
            
            # Força a atualização do estilo
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()
    
    def toggle_maximize(self):
        """Alterna entre tela cheia e tamanho normal."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def start_window_drag(self, event):
        """Inicia a operação de arrastar a janela."""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def window_drag(self, event):
        """Realiza a operação de arrastar a janela."""
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    

    def aplicar_tema(self):
        """Aplica o tema atual a todos os componentes."""
        is_dark = self.settings.get_theme() == 'dark'
        
        # Cores do tema
        if is_dark:
            bg_color = "#1c1c1e"
            surface_color = "#2c2c2e" 
            menu_color = "#1c1c1e"
            text_color = "#ffffff"
            text_secondary = "#8e8e93"
            border_color = "#3a3a3c"
            button_hover = "#3a3a3c"
            accent_color = "#007AFF"
        else:
            bg_color = "#ffffff"
            surface_color = "#f2f2f7"
            menu_color = "#f9f9f9"
            text_color = "#000000"
            text_secondary = "#6d6d70"
            border_color = "#d1d1d6"
            button_hover = "#e5e5ea"
            accent_color = "#007AFF"
        
        # Aplicar stylesheet principal
        self.setStyleSheet(f"""
            /* Janela principal */
            QMainWindow {{
                background-color: {bg_color};
                color: {text_color};
            }}
            
            #centralWidget {{
                background-color: {bg_color};
            }}
            
            /* Menu bar */
            QMenuBar {{
                background-color: {surface_color};
                color: {text_color};
                border-bottom: 1px solid {border_color};
                padding: 4px;
            }}
            
            QMenuBar::item {{
                background: transparent;
                padding: 8px 12px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {button_hover};
            }}
            
            QMenu {{
                background-color: {surface_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 4px;
            }}
            
            QMenu::item {{
                padding: 8px 16px;
                border-radius: 4px;
            }}
            
            QMenu::item:selected {{
                background-color: {button_hover};
            }}
            
            QMenu::separator {{
                height: 1px;
                background-color: {border_color};
                margin: 4px 8px;
            }}
            
            /* Status bar */
            #statusBar {{
                background-color: {surface_color};
                color: {text_secondary};
                border-top: 1px solid {border_color};
                padding: 4px;
            }}
            
            /* Container do menu */
            #menuContainer {{
                background-color: {menu_color};
                border-right: 1px solid {border_color};
            }}
            
            #menuHeader {{
                background-color: {menu_color};
                border-bottom: 1px solid {border_color};
            }}
            
            /* Menu lateral */
            #menuLateral {{
                background-color: {menu_color};
            }}
            
            #appTitle {{
                color: {text_color};
            }}
            
            /* Botão hambúrguer */
            #hamburgerButton {{
                background-color: transparent;
                border: none;
                color: {text_color};
                font-size: 18px;
                font-weight: bold;
                border-radius: 6px;
                padding: 4px;
            }}
            
            #hamburgerButton:hover {{
                background-color: {button_hover};
            }}
            
            #hamburgerButton:pressed {{
                background-color: {border_color};
            }}
            
            /* Botões do menu */
            #menuButton {{
                background-color: transparent;
                border: none;
                text-align: left;
                padding: 8px;
                border-radius: 8px;
                color: {text_color};
            }}
            
            #menuButton:hover {{
                background-color: {button_hover};
            }}
            
            #menuButton[active="true"] {{
                background-color: {accent_color};
                color: white;
            }}
            
            #menuButton[active="true"] #buttonIcon,
            #menuButton[active="true"] #buttonText {{
                color: white;
            }}
            
            #buttonIcon {{
                color: {text_secondary};
            }}
            
            #buttonText {{
                color: {text_color};
            }}
            
            /* Separadores */
            #separator {{
                background-color: {border_color};
                border: none;
                max-height: 1px;
            }}
            
            /* Créditos */
            #creditos {{
                color: {text_secondary};
                font-size: 11px;
                padding: 8px;
            }}
            
            /* Área de conteúdo */
            #contentContainer {{
                background-color: {bg_color};
            }}
            
            #pageTitle {{
                color: {text_color};
                margin-bottom: 10px;
            }}
            
            #contentSeparator {{
                background-color: {border_color};
                border: none;
                max-height: 1px;
            }}
            
            /* Botões da toolbar */
            #toolbarButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                min-width: 80px;
            }}
            
            #toolbarButton:hover {{
                background-color: #0056b3;
            }}
            
            #toolbarButton:pressed {{
                background-color: #004085;
            }}
            
            /* Avatar e nome do usuário */
            #userAvatar {{
                background-color: {accent_color};
                color: white;
                border-radius: 15px;
                font-weight: bold;
            }}
            
            #userName {{
                color: {text_color};
                font-weight: 500;
            }}
        """)
        
        # Forçar atualização visual
        self.update()
        if hasattr(self, 'repaint'):
            self.repaint()

    def aplicar_tema_completo(self):
        """Aplica tema em todos os widgets, incluindo janela principal"""
        self.aplicar_tema()
    
    def abrir_configuracoes(self):
        """Abre a janela de configurações."""
        dialog = ConfigDialog(self.settings)
        if dialog.exec_() == QDialog.Accepted:
            # Aplicar as configurações imediatamente
            self.aplicar_tema()
            QMessageBox.information(self, "Configurações", 
                                  "As configurações foram salvas e aplicadas.")
    
    def atualizar_dados(self):
        """Atualiza os dados da página atual."""
        current_index = self.stack.currentIndex()
        
        pages = [self.dashboard_page, self.estoque_page, self.fornecedor_page,
                self.promocoes_page, self.clientes_page, self.caixa_page]
        
        if current_index < len(pages):
            pages[current_index].carregar_dados()
            self.statusBar.showMessage("Dados atualizados com sucesso!", 3000)
    
    def check_promocoes_ativas(self):
        """Verifica e exibe promoções ativas na barra de status."""
        promocoes_ativas = self.db.listar_promocoes_ativas()
        
        if promocoes_ativas:
            num_promocoes = len(promocoes_ativas)
            self.statusBar.showMessage(f"{num_promocoes} promoções ativas hoje ({QDate.currentDate().toString('dd/MM/yyyy')})")
    
    def relatorio_estoque_baixo(self):
        """Gera relatório de produtos com estoque baixo."""
        produtos = [p for p in self.db.listar_produtos() if p['quantidade'] < 10]
        
        if not produtos:
            QMessageBox.information(self, "Relatório", "Não há produtos com estoque baixo.")
            return
        
        msg = "Produtos com estoque baixo (menos de 10 unidades):\n\n"
        for produto in produtos:
            msg += f"• {produto['nome']} - Estoque: {produto['quantidade']} unidades\n"
        
        QMessageBox.information(self, "Relatório de Estoque Baixo", msg)
    
    def relatorio_vencimentos(self):
        """Gera relatório de produtos próximos ao vencimento."""
        produtos = self.db.verificar_produtos_vencendo(dias=30)
        
        if not produtos:
            QMessageBox.information(self, "Relatório", "Não há produtos próximos do vencimento nos próximos 30 dias.")
            return
        
        msg = "Produtos que vencerão nos próximos 30 dias:\n\n"
        for produto in produtos:
            msg += f"• {produto['nome']} - Vencimento: {produto['data_validade']}\n"
        
        QMessageBox.information(self, "Relatório de Vencimentos", msg)
    
    def relatorio_promocoes(self):
        """Gera relatório de promoções ativas."""
        promocoes = self.db.listar_promocoes_ativas()
        
        if not promocoes:
            QMessageBox.information(self, "Relatório", "Não há promoções ativas no momento.")
            return
        
        msg = "Promoções ativas:\n\n"
        for promocao in promocoes:
            economia = ((promocao['preco_antigo'] - promocao['preco_promocional']) / promocao['preco_antigo']) * 100
            msg += f"• {promocao['produto_nome']} - De R$ {promocao['preco_antigo']:.2f} por R$ {promocao['preco_promocional']:.2f} ({economia:.1f}% de desconto)\n"
            msg += f"  Válida até: {promocao['data_fim']}\n\n"
        
        QMessageBox.information(self, "Relatório de Promoções Ativas", msg)
    
    def mostrar_sobre(self):
        """Mostra informações sobre o sistema."""
        QMessageBox.about(self, "Sobre o Sistema", 
                         "Sistema de Estoque v1.0\n\n"
                         "Desenvolvido com Python e PyQt5\n\n"
                         "© 2025 - Todos os direitos reservados")
    
    def closeEvent(self, event):
        """Evento chamado quando a janela é fechada."""
        self.db.fechar()
        event.accept()

    def setup_for_user(self, usuario):
        """Configura a interface para o usuário logado"""
        try:
            if not hasattr(self, 'user_manager'):
                self.user_manager = UserManager(self, self.db)
            self.user_manager.setup_for_user(usuario)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao configurar usuário: {str(e)}")

    def add_user_menu(self):
        """Método de compatibilidade"""
        if hasattr(self, 'usuario'):
            self.setup_for_user(self.usuario)

    def ajustar_permissoes(self, tipo_usuario):
        """Método de compatibilidade"""
        if hasattr(self, 'user_manager'):
            self.user_manager.adjust_permissions()

    def abrir_perfil(self):
        """Abre perfil do usuário"""
        if hasattr(self, 'user_manager'):
            self.user_manager.open_profile()

    def alterar_senha(self):
        """Altera senha do usuário"""
        if hasattr(self, 'user_manager'):
            self.user_manager.change_password()

    def abrir_admin(self):
        """Abre painel administrativo"""
        if hasattr(self, 'user_manager'):
            self.user_manager.open_admin()

    def logout(self):
        """Realiza logout"""
        if hasattr(self, 'user_manager'):
            self.user_manager.logout()

class UserAvatarWidget(QWidget):
    """Widget responsável por exibir o avatar do usuário"""
    
    def __init__(self, usuario, size=32):
        super().__init__()
        self.usuario = usuario
        self.size = size
        self.setup_ui()
    
    def setup_ui(self):
        """Configura a interface do avatar"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Criar label para o avatar
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(self.size, self.size)
        
        # Gerar avatar
        self.create_avatar()
        
        layout.addWidget(self.avatar_label)
    
    def create_avatar(self):
        """Cria o avatar do usuário"""
        try:
            # Tentar carregar avatar do arquivo
            avatar_pixmap = QPixmap("assets/avatar.png")
            
            if not avatar_pixmap.isNull():
                self.create_circular_avatar(avatar_pixmap)
            else:
                self.create_initials_avatar()
                
        except Exception:
            self.create_initials_avatar()
    
    def create_circular_avatar(self, pixmap):
        """Cria um avatar circular a partir de uma imagem"""
        rounded_avatar = QPixmap(self.size, self.size)
        rounded_avatar.fill(Qt.transparent)
        
        painter = QPainter(rounded_avatar)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Criar caminho circular
        path = QPainterPath()
        path.addEllipse(0, 0, self.size, self.size)
        painter.setClipPath(path)
        
        # Redimensionar e desenhar
        scaled_pixmap = pixmap.scaled(
            self.size, self.size, 
            Qt.KeepAspectRatioByExpanding, 
            Qt.SmoothTransformation
        )
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()
        
        self.avatar_label.setPixmap(rounded_avatar)
    
    def create_initials_avatar(self):
        """Cria um avatar com as iniciais do usuário"""
        initials = self.get_user_initials()
        
        avatar_pixmap = QPixmap(self.size, self.size)
        avatar_pixmap.fill(Qt.transparent)
        
        painter = QPainter(avatar_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Desenhar círculo de fundo
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor("#0d6efd"))
        painter.drawEllipse(0, 0, self.size, self.size)
        
        # Adicionar iniciais
        painter.setPen(QColor("#ffffff"))
        font_size = max(8, self.size // 3)
        painter.setFont(QFont("Arial", font_size, QFont.Bold))
        painter.drawText(avatar_pixmap.rect(), Qt.AlignCenter, initials)
        painter.end()
        
        self.avatar_label.setPixmap(avatar_pixmap)
    
    def get_user_initials(self):
        """Obtém as iniciais do usuário"""
        try:
            nome_parts = self.usuario['nome'].split()
            initials = "".join([part[0].upper() for part in nome_parts if part])[:2]
            return initials if initials else "U"
        except (KeyError, IndexError, AttributeError):
            return "U"


class IconProvider:
    """Provedor de ícones SVG"""
    
    ICONS = {
        'chevron_down': """
            <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" 
                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
        """,
        'profile': """
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" 
                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                <circle cx="12" cy="7" r="4"></circle>
            </svg>
        """,
        'password': """
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" 
                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
            </svg>
        """,
        'admin': """
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" 
                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 20h9"></path>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
            </svg>
        """,
        'logout': """
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" 
                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                <polyline points="16 17 21 12 16 7"></polyline>
                <line x1="21" y1="12" x2="9" y2="12"></line>
            </svg>
        """
    }
    
    @classmethod
    def create_icon(cls, icon_name, size=16):
        """Cria um ícone a partir do SVG"""
        if icon_name not in cls.ICONS:
            return QIcon()
        
        svg_content = cls.ICONS[icon_name]
        svg_renderer = QSvgRenderer(QByteArray(svg_content.encode()))
        
        icon_pixmap = QPixmap(size, size)
        icon_pixmap.fill(Qt.transparent)
        
        painter = QPainter(icon_pixmap)
        svg_renderer.render(painter)
        painter.end()
        
        return QIcon(icon_pixmap)


class UserMenuWidget(QFrame):
    """Widget do menu do usuário"""
    
    profile_requested = pyqtSignal()
    password_change_requested = pyqtSignal()
    admin_requested = pyqtSignal()
    logout_requested = pyqtSignal()
    
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setup_ui()
        self.setup_menu()
    
    def setup_ui(self):
        """Configura a interface do widget"""
        self.setObjectName("userContainer")
        self.setCursor(Qt.PointingHandCursor)
        self.setup_styles()
        
        # Layout principal
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        # Avatar
        self.avatar_widget = UserAvatarWidget(self.usuario, 28)
        layout.addWidget(self.avatar_widget)
        
        # Nome do usuário
        first_name = self.get_first_name()
        self.name_label = QLabel(first_name)
        self.name_label.setStyleSheet("""
            color: #f0f0f0;
            font-weight: bold;
            font-size: 11pt;
        """)
        layout.addWidget(self.name_label)
        
        # Botão dropdown
        self.dropdown_button = QPushButton()
        self.dropdown_button.setFixedSize(20, 20)
        self.dropdown_button.setCursor(Qt.PointingHandCursor)
        self.dropdown_button.setIcon(IconProvider.create_icon('chevron_down', 12))
        self.dropdown_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.dropdown_button)
        
        # Conectar eventos
        self.dropdown_button.clicked.connect(self.show_menu)
        self.mousePressEvent = self.on_click
    
    def setup_styles(self):
        """Configura os estilos do widget"""
        self.setStyleSheet("""
            #userContainer {
                background-color: #1e1e1e;
                border-radius: 16px;
                border: 1px solid #333;
            }
            #userContainer:hover {
                background-color: #2d2d2d;
                border-color: #444;
            }
        """)
    
    def setup_menu(self):
        """Configura o menu dropdown"""
        self.menu = QMenu(self)
        self.menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e1e;
                color: #f0f0f0;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 8px;
                min-width: 160px;
            }
            QMenu::item {
                padding: 12px 16px;
                border-radius: 6px;
                margin: 2px;
            }
            QMenu::item:selected {
                background-color: #2d2d2d;
                color: #0d6efd;
            }
            QMenu::separator {
                height: 1px;
                background-color: #333;
                margin: 8px 4px;
            }
        """)
        
        # Adicionar ações ao menu
        self.add_menu_actions()
    
    def add_menu_actions(self):
        """Adiciona as ações ao menu"""
        # Ação de perfil
        profile_action = QAction(IconProvider.create_icon('profile'), "Meu Perfil", self)
        profile_action.triggered.connect(self.profile_requested.emit)
        self.menu.addAction(profile_action)
        
        # Ação de alterar senha
        password_action = QAction(IconProvider.create_icon('password'), "Alterar Senha", self)
        password_action.triggered.connect(self.password_change_requested.emit)
        self.menu.addAction(password_action)
        
        # Separador e ação de admin (se aplicável)
        if self.is_admin():
            self.menu.addSeparator()
            admin_action = QAction(IconProvider.create_icon('admin'), "Administração", self)
            admin_action.triggered.connect(self.admin_requested.emit)
            self.menu.addAction(admin_action)
        
        # Separador e logout
        self.menu.addSeparator()
        logout_action = QAction(IconProvider.create_icon('logout'), "Sair", self)
        logout_action.triggered.connect(self.logout_requested.emit)
        self.menu.addAction(logout_action)
    
    def show_menu(self):
        """Exibe o menu dropdown"""
        # Posicionar o menu abaixo do widget
        menu_pos = self.mapToGlobal(self.rect().bottomLeft())
        menu_pos.setX(menu_pos.x() - 10)  # Pequeno ajuste horizontal
        self.menu.exec_(menu_pos)
    
    def on_click(self, event):
        """Manipula o clique no widget"""
        if event.button() == Qt.LeftButton:
            self.show_menu()
        super().mousePressEvent(event)
    
    def get_first_name(self):
        """Obtém o primeiro nome do usuário"""
        try:
            return self.usuario['nome'].split()[0]
        except (KeyError, IndexError, AttributeError):
            return "Usuário"
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        try:
            return self.usuario.get('tipo', '').lower() == 'admin'
        except (KeyError, AttributeError):
            return False


class UserManager:
    """Gerenciador principal do usuário na aplicação"""
    
    def __init__(self, main_window, db):
        self.main_window = main_window
        self.db = db
        self.usuario = None
        self.user_menu_widget = None
        self.user_status_label = None
        
        # Diálogos ativos
        self.active_dialogs = {}
    
    def setup_for_user(self, usuario):
        """Configura a interface para o usuário logado"""
        self.usuario = usuario
        self.setup_status_bar()
        self.setup_user_menu()
        self.adjust_permissions()
    
    def setup_status_bar(self):
        """Configura a barra de status com informações do usuário"""
        try:
            user_info = f"Usuário: {self.usuario['nome']} | Perfil: {self.usuario['tipo'].capitalize()}"
            self.user_status_label = QLabel(user_info)
            self.user_status_label.setStyleSheet("padding-right: 10px;")
            self.main_window.statusBar.addPermanentWidget(self.user_status_label)
        except Exception as e:
            print(f"Erro ao configurar barra de status: {e}")
    
    def setup_user_menu(self):
        """Configura o menu do usuário"""
        try:
            # Criar widget do menu do usuário
            self.user_menu_widget = UserMenuWidget(self.usuario)
            
            # Conectar sinais
            self.user_menu_widget.profile_requested.connect(self.open_profile)
            self.user_menu_widget.password_change_requested.connect(self.change_password)
            self.user_menu_widget.admin_requested.connect(self.open_admin)
            self.user_menu_widget.logout_requested.connect(self.logout)
            
            # Adicionar à barra de menu
            self.main_window.menuBar().setCornerWidget(self.user_menu_widget, Qt.TopRightCorner)
            
        except Exception as e:
            print(f"Erro ao configurar menu do usuário: {e}")
    
    def adjust_permissions(self):
        """Ajusta a interface baseado nas permissões do usuário"""
        try:
            if self.usuario.get('tipo', '').lower() != 'admin':
                # Ocultar funcionalidades de administração
                if hasattr(self.main_window, 'btn_config'):
                    self.main_window.btn_config.setVisible(False)
                
                # Remover menu de administração se existir
                admin_menu = self.main_window.menuBar().findChild(QMenu, "adminMenu")
                if admin_menu:
                    self.main_window.menuBar().removeAction(admin_menu.menuAction())
                    
        except Exception as e:
            print(f"Erro ao ajustar permissões: {e}")
    
    def open_profile(self):
        """Abre a janela de perfil do usuário"""
        try:
            if 'profile' in self.active_dialogs:
                self.active_dialogs['profile'].raise_()
                return
            
            from ui.profile_window import ProfileWindow
            
            profile_dialog = ProfileWindow(self.db, self.usuario)
            self.active_dialogs['profile'] = profile_dialog
            
            # Conectar sinal de finalização
            profile_dialog.finished.connect(lambda: self.cleanup_dialog('profile'))
            
            result = profile_dialog.exec_()
            
            if result == QDialog.Accepted:
                # Atualizar informações do usuário
                self.update_user_info()
                
        except Exception as e:
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao abrir perfil: {str(e)}")
    
    def change_password(self):
        """Abre a janela de alteração de senha"""
        try:
            if 'password' in self.active_dialogs:
                self.active_dialogs['password'].raise_()
                return
            
            from ui.change_password_window import ChangePasswordWindow
            
            password_dialog = ChangePasswordWindow(self.db, self.usuario['id'])
            self.active_dialogs['password'] = password_dialog
            
            # Conectar sinal de finalização
            password_dialog.finished.connect(lambda: self.cleanup_dialog('password'))
            
            password_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao abrir alteração de senha: {str(e)}")
    
    def open_admin(self):
        """Abre a janela de administração"""
        try:
            if not self.user_menu_widget.is_admin():
                QMessageBox.warning(self.main_window, "Acesso Negado", 
                                  "Você não tem permissões de administrador.")
                return
            
            if 'admin' in self.active_dialogs:
                self.active_dialogs['admin'].raise_()
                return
            
            from ui.admin_window import AdminWindow
            
            admin_dialog = AdminWindow(self.db, self.usuario)
            self.active_dialogs['admin'] = admin_dialog
            
            # Conectar sinal de finalização
            admin_dialog.finished.connect(lambda: self.cleanup_dialog('admin'))
            
            admin_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao abrir administração: {str(e)}")
    
    def logout(self):
        """Realiza o logout do usuário"""
        try:
            reply = QMessageBox.question(
                self.main_window, 
                "Confirmação", 
                "Deseja realmente sair do sistema?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.perform_logout()
                
        except Exception as e:
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao realizar logout: {str(e)}")
    
    def perform_logout(self):
        """Executa o processo de logout"""
        try:
            # Fechar todos os diálogos ativos
            self.cleanup_all_dialogs()
            
            # Garantir conexão com o banco
            if hasattr(self.db, 'ensure_connection'):
                self.db.ensure_connection()
            
            # Ocultar janela principal
            self.main_window.hide()
            
            # Abrir janela de login
            from ui.login_window import LoginWindow
            
            login_window = LoginWindow(self.db)
            
            # Conectar sinal de login bem-sucedido se necessário
            if (hasattr(self.main_window, 'parent') and 
                self.main_window.parent() and 
                hasattr(self.main_window.parent(), 'on_login_success')):
                login_window.login_success_signal.connect(
                    self.main_window.parent().on_login_success
                )
            
            result = login_window.exec_()
            
            if result == QDialog.Accepted:
                # Login bem-sucedido - configurar novo usuário
                new_usuario = getattr(login_window, 'usuario', None)
                if new_usuario:
                    self.setup_for_user(new_usuario)
                    self.main_window.show()
                else:
                    self.exit_application()
            else:
                # Login cancelado
                self.exit_application()
                
        except Exception as e:
            print(f"Erro durante logout: {e}")
            self.exit_application()
    
    def update_user_info(self):
        """Atualiza as informações do usuário na interface"""
        try:
            # Atualizar dados do usuário
            self.usuario = self.db.obter_usuario_por_id(self.usuario['id'])
            
            # Atualizar barra de status
            if self.user_status_label:
                user_info = f"Usuário: {self.usuario['nome']} | Perfil: {self.usuario['tipo'].capitalize()}"
                self.user_status_label.setText(user_info)
            
            # Atualizar menu do usuário
            if self.user_menu_widget:
                self.user_menu_widget.usuario = self.usuario
                self.user_menu_widget.name_label.setText(self.user_menu_widget.get_first_name())
                
        except Exception as e:
            print(f"Erro ao atualizar informações do usuário: {e}")
    
    def cleanup_dialog(self, dialog_name):
        """Limpa referência de diálogo específico"""
        if dialog_name in self.active_dialogs:
            dialog = self.active_dialogs.pop(dialog_name)
            if dialog:
                dialog.deleteLater()
    
    def cleanup_all_dialogs(self):
        """Limpa todos os diálogos ativos"""
        for dialog_name, dialog in list(self.active_dialogs.items()):
            if dialog:
                try:
                    dialog.close()
                    dialog.deleteLater()
                except:
                    pass
        self.active_dialogs.clear()
    
    def exit_application(self):
        """Encerra a aplicação"""
        try:
            self.cleanup_all_dialogs()
            self.main_window.close()
            import sys
            sys.exit(0)
        except:
            import os
            os._exit(0)


# Integração com a janela principal - substitua os métodos antigos por estes:

def setup_for_user(self, usuario):
    """Método para integrar na janela principal"""
    if not hasattr(self, 'user_manager'):
        self.user_manager = UserManager(self, self.db)
    
    self.user_manager.setup_for_user(usuario)

class ConfigDialog(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.initUI()
    
    def initUI(self):
        # Configurar janela
        self.setWindowTitle("Configurações")
        self.setFixedWidth(450)
        self.setObjectName("configDialog")
        
        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título
        titulo = QLabel("Configurações do Sistema")
        titulo.setFont(QFont("Segoe UI", 14, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)
        
        # Tema
        tema_label = QLabel("Tema:")
        tema_label.setFont(QFont("Segoe UI", 11))
        
        self.tema_combo = QComboBox()
        self.tema_combo.setFont(QFont("Segoe UI", 11))
        self.tema_combo.addItem("Tema Claro", "light")
        self.tema_combo.addItem("Tema Escuro", "dark")
        self.tema_combo.setMinimumHeight(30)
        
        # Selecionar tema atual
        tema_atual = self.settings.get_theme()
        index = self.tema_combo.findData(tema_atual)
        if index != -1:
            self.tema_combo.setCurrentIndex(index)
        
        # Tamanho da fonte
        font_label = QLabel("Tamanho da Fonte:")
        font_label.setFont(QFont("Segoe UI", 11))
        
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setFont(QFont("Segoe UI", 11))
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(self.settings.get_font_size())
        self.font_size_spin.setMinimumHeight(30)
        
        # Adicionar campos ao formulário
        form_layout.addRow(tema_label, self.tema_combo)
        form_layout.addRow(font_label, self.font_size_spin)
        
        layout.addLayout(form_layout)
        
        # Separador
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.HLine)
        separador2.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador2)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.setFont(QFont("Segoe UI", 11))
        self.salvar_btn.setMinimumHeight(35)
        self.salvar_btn.setObjectName("saveButton")
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)
        
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.setFont(QFont("Segoe UI", 11))
        self.cancelar_btn.setMinimumHeight(35)
        self.cancelar_btn.setObjectName("cancelButton")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        
        layout.addLayout(button_layout)
    
    def salvar_configuracoes(self):
        """Salva as configurações."""
        tema = self.tema_combo.currentData()
        tamanho_fonte = self.font_size_spin.value()
        
        self.settings.set_theme(tema)
        self.settings.set_font_size(tamanho_fonte)
        
        self.accept()

# Adicionar esta linha se ainda não existir:
from PyQt5.QtWidgets import QApplication

