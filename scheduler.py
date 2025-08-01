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
        while self._is_running:
            try:
                if not self.settings.get_notification_enabled():
                    # Se as notificações estão desativadas, dorme por mais tempo para economizar recursos.
                    # Vamos verificar a cada 5 minutos se elas foram reativadas.
                    time.sleep(300) 
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

                # A thread dorme por quase 60 segundos. A verificação é feita uma vez por minuto.
                # O loop verifica a flag _is_running a cada segundo para uma parada mais responsiva.
                for _ in range(60):
                    if not self._is_running:
                        break
                    time.sleep(1)

            except Exception as e:
                self.log_message.emit(f"Erro no loop do agendador: {e}")
                time.sleep(60) # Espera um minuto antes de tentar novamente

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
        
        # 1. Sinaliza para a thread atual parar
        self.stop()
        
        # 2. Espera até 5 segundos para a thread terminar seu ciclo atual.
        # Isso é crucial para evitar iniciar uma nova thread enquanto a antiga ainda está rodando.
        self.wait(5000)
        
        # 3. Reseta a flag e inicia a thread novamente.
        self._is_running = True
        self.start()