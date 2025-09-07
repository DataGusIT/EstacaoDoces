import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen, QDialog, QLabel
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

from ui.main_window import MainWindow
from ui.login_window import LoginWindow  # Importar a janela de login
from database.db_manager import DatabaseManager
from config.settings import Settings

def get_app_data_dir():
    """Retorna o diretório apropriado para dados do aplicativo"""
    if sys.platform == "win32":
        # Windows: usar AppData/Local
        base_dir = os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(base_dir, 'SeuNomeDoApp')  # Substitua pelo nome do seu app
    elif sys.platform == "darwin":
        # macOS: usar Library/Application Support
        app_dir = os.path.expanduser('~/Library/Application Support/SeuNomeDoApp')
    else:
        # Linux: usar .config
        app_dir = os.path.expanduser('~/.config/SeuNomeDoApp')
    
    return app_dir

def get_app_dirs():
    """Retorna os diretórios necessários para o aplicativo"""
    app_data_dir = get_app_data_dir()
    
    return {
        'app_data': app_data_dir,
        'database': os.path.join(app_data_dir, 'database'),
        'config': os.path.join(app_data_dir, 'config'),
        'assets': os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
    }

def setup_directories():
    """Cria os diretórios necessários no local apropriado"""
    dirs = get_app_dirs()
    
    try:
        # Criar diretórios no AppData do usuário
        os.makedirs(dirs['app_data'], exist_ok=True)
        os.makedirs(dirs['database'], exist_ok=True)
        os.makedirs(dirs['config'], exist_ok=True)
        
        # Assets ficam no diretório de instalação (somente leitura)
        # Se não existir, criar no AppData também
        if not os.path.exists(dirs['assets']):
            assets_fallback = os.path.join(dirs['app_data'], 'assets')
            os.makedirs(assets_fallback, exist_ok=True)
            os.makedirs(os.path.join(assets_fallback, 'icons'), exist_ok=True)
            dirs['assets'] = assets_fallback
        
        return dirs
        
    except PermissionError as e:
        QMessageBox.critical(None, "Erro", 
                           f"Erro ao criar diretórios necessários:\n{str(e)}\n\n"
                           f"Verifique as permissões ou execute como administrador.")
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(None, "Erro", 
                           f"Erro inesperado ao configurar diretórios:\n{str(e)}")
        sys.exit(1)

class SessionManager:
    """Gerencia a sessão do usuário logado"""
    
    def __init__(self):
        self.usuario_atual = None
    
    def set_usuario(self, usuario):
        self.usuario_atual = usuario
    
    def get_usuario(self):
        return self.usuario_atual
    
    def tem_permissao(self, tipo_permissao='comum'):
        """Verifica se o usuário tem determinada permissão"""
        if not self.usuario_atual:
            return False
        
        if tipo_permissao == 'comum':
            return True
        
        if tipo_permissao == 'admin':
            return self.usuario_atual['tipo'] == 'admin'
        
        return False

class AlertDialog(QDialog):
    """Dialog customizado com efeitos visuais para alertas"""
    
    def __init__(self, parent, title, message, alert_type="info"):
        super().__init__(parent)
        self.alert_type = alert_type
        self.setWindowTitle(title)
        self.setModal(True)
        self.setup_ui(message)
        self.setup_animation()
        
    def setup_ui(self, message):
        from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit
        
        layout = QVBoxLayout()
        
        # Área de texto para a mensagem
        self.text_area = QTextEdit()
        self.text_area.setPlainText(message)
        self.text_area.setReadOnly(True)
        self.text_area.setMinimumSize(500, 300)
        
        # Definir cores baseadas no tipo de alerta
        if self.alert_type == "critical":  # Produtos vencidos
            self.bg_color = "#ffebee"  # Vermelho claro
            self.border_color = "#f44336"  # Vermelho
            self.pulse_color = "#ffcdd2"  # Vermelho mais claro
        elif self.alert_type == "warning":  # Produtos vencendo
            self.bg_color = "#fff8e1"  # Amarelo claro
            self.border_color = "#ff9800"  # Laranja
            self.pulse_color = "#ffe0b2"  # Laranja claro
        elif self.alert_type == "stock":  # Estoque baixo
            self.bg_color = "#e8f5e8"  # Verde claro
            self.border_color = "#4caf50"  # Verde
            self.pulse_color = "#c8e6c9"  # Verde mais claro
        else:  # Info padrão
            self.bg_color = "#e3f2fd"  # Azul claro
            self.border_color = "#2196f3"  # Azul
            self.pulse_color = "#bbdefb"  # Azul mais claro
        
        # Aplicar estilo inicial
        self.apply_style(self.bg_color)
        
        layout.addWidget(self.text_area)
        
        # Botões
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)
        ok_button.setMinimumHeight(35)
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def apply_style(self, bg_color):
        style = f"""
        QDialog {{
            background-color: {bg_color};
            border: 3px solid {self.border_color};
            border-radius: 10px;
        }}
        QTextEdit {{
            background-color: white;
            border: 2px solid {self.border_color};
            border-radius: 5px;
            padding: 10px;
            font-size: 12px;
            color: #333333;
        }}
        QPushButton {{
            background-color: {self.border_color};
            color: white;
            border: none;
            padding: 8px 20px;
            border-radius: 5px;
            font-weight: bold;
            font-size: 14px;
        }}
        QPushButton:hover {{
            background-color: {self.pulse_color};
            color: #333333;
        }}
        QDialog QLabel {{
            color: #333333;
        }}
        """
        self.setStyleSheet(style)
    
    def setup_animation(self):
        # Só animar para alertas críticos e de aviso
        if self.alert_type in ["critical", "warning"]:
            self.timer = QTimer()
            self.timer.timeout.connect(self.pulse_effect)
            self.pulse_state = False
            self.timer.start(800)  # Pulsar a cada 800ms
    
    def pulse_effect(self):
        if self.pulse_state:
            self.apply_style(self.bg_color)
        else:
            self.apply_style(self.pulse_color)
        self.pulse_state = not self.pulse_state

def verificar_produtos_alertas(window, db, theme_colors):
    """Função separada para verificar produtos com problemas de validade e estoque"""
    try:
        # Tenta importar a AlertDialog aqui para garantir que está acessível
        from ui.main_window import AlertDialog

        # Verificar produtos vencidos
        produtos_vencidos = db.verificar_produtos_vencidos()
        if produtos_vencidos:
            msg = "**ATENÇÃO: Os seguintes produtos estão VENCIDOS:**\n\n"
            for p in produtos_vencidos:
                msg += f"* **{p['nome']}** - Vencimento: {p['data_validade']}\n"
            msg += "\n\n**AÇÃO NECESSÁRIA:** Remova estes produtos do estoque IMEDIATAMENTE!"
            dialog = AlertDialog(window, "Produtos Vencidos", msg, "critical", theme_colors)
            dialog.exec_()
        
        # Verificar produtos vencendo
        produtos_vencendo = db.verificar_produtos_vencendo(dias=15)
        if produtos_vencendo:
            msg = "**Os seguintes produtos estão próximos do vencimento (15 dias):**\n\n"
            for p in produtos_vencendo:
                msg += f"* **{p['nome']}** - Vencimento: {p['data_validade']}\n"
            msg += "\n\n**SUGESTÃO:** Considere fazer uma promoção para evitar perdas."
            dialog = AlertDialog(window, "Próximos do Vencimento", msg, "warning", theme_colors)
            dialog.exec_()
            
        # Verificar estoque baixo
        produtos_estoque_baixo = db.verificar_produtos_estoque_baixo()
        if produtos_estoque_baixo:
            msg = "**Os seguintes produtos estão com estoque baixo:**\n\n"
            for p in produtos_estoque_baixo:
                fornecedor = p['fornecedor_nome'] or 'Não informado'
                msg += f"* **{p['nome']}** - Estoque: {p['quantidade']} (Mín: {p['estoque_minimo']})\n"
                msg += f"  Fornecedor: *{fornecedor}*\n"
            msg += "\n\n**AÇÃO RECOMENDADA:** Realizar pedido de reposição."
            dialog = AlertDialog(window, "Estoque Baixo", msg, "stock", theme_colors)
            dialog.exec_()
            
    except Exception as e:
        # Se houver erro AQUI, use uma QMessageBox simples para não causar um loop de erros.
        print(f"Erro ao verificar ou exibir alertas de produtos: {str(e)}")
        import traceback
        traceback.print_exc()
        QMessageBox.critical(window, "Erro de Alerta", f"Não foi possível exibir o alerta de produtos.\n\nErro: {str(e)}")


def on_login_success(usuario):
    """Função para lidar com o login bem-sucedido"""
    global window # Torna a window acessível globalmente nesta função
    session.set_usuario(usuario)
    
    # Passa o dicionário de tema para a MainWindow
    window = MainWindow(db, settings, theme_colors)

    window.session = session
    window.usuario = usuario
    window.setup_for_user(usuario)
    window.show()
    
    # 2. Passe theme_colors para a função de verificação
    QTimer.singleShot(500, lambda: verificar_produtos_alertas(window, db, theme_colors))


if __name__ == "__main__":
    # Iniciar aplicação
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # ================================================================= #
    #       CORREÇÃO APLICADA AQUI                                      #
    # ================================================================= #
    
    # 1. Define o caminho para o seu ícone.
    #    Como a função setup_directories() já define 'ASSETS_DIR', podemos usá-lo.
    #    Note que seu caminho é 'assets/img/Logo.png' e não 'Logo2.png'
    logo_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'img', 'Logo.png')
    
    # 2. Cria o ícone e o define para a aplicação inteira.
    app.setWindowIcon(QIcon(logo_path))

    # --- FIM DA CORREÇÃO ---

    # Configurar diretórios necessários (seu código original continua aqui)
    app_dirs = setup_directories()
    
    # Definir variáveis de ambiente para que outros módulos usem os caminhos corretos
    os.environ['APP_DATA_DIR'] = app_dirs['app_data']
    os.environ['DATABASE_DIR'] = app_dirs['database']
    os.environ['CONFIG_DIR'] = app_dirs['config']
    os.environ['ASSETS_DIR'] = app_dirs['assets']
    
    try:
        # Aplicar configurações (agora usando o diretório correto)
        settings = Settings()
        
        # ... (O resto do seu código permanece exatamente o mesmo) ...
        
        is_dark = settings.get_theme() == 'dark'
        if is_dark:
            theme_colors = {
                'bg_color': "#1c2128", 'surface_color': "#22272e", 'menu_color': "#22272e",
                'text_color': "#cdd9e5", 'text_secondary': "#768390", 'border_color': "#373e47",
                'button_hover': "#373e47", 'accent_color': "#007AFF"
            }
        else:
            theme_colors = {
                'bg_color': "#ffffff", 'surface_color': "#f2f2f7", 'menu_color': "#f9f9f9",
                'text_color': "#000000", 'text_secondary': "#6d6d70", 'border_color': "#d1d1d6",
                'button_hover': "#e5e5ea", 'accent_color': "#007AFF"
            }
        
        settings.apply_theme(app)
        
        font = QFont("Arial", settings.get_font_size())
        app.setFont(font)
        
        splash_path = os.path.join(app_dirs['assets'], 'splash.png')
        splash_pixmap = QPixmap(splash_path)
        if not splash_pixmap.isNull():
            splash = QSplashScreen(splash_pixmap)
            splash.show()
            app.processEvents()
        else:
            splash = None
        
        db = DatabaseManager()
        session = SessionManager()
        
        if splash:
            QTimer.singleShot(1500, splash.close)
        
        login_window = LoginWindow(db, theme_colors)
        login_window.login_success_signal.connect(on_login_success)
        
        if login_window.exec_() != QDialog.Accepted:
            sys.exit(0)
        
        sys.exit(app.exec_())
    
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao iniciar o sistema: {str(e)}")
        sys.exit(1)