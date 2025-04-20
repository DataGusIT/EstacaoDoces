from PyQt5.QtCore import QSettings
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QApplication

class Settings:
    def __init__(self):
        self.settings = QSettings("SistemaEstoque", "Config")
    
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