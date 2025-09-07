# scheduler.py

from PyQt5.QtCore import QThread, pyqtSignal, QTime, QDate
import time

class Scheduler(QThread):
    notification_triggered = pyqtSignal()
    log_message = pyqtSignal(str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self._is_running = True
        self.last_sent_date = None # Para garantir o envio apenas uma vez ao dia

    def run(self):
        """O corpo da thread. Roda em loop verificando o horário."""
        self.log_message.emit("Agendador de notificações iniciado.")
        
        # --- LÓGICA PRINCIPAL CORRIGIDA ---
        while self._is_running:
            try:
                # Se as notificações estão desativadas, apenas dorme e continua.
                if not self.settings.get_notification_enabled():
                    time.sleep(1) 
                    continue

                now = QTime.currentTime()
                today = QDate.currentDate()
                
                scheduled_time_str = self.settings.get_notification_time()
                scheduled_time = QTime.fromString(scheduled_time_str, "HH:mm")

                # Verifica se está no minuto exato e se o e-mail de hoje já não foi enviado
                if now.hour() == scheduled_time.hour() and now.minute() == scheduled_time.minute():
                    if self.last_sent_date != today:
                        self.log_message.emit(f"Horário agendado ({scheduled_time_str}) atingido. Disparando notificações.")
                        self.notification_triggered.emit()
                        self.last_sent_date = today # Marca que o e-mail de hoje foi enviado

                # A thread dorme por 1 segundo, tornando a verificação de _is_running
                # muito responsiva e garantindo uma parada quase instantânea.
                time.sleep(1)

            except Exception as e:
                self.log_message.emit(f"Erro no loop do agendador: {e}")
                # Em caso de erro, espera um pouco mais para não sobrecarregar
                time.sleep(5) 
        # --- FIM DA CORREÇÃO ---

        self.log_message.emit("Agendador de notificações parado.")

    def stop(self):
        """Sinaliza para a thread parar de forma segura."""
        self._is_running = False

    def restart(self):
        """
        Para a thread atual de forma segura e a reinicia para aplicar
        as novas configurações.
        """
        self.log_message.emit("Reiniciando o agendador com novas configurações...")
        self.stop()
        self.wait(2000) # Espera no máximo 2 segundos para a thread antiga terminar
        
        self._is_running = True
        self.last_sent_date = None # Reseta a data para garantir que funcione no mesmo dia se a hora for alterada
        self.start()