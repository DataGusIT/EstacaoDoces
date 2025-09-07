# main.py

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QStackedWidget, QHBoxLayout, QFrame,
                            QAction, QMenu, QToolBar, QDialog, QFormLayout,
                            QComboBox, QSpinBox, QMessageBox, QStatusBar, QSizePolicy, QTimeEdit, QLineEdit, QCheckBox, QGroupBox, QDateEdit, QTextEdit, QTableWidgetItem,  QTabWidget, QTableWidget, QHeaderView,  QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QIcon, QPixmap, QCursor, QPainter, QColor, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QDate, QSize, QByteArray, QPropertyAnimation, QEasingCurve, pyqtSignal, QTime, QTimer, QSettings, QPoint
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

# ====================================================================
#       1. ADICIONE ESTA NOVA CLASSE AO FINAL DO ARQUIVO
# ====================================================================
class SearchInputWidget(QFrame):
    """Um widget customizado que combina um ícone e um QLineEdit."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("searchInputFrame")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 5, 0)
        layout.setSpacing(8)

        self.icon_label = QLabel(self)
        
        self.line_edit = QLineEdit(self)
        self.line_edit.setObjectName("globalSearchInput")
        self.line_edit.setPlaceholderText("Buscar produto, cliente, promo...")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.line_edit)

    def set_icon(self, icon):
        self.icon_label.setPixmap(icon.pixmap(16, 16))



class MainWindow(QMainWindow):
    def __init__(self, db, settings, theme_colors):
        super().__init__()
        self.db = db
        self.settings = settings
        self.theme_colors = theme_colors 
        self.menu_collapsed = True
        self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
        
        # Primeiro, carregamos a logo para que self.logo_pixmap exista
        self.carregar_logo() 
        
        # Agora, podemos construir a UI que depende da logo
        self.initUI()
        self.check_promocoes_ativas()

    # main.py

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
        # Agora usamos diretamente o atributo da classe que foi carregado no __init__
        if not self.logo_pixmap.isNull():
            self.app_logo.setPixmap(self.logo_pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.app_logo.setFixedSize(60, 60)

        app_title = QLabel("Sistema de Estoque - GestorX")
        app_title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        app_title.setObjectName("appTitle")
        
        header_layout.addWidget(self.app_logo)
        header_layout.addWidget(app_title)
        
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

        # --- BARRA DE BUSCA GLOBAL (USANDO O NOVO WIDGET) ---
        self.search_widget = SearchInputWidget()
        self.search_widget.setMinimumWidth(300)
        self.search_widget.setMaximumWidth(400)
        self.search_widget.line_edit.textChanged.connect(self.atualizar_busca_global)
        header_layout.addWidget(self.search_widget)

        header_layout.addStretch()
        
        self.refresh_button = QPushButton("Atualizar")
        self.refresh_button.setObjectName("primaryActionButton")
        self.refresh_button.setCursor(Qt.PointingHandCursor)
        self.refresh_button.clicked.connect(self.atualizar_dados)
        header_layout.addWidget(self.refresh_button)
        
        self.notification_btn = QPushButton()
        self.notification_btn.setObjectName("headerIconButton")
        self.notification_btn.setFixedSize(36, 36)
        self.notification_btn.setCursor(Qt.PointingHandCursor)
        self.notification_btn.setToolTip("Configurar Notificações")
        self.notification_btn.clicked.connect(self.abrir_configuracoes_notificacao)
        header_layout.addWidget(self.notification_btn)

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

        self.search_results_popup = QListWidget(self)
        self.search_results_popup.setObjectName("searchResultsPopup")
        self.search_results_popup.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.search_results_popup.setFocusPolicy(Qt.NoFocus)
        self.search_results_popup.itemClicked.connect(self.item_busca_selecionado)
        self.search_results_popup.hide()

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

        self.dashboard_page = DashboardWindow(self.db, theme_colors)
        self.estoque_page = EstoqueWindow(self.db, theme_colors, self.settings, self.logo_pixmap)
        self.fornecedor_page = FornecedorWindow(self.db, theme_colors, self.settings)
        self.promocoes_page = PromocoesWindow(self.db, theme_colors)
        self.clientes_page = ClientesWindow(self.db, theme_colors)
        self.caixa_page = CaixaWindow(self.db, theme_colors, self.settings)

        # ==================== INÍCIO DA CORREÇÃO ====================
        # Corrigido para usar os nomes de atributo corretos: _page em vez de _window
        self.caixa_page.venda_finalizada.connect(self.dashboard_page.carregar_dados)
        # ===================== FIM DA CORREÇÃO ======================

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

        self.user_status_widget = QFrame()
        self.user_status_widget.setObjectName("userStatusWidget")
        status_layout = QHBoxLayout(self.user_status_widget)
        status_layout.setContentsMargins(8, 2, 8, 2)
        status_layout.setSpacing(6)

        self.status_user_icon = QLabel()
        status_layout.addWidget(self.status_user_icon)
        self.status_user_label = QLabel("Usuário")
        self.status_user_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_user_label)

        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("statusSeparator")
        status_layout.addWidget(separator)
        
        self.status_profile_icon = QLabel()
        status_layout.addWidget(self.status_profile_icon)
        self.status_profile_label = QLabel("Perfil")
        self.status_profile_label.setObjectName("statusLabel")
        status_layout.addWidget(self.status_profile_label)
        
        self.statusBar.addPermanentWidget(self.user_status_widget)
        
        self.toggle_menu()
        self.switch_page(0)
        self.aplicar_tema()

        if hasattr(self.clientes_page, 'dados_clientes_alterados'):
            self.clientes_page.dados_clientes_alterados.connect(self.on_dados_clientes_changed)
        if hasattr(self.estoque_page, 'dados_produtos_alterados'):
            self.estoque_page.dados_produtos_alterados.connect(self.on_dados_produtos_changed)
        if hasattr(self.fornecedor_page, 'dados_fornecedores_alterados'):
            self.fornecedor_page.dados_fornecedores_alterados.connect(self.on_dados_fornecedores_changed)
        if hasattr(self.caixa_page, 'movimento_manual_registrado'):
            self.caixa_page.movimento_manual_registrado.connect(self.dashboard_page.carregar_dados)
        
        self.notification_manager = NotificationManager(self.db, self.settings)
        self.scheduler = Scheduler(self.settings)
        self.scheduler.notification_triggered.connect(self.notification_manager.check_and_send_notifications)
        self.scheduler.log_message.connect(self.log_scheduler_message)
        self.scheduler.start()

        self.show()

    def showEvent(self, event):
        """
        Evento chamado pouco antes de a janela ser exibida.
        Usamos para garantir que a janela sempre apareça no estado e posição corretos.
        """
        # --- CORREÇÃO APLICADA AQUI (NOVO MÉTODO) ---
        # 1. Garante que a janela não está minimizada ou maximizada ao ser reexibida.
        #    Isso resolve o aviso 'Tight layout not applied'.
        self.setWindowState(Qt.WindowNoState)

        # 2. Re-centraliza a janela na tela toda vez que ela for mostrada.
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_geometry = self.frameGeometry()
        window_geometry.moveCenter(screen_geometry.center())
        self.move(window_geometry.topLeft())

        # 3. Prepara a janela para a animação de fade-in.
        self.setWindowOpacity(0.0)

        # Chama a implementação original do evento para que a janela seja de fato preparada para ser mostrada.
        super().showEvent(event)
        
        # 4. Inicia a animação de fade-in agora que a janela tem o tamanho e posição corretos.
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(400)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.start()

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
        """Carrega a logo personalizada ou a padrão e armazena em self.logo_pixmap."""
        logo_path = self.settings.get_value("custom_logo_path", "")
        
        # Se o caminho personalizado não for válido, usa o caminho padrão
        if not logo_path or not os.path.exists(logo_path):
            logo_path = "assets/img/Logo2.png"  # Certifique-se que este é o caminho correto do seu logo padrão
        
        self.logo_pixmap = QPixmap(logo_path)
        
        # Opcional: Atualiza o ícone da própria janela principal
        if not self.logo_pixmap.isNull():
            self.setWindowIcon(QIcon(self.logo_pixmap))
    
    def carregar_logo_pixmap(self):
        """Carrega a logo (personalizada ou padrão) como QPixmap para uso no cabeçalho."""
        
        # --- INÍCIO DA CORREÇÃO ---
        # Usamos QSettings aqui para ler a configuração salva localmente
        local_settings = QSettings("SuaEmpresa", "SeuERP")
        logo_path = local_settings.value("custom_logo_path", "")
        # --- FIM DA CORREÇÃO ---
        
        # O resto da função continua exatamente como antes
        if not logo_path or not os.path.exists(logo_path):
            logo_path = os.path.join("assets", "img", "Logo2.png")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            return pixmap.scaled(60, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            print(f"ATENÇÃO: Arquivo de logo não encontrado no caminho: {logo_path}")
            return None
        
    # NOVO MÉTODO para ser chamado pelo sinal da AdminWindow
    def recarregar_logo_dinamico(self):
        """Recarrega a logo na interface principal sem precisar reiniciar."""
        print("Sinal recebido: Recarregando a logo...")
        logo_pixmap = self.carregar_logo_pixmap()
        if logo_pixmap:
            self.app_logo.setPixmap(logo_pixmap)
    
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
        """Atualiza o ícone de maximizar/restaurar e restaura a opacidade."""
        if event.type() == event.WindowStateChange:
            # --- CORREÇÃO PARA RESTAURAR JANELA MINIMIZADA ---
            # Se o novo estado da janela NÃO for minimizado, significa que
            # ela foi restaurada ou maximizada. Portanto, resetamos a opacidade.
            if not (self.windowState() & Qt.WindowMinimized):
                self.setWindowOpacity(1.0)
            # --- FIM DA CORREÇÃO ---

            # Lógica existente para trocar o ícone de maximizar/restaurar
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
                'bg_color': "#1c2128", 
                'surface_color': "#22272e", 
                'menu_color': "#22272e",
                'text_color': "#cdd9e5", 
                'text_secondary': "#768390", 
                'border_color': "#373e47",
                'button_hover': "#373e47", 
                'accent_color': "#007AFF"
            }
        else:
            # ================================================================= #
            #       CORREÇÃO APLICADA AQUI PARA UM TEMA CLARO MAIS SUAVE        #
            # ================================================================= #
            return {
                'bg_color': "#f8f9fa",       # Fundo: Cinza muito claro (off-white)
                'surface_color': "#ffffff",  # Superfície: Branco puro para contraste sutil
                'menu_color': "#ffffff",     # Menu: Branco, para combinar com a superfície
                'text_color': "#212529",     # Texto: Cinza escuro, menos forte que o preto
                'text_secondary': "#6c757d", # Texto secundário: Cinza médio
                'border_color': "#dee2e6",   # Bordas: Cinza claro e suave
                'button_hover': "#e9ecef",   # Hover do botão: Cinza um pouco mais escuro
                'accent_color': "#007AFF"    # Cor de destaque: Permanece a mesma
            }

     # Adicione este novo método DENTRO da classe MainWindow
    def atualizar_busca_global(self, texto):
        """Chamado sempre que o texto na barra de busca muda."""
        if len(texto) < 2:
            self.search_results_popup.hide()
            return

        resultados = self.db.busca_global(texto)
        self.search_results_popup.clear()

        if not resultados:
            self.search_results_popup.hide()
            return
        
        icon_map = {
            'produto': 'produto', 'cliente': 'cliente',
            'fornecedor': 'fornecedor', 'promocao': 'promocao'
        }
        
        for res in resultados:
            icon_name = icon_map.get(res['tipo'], 'search')
            icon = IconManager.get_icon(icon_name, color=self.theme_colors.get('text_color'))
            
            item = QListWidgetItem(icon, res['texto'])
            item_data = {'id': res['id'], 'tipo': res['tipo']}
            item.setData(Qt.UserRole, item_data)
            self.search_results_popup.addItem(item)
            
        # --- CORREÇÃO APLICADA AQUI ---
        # A posição e a largura agora são baseadas no self.search_widget (o frame)
        point = self.search_widget.mapToGlobal(QPoint(0, self.search_widget.height()))
        self.search_results_popup.move(point)
        self.search_results_popup.setFixedWidth(self.search_widget.width())
        self.search_results_popup.show()

    # SUBSTITUA ESTE MÉTODO INTEIRO TAMBÉM
    def item_busca_selecionado(self, item):
        """Chamado quando um item do dropdown de busca é clicado."""
        data = item.data(Qt.UserRole)
        item_id = data['id']
        item_tipo = data['tipo']

        self.search_results_popup.hide()
        # --- CORREÇÃO APLICADA AQUI ---
        # Limpa o texto do QLineEdit que está DENTRO do search_widget
        self.search_widget.line_edit.clear()

        page_map = {
            'produto': (1, self.estoque_page),
            'cliente': (4, self.clientes_page),
            'fornecedor': (2, self.fornecedor_page),
            'promocao': (3, self.promocoes_page)
        }

        if item_tipo in page_map:
            page_index, page_widget = page_map[item_tipo]
            
            self.switch_page(page_index)
            
            if hasattr(page_widget, 'selecionar_item_por_id'):
                QTimer.singleShot(100, lambda: page_widget.selecionar_item_por_id(item_id))
            else:
                print(f"AVISO: O método 'selecionar_item_por_id' não foi encontrado em {page_widget.__class__.__name__}")
    
    def aplicar_tema(self):
        """Aplica o tema atual a todos os componentes, centralizando o estilo."""
        theme = self._get_theme_colors()
        self.theme_colors = theme
        accent_color = theme['accent_color']
        text_color = theme['text_color']
        text_secondary = theme['text_secondary']
        bg_color = theme['bg_color']
        surface_color = theme['surface_color']
        border_color = theme['border_color']
        button_hover = theme['button_hover']

        icon_color = theme.get('text_secondary', '#768390')
        self.status_user_icon.setPixmap(IconManager.get_icon('user', color=icon_color).pixmap(14, 14))
        self.status_profile_icon.setPixmap(IconManager.get_icon('profile_type', color=icon_color).pixmap(14, 14))

        self.hamburger_btn.setIcon(IconManager.get_icon('menu', text_color))
        self.refresh_button.setIcon(IconManager.get_icon('atualizar', 'white')) 
        self.notification_btn.setIcon(IconManager.get_icon('notification', text_secondary))
        self.minimize_btn.setIcon(IconManager.get_icon('minimizar', text_secondary))
        self.maximize_btn.setIcon(IconManager.get_icon('maximizar' if not self.isMaximized() else 'restaurar', text_secondary))
        self.close_btn.setIcon(IconManager.get_icon('fechar', text_secondary))
        
        # Define o ícone da busca no novo widget
        self.search_widget.set_icon(IconManager.get_icon('search', color=text_secondary))
        
        self.switch_page(self.stack.currentIndex())
        
        # Aplica a folha de estilo principal
        self.setStyleSheet(f"""
            QMainWindow, #centralWidget, QDialog {{
                background-color: {bg_color};
                color: {text_color};
            }}

             QStatusBar {{
                background-color: {theme['menu_color']};
                border-top: 1px solid {theme['border_color']};
            }}
            QStatusBar::item {{ border: none; }}
            #userStatusWidget {{
                background-color: {theme['surface_color']};
                border: 1px solid {theme['border_color']};
                border-radius: 8px;
                margin-right: 5px;
            }}
            #statusLabel {{
                color: {theme['text_color']};
                font-weight: bold;
                font-size: 8pt;
            }}
            #statusSeparator {{ background-color: {theme['border_color']}; }}

            /* CORREÇÃO E MELHORIA DA BARRA DE BUSCA */
            /* ESTILO CORRIGIDO E ROBUSTO PARA A BARRA DE BUSCA */
            #searchInputFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 2px;
            }}
            #searchInputFrame:focus-within {{
                border: 1px solid {accent_color};
            }}
            #globalSearchInput {{
                background-color: transparent;
                border: none;
                font-size: 10pt;
                padding: 6px;
            }}

            /* ESTILO PARA O DROPDOWN DE RESULTADOS */
            #searchResultsPopup {{
                background-color: {surface_color};
                color: {text_color};
                border: 1px solid {accent_color};
                border-radius: 6px;
                padding: 4px;
            }}
            #searchResultsPopup::item {{ padding: 8px; border-radius: 4px; }}
            #searchResultsPopup::item:hover {{ background-color: {button_hover}; }}
            #searchResultsPopup::item:selected {{ background-color: {accent_color}; color: white; }}

            QMenu {{
                background-color: {theme['menu_color']};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 5px;
            }}
            QMenu::item {{
                padding: 8px 20px;
                border-radius: 6px;
                margin: 2px;
            }}
            QMenu::item:selected {{
                background-color: {accent_color};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {border_color};
                margin: 5px;
            }}
            
            /* --- CORREÇÃO 2: Adiciona a regra para o texto dos botões inativos do menu --- */
            #menuButton #buttonText {{
                color: {theme['text_color']};
            }}
            #menuButton[active="true"] #buttonText {{
                color: white; /* O texto do botão ativo é sempre branco */
            }}
            /* --- FIM DA CORREÇÃO --- */

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
                border: 1px solid {border_color};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: url(assets/img/chevron-down.png);
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

            /* ========================================================= */
            /*       INÍCIO DA MODIFICAÇÃO: ESTILO DO BOTÃO DE SINO      */
            /* ========================================================= */
            #headerIconButton {{
                background-color: transparent;
                border: 1px solid {border_color};
                border-radius: 6px;
            }}
            #headerIconButton:hover {{
                background-color: {button_hover};
                border-color: {accent_color};
            }}
            #headerIconButton:pressed {{
                background-color: {border_color};
            }}
            /* ========================================================= */
            /*       FIM DA MODIFICAÇÃO                                  */
            /* ========================================================= */
            
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
/* ================================================================= */
        /*       CORREÇÃO APLICADA AQUI                                      */
        /* ================================================================= */
        
        /* 1. Estilo do BOTÃO. Note que a propriedade 'color' foi REMOVIDA. */
        #menuButton {{
            background-color: transparent;
            border: none;
            text-align: left; 
            padding: 8px;
            border-radius: 8px;
        }}
        #menuButton:hover {{
            background-color: {theme['button_hover']};
        }}
        /* A propriedade 'color' também foi removida daqui */
        #menuButton[active="true"] {{
            background-color: {theme['accent_color']};
        }}

        /* 2. NOVAS REGRAS DIRETAMENTE PARA O TEXTO (QLabel) dentro do botão */
        
        /* Cor do texto para o botão INATIVO */
        #menuButton #buttonText {{
            color: {theme['text_color']};
        }}
        /* Cor do texto para o botão ATIVO (sempre branco) */
        #menuButton[active="true"] #buttonText {{
            color: white;
        }}

        /* --- FIM DA CORREÇÃO --- */
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

        if hasattr(self, 'user_manager') and self.user_manager:
            self.user_manager.update_ui_for_theme(theme)
        
        self.update()
        if hasattr(self, 'repaint'):
            self.repaint()

    def aplicar_tema_completo(self):
        """Aplica tema em todos os widgets, incluindo janela principal"""
        self.aplicar_tema()
    
    # =========================================================
    #       INÍCIO DA MODIFICAÇÃO: NOVO MÉTODO
    # =========================================================
    def abrir_configuracoes_notificacao(self):
        """Abre a janela de configurações de notificação."""
        theme_colors = self._get_theme_colors()
        dialog = NotificationConfigDialog(self.settings, theme_colors, self)

        if dialog.exec_() == QDialog.Accepted:
            # Reinicia o agendador para aplicar novas configurações de notificação
            self.scheduler.restart()
            alert = AlertDialog(self, 
                                "Configurações Salvas", 
                                "As configurações de notificação foram atualizadas com sucesso!",
                                alert_type="info", 
                                theme_colors=self._get_theme_colors())
            alert.exec_()
    # =========================================================
    #       FIM DA MODIFICAÇÃO
    # =========================================================

    # =================================================================================
    #       INÍCIO DA SUGESTÃO: ADICIONE ESTE NOVO MÉTODO DENTRO DA CLASSE MAINWINDOW
    # =================================================================================
    def executar_busca_global(self):
        """Executa a busca com o termo do QLineEdit e exibe os resultados."""
        termo = self.global_search_input.text().strip()
        if not termo:
            return

        print(f"Buscando por: '{termo}'...")
        self.statusBar.showMessage(f"Buscando por: '{termo}'...", 2000)
        
        resultados = self.db.busca_global(termo)
        
        total_encontrado = len(resultados['produtos']) + len(resultados['clientes']) + len(resultados['fornecedores'])
        
        if total_encontrado == 0:
            QMessageBox.information(self, "Busca", f"Nenhum resultado encontrado para '{termo}'.")
            return
        
        dialog = GlobalSearchResultsDialog(resultados, self._get_theme_colors(), self)
        dialog.exec_()

    # =================================================================================
    #       FIM DO NOVO MÉTODO
    # =================================================================================

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
            
            # ATENÇÃO: A linha abaixo foi movida para 'abrir_configuracoes_notificacao'
            # self.scheduler.restart()

            alert = AlertDialog(self, 
                                "Configurações Salvas", 
                                "O novo tema foi aplicado!",
                                alert_type="info", 
                                theme_colors=self._get_theme_colors())
            alert.exec_()
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
    
    # Em main.py, dentro da classe MainWindow

    def mostrar_sobre(self):
        """Mostra uma janela 'Sobre' estilizada com informações do sistema."""
        # Cria uma instância de QMessageBox para ter mais controle sobre a aparência
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Sobre o GestorX")

        # Carrega o logo do aplicativo para usar como ícone da janela
        logo_pixmap = self.carregar_logo_pixmap()
        if logo_pixmap:
            # Redimensiona o logo para um tamanho adequado para a caixa de diálogo
            dialog.setIconPixmap(logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        # Obtém as cores do tema atual para usar no texto HTML
        theme = self._get_theme_colors()
        text_color = theme['text_color']
        text_secondary = theme['text_secondary']
        accent_color = theme['accent_color']
        border_color = theme['border_color']
        surface_color = theme['surface_color']

        # Cria o conteúdo da janela usando Rich Text (HTML) para uma formatação profissional
        rich_text = f"""
        <h3 style='color: {text_color}; margin-bottom: 10px;'>GestorX - Sistema de Estoque</h3>
        <p style='color: {text_color};'><b>Versão:</b> 1.0</p>
        <p style='color: {text_secondary};'>
            Uma solução moderna e eficiente para o gerenciamento do seu negócio, 
            desenvolvida com a robustez do Python e a versatilidade da biblioteca PyQt5.
        </p>
        <hr style='border: 1px solid {border_color};'>
        <p style='color: {text_color};'>
            <b>Suporte Técnico e Sugestões:</b><br>
            Para dúvidas ou ajuda, entre em contato com nossa equipe através do e-mail:
            <br><a style='color: {accent_color}; text-decoration: none;' href='mailto:gestorxerp@gmail.com'>gestorxerp@gmail.com</a>
        </p>
        <br>
        <p style='font-size: 9pt; color: {text_secondary};'>
            © 2025 GestorX. Todos os direitos reservados.
        </p>
        """
        
        dialog.setText(rich_text)
        dialog.setTextFormat(Qt.RichText) # Informa ao QMessageBox que o texto é HTML

        # Adiciona e customiza o botão "OK"
        dialog.setStandardButtons(QMessageBox.Ok)
        dialog.button(QMessageBox.Ok).setText("Fechar")
        dialog.button(QMessageBox.Ok).setCursor(Qt.PointingHandCursor)


        # Aplica uma folha de estilos para que a janela "Sobre" combine com o tema da aplicação
        dialog.setStyleSheet(f"""
            QMessageBox {{
                background-color: {surface_color};
                border: 1px solid {border_color};
                border-radius: 8px;
            }}
            QLabel#qt_msgbox_label {{ /* Seleciona o label principal do texto */
                color: {text_color};
                font-size: 11pt;
            }}
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: none;
                padding: 8px 24px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: #0069d9; /* Um tom mais escuro da cor de destaque */
            }}
        """)

        dialog.exec_()
    
    def closeEvent(self, event):
        """Evento chamado quando a janela é fechada."""
        print("Sinalizando para o agendador de notificações parar...")
        # Apenas avisamos a thread para parar. Não esperamos por ela.
        self.scheduler.stop()
        
        # O .wait() foi REMOVIDO daqui. Esta é a correção principal para o travamento.
        
        print("Fechando a conexão com o banco de dados.")
        self.db.fechar()
        event.accept() # Aceita o evento de fechamento, permitindo que a janela feche imediatamente.

    # Em main.py, dentro da classe MainWindow

    def setup_for_user(self, usuario):
        """Configura a interface para o usuário logado e ajusta as permissões da UI."""
        try:
            if not hasattr(self, 'user_manager'):
                self.user_manager = UserManager(self, self.db) 
            
            # --- CRIAÇÃO E CONFIGURAÇÃO DO MENU DO USUÁRIO ---
            user_menu_widget = UserMenuWidget(usuario, self.theme_colors)
            user_menu_widget.profile_requested.connect(self.user_manager.open_profile)
            user_menu_widget.password_change_requested.connect(self.user_manager.change_password)
            user_menu_widget.admin_requested.connect(self.user_manager.open_admin)
            user_menu_widget.logout_requested.connect(self.user_manager.logout)

            # Limpa o placeholder antigo antes de adicionar o novo widget
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
            
            # Associa o widget ao UserManager para referência futura (opcional, mas bom)
            self.user_manager.user_menu_widget = user_menu_widget
            
            # --- ATUALIZA O ESTADO DO USERMANAGER ---
            # Chama o setup do UserManager, que agora só cuida da barra de status e estado interno
            self.user_manager.setup_for_user(usuario)

            # --- CORREÇÃO DE PERMISSÕES (MOVIDA PARA CÁ) ---
            # Agora que todos os widgets existem, ajustamos a visibilidade deles aqui.
            
            # 1. Pega o tipo de usuário de forma segura
            user_type = usuario.get('tipo') or ''
            is_admin = user_type.lower() == 'admin'

            # 2. Ajusta o botão 'Configurações' no menu lateral
            if hasattr(self, 'btn_config'):
                self.btn_config.setVisible(is_admin)

            # 3. Ajusta a ação 'Administração' no menu do usuário recém-criado
            admin_action = None
            separator_before_admin = None
            
            # Procura pela ação de admin e seu separador
            actions = user_menu_widget.menu.actions()
            for i, action in enumerate(actions):
                if "Administração" in action.text():
                    admin_action = action
                    if i > 0 and actions[i-1].isSeparator():
                        separator_before_admin = actions[i-1]
                    break
            
            # Define a visibilidade da ação e do separador
            if admin_action:
                admin_action.setVisible(is_admin)
            if separator_before_admin:
                separator_before_admin.setVisible(is_admin)

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
        """Configura os estilos do widget e ATUALIZA os ícones com base no tema."""
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
        
        self.dropdown_button.setIcon(IconManager.get_icon('chevron_down', color=text_secondary))
        
        # --- CORREÇÃO: Atualiza os ícones das ações do menu ---
        if hasattr(self, 'profile_action'):
            self.profile_action.setIcon(IconManager.get_icon('profile', color=text_color))
        if hasattr(self, 'password_action'):
            self.password_action.setIcon(IconManager.get_icon('password', color=text_color))
        if hasattr(self, 'admin_action') and self.admin_action:
            self.admin_action.setIcon(IconManager.get_icon('admin', color=text_color))
        if hasattr(self, 'logout_action'):
            self.logout_action.setIcon(IconManager.get_icon('logout', color=text_color))

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
        
        # --- CORREÇÃO: Salva referências às ações ---
        self.profile_action = QAction(IconManager.get_icon('profile', color=text_color), "Meu Perfil", self)
        self.profile_action.triggered.connect(self.profile_requested.emit)
        self.menu.addAction(self.profile_action)
        
        self.password_action = QAction(IconManager.get_icon('password', color=text_color), "Alterar Senha", self)
        self.password_action.triggered.connect(self.password_change_requested.emit)
        self.menu.addAction(self.password_action)
        
        self.admin_action = None # Inicializa como None
        if self.is_admin():
            self.menu.addSeparator()
            self.admin_action = QAction(IconManager.get_icon('admin', color=text_color), "Administração", self)
            self.admin_action.triggered.connect(self.admin_requested.emit)
            self.menu.addAction(self.admin_action)
        
        self.menu.addSeparator()
        self.logout_action = QAction(IconManager.get_icon('logout', color=text_color), "Sair", self)
        self.logout_action.triggered.connect(self.logout_requested.emit)
        self.menu.addAction(self.logout_action)
    
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

# Em main.py

# Em main.py

class UserManager:
    """Gerenciador principal do usuário na aplicação"""

    def __init__(self, main_window, db):
        self.main_window = main_window
        self.db = db
        self.usuario = None
        self.user_menu_widget = None
        self.active_dialogs = {}
    
    # =========================================================
    #       CORREÇÃO 1: MÉTODO FALTANDO ADICIONADO AQUI
    # =========================================================
    def setup_for_user(self, usuario):
        """Configura a interface para o usuário logado"""
        # Garante que o usuário sempre tenha um 'tipo'
        if not usuario.get('tipo'):
            usuario['tipo'] = 'Comum'
        
        self.usuario = usuario
        self.setup_status_bar()

    # =========================================================
    #       CORREÇÃO 2: REMOVIDA A VERSÃO DUPLICADA E ANTIGA DO MÉTODO
    # =========================================================
    def setup_status_bar(self):
        """Configura a barra de status com informações do usuário"""
        try:
            # Pega os dados do usuário logado
            nome_usuario = self.usuario.get('nome', 'Desconhecido')
            tipo_usuario = self.usuario.get('tipo', 'Indefinido')

            # Atualiza os labels corretos que estão na MainWindow
            self.main_window.status_user_label.setText(nome_usuario)
            self.main_window.status_profile_label.setText(tipo_usuario.capitalize())
            
        except Exception as e:
            print(f"Erro ao configurar barra de status: {e}")
    
    def open_profile(self):
        """Abre a janela de perfil do usuário"""
        try:
            if 'profile' in self.active_dialogs:
                self.active_dialogs['profile'].raise_()
                return
            
            if self.usuario and not self.usuario.get('tipo'):
                self.usuario['tipo'] = 'Comum'

            from ui.profile_window import ProfileWindow
            logo_pixmap = self.main_window.carregar_logo_pixmap()
            profile_dialog = ProfileWindow(self.db, self.usuario, self.main_window.theme_colors, logo_pixmap)
            
            self.active_dialogs['profile'] = profile_dialog
            profile_dialog.finished.connect(lambda: self.cleanup_dialog('profile'))
            
            if profile_dialog.exec_() == QDialog.Accepted:
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
            logo_pixmap = self.main_window.carregar_logo_pixmap()
            password_dialog = ChangePasswordWindow(self.db, self.usuario['id'], self.main_window.theme_colors, logo_pixmap)
            
            self.active_dialogs['password'] = password_dialog
            password_dialog.finished.connect(lambda: self.cleanup_dialog('password'))
            password_dialog.exec_()
            
        except Exception as e:
            QMessageBox.critical(self.main_window, "Erro", f"Erro ao abrir alteração de senha: {str(e)}")
    
    # Em UserManager (main.py ou ui/main_window.py)
    def open_admin(self):
        """Abre a janela de administração."""
        try:
            user_type = self.usuario.get('tipo') or ''
            if user_type.lower() != 'admin':
                # ... (código de acesso negado) ...
                return

            from ui.admin_window import AdminWindow
            # A chamada agora inclui o objeto 'settings' da MainWindow
            admin_dialog = AdminWindow(self.db, self.usuario, self.main_window.settings, self.main_window.theme_colors)
            admin_dialog.logo_alterado.connect(self.main_window.recarregar_logo_dinamico)

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
            self.cleanup_all_dialogs()
            
            if hasattr(self.db, 'ensure_connection'):
                self.db.ensure_connection()
            
            self.main_window.hide()
            
            from ui.login_window import LoginWindow
            login_window = LoginWindow(self.db, self.main_window.theme_colors)
            
            result = login_window.exec_()
            
            if result == QDialog.Accepted:
                new_usuario = getattr(login_window, 'usuario', None)
                if new_usuario:
                    self.main_window.setup_for_user(new_usuario)
                    self.main_window.show()
                else:
                    self.exit_application()
            else:
                self.exit_application()
                
        except Exception as e:
            print(f"Erro durante logout: {e}")
            self.exit_application()
    
    def update_user_info(self):
        """Atualiza as informações do usuário na interface"""
        try:
            self.usuario = self.db.obter_usuario_por_id(self.usuario['id'])

            if self.usuario and not self.usuario.get('tipo'):
                self.usuario['tipo'] = 'Comum'
            
            # Reutiliza a mesma lógica para atualizar a barra de status
            self.setup_status_bar()
            
            if self.user_menu_widget:
                self.user_menu_widget.usuario = self.usuario
                self.user_menu_widget.name_label.setText(self.user_menu_widget.get_first_name())
                
        except Exception as e:
            print(f"Erro ao atualizar informações do usuário: {e}")
    
    def cleanup_dialog(self, dialog_name):
        if dialog_name in self.active_dialogs:
            dialog = self.active_dialogs.pop(dialog_name)
            if dialog:
                dialog.deleteLater()
    
    def cleanup_all_dialogs(self):
        for dialog_name, dialog in list(self.active_dialogs.items()):
            if dialog:
                try:
                    dialog.close()
                    dialog.deleteLater()
                except:
                    pass
        self.active_dialogs.clear()
    
    def exit_application(self):
        try:
            self.cleanup_all_dialogs()
            self.main_window.close()
            import sys
            sys.exit(0)
        except:
            import os
            os._exit(0)
    
    def update_ui_for_theme(self, theme_colors):
        """
        Atualiza todos os componentes da UI gerenciados pelo UserManager para refletir a mudança de tema.
        """
        if hasattr(self, 'user_menu_widget') and self.user_menu_widget:
            self.user_menu_widget.theme_colors = theme_colors
            self.user_menu_widget.apply_styles()
            
            if hasattr(self.user_menu_widget, 'avatar_widget'):
                self.user_menu_widget.avatar_widget.theme_colors = theme_colors
                self.user_menu_widget.avatar_widget.create_avatar()

# =================================================================================
#       INÍCIO DA MODIFICAÇÃO: NOVA CLASSE NotificationConfigDialog
# =================================================================================
class NotificationConfigDialog(QDialog):
    def __init__(self, settings, theme_colors, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_colors = theme_colors
        
        self.initUI()
        self.apply_styles()
        self.enable_notifications_check.toggled.connect(self.toggle_email_fields)
        self.toggle_email_fields(self.enable_notifications_check.isChecked())

    def initUI(self):
        self.setWindowTitle("Configurar Notificações")
        self.setMinimumWidth(550)
        self.setObjectName("configDialog") # Reutiliza o estilo do diálogo principal
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        title_label = QLabel("Notificações por E-mail")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setObjectName("dialogTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # Grupo de configurações
        notification_group = QGroupBox("Configurações de Envio")
        notification_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        notification_layout = QVBoxLayout(notification_group)
        notification_layout.setSpacing(10)

        self.enable_notifications_check = QCheckBox("Ativar resumo diário por e-mail")
        self.enable_notifications_check.setChecked(self.settings.get_notification_enabled())
        notification_layout.addWidget(self.enable_notifications_check)

        time_form_layout = QFormLayout()
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        current_time = QTime.fromString(self.settings.get_notification_time(), "HH:mm")
        self.time_edit.setTime(current_time)
        time_form_layout.addRow(self.create_label_with_icon("Horário de Envio:", "vencimentos"), self.time_edit)
        notification_layout.addLayout(time_form_layout)

        smtp_form_layout = QFormLayout()
        smtp_config = self.settings.get_smtp_config()
        
        self.smtp_user_edit = QLineEdit(smtp_config.get('user', ''))
        self.smtp_pass_edit = QLineEdit(smtp_config.get('password', ''))
        self.smtp_pass_edit.setEchoMode(QLineEdit.Password)
        self.smtp_recipient_edit = QLineEdit(smtp_config.get('recipient', ''))
        
        smtp_form_layout.addRow("Usuário (e-mail):", self.smtp_user_edit)
        smtp_form_layout.addRow("Senha:", self.smtp_pass_edit)
        smtp_form_layout.addRow(self.create_label_with_icon("Enviar para:", "send"), self.smtp_recipient_edit)
        notification_layout.addLayout(smtp_form_layout)
        
        main_layout.addWidget(notification_group)
        main_layout.addStretch()

        # Botões de Ação
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.setObjectName("cancelButton")
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', color=self.theme_colors.get('text_color', '#000')))
        self.cancelar_btn.clicked.connect(self.reject)
        
        self.salvar_btn = QPushButton("Salvar Alterações")
        self.salvar_btn.setObjectName("saveButton")
        self.salvar_btn.setIcon(IconManager.get_icon('save', color='white'))
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)

        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        main_layout.addLayout(button_layout)
    
    def toggle_email_fields(self, enabled):
        """Habilita ou desabilita os campos de e-mail com base no estado do checkbox."""
        self.time_edit.setEnabled(enabled)
        self.smtp_user_edit.setEnabled(enabled)
        self.smtp_pass_edit.setEnabled(enabled)
        self.smtp_recipient_edit.setEnabled(enabled)

    def create_label_with_icon(self, text, icon_name):
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
        theme = self.theme_colors
        style = f"""
            #configDialog {{ background-color: {theme.get('bg_color', '#fff')}; }}
            #dialogTitle {{ color: {theme.get('text_color', '#000')}; margin-bottom: 10px; }}
            QGroupBox {{
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 8px; margin-top: 10px; padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 5px 5px 10px; color: {theme.get('accent_color', '#007aff')};
            }}
            QLabel, QCheckBox {{ color: {theme.get('text_color', '#000')}; font-size: 10pt; }}
            QLineEdit, QComboBox, QSpinBox, QTimeEdit {{
                background-color: {theme.get('surface_color', '#eee')};
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 4px; padding: 6px; font-size: 10pt;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {{ border: 1px solid {theme.get('accent_color', '#007aff')}; }}
            #saveButton {{
                background-color: {theme.get('accent_color', '#007aff')}; color: white;
                border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }}
            #saveButton:hover {{ background-color: #0069d9; }}
            #cancelButton {{
                background-color: transparent; color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }}
            #cancelButton:hover {{ background-color: {theme.get('button_hover', '#ddd')}; border-color: {theme.get('text_color', '#000')}; }}
        """
        self.setStyleSheet(style)

    def salvar_configuracoes(self):
        self.settings.set_notification_enabled(self.enable_notifications_check.isChecked())
        self.settings.set_notification_time(self.time_edit.time().toString("HH:mm"))

        new_smtp_config = {
            "host": "smtp.gmail.com",
            "port": 587,
            "user": self.smtp_user_edit.text(),
            "password": self.smtp_pass_edit.text(),
            "recipient": self.smtp_recipient_edit.text()
        }
        self.settings.set_smtp_config(new_smtp_config)
        
        self.accept()
# =================================================================================
#       FIM DA MODIFICAÇÃO
# =================================================================================


class ConfigDialog(QDialog):
    def __init__(self, settings, theme_colors, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.theme_colors = theme_colors
        
        self.initUI()
        self.apply_styles()

    def initUI(self):
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(550)
        self.setObjectName("configDialog")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        title_label = QLabel("Configurações do Sistema")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setObjectName("dialogTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # =========================================================
        #       INÍCIO DA MODIFICAÇÃO: REMOVER GRUPO DE NOTIFICAÇÃO
        # =========================================================
        appearance_group = QGroupBox("Aparência")
        appearance_group.setFont(QFont("Segoe UI", 10, QFont.Bold))
        appearance_layout = QFormLayout(appearance_group)
        appearance_layout.setLabelAlignment(Qt.AlignLeft)
        appearance_layout.setSpacing(10)
        
        self.tema_combo = QComboBox()
        self.tema_combo.addItem(IconManager.get_icon('estoque', color=self.theme_colors.get('text_color', '#000')), "Tema Claro", "light")
        self.tema_combo.addItem(IconManager.get_icon('estoque', color=self.theme_colors.get('text_color', '#000')), "Tema Escuro", "dark")
        current_theme = self.settings.get_theme()
        index = self.tema_combo.findData(current_theme)
        if index != -1:
            self.tema_combo.setCurrentIndex(index)
        
        appearance_layout.addRow(self.create_label_with_icon("Tema:", "config"), self.tema_combo)
        main_layout.addWidget(appearance_group)
        
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.setObjectName("cancelButton")
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', color=self.theme_colors.get('text_color', '#000')))
        self.cancelar_btn.clicked.connect(self.reject)
        
        self.salvar_btn = QPushButton("Salvar Alterações")
        self.salvar_btn.setObjectName("saveButton")
        self.salvar_btn.setIcon(IconManager.get_icon('save', color='white'))
        self.salvar_btn.clicked.connect(self.salvar_configuracoes)

        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        main_layout.addLayout(button_layout)
        # =========================================================
        #       FIM DA MODIFICAÇÃO
        # =========================================================

    def create_label_with_icon(self, text, icon_name):
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
        theme = self.theme_colors
        style = f"""
            #configDialog {{ background-color: {theme.get('bg_color', '#fff')}; }}
            #dialogTitle {{ color: {theme.get('text_color', '#000')}; margin-bottom: 10px; }}
            QGroupBox {{
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 8px; margin-top: 10px; padding: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 5px 5px 10px; color: {theme.get('accent_color', '#007aff')};
            }}
            QLabel, QCheckBox {{ color: {theme.get('text_color', '#000')}; font-size: 10pt; }}
            QLineEdit, QComboBox, QSpinBox, QTimeEdit {{
                background-color: {theme.get('surface_color', '#eee')};
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 4px; padding: 6px; font-size: 10pt;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {{ border: 1px solid {theme.get('accent_color', '#007aff')}; }}
            #saveButton {{
                background-color: {theme.get('accent_color', '#007aff')}; color: white;
                border: none; padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }}
            #saveButton:hover {{ background-color: #0069d9; }}
            #cancelButton {{
                background-color: transparent; color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                padding: 8px 16px; border-radius: 4px; font-weight: bold;
            }}
            #cancelButton:hover {{ background-color: {theme.get('button_hover', '#ddd')}; border-color: {theme.get('text_color', '#000')}; }}
        """
        self.setStyleSheet(style)

    def salvar_configuracoes(self):
        tema = self.tema_combo.currentData()
        self.settings.set_theme(tema)

        # =========================================================
        #       INÍCIO DA MODIFICAÇÃO: REMOVER SALVAMENTO DE NOTIFICAÇÃO
        # =========================================================
        # As linhas abaixo foram removidas daqui e movidas para o novo diálogo
        # self.settings.set_notification_enabled(...)
        # self.settings.set_notification_time(...)
        # self.settings.set_smtp_config(...)
        # =========================================================
        #       FIM DA MODIFICAÇÃO
        # =========================================================
        
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

# =================================================================================
#       INÍCIO DA SUGESTÃO: ADICIONE ESTA NOVA CLASSE AO FINAL DO ARQUIVO main.py
# =================================================================================
class GlobalSearchResultsDialog(QDialog):
    """Uma janela de diálogo para exibir os resultados da busca global em abas."""
    def __init__(self, resultados, theme_colors, parent=None):
        super().__init__(parent)
        self.resultados = resultados
        self.theme_colors = theme_colors
        self.setWindowTitle("Resultados da Busca")
        self.setMinimumSize(800, 500)
        self.setObjectName("searchResultsDialog")
        self.initUI()
        self.apply_styles()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel("Resultados da Busca Global")
        title_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title_label.setObjectName("dialogTitle")
        main_layout.addWidget(title_label)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.setup_produtos_tab()
        self.setup_clientes_tab()
        self.setup_fornecedores_tab()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton("Fechar")
        close_button.setObjectName("primaryActionButton") # Reutiliza estilo
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        main_layout.addLayout(button_layout)

    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        return table

    def setup_produtos_tab(self):
        produtos = self.resultados.get('produtos', [])
        widget = QWidget()
        layout = QVBoxLayout(widget)
        table = self.create_table(["Nome", "Código de Barras", "Preço de Venda"])
        table.setRowCount(len(produtos))
        for row, item in enumerate(produtos):
            table.setItem(row, 0, QTableWidgetItem(item.get('nome')))
            table.setItem(row, 1, QTableWidgetItem(item.get('codigo_barras')))
            table.setItem(row, 2, QTableWidgetItem(f"R$ {item.get('preco_venda', 0):.2f}"))
        layout.addWidget(table)
        self.tabs.addTab(widget, f"Produtos ({len(produtos)})")

    def setup_clientes_tab(self):
        clientes = self.resultados.get('clientes', [])
        widget = QWidget()
        layout = QVBoxLayout(widget)
        table = self.create_table(["Nome", "Telefone", "Email"])
        table.setRowCount(len(clientes))
        for row, item in enumerate(clientes):
            table.setItem(row, 0, QTableWidgetItem(item.get('nome')))
            table.setItem(row, 1, QTableWidgetItem(item.get('telefone')))
            table.setItem(row, 2, QTableWidgetItem(item.get('email')))
        layout.addWidget(widget)
        self.tabs.addTab(widget, f"Clientes ({len(clientes)})")

    def setup_fornecedores_tab(self):
        fornecedores = self.resultados.get('fornecedores', [])
        widget = QWidget()
        layout = QVBoxLayout(widget)
        table = self.create_table(["Empresa", "Representante", "Telefone"])
        table.setRowCount(len(fornecedores))
        for row, item in enumerate(fornecedores):
            table.setItem(row, 0, QTableWidgetItem(item.get('empresa')))
            table.setItem(row, 1, QTableWidgetItem(item.get('representante')))
            table.setItem(row, 2, QTableWidgetItem(item.get('telefone')))
        layout.addWidget(widget)
        self.tabs.addTab(widget, f"Fornecedores ({len(fornecedores)})")

    def apply_styles(self):
        # Reutiliza o estilo dos componentes já definidos na folha de estilo principal
        self.setStyleSheet(f"""
            #searchResultsDialog {{
                background-color: {self.theme_colors['bg_color']};
            }}
            #dialogTitle {{
                color: {self.theme_colors['text_color']};
                margin-bottom: 10px;
            }}
        """)
# =================================================================================
#       FIM DA NOVA CLASSE
# =================================================================================