from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QDoubleSpinBox,
                           QDialog, QFrame, QTabWidget, QRadioButton, QFileDialog, 
                           QSizePolicy, QGroupBox, QProgressDialog)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
import csv
import os
import math

# Importações necessárias
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager

# ================================================================= #
#       CLASSE WORKER PARA IMPORTAÇÃO DE CSV EM THREAD              #
# ================================================================= #

class PromocaoCsvImportWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, int, list)

    def __init__(self, db_path, file_path):
        super().__init__()
        self.db_path = db_path
        self.file_path = file_path
        self.local_db = None

    def run(self):
        importadas = 0
        erros = 0
        detalhes_erros = []
        try:
            self.local_db = DatabaseManager(self.db_path)
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                total_linhas = max(1, sum(1 for _ in f) - 1)

            with open(self.file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                self.local_db.begin_transaction()
                
                for i, row in enumerate(reader):
                    try:
                        produto_nome = row.get('Produto', '').strip()
                        if not produto_nome:
                            raise ValueError("Nome do produto é obrigatório.")
                        
                        produto = self.local_db.buscar_produto_por_nome_exato(produto_nome)
                        if not produto:
                            raise ValueError(f"Produto '{produto_nome}' não encontrado.")

                        preco_antigo = float(row['Preço Antigo'].replace(',', '.'))
                        preco_promo = float(row['Preço Promocional'].replace(',', '.'))
                        data_inicio = datetime.strptime(row['Data Início'], '%d/%m/%Y').strftime('%Y-%m-%d')
                        data_fim = datetime.strptime(row['Data Fim'], '%d/%m/%Y').strftime('%Y-%m-%d')

                        self.local_db.adicionar_promocao(
                            produto_id=produto['id'],
                            preco_antigo=preco_antigo,
                            preco_promocional=preco_promo,
                            data_inicio=data_inicio,
                            data_fim=data_fim,
                            descricao=row.get('Descrição', '').strip()
                        )
                        importadas += 1
                    except Exception as e:
                        erros += 1
                        detalhes_erros.append(f"Linha {i+2}: {e}")
                    self.progress.emit(int(((i + 1) / total_linhas) * 100))
                
                self.local_db.commit_transaction()
        except Exception as e:
            if self.local_db: self.local_db.rollback_transaction()
            detalhes_erros.append(f"Erro geral: {e}")
        finally:
            if self.local_db: self.local_db.fechar()
        
        self.finished.emit(importadas, erros, detalhes_erros)


class PromocoesWindow(QWidget):
    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.pagina_atual = 1
        self.itens_por_pagina = 50
        self.total_paginas = 1

        self.initUI()
        self.atualizar_visualizacao_dados()

    def set_theme(self, theme_colors):
        self.theme_colors = theme_colors
        self.update_button_icons()
        self.atualizar_visualizacao_dados()

    def update_button_icons(self):
        icon_color = self.theme_colors.get('text_color', '#000')

        self.search_button.setIcon(IconManager.get_icon('search', icon_color))
        self.exportar_button.setIcon(IconManager.get_icon('export', icon_color))
        self.importar_button.setIcon(IconManager.get_icon('import', icon_color))
        # A linha do 'produtos_especiais_button' foi removida.

        self.add_button.setIcon(IconManager.get_icon('add', 'white'))
        self.prev_page_btn.setIcon(IconManager.get_icon('angle-left', icon_color))
        self.next_page_btn.setIcon(IconManager.get_icon('angle-right', icon_color))

    def initUI(self):
        layout = QVBoxLayout(self)
        titulo = QLabel("Gerenciamento de Promoções")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)

        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar promoção pelo nome do produto...")
        self.search_input.returnPressed.connect(self.pesquisar_promocoes)
        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar")
        self.search_button.clicked.connect(self.pesquisar_promocoes)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addWidget(search_group)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels(["ID", "Produto", "Preço Antigo", "Desconto %", "Preço Promo", "Início", "Fim", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        paginacao_layout = QHBoxLayout()
        # O espaço no texto ajuda a separar o ícone do texto visualmente
        self.prev_page_btn = QPushButton(" Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
        
        self.page_label = QLabel(f"Página {self.pagina_atual} de {self.total_paginas}")
        
        self.next_page_btn = QPushButton("Próxima ")
        # Garante que o ícone fique à direita do texto
        self.next_page_btn.setLayoutDirection(Qt.RightToLeft)
        self.next_page_btn.clicked.connect(self.ir_proxima_pagina)
        
        paginacao_layout.addWidget(self.prev_page_btn)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.page_label)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.next_page_btn)
        layout.addLayout(paginacao_layout)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        self.add_button = QPushButton(" Adicionar Promoção")
        self.add_button.setObjectName("primaryActionButton")
        self.add_button.clicked.connect(self.abrir_formulario_promocao)
        
        self.exportar_button = QPushButton(" Exportar CSV")
        self.exportar_button.clicked.connect(self.exportar_csv)
        
        self.importar_button = QPushButton(" Importar CSV")
        self.importar_button.clicked.connect(self.importar_csv)

        botoes_acao = [self.add_button, self.exportar_button, self.importar_button]

        for btn in botoes_acao:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            action_layout.addWidget(btn)
            
        layout.addLayout(action_layout)
        # Esta chamada garante que os ícones sejam carregados na inicialização
        self.update_button_icons()

    def ir_pagina_anterior(self):
        if self.pagina_atual > 1:
            self.pagina_atual -= 1
            self.atualizar_visualizacao_dados()

    def ir_proxima_pagina(self):
        if self.pagina_atual < self.total_paginas:
            self.pagina_atual += 1
            self.atualizar_visualizacao_dados()

    def carregar_dados(self):
        self.pagina_atual = 1
        self.search_input.clear()
        self.atualizar_visualizacao_dados()

    def pesquisar_promocoes(self):
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()

    def atualizar_visualizacao_dados(self):
        filtros = {'termo_pesquisa': self.search_input.text()}
        total_itens = self.db.contar_promocoes_filtradas(filtros)
        promocoes = self.db.listar_promocoes_paginado_e_filtrado(
            filtros, self.pagina_atual, self.itens_por_pagina
        )
        self.atualizar_tabela(promocoes)
        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina) or 1
        self.page_label.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.prev_page_btn.setEnabled(self.pagina_atual > 1)
        self.next_page_btn.setEnabled(self.pagina_atual < self.total_paginas)

    def atualizar_tabela(self, promocoes):
        self.tabela.setRowCount(0)
        icon_color = self.theme_colors.get('text_color', '#000')

        for row, promocao in enumerate(promocoes):
            self.tabela.insertRow(row)
            
            preco_antigo = promocao['preco_antigo']
            preco_promocional = promocao['preco_promocional']
            taxa_desconto = ((preco_antigo - preco_promocional) / preco_antigo) * 100 if preco_antigo > 0 else 0
            
            self.tabela.setItem(row, 0, QTableWidgetItem(str(promocao['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(promocao['produto_nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(f"R$ {promocao['preco_antigo']:.2f}"))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{taxa_desconto:.1f}%"))
            self.tabela.setItem(row, 4, QTableWidgetItem(f"R$ {promocao['preco_promocional']:.2f}"))
            self.tabela.setItem(row, 5, QTableWidgetItem(str(promocao['data_inicio'])))
            self.tabela.setItem(row, 6, QTableWidgetItem(str(promocao['data_fim'])))
            
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(5, 2, 5, 2)
            acoes_layout.setSpacing(5)

            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), " ")
            editar_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            editar_btn.clicked.connect(lambda _, p_id=promocao['id']: self.abrir_formulario_promocao(p_id))
            
            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), " ")
            excluir_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            excluir_btn.clicked.connect(lambda _, p_id=promocao['id']: self.excluir_promocao(p_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            self.tabela.setCellWidget(row, 7, acoes_widget)
            
    # ... O restante do código (abrir formulários, excluir, importar, exportar) permanece o mesmo ...
    def abrir_formulario_promocao(self, promocao_id=None):
        # A chamada agora passa o parent, como corrigido anteriormente
        dialog = FormularioPromocao(self.db, self.theme_colors, promocao_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_visualizacao_dados()
            
    def excluir_promocao(self, promocao_id):
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir esta promoção?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_promocao(promocao_id):
                QMessageBox.information(self, "Sucesso", "Promoção excluída.")
                self.atualizar_visualizacao_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir a promoção.")
    
    def exportar_csv(self):
        try:
            promocoes = self.db.listar_promocoes()
            if not promocoes:
                QMessageBox.information(self, "Aviso", "Não há promoções para exportar!")
                return
            arquivo, _ = QFileDialog.getSaveFileName(
            
                self, "Exportar Promoções", "promocoes.csv", "Arquivos CSV (*.csv)"
            )
            
            if arquivo:
                with open(arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = ['ID', 'Produto', 'Preço Antigo', 'Preço Promocional', 
                                'Taxa de Desconto (%)', 'Data Início', 'Data Fim', 'Descrição']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    
                    for promocao in promocoes:
                        taxa_desconto = 0
                        if promocao['preco_antigo'] > 0:
                            taxa_desconto = ((promocao['preco_antigo'] - promocao['preco_promocional']) / promocao['preco_antigo']) * 100
                        
                        writer.writerow({
                            'ID': promocao['id'], 'Produto': promocao['produto_nome'],
                            'Preço Antigo': f"{promocao['preco_antigo']:.2f}",
                            'Preço Promocional': f"{promocao['preco_promocional']:.2f}",
                            'Taxa de Desconto (%)': f"{taxa_desconto:.1f}",
                            'Data Início': promocao['data_inicio'], 'Data Fim': promocao['data_fim'],
                            'Descrição': promocao.get('descricao', '')
                        })
                
                QMessageBox.information(self, "Sucesso", f"Promoções exportadas para:\n{arquivo}")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar CSV:\n{str(e)}")

    def importar_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importar Promoções CSV", "", "CSV Files (*.csv)")
        if not file_path: return

        self.progress_dialog = QProgressDialog("Importando promoções...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        
        self.import_thread = PromocaoCsvImportWorker(self.db.db_path, file_path)
        self.import_thread.progress.connect(self.progress_dialog.setValue)
        self.import_thread.finished.connect(self.importacao_concluida)
        self.progress_dialog.canceled.connect(self.import_thread.terminate)
        self.import_thread.start()
        self.progress_dialog.exec_()

    def importacao_concluida(self, importadas, erros, detalhes):
        self.progress_dialog.close()
        self.atualizar_visualizacao_dados()
        msg = f"Importação concluída!\n\nSucesso: {importadas}\nFalhas: {erros}"
        if erros > 0:
            msg += "\n\nPrimeiros erros:\n" + "\n".join(detalhes[:5])
            QMessageBox.warning(self, "Importação com Erros", msg)
        else:
            QMessageBox.information(self, "Importação Concluída", msg)

class FormularioPromocao(QDialog):
    def __init__(self, db, theme_colors, promocao_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.theme_colors = theme_colors
        self.promocao_id = promocao_id
        self.promocao = None
        self.produto_selecionado_id = None # Armazena o ID do produto escolhido

        if promocao_id:
            self.promocao = self.db.obter_promocao(promocao_id)
            if self.promocao:
                self.produto_selecionado_id = self.promocao['produto_id']

        self.initUI()
        self.apply_styles()
        
        if self.promocao:
            self.carregar_dados_promocao()
        else:
            self.carregar_produtos_recomendados()
            self.carregar_todos_os_produtos()
    
    def initUI(self):
        self.setWindowTitle("Cadastro de Promoção")
        self.setMinimumSize(600, 650)
        layout = QVBoxLayout(self)

        # --- SELEÇÃO DE PRODUTO (NOVA ABORDAGEM COM ABAS) ---
        produto_group = QGroupBox("1. Selecione o Produto", self)
        produto_layout = QVBoxLayout(produto_group)
        
        self.tabs_selecao_produto = QTabWidget(self)
        
        # Aba 1: Produtos Recomendados
        tab_recomendados = QWidget()
        layout_recomendados = QVBoxLayout(tab_recomendados)
        self.tabela_recomendados = QTableWidget(self)
        self.tabela_recomendados.setColumnCount(4)
        self.tabela_recomendados.setHorizontalHeaderLabels(["Produto", "Motivo", "Estoque/Validade", "Preço Atual"])
        self.tabela_recomendados.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_recomendados.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela_recomendados.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabela_recomendados.cellClicked.connect(self.selecionar_produto_pela_tabela)
        layout_recomendados.addWidget(self.tabela_recomendados)
        
        # Aba 2: Todos os Produtos
        tab_todos = QWidget()
        layout_todos = QVBoxLayout(tab_todos)
        self.combo_todos_produtos = QComboBox(self)
        self.combo_todos_produtos.currentIndexChanged.connect(self.selecionar_produto_pelo_combo)
        layout_todos.addWidget(QLabel("Buscar e selecionar um produto específico:", self))
        layout_todos.addWidget(self.combo_todos_produtos)
        layout_todos.addStretch()

        self.tabs_selecao_produto.addTab(tab_recomendados, "Recomendados")
        self.tabs_selecao_produto.addTab(tab_todos, "Todos os Produtos")
        produto_layout.addWidget(self.tabs_selecao_produto)
        layout.addWidget(produto_group)

        # --- DETALHES DA PROMOÇÃO ---
        detalhes_group = QGroupBox("2. Defina os Detalhes da Promoção", self)
        form_layout = QFormLayout(detalhes_group)

        self.produto_selecionado_label = QLabel("Nenhum produto selecionado")
        self.produto_selecionado_label.setStyleSheet("font-weight: bold;")
        
        self.preco_antigo_input = QDoubleSpinBox(self)
        self.preco_antigo_input.setReadOnly(True)
        self.preco_antigo_input.setRange(0, 99999.99); self.preco_antigo_input.setPrefix("R$ ")
        
        self.taxa_desconto_input = QDoubleSpinBox(self)
        self.taxa_desconto_input.setRange(0.1, 100); self.taxa_desconto_input.setSuffix(" %")
        self.taxa_desconto_input.setValue(10)
        self.taxa_desconto_input.valueChanged.connect(self.calcular_preco_promocional)
        
        self.preco_promocional_input = QDoubleSpinBox(self)
        self.preco_promocional_input.setRange(0, 99999.99); self.preco_promocional_input.setPrefix("R$ ")
        self.preco_promocional_input.valueChanged.connect(self.calcular_taxa_desconto)
        
        self.data_inicio_input = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.data_inicio_input.setDisplayFormat("dd/MM/yyyy")
        self.data_fim_input = QDateEdit(calendarPopup=True, date=QDate.currentDate().addDays(30))
        self.data_fim_input.setDisplayFormat("dd/MM/yyyy")
        self.descricao_input = QLineEdit(self)

        form_layout.addRow("Produto em Promoção:", self.produto_selecionado_label)
        form_layout.addRow("Preço Original:", self.preco_antigo_input)
        form_layout.addRow("Taxa de Desconto:", self.taxa_desconto_input)
        form_layout.addRow("Preço Promocional:", self.preco_promocional_input)
        form_layout.addRow("Data de Início:", self.data_inicio_input)
        form_layout.addRow("Data de Fim:", self.data_fim_input)
        form_layout.addRow("Descrição:", self.descricao_input)
        layout.addWidget(detalhes_group)

        # --- BOTÕES DE AÇÃO ---
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(" Salvar Promoção")
        self.salvar_btn.setObjectName("primaryActionButton")
        self.salvar_btn.clicked.connect(self.salvar_promocao)
        
        self.cancelar_btn = QPushButton(" Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        layout.addLayout(button_layout)
    
    def apply_styles(self):
        """Aplica os estilos do tema principal a todos os componentes do diálogo."""
        colors = self.theme_colors
        # Estilo completo para garantir que todos os widgets herdem a aparência.
        style = f"""
            QDialog {{
                background-color: {colors.get('bg_color', '#fff')};
                color: {colors.get('text_color', '#000')};
            }}
            QGroupBox {{
                border: 1px solid {colors.get('border_color', '#ccc')};
                border-radius: 6px; margin-top: 15px; padding: 10px; font-weight: bold;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin; subcontrol-position: top center;
                padding: 0 10px; background-color: {colors.get('bg_color', '#fff')};
                color: {colors.get('text_secondary', '#333')};
            }}
            QTableWidget {{
                background-color: {colors.get('surface_color', '#f2f2f7')};
                border: 1px solid {colors.get('border_color', '#d1d1d6')};
                gridline-color: {colors.get('border_color', '#d1d1d6')};
            }}
            QHeaderView::section {{
                background-color: {colors.get('bg_color', '#fff')};
                color: {colors.get('text_color', '#000')};
                padding: 5px; border: 1px solid {colors.get('border_color', '#d1d1d6')};
                font-weight: bold;
            }}
            QComboBox, QDoubleSpinBox, QDateEdit, QLineEdit {{
                background-color: {colors.get('bg_color', '#fff')};
                color: {colors.get('text_color', '#000')};
                border: 1px solid {colors.get('border_color', '#ccc')};
                border-radius: 4px; padding: 5px;
            }}
            QPushButton {{
                background-color: transparent; color: {colors.get('text_color', '#000')};
                border: 1px solid {colors.get('border_color', '#ccc')};
                padding: 8px 12px; border-radius: 4px; font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {colors.get('button_hover', '#e0e0e0')};
                border: 1px solid {colors.get('accent_color', '#007aff')};
            }}
            #primaryActionButton {{
                background-color: {colors.get('accent_color', '#007aff')};
                color: white; border: none;
            }}
            #primaryActionButton:hover {{ background-color: #0069d9; }}
        """
        self.setStyleSheet(style)
        self.salvar_btn.setIcon(IconManager.get_icon('save', 'white'))
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', colors.get('text_color', '#000')))
        
    # ... O restante da classe FormularioPromocao permanece o mesmo ...
    def calcular_preco_promocional(self):
        preco_antigo = self.preco_antigo_input.value()
        taxa_desconto = self.taxa_desconto_input.value()
        preco_promocional = preco_antigo * (1 - taxa_desconto / 100)
        self.preco_promocional_input.blockSignals(True)
        self.preco_promocional_input.setValue(preco_promocional)
        self.preco_promocional_input.blockSignals(False)

    def calcular_taxa_desconto(self):
        preco_antigo = self.preco_antigo_input.value()
        preco_promocional = self.preco_promocional_input.value()
        if preco_antigo > 0:
            taxa_desconto = ((preco_antigo - preco_promocional) / preco_antigo) * 100
            self.taxa_desconto_input.blockSignals(True)
            self.taxa_desconto_input.setValue(taxa_desconto)
            self.taxa_desconto_input.blockSignals(False)

    def atualizar_preco_antigo(self):
        produto_id = self.produto_combo.currentData()
        if produto_id and (produto := self.db.obter_produto(produto_id)):
            self.preco_antigo_input.setValue(produto['preco_venda'])
            self.calcular_preco_promocional()
        else:
            self.preco_antigo_input.setValue(0)
            self.preco_promocional_input.setValue(0)
    
    def carregar_produtos_recomendados(self):
        self.tabela_recomendados.setRowCount(0)
        hoje = datetime.now().date()
        
        produtos_estoque_baixo = self.db.verificar_produtos_estoque_baixo()
        produtos_vencendo = self.db.verificar_produtos_vencendo(dias=30)
        
        # Adiciona produtos de estoque baixo
        for produto in produtos_estoque_baixo:
            row = self.tabela_recomendados.rowCount()
            self.tabela_recomendados.insertRow(row)
            self.tabela_recomendados.setItem(row, 0, QTableWidgetItem(produto['nome']))
            self.tabela_recomendados.setItem(row, 1, QTableWidgetItem("Estoque Baixo"))
            self.tabela_recomendados.setItem(row, 2, QTableWidgetItem(f"{produto['quantidade']} / {produto['estoque_minimo']}"))
            self.tabela_recomendados.setItem(row, 3, QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}"))
            self.tabela_recomendados.item(row, 0).setData(Qt.UserRole, produto['id']) # Armazena o ID

        # Adiciona produtos perto do vencimento (evitando duplicatas)
        ids_ja_na_tabela = {self.tabela_recomendados.item(r, 0).data(Qt.UserRole) for r in range(self.tabela_recomendados.rowCount())}
        for produto in produtos_vencendo:
            if produto['id'] in ids_ja_na_tabela: continue
            row = self.tabela_recomendados.rowCount()
            self.tabela_recomendados.insertRow(row)
            dias_restantes = (datetime.strptime(produto['data_validade'], '%Y-%m-%d').date() - hoje).days
            self.tabela_recomendados.setItem(row, 0, QTableWidgetItem(produto['nome']))
            self.tabela_recomendados.setItem(row, 1, QTableWidgetItem("Vencimento Próximo"))
            self.tabela_recomendados.setItem(row, 2, QTableWidgetItem(f"{dias_restantes} dias"))
            self.tabela_recomendados.setItem(row, 3, QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}"))
            self.tabela_recomendados.item(row, 0).setData(Qt.UserRole, produto['id'])

    def carregar_todos_os_produtos(self):
        self.combo_todos_produtos.blockSignals(True)
        self.combo_todos_produtos.clear()
        self.combo_todos_produtos.addItem("Selecione um produto...", None)
        produtos = self.db.listar_produtos()
        for produto in produtos:
            self.combo_todos_produtos.addItem(produto['nome'], produto['id'])
        self.combo_todos_produtos.blockSignals(False)

    def selecionar_produto_pela_tabela(self, row, column):
        item = self.tabela_recomendados.item(row, 0)
        produto_id = item.data(Qt.UserRole)
        self.selecionar_produto(produto_id)

    def selecionar_produto_pelo_combo(self, index):
        produto_id = self.combo_todos_produtos.itemData(index)
        self.selecionar_produto(produto_id)
        
    def selecionar_produto(self, produto_id):
        if not produto_id:
            self.produto_selecionado_id = None
            self.produto_selecionado_label.setText("Nenhum produto selecionado")
            self.preco_antigo_input.setValue(0)
            return

        produto = self.db.obter_produto(produto_id)
        if produto:
            self.produto_selecionado_id = produto['id']
            self.produto_selecionado_label.setText(produto['nome'])
            self.preco_antigo_input.setValue(produto['preco_venda'])
            self.calcular_preco_promocional() # Recalcula o preço com o desconto padrão

    def carregar_dados_promocao(self):
        if not self.promocao: return
        self.tabs_selecao_produto.setEnabled(False) # Não permite trocar o produto de uma promoção existente
        self.selecionar_produto(self.promocao['produto_id']) # Popula os campos do produto
        
        self.preco_promocional_input.setValue(self.promocao['preco_promocional'])
        self.calcular_taxa_desconto() # Calcula a taxa com base nos preços carregados
        self.data_inicio_input.setDate(QDate.fromString(self.promocao['data_inicio'], "yyyy-MM-dd"))
        self.data_fim_input.setDate(QDate.fromString(self.promocao['data_fim'], "yyyy-MM-dd"))
        self.descricao_input.setText(self.promocao['descricao'])
        
    def salvar_promocao(self):
        """
        Coleta os dados, valida e salva a promoção no banco de dados.
        Esta é a implementação completa.
        """
        # 1. Validação inicial
        if not self.produto_selecionado_id:
            QMessageBox.warning(self, "Ação Necessária", "Por favor, selecione um produto para a promoção.")
            return
        
        # 2. Coletar dados dos widgets
        preco_antigo = self.preco_antigo_input.value()
        preco_promocional = self.preco_promocional_input.value()
        data_inicio = self.data_inicio_input.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim_input.date().toString("yyyy-MM-dd")
        descricao = self.descricao_input.text().strip()

        # 3. Validação dos dados
        if not (0 < preco_promocional < preco_antigo):
            QMessageBox.warning(self, "Dados Inválidos", "O preço promocional deve ser maior que zero e menor que o preço original.")
            return
        
        if self.data_inicio_input.date() > self.data_fim_input.date():
            QMessageBox.warning(self, "Dados Inválidos", "A data de fim da promoção deve ser igual ou posterior à data de início.")
            return

        # 4. Lógica de salvar (Adicionar ou Atualizar)
        try:
            if self.promocao_id:
                sucesso = self.db.atualizar_promocao(
                    self.promocao_id, self.produto_selecionado_id, preco_antigo, 
                    preco_promocional, data_inicio, data_fim, descricao
                )
                mensagem = "Promoção atualizada com sucesso!"
            else:
                sucesso = self.db.adicionar_promocao(
                    self.produto_selecionado_id, preco_antigo, preco_promocional, 
                    data_inicio, data_fim, descricao
                )
                mensagem = "Promoção cadastrada com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro no Banco de Dados", "Não foi possível salvar a promoção.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro Inesperado", f"Ocorreu um erro ao salvar a promoção:\n{str(e)}")