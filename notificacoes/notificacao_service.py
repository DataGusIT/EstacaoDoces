from datetime import datetime, timedelta
from email_notifier import EmailNotifier
import os
import json

class NotificacaoService:
    def __init__(self, db_manager):
        """
        Inicializa o serviço de notificações
        
        Args:
            db_manager: Instância do DatabaseManager para acessar o banco de dados
        """
        self.db_manager = db_manager
        self.config = self._carregar_config()
        
        # Inicializa o notificador de email com as configurações
        self.email_notifier = EmailNotifier(
            smtp_server=self.config['email']['smtp_server'],
            smtp_port=self.config['email']['smtp_port'],
            username=self.config['email']['username'],
            password=self.config['email']['password'],
            sender_email=self.config['email']['sender_email']
        )
    
    def _carregar_config(self):
        """
        Carrega as configurações de um arquivo config.json ou cria configurações padrão
        """
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')
        
        # Verifica se o diretório config existe, se não, cria
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        # Configurações padrão
        default_config = {
            'email': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'username': 'seu_email@gmail.com',
                'password': 'sua_senha_app',  # Recomendável usar senha de app para Gmail
                'sender_email': 'seu_email@gmail.com',
                'destinatarios': ['gerente@empresa.com', 'compras@empresa.com']
            },
            'notificacoes': {
                'estoque_baixo': {
                    'ativo': True,
                    'verificar_a_cada_horas': 24,
                    'ultima_verificacao': None
                },
                'vencimento': {
                    'ativo': True,
                    'alertas_dias': [15, 30],
                    'verificar_a_cada_horas': 24,
                    'ultima_verificacao': None
                }
            }
        }
        
        # Verifica se o arquivo config.json existe
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Garante que todas as chaves padrão existam
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                        elif isinstance(default_config[key], dict):
                            for subkey in default_config[key]:
                                if subkey not in config[key]:
                                    config[key][subkey] = default_config[key][subkey]
                    return config
            except Exception as e:
                print(f"Erro ao carregar configurações: {e}")
                return default_config
        else:
            # Se o arquivo não existe, cria com as configurações padrão
            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4)
                print(f"Arquivo de configuração criado em {config_file}")
            except Exception as e:
                print(f"Erro ao criar arquivo de configuração: {e}")
            
            return default_config
    
    def _salvar_config(self):
        """
        Salva as configurações atualizadas no arquivo config.json
        """
        config_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'config.json')
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            return True
        except Exception as e:
            print(f"Erro ao salvar configurações: {e}")
            return False
    
    def verificar_estoque_baixo(self):
        """
        Verifica produtos com estoque baixo e envia notificação se necessário
        
        Returns:
            bool: True se a verificação foi realizada, False caso contrário
        """
        # Verifica se a notificação está ativa
        if not self.config['notificacoes']['estoque_baixo']['ativo']:
            return False
        
        # Verifica quando foi a última verificação
        ultima_verificacao = self.config['notificacoes']['estoque_baixo']['ultima_verificacao']
        horas_intervalo = self.config['notificacoes']['estoque_baixo']['verificar_a_cada_horas']
        
        agora = datetime.now()
        
        # Se já fez verificação antes, checa se já passou o intervalo de tempo
        if ultima_verificacao:
            ultima = datetime.fromisoformat(ultima_verificacao)
            if agora < ultima + timedelta(hours=horas_intervalo):
                return False  # Ainda não passou tempo suficiente desde a última verificação
        
        # Busca produtos com estoque baixo
        produtos = self.db_manager.verificar_produtos_estoque_baixo()
        
        # Atualiza última verificação
        self.config['notificacoes']['estoque_baixo']['ultima_verificacao'] = agora.isoformat()
        self._salvar_config()
        
        # Se não tem produtos com estoque baixo, retorna
        if not produtos:
            return True
        
        # Envia notificação
        destinatarios = self.config['email']['destinatarios']
        resultado = self.email_notifier.notificar_estoque_baixo(destinatarios, produtos)
        
        return resultado
    
    def verificar_produtos_vencendo(self):
        """
        Verifica produtos próximos do vencimento e envia notificação se necessário
        
        Returns:
            bool: True se a verificação foi realizada, False caso contrário
        """
        # Verifica se a notificação está ativa
        if not self.config['notificacoes']['vencimento']['ativo']:
            return False
        
        # Verifica quando foi a última verificação
        ultima_verificacao = self.config['notificacoes']['vencimento']['ultima_verificacao']
        horas_intervalo = self.config['notificacoes']['vencimento']['verificar_a_cada_horas']
        
        agora = datetime.now()
        
        # Se já fez verificação antes, checa se já passou o intervalo de tempo
        if ultima_verificacao:
            ultima = datetime.fromisoformat(ultima_verificacao)
            if agora < ultima + timedelta(hours=horas_intervalo):
                return False  # Ainda não passou tempo suficiente desde a última verificação
        
        # Atualiza última verificação
        self.config['notificacoes']['vencimento']['ultima_verificacao'] = agora.isoformat()
        self._salvar_config()
        
        # Pega os limites de dias para alertas (15 e 30 dias por padrão)
        dias_alerta = sorted(self.config['notificacoes']['vencimento']['alertas_dias'], reverse=True)
        
        # Data atual para comparação
        data_atual = datetime.now().date()
        
        # Lista para armazenar os produtos por categoria de alerta
        produtos_urgentes = []  # Para produtos com vencimento em 15 dias ou menos
        produtos_alerta = []    # Para produtos com vencimento entre 16 e 30 dias
        
        # Pega todos os produtos com validade entre hoje e o máximo de dias configurado
        dias_max = max(dias_alerta)
        todos_produtos = self._buscar_todos_produtos_vencendo(dias_max)
        
        # Categoriza os produtos por dias até o vencimento
        for produto in todos_produtos:
            # Calcula quantos dias faltam para o vencimento
            data_validade = datetime.strptime(produto['data_validade'], '%Y-%m-%d').date()
            dias_restantes = (data_validade - data_atual).days
            
            # Classifica o produto na categoria apropriada
            if 0 <= dias_restantes <= dias_alerta[-1]:  # 15 dias por padrão (urgentes)
                produtos_urgentes.append(produto)
            elif dias_alerta[-1] < dias_restantes <= dias_alerta[0]:  # 16-30 dias por padrão (alerta)
                produtos_alerta.append(produto)
        
        # Envia as notificações
        destinatarios = self.config['email']['destinatarios']
        resultados = {}
        
        # Envia notificação para produtos urgentes (15 dias ou menos)
        if produtos_urgentes:
            resultados["urgente"] = self.email_notifier.notificar_produtos_vencendo_urgente(
                destinatarios, produtos_urgentes, dias_alerta[-1]
            )
        
        # Envia notificação para produtos em alerta (entre 16 e 30 dias)
        if produtos_alerta:
            resultados["alerta"] = self.email_notifier.notificar_produtos_vencendo_alerta(
                destinatarios, produtos_alerta, dias_alerta[0]
            )
        
        return len(resultados) > 0
    
    def _buscar_todos_produtos_vencendo(self, dias_max):
        """
        Busca todos os produtos que irão vencer nos próximos X dias
        
        Args:
            dias_max (int): Número máximo de dias para verificar
            
        Returns:
            list: Lista de produtos
        """
        # Garantir conexão com o banco
        self.db_manager.ensure_connection()
        
        # Calcular a data limite
        data_atual = datetime.now().date()
        data_limite = data_atual + timedelta(days=dias_max)
        
        # Converter para string no formato YYYY-MM-DD
        data_atual_str = data_atual.strftime('%Y-%m-%d')
        data_limite_str = data_limite.strftime('%Y-%m-%d')
        
        # Executar consulta SQL
        self.db_manager.cursor.execute('''
        SELECT p.*, f.nome as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.data_validade BETWEEN ? AND ?
        ORDER BY p.data_validade
        ''', (data_atual_str, data_limite_str))
        
        return self.db_manager.cursor.fetchall()
    
    def verificar_todas_notificacoes(self):
        """
        Executa todas as verificações disponíveis
        
        Returns:
            dict: Resultados de cada verificação
        """
        resultados = {
            'estoque_baixo': self.verificar_estoque_baixo(),
            'produtos_vencendo': self.verificar_produtos_vencendo()
        }
        
        return resultados
