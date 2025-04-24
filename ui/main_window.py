from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QStackedWidget, QHBoxLayout, QFrame,
                            QAction, QMenu, QToolBar, QDialog, QFormLayout,
                            QComboBox, QSpinBox, QMessageBox, QStatusBar)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt, QDate

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
    
    def initUI(self):
        # Configurar janela principal
        self.setWindowTitle("Sistema de Estoque")
        self.setGeometry(100, 100, 1000, 600)
        
        # Menu superior
        self.criar_menu()
        
        # Toolbar
        self.criar_toolbar()
        
        # Status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage("Sistema pronto", 3000)
        
        # Widget central
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        
        # Menu lateral
        self.menu_widget = QFrame()
        self.menu_widget.setMaximumWidth(250)
        self.menu_widget.setFrameShape(QFrame.StyledPanel)
        menu_layout = QVBoxLayout(self.menu_widget)
        
        # Título do menu
        titulo_label = QLabel("Sistema de Estoque")
        titulo_label.setFont(QFont("Arial", 16, QFont.Bold))
        titulo_label.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(titulo_label)
        
        # Linha separadora
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        menu_layout.addWidget(separador)
        
        # Botões do menu
        self.btn_estoque = QPushButton("Controle de Estoque")
        self.btn_fornecedor = QPushButton("Cadastro de Fornecedores")
        self.btn_promocoes = QPushButton("Cadastro de Promoções")
        self.btn_clientes = QPushButton("Cadastro de Clientes")
        self.btn_caixa = QPushButton("Controle de Caixa")
        self.btn_dashboard = QPushButton("Dashboard")
        
        # Estilizar botões
        for btn in [self.btn_estoque, self.btn_fornecedor, self.btn_promocoes, self.btn_clientes]:
            btn.setMinimumHeight(50)
            btn.setFont(QFont("Arial", 11))
        
        # Adicionar botões ao menu
        menu_layout.addWidget(self.btn_estoque)
        menu_layout.addWidget(self.btn_fornecedor)
        menu_layout.addWidget(self.btn_promocoes)
        menu_layout.addWidget(self.btn_clientes)
        menu_layout.addWidget(self.btn_caixa)
        menu_layout.addWidget(self.btn_dashboard)
        menu_layout.addStretch()
        
        # Créditos no final do menu
        creditos = QLabel("© 2025 Sistema de Estoque")
        creditos.setAlignment(Qt.AlignCenter)
        menu_layout.addWidget(creditos)
        
        # Área de conteúdo (usando QStackedWidget para alternar entre telas)
        self.stack = QStackedWidget()
        
        # Criar as páginas e adicioná-las ao stack
        self.estoque_page = EstoqueWindow(self.db)
        self.fornecedor_page = FornecedorWindow(self.db)
        self.promocoes_page = PromocoesWindow(self.db)
        self.clientes_page = ClientesWindow(self.db)
        self.caixa_page = CaixaWindow(self.db)
        self.dashboard_page = DashboardWindow(self.db)
        
        self.stack.addWidget(self.estoque_page)
        self.stack.addWidget(self.fornecedor_page)
        self.stack.addWidget(self.promocoes_page)
        self.stack.addWidget(self.clientes_page)
        self.stack.addWidget(self.caixa_page)
        self.stack.addWidget(self.dashboard_page)
        
        # Conectar sinais dos botões
        self.btn_estoque.clicked.connect(lambda: self.switch_page(0))
        self.btn_fornecedor.clicked.connect(lambda: self.switch_page(1))
        self.btn_promocoes.clicked.connect(lambda: self.switch_page(2))
        self.btn_clientes.clicked.connect(lambda: self.switch_page(3))
        self.btn_caixa.clicked.connect(lambda: self.switch_page(4))
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(5))
        
        # Adicionar elementos ao layout principal
        main_layout.addWidget(self.menu_widget)
        main_layout.addWidget(self.stack)
        
        # Configurar widget central
        self.setCentralWidget(central_widget)
    
    def criar_menu(self):
        """Cria a barra de menu superior."""
        menubar = self.menuBar()
        
        # Menu Arquivo
        arquivo_menu = menubar.addMenu('Arquivo')
        
        config_action = QAction('Configurações', self)
        config_action.triggered.connect(self.abrir_configuracoes)
        arquivo_menu.addAction(config_action)
        
        arquivo_menu.addSeparator()
        
        sair_action = QAction('Sair', self)
        sair_action.triggered.connect(self.close)
        arquivo_menu.addAction(sair_action)
        
        # Menu Relatórios
        relatorios_menu = menubar.addMenu('Relatórios')
        
        estoque_baixo_action = QAction('Produtos com Estoque Baixo', self)
        estoque_baixo_action.triggered.connect(self.relatorio_estoque_baixo)
        relatorios_menu.addAction(estoque_baixo_action)
        
        vencimentos_action = QAction('Produtos a Vencer', self)
        vencimentos_action.triggered.connect(self.relatorio_vencimentos)
        relatorios_menu.addAction(vencimentos_action)
        
        promocoes_action = QAction('Promoções Ativas', self)
        promocoes_action.triggered.connect(self.relatorio_promocoes)
        relatorios_menu.addAction(promocoes_action)
        
        # Menu Ajuda
        ajuda_menu = menubar.addMenu('Ajuda')
        
        sobre_action = QAction('Sobre', self)
        sobre_action.triggered.connect(self.mostrar_sobre)
        ajuda_menu.addAction(sobre_action)
    
    def criar_toolbar(self):
        """Cria a barra de ferramentas."""
        toolbar = QToolBar("Barra de Ferramentas")
        self.addToolBar(toolbar)
        
        refresh_action = QAction('Atualizar', self)
        refresh_action.triggered.connect(self.atualizar_dados)
        toolbar.addAction(refresh_action)
    
    def switch_page(self, index):
        """Muda para a página especificada e atualiza a interface."""
        self.stack.setCurrentIndex(index)
        
        # Atualizar título da janela com base na página
        titles = ["Controle de Estoque", "Cadastro de Fornecedores", 
                 "Cadastro de Promoções", "Cadastro de Clientes", "Controle de Caixa", "Dashboard"]
        
        self.setWindowTitle(f"Sistema de Estoque - {titles[index]}")
        
        # Destacar botão ativo
        buttons = [self.btn_estoque, self.btn_fornecedor, self.btn_promocoes, self.btn_clientes, self.btn_caixa, self.btn_dashboard]
        
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet("font-weight: bold; background-color: #d0d0d0;")
            else:
                btn.setStyleSheet("")
    
    def abrir_configuracoes(self):
        """Abre a janela de configurações."""
        dialog = ConfigDialog(self.settings)
        if dialog.exec_() == QDialog.Accepted:
            # Recarregar a aplicação para aplicar as configurações
            QMessageBox.information(self, "Configurações", 
                                  "As configurações foram salvas. Algumas alterações podem exigir reiniciar o aplicativo.")
    
    def atualizar_dados(self):
        """Atualiza os dados da página atual."""
        current_index = self.stack.currentIndex()
        
        if current_index == 0:
            self.estoque_page.carregar_dados()
        elif current_index == 1:
            self.fornecedor_page.carregar_dados()
        elif current_index == 2:
            self.promocoes_page.carregar_dados()
        elif current_index == 3:
            self.clientes_page.carregar_dados()
        elif current_index == 4:
            self.caixa_page.carregar_dados()
        elif current_index == 5:
            self.dashboard_page.carregar_dados()
        
        self.statusBar.showMessage("Dados atualizados com sucesso!", 3000)
    
    def check_promocoes_ativas(self):
        """Verifica e exibe promoções ativas na barra de status."""
        promocoes_ativas = self.db.listar_promocoes_ativas()
        
        if promocoes_ativas:
            num_promocoes = len(promocoes_ativas)
            self.statusBar.showMessage(f"{num_promocoes} promoções ativas hoje ({QDate.currentDate().toString('dd/MM/yyyy')})")
    
    def relatorio_estoque_baixo(self):
        """Gera relatório de produtos com estoque baixo."""
        # Implementação simulada - você pode criar uma janela real de relatório
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


class ConfigDialog(QDialog):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.initUI()
    
    def initUI(self):
        # Configurar janela
        self.setWindowTitle("Configurações")
        self.setFixedWidth(400)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        # Tema
        self.tema_combo = QComboBox()
        self.tema_combo.addItem("Tema Claro", "light")
        self.tema_combo.addItem("Tema Escuro", "dark")
        
        # Selecionar tema atual
        tema_atual = self.settings.get_theme()
        index = self.tema_combo.findData(tema_atual)
        if index != -1:
            self.tema_combo.setCurrentIndex(index)
        
        # Tamanho da fonte
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 16)
        self.font_size_spin.setValue(self.settings.get_font_size())
        
        # Adicionar campos ao formulário
        form_layout.addRow("Tema:", self.tema_combo)
        form_layout.addRow("Tamanho da Fonte:", self.font_size_spin)
        
        layout.addLayout(form_layout)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)
        self.cancelar_btn = QPushButton("Cancelar")
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