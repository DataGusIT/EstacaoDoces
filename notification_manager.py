# notification_manager.py

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

class NotificationManager:
    def __init__(self, db_manager, settings):
        self.db = db_manager
        self.settings = settings

    def check_and_send_notifications(self):
        """Método principal que verifica e envia o e-mail de relatório diário."""
        print(f"[{datetime.now()}] Verificando a necessidade de enviar notificações...")

        # 1. Pega os dados dos alertas do banco
        produtos_vencidos = self.db.verificar_produtos_vencidos()
        produtos_estoque_baixo = self.db.verificar_produtos_estoque_baixo()
        produtos_vencendo = self.db.verificar_produtos_vencendo(dias=30)

        # 2. Se não houver nada para reportar, não envia o e-mail
        if not produtos_vencidos and not produtos_estoque_baixo and not produtos_vencendo:
            print("Nenhum alerta encontrado. E-mail não será enviado.")
            return True, "Sem alertas para notificar."

        # 3. Monta o corpo do e-mail
        html_body = self._build_html_email(
            produtos_vencidos,
            produtos_estoque_baixo,
            produtos_vencendo
        )

        # 4. Envia o e-mail
        smtp_config = self.settings.get_smtp_config()
        subject = f"Relatório Diário de Alertas do Estoque - {datetime.now().strftime('%d/%m/%Y')}"
        
        success, message = self._send_email(
            recipient=smtp_config['recipient'],
            subject=subject,
            html_body=html_body
        )
        
        if success:
            print("E-mail de notificação enviado com sucesso!")
        else:
            print(f"Falha ao enviar e-mail: {message}")
            
        return success, message

    def _build_html_email(self, vencidos, estoque_baixo, vencendo):
        """Cria o conteúdo HTML 'inteligente' para o e-mail."""
        
        # Helper para criar uma tabela de produtos
        def create_product_table(produtos):
            if not produtos:
                return "<p>Nenhum item nesta categoria.</p>"
            
            table_html = """
            <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f2f2f2;">
                    <th>Produto</th>
                    <th>Qtde. Atual</th>
                    <th>Fornecedor</th>
                    <th>Validade</th>
                </tr>
            """
            for produto in produtos:
                table_html += f"""
                <tr>
                    <td>{produto['nome']}</td>
                    <td style="text-align: center;">{produto['quantidade']}</td>
                    <td>{produto['fornecedor_nome'] or 'N/D'}</td>
                    <td style="text-align: center;">{produto['data_validade']}</td>
                </tr>
                """
            table_html += "</table>"
            return table_html

        # Corpo principal do e-mail
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                h2 {{ color: #d9534f; }} /* Vermelho para alertas críticos */
                h3 {{ color: #f0ad4e; }} /* Laranja para avisos */
                h4 {{ color: #5bc0de; }} /* Azul para informações */
                p.dica {{ background-color: #eef; padding: 10px; border-left: 5px solid #55f; }}
            </style>
        </head>
        <body>
            <h1>Relatório Diário de Alertas do Sistema de Estoque</h1>
            <p>Este é um resumo automático da situação do seu estoque para hoje, {datetime.now().strftime('%d de %B de %Y')}.</p>
            
            <hr>
            
            <h2>🚨 Alerta Crítico: Produtos Vencidos</h2>
            <p>Os seguintes itens já passaram da data de validade e precisam ser removidos do estoque imediatamente.</p>
            {create_product_table(vencidos)}
            <p class="dica"><b>Dica:</b> Retire esses produtos da área de venda para garantir a segurança e a satisfação dos seus clientes. Dê baixa no sistema para corrigir o inventário.</p>

            <hr>

            <h3>⚠️ Aviso: Estoque Baixo</h3>
            <p>Estes produtos atingiram ou estão abaixo do nível de estoque mínimo definido.</p>
            {create_product_table(estoque_baixo)}
            <p class="dica"><b>Dica:</b> Considere fazer um novo pedido de compra para esses itens para evitar a falta de produtos. Verifique os prazos de entrega dos seus fornecedores.</p>

            <hr>

            <h4>ℹ️ Informativo: Produtos Próximos do Vencimento (30 dias)</h4>
            <p>Os itens abaixo vencerão em breve. Planeje ações para vendê-los a tempo.</p>
            {create_product_table(vencendo)}
            <p class="dica"><b>Dica:</b> Crie promoções, combos ou coloque esses produtos em destaque na loja para acelerar a venda e evitar perdas.</p>

            <br>
            <p>Atenciosamente,<br>GestorX</p>
        </body>
        </html>
        """
        return html

    def _send_email(self, recipient, subject, html_body):
        """Envia um e-mail usando as configurações salvas."""
        smtp_config = self.settings.get_smtp_config()
        
        # Validação básica
        if not all([smtp_config['host'], smtp_config['user'], smtp_config['password'], recipient]):
            return False, "Configurações SMTP incompletas."

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = smtp_config['user']
        msg['To'] = recipient

        msg.attach(MIMEText(html_body, 'html'))

        try:
            with smtplib.SMTP(smtp_config['host'], smtp_config['port']) as server:
                server.starttls()  # Habilita segurança
                server.login(smtp_config['user'], smtp_config['password'])
                server.sendmail(smtp_config['user'], recipient, msg.as_string())
                return True, "E-mail enviado com sucesso."
        except Exception as e:
            return False, f"Erro SMTP: {str(e)}"