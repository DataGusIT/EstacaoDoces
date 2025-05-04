import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen, QDialog
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer

from ui.main_window import MainWindow
from ui.login_window import LoginWindow  # Importar a janela de login
from database.db_manager import DatabaseManager
from config.settings import Settings

# Garantir que os diretórios necessários existam
os.makedirs("database", exist_ok=True)
os.makedirs("assets/icons", exist_ok=True)
os.makedirs("config", exist_ok=True)

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

if __name__ == "__main__":
    # Iniciar aplicação
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Estilo consistente entre plataformas
    
    # Aplicar configurações
    settings = Settings()
    settings.apply_theme(app)
    
    # Definir fonte global
    font = QFont("Arial", settings.get_font_size())
    app.setFont(font)
    
    # Splash Screen (opcional)
    splash_pixmap = QPixmap("assets/splash.png")
    if not splash_pixmap.isNull():
        splash = QSplashScreen(splash_pixmap)
        splash.show()
        app.processEvents()
    else:
        splash = None
    
    # Criar conexão com o banco de dados
    try:
        db = DatabaseManager()
        session = SessionManager()  # Criar gerenciador de sessão
        
        # Mostrar login após a splash screen
        if splash:
            QTimer.singleShot(1500, splash.close)
        
        # Exibir tela de login
        login_window = LoginWindow(db)
        
        # Conectar o sinal de login bem-sucedido
        def on_login_success(self, usuario):
            # Salvar informações do usuário logado
            session.set_usuario(self, usuario)
            
            # Criar e mostrar a janela principal
            window = MainWindow(db, settings)
            window.session = session  # Passar o gerenciador de sessão
            window.user_info = usuario  # Passar as informações do usuário
            window.setup_for_user(usuario)  # Configurar interface para o usuário
            window.show()
            
            # Verificar produtos vencidos ou prestes a vencer ao iniciar
            produtos_vencidos = db.verificar_produtos_vencidos()
            produtos_vencendo = db.verificar_produtos_vencendo(dias=15)
            
            if produtos_vencidos:
                msg = "Os seguintes produtos estão vencidos:\n\n"
                for produto in produtos_vencidos:
                    msg += f"• {produto['nome']} - Vencimento: {produto['data_validade']}\n"
                
                QMessageBox.warning(window, "Produtos Vencidos", msg)
            
            if produtos_vencendo:
                msg = "Os seguintes produtos estão próximos do vencimento:\n\n"
                for produto in produtos_vencendo:
                    msg += f"• {produto['nome']} - Vencimento: {produto['data_validade']}\n"
                
                QMessageBox.information(window, "Produtos Próximos do Vencimento", msg)
        
            # Conectar o sinal ao slot
            # Conectando o sinal de login bem-sucedido
            self.login_success_signal.connect(on_login_success)
        
        # Mostrar janela de login
        if login_window.exec_() != QDialog.Accepted:
            # Se o usuário fechou a janela de login sem fazer login
            sys.exit(0)
        
        # Executar o loop de eventos
        sys.exit(app.exec_())
    
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao iniciar o sistema: {str(e)}")
        sys.exit(1)
