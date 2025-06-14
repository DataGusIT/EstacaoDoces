import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox, QSplashScreen, QDialog, QLabel
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

def verificar_produtos_alertas(window, db):
    """Função separada para verificar produtos com problemas de validade e estoque"""
    try:
        # Verificar produtos vencidos
        produtos_vencidos = db.verificar_produtos_vencidos()
        produtos_vencendo = db.verificar_produtos_vencendo(dias=15)
        produtos_estoque_baixo = db.verificar_produtos_estoque_baixo()
        
        # Debug: Verificar se há produtos para alertar
        print(f"Produtos vencidos encontrados: {len(produtos_vencidos) if produtos_vencidos else 0}")
        print(f"Produtos vencendo encontrados: {len(produtos_vencendo) if produtos_vencendo else 0}")
        print(f"Produtos com estoque baixo: {len(produtos_estoque_baixo) if produtos_estoque_baixo else 0}")
        
        # Alertar produtos vencidos (CRÍTICO - vermelho piscando)
        if produtos_vencidos:
            msg = "🚨 ATENÇÃO: Os seguintes produtos estão VENCIDOS:\n\n"
            for produto in produtos_vencidos:
                msg += f"• {produto['nome']} - Vencimento: {produto['data_validade']}\n"
            
            msg += "\n⚠️ AÇÃO NECESSÁRIA: Remova estes produtos do estoque IMEDIATAMENTE!"
            msg += "\n💀 Produtos vencidos podem causar problemas de saúde!"
            
            dialog = AlertDialog(window, "🚨 PRODUTOS VENCIDOS - AÇÃO URGENTE", msg, "critical")
            dialog.exec_()
        
        # Alertar produtos vencendo (WARNING - amarelo piscando)
        if produtos_vencendo:
            msg = "⏰ Os seguintes produtos estão próximos do vencimento (15 dias):\n\n"
            for produto in produtos_vencendo:
                msg += f"• {produto['nome']} - Vencimento: {produto['data_validade']}\n"
            
            msg += "\n💡 SUGESTÃO: Considere fazer promoção destes produtos!"
            msg += "\n📢 Ofereça desconto para evitar perdas!"
            
            dialog = AlertDialog(window, "⏰ Produtos Próximos do Vencimento", msg, "warning")
            dialog.exec_()
        
        # Alertar estoque baixo (INFO - verde suave)
        if produtos_estoque_baixo:
            msg = "📦 Os seguintes produtos estão com estoque baixo:\n\n"
            for produto in produtos_estoque_baixo:
                # Corrigir acesso aos dados do sqlite3.Row
                try:
                    fornecedor = produto['fornecedor_nome'] if produto['fornecedor_nome'] else 'Não informado'
                except (KeyError, TypeError):
                    fornecedor = 'Não informado'
                
                msg += f"• {produto['nome']} - Estoque: {produto['quantidade']} (Mín: {produto['estoque_minimo']})\n"
                msg += f"  Fornecedor: {fornecedor}\n\n"
            
            msg += "🛒 AÇÃO RECOMENDADA: Realizar pedido de reposição!"
            msg += "\n📞 Entre em contato com os fornecedores listados."
            
            dialog = AlertDialog(window, "📦 Produtos com Estoque Baixo", msg, "stock")
            dialog.exec_()
            
    except Exception as e:
        print(f"Erro ao verificar produtos: {str(e)}")
        QMessageBox.critical(window, "Erro", f"Erro ao verificar produtos: {str(e)}")

def on_login_success(usuario):
    """Função para lidar com o login bem-sucedido"""
    # Salvar informações do usuário logado
    session.set_usuario(usuario)
    
    # Criar e mostrar a janela principal
    window = MainWindow(db, settings)
    window.session = session  # Passar o gerenciador de sessão
    window.usuario = usuario  # Passar as informações do usuário
    window.setup_for_user(usuario)  # Configurar interface para o usuário
    window.show()
    
    # Aguardar um pouco para a janela ser totalmente carregada
    # antes de mostrar os alertas
    QTimer.singleShot(500, lambda: verificar_produtos_alertas(window, db))

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
        login_window.login_success_signal.connect(on_login_success)
        
        # Mostrar janela de login
        if login_window.exec_() != QDialog.Accepted:
            # Se o usuário fechou a janela de login sem fazer login
            sys.exit(0)
        
        # Executar o loop de eventos
        sys.exit(app.exec_())
    
    except Exception as e:
        QMessageBox.critical(None, "Erro", f"Erro ao iniciar o sistema: {str(e)}")
        sys.exit(1)