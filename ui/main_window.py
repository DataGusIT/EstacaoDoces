from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QStackedWidget, QHBoxLayout, QFrame,
                            QAction, QMenu, QToolBar, QDialog, QFormLayout,
                            QComboBox, QSpinBox, QMessageBox, QStatusBar, QSizePolicy)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QCursor
from PyQt5.QtCore import Qt, QDate, QSize
# Adicionar esta linha se ainda não existir:
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
        self.initUI()
        self.check_promocoes_ativas()
        self.aplicar_tema()
    
    def initUI(self):
        # Configurar janela principal
        self.setWindowTitle("Sistema de Estoque")
        self.setGeometry(100, 100, 1200, 700)
        
        # Menu superior (agora contendo também as ações da toolbar)
        self.criar_menu()
        
        # Remover a criação da toolbar separada, pois agora está integrada ao menu
        # self.criar_toolbar()  # Esta linha deve ser comentada ou removida
        
        # Status bar com estilo moderno
        self.statusBar = QStatusBar()
        self.statusBar.setStyleSheet("QStatusBar{background-color: #f8f9fa; color: #495057; padding: 5px; font-size: 12px;}")
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Sistema pronto", 3000)
        
        # Widget central
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Menu lateral
        self.menu_widget = QFrame()
        self.menu_widget.setMinimumWidth(250)
        self.menu_widget.setMaximumWidth(250)
        self.menu_widget.setObjectName("menuLateral")
        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setSpacing(5)
        menu_layout.setContentsMargins(10, 20, 10, 20)
        
        # Título do menu com logo
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        # Suponha que você tenha um ícone em resources/logo.png
        # logo_pixmap = QPixmap("resources/logo.png")
        # logo_label.setPixmap(logo_pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        titulo_label = QLabel("Sistema de Estoque")
        titulo_label.setFont(QFont("Segoe UI", this_size := 16, QFont.Bold))
        titulo_label.setObjectName("tituloApp")
        
        # header_layout.addWidget(logo_label)
        header_layout.addWidget(titulo_label)
        header_layout.setAlignment(Qt.AlignCenter)
        menu_layout.addLayout(header_layout)
        
        # Linha separadora
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        separador.setObjectName("separator")
        menu_layout.addWidget(separador)
        menu_layout.addSpacing(15)
        
        # Botões do menu com ícones
        self.btn_dashboard = self.criar_botao_menu("Dashboard", "home")
        self.btn_estoque = self.criar_botao_menu("Controle de Estoque", "package")
        self.btn_fornecedor = self.criar_botao_menu("Fornecedores", "truck")
        self.btn_promocoes = self.criar_botao_menu("Promoções", "tag")
        self.btn_clientes = self.criar_botao_menu("Clientes", "users")
        self.btn_caixa = self.criar_botao_menu("Controle de Caixa", "dollar-sign")
        
        # Adicionar botões ao menu
        menu_layout.addWidget(self.btn_dashboard)
        menu_layout.addWidget(self.btn_estoque)
        menu_layout.addWidget(self.btn_fornecedor)
        menu_layout.addWidget(self.btn_promocoes)
        menu_layout.addWidget(self.btn_clientes)
        menu_layout.addWidget(self.btn_caixa)
        menu_layout.addStretch()
        
        # Separador antes das configurações
        separador2 = QFrame()
        separador2.setFrameShape(QFrame.HLine)
        separador2.setFrameShadow(QFrame.Sunken)
        separador2.setObjectName("separator")
        menu_layout.addWidget(separador2)
        
        # Botão de configurações
        self.btn_config = self.criar_botao_menu("Configurações", "settings")
        self.btn_config.clicked.connect(self.abrir_configuracoes)
        menu_layout.addWidget(self.btn_config)
        
        # Créditos no final do menu
        creditos = QLabel("© 2025 Sistema de Estoque")
        creditos.setAlignment(Qt.AlignCenter)
        creditos.setObjectName("creditos")
        menu_layout.addWidget(creditos)
        
        # Área de conteúdo (usando QStackedWidget para alternar entre telas)
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_layout = QVBoxLayout(content_container)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Cabeçalho da área de conteúdo
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.page_title.setObjectName("pageTitle")
        content_layout.addWidget(self.page_title)
        
        # Separador no conteúdo
        content_separator = QFrame()
        content_separator.setFrameShape(QFrame.HLine)
        content_separator.setFrameShadow(QFrame.Sunken)
        content_separator.setObjectName("contentSeparator")
        content_layout.addWidget(content_separator)
        content_layout.addSpacing(10)
        
        # Stack para as páginas
        self.stack = QStackedWidget()
        content_layout.addWidget(self.stack)
        
        # Criar as páginas e adicioná-las ao stack
        self.estoque_page = EstoqueWindow(self.db)
        self.fornecedor_page = FornecedorWindow(self.db)
        self.promocoes_page = PromocoesWindow(self.db)
        self.clientes_page = ClientesWindow(self.db)
        self.caixa_page = CaixaWindow(self.db)
        self.dashboard_page = DashboardWindow(self.db)
        
        self.stack.addWidget(self.dashboard_page)  # Mudamos a ordem para colocar o dashboard primeiro
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
        
        # Adicionar elementos ao layout principal
        main_layout.addWidget(self.menu_widget)
        main_layout.addWidget(content_container)
        
        # Configurar widget central
        self.setCentralWidget(central_widget)
    
    def criar_botao_menu(self, texto, icone_nome=None):
        """Cria um botão estilizado para o menu lateral."""
        btn = QPushButton(texto)
        btn.setFont(QFont("Segoe UI", 12))
        btn.setMinimumHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("menuButton")
        
        # Se você tiver ícones, pode adicioná-los desta forma:
        # if icone_nome:
        #     btn.setIcon(QIcon(f"resources/icons/{icone_nome}.png"))
        #     btn.setIconSize(QSize(20, 20))
        
        return btn
    
    def criar_menu(self):
        """Cria a barra de menu superior."""
        menubar = self.menuBar()
        menubar.setObjectName("menuBar")
        
        # Menu Arquivo
        arquivo_menu = menubar.addMenu('Arquivo')
        
        config_action = QAction('Configurações', self)
        config_action.triggered.connect(self.abrir_configuracoes)
        # config_action.setIcon(QIcon("resources/icons/settings.png"))
        arquivo_menu.addAction(config_action)
        
        arquivo_menu.addSeparator()
        
        sair_action = QAction('Sair', self)
        sair_action.triggered.connect(self.close)
        # sair_action.setIcon(QIcon("resources/icons/logout.png"))
        arquivo_menu.addAction(sair_action)
        
        # Menu Relatórios
        relatorios_menu = menubar.addMenu('Relatórios')
        
        estoque_baixo_action = QAction('Produtos com Estoque Baixo', self)
        estoque_baixo_action.triggered.connect(self.relatorio_estoque_baixo)
        # estoque_baixo_action.setIcon(QIcon("resources/icons/alert.png"))
        relatorios_menu.addAction(estoque_baixo_action)
        
        vencimentos_action = QAction('Produtos a Vencer', self)
        vencimentos_action.triggered.connect(self.relatorio_vencimentos)
        # vencimentos_action.setIcon(QIcon("resources/icons/calendar.png"))
        relatorios_menu.addAction(vencimentos_action)
        
        promocoes_action = QAction('Promoções Ativas', self)
        promocoes_action.triggered.connect(self.relatorio_promocoes)
        # promocoes_action.setIcon(QIcon("resources/icons/tag.png"))
        relatorios_menu.addAction(promocoes_action)
        
        # Menu Ajuda
        ajuda_menu = menubar.addMenu('Ajuda')
        
        sobre_action = QAction('Sobre', self)
        sobre_action.triggered.connect(self.mostrar_sobre)
        # sobre_action.setIcon(QIcon("resources/icons/info.png"))
        ajuda_menu.addAction(sobre_action)
        
        # Adicionar ações da toolbar diretamente ao menubar (move as ações para a mesma linha)
        toolbar_widget = QWidget()
        toolbar_layout = QHBoxLayout(toolbar_widget)
        toolbar_layout.setContentsMargins(0, 0, 10, 0)
        toolbar_layout.setSpacing(5)
        
        refresh_action = QAction('Atualizar', self)
        # refresh_action.setIcon(QIcon("resources/icons/refresh.png"))
        refresh_action.triggered.connect(self.atualizar_dados)
        
        search_action = QAction('Pesquisar', self)
        # search_action.setIcon(QIcon("resources/icons/search.png"))
        
        export_action = QAction('Exportar', self)
        # export_action.setIcon(QIcon("resources/icons/export.png"))
        
        # Criar botões para a toolbar que ficará no menubar
        refresh_button = QPushButton("Atualizar")
        refresh_button.setObjectName("toolbarButton")
        refresh_button.clicked.connect(self.atualizar_dados)
        refresh_button.setCursor(Qt.PointingHandCursor)
        
        search_button = QPushButton("Pesquisar")
        search_button.setObjectName("toolbarButton")
        search_button.setCursor(Qt.PointingHandCursor)
        
        export_button = QPushButton("Exportar")
        export_button.setObjectName("toolbarButton")
        export_button.setCursor(Qt.PointingHandCursor)
        
        # Adicionar botões ao layout
        toolbar_layout.addWidget(refresh_button)
        toolbar_layout.addWidget(search_button)
        toolbar_layout.addWidget(export_button)
        
        # Adicionar um widget de espaçamento que vai crescer e empurrar os botões para a direita
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar_layout.addWidget(spacer)
        
        # Adicionar o widget com os botões ao menubar
        menubar.setCornerWidget(toolbar_widget)
    
    def criar_toolbar(self):
        """Cria a barra de ferramentas."""
        toolbar = QToolBar("Barra de Ferramentas")
        toolbar.setObjectName("mainToolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)
        
        refresh_action = QAction('Atualizar', self)
        # refresh_action.setIcon(QIcon("resources/icons/refresh.png"))
        refresh_action.triggered.connect(self.atualizar_dados)
        toolbar.addAction(refresh_action)
        
        # Adicionar mais ações úteis à toolbar
        search_action = QAction('Pesquisar', self)
        # search_action.setIcon(QIcon("resources/icons/search.png"))
        toolbar.addAction(search_action)
        
        export_action = QAction('Exportar', self)
        # export_action.setIcon(QIcon("resources/icons/export.png"))
        toolbar.addAction(export_action)
    
    def switch_page(self, index):
        """Muda para a página especificada e atualiza a interface."""
        self.stack.setCurrentIndex(index)
        
        # Atualizar título da página
        titles = ["Dashboard", "Controle de Estoque", "Fornecedores", 
                 "Promoções", "Clientes", "Controle de Caixa"]
        
        self.page_title.setText(titles[index])
        self.setWindowTitle(f"Sistema de Estoque - {titles[index]}")
        
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
    
    def aplicar_tema(self):
        """Aplica o tema conforme configurações."""
        tema = self.settings.get_theme()
        font_size = self.settings.get_font_size()
        
        # Ajustar tamanho da fonte global
        font = QFont("Segoe UI", font_size)
        QApplication.setFont(font)
        
        # Definir folha de estilo baseada no tema
        if tema == "dark":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #121212;
                    color: #f0f0f0;
                }
                #menuLateral {
                    background-color: #1e1e1e;
                    border-right: 1px solid #333;
                }
                #menuButton {
                    background-color: transparent;
                    color: #d0d0d0;
                    border: none;
                    text-align: left;
                    padding-left: 15px;
                    border-radius: 5px;
                }
                #menuButton:hover {
                    background-color: #2d2d2d;
                }
                #menuButton[active="true"] {
                    background-color: #383838;
                    color: #ffffff;
                    font-weight: bold;
                }
                #tituloApp {
                    color: #ffffff;
                }
                #pageTitle {
                    color: #ffffff;
                }
                #contentContainer {
                    background-color: #121212;
                }
                #separator, #contentSeparator {
                    background-color: #333;
                }
                #creditos {
                    color: #888;
                }
                #toolbarButton {
                background-color: #2d2d2d;
                color: #d0d0d0;
                border: none;
                border-radius: 3px;
                padding: 3px 10px;
                margin: 2px;
                }
                #toolbarButton:hover {
                    background-color: #383838;
                }
                #toolbarButton:pressed {
                    background-color: #454545;
                }
                QMenuBar {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                }
                QMenuBar::item:selected {
                    background-color: #2d2d2d;
                }
                QMenu {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    border: 1px solid #333;
                }
                QMenu::item:selected {
                    background-color: #2d2d2d;
                }
                QToolBar {
                    background-color: #1e1e1e;
                    border-bottom: 1px solid #333;
                }
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #0b5ed7;
                }
                QPushButton:pressed {
                    background-color: #0a58ca;
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #2c2c2c;
                    color: #f0f0f0;
                    border: 1px solid #444;
                    border-radius: 4px;
                    padding: 4px;
                }
                QTableView {
                    background-color: #2c2c2c;
                    color: #f0f0f0;
                    gridline-color: #444;
                    border: 1px solid #444;
                }
                QHeaderView::section {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    padding: 5px;
                    border: 1px solid #444;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                    background-color: #2c2c2c;
                }
                QTabBar::tab {
                    background-color: #1e1e1e;
                    color: #f0f0f0;
                    border: 1px solid #444;
                    padding: 5px 10px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #2c2c2c;
                }
                QTabBar::tab:hover {
                    background-color: #2d2d2d;
                }
            """)
        else:  # Tema claro
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #f8f9fa;
                    color: #212529;
                }
                #menuLateral {
                    background-color: #343a40;
                    color: #f8f9fa;
                }
                #menuButton {
                    background-color: transparent;
                    color: #f8f9fa;
                    border: none;
                    text-align: left;
                    padding-left: 15px;
                    border-radius: 5px;
                }
                #menuButton:hover {
                    background-color: #495057;
                }
                #menuButton[active="true"] {
                    background-color: #0d6efd;
                    color: white;
                    font-weight: bold;
                }
                #tituloApp {
                    color: white;
                }
                #pageTitle {
                    color: #212529;
                }
                #contentContainer {
                    background-color: #fff;
                    border-radius: 8px;
                }
                #separator {
                    background-color: #495057;
                }
                #contentSeparator {
                    background-color: #dee2e6;
                }
                #creditos {
                    color: #adb5bd;
                }
                #toolbarButton {
                background-color: #e9ecef;
                color: #212529;
                border: none;
                border-radius: 3px;
                padding: 3px 10px;
                margin: 2px;
                }
                #toolbarButton:hover {
                    background-color: #dee2e6;
                }
                #toolbarButton:pressed {
                    background-color: #ced4da;
                }
                QMenuBar {
                    background-color: #f8f9fa;
                    color: #212529;
                }
                QMenuBar::item:selected {
                    background-color: #e9ecef;
                }
                QMenu {
                    background-color: #fff;
                    color: #212529;
                    border: 1px solid #dee2e6;
                }
                QMenu::item:selected {
                    background-color: #e9ecef;
                }
                QToolBar {
                    background-color: #f8f9fa;
                    border-bottom: 1px solid #dee2e6;
                }
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #0b5ed7;
                }
                QPushButton:pressed {
                    background-color: #0a58ca;
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #fff;
                    color: #212529;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 4px;
                }
                QTableView {
                    background-color: #fff;
                    color: #212529;
                    gridline-color: #dee2e6;
                    border: 1px solid #dee2e6;
                }
                QHeaderView::section {
                    background-color: #e9ecef;
                    color: #495057;
                    padding: 5px;
                    border: 1px solid #dee2e6;
                }
                QTabWidget::pane {
                    border: 1px solid #dee2e6;
                    background-color: #fff;
                }
                QTabBar::tab {
                    background-color: #e9ecef;
                    color: #495057;
                    border: 1px solid #dee2e6;
                    padding: 5px 10px;
                    margin-right: 2px;
                }
                QTabBar::tab:selected {
                    background-color: #fff;
                }
                QTabBar::tab:hover {
                    background-color: #f8f9fa;
                }
            """)
    
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
        self.usuario = usuario
        
        # Adicionar informações do usuário na barra de status
        self.user_status_label = QLabel(f"Usuário: {usuario['nome']} | Perfil: {usuario['tipo'].capitalize()}")
        self.user_status_label.setStyleSheet("padding-right: 10px;")
        self.statusBar.addPermanentWidget(self.user_status_label)
        
        # Adicionar botão de usuário ao menu
        self.add_user_menu()
        
        # Ajustar permissões conforme o tipo de usuário
        self.ajustar_permissoes(usuario['tipo'])

    def add_user_menu(self):
        """Adiciona o menu do usuário à barra de menu"""
        # Criar widget para o menu do usuário
        user_widget = QWidget()
        user_layout = QHBoxLayout(user_widget)
        user_layout.setContentsMargins(0, 0, 15, 0)
        user_layout.setSpacing(5)
        
        # Adicionar label com nome de usuário
        user_label = QLabel(f"Olá, {self.usuario['nome'].split()[0]}")
        user_label.setStyleSheet("font-weight: bold; color: #34495e;")
        
        # Criar botão de menu do usuário
        user_button = QPushButton("▼")
        user_button.setObjectName("userButton")
        user_button.setFixedSize(24, 24)
        user_button.setCursor(Qt.PointingHandCursor)
        user_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 10px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Adicionar ao layout
        user_layout.addWidget(user_label)
        user_layout.addWidget(user_button)
        
        # Criar menu de usuário
        user_menu = QMenu(self)
        user_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #dcdde1;
                padding: 5px;
            }
            QMenu::item {
                padding: 8px 30px 8px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #f5f6fa;
                color: #2980b9;
            }
        """)
        
        # Adicionar ações ao menu
        perfil_action = QAction("Meu Perfil", self)
        perfil_action.triggered.connect(self.abrir_perfil)
        
        senha_action = QAction("Alterar Senha", self)
        senha_action.triggered.connect(self.alterar_senha)
        
        if self.usuario['tipo'] == 'admin':
            admin_action = QAction("Administração", self)
            admin_action.triggered.connect(self.abrir_admin)
            user_menu.addAction(admin_action)
            user_menu.addSeparator()
        
        user_menu.addAction(perfil_action)
        user_menu.addAction(senha_action)
        user_menu.addSeparator()
        
        logout_action = QAction("Sair", self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)
        
        # Conectar botão ao menu
        user_button.clicked.connect(lambda: user_menu.exec_(QCursor.pos()))
        
        # Adicionar à barra de menu
        corner_widget = self.menuBar().cornerWidget(Qt.TopRightCorner)
        if corner_widget:
            corner_layout = corner_widget.layout()
            corner_layout.insertWidget(0, user_widget)
        else:
            self.menuBar().setCornerWidget(user_widget, Qt.TopRightCorner)

    def ajustar_permissoes(self, tipo_usuario):
        """Ajusta a interface baseado nas permissões do usuário"""
        if tipo_usuario != 'admin':
            # Desabilitar funcionalidades de administração
            # Por exemplo, ocultar o botão de configurações do menu lateral
            self.btn_config.setVisible(False)
            
            # Remover opção de administração do menu
            admin_menu = self.menuBar().findChild(QMenu, "adminMenu")
            if admin_menu:
                self.menuBar().removeAction(admin_menu.menuAction())
        
        # Pode adicionar mais ajustes dependendo do tipo de usuário

    def abrir_perfil(self):
        """Abre a janela de perfil do usuário"""
        from ui.profile_window import ProfileWindow
        profile_dialog = ProfileWindow(self.db, self.usuario)
        if profile_dialog.exec_():
            # Atualizar informações do usuário se necessário
            self.usuario = self.db.obter_usuario_por_id(self.usuario['id'])
            self.user_status_label.setText(f"Usuário: {self.usuario['nome']} | Perfil: {self.usuario['tipo'].capitalize()}")

    def alterar_senha(self):
        """Abre a janela de alteração de senha"""
        from ui.change_password_window import ChangePasswordWindow
        password_dialog = ChangePasswordWindow(self.db, self.usuario['id'])
        password_dialog.exec_()

    

    def logout(self):
        """Realiza o logout do usuário"""
        resposta = QMessageBox.question(self, "Confirmação", 
                                    "Deseja realmente sair do sistema?",
                                    QMessageBox.Yes | QMessageBox.No)
        
        if resposta == QMessageBox.Yes:
            # Fechar a janela principal e voltar para o login
            self.close()
            from ui.login_window import LoginWindow
            login_window = LoginWindow(self.db)
            if login_window.exec_():
                # Se o login for bem-sucedido, reabrir a aplicação
                from main import on_login_success
                on_login_success(login_window.usuario)


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