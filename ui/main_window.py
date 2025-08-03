from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QStackedWidget, QHBoxLayout, QFrame,
                            QAction, QMenu, QToolBar, QDialog, QFormLayout,
                            QComboBox, QSpinBox, QMessageBox, QStatusBar, QSizePolicy, QTimeEdit, QLineEdit, QCheckBox, QGroupBox, QDateEdit, QTextEdit)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QCursor, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QDate, QSize, QByteArray, QPropertyAnimation, QEasingCurve, pyqtSignal, QTime, QTimer
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QApplication
import os
import qtawesome as qta

from ui.estoque_window import EstoqueWindow
from ui.fornecedor_window import FornecedorWindow
from ui.promocoes_window import PromocoesWindow
from ui.clientes_window import ClientesWindow
from ui.caixa_window import CaixaWindow
from ui.dashboard_window import DashboardWindow
from ui.icon_manager import IconManager

from scheduler import Scheduler
from notification_manager import NotificationManager

class MainWindow(QMainWindow):
    def __init__(self, db, settings, theme_colors):
        super().__init__()
        self.db = db
        self.settings = settings
        self.theme_colors = theme_colors # Salve o dicionário
        self.menu_collapsed = True
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        self.initUI()
        self.check_promocoes_ativas()
        # A chamada para aplicar_tema agora é feita no final do initUI

    def initUI(self):
        self.setWindowTitle("Sistema de Estoque - GestorX")
        self.setGeometry(100, 100, 1280, 720)
        
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        theme_colors = self._get_theme_colors()

        # ===== CABEÇALHO UNIFICADO =====
        header_frame = QFrame()
        header_frame.setObjectName("headerFrame")
        header_frame.setFixedHeight(50)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 0, 5, 0)
        header_layout.setSpacing(10)
        
        self.app_logo = QLabel()
        logo_pixmap = self.carregar_logo_pixmap() 
        if logo_pixmap:
            self.app_logo.setPixmap(logo_pixmap)
            
        # --- CORREÇÃO: Aumente o tamanho do QLabel aqui ---
        self.app_logo.setFixedSize(60, 60) # De: 32, 32  Para: 40, 40

        app_title = QLabel("Sistema de Estoque - GestorX")
        app_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        app_title.setObjectName("appTitle")
        
        header_layout.addWidget(self.app_logo)
        header_layout.addWidget(app_title)
        
        # Menus do cabeçalho
        self.arquivo_btn = QPushButton("Arquivo")
        arquivo_menu = QMenu(self)
        self.config_action = QAction('Configurações', self)
        self.sair_action = QAction('Sair', self)
        arquivo_menu.addAction(self.config_action)
        arquivo_menu.addSeparator()
        arquivo_menu.addAction(self.sair_action)
        self.arquivo_btn.setMenu(arquivo_menu)
        self.config_action.triggered.connect(self.abrir_configuracoes)
        self.sair_action.triggered.connect(self.close)

        self.relatorios_btn = QPushButton("Relatórios")
        relatorios_menu = QMenu(self)
        self.estoque_baixo_action = QAction('Estoque Baixo', self)
        self.vencimentos_action = QAction('Produtos a Vencer', self)
        relatorios_menu.addAction(self.estoque_baixo_action)
        relatorios_menu.addAction(self.vencimentos_action)
        self.relatorios_btn.setMenu(relatorios_menu)
        self.estoque_baixo_action.triggered.connect(self.relatorio_estoque_baixo)
        self.vencimentos_action.triggered.connect(self.relatorio_vencimentos)
        
        self.ajuda_btn = QPushButton("Ajuda")
        ajuda_menu = QMenu(self)
        self.sobre_action = QAction('Sobre', self)
        ajuda_menu.addAction(self.sobre_action)
        self.ajuda_btn.setMenu(ajuda_menu)
        self.sobre_action.triggered.connect(self.mostrar_sobre)

        self.header_menu_buttons = [self.arquivo_btn, self.relatorios_btn, self.ajuda_btn]
        for btn in self.header_menu_buttons:
            btn.setObjectName("headerMenuButton")
            btn.setCursor(Qt.PointingHandCursor)
            header_layout.addWidget(btn)

        header_layout.addStretch()
        
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.setObjectName("headerActionButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.atualizar_dados)
        header_layout.addWidget(self.refresh_button)
        
        self.user_menu_placeholder = QFrame()
        header_layout.addWidget(self.user_menu_placeholder)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        header_layout.addWidget(separator)
        
        window_controls_frame = QFrame()
        window_layout = QHBoxLayout(window_controls_frame)
        window_layout.setContentsMargins(0, 0, 0, 0)
        window_layout.setSpacing(0)
        
        self.minimize_btn = QPushButton()
        self.maximize_btn = QPushButton()
        self.close_btn = QPushButton()
        
        for btn, name in [(self.minimize_btn, "minimizeButton"), (self.maximize_btn, "maximizeButton"), (self.close_btn, "closeButton")]:
            btn.setObjectName(name)
            btn.setFixedSize(45, 30)
        
        self.minimize_btn.clicked.connect(self.showMinimizedAnimated)
        self.maximize_btn.clicked.connect(self.toggleMaximizeAnimated)
        self.close_btn.clicked.connect(self.close)
        
        window_layout.addWidget(self.minimize_btn)
        window_layout.addWidget(self.maximize_btn)
        window_layout.addWidget(self.close_btn)
        
        header_layout.addWidget(window_controls_frame)
        main_layout.addWidget(header_frame)
        
        header_frame.mousePressEvent = self.start_window_drag
        header_frame.mouseMoveEvent = self.window_drag
        self.drag_position = None

        # ===== CONTEÚDO PRINCIPAL =====
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.menu_container = QFrame()
        self.menu_container.setObjectName("menuContainer")
        menu_container_layout = QVBoxLayout(self.menu_container)
        menu_container_layout.setContentsMargins(0, 0, 0, 0)
        menu_container_layout.setSpacing(0)
        
        menu_header = QFrame()
        menu_header.setObjectName("menuHeader")
        menu_header.setFixedHeight(50)
        menu_header_layout = QHBoxLayout(menu_header)
        menu_header_layout.setContentsMargins(10, 10, 10, 10)
        
        self.hamburger_btn = QPushButton()
        self.hamburger_btn.setObjectName("hamburgerButton")
        self.hamburger_btn.setFixedSize(40, 40)
        self.hamburger_btn.setIconSize(QSize(20, 20))
        self.hamburger_btn.setCursor(Qt.PointingHandCursor)
        self.hamburger_btn.clicked.connect(self.toggle_menu)
        menu_header_layout.addWidget(self.hamburger_btn, alignment=Qt.AlignCenter)
        menu_container_layout.addWidget(menu_header)
        
        self.menu_widget = QFrame()
        self.menu_widget.setObjectName("menuLateral")
        menu_widget_layout = QVBoxLayout(self.menu_widget)
        menu_widget_layout.setSpacing(5)
        menu_widget_layout.setContentsMargins(5, 15, 5, 15)
        
        self.btn_dashboard = self.criar_botao_menu("Dashboard", 'dashboard')
        self.btn_estoque = self.criar_botao_menu("Controle de Estoque", 'estoque')
        self.btn_fornecedor = self.criar_botao_menu("Fornecedores", 'fornecedores')
        self.btn_promocoes = self.criar_botao_menu("Promoções", 'promocoes')
        self.btn_clientes = self.criar_botao_menu("Clientes", 'clientes')
        self.btn_caixa = self.criar_botao_menu("Controle de Caixa", 'caixa')
        
        self.menu_buttons = [self.btn_dashboard, self.btn_estoque, self.btn_fornecedor, self.btn_promocoes, self.btn_clientes, self.btn_caixa]
        
        for btn in self.menu_buttons:
            menu_widget_layout.addWidget(btn)
        menu_widget_layout.addStretch()
        
        self.btn_config = self.criar_botao_menu("Configurações", 'config')
        self.btn_config.clicked.connect(self.abrir_configuracoes)
        menu_widget_layout.addWidget(self.btn_config)
        menu_container_layout.addWidget(self.menu_widget)
        
        content_container = QFrame()
        content_container.setObjectName("contentContainer")
        content_container_layout = QVBoxLayout(content_container)
        content_container_layout.setContentsMargins(20, 20, 20, 20)
        
        self.page_title = QLabel("Dashboard")
        self.page_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.page_title.setObjectName("pageTitle")
        content_container_layout.addWidget(self.page_title)
        
        content_separator = QFrame()
        content_separator.setFrameShape(QFrame.HLine)
        content_separator.setFrameShadow(QFrame.Sunken)
        content_separator.setObjectName("contentSeparator")
        content_container_layout.addWidget(content_separator)
        content_container_layout.addSpacing(10)
        
        self.stack = QStackedWidget()
        content_container_layout.addWidget(self.stack)

        ## ========================================================== ##
        ## CORREÇÃO CRÍTICA: Instanciação das páginas com theme_colors ##
        ## ========================================================== ##
        self.dashboard_page = DashboardWindow(self.db, theme_colors)
        self.estoque_page = EstoqueWindow(self.db, theme_colors)
        self.fornecedor_page = FornecedorWindow(self.db, theme_colors)
        self.promocoes_page = PromocoesWindow(self.db, theme_colors)
        
        # Para as janelas abaixo funcionarem, elas também precisarão ser adaptadas
        # para receber `theme_colors` no construtor.
        self.clientes_page = ClientesWindow(self.db, theme_colors)
        self.caixa_page = CaixaWindow(self.db, theme_colors)

        self.stack.addWidget(self.dashboard_page)
        self.stack.addWidget(self.estoque_page)
        self.stack.addWidget(self.fornecedor_page)
        self.stack.addWidget(self.promocoes_page)
        self.stack.addWidget(self.clientes_page)
        self.stack.addWidget(self.caixa_page)
        
        self.btn_dashboard.clicked.connect(lambda: self.switch_page(0))
        self.btn_estoque.clicked.connect(lambda: self.switch_page(1))
        self.btn_fornecedor.clicked.connect(lambda: self.switch_page(2))
        self.btn_promocoes.clicked.connect(lambda: self.switch_page(3))
        self.btn_clientes.clicked.connect(lambda: self.switch_page(4))
        self.btn_caixa.clicked.connect(lambda: self.switch_page(5))
        
        content_layout.addWidget(self.menu_container)
        content_layout.addWidget(content_container, 1)
        main_layout.addWidget(content_frame)
        
        self.statusBar = QStatusBar()
        self.statusBar.setObjectName("statusBar")
        self.statusBar.setFixedHeight(25)
        self.setStatusBar(self.statusBar)
        
        self.toggle_menu()
        self.switch_page(0)
        
        self.setWindowOpacity(0.0)
        self.show()
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(500)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.start()

        # Aplica o tema DEPOIS que todos os widgets foram criados.
        self.aplicar_tema()

        # --- CONEXÕES PARA ATUALIZAÇÃO AUTOMÁTICA ---
        # Conecta o sinal da janela de clientes a um "manipulador" (handler)
        if hasattr(self.clientes_page, 'dados_clientes_alterados'):
            self.clientes_page.dados_clientes_alterados.connect(self.on_dados_clientes_changed)

        # Faça o mesmo para outras páginas
        if hasattr(self.estoque_page, 'dados_produtos_alterados'):
            self.estoque_page.dados_produtos_alterados.connect(self.on_dados_produtos_changed)

        if hasattr(self.fornecedor_page, 'dados_fornecedores_alterados'):
            self.fornecedor_page.dados_fornecedores_alterados.connect(self.on_dados_fornecedores_changed)
        
        # ... etc para outras janelas que modificam dados

         # --- INICIA O GERENCIADOR DE NOTIFICAÇÕES E O AGENDADOR ---
        self.notification_manager = NotificationManager(self.db, self.settings)
        self.scheduler = Scheduler(self.settings)
        self.scheduler.notification_triggered.connect(self.notification_manager.check_and_send_notifications)
        self.scheduler.log_message.connect(self.log_scheduler_message)
        self.scheduler.start() # Inicia a thread do agendador
    
    def on_dados_clientes_changed(self):
        """
        Este método (slot) é chamado quando a ClientesWindow emite o sinal.
        Ele atualiza as janelas que dependem da lista de clientes.
        """
        print("Sinal recebido: dados de clientes alterados. Atualizando Caixa...")
        # A CaixaWindow precisa da lista de clientes atualizada.
        if hasattr(self.caixa_page, 'carregar_clientes'):
            self.caixa_page.carregar_clientes()
        
        # O Dashboard também pode precisar ser atualizado.
        if hasattr(self.dashboard_page, 'carregar_dados'):
            self.dashboard_page.carregar_dados()

    def on_dados_produtos_changed(self):
        """
        Chamado quando a EstoqueWindow emite seu sinal.
        Atualiza as janelas que dependem da lista de produtos.
        """
        print("Sinal recebido: dados de produtos alterados. Atualizando Caixa e Promoções...")
        # A CaixaWindow precisa da lista de produtos.
        if hasattr(self.caixa_page, 'carregar_produtos'):
            self.caixa_page.carregar_produtos()
        
        # A PromocoesWindow também precisa.
        if hasattr(self.promocoes_page, 'carregar_dados'):
            self.promocoes_page.carregar_dados()

        # O Dashboard também.
        if hasattr(self.dashboard_page, 'carregar_dados'):
            self.dashboard_page.carregar_dados()

    def on_dados_fornecedores_changed(self):
        """
        Chamado quando a FornecedorWindow emite seu sinal.
        """
        print("Sinal recebido: dados de fornecedores alterados. Atualizando Estoque...")
        # A EstoqueWindow precisa da lista de fornecedores.
        if hasattr(self.estoque_page, 'carregar_dados'):
             self.estoque_page.carregar_dados()

    def log_scheduler_message(self, message):
        """Exibe mensagens do agendador na barra de status."""
        print(message) # Para depuração no console
        self.statusBar.showMessage(message, 5000)

    def carregar_logo(self):
        """Carrega a logo como QIcon para uso na barra de título"""
        logo_path = os.path.join("assets", "img", "GestorX_logo.png")
        if os.path.exists(logo_path):
            return QIcon(logo_path)
        else:
            # Retorna um ícone padrão se a logo não for encontrada
            return QIcon()
    
    def carregar_logo_pixmap(self):
        """Carrega a logo como QPixmap para uso no cabeçalho"""
        logo_path = os.path.join("assets", "img", "GestorX (2).png")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            
            # --- CORREÇÃO: Redimensione a imagem para o novo tamanho aqui ---
            return pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation) # De: 32, 32  Para: 40, 40
        else:
            print(f"ATENÇÃO: Arquivo de logo não encontrado no caminho: {logo_path}")
            return None
    
    def criar_botao_menu(self, texto, icon_name=None):
        """Cria um botão estilizado para o menu lateral usando qtawesome."""
        btn = QPushButton()
        btn.setObjectName("menuButton")
        btn.setMinimumHeight(45)
        btn.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(btn)
        layout.setContentsMargins(15, 0, 15, 0)
        layout.setSpacing(15)
        
        icon_color = self._get_theme_colors()['text_secondary']
        
        if icon_name:
            icon_widget = QLabel()
            icon_widget.setObjectName("buttonIcon")
            icon_pixmap = IconManager.get_icon(icon_name, color=icon_color).pixmap(QSize(20, 20))
            icon_widget.setPixmap(icon_pixmap)
            icon_widget.setFixedSize(24, 24)
            icon_widget.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_widget)
            btn.icon_widget = icon_widget # Salva referência ao widget do ícone
            btn.icon_name = icon_name # Salva o nome do ícone
        
        text_label = QLabel(texto)
        text_label.setFont(QFont("Segoe UI", 10))
        text_label.setObjectName("buttonText")
        layout.addWidget(text_label)
        layout.addStretch()
        
        btn.text_label = text_label
        return btn
    
    def toggle_menu(self):
        """Alterna entre menu expandido e recolhido com animação."""
        start_width = self.menu_container.width()
        if self.menu_collapsed:
            end_width = 250
            self.menu_collapsed = False
            for btn in self.menu_buttons + [self.btn_config]:
                btn.text_label.show()
        else:
            end_width = 60 # Largura recolhida
            self.menu_collapsed = True
            for btn in self.menu_buttons + [self.btn_config]:
                btn.text_label.hide()
        
        self.animation = QPropertyAnimation(self.menu_container, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(start_width)
        self.animation.setEndValue(end_width)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation.start()
        
        self.animation2 = QPropertyAnimation(self.menu_container, b"maximumWidth")
        self.animation2.setDuration(250)
        self.animation2.setStartValue(start_width)
        self.animation2.setEndValue(end_width)
        self.animation2.setEasingCurve(QEasingCurve.InOutCubic)
        self.animation2.start()
    
    def switch_page(self, index):
        """Muda para a página especificada e atualiza a interface."""
        self.stack.setCurrentIndex(index)
        titles = ["Dashboard", "Controle de Estoque", "Fornecedores", "Promoções", "Clientes", "Controle de Caixa"]
        self.page_title.setText(titles[index])
        self.statusBar.showMessage(f"Área: {titles[index]}", 3000)
        
        buttons = [self.btn_dashboard, self.btn_estoque, self.btn_fornecedor, self.btn_promocoes, self.btn_clientes, self.btn_caixa]
        theme_colors = self._get_theme_colors()

        for i, btn in enumerate(buttons):
            is_active = (i == index)
            btn.setProperty("active", is_active)
            
            # ATUALIZA A COR DO ÍCONE
            if hasattr(btn, 'icon_widget') and hasattr(btn, 'icon_name'):
                color = 'white' if is_active else theme_colors['text_secondary']
                new_icon = IconManager.get_icon(btn.icon_name, color=color)
                btn.icon_widget.setPixmap(new_icon.pixmap(QSize(20, 20)))
            
            btn.style().unpolish(btn)
            btn.style().polish(btn)
    
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

    def changeEvent(self, event):
        """Atualiza o ícone de maximizar/restaurar."""
        if event.type() == event.WindowStateChange:
            theme_colors = self._get_theme_colors()
            icon_color = theme_colors['text_secondary']
            if self.isMaximized():
                self.maximize_btn.setIcon(IconManager.get_icon('restaurar', icon_color))
            else:
                self.maximize_btn.setIcon(IconManager.get_icon('maximizar', icon_color))
        super().changeEvent(event)
    
    def showMinimizedAnimated(self):
        """Minimiza a janela com uma animação de fade out."""
        if self.isMinimized():
            return
            
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(200)
        self.animation.setStartValue(1.0)
        self.animation.setEndValue(0.0)
        self.animation.setEasingCurve(QEasingCurve.InQuad)
        
        # Conecta o término da animação à minimização real da janela
        self.animation.finished.connect(self.showMinimized)
        
        self.animation.start()

    def toggleMaximizeAnimated(self):
        """Alterna entre maximizado e normal com uma animação sutil."""
        if self.isMaximized():
            # Animação para restaurar (fade out parcial e depois fade in)
            self.animation_out = QPropertyAnimation(self, b"windowOpacity")
            self.animation_out.setDuration(150)
            self.animation_out.setStartValue(1.0)
            self.animation_out.setEndValue(0.7)
            self.animation_out.setEasingCurve(QEasingCurve.InQuad)
            self.animation_out.finished.connect(self.showNormalAnimated)
            self.animation_out.start()
        else:
            # Maximiza diretamente, pois o SO geralmente já anima isso
            self.showMaximized()

    def showNormalAnimated(self):
        """Função auxiliar para restaurar a janela e aplicar fade in."""
        self.showNormal()
        self.setWindowOpacity(0.7) # Começa de onde a animação de saída parou
        
        self.animation_in = QPropertyAnimation(self, b"windowOpacity")
        self.animation_in.setDuration(200)
        self.animation_in.setStartValue(0.7)
        self.animation_in.setEndValue(1.0)
        self.animation_in.setEasingCurve(QEasingCurve.OutQuad)
        self.animation_in.start()
            
        # Se quiser forçar o fade ao restaurar (pode não ficar ideal):
        # if self.isMaximized():
        #     self.animation = QPropertyAnimation(self, b"windowOpacity")
        #     self.animation.setDuration(150)
        #     self.animation.setStartValue(1.0)
        #     self.animation.setEndValue(0.0)
        #     self.animation.finished.connect(self.showNormalAnimated)
        #     self.animation.start()
        # else:
        #     self.showMaximized()

    def get_main_stylesheet(self):
        """Retorna o stylesheet completo da aplicação com efeitos de hover."""
        # Cores base para facilitar a troca de tema no futuro
        bg_hover = "#4a4a4a"       # Cinza para hover nos botões de minimizar/maximizar
        bg_pressed = "#5a5a5a"     # Cinza mais escuro para clique
        close_hover = "#e81123"    # Vermelho para hover no botão de fechar
        close_pressed = "#f1707a"  # Vermelho claro para clique no botão de fechar

        return f"""
            /* Estilo geral dos botões de controle da janela */
            #minimizeButton, #maximizeButton, #closeButton {{
                background-color: transparent;
                border: none;
                color: #ccc; /* Cor do ícone/texto */
                font-family: "Segoe UI Symbol"; /* Fonte que garante a exibição dos símbolos */
                font-size: 14px;
            }}

            /* Efeito de hover para minimizar e maximizar */
            #minimizeButton:hover, #maximizeButton:hover {{
                background-color: {bg_hover};
            }}

            /* EFEITO DE HOVER ESPECIAL PARA O BOTÃO FECHAR */
            #closeButton:hover {{
                background-color: {close_hover};
                color: white; /* Cor do 'X' fica branca para contraste */
            }}

            /* Efeito de clique (pressionado) */
            #minimizeButton:pressed, #maximizeButton:pressed {{
                background-color: {bg_pressed};
            }}

            #closeButton:pressed {{
                background-color: {close_pressed};
            }}

            /* ----- SEU OUTRO STYLESHEET PODE VIR AQUI ----- */
            /* Exemplo: Estilo dos botões do menu do cabeçalho */
            #headerMenuButton {{
                background-color: transparent;
                border: none;
                padding: 8px 12px;
                border-radius: 6px;
                color: #ccc;
            }}
            #headerMenuButton:hover {{
                background-color: {bg_hover};
                color: white;
            }}
            #headerMenuButton:pressed {{
                background-color: {bg_pressed};
            }}
            #headerMenuButton::menu-indicator {{
                image: none;
            }}
        """

    def _get_theme_colors(self):
        """ÚNICA FONTE DE VERDADE para as cores do tema."""
        is_dark = self.settings.get_theme() == 'dark'
        if is_dark:
            return {
                'bg_color': "#1c2128", 'surface_color': "#22272e", 'menu_color': "#22272e",
                'text_color': "#cdd9e5", 'text_secondary': "#768390", 'border_color': "#373e47",
                'button_hover': "#373e47", 'accent_color': "#007AFF"
            }
        else:
            return {
                'bg_color': "#ffffff", 'surface_color': "#f2f2f7", 'menu_color': "#f9f9f9",
                'text_color': "#000000", 'text_secondary': "#6d6d70", 'border_color': "#d1d1d6",
                'button_hover': "#e5e5ea", 'accent_color': "#007AFF"
            }
    
    def aplicar_tema(self):
        """Aplica o tema atual a todos os componentes, centralizando o estilo."""
        theme = self._get_theme_colors()
        accent_color = theme['accent_color']
        text_color = theme['text_color']
        text_secondary = theme['text_secondary']
        bg_color = theme['bg_color']
        surface_color = theme['surface_color']
        border_color = theme['border_color']
        button_hover = theme['button_hover']

        # --- CORREÇÃO: A linha que definia a imagem da logo foi removida daqui ---
        # A logo agora é definida apenas no initUI e não será mais sobrescrita.

        # Ícones dinâmicos que DEVEM mudar com o tema
        self.hamburger_btn.setIcon(IconManager.get_icon('menu', text_color))
        self.refresh_button.setIcon(IconManager.get_icon('atualizar', 'white'))
        self.minimize_btn.setIcon(IconManager.get_icon('minimizar', text_secondary))
        self.maximize_btn.setIcon(IconManager.get_icon('maximizar' if not self.isMaximized() else 'restaurar', text_secondary))
        self.close_btn.setIcon(IconManager.get_icon('fechar', text_secondary))
        
        # Atualiza os ícones do menu lateral para a cor correta (inativa/ativa)
        self.switch_page(self.stack.currentIndex())
        
        # Aplica a folha de estilo principal (o restante da sua função está perfeito)
        self.setStyleSheet(f"""
            QMainWindow, #centralWidget, QDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}
            
            /* --- CAMPOS DE ENTRADA E SELEÇÃO --- */
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {surface_color};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 4px;
                padding: 5px;
                font-size: 10pt;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 1px solid {accent_color};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url(assets/img/chevron-down.png); /* Crie um ícone de seta para baixo */
            }}
            QComboBox QAbstractItemView {{
                background-color: {surface_color};
                border: 1px solid {border_color};
                selection-background-color: {accent_color};
            }}

            /* --- TABELA --- */
            QTableWidget {{
                background-color: {surface_color};
                color: {text_color};
                border: 1px solid {border_color};
                gridline-color: {border_color};
            }}
            QTableWidget::item {{
                padding: 5px;
                border-bottom: 1px solid {border_color};
            }}
            QTableWidget::item:selected {{
                background-color: {accent_color};
                color: white;
            }}
            QHeaderView::section {{
                background-color: {bg_color};
                color: {text_color};
                padding: 5px;
                border: 1px solid {border_color};
                font-weight: bold;
            }}

            /* --- ESTILO DAS ABAS (QTabWidget) --- */
            QTabWidget::pane {{
                border: 1px solid {border_color};
                border-top: none;
                background-color: {surface_color};
            }}
            QTabWidget::tab-bar {{
                alignment: left;
            }}
            QTabBar::tab {{
                background-color: {bg_color};
                color: {text_secondary};
                padding: 8px 15px;
                border: 1px solid {border_color};
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
                font-weight: bold;
            }}
            QTabBar::tab:hover {{
                background-color: {button_hover};
                color: {text_color};
            }}
            QTabBar::tab:selected {{
                background-color: {surface_color};
                color: {accent_color};
                border: 1px solid {border_color};
                border-bottom: 1px solid {surface_color};
            }}

            /* --- BOTÕES --- */
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: 1px solid {border_color};
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
                border-color: {accent_color};
            }}
            QPushButton:pressed {{
                background-color: {border_color};
            }}
            #primaryActionButton {{
                background-color: {accent_color};
                color: white;
                border: none;
            }}
            #primaryActionButton:hover {{
                background-color: #0069d9;
            }}
            
            /* --- OUTROS COMPONENTES --- */
            QGroupBox {{
                border: 1px solid {border_color};
                border-radius: 6px;
                margin-top: 20px;
                font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 10px;
                background-color: {bg_color};
                color: {text_secondary};
            }}
            
            #headerFrame, #menuHeader, #menuLateral {{
                background-color: {theme['menu_color']};
                border-bottom: 1px solid {theme['border_color']};
            }}
            #menuContainer {{
                background-color: {theme['menu_color']};
                border-right: 1px solid {theme['border_color']};
            }}
            #appTitle, #pageTitle {{ color: {theme['text_color']}; }}
            #hamburgerButton, #headerMenuButton {{
                background-color: transparent; border: none;
                color: {theme['text_color']}; border-radius: 6px;
            }}
            #menuButton {{
                background-color: transparent; border: none; text-align: left; 
                padding: 8px; border-radius: 8px; color: {theme['text_color']};
            }}
            #menuButton:hover {{ background-color: {theme['button_hover']}; }}
            #menuButton[active="true"] {{ background-color: {theme['accent_color']}; color: white; }}
        """)
    
        # Propaga a mudança do tema para as sub-páginas
        if hasattr(self, 'dashboard_page') and self.dashboard_page:
            self.dashboard_page.set_theme(theme)
        if hasattr(self, 'estoque_page') and self.estoque_page:
            self.estoque_page.set_theme(theme)
        if hasattr(self, 'fornecedor_page') and self.fornecedor_page:
            self.fornecedor_page.set_theme(theme)
        if hasattr(self, 'promocoes_page') and self.promocoes_page:
            self.promocoes_page.set_theme(theme)
        if hasattr(self, 'clientes_page') and self.clientes_page:
            self.clientes_page.set_theme(theme)
        if hasattr(self, 'caixa_page') and self.caixa_page:
            if hasattr(self.caixa_page, 'set_theme'):
                 self.caixa_page.set_theme(theme)
        
        self.update()
        if hasattr(self, 'repaint'):
            self.repaint()

    def aplicar_tema_completo(self):
        """Aplica tema em todos os widgets, incluindo janela principal"""
        self.aplicar_tema()
    
    def abrir_configuracoes(self):
        """Abre a janela de configurações."""
        
        # PEGA AS CORES DO TEMA ATUAL
        theme_colors = self._get_theme_colors()

        # PASSA AS CORES PARA O DIÁLOGO
        dialog = ConfigDialog(self.settings, theme_colors, self) # 'self' define a MainWindow como pai

        # A lógica restante permanece a mesma
        if dialog.exec_() == QDialog.Accepted:
            # Pede para a janela principal se redesenhar com o novo tema
            self.aplicar_tema() 
            
            # Reinicia o agendador para aplicar novas configurações de notificação
            self.scheduler.restart()

            QMessageBox.information(self, "Configurações", 
                                "As configurações foram salvas. Algumas alterações podem exigir que o aplicativo seja reiniciado para terem efeito completo.")
    
    def atualizar_dados(self):
        """Atualiza os dados da página atual chamando seu método padronizado 'carregar_dados'."""
        current_widget = self.stack.currentWidget()
        
        if hasattr(current_widget, 'carregar_dados'):
            try:
                print(f"DEBUG: Chamando carregar_dados() na página {current_widget.__class__.__name__}")
                current_widget.carregar_dados()
                self.statusBar.showMessage("Dados atualizados com sucesso!", 3000)
            except Exception as e:
                print(f"ERRO ao chamar carregar_dados na página {current_widget.__class__.__name__}: {e}")
                self.statusBar.showMessage("Erro ao atualizar dados.", 3000)
        else:
            self.statusBar.showMessage(f"A página atual não possui um método de atualização ('carregar_dados').", 3000)
    
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
        # --- PARA A THREAD DO AGENDADOR DE FORMA SEGURA ---
        print("Parando o agendador de notificações...")
        self.scheduler.stop()
        self.scheduler.wait() # Espera a thread terminar
        print("Agendador parado.")
        
        self.db.fechar()
        event.accept()

    def setup_for_user(self, usuario):
        """Configura a interface para o usuário logado"""
        try:
            if not hasattr(self, 'user_manager'):
                # Passa a MainWindow (self) para o UserManager
                self.user_manager = UserManager(self, self.db) 
            
            self.user_manager.usuario = usuario
            
            # --- CORREÇÃO PRINCIPAL AQUI ---
            # Ao criar o UserMenuWidget, passe as cores do tema
            user_menu_widget = UserMenuWidget(usuario, self.theme_colors)
            
            # Conecta os sinais... (código existente)
            user_menu_widget.profile_requested.connect(self.user_manager.open_profile)
            user_menu_widget.password_change_requested.connect(self.user_manager.change_password)
            user_menu_widget.admin_requested.connect(self.user_manager.open_admin)
            user_menu_widget.logout_requested.connect(self.user_manager.logout)

            # Lógica para substituir o placeholder... (código existente)
            if self.user_menu_placeholder.layout() is not None:
                while self.user_menu_placeholder.layout().count():
                    child = self.user_menu_placeholder.layout().takeAt(0)
                    if child.widget():
                        child.widget().deleteLater()
            else:
                placeholder_layout = QHBoxLayout()
                placeholder_layout.setContentsMargins(0, 0, 0, 0)
                self.user_menu_placeholder.setLayout(placeholder_layout)
            
            self.user_menu_placeholder.layout().addWidget(user_menu_widget)

            # Configura a barra de status e ajusta permissões
            self.user_manager.setup_status_bar()
            self.user_manager.adjust_permissions()

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
    
    def __init__(self, usuario, theme_colors, size=32):
        super().__init__()
        self.usuario = usuario
        self.theme_colors = theme_colors # Armazena as cores
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
        
        # Desenhar círculo de fundo usando a cor de destaque do tema
        painter.setPen(Qt.NoPen)
        # USA A COR DO TEMA AQUI!
        painter.setBrush(QColor(self.theme_colors.get('accent_color', '#007AFF'))) 
        painter.drawEllipse(0, 0, self.size, self.size)
        
        # Adicionar iniciais com cor branca (geralmente fica bom em qualquer accent color)
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

class UserMenuWidget(QFrame):
    """Widget do menu do usuário"""
    
    profile_requested = pyqtSignal()
    password_change_requested = pyqtSignal()
    admin_requested = pyqtSignal()
    logout_requested = pyqtSignal()
    
    def __init__(self, usuario, theme_colors):
        super().__init__()
        self.usuario = usuario
        self.theme_colors = theme_colors
        self.setup_ui()
        self.setup_menu()
        self.apply_styles() 
    
    def setup_ui(self):
        """Configura a interface do widget"""
        self.setObjectName("userContainer")
        self.setCursor(Qt.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)
        
        self.avatar_widget = UserAvatarWidget(self.usuario, self.theme_colors, 28)
        layout.addWidget(self.avatar_widget)
        
        self.name_label = QLabel(self.get_first_name())
        layout.addWidget(self.name_label)
        
        self.dropdown_button = QPushButton()
        self.dropdown_button.setFixedSize(20, 20)
        self.dropdown_button.setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.dropdown_button)
        
        self.dropdown_button.clicked.connect(self.show_menu)
        self.mousePressEvent = self.on_click

    def apply_styles(self):
        """Configura os estilos do widget com base no tema."""
        colors = self.theme_colors
        text_color = colors.get('text_color', '#cdd9e5')
        text_secondary = colors.get('text_secondary', '#768390')
        surface_color = colors.get('surface_color', '#22272e')
        menu_color = colors.get('menu_color', '#22272e')
        border_color = colors.get('border_color', '#373e47')
        accent_color = colors.get('accent_color', '#007AFF')

        self.setStyleSheet(f"""
            #userContainer {{
                background-color: {surface_color};
                border-radius: 18px;
                border: 1px solid {border_color};
            }}
            #userContainer:hover {{
                border-color: {accent_color};
            }}
            QLabel {{
                color: {text_color};
                font-weight: bold;
                font-size: 10pt;
                background-color: transparent;
            }}
            QPushButton {{
                background-color: transparent; border: none; padding: 0;
            }}
        """)
        
        # ATUALIZAÇÃO: Ícone do dropdown usando IconManager
        self.dropdown_button.setIcon(IconManager.get_icon('chevron_down', color=text_secondary))
        
        self.menu.setStyleSheet(f"""
            QMenu {{
                background-color: {menu_color}; color: {text_color};
                border: 1px solid {border_color}; border-radius: 8px;
                padding: 5px; min-width: 180px;
            }}
            QMenu::item {{
                padding: 10px 15px; border-radius: 6px; margin: 2px;
            }}
            QMenu::item:selected {{
                background-color: {accent_color}; color: white;
            }}
            QMenu::separator {{
                height: 1px; background-color: {border_color}; margin: 5px;
            }}
        """)
    
    def setup_menu(self):
        """Configura o menu dropdown"""
        self.menu = QMenu(self)
        self.add_menu_actions()
    
    def add_menu_actions(self):
        """Adiciona as ações ao menu"""
        text_color = self.theme_colors.get('text_color', '#cdd9e5')
        
        # Ação de perfil - USA ICONMANAGER
        profile_action = QAction(IconManager.get_icon('profile', color=text_color), "Meu Perfil", self)
        profile_action.triggered.connect(self.profile_requested.emit)
        self.menu.addAction(profile_action)
        
        # Ação de alterar senha - USA ICONMANAGER
        password_action = QAction(IconManager.get_icon('password', color=text_color), "Alterar Senha", self)
        password_action.triggered.connect(self.password_change_requested.emit)
        self.menu.addAction(password_action)
        
        # Separador e ação de admin (se aplicável)
        if self.is_admin():
            self.menu.addSeparator()
            # USA ICONMANAGER
            admin_action = QAction(IconManager.get_icon('admin', color=text_color), "Administração", self)
            admin_action.triggered.connect(self.admin_requested.emit)
            self.menu.addAction(admin_action)
        
        # Separador e logout
        self.menu.addSeparator()
        # USA ICONMANAGER
        logout_action = QAction(IconManager.get_icon('logout', color=text_color), "Sair", self)
        logout_action.triggered.connect(self.logout_requested.emit)
        self.menu.addAction(logout_action)
    
    def show_menu(self):
        """Exibe o menu dropdown"""
        menu_pos = self.mapToGlobal(self.rect().bottomLeft())
        menu_pos.setX(menu_pos.x() - 10)
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
            #self.main_window.menuBar().setCornerWidget(self.user_menu_widget, Qt.TopRightCorner)
            
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
            
            # ATUALIZAÇÃO: Passe self.main_window.theme_colors
            profile_dialog = ProfileWindow(self.db, self.usuario, self.main_window.theme_colors)
            
            self.active_dialogs['profile'] = profile_dialog
            profile_dialog.finished.connect(lambda: self.cleanup_dialog('profile'))
            
            if profile_dialog.exec_() == QDialog.Accepted:
                self.update_user_info()
                
        except Exception as e:
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao abrir perfil: {str(e)}")
    
    # Em ui/main_window.py, dentro da classe UserManager

    def change_password(self):
        """Abre a janela de alteração de senha"""
        try:
            if 'password' in self.active_dialogs:
                self.active_dialogs['password'].raise_()
                return
            
            from ui.change_password_window import ChangePasswordWindow
            
            # --- CORREÇÃO PRINCIPAL AQUI ---
            # A MainWindow é referenciada como self.main_window.
            # Passamos o dicionário de temas dela para o diálogo.
            password_dialog = ChangePasswordWindow(self.db, self.usuario['id'], self.main_window.theme_colors)
            
            self.active_dialogs['password'] = password_dialog
            
            # Conectar sinal de finalização
            password_dialog.finished.connect(lambda: self.cleanup_dialog('password'))
            
            password_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao abrir alteração de senha: {str(e)}")
    
    def open_admin(self):
        """Abre a janela de administração"""
        try:
            if self.usuario.get('tipo', '').lower() != 'admin':
                QMessageBox.warning(self.main_window, "Acesso Negado",
                                  "Você não tem permissões de administrador.")
                return
            
            if 'admin' in self.active_dialogs:
                self.active_dialogs['admin'].raise_()
                return
            
            from ui.admin_window import AdminWindow
            
            # --- ATUALIZAÇÃO PRINCIPAL AQUI ---
            # Passe o dicionário de temas da janela principal para a AdminWindow
            admin_dialog = AdminWindow(self.db, self.usuario, self.main_window.theme_colors)
            
            self.active_dialogs['admin'] = admin_dialog
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
    def __init__(self, settings, theme_colors, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_colors = theme_colors  # Recebe as cores do tema!
        
        self.initUI()
        self.apply_styles() # Aplica o estilo baseado no tema

    def initUI(self):
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(550)
        self.setObjectName("configDialog")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # --- Título ---
        title_label = QLabel("Configurações do Sistema")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setObjectName("dialogTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # --- Grupo de Aparência ---
        appearance_group = QGroupBox("Aparência")
        appearance_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        appearance_layout = QFormLayout(appearance_group)
        appearance_layout.setLabelAlignment(Qt.AlignLeft)
        appearance_layout.setSpacing(10)
        
        # Tema
        self.tema_combo = QComboBox()
        self.tema_combo.addItem(IconManager.get_icon('estoque', color=self.theme_colors['text_color']), "Tema Claro", "light")
        self.tema_combo.addItem(IconManager.get_icon('estoque', color=self.theme_colors['text_color']), "Tema Escuro", "dark")
        current_theme = self.settings.get_theme()
        index = self.tema_combo.findData(current_theme)
        if index != -1:
            self.tema_combo.setCurrentIndex(index)
        
        appearance_layout.addRow(self.create_label_with_icon("Tema:", "config"), self.tema_combo)
        
        main_layout.addWidget(appearance_group)

        # --- Grupo de Notificações ---
        notification_group = QGroupBox("Notificações por E-mail")
        notification_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        notification_layout = QVBoxLayout(notification_group)
        notification_layout.setSpacing(10)

        self.enable_notifications_check = QCheckBox("Ativar resumo diário por e-mail")
        self.enable_notifications_check.setChecked(self.settings.get_notification_enabled())
        notification_layout.addWidget(self.enable_notifications_check)

        # Container para o horário
        time_form_layout = QFormLayout()
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        current_time = QTime.fromString(self.settings.get_notification_time(), "HH:mm")
        self.time_edit.setTime(current_time)
        time_form_layout.addRow(self.create_label_with_icon("Horário de Envio:", "vencimentos"), self.time_edit)
        notification_layout.addLayout(time_form_layout)

        # Container para SMTP
        smtp_form_layout = QFormLayout()
        smtp_config = self.settings.get_smtp_config()
        self.smtp_host_edit = QLineEdit(smtp_config['host'])
        self.smtp_port_edit = QSpinBox()
        self.smtp_port_edit.setRange(1, 65535)
        self.smtp_port_edit.setValue(smtp_config['port'])
        self.smtp_user_edit = QLineEdit(smtp_config['user'])
        self.smtp_pass_edit = QLineEdit(smtp_config['password'])
        self.smtp_pass_edit.setEchoMode(QLineEdit.Password)
        self.smtp_recipient_edit = QLineEdit(smtp_config['recipient'])
        
        smtp_form_layout.addRow("Servidor SMTP:", self.smtp_host_edit)
        smtp_form_layout.addRow("Porta:", self.smtp_port_edit)
        smtp_form_layout.addRow("Usuário (e-mail):", self.smtp_user_edit)
        smtp_form_layout.addRow("Senha:", self.smtp_pass_edit)
        smtp_form_layout.addRow(self.create_label_with_icon("Enviar para:", "send"), self.smtp_recipient_edit)
        notification_layout.addLayout(smtp_form_layout)
        
        main_layout.addWidget(notification_group)
        main_layout.addStretch()

        # --- Botões ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.setObjectName("cancelButton")
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', color=self.theme_colors['text_color']))
        self.cancelar_btn.clicked.connect(self.reject)
        
        self.salvar_btn = QPushButton("Salvar Alterações")
        self.salvar_btn.setObjectName("saveButton")
        self.salvar_btn.setIcon(IconManager.get_icon('save', color='white'))
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)

        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        main_layout.addLayout(button_layout)
    
    def create_label_with_icon(self, text, icon_name):
        """Cria um QHBoxLayout com um ícone e um texto para usar como label."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        icon = IconManager.get_icon(icon_name, color=icon_color).pixmap(16, 16)
        icon_label.setPixmap(icon)
        
        text_label = QLabel(text)
        
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        layout.addStretch()
        
        return widget

    def apply_styles(self):
        """Aplica o estilo dinâmico com base nas cores do tema."""
        theme = self.theme_colors
        style = f"""
            #configDialog {{
                background-color: {theme['bg_color']};
            }}
            #dialogTitle {{
                color: {theme['text_color']};
                margin-bottom: 10px;
            }}
            QGroupBox {{
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 8px;
                margin-top: 10px;
                padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px 5px 10px;
                color: {theme['accent_color']};
            }}
            QLabel, QCheckBox {{
                color: {theme['text_color']};
                font-size: 10pt;
            }}
            QLineEdit, QComboBox, QSpinBox, QTimeEdit {{
                background-color: {theme['surface_color']};
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 4px;
                padding: 6px;
                font-size: 10pt;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {{
                border: 1px solid {theme['accent_color']};
            }}
            /* Botão de Salvar (Ação Primária) */
            #saveButton {{
                background-color: {theme['accent_color']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            #saveButton:hover {{
                background-color: #0069d9; /* Um pouco mais escuro no hover */
            }}
            /* Botão de Cancelar (Ação Secundária) */
            #cancelButton {{
                background-color: transparent;
                color: {theme['text_color']};
                border: 1px solid {theme['border_color']};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            #cancelButton:hover {{
                background-color: {theme['button_hover']};
                border-color: {theme['text_color']};
            }}
        """
        self.setStyleSheet(style)

    def salvar_configuracoes(self):
        """Salva TODAS as configurações."""
        # Salva configurações de tema
        tema = self.tema_combo.currentData()
        self.settings.set_theme(tema)

        # Salva as configurações de notificação
        self.settings.set_notification_enabled(self.enable_notifications_check.isChecked())
        self.settings.set_notification_time(self.time_edit.time().toString("HH:mm"))

        new_smtp_config = {
            "host": self.smtp_host_edit.text(),
            "port": self.smtp_port_edit.value(),
            "user": self.smtp_user_edit.text(),
            "password": self.smtp_pass_edit.text(),
            "recipient": self.smtp_recipient_edit.text()
        }
        self.settings.set_smtp_config(new_smtp_config)
        
        self.accept()

# Adicionar esta linha se ainda não existir:
from PyQt5.QtWidgets import QApplication

class AlertDialog(QDialog):
    """Dialog customizado, integrado ao tema e visualmente aprimorado para alertas."""
    
    def __init__(self, parent, title, message, alert_type="info", theme_colors=None):
        super().__init__(parent)
        self.alert_type = alert_type
        self.theme_colors = theme_colors or self._get_default_colors()
        self.title_text = title
        
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint) # Janela sem bordas padrão
        self.setAttribute(Qt.WA_TranslucentBackground) # Para cantos arredondados

        self._setup_alert_info()
        self.setup_ui(message)
        self.setup_animation()

        # Permitir arrastar a janela
        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def _get_default_colors(self):
        """Fornece cores padrão caso o tema não seja passado."""
        return {
            'bg_color': "#ffffff", 'surface_color': "#f2f2f7", 'text_color': "#000000",
            'border_color': "#d1d1d6", 'accent_color': "#007AFF"
        }

    def _setup_alert_info(self):
        """Define ícone e cor com base no tipo de alerta."""
        alerts = {
            "critical": {"icon": "delete", "color": "#d73a49", "pulse": "#ffcdd2", "prefix": "🚨"},
            "warning":  {"icon": "estoque_baixo", "color": "#ffc107", "pulse": "#fff8e1", "prefix": "⏰"},
            "stock":    {"icon": "check_stock", "color": "#007AFF", "pulse": "#bbdefb", "prefix": "📦"},
            "info":     {"icon": "sobre", "color": "#2196f3", "pulse": "#e3f2fd", "prefix": "ℹ️"}
        }
        self.alert_info = alerts.get(self.alert_type, alerts["info"])

    def setup_ui(self, message):
        # Widget de container principal para ter cantos arredondados e sombra
        container = QFrame(self)
        container.setObjectName("alertDialogContainer")
        
        # Layout geral
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(1, 1, 1, 1) # Borda será o padding
        main_layout.setSpacing(0)

        self.setLayout(QVBoxLayout()) # Layout principal do QDialog
        self.layout().addWidget(container)
        self.layout().setContentsMargins(0,0,0,0)

        # --- Cabeçalho ---
        header = QFrame()
        header.setObjectName("alertHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        icon_label = QLabel()
        icon_pixmap = IconManager.get_icon(self.alert_info['icon'], color='white').pixmap(QSize(28, 28))
        icon_label.setPixmap(icon_pixmap)
        
        title_label = QLabel(f"{self.alert_info['prefix']} {self.title_text}")
        title_label.setObjectName("alertTitle")
        
        header_layout.addWidget(icon_label)
        header_layout.addSpacing(10)
        header_layout.addWidget(title_label, 1)

        # --- Corpo ---
        body = QFrame()
        body.setObjectName("alertBody")
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(20, 15, 20, 20)
        
        self.text_area = QTextEdit()
        self.text_area.setMarkdown(message.replace("\n", "  \n")) # Suporte a Markdown para negrito, etc.
        self.text_area.setReadOnly(True)
        self.text_area.setObjectName("alertTextArea")
        
        # --- Rodapé com Botão ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Entendido")
        ok_button.setObjectName("okButton")
        ok_button.clicked.connect(self.accept)
        ok_button.setCursor(Qt.PointingHandCursor)
        button_layout.addWidget(ok_button)

        body_layout.addWidget(self.text_area)
        body_layout.addSpacing(15)
        body_layout.addLayout(button_layout)
        
        main_layout.addWidget(header)
        main_layout.addWidget(body)

        # Aplicar estilo inicial
        self.apply_style(self.alert_info['color'])

    def apply_style(self, border_color):
        style = f"""
        #alertDialogContainer {{
            background-color: {self.theme_colors['surface_color']};
            border: 2px solid {border_color};
            border-radius: 12px;
        }}
        #alertHeader {{
            background-color: {border_color};
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }}
        #alertTitle {{
            color: white;
            font-size: 14pt;
            font-weight: bold;
        }}
        #alertBody {{
            background-color: {self.theme_colors['surface_color']};
            border-bottom-left-radius: 10px;
            border-bottom-right-radius: 10px;
        }}
        #alertTextArea {{
            background-color: {self.theme_colors['bg_color']};
            color: {self.theme_colors['text_color']};
            border: 1px solid {self.theme_colors['border_color']};
            border-radius: 6px;
            font-size: 10pt;
            padding: 8px;
        }}
        #okButton {{
            background-color: {self.alert_info['color']};
            color: white;
            font-weight: bold;
            font-size: 10pt;
            padding: 8px 25px;
            border-radius: 6px;
            border: none;
        }}
        #okButton:hover {{
            background-color: {self.theme_colors['button_hover']};
            color: {self.theme_colors['text_color']};
            border: 1px solid {self.alert_info['color']};
        }}
        """
        self.setStyleSheet(style)
        self.setMinimumSize(600, 400)

    def setup_animation(self):
        if self.alert_type in ["critical", "warning"]:
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.pulse_effect)
            self.pulse_state = False
            self.timer.start(700)

    def pulse_effect(self):
        border_color = self.theme_colors['surface_color'] if self.pulse_state else self.alert_info['color']
        self.apply_style(border_color)
        self.pulse_state = not self.pulse_state