import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
from ui.main_window import MainWindow
from database.db_manager import DatabaseManager
from config.settings import Settings

# Garantir que os diretórios necessários existam
os.makedirs("database", exist_ok=True)
os.makedirs("assets/icons", exist_ok=True)
os.makedirs("config", exist_ok=True)

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
        
        # Adicionar um pequeno atraso para mostrar a splash screen
        if splash:
            QTimer.singleShot(1500, splash.close)
        
        # Criar e mostrar a janela principal
        window = MainWindow(db, settings)
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
        
        # Executar o loop de eventos
        sys.exit(app.exec_())
    
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao iniciar o sistema: {str(e)}")
        sys.exit(1)