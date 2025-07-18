import qtawesome as qta

class IconManager:
    """Centraliza a criação de ícones para garantir consistência."""

    ICONS = {
        # === ÍCONES GERAIS E DE NAVEGAÇÃO ===
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
        'atualizar': 'fa5s.sync-alt',
        'arquivo': 'fa5s.file-alt',
        'ajuda': 'fa5s.question-circle',

        # === CONTROLES DE JANELA ===
        'minimizar': 'fa5.window-minimize',
        'maximizar': 'fa5.window-maximize',
        'restaurar': 'fa5.window-restore',
        'fechar': 'fa5s.times',
        
        # === AÇÕES COMUNS ===
        'search': 'fa5s.search',
        'filter': 'fa5s.filter',
        'clear': 'fa5s.broom',
        'add': 'fa5s.plus-circle',
        'edit': 'fa5s.pencil-alt',
        'delete': 'fa5s.trash-alt',
        'save': 'fa5s.save',
        'cancel': 'fa5s.times-circle',
        'confirm': 'fa5s.check-circle',
        'check': 'fa5s.check',
        
        # === IMPORTAÇÃO / EXPORTAÇÃO ===
        'report': 'fa5s.file-pdf',
        'export': 'fa5s.file-csv',
        'import': 'fa5s.file-upload',
        'send': 'fa5s.paper-plane',

        # === USUÁRIO E ACESSO ===
        'perfil': 'fa5s.user-circle',
        'senha': 'fa5s.key',
        'user': 'fa5s.user',
        'password': 'fa5s.lock',
        'eye': 'fa5s.eye',
        'eye-off': 'fa5s.eye-slash',
        'profile': 'fa5s.user-circle',
        'admin': 'fa5s.user-shield',
        'logout': 'fa5s.sign-out-alt',
        'lock': 'fa5s.lock',
        'unlock': 'fa5s.unlock',
        'login': 'fa5s.sign-in-alt',
        
        # === PAGINAÇÃO E SETAS ===
        'angle-left': 'fa5s.angle-left',
        'angle-right': 'fa5s.angle-right',
        'chevron_down': 'fa5s.chevron-down',

        # === ÍCONES DE ESTOQUE E PRODUTO (JÁ EXISTENTES) ===
        'estoque_baixo': 'fa5s.exclamation-triangle',
        'vencimentos': 'fa5s.calendar-times',
        'break': 'fa5s.unlink', # Quebrar embalagem
        'check_stock': 'fa5s.box-open',

        # --- ÍCONES NOVOS PARA O FORMULÁRIO DE PRODUTO ---
        'barcode': 'fa5s.barcode',
        'box': 'fa5s.box',
        'comment-alt': 'fa5s.comment-alt',
        'tags': 'fa5s.tags', # Alias para 'promocoes'
        'truck': 'fa5s.truck', # Alias para 'fornecedores'
        'map-marker-alt': 'fa5s.map-marker-alt',
        'dollar-sign': 'fa5s.dollar-sign',
        'percentage': 'fa5s.percentage',
        'ruler': 'fa5s.ruler-combined', # Ícone para unidade de medida
        'box-open': 'fa5s.box-open', # Alias para 'check_stock'
        'tag': 'fa5s.tag', # Singular para preço unitário
        'cubes': 'fa5s.cubes', # Para estoque fracionado
        
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