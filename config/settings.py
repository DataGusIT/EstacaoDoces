
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

class Settings:
    def __init__(self):
        # O nome da sua empresa e do app para salvar as configurações
        self.settings = QSettings("SuaEmpresa", "SeuERP")

    # ===================================================================
    #       INÍCIO DA CORREÇÃO: MÉTODOS GENÉRICOS ADICIONADOS
    # ===================================================================
    
     # ===================================================================
    #       INÍCIO DA CORREÇÃO: ADICIONAR ESTE MÉTODO
    # ===================================================================
    def get_value(self, key, default_value=None):
        """
        Método genérico para buscar qualquer configuração.
        É um atalho para o método .value() do QSettings.
        """
        # A lógica aqui é garantir que o tipo do valor padrão seja usado na conversão,
        # se fornecido. Isso evita problemas com boolianos e inteiros.
        if isinstance(default_value, bool):
            return self.settings.value(key, default_value, type=bool)
        if isinstance(default_value, int):
            return self.settings.value(key, default_value, type=int)
        return self.settings.value(key, default_value)
    # ===================================================================
    #       FIM DA CORREÇÃO
    # ===================================================================

    def set_value(self, key, value):
        """
        Método genérico para salvar qualquer configuração.
        É um atalho para o método .setValue() do QSettings.
        """
        self.settings.setValue(key, value)

    def remove(self, key):
        """
        Método genérico para remover uma configuração.
        É um atalho para o método .remove() do QSettings.
        """
        self.settings.remove(key)

    # ===================================================================
    #       FIM DA CORREÇÃO
    # ===================================================================
    
    def get_theme(self):
        """Retorna o tema atual (claro/escuro)."""
        return self.settings.value("theme", "light")
    
    def set_theme(self, theme):
        """Define o tema (claro/escuro)."""
        self.settings.setValue("theme", theme)
    
    def apply_theme(self, app):
        """Aplica o tema atual ao aplicativo."""
        theme = self.get_theme()
        
        if theme == "dark":
            # Tema escuro
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor(53, 53, 53))
            palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
            palette.setColor(QPalette.Base, QColor(25, 25, 25))
            palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
            palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
            palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
            palette.setColor(QPalette.Text, QColor(255, 255, 255))
            palette.setColor(QPalette.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
            palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
            palette.setColor(QPalette.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
            
            app.setPalette(palette)
        else:
            # Tema claro (padrão)
            app.setPalette(QApplication.style().standardPalette())
    
    def get_font_size(self):
        """Retorna o tamanho da fonte."""
        return self.settings.value("font_size", 9, type=int)
    
    def set_font_size(self, size):
        """Define o tamanho da fonte."""
        self.settings.setValue("font_size", size)

    # --- MÉTODOS PARA CONFIGURAÇÃO DE NOTIFICAÇÕES ---

    def get_notification_enabled(self):
        """Verifica se as notificações por e-mail estão ativas."""
        return self.settings.value("notifications/enabled", False, type=bool)

    def set_notification_enabled(self, enabled):
        """Define se as notificações estão ativas."""
        self.settings.setValue("notifications/enabled", enabled)

    def get_notification_time(self):
        """Retorna o horário agendado para as notificações (ex: "08:00")."""
        return self.settings.value("notifications/time", "08:00")

    def set_notification_time(self, time_str):
        """Define o horário das notificações."""
        self.settings.setValue("notifications/time", time_str)

    def get_smtp_config(self):
        """Retorna um dicionário com as configurações do servidor SMTP."""
        return {
            "host": self.settings.value("smtp/host", "smtp.example.com"),
            "port": self.settings.value("smtp/port", 587, type=int),
            "user": self.settings.value("smtp/user", "seu_email@example.com"),
            "password": self.settings.value("smtp/password", ""), # A senha
            "recipient": self.settings.value("smtp/recipient", "destinatario@example.com") # E-mail que receberá a notificação
        }

    def set_smtp_config(self, config):
        """Salva as configurações SMTP."""
        self.settings.setValue("smtp/host", config["host"])
        self.settings.setValue("smtp/port", config["port"])
        self.settings.setValue("smtp/user", config["user"])
        self.settings.setValue("smtp/password", config["password"])
        self.settings.setValue("smtp/recipient", config["recipient"])