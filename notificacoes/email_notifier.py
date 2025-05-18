import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os

class EmailNotifier:
    def __init__(self, smtp_server, smtp_port, username, password, sender_email):
        """
        Inicializa o serviço de notificação por email
        
        Args:
            smtp_server (str): Servidor SMTP (ex: smtp.gmail.com)
            smtp_port (int): Porta do servidor SMTP (ex: 587 para TLS)
            username (str): Nome de usuário para autenticação SMTP
            password (str): Senha para autenticação SMTP
            sender_email (str): Email do remetente
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.sender_email = sender_email
    
    def enviar_email(self, destinatarios, assunto, conteudo_html):
        """
        Envia email para os destinatários informados
        
        Args:
            destinatarios (list): Lista de emails dos destinatários
            assunto (str): Assunto do email
            conteudo_html (str): Conteúdo do email em formato HTML
            
        Returns:
            bool: True se o email foi enviado com sucesso, False caso contrário
        """
        try:
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = assunto
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(destinatarios)
            
            # Adicionar conteúdo HTML
            part = MIMEText(conteudo_html, 'html')
            msg.attach(part)
            
            # Conectar ao servidor SMTP
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Segurança TLS
            server.login(self.username, self.password)
            
            # Enviar email
            server.sendmail(self.sender_email, destinatarios, msg.as_string())
            server.quit()
            
            print(f"Email enviado com sucesso para {', '.join(destinatarios)}")
            return True
            
        except Exception as e:
            print(f"Erro ao enviar email: {e}")
            return False
    
    def notificar_estoque_baixo(self, destinatarios, produtos):
        """
        Envia notificação de produtos com estoque baixo
        
        Args:
            destinatarios (list): Lista de emails dos destinatários
            produtos (list): Lista de produtos com estoque baixo
        """
        if not produtos:
            return False
        
        # Preparar tabela HTML com os produtos
        rows = ""
        for produto in produtos:
            rows += f"""
            <tr>
                <td>{produto['id']}</td>
                <td>{produto['nome']}</td>
                <td>{produto['descricao'] or '-'}</td>
                <td>{produto['quantidade']}</td>
                <td>{produto['estoque_minimo']}</td>
                <td>{produto['fornecedor_nome'] or 'Não informado'}</td>
            </tr>
            """
        
        # Montar conteúdo HTML
        html = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .alerta {{
                    background-color: #fffacd;
                    padding: 10px;
                    border-left: 5px solid #ffd700;
                    margin-bottom: 15px;
                }}
            </style>
        </head>
        <body>
            <h2>⚠️ Alerta de Estoque Baixo</h2>
            <div class="alerta">
                <p>Os seguintes produtos estão com estoque abaixo do mínimo definido e precisam de reposição:</p>
            </div>
            
            <table>
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>Descrição</th>
                    <th>Quantidade</th>
                    <th>Estoque Mínimo</th>
                    <th>Fornecedor</th>
                </tr>
                {rows}
            </table>
            
            <p>Este é um email automático. Por favor, não responda.</p>
            <p>Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        return self.enviar_email(
            destinatarios=destinatarios,
            assunto=f"⚠️ ALERTA: {len(produtos)} produtos com estoque baixo",
            conteudo_html=html
        )
    
    def notificar_produtos_vencendo_alerta(self, destinatarios, produtos, dias_limite):
        """
        Envia notificação de produtos próximos do vencimento (Alerta: 16-30 dias)
        
        Args:
            destinatarios (list): Lista de emails dos destinatários
            produtos (list): Lista de produtos próximos do vencimento
            dias_limite (int): Limite de dias para considerar alerta (geralmente 30)
        """
        if not produtos:
            return False
        
        # Preparar tabela HTML com os produtos
        rows = ""
        data_atual = datetime.now().date()
        
        for produto in produtos:
            data_validade = produto['data_validade']
            if data_validade:
                data_obj = datetime.strptime(data_validade, '%Y-%m-%d').date()
                dias_restantes = (data_obj - data_atual).days
                data_formatada = data_obj.strftime('%d/%m/%Y')
            else:
                dias_restantes = "N/A"
                data_formatada = "Não informada"
                
            rows += f"""
            <tr>
                <td>{produto['id']}</td>
                <td>{produto['nome']}</td>
                <td>{produto['descricao'] or '-'}</td>
                <td>{produto['quantidade']}</td>
                <td>{data_formatada}</td>
                <td>{dias_restantes}</td>
                <td>{produto['fornecedor_nome'] or 'Não informado'}</td>
            </tr>
            """
        
        # Montar conteúdo HTML
        html = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .alerta {{
                    background-color: #fffacd;
                    padding: 10px;
                    border-left: 5px solid #ffd700;
                    margin-bottom: 15px;
                }}
            </style>
        </head>
        <body>
            <h2>⚠️ Alerta de Produtos Vencendo</h2>
            <div class="alerta">
                <p>Os seguintes produtos vencerão nos próximos {dias_limite} dias:</p>
            </div>
            
            <table>
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>Descrição</th>
                    <th>Quantidade</th>
                    <th>Data de Validade</th>
                    <th>Dias Restantes</th>
                    <th>Fornecedor</th>
                </tr>
                {rows}
            </table>
            
            <p>Recomendamos verificar o estoque e planejar ações adequadas para evitar perdas.</p>
            <p>Este é um email automático. Por favor, não responda.</p>
            <p>Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        return self.enviar_email(
            destinatarios=destinatarios,
            assunto=f"⚠️ ALERTA: {len(produtos)} produtos vencendo nos próximos {dias_limite} dias",
            conteudo_html=html
        )
    
    def notificar_produtos_vencendo_urgente(self, destinatarios, produtos, dias_limite):
        """
        Envia notificação de produtos próximos do vencimento (Urgente: 15 dias ou menos)
        
        Args:
            destinatarios (list): Lista de emails dos destinatários
            produtos (list): Lista de produtos próximos do vencimento
            dias_limite (int): Limite de dias para considerar urgente (geralmente 15)
        """
        if not produtos:
            return False
        
        # Preparar tabela HTML com os produtos
        rows = ""
        data_atual = datetime.now().date()
        
        for produto in produtos:
            data_validade = produto['data_validade']
            if data_validade:
                data_obj = datetime.strptime(data_validade, '%Y-%m-%d').date()
                dias_restantes = (data_obj - data_atual).days
                data_formatada = data_obj.strftime('%d/%m/%Y')
            else:
                dias_restantes = "N/A"
                data_formatada = "Não informada"
                
            rows += f"""
            <tr>
                <td>{produto['id']}</td>
                <td>{produto['nome']}</td>
                <td>{produto['descricao'] or '-'}</td>
                <td>{produto['quantidade']}</td>
                <td>{data_formatada}</td>
                <td>{dias_restantes}</td>
                <td>{produto['fornecedor_nome'] or 'Não informado'}</td>
            </tr>
            """
        
        # Montar conteúdo HTML
        html = f"""
        <html>
        <head>
            <style>
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                .urgente {{
                    background-color: #ffebee;
                    padding: 10px;
                    border-left: 5px solid #d32f2f;
                    margin-bottom: 15px;
                }}
            </style>
        </head>
        <body>
            <h2>🚨 URGENTE: Produtos Próximos ao Vencimento</h2>
            <div class="urgente">
                <p>Os seguintes produtos vencerão em {dias_limite} dias ou menos:</p>
            </div>
            
            <table>
                <tr>
                    <th>ID</th>
                    <th>Nome</th>
                    <th>Descrição</th>
                    <th>Quantidade</th>
                    <th>Data de Validade</th>
                    <th>Dias Restantes</th>
                    <th>Fornecedor</th>
                </tr>
                {rows}
            </table>
            
            <p><strong>AÇÃO IMEDIATA NECESSÁRIA!</strong> Por favor, verifique estes produtos e tome as providências necessárias para evitar perdas.</p>
            <p>Este é um email automático. Por favor, não responda.</p>
            <p>Data e hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        return self.enviar_email(
            destinatarios=destinatarios,
            assunto=f"🚨 URGENTE: {len(produtos)} produtos vencendo em {dias_limite} dias ou menos",
            conteudo_html=html
        )
    
    # Método legado para compatibilidade
    def notificar_produtos_vencendo(self, destinatarios, produtos, dias_restantes):
        """
        Método legado para manter compatibilidade
        """
        if dias_restantes <= 15:
            return self.notificar_produtos_vencendo_urgente(destinatarios, produtos, dias_restantes)
        else:
            return self.notificar_produtos_vencendo_alerta(destinatarios, produtos, dias_restantes)
    