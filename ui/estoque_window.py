from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QSpinBox,
                           QDoubleSpinBox, QDialog, QFrame, QToolButton, QGroupBox,
                           QFileDialog, QCheckBox, QProgressDialog, QGridLayout)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
import csv
import qtawesome as qta
import math
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager 


# ================================================================= #
#       CLASSE CSV IMPORT WORKER TOTALMENTE IMPLEMENTADA            #
# ================================================================= #
class CsvImportWorker(QThread):
    """
    Executa a importação de CSV em uma thread para não congelar a UI.
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, int, list)

    # MUDANÇA 1: O __init__ agora recebe db_path em vez de um objeto db
    def __init__(self, db_path, file_path):
        super().__init__()
        self.db_path = db_path
        self.file_path = file_path
        self.local_db = None # Será a nossa conexão local

    def run(self):
        produtos_importados = 0
        produtos_erro = 0
        erros_detalhes = []

        try:
            # MUDANÇA 2: Crie uma nova instância do DatabaseManager DENTRO da thread.
            # Isso cria uma nova conexão que pertence a ESTA thread.
            self.local_db = DatabaseManager(self.db_path)

            with open(self.file_path, 'r', encoding='utf-8') as f:
                # Corrigindo um potencial erro se o arquivo estiver vazio
                linhas = list(f)
                total_linhas = max(1, len(linhas) - 1)

            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                # MUDANÇA 3: Use a conexão local (local_db) para todas as operações
                self.local_db.begin_transaction() 

                for i, row in enumerate(reader):
                    try:
                        if not row.get('nome', '').strip():
                            raise ValueError("Nome do produto é obrigatório")

                        # Adapte esta parte para usar os métodos de extração que você já tem
                        # (tornando-os estáticos ou recriando a lógica aqui)
                        preco_compra = self._extrair_preco(row.get('preco_compra', '0'))
                        preco_venda = self._extrair_preco(row.get('preco_venda', '0'))
                        margem_lucro = self._extrair_margem(row.get('margem', '0'))
                        quantidade = self._extrair_quantidade_do_estoque_detalhado(row.get('estoque_detalhado', '0'))
                        data_validade = self._formatar_data_validade(row.get('validade', ''))

                        produto_data = {
                            'codigo_barras': row.get('codigo_barras', '').strip(),
                            'nome': row.get('nome', '').strip(),
                            'descricao': row.get('descricao', ''),
                            'quantidade': quantidade,
                            'estoque_minimo': int(row.get('estoque_minimo', '0') or 0),
                            'preco_compra': preco_compra,
                            'margem_lucro': margem_lucro,
                            'preco_venda': preco_venda,
                            'data_validade': data_validade,
                            'localizacao': row.get('localizacao', '').strip() or None,
                            'fornecedor_id': None,
                            'categoria': row.get('categoria', '').strip() or None,
                            'fracionado': 0,
                            'unidade_medida': 'unidade',
                            'qtd_por_embalagem': 1,
                            'preco_unitario_fracao': 0,
                            'estoque_fracionado': 0
                        }
                        
                        produto_existente = None
                        if produto_data['codigo_barras']:
                            produto_existente = self.local_db.buscar_produto_por_codigo_barras(produto_data['codigo_barras'])
                        if not produto_existente:
                            produto_existente = self.local_db.buscar_produto_por_nome_exato(produto_data['nome'])

                        if produto_existente:
                            # A sua função de atualizar espera os parâmetros um por um
                            self.local_db.atualizar_produto(produto_existente['id'], **produto_data)
                        else:
                            # A sua função de adicionar espera os parâmetros um por um
                            self.local_db.adicionar_produto(**produto_data)
                        
                        produtos_importados += 1
                    except Exception as e:
                        produtos_erro += 1
                        erros_detalhes.append(f"Linha {i+2}: {str(e)}")
                    
                    self.progress.emit(int(((i + 1) / total_linhas) * 100))
                
                self.local_db.commit_transaction()

        except Exception as e:
            if self.local_db:
                self.local_db.rollback_transaction()
            erros_detalhes.append(f"Erro geral: {str(e)}")
        finally:
            # MUDANÇA 4: Garanta que a conexão local seja fechada
            if self.local_db:
                self.local_db.fechar()

        self.finished.emit(produtos_importados, produtos_erro, erros_detalhes)
    
    # Copiei seus métodos de extração aqui para a lógica funcionar
    def _extrair_quantidade_do_estoque_detalhado(self, estoque_str):
        try:
            if estoque_str.isdigit(): return int(estoque_str)
            import re
            numeros = re.findall(r'\d+', estoque_str)
            return int(numeros[0]) if numeros else 0
        except: return 0

    def _extrair_preco(self, preco_str):
        try:
            return float(preco_str.replace('R$', '').replace(' ', '').replace(',', '.'))
        except: return 0.0

    def _extrair_margem(self, margem_str):
        try:
            return float(margem_str.replace('%', '').replace(' ', '').replace(',', '.'))
        except: return 0.0

    def _formatar_data_validade(self, data_str):
        if not data_str or not data_str.strip(): return None
        try:
            if '/' in data_str: return datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            return datetime.strptime(data_str, "%Y-%m-%d").strftime("%Y-%m-%d")
        except: return None
    
class EstoqueWindow(QWidget):
    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.pagina_atual = 1
        self.itens_por_pagina = 100 
        self.total_paginas = 1

        # CORREÇÃO: Chamada única para initUI e para o carregamento de dados
        self.initUI()
        self.set_theme(self.theme_colors) 
        self.atualizar_visualizacao_dados()

    def _get_button_style(self, style_type):
        """Retorna uma string de estilo CSS para um tipo de botão específico."""
        base_style = """
            QPushButton {{
                color: {text_color};
                background-color: {bg_color};
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {pressed_color};
            }}
        """
        styles = {
            "add":      ("white", "#28a745", "#218838", "#1e7e34"),  # Verde (Sucesso)
            "report":   ("white", "#007bff", "#0069d9", "#0062cc"),  # Azul (Informativo)
            "data":     ("white", "#17a2b8", "#138496", "#117a8b"),  # Azul-petróleo (Import/Export)
            "edit":     ("black", "#ffc107", "#e0a800", "#d39e00"),  # Amarelo (Aviso/Edição)
            "delete":   ("white", "#dc3545", "#c82333", "#bd2130"),  # Vermelho (Perigo/Exclusão)
            "action":   ("white", "#fd7e14", "#e67311", "#da6d10")   # Laranja (Ação especial)
        }
        text, bg, hover, pressed = styles.get(style_type, ("black", "#f0f0f0", "#e0e0e0", "#d0d0d0"))
        return base_style.format(text_color=text, bg_color=bg, hover_color=hover, pressed_color=pressed)
    
    def set_theme(self, theme_colors):
        """Atualiza o tema da janela, dos ícones e do cabeçalho da tabela."""
        self.theme_colors = theme_colors
        
        # CORREÇÃO 1: Estilo do cabeçalho agora usa 'surface_color' para ser distinto do fundo.
        header_style = f"""
            QHeaderView::section {{
                background-color: {self.theme_colors.get('surface_color', '#e0e0e0')};
                color: {self.theme_colors.get('text_color', '#000000')};
                padding: 4px;
                border: 1px solid {self.theme_colors.get('border_color', '#c0c0c0')};
                font-weight: bold;
            }}
        """
        self.tabela.horizontalHeader().setStyleSheet(header_style)
        
        self.update_button_icons()
        self.atualizar_visualizacao_dados() # Recarrega para aplicar cores nos ícones da tabela
    
    def update_button_icons(self):
        """Atualiza todos os ícones da interface para refletir o novo tema."""
        text_color = self.theme_colors.get('text_color', '#000')
        
        self.search_button.setIcon(IconManager.get_icon('search', text_color))
        self.aplicar_filtro_btn.setIcon(IconManager.get_icon('filter', text_color))
        self.limpar_filtro_btn.setIcon(IconManager.get_icon('clear', text_color))
        self.prev_page_btn.setIcon(IconManager.get_icon('angle-left', text_color))
        self.next_page_btn.setIcon(IconManager.get_icon('angle-right', text_color))

        self.add_button.setIcon(IconManager.get_icon('add', 'white'))
        self.relatorio_btn.setIcon(IconManager.get_icon('report', 'white'))
        self.relatorio_estoque_btn.setIcon(IconManager.get_icon('report', 'white'))
        self.exportar_csv_btn.setIcon(IconManager.get_icon('export', 'white'))
        self.importar_csv_btn.setIcon(IconManager.get_icon('import', 'white'))
    
    def initUI(self):
        layout = QVBoxLayout(self)
    
        titulo = QLabel("Controle de Estoque")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        search_group = QGroupBox("Pesquisa e Filtros")
        search_layout = QVBoxLayout(search_group)
        
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar produto por nome, descrição ou código de barras...")
        
        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar")
        self.search_button.clicked.connect(self.pesquisar_produtos)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)
        search_layout.addLayout(search_input_layout)
        
        filter_layout = QHBoxLayout()
        self.estoque_combo = QComboBox()
        self.estoque_combo.addItem("Todos os níveis", "todos")
        self.estoque_combo.addItem("Estoque Baixo", "baixo")
        self.estoque_combo.addItem("Estoque Médio", "medio")
        self.estoque_combo.addItem("Estoque Alto", "alto")
        filter_layout.addWidget(QLabel("Nível de Estoque:"))
        filter_layout.addWidget(self.estoque_combo)
        
        self.vencimento_combo = QComboBox()
        self.vencimento_combo.addItem("Todos", "todos")
        self.vencimento_combo.addItem("Vence em 30 dias", "30")
        self.vencimento_combo.addItem("Vence em 15 dias", "15")
        self.vencimento_combo.addItem("Vencidos", "vencidos")
        filter_layout.addWidget(QLabel("Vencimento:"))
        filter_layout.addWidget(self.vencimento_combo)

        self.categoria_combo = QComboBox()
        self.categoria_combo.addItem("Todas as categorias", "todas")
        self.carregar_categorias()
        filter_layout.addWidget(QLabel("Categoria:"))
        filter_layout.addWidget(self.categoria_combo)
        
        self.aplicar_filtro_btn = QPushButton()
        self.aplicar_filtro_btn.setToolTip("Aplicar Filtros")
        self.aplicar_filtro_btn.clicked.connect(self.aplicar_filtros)
        
        self.limpar_filtro_btn = QPushButton()
        self.limpar_filtro_btn.setToolTip("Limpar Filtros")
        self.limpar_filtro_btn.clicked.connect(self.limpar_filtros)
        
        filter_layout.addWidget(self.aplicar_filtro_btn)
        filter_layout.addWidget(self.limpar_filtro_btn)
        
        search_layout.addLayout(filter_layout)
        layout.addWidget(search_group)
        
        legenda_layout = QHBoxLayout()
        estoque_baixo_label = QLabel("Estoque Baixo")
        estoque_baixo_label.setStyleSheet("color: red;")
        legenda_layout.addWidget(estoque_baixo_label)
        vencimento_30_label = QLabel("Vence em 30 dias")
        vencimento_30_label.setStyleSheet("color: orange;")
        legenda_layout.addWidget(vencimento_30_label)
        vencimento_15_label = QLabel("Vence em 15 dias")
        vencimento_15_label.setStyleSheet("color: red;")
        legenda_layout.addWidget(vencimento_15_label)
        legenda_layout.addStretch()
        layout.addLayout(legenda_layout)
        
        self.tabela = QTableWidget()
        # CORREÇÃO 3: Reduzido o número de colunas e removido "ID" dos cabeçalhos
        self.tabela.setColumnCount(12)
        self.tabela.setHorizontalHeaderLabels([
            "Código de Barras", "Nome", "Categoria", "Estoque Detalhado", "Estoque Mín.", 
            "Preço Compra", "Margem %", "Preço Venda", "Validade", 
            "Localização", "Fornecedor", "Ações"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        paginacao_layout = QHBoxLayout()
        paginacao_layout.setAlignment(Qt.AlignCenter)
        
        self.prev_page_btn = QPushButton(" Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
        
        self.page_label = QLabel(f"Página {self.pagina_atual} de {self.total_paginas}")
        
        self.next_page_btn = QPushButton("Próxima")
        self.next_page_btn.setLayoutDirection(Qt.RightToLeft)
        self.next_page_btn.clicked.connect(self.ir_proxima_pagina)

        paginacao_layout.addWidget(self.prev_page_btn)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.page_label)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.next_page_btn)
        layout.addLayout(paginacao_layout)
        
        action_layout = QHBoxLayout()
    
        self.add_button = QPushButton(" Adicionar Produto")
        self.add_button.setObjectName("primaryActionButton") 
        self.add_button.clicked.connect(self.abrir_formulario_produto)

        self.relatorio_btn = QPushButton(" Relatório de Vencimentos")
        self.relatorio_btn.clicked.connect(self.relatorio_vencimentos)

        self.relatorio_estoque_btn = QPushButton(" Relatório de Estoque Baixo")
        self.relatorio_estoque_btn.clicked.connect(self.relatorio_estoque_baixo)
        
        self.exportar_csv_btn = QPushButton(" Exportar CSV")
        self.exportar_csv_btn.clicked.connect(self.exportar_csv)

        self.importar_csv_btn = QPushButton(" Importar CSV")
        self.importar_csv_btn.clicked.connect(self.importar_csv)

        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.relatorio_btn)
        action_layout.addWidget(self.relatorio_estoque_btn)
        action_layout.addWidget(self.exportar_csv_btn)
        action_layout.addWidget(self.importar_csv_btn)
        layout.addLayout(action_layout)
        self.update_button_icons()

    def ir_pagina_anterior(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_visualizacao_dados()

    def ir_proxima_pagina(self):
        if self.pagina_atual < self.total_paginas:
            self.pagina_atual += 1
            self.atualizar_visualizacao_dados()

    def atualizar_categorias_filtro(self):
        categoria_selecionada = self.categoria_combo.currentData()
        self.carregar_categorias()
        if categoria_selecionada and categoria_selecionada != "todas":
            index = self.categoria_combo.findData(categoria_selecionada)
            if index >= 0:
                self.categoria_combo.setCurrentIndex(index)
    
    def carregar_dados(self):
        """Agora é apenas uma chamada para a função central."""
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
        self.carregar_categorias()

    def carregar_categorias(self):
        # ... (seu método está correto, mas vamos garantir que o dado 'todas' exista) ...
        current_data = self.categoria_combo.currentData()
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Todas as categorias", "todas")
        categorias = self.db.listar_categorias_unicas()
        for categoria in categorias:
            if categoria and categoria.strip():
                self.categoria_combo.addItem(categoria, categoria)
        
        index = self.categoria_combo.findData(current_data)
        if index != -1:
            self.categoria_combo.setCurrentIndex(index)
    
    def pesquisar_produtos(self):
        """Apenas reseta a página e atualiza a visualização."""
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()

    def aplicar_filtros(self):
        """Apenas reseta a página e atualiza a visualização."""
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
    
    def limpar_filtros(self):
        """Limpa os campos, reseta a página e atualiza a visualização."""
        self.estoque_combo.setCurrentIndex(0)
        self.vencimento_combo.setCurrentIndex(0)
        self.categoria_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
        self.carregar_categorias() # Recarrega as categorias após limpar
    
    def atualizar_visualizacao_dados(self):
        """
        Função central que busca os filtros da UI, consulta o banco de dados
        com paginação e filtros, e atualiza a tabela e os controles de paginação.
        """
        filtros = {
            'termo_pesquisa': self.search_input.text(),
            'estoque': self.estoque_combo.currentData(),
            'vencimento': self.vencimento_combo.currentData(),
            'categoria': self.categoria_combo.currentData(),
        }

        produtos = self.db.listar_produtos_paginado_e_filtrado(
            filtros=filtros,
            pagina=self.pagina_atual,
            itens_por_pagina=self.itens_por_pagina
        )
        total_itens = self.db.contar_produtos_filtrados(filtros=filtros)
        self.atualizar_tabela(produtos)

        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina) or 1
        
        self.page_label.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.prev_page_btn.setEnabled(self.pagina_atual > 1)
        self.next_page_btn.setEnabled(self.pagina_atual < self.total_paginas)
    
    def atualizar_tabela(self, produtos):
        self.tabela.setRowCount(0)
        icon_color = self.theme_colors.get('text_color', '#000')
        hoje = datetime.now().date()
        
        for row, produto in enumerate(produtos):
            self.tabela.insertRow(row)
            
            # ===== INÍCIO DA CORREÇÃO =====
            def get_value(key, default=""):
                """
                Obtém um valor de um objeto sqlite3.Row de forma segura.
                Verifica se a chave (nome da coluna) existe antes de acessá-la.
                """
                return produto[key] if key in produto.keys() else default
            # ===== FIM DA CORREÇÃO =====

            # O restante do método continua igual, mas agora usando a função corrigida
            self.tabela.setItem(row, 0, QTableWidgetItem(get_value('codigo_barras', '')))
            
            nome_produto = get_value('nome', 'Produto Desconhecido')
            is_fracionado = bool(get_value('fracionado', False))
            if is_fracionado:
                nome_produto += f" (Frac. - {get_value('unidade_medida', 'un')})"
            self.tabela.setItem(row, 1, QTableWidgetItem(nome_produto))

            self.tabela.setItem(row, 2, QTableWidgetItem(get_value('categoria', "Sem categoria")))
            
            quantidade = get_value('quantidade', 0)
            estoque_fracionado = get_value('estoque_fracionado', 0)
            if is_fracionado:
                estoque_total = get_value('estoque_total_calculado', 0)
                quantidade_display = f"{quantidade} emb. + {estoque_fracionado} {get_value('unidade_medida', 'un')} (Total: {estoque_total})"
                tooltip_text = f"Embalagens: {quantidade}\nFracionado: {estoque_fracionado} {get_value('unidade_medida', 'un')}\nTotal em unidades: {estoque_total}"
            else:
                quantidade_display = str(quantidade)
                tooltip_text = f"Quantidade: {quantidade}"
            quantidade_item = QTableWidgetItem(quantidade_display)
            quantidade_item.setToolTip(tooltip_text)
            estoque_minimo = get_value('estoque_minimo', 0)
            estoque_atual = get_value('estoque_total_calculado', quantidade)
            if estoque_atual <= estoque_minimo:
                quantidade_item.setForeground(QBrush(QColor('red')))
                quantidade_item.setToolTip(quantidade_item.toolTip() + "\nESTOQUE ABAIXO DO MÍNIMO!")
            self.tabela.setItem(row, 3, quantidade_item)
            
            self.tabela.setItem(row, 4, QTableWidgetItem(str(estoque_minimo)))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {get_value('preco_compra', 0):.2f}"))
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{get_value('margem_lucro', 0):.2f}%"))
            
            if is_fracionado and get_value('preco_unitario_fracao', 0):
                preco_display = f"Emb: R$ {get_value('preco_venda', 0):.2f} | Un: R$ {get_value('preco_unitario_fracao', 0):.2f}"
            else:
                preco_display = f"R$ {get_value('preco_venda', 0):.2f}"
            self.tabela.setItem(row, 7, QTableWidgetItem(preco_display))
            
            validade_str = get_value('data_validade', '')
            validade_item = QTableWidgetItem(validade_str)
            if validade_str:
                try:
                    data_validade = datetime.strptime(validade_str, "%Y-%m-%d").date()
                    dias_para_vencer = (data_validade - hoje).days
                    if dias_para_vencer <= 0:
                        validade_item.setForeground(QBrush(QColor('darkred')))
                        validade_item.setToolTip("Produto VENCIDO!")
                    elif dias_para_vencer <= 15:
                        validade_item.setForeground(QBrush(QColor('red')))
                        validade_item.setToolTip(f"Vence em {dias_para_vencer} dias!")
                    elif dias_para_vencer <= 30:
                        validade_item.setForeground(QBrush(QColor('orange')))
                        validade_item.setToolTip(f"Vence em {dias_para_vencer} dias!")
                except (ValueError, TypeError): pass
            self.tabela.setItem(row, 8, validade_item)

            self.tabela.setItem(row, 9, QTableWidgetItem(get_value('localizacao', '')))
            self.tabela.setItem(row, 10, QTableWidgetItem(get_value('fornecedor_nome', "N/A")))
            
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            acoes_layout.setSpacing(5)
            
            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), "")
            editar_btn.setToolTip("Editar Produto")
            editar_btn.setFixedSize(30, 30)
            editar_btn.clicked.connect(lambda _, p_id=get_value('id'): self.abrir_formulario_produto(p_id))
            
            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), "")
            excluir_btn.setToolTip("Excluir Produto")
            excluir_btn.setFixedSize(30, 30)
            excluir_btn.clicked.connect(lambda _, p_id=get_value('id'): self.excluir_produto(p_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            if is_fracionado and quantidade > 0:
                quebrar_btn = QPushButton(IconManager.get_icon('break', icon_color), "")
                quebrar_btn.setToolTip("Quebrar embalagem em unidades")
                quebrar_btn.setFixedSize(30, 30)
                quebrar_btn.clicked.connect(lambda _, p_id=get_value('id'): self.abrir_dialog_quebrar_embalagem(p_id))
                acoes_layout.addWidget(quebrar_btn)
            
            self.tabela.setCellWidget(row, 11, acoes_widget)

    def abrir_dialog_quebrar_embalagem(self, produto_id):
        produto_info = self.db.obter_info_estoque_fracionado(produto_id)
        if not produto_info or not produto_info['fracionado']:
            QMessageBox.warning(self, "Erro", "Este produto não é fracionado!")
            return
        
        # --- ALTERAÇÃO NECESSÁRIA AQUI ---
        # Adicione self.theme_colors como o terceiro argumento
        dialog = DialogQuebrarEmbalagem(self.db, produto_info, self.theme_colors)
        
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados() # Você pode usar self.atualizar_visualizacao_dados() aqui também
    
    def abrir_formulario_produto(self, produto_id=None):
        dialog = FormularioProduto(self.db, produto_id, self.theme_colors)

        # --- LINHA ADICIONADA ---
        # Faz o diálogo abrir maximizado, ocupando a tela inteira.
        dialog.showMaximized()

        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
            self.atualizar_categorias_filtro()  
    
    def excluir_produto(self, produto_id):
        confirmacao = QMessageBox.question(
            self, "Confirmar Exclusão", "Tem certeza que deseja excluir este produto?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_produto(produto_id):
                QMessageBox.information(self, "Sucesso", "Produto excluído com sucesso!")
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir o produto.")
    
    # ... O restante do seu código (relatórios, importação, exportação, etc.) permanece o mesmo ...
    # Nenhuma alteração é necessária nas funções abaixo
    def relatorio_vencimentos(self):
        """Gera relatório de produtos próximos ao vencimento."""
        produtos = self.db.verificar_produtos_vencendo(dias=30)
        
        if not produtos:
            QMessageBox.information(self, "Relatório", "Não há produtos próximos do vencimento nos próximos 30 dias.")
            return
        
        msg = "Produtos que vencerão nos próximos 30 dias:\n\n"
        for produto in produtos:
            dias_para_vencer = (datetime.strptime(produto['data_validade'], "%Y-%m-%d").date() - datetime.now().date()).days
            msg += f"• {produto['nome']} - Vencimento: {produto['data_validade']} (em {dias_para_vencer} dias)\n"
        
        # Diálogo com opções de visualizar ou baixar PDF
        dialog = QDialog(self)
        dialog.setWindowTitle("Relatório de Vencimentos")
        dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(dialog)
        
        # Mensagem
        msg_label = QLabel(msg)
        msg_label.setWordWrap(True)
        dialog_layout.addWidget(msg_label)
        
        # Botões
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        
        pdf_btn = QPushButton("Baixar como PDF")
        pdf_btn.clicked.connect(lambda: self.gerar_pdf_vencimentos(produtos))
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(pdf_btn)
        dialog_layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def gerar_pdf_vencimentos(self, produtos):
        """Gera um PDF com os produtos próximos ao vencimento e salva no disco."""
        try:
            # Solicitar local para salvar o arquivo
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Relatório de Vencimentos", 
                os.path.expanduser("~/relatorio_vencimentos.pdf"),
                "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return  # Cancelado pelo usuário
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Conteúdo do documento
            elementos = []
            
            # Estilos
            styles = getSampleStyleSheet()
            titulo_style = styles["Heading1"]
            subtitulo_style = styles["Heading2"]
            normal_style = styles["Normal"]
            
            # Data atual
            data_atual = datetime.now().strftime("%d/%m/%Y")
            
            # Título
            elementos.append(Paragraph("Relatório de Produtos Próximos ao Vencimento", titulo_style))
            elementos.append(Spacer(1, 0.5 * cm))
            elementos.append(Paragraph(f"Gerado em: {data_atual}", normal_style))
            elementos.append(Spacer(1, 1 * cm))
            
            # Subtítulo
            elementos.append(Paragraph("Produtos que vencerão nos próximos 30 dias:", subtitulo_style))
            elementos.append(Spacer(1, 0.5 * cm))
            
            # Dados da tabela
            data = [["Nome do Produto", "Data de Validade", "Dias Restantes", "Qtde. em Estoque"]]
            
            hoje = datetime.now().date()
            
            # Ordenar produtos por data de vencimento (do mais próximo ao mais distante)
            produtos_ordenados = sorted(produtos, 
                                        key=lambda p: datetime.strptime(p['data_validade'], "%Y-%m-%d").date())
            
            for produto in produtos_ordenados:
                data_validade = datetime.strptime(produto['data_validade'], "%Y-%m-%d").date()
                dias_para_vencer = (data_validade - hoje).days
                
                # Formatação da data para exibição
                data_formatada = data_validade.strftime("%d/%m/%Y")
                
                data.append([
                    produto['nome'],
                    data_formatada,
                    str(dias_para_vencer),
                    str(produto['quantidade'])
                ])
            
            # Criar tabela
            tabela = Table(data, colWidths=[doc.width * 0.4, doc.width * 0.2, doc.width * 0.2, doc.width * 0.2])
            
            # Estilo da tabela
            estilo_tabela = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ])
            
            # Destacar produtos próximos de vencer
            for i, produto in enumerate(produtos_ordenados, 1):
                data_validade = datetime.strptime(produto['data_validade'], "%Y-%m-%d").date()
                dias_para_vencer = (data_validade - hoje).days
                
                if dias_para_vencer <= 0:
                    # Produto vencido
                    estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.pink)
                    estilo_tabela.add('TEXTCOLOR', (0, i), (-1, i), colors.darkred)
                elif dias_para_vencer <= 15:
                    # Vence em 15 dias ou menos
                    estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.mistyrose)
                    estilo_tabela.add('TEXTCOLOR', (0, i), (-1, i), colors.red)
                elif dias_para_vencer <= 30:
                    # Vence em 30 dias ou menos
                    estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.lightgoldenrodyellow)
                    estilo_tabela.add('TEXTCOLOR', (0, i), (-1, i), colors.darkorange)
            
            tabela.setStyle(estilo_tabela)
            elementos.append(tabela)
            
            # Adicionar legenda
            elementos.append(Spacer(1, 1 * cm))
            elementos.append(Paragraph("Legenda:", subtitulo_style))
            elementos.append(Spacer(1, 0.2 * cm))
            
            legenda_style = ParagraphStyle(
                'Legenda',
                parent=normal_style,
                spaceAfter=6
            )
            
            elementos.append(Paragraph("• <font color='darkred'>Vermelho escuro</font>: Produtos vencidos", legenda_style))
            elementos.append(Paragraph("• <font color='red'>Vermelho</font>: Produtos que vencem em 15 dias ou menos", legenda_style))
            elementos.append(Paragraph("• <font color='darkorange'>Laranja</font>: Produtos que vencem entre 16 e 30 dias", legenda_style))
            
            # Nota de rodapé
            elementos.append(Spacer(1, 2 * cm))
            nota_style = ParagraphStyle(
                'Nota',
                parent=normal_style,
                fontSize=8,
                textColor=colors.grey
            )
            elementos.append(Paragraph("Este relatório foi gerado automaticamente pelo sistema de controle de estoque.", nota_style))
            
            # Construir o documento
            doc.build(elementos)
            
            QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso em:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {str(e)}")
    
    def relatorio_estoque_baixo(self):
        """Gera relatório de produtos com estoque baixo."""
        produtos = self.db.verificar_produtos_estoque_baixo()
        
        if not produtos:
            QMessageBox.information(self, "Relatório", "Não há produtos com estoque abaixo do mínimo.")
            return
        
        msg = "Produtos com estoque abaixo do mínimo:\n\n"
        for produto in produtos:
            estoque_minimo = produto['estoque_minimo'] or 0
            msg += f"• {produto['nome']} - Quantidade: {produto['quantidade']} (Mínimo: {estoque_minimo})\n"
        
        # Diálogo com opções de visualizar ou baixar PDF
        dialog = QDialog(self)
        dialog.setWindowTitle("Relatório de Estoque Baixo")
        dialog.setMinimumWidth(400)
        
        dialog_layout = QVBoxLayout(dialog)
        
        # Mensagem
        msg_label = QLabel(msg)
        msg_label.setWordWrap(True)
        dialog_layout.addWidget(msg_label)
        
        # Botões
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        
        pdf_btn = QPushButton("Baixar como PDF")
        pdf_btn.clicked.connect(lambda: self.gerar_pdf_estoque_baixo(produtos))
        
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(pdf_btn)
        dialog_layout.addLayout(btn_layout)
        
        dialog.exec_()
    
    def gerar_pdf_estoque_baixo(self, produtos):
        """Gera um PDF com os produtos com estoque baixo e salva no disco."""
        try:
            # Solicitar local para salvar o arquivo
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Salvar Relatório de Estoque Baixo", 
                os.path.expanduser("~/relatorio_estoque_baixo.pdf"),
                "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return  # Cancelado pelo usuário
            
            # Criar documento PDF
            doc = SimpleDocTemplate(
                file_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Conteúdo do documento
            elementos = []
            
            # Estilos
            styles = getSampleStyleSheet()
            titulo_style = styles["Heading1"]
            subtitulo_style = styles["Heading2"]
            normal_style = styles["Normal"]
            
            # Data atual
            data_atual = datetime.now().strftime("%d/%m/%Y")
            
            # Título
            elementos.append(Paragraph("Relatório de Produtos com Estoque Baixo", titulo_style))
            elementos.append(Spacer(1, 0.5 * cm))
            elementos.append(Paragraph(f"Gerado em: {data_atual}", normal_style))
            elementos.append(Spacer(1, 1 * cm))
            
            # Subtítulo
            elementos.append(Paragraph("Produtos com estoque abaixo do mínimo definido:", subtitulo_style))
            elementos.append(Spacer(1, 0.5 * cm))
            
            # Dados da tabela
            data = [["Nome do Produto", "Qtde. Atual", "Estoque Mínimo", "Diferença", "Fornecedor"]]
            
            # Ordenar produtos por porcentagem em relação ao mínimo
            def calc_percentual(produto):
                # Evitar divisão por zero
                if produto['estoque_minimo'] == 0:
                    return float('inf')
                return produto['quantidade'] / produto['estoque_minimo']
            
            produtos_ordenados = sorted(produtos, key=calc_percentual)
            
            for produto in produtos_ordenados:
                estoque_minimo = produto['estoque_minimo'] or 0
                diferenca = produto['quantidade'] - estoque_minimo
                fornecedor = produto['fornecedor_nome'] if produto['fornecedor_nome'] else "N/A"
                
                data.append([
                    produto['nome'],
                    str(produto['quantidade']),
                    str(estoque_minimo),
                    str(diferenca),
                    fornecedor
                ])
            
            # Criar tabela
            tabela = Table(data, colWidths=[doc.width * 0.3, doc.width * 0.15, doc.width * 0.15, 
                                          doc.width * 0.15, doc.width * 0.25])
            
            # Estilo da tabela
            estilo_tabela = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ])
            
            # Destacar produtos com estoque crítico
            for i, produto in enumerate(produtos_ordenados, 1):
                estoque_minimo = produto['estoque_minimo'] or 0
                
                if estoque_minimo > 0:
                    percentual = produto['quantidade'] / estoque_minimo
                    
                    if percentual <= 0.25:  # Menos que 25% do estoque mínimo
                        estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.pink)
                        estilo_tabela.add('TEXTCOLOR', (0, i), (-1, i), colors.darkred)
                    elif percentual <= 0.5:  # Menos que 50% do estoque mínimo
                        estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.mistyrose)
                        estilo_tabela.add('TEXTCOLOR', (0, i), (-1, i), colors.red)
                    elif percentual <= 0.75:  # Menos que 75% do estoque mínimo
                        estilo_tabela.add('BACKGROUND', (0, i), (-1, i), colors.lightgoldenrodyellow)
                        estilo_tabela.add('TEXTCOLOR', (0, i), (-1, i), colors.darkorange)
            
            tabela.setStyle(estilo_tabela)
            elementos.append(tabela)
            
            # Adicionar legenda
            elementos.append(Spacer(1, 1 * cm))
            elementos.append(Paragraph("Legenda de nível crítico:", subtitulo_style))
            elementos.append(Spacer(1, 0.2 * cm))
            
            legenda_style = ParagraphStyle(
                'Legenda',
                parent=normal_style,
                spaceAfter=6
            )
            
            elementos.append(Paragraph("• <font color='darkred'>Vermelho escuro</font>: Menos de 25% do estoque mínimo", legenda_style))
            elementos.append(Paragraph("• <font color='red'>Vermelho</font>: Entre 25% e 50% do estoque mínimo", legenda_style))
            elementos.append(Paragraph("• <font color='darkorange'>Laranja</font>: Entre 50% e 75% do estoque mínimo", legenda_style))
            
            # Adicionar recomendações
            elementos.append(Spacer(1, 1 * cm))
            elementos.append(Paragraph("Recomendações:", subtitulo_style))
            elementos.append(Spacer(1, 0.2 * cm))
            
            elementos.append(Paragraph("• Produtos em vermelho escuro requerem atenção imediata para reabastecimento.", legenda_style))
            elementos.append(Paragraph("• Considere entrar em contato com os fornecedores para os itens mais críticos.", legenda_style))
            elementos.append(Paragraph("• Verifique frequentemente o status de pedidos pendentes para estes produtos.", legenda_style))
            
            # Tabela de sugestão de compra
            elementos.append(Spacer(1, 1 * cm))
            elementos.append(Paragraph("Sugestão de Compra:", subtitulo_style))
            elementos.append(Spacer(1, 0.5 * cm))
            
            # Dados da tabela de sugestão
            sugestao_data = [["Nome do Produto", "Qtde. a Comprar", "Fornecedor"]]
            
            for produto in produtos_ordenados:
                estoque_minimo = produto['estoque_minimo'] or 0
                # Sugestão: repor até 2x o estoque mínimo
                qtd_sugerida = (estoque_minimo * 2) - produto['quantidade']
                fornecedor = produto['fornecedor_nome'] if produto['fornecedor_nome'] else "N/A"
                
                if qtd_sugerida > 0:
                    sugestao_data.append([
                        produto['nome'],
                        str(qtd_sugerida),
                        fornecedor
                    ])
            
            # Criar tabela de sugestão se houver dados
            if len(sugestao_data) > 1:
                sugestao_tabela = Table(sugestao_data, colWidths=[doc.width * 0.4, doc.width * 0.2, doc.width * 0.4])
                
                # Estilo da tabela de sugestão
                sugestao_estilo = TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.darkblue),
                    ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (1, 1), (1, -1), 'CENTER'),
                ])
                
                sugestao_tabela.setStyle(sugestao_estilo)
                elementos.append(sugestao_tabela)
            else:
                elementos.append(Paragraph("Não há sugestões de compra disponíveis.", normal_style))
            
            # Nota de rodapé
            elementos.append(Spacer(1, 2 * cm))
            nota_style = ParagraphStyle(
                'Nota',
                parent=normal_style,
                fontSize=8,
                textColor=colors.grey
            )
            elementos.append(Paragraph("Este relatório foi gerado automaticamente pelo sistema de controle de estoque.", nota_style))
            
            # Construir o documento
            doc.build(elementos)
            
            QMessageBox.information(self, "Sucesso", f"Relatório salvo com sucesso em:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao gerar PDF: {str(e)}")
    
    def exportar_csv(self):
        """Exporta os dados da tabela atual para um arquivo CSV."""
        try:
            # Solicitar local para salvar o arquivo
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Exportar Estoque para CSV", 
                os.path.expanduser("~/estoque_export.csv"),
                "CSV Files (*.csv)"
            )
            
            if not file_path:
                return  # Cancelado pelo usuário
            
            # Obter dados atuais da tabela (considerando filtros aplicados)
            produtos = []
            for row in range(self.tabela.rowCount()):
                produto = {}
                produto['id'] = self.tabela.item(row, 0).text() if self.tabela.item(row, 0) else ""
                produto['codigo_barras'] = self.tabela.item(row, 1).text() if self.tabela.item(row, 1) else ""
                produto['nome'] = self.tabela.item(row, 2).text() if self.tabela.item(row, 2) else ""
                produto['categoria'] = self.tabela.item(row, 3).text() if self.tabela.item(row, 3) else ""
                produto['estoque_detalhado'] = self.tabela.item(row, 4).text() if self.tabela.item(row, 4) else ""
                produto['estoque_minimo'] = self.tabela.item(row, 5).text() if self.tabela.item(row, 5) else ""
                produto['preco_compra'] = self.tabela.item(row, 6).text() if self.tabela.item(row, 6) else ""
                produto['margem'] = self.tabela.item(row, 7).text() if self.tabela.item(row, 7) else ""
                produto['preco_venda'] = self.tabela.item(row, 8).text() if self.tabela.item(row, 8) else ""
                produto['validade'] = self.tabela.item(row, 9).text() if self.tabela.item(row, 9) else ""
                produto['localizacao'] = self.tabela.item(row, 10).text() if self.tabela.item(row, 10) else ""
                produto['fornecedor'] = self.tabela.item(row, 11).text() if self.tabela.item(row, 11) else ""
                produtos.append(produto)
            
            # Escrever CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'codigo_barras', 'nome', 'categoria', 'estoque_detalhado', 
                            'estoque_minimo', 'preco_compra', 'margem', 'preco_venda', 
                            'validade', 'localizacao', 'fornecedor']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Cabeçalho
                writer.writeheader()
                
                # Dados
                for produto in produtos:
                    writer.writerow(produto)
            
            QMessageBox.information(self, "Sucesso", f"Dados exportados com sucesso para:\n{file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar CSV: {str(e)}")

    def importar_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Importar CSV para Estoque", os.path.expanduser("~"), "CSV Files (*.csv)"
        )
        if not file_path:
            return

        confirmacao = QMessageBox.question(
            self, "Confirmar Importação",
            "A importação será executada em segundo plano.\nDeseja continuar?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao != QMessageBox.Yes:
            return

        # Configura o diálogo de progresso
        self.progress_dialog = QProgressDialog("Importando dados do CSV...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.canceled.connect(self.cancelar_importacao)

        # Cria e inicia a thread
        self.import_thread = CsvImportWorker(self.db.db_path, file_path)
    
        self.import_thread.progress.connect(self.progress_dialog.setValue)
        self.import_thread.finished.connect(self.importacao_concluida)
        self.import_thread.start()
        
        self.progress_dialog.show()

    def cancelar_importacao(self):
        if self.import_thread and self.import_thread.isRunning():
            self.import_thread.terminate() # Encerramento forçado
            QMessageBox.warning(self, "Cancelado", "A importação foi cancelada pelo usuário.")

    def importacao_concluida(self, importados, erros, detalhes_erros):
        self.progress_dialog.close()
        
        # Recarrega os dados na tela
        self.atualizar_visualizacao_dados()

        mensagem = f"Importação concluída!\n\n"
        mensagem += f"Produtos importados/atualizados: {importados}\n"
        mensagem += f"Erros encontrados: {erros}\n"
        
        if detalhes_erros:
            # Exibe apenas os primeiros erros para não sobrecarregar a mensagem
            mensagem += "\nDetalhes dos erros (primeiros 10):\n" + "\n".join(detalhes_erros[:10])

        if erros > 0:
            QMessageBox.warning(self, "Importação com Erros", mensagem)
        else:
            QMessageBox.information(self, "Importação Concluída", mensagem)


    def _extrair_quantidade_do_estoque_detalhado(self, estoque_str):
        """Extrai a quantidade numérica do campo estoque detalhado."""
        try:
            # Se for só um número
            if estoque_str.isdigit():
                return int(estoque_str)
            
            # Se tiver formato complexo, pegar primeiro número
            import re
            numeros = re.findall(r'\d+', estoque_str)
            if numeros:
                return int(numeros[0])
            
            return 0
        except:
            return 0

    def _extrair_preco(self, preco_str):
        """Extrai valor numérico de string de preço."""
        try:
            # Remover R$, espaços e outros caracteres
            preco_limpo = preco_str.replace('R$', '').replace(' ', '').replace(',', '.')
            return float(preco_limpo)
        except:
            return 0.0

    def _extrair_margem(self, margem_str):
        """Extrai valor numérico de string de margem."""
        try:
            margem_limpa = margem_str.replace('%', '').replace(' ', '').replace(',', '.')
            return float(margem_limpa)
        except:
            return 0.0

    def _formatar_data_validade(self, data_str):
        """Formata data de validade para formato YYYY-MM-DD."""
        if not data_str or data_str.strip() == "":
            return None
        
        try:
            # Tentar diferentes formatos de data
            from datetime import datetime
            
            # Formato YYYY-MM-DD (já correto)
            if len(data_str) == 10 and data_str.count('-') == 2:
                datetime.strptime(data_str, "%Y-%m-%d")
                return data_str
            
            # Formato DD/MM/YYYY
            if len(data_str) == 10 and data_str.count('/') == 2:
                data_obj = datetime.strptime(data_str, "%d/%m/%Y")
                return data_obj.strftime("%Y-%m-%d")
            
            # Formato DD-MM-YYYY
            if len(data_str) == 10 and data_str.count('-') == 2:
                data_obj = datetime.strptime(data_str, "%d-%m-%Y")
                return data_obj.strftime("%Y-%m-%d")
            
            return None
        except:
            return None


# Nenhuma alteração necessária nas classes FormularioProduto e DialogQuebrarEmbalagem
class FormularioProduto(QDialog):
    def __init__(self, db, produto_id=None, theme_colors=None):
        super().__init__()
        self.db = db
        self.produto_id = produto_id
        self.theme_colors = theme_colors if theme_colors else {}
        self.produto = None
        
        if produto_id:
            self.produto = self.db.obter_produto(produto_id)
            if not self.produto:
                QMessageBox.warning(self, "Erro", "Produto não encontrado!")
                self.reject()
                return

        self.initUI()
        self.apply_styles()
        
        if self.produto:
            self.carregar_dados_produto()

    def initUI(self):
        self.setWindowTitle("Formulário de Produto")
        
        main_layout = QVBoxLayout(self)
        
        grid_layout = QGridLayout()
        grid_layout.setSpacing(20)

        # --- COLUNA 1: INFORMAÇÕES DO PRODUTO ---
        info_group = QGroupBox("Informações do Produto")
        info_form_layout = QFormLayout(info_group)
        info_form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        
        self.codigo_barras_input = QLineEdit()
        self.nome_input = QLineEdit()
        self.descricao_input = QLineEdit()
        self.categoria_combo = QComboBox(); self.categoria_combo.setEditable(True); self.carregar_categorias()
        self.fornecedor_combo = QComboBox(); self.carregar_fornecedores()
        self.localizacao_input = QLineEdit()
        
        # ===== INÍCIO DA CORREÇÃO PRINCIPAL =====
        # Usando os nomes semânticos (apelidos) definidos no IconManager
        info_form_layout.addRow("Código de Barras:", self._create_input_with_icon('barcode', self.codigo_barras_input))
        info_form_layout.addRow("Nome do Produto:", self._create_input_with_icon('box', self.nome_input))
        info_form_layout.addRow("Descrição:", self._create_input_with_icon('comment-alt', self.descricao_input))
        info_form_layout.addRow("Categoria:", self._create_input_with_icon('tags', self.categoria_combo))
        info_form_layout.addRow("Fornecedor:", self._create_input_with_icon('truck', self.fornecedor_combo))
        info_form_layout.addRow("Localização:", self._create_input_with_icon('map-marker-alt', self.localizacao_input))

        # --- COLUNA 2: ESTOQUE E PRECIFICAÇÃO ---
        preco_group = QGroupBox("Estoque e Precificação")
        preco_form_layout = QFormLayout(preco_group)
        preco_form_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)

        self.quantidade_input = QSpinBox(); self.quantidade_input.setRange(0, 99999)
        self.estoque_minimo_input = QSpinBox(); self.estoque_minimo_input.setRange(0, 99999)
        self.preco_compra_input = QDoubleSpinBox(); self.preco_compra_input.setRange(0, 99999.99); self.preco_compra_input.setPrefix("R$ ")
        self.margem_lucro_input = QDoubleSpinBox(); self.margem_lucro_input.setRange(0, 999.99); self.margem_lucro_input.setSuffix(" %")
        self.preco_venda_input = QDoubleSpinBox(); self.preco_venda_input.setRange(0, 99999.99); self.preco_venda_input.setPrefix("R$ ")
        self.data_validade_input = QDateEdit(calendarPopup=True); self.data_validade_input.setDisplayFormat("dd/MM/yyyy")

        preco_form_layout.addRow("Quantidade:", self._create_input_with_icon('estoque', self.quantidade_input))
        preco_form_layout.addRow("Estoque Mínimo:", self._create_input_with_icon('estoque_baixo', self.estoque_minimo_input))
        preco_form_layout.addRow("Preço de Compra:", self._create_input_with_icon('dollar-sign', self.preco_compra_input))
        preco_form_layout.addRow("Margem de Lucro:", self._create_input_with_icon('percentage', self.margem_lucro_input))
        preco_form_layout.addRow("Preço de Venda:", self._create_input_with_icon('caixa', self.preco_venda_input))
        preco_form_layout.addRow("Data de Validade:", self._create_input_with_icon('vencimentos', self.data_validade_input))

        grid_layout.addWidget(info_group, 0, 0)
        grid_layout.addWidget(preco_group, 0, 1)

        # --- LINHA 2: GRUPO DE FRACIONAMENTO ---
        self.fracionado_group = QGroupBox("Produto Fracionado")
        self.fracionado_group.setCheckable(True)
        self.fracionado_group.setChecked(False)
        fracionado_layout = QFormLayout(self.fracionado_group)
        
        self.unidade_medida_input = QLineEdit(); self.unidade_medida_input.setPlaceholderText("Ex: kg, L, m")
        self.qtd_por_embalagem_input = QSpinBox(); self.qtd_por_embalagem_input.setRange(1, 9999)
        self.preco_unitario_fracao_input = QDoubleSpinBox(); self.preco_unitario_fracao_input.setRange(0, 99999.99); self.preco_unitario_fracao_input.setPrefix("R$ ")
        self.estoque_fracionado_input = QSpinBox(); self.estoque_fracionado_input.setRange(0, 99999)
        
        fracionado_layout.addRow("Unidade de Medida:", self._create_input_with_icon('ruler', self.unidade_medida_input))
        fracionado_layout.addRow("Unidades por Embalagem:", self._create_input_with_icon('box-open', self.qtd_por_embalagem_input))
        fracionado_layout.addRow("Preço Unitário (Fração):", self._create_input_with_icon('tag', self.preco_unitario_fracao_input))
        fracionado_layout.addRow("Estoque Fracionado Atual:", self._create_input_with_icon('cubes', self.estoque_fracionado_input))
        
        grid_layout.addWidget(self.fracionado_group, 1, 0, 1, 2)
        # ===== FIM DA CORREÇÃO PRINCIPAL =====

        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(" Salvar Produto")
        self.salvar_btn.setObjectName("primaryActionButton")
        self.salvar_btn.clicked.connect(self.salvar_produto)
        
        self.cancelar_btn = QPushButton(" Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        
        main_layout.addLayout(button_layout)
        
        self.preco_compra_input.valueChanged.connect(self.calcular_preco_venda)
        self.margem_lucro_input.valueChanged.connect(self.calcular_preco_venda)
        self.preco_venda_input.valueChanged.connect(self.calcular_margem_lucro)

    # ... todos os outros métodos de FormularioProduto (apply_styles, _create_input_with_icon, etc) permanecem os mesmos
    def _create_input_with_icon(self, icon_name, widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        # Esta função agora receberá o nome semântico correto
        icon_label.setPixmap(IconManager.get_icon(icon_name, color=icon_color).pixmap(16, 16))
        
        layout.addWidget(icon_label)
        layout.addWidget(widget, 1)
        return container

    def apply_styles(self):
        theme = self.theme_colors
        if not theme: return

        style = f"""
            QDialog {{
                background-color: {theme.get('bg_color', '#fff')};
            }}
            QGroupBox {{
                font-size: 11pt;
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 8px; margin-top: 15px; padding: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 10px; margin-left: 10px;
                background-color: {theme.get('bg_color', '#fff')};
                color: {theme.get('text_secondary', '#333')};
            }}
            QGroupBox:checked {{
                border-color: {theme.get('accent_color', '#007aff')};
            }}
            QLabel {{
                color: {theme.get('text_color', '#000')};
                font-size: 10pt;
            }}
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: {theme.get('surface_color', '#f2f2f7')};
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 4px; padding: 8px; min-height: 20px;
            }}
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border: 2px solid {theme.get('accent_color', '#007aff')};
            }}
            QPushButton {{
                padding: 10px 15px; border-radius: 6px; font-weight: bold;
            }}
            #primaryActionButton {{
                background-color: {theme.get('accent_color', '#007aff')};
                color: white; border: none;
            }}
            #primaryActionButton:hover {{
                background-color: #0069d9;
            }}
        """
        self.setStyleSheet(style)
        
        self.salvar_btn.setIcon(IconManager.get_icon('save', 'white'))
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', theme.get('text_color', '#000')))
    
    def carregar_categorias(self):
        self.categoria_combo.clear()
        self.categoria_combo.addItem("Selecione ou crie uma categoria", "")
        categorias = self.db.listar_categorias_unicas()
        for categoria in categorias:
            self.categoria_combo.addItem(categoria, categoria)
    
    def calcular_preco_venda(self):
        preco_compra = self.preco_compra_input.value()
        margem = self.margem_lucro_input.value() / 100
        preco_venda = preco_compra * (1 + margem)
        self.preco_venda_input.blockSignals(True)
        self.preco_venda_input.setValue(preco_venda)
        self.preco_venda_input.blockSignals(False)

    def calcular_margem_lucro(self):
        preco_compra = self.preco_compra_input.value()
        preco_venda = self.preco_venda_input.value()
        if preco_compra > 0:
            margem = ((preco_venda / preco_compra) - 1) * 100
            self.margem_lucro_input.blockSignals(True)
            self.margem_lucro_input.setValue(margem)
            self.margem_lucro_input.blockSignals(False)
    
    def carregar_fornecedores(self):
        self.fornecedor_combo.clear()
        self.fornecedor_combo.addItem("Selecione um fornecedor", None)
        fornecedores = self.db.listar_fornecedores()
        for fornecedor in fornecedores:
            self.fornecedor_combo.addItem(fornecedor['empresa'], fornecedor['id'])
    
    def carregar_dados_produto(self):
        self.codigo_barras_input.setText(self.produto['codigo_barras'] or "")
        self.nome_input.setText(self.produto['nome'])
        self.descricao_input.setText(self.produto['descricao'] or "")
        self.quantidade_input.setValue(self.produto['quantidade'])
        self.estoque_minimo_input.setValue(self.produto['estoque_minimo'] or 0)
        self.preco_compra_input.setValue(self.produto['preco_compra'])
        self.margem_lucro_input.setValue(self.produto['margem_lucro'] or 30.0)
        self.preco_venda_input.setValue(self.produto['preco_venda'])
        if self.produto['data_validade']:
            self.data_validade_input.setDate(QDate.fromString(self.produto['data_validade'], "yyyy-MM-dd"))
        self.localizacao_input.setText(self.produto['localizacao'] or "")
        
        if self.produto['fornecedor_id']:
            index = self.fornecedor_combo.findData(self.produto['fornecedor_id'])
            if index != -1: self.fornecedor_combo.setCurrentIndex(index)
        
        if self.produto['categoria']:
            index = self.categoria_combo.findText(self.produto['categoria'])
            if index != -1: self.categoria_combo.setCurrentIndex(index)
            else:
                self.categoria_combo.addItem(self.produto['categoria'])
                self.categoria_combo.setCurrentText(self.produto['categoria'])
        
        is_fracionado = bool(self.produto['fracionado'])
        self.fracionado_group.setChecked(is_fracionado)
        
        if is_fracionado:
            self.unidade_medida_input.setText(self.produto['unidade_medida'] or "")
            
            # --- LINHA CORRIGIDA ---
            # Converte o valor para inteiro antes de passá-lo para o QSpinBox.
            self.qtd_por_embalagem_input.setValue(int(self.produto['qtd_por_embalagem'] or 1))
            
            self.preco_unitario_fracao_input.setValue(self.produto['preco_unitario_fracao'] or 0.0)
            self.estoque_fracionado_input.setValue(self.produto['estoque_fracionado'] or 0)

    def salvar_produto(self):
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do produto é obrigatório!")
            return
            
        dados = {
            'codigo_barras': self.codigo_barras_input.text().strip(),
            'nome': self.nome_input.text().strip(),
            'descricao': self.descricao_input.text().strip(),
            'categoria': self.categoria_combo.currentText().strip() if self.categoria_combo.currentText() != "Selecione ou crie uma categoria" else None,
            'fornecedor_id': self.fornecedor_combo.currentData(),
            'quantidade': self.quantidade_input.value(),
            'estoque_minimo': self.estoque_minimo_input.value(),
            'preco_compra': self.preco_compra_input.value(),
            'margem_lucro': self.margem_lucro_input.value(),
            'preco_venda': self.preco_venda_input.value(),
            'data_validade': self.data_validade_input.date().toString("yyyy-MM-dd"),
            'localizacao': self.localizacao_input.text().strip(),
            'fracionado': self.fracionado_group.isChecked(),
            'unidade_medida': self.unidade_medida_input.text().strip() if self.fracionado_group.isChecked() else 'unidade',
            'qtd_por_embalagem': self.qtd_por_embalagem_input.value() if self.fracionado_group.isChecked() else 1,
            'preco_unitario_fracao': self.preco_unitario_fracao_input.value() if self.fracionado_group.isChecked() else 0.0,
            'estoque_fracionado': self.estoque_fracionado_input.value() if self.fracionado_group.isChecked() else 0,
        }
        
        try:
            if self.produto_id:
                sucesso = self.db.atualizar_produto(self.produto_id, **dados)
                mensagem = "Produto atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_produto(**dados)
                mensagem = "Produto cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro no Banco de Dados", "Não foi possível salvar o produto.")
        except Exception as e:
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro: {e}")

# ================================================================= #
#       CLASSE DIALOGQUEBRAREMBALAGEM TOTALMENTE CORRIGIDA          #
# ================================================================= #
class DialogQuebrarEmbalagem(QDialog):
    # MUDANÇA 1: Adicionar theme_colors ao construtor
    def __init__(self, db, produto_info, theme_colors=None):
        super().__init__()
        self.db = db
        self.produto_info = produto_info
        # Armazenar as cores do tema
        self.theme_colors = theme_colors if theme_colors else {}
        
        self.initUI()
        # MUDANÇA 2: Aplicar os estilos, assim como no FormularioProduto
        self.apply_styles()

    def initUI(self):
        self.setWindowTitle("Quebrar Embalagem")
        self.setMinimumWidth(450) # Aumentar um pouco a largura para os ícones
        
        layout = QVBoxLayout(self)
        
        info_group = QGroupBox("Informações do Produto")
        info_layout = QFormLayout(info_group)
        info_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        info_layout.setSpacing(15)

        # MUDANÇA 3: Usar o helper para adicionar ícones aos campos de informação
        info_layout.addRow(self._create_info_row('box', "Produto:", self.produto_info['nome']))
        info_layout.addRow(self._create_info_row('estoque', "Embalagens disponíveis:", str(self.produto_info['embalagens_inteiras'])))
        info_layout.addRow(self._create_info_row('box-open', "Unidades por embalagem:", str(self.produto_info['qtd_por_embalagem'])))
        info_layout.addRow(self._create_info_row('cubes', "Estoque fracionado atual:", f"{self.produto_info['estoque_fracionado']} {self.produto_info['unidade_medida']}"))
        
        layout.addWidget(info_group)
        
        quebrar_group = QGroupBox("Quebrar Embalagens")
        quebrar_layout = QFormLayout(quebrar_group)
        quebrar_layout.setSpacing(15)
        
        self.quantidade_input = QSpinBox()
        self.quantidade_input.setRange(1, self.produto_info['embalagens_inteiras'])
        self.quantidade_input.setValue(1)
        self.quantidade_input.valueChanged.connect(self.atualizar_preview)
        
        # MUDANÇA 4: Usar o helper para adicionar ícone ao campo de entrada
        quebrar_layout.addRow("Quantidade a quebrar:", self._create_input_with_icon('break', self.quantidade_input))
        
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("font-style: italic;")
        self.atualizar_preview()
        quebrar_layout.addRow("Resultado:", self._create_info_row('check', "Novo estoque:", self.preview_label))
        
        layout.addWidget(quebrar_group)
        layout.addStretch()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.confirmar_btn = QPushButton(" Confirmar")
        self.confirmar_btn.setObjectName("primaryActionButton")
        self.confirmar_btn.clicked.connect(self.quebrar_embalagem)
        
        self.cancelar_btn = QPushButton(" Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.confirmar_btn)
    
        # MUDANÇA 5: CORREÇÃO CRÍTICA - Adicionar o layout dos botões ao layout principal
        # Este era o motivo pelo qual seus botões não apareciam.
        layout.addLayout(button_layout)

    def atualizar_preview(self):
        qtd_quebrar = self.quantidade_input.value()
        unidades_geradas = qtd_quebrar * self.produto_info['qtd_por_embalagem']
        novo_estoque_fracionado = self.produto_info['estoque_fracionado'] + unidades_geradas
        novas_embalagens = self.produto_info['embalagens_inteiras'] - qtd_quebrar
        
        preview_text = (f"{novas_embalagens} emb. + {novo_estoque_fracionado} {self.produto_info['unidade_medida']}"
                        f"\n(Serão geradas +{unidades_geradas} unidades)")
        self.preview_label.setText(preview_text)

    # MUDANÇA 6: Adicionar método para aplicar estilos (similar ao FormularioProduto)
    def apply_styles(self):
        theme = self.theme_colors
        if not theme: return

        # Estilo geral para o diálogo, grupos e labels
        style = f"""
            QDialog {{ background-color: {theme.get('bg_color', '#fff')}; }}
            QGroupBox {{
                font-size: 10pt; border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 8px; margin-top: 15px; padding: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top left;
                padding: 0 10px; margin-left: 10px;
                background-color: {theme.get('bg_color', '#fff')};
                color: {theme.get('text_secondary', '#333')};
            }}
            QLabel {{ color: {theme.get('text_color', '#000')}; font-size: 10pt; }}
            QSpinBox {{
                background-color: {theme.get('surface_color', '#f2f2f7')};
                color: {theme.get('text_color', '#000')};
                border: 1px solid {theme.get('border_color', '#ccc')};
                border-radius: 4px; padding: 8px; min-height: 20px;
            }}
            QSpinBox:focus {{ border: 2px solid {theme.get('accent_color', '#007aff')}; }}
            QPushButton {{ padding: 10px 15px; border-radius: 6px; font-weight: bold; }}
            #primaryActionButton {{
                background-color: {theme.get('accent_color', '#007aff')}; color: white; border: none;
            }}
            #primaryActionButton:hover {{ background-color: #0069d9; }}
        """
        self.setStyleSheet(style)
        
        # Adicionar ícones aos botões
        self.confirmar_btn.setIcon(IconManager.get_icon('confirm', 'white'))
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', theme.get('text_color', '#000')))

    # MUDANÇA 7: Adicionar helpers para criar widgets com ícones (similar ao FormularioProduto)
    def _create_input_with_icon(self, icon_name, widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        icon_label.setPixmap(IconManager.get_icon(icon_name, color=icon_color).pixmap(16, 16))
        
        layout.addWidget(icon_label)
        layout.addWidget(widget, 1)
        return container

    def _create_info_row(self, icon_name, label_text, info_text_or_widget):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        icon_label = QLabel()
        icon_color = self.theme_colors.get('text_secondary', '#6d6d70')
        icon_label.setPixmap(IconManager.get_icon(icon_name, color=icon_color).pixmap(16, 16))
        
        field_label = QLabel(label_text)
        field_label.setStyleSheet("font-weight: bold;")
        
        layout.addWidget(icon_label)
        layout.addWidget(field_label)
        
        if isinstance(info_text_or_widget, QWidget):
            layout.addWidget(info_text_or_widget, 1)
        else:
            info_label = QLabel(str(info_text_or_widget))
            info_label.setWordWrap(True)
            layout.addWidget(info_label, 1)
            
        return container
    
    def quebrar_embalagem(self):
        qtd_quebrar = self.quantidade_input.value()
        confirmacao = QMessageBox.question(
            self, "Confirmar Quebra",
            f"Confirma quebrar {qtd_quebrar} embalagem(ns) em unidades fracionadas?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao == QMessageBox.Yes:
            if self.db.quebrar_embalagem(self.produto_info['produto_id'], qtd_quebrar):
                QMessageBox.information(self, "Sucesso", "Embalagem quebrada com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível quebrar a embalagem.")