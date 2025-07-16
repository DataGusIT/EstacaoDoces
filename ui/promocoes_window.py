from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QDoubleSpinBox,
                           QDialog, QFrame, QTabWidget, QRadioButton, QButtonGroup, QFileDialog, QSizePolicy, QGroupBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime, timedelta
import csv
import os
from ui.icon_manager import IconManager


class PromocoesWindow(QWidget):
    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.initUI()
        self.carregar_dados()

    def set_theme(self, theme_colors):
        self.theme_colors = theme_colors
        self.update_button_icons()
        self.carregar_dados()

    def update_button_icons(self):
        icon_color = self.theme_colors.get('text_color', '#000')

        self.search_button.setIcon(IconManager.get_icon('search', icon_color))
        self.exportar_button.setIcon(IconManager.get_icon('export', icon_color))
        self.importar_button.setIcon(IconManager.get_icon('import', icon_color))
        self.produtos_especiais_button.setIcon(IconManager.get_icon('tags', icon_color))

        self.add_button.setIcon(IconManager.get_icon('add', 'white'))

    def initUI(self):
        layout = QVBoxLayout(self)
        titulo = QLabel("Gerenciamento de Promoções")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)

        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar promoção pelo nome do produto...")
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

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        botoes_acao = []

        self.add_button = QPushButton()
        self.add_button.setText(" Adicionar Promoção")
        self.add_button.setObjectName("primaryActionButton")
        self.add_button.clicked.connect(self.abrir_formulario_promocao)
        botoes_acao.append(self.add_button)

        self.produtos_especiais_button = QPushButton()
        self.produtos_especiais_button.setText(" Promoções Especiais")
        self.produtos_especiais_button.clicked.connect(self.abrir_promocoes_especiais)
        botoes_acao.append(self.produtos_especiais_button)
        
        self.exportar_button = QPushButton()
        self.exportar_button.setText(" Exportar CSV")
        self.exportar_button.clicked.connect(self.exportar_csv)
        botoes_acao.append(self.exportar_button)
        
        self.importar_button = QPushButton()
        self.importar_button.setText(" Importar CSV")
        self.importar_button.clicked.connect(self.importar_csv)
        botoes_acao.append(self.importar_button)

        for btn in botoes_acao:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            action_layout.addWidget(btn)
            
        layout.addLayout(action_layout)
        self.update_button_icons()
    
    def carregar_dados(self):
        promocoes = self.db.listar_promocoes()
        self.atualizar_tabela(promocoes)
    
    def pesquisar_promocoes(self):
        termo = self.search_input.text()
        promocoes = self.db.listar_promocoes(filtro=termo) if termo else self.db.listar_promocoes()
        self.atualizar_tabela(promocoes)
    
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
        dialog = FormularioPromocao(self.db, promocao_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def abrir_promocoes_especiais(self):
        dialog = PromocoesEspeciaisDialog(self.db)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_promocao(self, promocao_id):
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir esta promoção?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_promocao(promocao_id):
                QMessageBox.information(self, "Sucesso", "Promoção excluída com sucesso!")
                self.carregar_dados()
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
        try:
            arquivo, _ = QFileDialog.getOpenFileName(
                self, "Importar Promoções", "", "Arquivos CSV (*.csv)"
            )
            if not arquivo: return
            
            confirmacao = QMessageBox.question(
                self, "Confirmar Importação", "Esta operação irá adicionar novas promoções.\nDeseja continuar?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirmacao != QMessageBox.Yes: return
            
            promocoes_importadas, erros = 0, []
            
            with open(arquivo, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for linha_num, row in enumerate(reader, start=2):
                    try:
                        if not all(k in row for k in ['Produto', 'Preço Antigo', 'Preço Promocional', 'Data Início', 'Data Fim']):
                            erros.append(f"Linha {linha_num}: Campos obrigatórios faltando")
                            continue
                        
                        produto_result = self.db.buscar_produto_por_nome_exato(row['Produto'].strip())
                        if not produto_result:
                            erros.append(f"Linha {linha_num}: Produto '{row['Produto']}' não encontrado")
                            continue
                        
                        produto = {'id': produto_result[0], 'nome': produto_result[1]}
                        
                        try:
                            preco_antigo = float(row['Preço Antigo'].replace(',', '.'))
                            preco_promocional = float(row['Preço Promocional'].replace(',', '.'))
                        except ValueError:
                            erros.append(f"Linha {linha_num}: Preços inválidos")
                            continue
                        
                        if not (0 < preco_promocional < preco_antigo):
                            erros.append(f"Linha {linha_num}: Preços inválidos (promocional deve ser menor que antigo e ambos > 0)")
                            continue
                        
                        data_inicio, data_fim = row['Data Início'].strip(), row['Data Fim'].strip()
                        valid_date = False
                        for formato in ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']:
                            try:
                                datetime.strptime(data_inicio, formato)
                                datetime.strptime(data_fim, formato)
                                if formato != '%Y-%m-%d':
                                    data_inicio = datetime.strptime(data_inicio, formato).strftime('%Y-%m-%d')
                                    data_fim = datetime.strptime(data_fim, formato).strftime('%Y-%m-%d')
                                valid_date = True
                                break
                            except ValueError: continue
                        if not valid_date:
                            erros.append(f"Linha {linha_num}: Formato de data inválido")
                            continue
                        
                        if self.db.adicionar_promocao(
                            produto['id'], preco_antigo, preco_promocional, data_inicio, data_fim, row.get('Descrição', '').strip()
                        ): promocoes_importadas += 1
                        else: erros.append(f"Linha {linha_num}: Erro ao salvar no banco de dados")
                    
                    except Exception as e:
                        erros.append(f"Linha {linha_num}: Erro inesperado - {str(e)}")
            
            self.carregar_dados()
            
            mensagem = f"Importação concluída!\nPromoções importadas: {promocoes_importadas}\n"
            if erros:
                mensagem += f"Erros: {len(erros)}\n\nPrimeiros 10 erros:\n" + "\n".join(erros[:10])
                if len(erros) > 10: mensagem += f"\n... e mais {len(erros) - 10} erros."
                QMessageBox.warning(self, "Importação com Erros", mensagem)
            else:
                QMessageBox.information(self, "Sucesso", mensagem)
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar CSV:\n{str(e)}")


class PromocoesEspeciaisDialog(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_produtos_especiais()
    
    def initUI(self):
        self.setWindowTitle("Promoções Especiais")
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        layout = QVBoxLayout(self)
        
        self.tabs = QTabWidget()
        self.tab_estoque_baixo = QWidget()
        self.tab_vencimento = QWidget()
        
        self.setup_tab_estoque_baixo()
        self.setup_tab_vencimento()
        
        self.tabs.addTab(self.tab_estoque_baixo, "Estoque Baixo")
        self.tabs.addTab(self.tab_vencimento, "Próximos ao Vencimento")
        layout.addWidget(self.tabs)
        
        desconto_group = QFrame()
        desconto_layout = QHBoxLayout(desconto_group)
        desconto_label = QLabel("Taxa de Desconto Padrão:")
        self.taxa_desconto_input = QDoubleSpinBox()
        self.taxa_desconto_input.setRange(0, 100)
        self.taxa_desconto_input.setSuffix("%")
        self.taxa_desconto_input.setValue(10)
        self.taxa_desconto_input.valueChanged.connect(self.atualizar_precos_promocionais)
        desconto_layout.addWidget(desconto_label)
        desconto_layout.addWidget(self.taxa_desconto_input)
        desconto_layout.addStretch()
        layout.addWidget(desconto_group)
        
        buttons_layout = QHBoxLayout()
        self.aplicar_button = QPushButton(IconManager.get_icon('confirm', 'white'), " Aplicar Promoções")
        self.aplicar_button.setObjectName("primaryActionButton")
        self.aplicar_button.clicked.connect(self.aplicar_promocoes)
        
        self.cancelar_button = QPushButton(IconManager.get_icon('cancel'), " Cancelar")
        self.cancelar_button.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.aplicar_button)
        buttons_layout.addWidget(self.cancelar_button)
        layout.addLayout(buttons_layout)
        
    # ... O restante da classe PromocoesEspeciaisDialog permanece o mesmo ...
    def setup_tab_estoque_baixo(self):
        layout = QVBoxLayout(self.tab_estoque_baixo)
        self.tabela_estoque_baixo = QTableWidget()
        self.tabela_estoque_baixo.setColumnCount(8)
        self.tabela_estoque_baixo.setHorizontalHeaderLabels([
            "Selecionar", "ID", "Produto", "Quantidade", "Estoque Mínimo", 
            "Preço Atual", "Taxa de Desconto", "Preço Promocional"
        ])
        self.tabela_estoque_baixo.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela_estoque_baixo.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_estoque_baixo)
    
    def setup_tab_vencimento(self):
        layout = QVBoxLayout(self.tab_vencimento)
        periodo_layout = QHBoxLayout()
        periodo_label = QLabel("Considerar produtos que vencem em:")
        self.periodo_combo = QComboBox()
        self.periodo_combo.addItem("7 dias", 7)
        self.periodo_combo.addItem("15 dias", 15)
        self.periodo_combo.addItem("30 dias", 30)
        self.periodo_combo.addItem("60 dias", 60)
        self.periodo_combo.setCurrentIndex(2)
        self.periodo_combo.currentIndexChanged.connect(self.carregar_produtos_vencimento)
        periodo_layout.addWidget(periodo_label)
        periodo_layout.addWidget(self.periodo_combo)
        periodo_layout.addStretch()
        layout.addLayout(periodo_layout)
        self.tabela_vencimento = QTableWidget()
        self.tabela_vencimento.setColumnCount(9)
        self.tabela_vencimento.setHorizontalHeaderLabels([
            "Selecionar", "ID", "Produto", "Data Validade", "Dias Restantes", "Quantidade",
            "Preço Atual", "Taxa de Desconto", "Preço Promocional"
        ])
        self.tabela_vencimento.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tabela_vencimento.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.tabela_vencimento)
    
    def carregar_produtos_especiais(self):
        self.carregar_produtos_estoque_baixo()
        self.carregar_produtos_vencimento()
    
    def carregar_produtos_estoque_baixo(self):
        produtos = self.db.verificar_produtos_estoque_baixo()
        self.tabela_estoque_baixo.setRowCount(0)
        for row, produto in enumerate(produtos):
            self.tabela_estoque_baixo.insertRow(row)
            checkbox = QWidget()
            checkbox_layout = QHBoxLayout(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            check = QRadioButton()
            checkbox_layout.addWidget(check)
            preco_atual = produto['preco_venda']
            taxa_desconto = self.taxa_desconto_input.value()
            preco_promocional = preco_atual * (1 - taxa_desconto / 100)
            self.tabela_estoque_baixo.setCellWidget(row, 0, checkbox)
            self.tabela_estoque_baixo.setItem(row, 1, QTableWidgetItem(str(produto['id'])))
            self.tabela_estoque_baixo.setItem(row, 2, QTableWidgetItem(produto['nome']))
            self.tabela_estoque_baixo.setItem(row, 3, QTableWidgetItem(str(produto['quantidade'])))
            self.tabela_estoque_baixo.setItem(row, 4, QTableWidgetItem(str(produto['estoque_minimo'])))
            self.tabela_estoque_baixo.setItem(row, 5, QTableWidgetItem(f"R$ {preco_atual:.2f}"))
            taxa_desconto_widget = QWidget()
            taxa_layout = QHBoxLayout(taxa_desconto_widget)
            taxa_layout.setContentsMargins(0, 0, 0, 0)
            taxa_spin = QDoubleSpinBox()
            taxa_spin.setRange(0, 100)
            taxa_spin.setSuffix("%")
            taxa_spin.setValue(taxa_desconto)
            taxa_spin.valueChanged.connect(lambda value, r=row: self.atualizar_preco_promocional_item(r, value))
            taxa_layout.addWidget(taxa_spin)
            self.tabela_estoque_baixo.setCellWidget(row, 6, taxa_desconto_widget)
            self.tabela_estoque_baixo.setItem(row, 7, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
    
    def carregar_produtos_vencimento(self):
        dias = self.periodo_combo.currentData()
        produtos = self.db.verificar_produtos_vencendo(dias)
        self.tabela_vencimento.setRowCount(0)
        hoje = datetime.now().date()
        for row, produto in enumerate(produtos):
            self.tabela_vencimento.insertRow(row)
            checkbox = QWidget()
            checkbox_layout = QHBoxLayout(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            check = QRadioButton()
            checkbox_layout.addWidget(check)
            data_validade = datetime.strptime(produto['data_validade'], '%Y-%m-%d').date()
            dias_restantes = (data_validade - hoje).days
            taxa_desconto_sugerida = min(50, int(50 * (1 - dias_restantes / dias))) if dias_restantes > 0 else 50
            preco_atual = produto['preco_venda']
            preco_promocional = preco_atual * (1 - taxa_desconto_sugerida / 100)
            self.tabela_vencimento.setCellWidget(row, 0, checkbox)
            self.tabela_vencimento.setItem(row, 1, QTableWidgetItem(str(produto['id'])))
            self.tabela_vencimento.setItem(row, 2, QTableWidgetItem(produto['nome']))
            self.tabela_vencimento.setItem(row, 3, QTableWidgetItem(produto['data_validade']))
            self.tabela_vencimento.setItem(row, 4, QTableWidgetItem(str(dias_restantes)))
            self.tabela_vencimento.setItem(row, 5, QTableWidgetItem(str(produto['quantidade'])))
            self.tabela_vencimento.setItem(row, 6, QTableWidgetItem(f"R$ {preco_atual:.2f}"))
            taxa_desconto_widget = QWidget()
            taxa_layout = QHBoxLayout(taxa_desconto_widget)
            taxa_layout.setContentsMargins(0, 0, 0, 0)
            taxa_spin = QDoubleSpinBox()
            taxa_spin.setRange(0, 100)
            taxa_spin.setSuffix("%")
            taxa_spin.setValue(taxa_desconto_sugerida)
            taxa_spin.valueChanged.connect(lambda value, r=row: self.atualizar_preco_promocional_vencimento(r, value))
            taxa_layout.addWidget(taxa_spin)
            self.tabela_vencimento.setCellWidget(row, 7, taxa_desconto_widget)
            self.tabela_vencimento.setItem(row, 8, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
    
    def atualizar_precos_promocionais(self):
        for row in range(self.tabela_estoque_baixo.rowCount()):
            taxa_widget = self.tabela_estoque_baixo.cellWidget(row, 6)
            if taxa_widget and (taxa_spin := taxa_widget.findChild(QDoubleSpinBox)):
                taxa_spin.setValue(self.taxa_desconto_input.value())
    
    def atualizar_preco_promocional_item(self, row, taxa_desconto):
        preco_texto = self.tabela_estoque_baixo.item(row, 5).text().replace('R$', '').strip()
        try:
            preco_atual = float(preco_texto)
            preco_promocional = preco_atual * (1 - taxa_desconto / 100)
            self.tabela_estoque_baixo.setItem(row, 7, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
        except (ValueError, AttributeError): pass
    
    def atualizar_preco_promocional_vencimento(self, row, taxa_desconto):
        preco_texto = self.tabela_vencimento.item(row, 6).text().replace('R$', '').strip()
        try:
            preco_atual = float(preco_texto)
            preco_promocional = preco_atual * (1 - taxa_desconto / 100)
            self.tabela_vencimento.setItem(row, 8, QTableWidgetItem(f"R$ {preco_promocional:.2f}"))
        except (ValueError, AttributeError): pass
    
    def aplicar_promocoes(self):
        produtos_selecionados = []
        tabela_ativa = self.tabela_estoque_baixo if self.tabs.currentIndex() == 0 else self.tabela_vencimento
        
        for row in range(tabela_ativa.rowCount()):
            if (cb_widget := tabela_ativa.cellWidget(row, 0)) and (checkbox := cb_widget.findChild(QRadioButton)) and checkbox.isChecked():
                produto_id = int(tabela_ativa.item(row, 1).text())
                preco_antigo_str = tabela_ativa.item(row, 5).text() if self.tabs.currentIndex() == 0 else tabela_ativa.item(row, 6).text()
                preco_antigo = float(preco_antigo_str.replace('R$', '').strip())
                taxa_widget = tabela_ativa.cellWidget(row, 6) if self.tabs.currentIndex() == 0 else tabela_ativa.cellWidget(row, 7)
                taxa_desconto = taxa_widget.findChild(QDoubleSpinBox).value()
                preco_promo_str = tabela_ativa.item(row, 7).text() if self.tabs.currentIndex() == 0 else tabela_ativa.item(row, 8).text()
                preco_promocional = float(preco_promo_str.replace('R$', '').strip())
                
                if self.tabs.currentIndex() == 0:
                    descricao = f"Promoção por estoque baixo - {taxa_desconto:.1f}% de desconto"
                else:
                    data_validade = tabela_ativa.item(row, 3).text()
                    descricao = f"Promoção por vencimento em {data_validade} - {taxa_desconto:.1f}% de desconto"

                produtos_selecionados.append({
                    'produto_id': produto_id, 'preco_antigo': preco_antigo,
                    'preco_promocional': preco_promocional, 'descricao': descricao
                })
        
        if not produtos_selecionados:
            QMessageBox.warning(self, "Aviso", "Nenhum produto selecionado!")
            return
        
        confirmacao = QMessageBox.question(self, "Confirmar Promoções", f"Deseja aplicar promoções para {len(produtos_selecionados)} produtos?", QMessageBox.Yes | QMessageBox.No)
        if confirmacao == QMessageBox.Yes:
            data_inicio = datetime.now().strftime('%Y-%m-%d')
            data_fim = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            sucesso = all(self.db.adicionar_promocao(p['produto_id'], p['preco_antigo'], p['preco_promocional'], data_inicio, data_fim, p['descricao']) for p in produtos_selecionados)
            if sucesso:
                QMessageBox.information(self, "Sucesso", "Promoções aplicadas com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Ocorreu um erro ao aplicar algumas promoções.")


class FormularioPromocao(QDialog):
    def __init__(self, db, promocao_id=None):
        super().__init__()
        self.db = db
        self.promocao_id = promocao_id
        self.promocao = None
        
        if promocao_id:
            self.promocao = self.db.obter_promocao(promocao_id)
            if not self.promocao:
                QMessageBox.warning(self, "Erro", "Promoção não encontrada!")
                self.reject()
        
        self.initUI()
        
        if self.promocao:
            self.carregar_dados_promocao()
    
    def initUI(self):
        self.setWindowTitle("Cadastro de Promoção")
        self.setFixedWidth(500)
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Detalhes da Promoção")
        form_layout = QFormLayout(form_group)
        
        self.produto_combo = QComboBox()
        self.carregar_produtos()
        
        self.preco_antigo_input = QDoubleSpinBox()
        self.preco_antigo_input.setReadOnly(True) # Preço antigo não deve ser editável
        self.preco_antigo_input.setRange(0, 99999.99)
        self.preco_antigo_input.setPrefix("R$ ")
        self.preco_antigo_input.setDecimals(2)
        
        self.taxa_desconto_input = QDoubleSpinBox()
        self.taxa_desconto_input.setRange(0, 100)
        self.taxa_desconto_input.setSuffix("%")
        self.taxa_desconto_input.setValue(10)
        self.taxa_desconto_input.valueChanged.connect(self.calcular_preco_promocional)
        
        self.preco_promocional_input = QDoubleSpinBox()
        self.preco_promocional_input.setRange(0, 99999.99)
        self.preco_promocional_input.setPrefix("R$ ")
        self.preco_promocional_input.setDecimals(2)
        self.preco_promocional_input.valueChanged.connect(self.calcular_taxa_desconto)
        
        self.data_inicio_input = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.data_inicio_input.setDisplayFormat("dd/MM/yyyy")
        
        self.data_fim_input = QDateEdit(calendarPopup=True, date=QDate.currentDate().addDays(30))
        self.data_fim_input.setDisplayFormat("dd/MM/yyyy")
        
        self.descricao_input = QLineEdit()
        
        form_layout.addRow("Produto:", self.produto_combo)
        form_layout.addRow("Preço Original:", self.preco_antigo_input)
        form_layout.addRow("Taxa de Desconto:", self.taxa_desconto_input)
        form_layout.addRow("Preço Promocional:", self.preco_promocional_input)
        form_layout.addRow("Data de Início:", self.data_inicio_input)
        form_layout.addRow("Data de Fim:", self.data_fim_input)
        form_layout.addRow("Descrição:", self.descricao_input)
        layout.addWidget(form_group)

        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(IconManager.get_icon('save', 'white'), " Salvar")
        self.salvar_btn.setObjectName("primaryActionButton")
        self.salvar_btn.clicked.connect(self.salvar_promocao)
        
        self.cancelar_btn = QPushButton(IconManager.get_icon('cancel'), " Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        layout.addLayout(button_layout)
        
        self.produto_combo.currentIndexChanged.connect(self.atualizar_preco_antigo)

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
    
    def salvar_promocao(self):
        produto_id = self.produto_combo.currentData()
        preco_antigo = self.preco_antigo_input.value()
        preco_promocional = self.preco_promocional_input.value()
        data_inicio = self.data_inicio_input.date().toString("yyyy-MM-dd")
        data_fim = self.data_fim_input.date().toString("yyyy-MM-dd")
        descricao = self.descricao_input.text()
        
        if not produto_id:
            QMessageBox.warning(self, "Erro", "Selecione um produto!")
            return
        if not (0 < preco_promocional < preco_antigo):
            QMessageBox.warning(self, "Erro", "Preço promocional deve ser menor que o preço antigo e ambos maiores que zero!")
            return
        if self.data_inicio_input.date() > self.data_fim_input.date():
            QMessageBox.warning(self, "Erro", "A data de início deve ser anterior à data de fim!")
            return
        
        if self.promocao_id:
            resultado = self.db.atualizar_promocao(self.promocao_id, produto_id, preco_antigo, preco_promocional, data_inicio, data_fim, descricao)
            mensagem = "Promoção atualizada com sucesso!" if resultado else "Erro ao atualizar promoção!"
        else:
            resultado = self.db.adicionar_promocao(produto_id, preco_antigo, preco_promocional, data_inicio, data_fim, descricao)
            mensagem = "Promoção adicionada com sucesso!" if resultado else "Erro ao adicionar promoção!"
        
        if resultado:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()
        else:
            QMessageBox.warning(self, "Erro", mensagem)

    def carregar_dados_promocao(self):
        if not self.promocao: return
        
        if (index := self.produto_combo.findData(self.promocao['produto_id'])) >= 0:
            self.produto_combo.setCurrentIndex(index)
        
        self.preco_antigo_input.setValue(self.promocao['preco_antigo'])
        self.preco_promocional_input.setValue(self.promocao['preco_promocional'])
        self.calcular_taxa_desconto()
        
        self.data_inicio_input.setDate(QDate.fromString(self.promocao['data_inicio'], "yyyy-MM-dd"))
        self.data_fim_input.setDate(QDate.fromString(self.promocao['data_fim'], "yyyy-MM-dd"))
        self.descricao_input.setText(self.promocao['descricao'])

    def carregar_produtos(self):
        self.produto_combo.clear()
        self.produto_combo.addItem("Selecione um produto", None)
        
        def add_separator_and_title(title):
            self.produto_combo.insertSeparator(self.produto_combo.count())
            self.produto_combo.addItem(title, None)
            
        produtos_estoque_baixo = self.db.verificar_produtos_estoque_baixo()
        if produtos_estoque_baixo:
            add_separator_and_title("--- PRODUTOS COM ESTOQUE BAIXO ---")
            for p in produtos_estoque_baixo: self.produto_combo.addItem(f"{p['nome']} (Estoque: {p['quantidade']})", p['id'])
        
        produtos_vencendo = self.db.verificar_produtos_vencendo(30)
        if produtos_vencendo:
            add_separator_and_title("--- PRODUTOS PRÓXIMOS AO VENCIMENTO ---")
            for p in produtos_vencendo: self.produto_combo.addItem(f"{p['nome']} (Validade: {p['data_validade']})", p['id'])
        
        add_separator_and_title("--- TODOS OS PRODUTOS ---")
        produtos = self.db.listar_produtos()
        ids_ja_listados = {p['id'] for p in produtos_estoque_baixo} | {p['id'] for p in produtos_vencendo}
        for p in produtos:
            if p['id'] not in ids_ja_listados:
                self.produto_combo.addItem(p['nome'], p['id'])