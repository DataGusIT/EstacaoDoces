import qtawesome as qta

class IconManager:
    """Centraliza a criação de ícones para garantir consistência."""

    # Mapeamento de nomes semânticos para nomes de ícones do FontAwesome 5
    ICONS = {
        # Ícones do sistema principal
        'dashboard': 'fa5s.tachometer-alt',
        'estoque': 'fa5s.boxes',
        'fornecedores': 'fa5s.truck-loading',
        'promocoes': 'fa5s.tags',
        'clientes': 'fa5s.users',
        'caixa': 'fa5s.cash-register',
        'config': 'fa5s.cog',
        'menu': 'fa5s.bars',
        'sair': 'fa5s.sign-out-alt',
        'sobre': 'fa5s.info-circle',
        'relatorio': 'fa5s.chart-bar',
        'estoque_baixo': 'fa5s.exclamation-triangle',
        'vencimentos': 'fa5s.calendar-times',
        'atualizar': 'fa5s.sync-alt',
        'arquivo': 'fa5s.file-alt',
        'ajuda': 'fa5s.question-circle',
        'minimizar': 'fa5.window-minimize',
        'maximizar': 'fa5.window-maximize',
        'restaurar': 'fa5.window-restore',
        'fechar': 'fa5s.times',
        'perfil': 'fa5s.user-circle',
        'senha': 'fa5s.key',
        'search': 'fa5s.search',
        'filter': 'fa5s.filter',
        'clear': 'fa5s.broom',
        'add': 'fa5s.plus-circle',
        'report': 'fa5s.file-pdf',
        'export': 'fa5s.file-csv',
        'import': 'fa5s.file-upload',
        'edit': 'fa5s.pencil-alt',
        'delete': 'fa5s.trash-alt',
        'break': 'fa5s.unlink',
        'save': 'fa5s.save',
        'cancel': 'fa5s.times-circle',
        'confirm': 'fa5s.check-circle',
        'send': 'fa5s.paper-plane',
        'check_stock': 'fa5s.box-open',
        'close': 'fa5s.times',
        
        # Ícones específicos para o login
        'user': 'fa5s.user',
        'password': 'fa5s.lock',
        'eye': 'fa5s.eye',
        'eye-off': 'fa5s.eye-slash',
        'check': 'fa5s.check',
        
        # --- ÍCONES ADICIONADOS PARA SUBSTITUIR O ICONPROVIDER ---
        'chevron_down': 'fa5s.chevron-down',
        'profile': 'fa5s.user-circle',    # Alias para 'perfil'
        'admin': 'fa5s.user-shield',      # Ícone de admin
        'logout': 'fa5s.sign-out-alt',    # Alias para 'sair'
        
        # Aliases adicionais
        'lock': 'fa5s.lock',
        'unlock': 'fa5s.unlock',
        'login': 'fa5s.sign-in-alt',
    }

    @staticmethod
    def get_icon(name, color='#000000', **options):
        """Retorna um QIcon de qtawesome a partir de um nome semântico."""
        icon_name = IconManager.ICONS.get(name, 'fa5s.question-circle') # Ícone de fallback
        return qta.icon(icon_name, color=color, **options)

    @staticmethod
    def has_icon(name):
        """Verifica se um ícone existe no mapeamento."""
        return name in IconManager.ICONS

    @staticmethod
    def list_available_icons():
        """Lista todos os ícones disponíveis."""
        return list(IconManager.ICONS.keys())

    @staticmethod
    def get_icon_safe(name, color='#000000', fallback_icon='question-circle'):
        """Versão segura que permite especificar um ícone de fallback personalizado."""
        if name in IconManager.ICONS:
            icon_name = IconManager.ICONS[name]
        else:
            icon_name = IconManager.ICONS.get(fallback_icon, 'fa5s.question-circle')
        return qta.icon(icon_name, color=color)