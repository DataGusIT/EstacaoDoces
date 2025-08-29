from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QDateEdit, QComboBox, QMessageBox, QHeaderView, QDoubleSpinBox,
                           QDialog, QFrame, QTabWidget, QRadioButton, QFileDialog, 
                           QSizePolicy, QGroupBox, QProgressDialog)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor
from datetime import datetime, timedelta
import csv
import os
import math

# Importações necessárias
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager

# Adicione estas importações extras no topo do seu arquivo
from PyQt5.QtWidgets import QProgressBar, QFrame
from PyQt5.QtCore import Qt

# --- CLASSE 1: DIÁLOGO DE ALERTA (ESTILO PERFIL) ---
class AlertDialog(QDialog):
    """Caixa de diálogo com o estilo sutil da tela de perfil."""
    def __init__(self, parent, title, message, alert_type='info', buttons=QMessageBox.Ok, theme_colors=None):
        super().__init__(parent)
        self.theme_colors = theme_colors if theme_colors is not None else {}
        self.drag_position = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        type_info = { 'success':  {'icon': 'check', 'color': '#28a745'}, 'warning':  {'icon': 'estoque_baixo', 'color': '#ffc107'}, 'error':    {'icon': 'delete', 'color': '#dc3545'}, 'question': {'icon': 'question', 'color': '#17a2b8'}, 'info':     {'icon': 'sobre', 'color': self.theme_colors.get('accent_color', '#007AFF')}, }.get(alert_type, {'icon': 'sobre', 'color': '#007AFF'})
        self.accent_color = type_info['color']
        self.icon_name = type_info['icon']
        self._setup_ui(title, message, buttons)

    def _setup_ui(self, title, message, buttons):
        self.setMinimumWidth(400)
        container = QFrame(self); container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(container); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        self.header = QFrame(); self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header); header_layout.setContentsMargins(20, 15, 10, 15)
        header_title_label = QLabel(title); header_title_label.setObjectName("headerTitleLabel")
        close_button = QPushButton(); close_button.setObjectName("controlButton"); close_button.setFixedSize(28, 28)
        close_button.setIcon(IconManager.get_icon('fechar', color=self.theme_colors.get('text_secondary', '#666')))
        close_button.clicked.connect(self.reject)
        header_layout.addWidget(header_title_label); header_layout.addStretch(); header_layout.addWidget(close_button)
        main_layout.addWidget(self.header)
        body = QWidget(); body_layout = QVBoxLayout(body); body_layout.setContentsMargins(25, 20, 25, 25); body_layout.setSpacing(20)
        subtitle_layout = QHBoxLayout()
        icon_label = QLabel(); icon_label.setPixmap(IconManager.get_icon(self.icon_name, color=self.accent_color).pixmap(24, 24))
        subtitle_label = QLabel(title); subtitle_label.setObjectName("subtitleLabel")
        subtitle_layout.addWidget(icon_label); subtitle_layout.addWidget(subtitle_label); subtitle_layout.addStretch()
        message_label = QLabel(message); message_label.setWordWrap(True); message_label.setObjectName("messageLabel")
        button_layout = QHBoxLayout(); button_layout.addStretch()
        if buttons & QMessageBox.Yes: button_layout.addWidget(self._create_button("Sim", lambda: self.done(QMessageBox.Yes), is_primary=True))
        if buttons & QMessageBox.Ok: button_layout.addWidget(self._create_button("OK", self.accept, is_primary=True))
        if buttons & QMessageBox.No: button_layout.addWidget(self._create_button("Não", self.reject))
        if buttons & QMessageBox.Cancel: button_layout.addWidget(self._create_button("Cancelar", self.reject))
        body_layout.addLayout(subtitle_layout); body_layout.addWidget(message_label); body_layout.addLayout(button_layout)
        main_layout.addWidget(body)
        base_layout = QVBoxLayout(self); base_layout.addWidget(container)
        self.apply_styles()

    def _create_button(self, text, on_click, is_primary=False):
        btn = QPushButton(text); btn.clicked.connect(on_click); btn.setCursor(Qt.PointingHandCursor)
        btn.setObjectName("primaryButton" if is_primary else "secondaryButton")
        return btn
        
    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f""" #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }} #header {{ border-bottom: 1px solid {colors.get('border_color', '#ccc')}; }} #headerTitleLabel {{ color: {colors.get('text_color', '#000')}; font-weight: bold; }} #subtitleLabel {{ color: {colors.get('text_color', '#000')}; font-size: 14pt; font-weight: bold; }} #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }} #controlButton {{ background: transparent; border: none; border-radius: 14px; }} #controlButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }} QPushButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; min-width: 90px;}} #primaryButton {{ background-color: {self.accent_color}; color: white; border: none; }} #secondaryButton {{ background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }} #secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }} """)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

# --- CLASSE 2: DIÁLOGO DE PROGRESSO TEMÁTICO ---
class ThemedProgressDialog(QDialog):
    canceled = pyqtSignal()
    def __init__(self, parent, title, message, theme_colors):
        super().__init__(parent)
        self.theme_colors = theme_colors if theme_colors is not None else {}
        self.drag_position = None
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setModal(True)
        self._setup_ui(title, message)
        self.apply_styles()

    def _setup_ui(self, title, message):
        self.setMinimumWidth(400)
        container = QFrame(self); container.setObjectName("mainContainer")
        main_layout = QVBoxLayout(container); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)
        self.header = QFrame(); self.header.setObjectName("header")
        header_layout = QHBoxLayout(self.header); header_layout.setContentsMargins(20, 15, 10, 15)
        title_label = QLabel(title); title_label.setObjectName("headerTitleLabel")
        header_layout.addWidget(title_label)
        main_layout.addWidget(self.header)
        body = QWidget(); body_layout = QVBoxLayout(body); body_layout.setContentsMargins(25, 20, 25, 25); body_layout.setSpacing(15)
        message_label = QLabel(message); message_label.setWordWrap(True); message_label.setObjectName("messageLabel")
        self.progress_bar = QProgressBar(); self.progress_bar.setTextVisible(True); self.progress_bar.setAlignment(Qt.AlignCenter)
        button_layout = QHBoxLayout(); button_layout.addStretch()
        cancel_button = QPushButton("Cancelar"); cancel_button.setObjectName("secondaryButton"); cancel_button.setCursor(Qt.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        body_layout.addWidget(message_label); body_layout.addWidget(self.progress_bar); body_layout.addLayout(button_layout)
        main_layout.addWidget(body)
        base_layout = QVBoxLayout(self); base_layout.addWidget(container)

    def apply_styles(self):
        colors = self.theme_colors
        self.setStyleSheet(f""" #mainContainer {{ background-color: {colors.get('surface_color', '#fff')}; border-radius: 12px; border: 1px solid {colors.get('border_color', '#ccc')}; }} #header {{ border-bottom: 1px solid {colors.get('border_color', '#ccc')}; }} #headerTitleLabel {{ color: {colors.get('text_color', '#000')}; font-weight: bold; }} #messageLabel {{ color: {colors.get('text_secondary', '#333')}; font-size: 11pt; }} QPushButton#secondaryButton {{ font-weight: bold; padding: 10px 25px; border-radius: 8px; background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; }} QPushButton#secondaryButton:hover {{ background-color: {colors.get('button_hover', '#eee')}; }} QProgressBar {{ border: 1px solid {colors.get('border_color', '#ccc')}; border-radius: 8px; padding: 1px; text-align: center; background-color: {colors.get('bg_color', '#eee')}; color: {colors.get('text_color', '#000')}; }} QProgressBar::chunk {{ background-color: {colors.get('accent_color', '#007AFF')}; border-radius: 7px; }} """)
    def setValue(self, value): self.progress_bar.setValue(value)
    def reject(self): self.canceled.emit(); super().reject()
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton: self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
    def mouseMoveEvent(self, event):
        if self.drag_position and event.buttons() == Qt.LeftButton: self.move(event.globalPos() - self.drag_position)

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
        # --- INÍCIO DA MODIFICAÇÃO ---
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels(["ID", "Produto", "Tipo", "Desconto %", "Detalhes da Promoção", "Início", "Fim", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents) # Produto
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents) # Tipo
        self.tabela.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents) # Desconto %
        self.tabela.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch) # Detalhes
        # --- FIM DA MODIFICAÇÃO ---
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # ... (Restante da função initUI permanece igual) ...
        paginacao_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton(" Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
        self.page_label = QLabel(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.next_page_btn = QPushButton("Próxima ")
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

        for row, promocao_row in enumerate(promocoes):
            promocao = dict(promocao_row)
            self.tabela.insertRow(row)

            produto = self.db.obter_produto(promocao['produto_id'])
            if not produto: continue

            tipo_aplicacao = promocao.get('tipo_aplicacao', 'Ambos')
            if not produto.get('fracionado'): tipo_aplicacao = 'Embalagem'

            tipo_texto = tipo_aplicacao
            detalhes_html = ""
            taxa_desconto = 0.0

            if tipo_aplicacao == 'Fração':
                preco_original, preco_promo = produto.get('preco_unitario_fracao', 0), promocao.get('preco_promocional_fracao', 0)
                if preco_original > 0: taxa_desconto = ((preco_original - preco_promo) / preco_original) * 100
                detalhes_html = f"""<span style='color: #888;'>Original: R$ {preco_original:.2f}</span><br><b style='font-size: 11pt; color: #28a745;'>Promoção: R$ {preco_promo:.2f}</b>"""
            elif tipo_aplicacao == 'Embalagem':
                preco_original, preco_promo = promocao.get('preco_antigo', 0), promocao.get('preco_promocional', 0)
                if preco_original > 0: taxa_desconto = ((preco_original - preco_promo) / preco_original) * 100
                detalhes_html = f"""<span style='color: #888;'>Original: R$ {preco_original:.2f}</span><br><b style='font-size: 11pt; color: #28a745;'>Promoção: R$ {preco_promo:.2f}</b>"""
            else: # 'Ambos'
                preco_original_emb, preco_promo_emb = promocao.get('preco_antigo', 0), promocao.get('preco_promocional', 0)
                if preco_original_emb > 0: taxa_desconto = ((preco_original_emb - preco_promo_emb) / preco_original_emb) * 100
                preco_original_fracao = produto.get('preco_unitario_fracao', 0)
                preco_promo_fracao = preco_original_fracao * (1 - (taxa_desconto / 100))
                detalhes_html = f"""<b>Emb:</b> R$ {preco_original_emb:.2f} → <b style='color: #28a745;'>R$ {preco_promo_emb:.2f}</b><br><b>Fração:</b> R$ {preco_original_fracao:.2f} → <b style='color: #28a745;'>R$ {preco_promo_fracao:.2f}</b>"""

            detalhes_label = QLabel(detalhes_html)
            detalhes_label.setWordWrap(True)
            detalhes_label.setAlignment(Qt.AlignCenter)

            self.tabela.setItem(row, 0, QTableWidgetItem(str(promocao['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(promocao['produto_nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(tipo_texto))
            self.tabela.setItem(row, 3, QTableWidgetItem(f"{taxa_desconto:.1f}%"))
            self.tabela.setCellWidget(row, 4, detalhes_label)
            self.tabela.setItem(row, 5, QTableWidgetItem(str(promocao['data_inicio'])))

            fim_item = QTableWidgetItem(str(promocao['data_fim']))
            data_fim_promo = promocao.get('data_fim')
            data_validade_prod = produto.get('data_validade')

            # --- INÍCIO DA CORREÇÃO DA FONTE ---
            # Se a data de fim da promoção for a mesma da validade, colore a FONTE
            if data_fim_promo and data_validade_prod and data_fim_promo == data_validade_prod:
                # Usa uma cor amarela brilhante para boa visibilidade no tema escuro
                fim_item.setForeground(QColor("#FFD700")) 
                font = QFont()
                font.setBold(True)
                fim_item.setFont(font)
                fim_item.setToolTip("Promoção termina na data de validade do produto.")
            # --- FIM DA CORREÇÃO DA FONTE ---
            
            self.tabela.setItem(row, 6, fim_item)

            # --- INÍCIO DA CORREÇÃO DOS BOTÕES DE AÇÃO ---
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(5, 2, 5, 2)
            acoes_layout.setSpacing(5)
            
            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), " ")
            editar_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            editar_btn.setToolTip("Editar Promoção")
            editar_btn.clicked.connect(lambda _, p_id=promocao['id']: self.abrir_formulario_promocao(p_id))
            
            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), " ")
            excluir_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            excluir_btn.setToolTip("Excluir Promoção")
            excluir_btn.clicked.connect(lambda _, p_id=promocao['id']: self.excluir_promocao(p_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            self.tabela.setCellWidget(row, 7, acoes_widget)
            # --- FIM DA CORREÇÃO DOS BOTÕES DE AÇÃO ---
        
        self.tabela.verticalHeader().setDefaultSectionSize(55)
            
    # ... O restante do código (abrir formulários, excluir, importar, exportar) permanece o mesmo ...
    def abrir_formulario_promocao(self, promocao_id=None):
        # A chamada agora passa o parent, como corrigido anteriormente
        dialog = FormularioPromocao(self.db, self.theme_colors, promocao_id, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_visualizacao_dados()
            
    def excluir_promocao(self, promocao_id):
        dialog = AlertDialog(self, "Confirmar Exclusão",
                             "Tem certeza que deseja excluir esta promoção?",
                             alert_type='question', buttons=QMessageBox.Yes | QMessageBox.No, theme_colors=self.theme_colors)
        
        if dialog.exec_() == QMessageBox.Yes:
            if self.db.excluir_promocao(promocao_id):
                AlertDialog(self, "Sucesso", "Promoção excluída com sucesso.", alert_type='success', theme_colors=self.theme_colors).exec_()
                self.atualizar_visualizacao_dados()
            else:
                AlertDialog(self, "Erro", "Não foi possível excluir a promoção.", alert_type='error', theme_colors=self.theme_colors).exec_()
    
    def exportar_csv(self):
        try:
            promocoes = self.db.listar_promocoes()
            if not promocoes:
                AlertDialog(self, "Exportar CSV", "Não há promoções para exportar.", alert_type='info', theme_colors=self.theme_colors).exec_()
                return
                
            arquivo, _ = QFileDialog.getSaveFileName(self, "Exportar Promoções", "promocoes.csv", "Arquivos CSV (*.csv)")
            if not arquivo:
                return

            with open(arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['ID', 'Produto', 'Preço Antigo', 'Preço Promocional', 'Taxa de Desconto (%)', 'Data Início', 'Data Fim', 'Descrição']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for promocao in promocoes:
                    taxa = ((promocao['preco_antigo'] - promocao['preco_promocional']) / promocao['preco_antigo']) * 100 if promocao['preco_antigo'] > 0 else 0
                    writer.writerow({
                        'ID': promocao['id'], 'Produto': promocao['produto_nome'],
                        'Preço Antigo': f"{promocao['preco_antigo']:.2f}",
                        'Preço Promocional': f"{promocao['preco_promocional']:.2f}",
                        'Taxa de Desconto (%)': f"{taxa:.1f}",
                        'Data Início': promocao['data_inicio'], 'Data Fim': promocao['data_fim'],
                        'Descrição': promocao.get('descricao', '')
                    })
            
            AlertDialog(self, "Sucesso", f"Promoções exportadas para:\n{arquivo}", alert_type='success', theme_colors=self.theme_colors).exec_()
        
        except Exception as e:
            AlertDialog(self, "Erro", f"Erro ao exportar CSV:\n{str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()

    def importar_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importar Promoções CSV", "", "CSV Files (*.csv)")
        if not file_path: return

        self.progress_dialog = ThemedProgressDialog(self, "Importando Promoções", "Aguarde enquanto os dados são processados...", self.theme_colors)
        self.import_thread = PromocaoCsvImportWorker(self.db.db_path, file_path)
        self.import_thread.progress.connect(self.progress_dialog.setValue)
        self.import_thread.finished.connect(self.importacao_concluida)
        self.progress_dialog.canceled.connect(self.import_thread.terminate)
        
        self.import_thread.start()
        self.progress_dialog.exec_()

    def importacao_concluida(self, importadas, erros, detalhes):
        self.progress_dialog.close()
        self.atualizar_visualizacao_dados()
        msg = f"Importação concluída!\n\n- Promoções importadas: {importadas}\n- Linhas com erro: {erros}"
        if erros > 0:
            msg += "\n\nPrimeiros erros:\n" + "\n".join(detalhes[:5])
            AlertDialog(self, "Importação com Erros", msg, alert_type='warning', theme_colors=self.theme_colors).exec_()
        else:
            AlertDialog(self, "Importação Concluída", msg, alert_type='success', theme_colors=self.theme_colors).exec_()

class FormularioPromocao(QDialog):
    def __init__(self, db, theme_colors, promocao_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.theme_colors = theme_colors
        self.promocao_id = promocao_id
        self.promocao = None
        self.produto_selecionado_id = None
        # --- NOVAS VARIÁVEIS PARA GUARDAR PREÇOS ORIGINAIS ---
        self.preco_original_embalagem = 0.0
        self.preco_original_fracao = 0.0

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
        self.setMinimumSize(600, 800)
        layout = QVBoxLayout(self)

        # --- SELEÇÃO DE PRODUTO (Sem alterações) ---
        produto_group = QGroupBox("1. Selecione o Produto", self)
        produto_layout = QVBoxLayout(produto_group)
        self.tabs_selecao_produto = QTabWidget(self)
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

        # --- DETALHES DA PROMOÇÃO (TOTALMENTE REFEITO) ---
        detalhes_group = QGroupBox("2. Defina os Detalhes da Promoção", self)
        form_layout = QFormLayout(detalhes_group)

        self.produto_selecionado_label = QLabel("Nenhum produto selecionado")
        self.produto_selecionado_label.setStyleSheet("font-weight: bold;")
        
        self.group_tipo_aplicacao = QGroupBox("Tipo de Promoção")
        self.group_tipo_aplicacao.setVisible(False)
        group_layout = QHBoxLayout(self.group_tipo_aplicacao)
        self.radio_ambos = QRadioButton("Ambos")
        self.radio_embalagem = QRadioButton("Apenas Embalagem")
        self.radio_fracao = QRadioButton("Apenas Fração")
        self.radio_ambos.setChecked(True)
        group_layout.addWidget(self.radio_ambos)
        group_layout.addWidget(self.radio_embalagem)
        group_layout.addWidget(self.radio_fracao)
        
        # --- LABELS DINÂMICAS E CAMPOS REINTRODUZIDOS ---
        self.lbl_preco_original = QLabel("Preço Original:") # O texto será alterado dinamicamente
        self.preco_antigo_input = QDoubleSpinBox(self)
        self.preco_antigo_input.setReadOnly(True)
        self.preco_antigo_input.setRange(0, 99999.99); self.preco_antigo_input.setPrefix("R$ ")

        self.lbl_taxa_desconto = QLabel("Taxa de Desconto:")
        self.taxa_desconto_input = QDoubleSpinBox(self)
        self.taxa_desconto_input.setRange(0.1, 100); self.taxa_desconto_input.setSuffix(" %")
        self.taxa_desconto_input.setValue(10)

        self.lbl_preco_promocional_embalagem = QLabel("Preço Promocional (Embalagem):")
        self.preco_promocional_input = QDoubleSpinBox(self)
        self.preco_promocional_input.setRange(0, 99999.99); self.preco_promocional_input.setPrefix("R$ ")
        
        self.lbl_preco_fracao = QLabel("Preço Promocional (Fração):")
        self.preco_promocional_fracao_input = QDoubleSpinBox(self)
        self.preco_promocional_fracao_input.setRange(0, 9999.99); self.preco_promocional_fracao_input.setPrefix("R$ ")
        
        self.data_inicio_input = QDateEdit(calendarPopup=True, date=QDate.currentDate())
        self.data_inicio_input.setDisplayFormat("dd/MM/yyyy")
        self.data_fim_input = QDateEdit(calendarPopup=True, date=QDate.currentDate().addDays(30))
        self.data_fim_input.setDisplayFormat("dd/MM/yyyy")
        self.descricao_input = QLineEdit(self)

        form_layout.addRow("Produto:", self.produto_selecionado_label)
        form_layout.addRow(self.group_tipo_aplicacao)
        form_layout.addRow(self.lbl_preco_original, self.preco_antigo_input)
        form_layout.addRow(self.lbl_taxa_desconto, self.taxa_desconto_input)
        form_layout.addRow(self.lbl_preco_promocional_embalagem, self.preco_promocional_input)
        form_layout.addRow(self.lbl_preco_fracao, self.preco_promocional_fracao_input)
        form_layout.addRow("Data de Início:", self.data_inicio_input)
        form_layout.addRow("Data de Fim:", self.data_fim_input)
        form_layout.addRow("Descrição:", self.descricao_input)
        layout.addWidget(detalhes_group)

        # --- BOTÕES DE AÇÃO (Sem alterações) ---
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(" Salvar Promoção")
        self.salvar_btn.setObjectName("primaryActionButton")
        self.salvar_btn.clicked.connect(self.salvar_promocao)
        self.cancelar_btn = QPushButton(" Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        layout.addLayout(button_layout)

        # --- CONEXÕES DOS SINAIS ---
        self.radio_ambos.toggled.connect(self._atualizar_visibilidade_campos_promo)
        self.radio_embalagem.toggled.connect(self._atualizar_visibilidade_campos_promo)
        self.radio_fracao.toggled.connect(self._atualizar_visibilidade_campos_promo)
        self.taxa_desconto_input.valueChanged.connect(self.calcular_preco_promocional)
        self.preco_promocional_input.valueChanged.connect(self.calcular_taxa_desconto)
        self.preco_promocional_fracao_input.valueChanged.connect(self.calcular_taxa_desconto)

    def _atualizar_visibilidade_campos_promo(self):
        """Controla a visibilidade e o comportamento dos campos de preço com base na seleção."""
        if not self.produto_selecionado_id:
            return

        produto = self.db.obter_produto(self.produto_selecionado_id)
        if not produto:
            return
            
        is_fracionado = produto.get('fracionado', False)

        # --- INÍCIO DA LÓGICA DE VISIBILIDADE CORRIGIDA ---
        if not is_fracionado:
            # Se o produto NÃO é fracionado, esconde tudo que for de fração
            self.lbl_preco_fracao.setVisible(False)
            self.preco_promocional_fracao_input.setVisible(False)
            self.lbl_preco_promocional_embalagem.setVisible(True)
            self.preco_promocional_input.setVisible(True)
            self.lbl_preco_original.setText("Preço Original:")
            self.preco_antigo_input.setValue(self.preco_original_embalagem)
        else:
            # Se o produto É fracionado, a visibilidade depende dos radio buttons
            is_ambos = self.radio_ambos.isChecked()
            is_embalagem = self.radio_embalagem.isChecked()
            is_fracao = self.radio_fracao.isChecked()

            self.lbl_preco_promocional_embalagem.setVisible(is_ambos or is_embalagem)
            self.preco_promocional_input.setVisible(is_ambos or is_embalagem)
            
            self.lbl_preco_fracao.setVisible(is_ambos or is_fracao)
            self.preco_promocional_fracao_input.setVisible(is_ambos or is_fracao)

            if is_fracao:
                self.lbl_preco_original.setText("Preço Original (Fração):")
                self.preco_antigo_input.setValue(self.preco_original_fracao)
            else:
                self.lbl_preco_original.setText("Preço Original (Embalagem):")
                self.preco_antigo_input.setValue(self.preco_original_embalagem)
        # --- FIM DA LÓGICA DE VISIBILIDADE CORRIGIDA ---
        
        self.calcular_preco_promocional()

    def calcular_preco_promocional(self):
        """Calcula o preço promocional com base na taxa de desconto."""
        taxa = self.taxa_desconto_input.value()
        
        # Bloqueia sinais para evitar loops
        self.preco_promocional_input.blockSignals(True)
        self.preco_promocional_fracao_input.blockSignals(True)

        # Se a promoção for para fração, o desconto se aplica ao preço da fração
        if self.radio_fracao.isChecked():
            preco_original = self.preco_original_fracao
            novo_preco = preco_original * (1 - taxa / 100)
            self.preco_promocional_fracao_input.setValue(novo_preco)
        else: # Se for "Ambos" ou "Embalagem", o desconto se aplica ao preço da embalagem
            preco_original = self.preco_original_embalagem
            novo_preco_embalagem = preco_original * (1 - taxa / 100)
            self.preco_promocional_input.setValue(novo_preco_embalagem)
            
            # Se for "Ambos", calcula o preço da fração proporcionalmente
            if self.radio_ambos.isChecked() and self.preco_original_fracao > 0:
                taxa_proporcional = (self.preco_original_embalagem - novo_preco_embalagem) / self.preco_original_embalagem
                novo_preco_fracao = self.preco_original_fracao * (1 - taxa_proporcional)
                self.preco_promocional_fracao_input.setValue(novo_preco_fracao)

        self.preco_promocional_input.blockSignals(False)
        self.preco_promocional_fracao_input.blockSignals(False)

    def calcular_taxa_desconto(self):
        """Calcula a taxa de desconto quando um dos preços promocionais é alterado manualmente."""
        self.taxa_desconto_input.blockSignals(True)

        if self.radio_fracao.isChecked() and self.preco_original_fracao > 0:
            preco_promo = self.preco_promocional_fracao_input.value()
            taxa = ((self.preco_original_fracao - preco_promo) / self.preco_original_fracao) * 100
            self.taxa_desconto_input.setValue(taxa)
        elif self.preco_original_embalagem > 0:
            preco_promo = self.preco_promocional_input.value()
            taxa = ((self.preco_original_embalagem - preco_promo) / self.preco_original_embalagem) * 100
            self.taxa_desconto_input.setValue(taxa)

        self.taxa_desconto_input.blockSignals(False)

    def selecionar_produto(self, produto_id):
        # Resetar o campo de data sempre que um novo produto for selecionado
        self.data_fim_input.setEnabled(True)
        self.data_fim_input.setStyleSheet("") # Limpa qualquer estilo anterior
        self.data_fim_input.setDate(QDate.currentDate().addDays(30))

        if not produto_id:
            self.produto_selecionado_id = None
            self.produto_selecionado_label.setText("Nenhum produto selecionado")
            self.preco_antigo_input.setValue(0)
            self.group_tipo_aplicacao.setVisible(False)
            self._atualizar_visibilidade_campos_promo()
            return

        # --- INÍCIO DA CORREÇÃO ---
        # O erro estava aqui. Usamos o 'produto_id' que a função recebe,
        # e não 'self.produto_selecionado_id', que ainda não foi atualizado.
        produto = self.db.obter_produto(produto_id)
        # --- FIM DA CORREÇÃO ---
        
        if produto:
            self.produto_selecionado_id = produto['id'] # Agora atualizamos a variável da classe
            self.preco_original_embalagem = produto.get('preco_venda', 0)
            self.preco_original_fracao = produto.get('preco_unitario_fracao', 0)
            
            texto_label = produto['nome']
            if produto.get('fracionado'):
                self.group_tipo_aplicacao.setVisible(True) # Agora isso vai funcionar
                texto_label += f"\n(Preço Fração: R$ {self.preco_original_fracao:.2f})"
                self.radio_ambos.setChecked(True)
            else:
                self.group_tipo_aplicacao.setVisible(False)

            self.produto_selecionado_label.setText(texto_label)
            
            # Lógica de validade (permanece a mesma)
            DIAS_ALERTA_VENCIMENTO = 30
            data_validade_str = produto.get('data_validade')

            if data_validade_str:
                try:
                    data_validade_obj = datetime.strptime(data_validade_str, '%Y-%m-%d').date()
                    hoje = datetime.now().date()
                    dias_para_vencer = (data_validade_obj - hoje).days

                    if 0 <= dias_para_vencer <= DIAS_ALERTA_VENCIMENTO:
                        qdate_validade = QDate.fromString(data_validade_str, "yyyy-MM-dd")
                        self.data_fim_input.setDate(qdate_validade)
                        self.data_fim_input.setEnabled(False)
                except (ValueError, TypeError):
                    pass
            
            self._atualizar_visibilidade_campos_promo()

    def salvar_promocao(self):
        if not self.produto_selecionado_id:
            AlertDialog(self, "Ação Necessária", "Por favor, selecione um produto para a promoção.", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        produto = self.db.obter_produto(self.produto_selecionado_id)
        preco_antigo = self.preco_original_embalagem
        preco_promocional = self.preco_promocional_input.value()
        preco_promocional_fracao = self.preco_promocional_fracao_input.value()
        tipo_aplicacao = 'Ambos'
        if produto and produto.get('fracionado', False):
            if self.radio_embalagem.isChecked(): tipo_aplicacao = 'Embalagem'
            elif self.radio_fracao.isChecked(): tipo_aplicacao = 'Fração'

        if tipo_aplicacao in ['Ambos', 'Embalagem'] and not (0 < preco_promocional < preco_antigo):
            AlertDialog(self, "Dados Inválidos", f"O preço promocional da embalagem deve ser maior que zero e menor que o original (R$ {preco_antigo:.2f}).", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        if produto.get('fracionado', False) and tipo_aplicacao in ['Ambos', 'Fração'] and not (0 < preco_promocional_fracao < self.preco_original_fracao):
            AlertDialog(self, "Dados Inválidos", f"O preço promocional da fração deve ser maior que zero e menor que o original (R$ {self.preco_original_fracao:.2f}).", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        if self.data_inicio_input.date() > self.data_fim_input.date():
            AlertDialog(self, "Dados Inválidos", "A data de fim deve ser posterior à data de início.", alert_type='warning', theme_colors=self.theme_colors).exec_()
            return

        dados_promocao = {
            'produto_id': self.produto_selecionado_id,
            'preco_antigo': preco_antigo,
            'preco_promocional': preco_promocional,
            'data_inicio': self.data_inicio_input.date().toString("yyyy-MM-dd"),
            'data_fim': self.data_fim_input.date().toString("yyyy-MM-dd"),
            'descricao': self.descricao_input.text().strip(),
            'tipo_aplicacao': tipo_aplicacao,
            'preco_promocional_fracao': preco_promocional_fracao
        }

        try:
            if self.promocao_id:
                sucesso = self.db.atualizar_promocao(self.promocao_id, **dados_promocao)
                mensagem = "Promoção atualizada com sucesso!"
            else:
                sucesso = self.db.adicionar_promocao(**dados_promocao)
                mensagem = "Promoção cadastrada com sucesso!"
            
            if sucesso:
                AlertDialog(self, "Sucesso", mensagem, alert_type='success', theme_colors=self.theme_colors).exec_()
                self.accept()
            else:
                AlertDialog(self, "Erro", "Não foi possível salvar a promoção no banco de dados.", alert_type='error', theme_colors=self.theme_colors).exec_()
        
        except Exception as e:
            AlertDialog(self, "Erro Inesperado", f"Ocorreu um erro crítico: {str(e)}", alert_type='error', theme_colors=self.theme_colors).exec_()
    
    # Manter as funções restantes como estavam
    def carregar_dados_promocao(self):
        if not self.promocao: return
        self.tabs_selecao_produto.setEnabled(False)
        self.selecionar_produto(self.promocao['produto_id'])
        tipo_aplicacao = self.promocao.get('tipo_aplicacao', 'Ambos')
        if tipo_aplicacao == 'Embalagem': self.radio_embalagem.setChecked(True)
        elif tipo_aplicacao == 'Fração': self.radio_fracao.setChecked(True)
        else: self.radio_ambos.setChecked(True)
        self.preco_promocional_input.setValue(self.promocao['preco_promocional'])
        if self.promocao['preco_promocional_fracao']:
            self.preco_promocional_fracao_input.setValue(self.promocao['preco_promocional_fracao'])
        self.data_inicio_input.setDate(QDate.fromString(self.promocao['data_inicio'], "yyyy-MM-dd"))
        self.data_fim_input.setDate(QDate.fromString(self.promocao['data_fim'], "yyyy-MM-dd"))
        self.descricao_input.setText(self.promocao['descricao'])
        self._atualizar_visibilidade_campos_promo()

    def apply_styles(self):
        colors = self.theme_colors
        style = f""" QDialog {{ background-color: {colors.get('bg_color', '#fff')}; color: {colors.get('text_color', '#000')}; }} QGroupBox {{ border: 1px solid {colors.get('border_color', '#ccc')}; border-radius: 6px; margin-top: 15px; padding: 10px; font-weight: bold; }} QGroupBox::title {{ subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; background-color: {colors.get('bg_color', '#fff')}; color: {colors.get('text_secondary', '#333')}; }} QTableWidget {{ background-color: {colors.get('surface_color', '#f2f2f7')}; border: 1px solid {colors.get('border_color', '#d1d1d6')}; gridline-color: {colors.get('border_color', '#d1d1d6')}; }} QHeaderView::section {{ background-color: {colors.get('bg_color', '#fff')}; color: {colors.get('text_color', '#000')}; padding: 5px; border: 1px solid {colors.get('border_color', '#d1d1d6')}; font-weight: bold; }} QComboBox, QDoubleSpinBox, QDateEdit, QLineEdit, QRadioButton {{ background-color: transparent; color: {colors.get('text_color', '#000')}; }} QPushButton {{ background-color: transparent; color: {colors.get('text_color', '#000')}; border: 1px solid {colors.get('border_color', '#ccc')}; padding: 8px 12px; border-radius: 4px; font-weight: bold; }} QPushButton:hover {{ background-color: {colors.get('button_hover', '#e0e0e0')}; border: 1px solid {colors.get('accent_color', '#007aff')}; }} #primaryActionButton {{ background-color: {colors.get('accent_color', '#007aff')}; color: white; border: none; }} #primaryActionButton:hover {{ background-color: #0069d9; }} """
        self.setStyleSheet(style)
        self.salvar_btn.setIcon(IconManager.get_icon('save', 'white'))
        self.cancelar_btn.setIcon(IconManager.get_icon('cancel', colors.get('text_color', '#000')))

    def carregar_produtos_recomendados(self):
        self.tabela_recomendados.setRowCount(0)
        hoje = datetime.now().date()
        produtos_estoque_baixo = self.db.verificar_produtos_estoque_baixo()
        produtos_vencendo = self.db.verificar_produtos_vencendo(dias=30)
        for produto in produtos_estoque_baixo:
            row = self.tabela_recomendados.rowCount()
            self.tabela_recomendados.insertRow(row)
            self.tabela_recomendados.setItem(row, 0, QTableWidgetItem(produto['nome']))
            self.tabela_recomendados.setItem(row, 1, QTableWidgetItem("Estoque Baixo"))
            self.tabela_recomendados.setItem(row, 2, QTableWidgetItem(f"{produto['quantidade']} / {produto['estoque_minimo']}"))
            self.tabela_recomendados.setItem(row, 3, QTableWidgetItem(f"R$ {produto['preco_venda']:.2f}"))
            self.tabela_recomendados.item(row, 0).setData(Qt.UserRole, produto['id'])
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