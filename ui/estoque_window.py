from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QSpinBox,
                           QDoubleSpinBox, QDialog, QFrame, QToolButton, QGroupBox,
                           QFileDialog, QCheckBox)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QIcon, QColor, QBrush
import os
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

class EstoqueWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_dados()
        
    
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título da página
        titulo = QLabel("Controle de Estoque")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Área de pesquisa e filtros
        search_group = QGroupBox("Pesquisa e Filtros")
        search_layout = QVBoxLayout(search_group)
        
        # Linha de pesquisa
        search_input_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar produto por nome, descrição ou código de barras...")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.pesquisar_produtos)
        search_input_layout.addWidget(self.search_input)
        search_input_layout.addWidget(self.search_button)
        search_layout.addLayout(search_input_layout)
        
        # Linha de filtros
        filter_layout = QHBoxLayout()
        
        # Filtro de estoque
        self.estoque_combo = QComboBox()
        self.estoque_combo.addItem("Todos os níveis", "todos")
        self.estoque_combo.addItem("Estoque Baixo", "baixo")
        self.estoque_combo.addItem("Estoque Médio", "medio")
        self.estoque_combo.addItem("Estoque Alto", "alto")
        filter_layout.addWidget(QLabel("Nível de Estoque:"))
        filter_layout.addWidget(self.estoque_combo)
        
        # Filtro de vencimento
        self.vencimento_combo = QComboBox()
        self.vencimento_combo.addItem("Todos", "todos")
        self.vencimento_combo.addItem("Vence em 30 dias", "30")
        self.vencimento_combo.addItem("Vence em 15 dias", "15")
        self.vencimento_combo.addItem("Vencidos", "vencidos")
        filter_layout.addWidget(QLabel("Vencimento:"))
        filter_layout.addWidget(self.vencimento_combo)
        
        # Botão de aplicar filtros
        self.aplicar_filtro_btn = QPushButton("Aplicar Filtros")
        self.aplicar_filtro_btn.clicked.connect(self.aplicar_filtros)
        filter_layout.addWidget(self.aplicar_filtro_btn)
        
        # Botão para limpar filtros
        self.limpar_filtro_btn = QPushButton("Limpar Filtros")
        self.limpar_filtro_btn.clicked.connect(self.limpar_filtros)
        filter_layout.addWidget(self.limpar_filtro_btn)
        
        search_layout.addLayout(filter_layout)
        layout.addWidget(search_group)
        
        # Legenda dos ícones
        legenda_layout = QHBoxLayout()
        
        # Ícone de estoque baixo
        estoque_baixo_label = QLabel("Estoque Baixo")
        estoque_baixo_label.setStyleSheet("color: red;")
        legenda_layout.addWidget(estoque_baixo_label)
        
        # Ícone de vencimento em 30 dias
        vencimento_30_label = QLabel("Vence em 30 dias")
        vencimento_30_label.setStyleSheet("color: orange;")
        legenda_layout.addWidget(vencimento_30_label)
        
        # Ícone de vencimento em 15 dias
        vencimento_15_label = QLabel("Vence em 15 dias")
        vencimento_15_label.setStyleSheet("color: red;")
        legenda_layout.addWidget(vencimento_15_label)
        
        legenda_layout.addStretch()
        layout.addLayout(legenda_layout)
        
        # Tabela de produtos
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(12)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Código de Barras", "Nome", "Estoque Detalhado", "Estoque Mín.", 
            "Preço Compra", "Margem %", "Preço Venda", "Validade", 
            "Localização", "Fornecedor", "Ações"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Produto")
        self.add_button.clicked.connect(self.abrir_formulario_produto)
        
        self.relatorio_btn = QPushButton("Relatório de Vencimentos")
        self.relatorio_btn.clicked.connect(self.relatorio_vencimentos)
        
        self.relatorio_estoque_btn = QPushButton("Relatório de Estoque Baixo")
        self.relatorio_estoque_btn.clicked.connect(self.relatorio_estoque_baixo)
        
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.relatorio_btn)
        action_layout.addWidget(self.relatorio_estoque_btn)
        layout.addLayout(action_layout)
    
    def carregar_dados(self):
        """Carrega os produtos do banco de dados para a tabela."""
        produtos = self.db.listar_produtos_com_fracionamento()  # Usando novo método
        self.atualizar_tabela(produtos)
    
    def pesquisar_produtos(self):
        """Pesquisa produtos pelo termo digitado."""
        termo = self.search_input.text()
        if termo:
            produtos = self.db.listar_produtos_com_fracionamento(filtro=termo)  # Usando novo método
        else:
            produtos = self.db.listar_produtos_com_fracionamento()  # Usando novo método
        
        self.atualizar_tabela(produtos)
    
    def aplicar_filtros(self):
        """Aplica os filtros selecionados."""
        filtro_estoque = self.estoque_combo.currentData()
        filtro_vencimento = self.vencimento_combo.currentData()
        
        produtos = self.db.filtrar_produtos(filtro_estoque, filtro_vencimento)
        self.atualizar_tabela(produtos)
    
    def limpar_filtros(self):
        """Limpa todos os filtros aplicados."""
        self.estoque_combo.setCurrentIndex(0)
        self.vencimento_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.carregar_dados()
    
    def atualizar_tabela(self, produtos):
        """Atualiza a tabela com os produtos fornecidos."""
        self.tabela.setRowCount(0)
        
        hoje = datetime.now().date()
        
        for row, produto in enumerate(produtos):
            self.tabela.insertRow(row)
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(produto['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(produto['codigo_barras'] or ""))
            
            # Nome do produto - incluir indicador se é fracionado
            nome_produto = produto['nome']
            if produto['fracionado']:
                nome_produto += f" (Frac. - {produto['unidade_medida']})"
            nome_item = QTableWidgetItem(nome_produto)
            self.tabela.setItem(row, 2, nome_item)
            
            # Quantidade - mostrar detalhes se for fracionado
            if produto['fracionado']:
                estoque_total = produto['estoque_total_calculado']
                quantidade_display = f"{produto['quantidade']} emb. + {produto['estoque_fracionado']} {produto['unidade_medida']} (Total: {estoque_total})"
                tooltip_text = f"Embalagens: {produto['quantidade']}\nFracionado: {produto['estoque_fracionado']} {produto['unidade_medida']}\nTotal em unidades: {estoque_total}"
            else:
                quantidade_display = str(produto['quantidade'])
                tooltip_text = f"Quantidade: {produto['quantidade']}"
            
            quantidade_item = QTableWidgetItem(quantidade_display)
            quantidade_item.setToolTip(tooltip_text)
            
            estoque_minimo = produto['estoque_minimo'] or 0
            
            # Verificar se está abaixo do estoque mínimo (usando estoque total calculado)
            estoque_atual = produto['estoque_total_calculado'] if produto['fracionado'] else produto['quantidade']
            if estoque_atual <= estoque_minimo:
                quantidade_item.setForeground(QBrush(QColor('red')))
                quantidade_item.setToolTip(quantidade_item.toolTip() + "\nESTOQUE ABAIXO DO MÍNIMO!")
            
            self.tabela.setItem(row, 3, quantidade_item)
            self.tabela.setItem(row, 4, QTableWidgetItem(str(estoque_minimo)))
            self.tabela.setItem(row, 5, QTableWidgetItem(f"R$ {produto['preco_compra']:.2f}"))
            
            # Margem de lucro
            margem = produto['margem_lucro'] or 0
            self.tabela.setItem(row, 6, QTableWidgetItem(f"{margem:.2f}%"))
            
            # Preço de venda - mostrar preço da embalagem e fração se aplicável
            if produto['fracionado'] and produto['preco_unitario_fracao']:
                preco_display = f"Emb: R$ {produto['preco_venda']:.2f} | Un: R$ {produto['preco_unitario_fracao']:.2f}"
            else:
                preco_display = f"R$ {produto['preco_venda']:.2f}"
            self.tabela.setItem(row, 7, QTableWidgetItem(preco_display))
            
            # Data de validade (mantém igual)
            validade_item = QTableWidgetItem(str(produto['data_validade'] or ""))
            
            # Verificar vencimento
            if produto['data_validade']:
                try:
                    data_validade = datetime.strptime(produto['data_validade'], "%Y-%m-%d").date()
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
                except:
                    pass
            
            self.tabela.setItem(row, 8, validade_item)
            self.tabela.setItem(row, 9, QTableWidgetItem(produto['localizacao'] or ""))
            
            fornecedor_nome = produto['fornecedor_nome'] if produto['fornecedor_nome'] else "N/A"
            self.tabela.setItem(row, 10, QTableWidgetItem(fornecedor_nome))
            
            # Botões de ação - adicionar botão para quebrar embalagem se for fracionado
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            
            editar_btn = QPushButton("Editar")
            editar_btn.clicked.connect(lambda _, p_id=produto['id']: self.abrir_formulario_produto(p_id))
            
            excluir_btn = QPushButton("Excluir")
            excluir_btn.clicked.connect(lambda _, p_id=produto['id']: self.excluir_produto(p_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            # Botão para quebrar embalagem (apenas se for fracionado e tiver embalagens)
            if produto['fracionado'] and produto['quantidade'] > 0:
                quebrar_btn = QPushButton("Quebrar")
                quebrar_btn.setToolTip("Quebrar embalagem em unidades")
                quebrar_btn.clicked.connect(lambda _, p_id=produto['id']: self.abrir_dialog_quebrar_embalagem(p_id))
                acoes_layout.addWidget(quebrar_btn)
            
            self.tabela.setCellWidget(row, 11, acoes_widget)
    
    def abrir_dialog_quebrar_embalagem(self, produto_id):
        """Abre diálogo para quebrar embalagens em unidades fracionadas."""
        produto_info = self.db.obter_info_estoque_fracionado(produto_id)
        
        if not produto_info or not produto_info['fracionado']:
            QMessageBox.warning(self, "Erro", "Este produto não é fracionado!")
            return
        
        dialog = DialogQuebrarEmbalagem(self.db, produto_info)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()  # Recarregar tabela após quebrar embalagem
    
    def abrir_formulario_produto(self, produto_id=None):
        """Abre o formulário para adicionar ou editar um produto."""
        dialog = FormularioProduto(self.db, produto_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_produto(self, produto_id):
        """Exclui um produto após confirmação."""
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este produto?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_produto(produto_id):
                QMessageBox.information(self, "Sucesso", "Produto excluído com sucesso!")
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir o produto.")
    
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


class FormularioProduto(QDialog):
    def __init__(self, db, produto_id=None):
        super().__init__()
        self.db = db
        self.produto_id = produto_id
        self.produto = None
        
        if produto_id:
            self.produto = self.db.obter_produto(produto_id)
            if not self.produto:
                QMessageBox.warning(self, "Erro", "Produto não encontrado!")
                self.reject()
        
        self.initUI()
        
        if self.produto:
            self.carregar_dados_produto()
    
    def initUI(self):
        # Configurar janela
        self.setWindowTitle("Cadastro de Produto")
        self.setFixedWidth(600)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        # Campos do formulário
        self.codigo_barras_input = QLineEdit()
        self.nome_input = QLineEdit()
        self.descricao_input = QLineEdit()
        
        # Quantidade
        self.quantidade_input = QSpinBox()
        self.quantidade_input.setRange(0, 99999)
        
        # Estoque mínimo
        self.estoque_minimo_input = QSpinBox()
        self.estoque_minimo_input.setRange(0, 99999)
        
        # Preço de compra
        self.preco_compra_input = QDoubleSpinBox()
        self.preco_compra_input.setRange(0, 99999.99)
        self.preco_compra_input.setPrefix("R$ ")
        self.preco_compra_input.setDecimals(2)
        self.preco_compra_input.valueChanged.connect(self.calcular_preco_venda)
        
        # Margem de lucro
        self.margem_lucro_input = QDoubleSpinBox()
        self.margem_lucro_input.setRange(0, 999.99)
        self.margem_lucro_input.setSuffix("%")
        self.margem_lucro_input.setDecimals(2)
        self.margem_lucro_input.setValue(30.0)  # Valor padrão de 30%
        self.margem_lucro_input.valueChanged.connect(self.calcular_preco_venda)
        
        # Preço de venda
        self.preco_venda_input = QDoubleSpinBox()
        self.preco_venda_input.setRange(0, 99999.99)
        self.preco_venda_input.setPrefix("R$ ")
        self.preco_venda_input.setDecimals(2)
        self.preco_venda_input.valueChanged.connect(self.calcular_margem_lucro)
        
        # Data de validade
        self.data_validade_input = QDateEdit()
        self.data_validade_input.setDisplayFormat("dd/MM/yyyy")
        self.data_validade_input.setCalendarPopup(True)
        self.data_validade_input.setDate(QDate.currentDate().addDays(30))  # Default para 30 dias
        
        self.localizacao_input = QLineEdit()

        self.fracionado_checkbox = QCheckBox("Produto Fracionado")
        self.fracionado_checkbox.toggled.connect(self.toggle_campos_fracionado)
        
        # Campos específicos para fracionamento
        self.unidade_medida_input = QLineEdit()
        self.unidade_medida_input.setPlaceholderText("Ex: kg, litros, metros, etc.")
        
        self.qtd_por_embalagem_input = QSpinBox()
        self.qtd_por_embalagem_input.setRange(1, 9999)
        self.qtd_por_embalagem_input.setValue(1)
        
        self.preco_unitario_fracao_input = QDoubleSpinBox()
        self.preco_unitario_fracao_input.setRange(0, 99999.99)
        self.preco_unitario_fracao_input.setPrefix("R$ ")
        self.preco_unitario_fracao_input.setDecimals(2)
        
        self.estoque_fracionado_input = QSpinBox()
        self.estoque_fracionado_input.setRange(0, 99999)
        
        self.fornecedor_combo = QComboBox()
        self.carregar_fornecedores()
        
        # Adicionar campos ao formulário
        form_layout.addRow("Código de Barras:", self.codigo_barras_input)
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Descrição:", self.descricao_input)
        form_layout.addRow("Quantidade:", self.quantidade_input)
        form_layout.addRow("Estoque Mínimo:", self.estoque_minimo_input)
        form_layout.addRow("Preço de Compra:", self.preco_compra_input)
        form_layout.addRow("Margem de Lucro:", self.margem_lucro_input)
        form_layout.addRow("Preço de Venda:", self.preco_venda_input)
        form_layout.addRow("Data de Validade:", self.data_validade_input)
        form_layout.addRow("Localização:", self.localizacao_input)
        form_layout.addRow("Fornecedor:", self.fornecedor_combo)
        form_layout.addRow("", self.fracionado_checkbox)
        form_layout.addRow("Unidade de Medida:", self.unidade_medida_input)
        form_layout.addRow("Qtd por Embalagem:", self.qtd_por_embalagem_input)
        form_layout.addRow("Preço Unitário (Fração):", self.preco_unitario_fracao_input)
        form_layout.addRow("Estoque Fracionado:", self.estoque_fracionado_input)

         # Inicialmente desabilitar campos de fracionamento
        self.toggle_campos_fracionado()

        layout.addLayout(form_layout)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar_produto)
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        
        layout.addLayout(button_layout)
    
    def toggle_campos_fracionado(self):
        """Habilita/desabilita campos de fracionamento baseado no checkbox."""
        enabled = self.fracionado_checkbox.isChecked()
        
        self.unidade_medida_input.setEnabled(enabled)
        self.qtd_por_embalagem_input.setEnabled(enabled)
        self.preco_unitario_fracao_input.setEnabled(enabled)
        self.estoque_fracionado_input.setEnabled(enabled)
        
        if not enabled:
            # Limpar campos quando desabilitado
            self.unidade_medida_input.clear()
            self.qtd_por_embalagem_input.setValue(1)
            self.preco_unitario_fracao_input.setValue(0)
            self.estoque_fracionado_input.setValue(0)
    
    def calcular_preco_venda(self):
        """Calcula o preço de venda com base no preço de compra e margem de lucro."""
        preco_compra = self.preco_compra_input.value()
        margem = self.margem_lucro_input.value() / 100
        
        # Evitar sinal de mudança recursivo
        self.preco_venda_input.blockSignals(True)
        self.preco_venda_input.setValue(preco_compra * (1 + margem))
        self.preco_venda_input.blockSignals(False)
    
    def calcular_margem_lucro(self):
        """Calcula a margem de lucro com base no preço de compra e preço de venda."""
        preco_compra = self.preco_compra_input.value()
        preco_venda = self.preco_venda_input.value()
        
        if preco_compra > 0:
            margem = ((preco_venda / preco_compra) - 1) * 100
            
            # Evitar sinal de mudança recursivo
            self.margem_lucro_input.blockSignals(True)
            self.margem_lucro_input.setValue(margem)
            self.margem_lucro_input.blockSignals(False)
    
    def carregar_fornecedores(self):
        """Carrega a lista de fornecedores para o combobox."""
        self.fornecedor_combo.clear()
        self.fornecedor_combo.addItem("Selecione um fornecedor", None)
        
        fornecedores = self.db.listar_fornecedores()
        for fornecedor in fornecedores:
            # Mudança aqui: usar 'empresa' ao invés de 'nome'
            self.fornecedor_combo.addItem(fornecedor['empresa'], fornecedor['id'])
    
    def carregar_dados_produto(self):
        """Carrega os dados do produto nos campos do formulário."""
        self.codigo_barras_input.setText(self.produto['codigo_barras'] or "")
        self.nome_input.setText(self.produto['nome'])
        self.descricao_input.setText(self.produto['descricao'] or "")
        self.quantidade_input.setValue(self.produto['quantidade'])
        self.estoque_minimo_input.setValue(self.produto['estoque_minimo'] or 0)
        self.preco_compra_input.setValue(self.produto['preco_compra'])
        
        # Bloquear sinais para evitar cálculos em cascata durante o carregamento
        self.margem_lucro_input.blockSignals(True)
        self.preco_venda_input.blockSignals(True)
        
        self.margem_lucro_input.setValue(self.produto['margem_lucro'] or 30.0)
        self.preco_venda_input.setValue(self.produto['preco_venda'])
        
        # Desbloquear sinais
        self.margem_lucro_input.blockSignals(False)
        self.preco_venda_input.blockSignals(False)
        
        if self.produto['data_validade']:
            data_validade = QDate.fromString(self.produto['data_validade'], "yyyy-MM-dd")
            self.data_validade_input.setDate(data_validade)
        
        self.localizacao_input.setText(self.produto['localizacao'] or "")
        
        # Carregar dados de fracionamento
        self.fracionado_checkbox.setChecked(bool(self.produto['fracionado']))
        self.unidade_medida_input.setText(self.produto['unidade_medida'] or "")
        
        # Converter para int antes de definir o valor
        qtd_embalagem = int(self.produto['qtd_por_embalagem'] or 1)
        self.qtd_por_embalagem_input.setValue(qtd_embalagem)
        
        self.preco_unitario_fracao_input.setValue(self.produto['preco_unitario_fracao'] or 0)
        
        # Converter estoque fracionado para int se necessário
        estoque_frac = int(self.produto['estoque_fracionado'] or 0)
        self.estoque_fracionado_input.setValue(estoque_frac)
        
        # Selecionar o fornecedor
        if self.produto['fornecedor_id']:
            index = self.fornecedor_combo.findData(self.produto['fornecedor_id'])
            if index != -1:
                self.fornecedor_combo.setCurrentIndex(index)
    
    def salvar_produto(self):
        """Salva os dados do produto no banco de dados."""
        # Validar campos obrigatórios
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do produto é obrigatório!")
            return
        
        # Validações para produtos fracionados
        if self.fracionado_checkbox.isChecked():
            if not self.unidade_medida_input.text().strip():
                QMessageBox.warning(self, "Erro", "Unidade de medida é obrigatória para produtos fracionados!")
                return
            if self.qtd_por_embalagem_input.value() <= 0:
                QMessageBox.warning(self, "Erro", "Quantidade por embalagem deve ser maior que zero!")
                return
        
        # Coletar dados do formulário
        codigo_barras = self.codigo_barras_input.text().strip()
        nome = self.nome_input.text().strip()
        descricao = self.descricao_input.text().strip()
        quantidade = self.quantidade_input.value()
        estoque_minimo = self.estoque_minimo_input.value()
        preco_compra = self.preco_compra_input.value()
        margem_lucro = self.margem_lucro_input.value()
        preco_venda = self.preco_venda_input.value()
        data_validade = self.data_validade_input.date().toString("yyyy-MM-dd")
        localizacao = self.localizacao_input.text().strip()
        
        # Dados de fracionamento
        fracionado = self.fracionado_checkbox.isChecked()
        unidade_medida = self.unidade_medida_input.text().strip() if fracionado else "unidade"
        qtd_por_embalagem = self.qtd_por_embalagem_input.value() if fracionado else 1
        preco_unitario_fracao = self.preco_unitario_fracao_input.value() if fracionado else None
        estoque_fracionado = self.estoque_fracionado_input.value() if fracionado else 0
        
        fornecedor_id = self.fornecedor_combo.currentData()
        if fornecedor_id == "":
            fornecedor_id = None
        
        try:
            # Inserir ou atualizar produto
            if self.produto_id:
                sucesso = self.db.atualizar_produto(
                    self.produto_id, codigo_barras, nome, descricao, quantidade, 
                    estoque_minimo, preco_compra, margem_lucro, preco_venda, 
                    data_validade, localizacao, fornecedor_id,
                    fracionado, unidade_medida, qtd_por_embalagem, 
                    preco_unitario_fracao, estoque_fracionado
                )
                mensagem = "Produto atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_produto(
                    codigo_barras, nome, descricao, quantidade, estoque_minimo,
                    preco_compra, margem_lucro, preco_venda, data_validade, 
                    localizacao, fornecedor_id,
                    fracionado, unidade_medida, qtd_por_embalagem, 
                    preco_unitario_fracao, estoque_fracionado
                )
                mensagem = "Produto cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o produto.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar produto: {str(e)}")

class DialogQuebrarEmbalagem(QDialog):
    def __init__(self, db, produto_info):
        super().__init__()
        self.db = db
        self.produto_info = produto_info
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Quebrar Embalagem")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # Informações do produto
        info_group = QGroupBox("Informações do Produto")
        info_layout = QFormLayout(info_group)
        
        info_layout.addRow("Produto:", QLabel(self.produto_info['nome']))
        info_layout.addRow("Embalagens disponíveis:", QLabel(str(self.produto_info['embalagens_inteiras'])))
        info_layout.addRow("Unidades por embalagem:", QLabel(str(self.produto_info['qtd_por_embalagem'])))
        info_layout.addRow("Estoque fracionado atual:", QLabel(f"{self.produto_info['estoque_fracionado']} {self.produto_info['unidade_medida']}"))
        
        layout.addWidget(info_group)
        
        # Entrada para quantidade a quebrar
        quebrar_group = QGroupBox("Quebrar Embalagens")
        quebrar_layout = QFormLayout(quebrar_group)
        
        self.quantidade_input = QSpinBox()
        self.quantidade_input.setRange(1, self.produto_info['embalagens_inteiras'])
        self.quantidade_input.setValue(1)
        self.quantidade_input.valueChanged.connect(self.atualizar_preview)
        
        quebrar_layout.addRow("Quantidade de embalagens:", self.quantidade_input)
        
        # Preview do resultado
        self.preview_label = QLabel()
        self.atualizar_preview()
        quebrar_layout.addRow("Resultado:", self.preview_label)
        
        layout.addWidget(quebrar_group)
        
        # Botões
        button_layout = QHBoxLayout()
        
        confirmar_btn = QPushButton("Confirmar")
        confirmar_btn.clicked.connect(self.quebrar_embalagem)
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(confirmar_btn)
        button_layout.addWidget(cancelar_btn)
        
        layout.addLayout(button_layout)
    
    def atualizar_preview(self):
        """Atualiza o preview do resultado da quebra."""
        qtd_quebrar = self.quantidade_input.value()
        unidades_geradas = qtd_quebrar * self.produto_info['qtd_por_embalagem']
        novo_estoque_fracionado = self.produto_info['estoque_fracionado'] + unidades_geradas
        novas_embalagens = self.produto_info['embalagens_inteiras'] - qtd_quebrar
        
        preview_text = f"""
        Embalagens restantes: {novas_embalagens}
        Estoque fracionado: {novo_estoque_fracionado} {self.produto_info['unidade_medida']}
        (+{unidades_geradas} {self.produto_info['unidade_medida']} geradas)
        """
        
        self.preview_label.setText(preview_text.strip())
    
    def quebrar_embalagem(self):
        """Confirma a quebra da embalagem."""
        qtd_quebrar = self.quantidade_input.value()
        
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Quebra",
            f"Confirma quebrar {qtd_quebrar} embalagem(ns) em unidades fracionadas?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            if self.db.quebrar_embalagem(self.produto_info['produto_id'], qtd_quebrar):
                QMessageBox.information(self, "Sucesso", "Embalagem quebrada com sucesso!")
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível quebrar a embalagem.")