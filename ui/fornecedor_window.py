from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame, QComboBox, QFileDialog,
                           QTextEdit, QSpinBox, QCheckBox, QGroupBox, QProgressDialog, QSizePolicy, QProgressBar) # QProgressDialog
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject
from PyQt5.QtGui import QFont, QIcon
import csv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import math # Adicionado para paginação

# Importações necessárias
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager # Importante para a thread

class FornecedorCsvImportWorker(QThread):
    """Executa a importação de CSV de fornecedores em uma thread."""
    progress = pyqtSignal(int)
    finished = pyqtSignal(int, int, list)

    def __init__(self, db_path, file_path):
        super().__init__()
        self.db_path = db_path
        self.file_path = file_path
        self.local_db = None

    def run(self):
        importados = 0
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
                        if not row.get('empresa', '').strip():
                            raise ValueError("Nome da empresa é obrigatório.")
                        
                        self.local_db.adicionar_fornecedor(
                            empresa=row.get('empresa', '').strip(),
                            representante=row.get('representante', '').strip(),
                            frequencia_compra=row.get('frequencia_compra', '').strip(),
                            telefone=row.get('telefone', '').strip(),
                            email=row.get('email', '').strip(),
                            endereco=row.get('endereco', '').strip(),
                            contato=row.get('contato', '').strip()
                        )
                        importados += 1
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
        
        self.finished.emit(importados, erros, detalhes_erros)

class FornecedorWindow(QWidget):
    def __init__(self, db, theme_colors):
        super().__init__()
        self.theme_colors = theme_colors 
        self.db = db
        # Estado da Paginação
        self.pagina_atual = 1
        self.itens_por_pagina = 50
        self.total_paginas = 1
        
        self.initUI()
        self.atualizar_visualizacao_dados()
        self.update_button_icons()
        self.carregar_dados()
        
    # NOVO MÉTODO: Centraliza a estilização dos botões (copiado da outra classe)
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
    
    def _get_flat_button_style(self):
        """Retorna uma string de estilo CSS para botões 'flat' (transparentes)."""
        text_color = self.theme_colors.get('text_color', '#000000')
        border_color = self.theme_colors.get('border_color', '#cccccc')
        hover_color = self.theme_colors.get('highlight_color', 'rgba(128, 128, 128, 0.2)')
        
        style = f"""
            QPushButton {{
                background-color: transparent;
                color: {text_color};
                border: 1px solid {border_color};
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
                border: 1px solid {text_color};
            }}
            QPushButton:pressed {{
                background-color: {border_color};
            }}
        """
        return style
    
    def apply_styles(self):
        """Aplica todos os estilos aos widgets da janela."""
        # Botão primário (colorido)
        self.add_button.setStyleSheet(self._get_button_style("add"))
        
        # Botões de ação secundários (transparentes/flat)
        flat_style = self._get_flat_button_style()
        self.importar_csv_btn.setStyleSheet(flat_style)
        self.exportar_csv_btn.setStyleSheet(flat_style)
        self.verificar_estoque_btn.setStyleSheet(flat_style)

        # Atualiza ícones para a cor do tema
        self.update_button_icons()

    def set_theme(self, theme_colors):
        """Atualiza as cores do tema e os ícones."""
        self.theme_colors = theme_colors
        self.update_button_icons()
        # Recarrega a tabela para que os ícones internos sejam atualizados
        self.carregar_dados()

    def update_button_icons(self):
        """Atualiza apenas os ícones dos botões."""
        icon_color = self.theme_colors.get('text_color', '#000')

        self.search_button.setIcon(IconManager.get_icon('search', icon_color))
        
        # O botão primário sempre terá um ícone branco
        self.add_button.setIcon(IconManager.get_icon('add', 'white'))
        
        # Os ícones dos botões flat seguem a cor do texto do tema
        self.importar_csv_btn.setIcon(IconManager.get_icon('import', icon_color))
        self.exportar_csv_btn.setIcon(IconManager.get_icon('export', icon_color))
        self.verificar_estoque_btn.setIcon(IconManager.get_icon('check_stock', icon_color))
        
        # Ícones de paginação
        self.prev_page_btn.setIcon(IconManager.get_icon('angle-left', icon_color))
        self.next_page_btn.setIcon(IconManager.get_icon('angle-right', icon_color))
    
    def initUI(self):
        layout = QVBoxLayout(self)
        titulo = QLabel("Cadastro de Fornecedores")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)

        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por empresa, representante ou email...")
        self.search_input.returnPressed.connect(self.pesquisar_fornecedores)
        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar Fornecedor")
        self.search_button.clicked.connect(self.pesquisar_fornecedores)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addWidget(search_group)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels(["ID", "Empresa", "Representante", "Frequência", "Telefone", "Email", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        # Controles de Paginação
        paginacao_layout = QHBoxLayout()
        self.prev_page_btn = QPushButton(IconManager.get_icon('angle-left'), " Anterior")
        self.prev_page_btn.clicked.connect(self.ir_pagina_anterior)
        self.page_label = QLabel(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.next_page_btn = QPushButton(IconManager.get_icon('angle-right'), "Próxima")
        self.next_page_btn.setLayoutDirection(Qt.RightToLeft)
        self.next_page_btn.clicked.connect(self.ir_proxima_pagina)
        paginacao_layout.addWidget(self.prev_page_btn)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.page_label)
        paginacao_layout.addStretch()
        paginacao_layout.addWidget(self.next_page_btn)
        layout.addLayout(paginacao_layout)

        action_layout = QHBoxLayout()
        self.add_button = QPushButton(" Adicionar Fornecedor")
        self.add_button.setObjectName("primaryActionButton")
        self.add_button.clicked.connect(self.abrir_formulario_fornecedor)

        self.importar_csv_btn = QPushButton(" Importar CSV")
        self.importar_csv_btn.clicked.connect(self.importar_csv)

        self.exportar_csv_btn = QPushButton(" Exportar CSV")
        self.exportar_csv_btn.clicked.connect(self.exportar_csv)

        self.verificar_estoque_btn = QPushButton(" Verificar Estoque Baixo")
        self.verificar_estoque_btn.clicked.connect(self.verificar_estoque_baixo)
        
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.importar_csv_btn)
        action_layout.addWidget(self.exportar_csv_btn)
        action_layout.addWidget(self.verificar_estoque_btn)
        layout.addLayout(action_layout)
    
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

    def pesquisar_fornecedores(self):
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()
        
    def atualizar_visualizacao_dados(self):
        """Função central que busca, filtra e pagina os dados."""
        filtros = {'termo_pesquisa': self.search_input.text()}
        
        total_itens = self.db.contar_fornecedores_filtrados(filtros)
        fornecedores = self.db.listar_fornecedores_paginado_e_filtrado(
            filtros, self.pagina_atual, self.itens_por_pagina
        )
        
        self.atualizar_tabela(fornecedores)
        
        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina) or 1
        self.page_label.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.prev_page_btn.setEnabled(self.pagina_atual > 1)
        self.next_page_btn.setEnabled(self.pagina_atual < self.total_paginas)
    
    def atualizar_tabela(self, fornecedores):
        self.tabela.setRowCount(0)
        icon_color = self.theme_colors.get('text_color', '#000')

        for row, fornecedor in enumerate(fornecedores):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(fornecedor['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(fornecedor['empresa']))
            self.tabela.setItem(row, 2, QTableWidgetItem(fornecedor['representante'] or ""))
            self.tabela.setItem(row, 3, QTableWidgetItem(fornecedor['frequencia_compra'] or ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(fornecedor['telefone'] or ""))
            self.tabela.setItem(row, 5, QTableWidgetItem(fornecedor['email'] or ""))

            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(5, 2, 5, 2)
            acoes_layout.setSpacing(5)

            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), " ")
            editar_btn.setToolTip("Editar Fornecedor")
            editar_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            editar_btn.clicked.connect(lambda _, f_id=fornecedor['id']: self.abrir_formulario_fornecedor(f_id))

            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), "")
            excluir_btn.setToolTip("Excluir Fornecedor")
            excluir_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            excluir_btn.clicked.connect(lambda _, f_id=fornecedor['id']: self.excluir_fornecedor(f_id))

            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)

            self.tabela.setCellWidget(row, 6, acoes_widget)
    
    def abrir_formulario_fornecedor(self, fornecedor_id=None):
        dialog = FormularioFornecedor(self.db, fornecedor_id)
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_visualizacao_dados() # Recarrega a view atual

    def excluir_fornecedor(self, fornecedor_id):
        confirmacao = QMessageBox.question(self, "Confirmar Exclusão", "...", QMessageBox.Yes | QMessageBox.No)
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_fornecedor(fornecedor_id):
                QMessageBox.information(self, "Sucesso", "Fornecedor excluído.")
                self.atualizar_visualizacao_dados() # Recarrega a view

    # ... O restante do código de FornecedorWindow permanece o mesmo (importar, exportar, etc.) ...
    def importar_csv(self):
        """Importa fornecedores de um arquivo CSV."""
        arquivo, _ = QFileDialog.getOpenFileName(
            self, 
            "Importar Fornecedores CSV", 
            "", 
            "CSV Files (*.csv)"
        )
        
        if arquivo:
            try:
                with open(arquivo, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    fornecedores_importados = 0
                    
                    for row in reader:
                        # Validar dados obrigatórios
                        if not row.get('empresa', '').strip():
                            continue
                            
                        # Adicionar fornecedor
                        sucesso = self.db.adicionar_fornecedor(
                            empresa=row.get('empresa', '').strip(),
                            representante=row.get('representante', '').strip(),
                            frequencia_compra=row.get('frequencia_compra', '').strip(),
                            telefone=row.get('telefone', '').strip(),
                            email=row.get('email', '').strip(),
                            endereco=row.get('endereco', '').strip(),
                            contato=row.get('contato', '').strip()
                        )
                        
                        if sucesso:
                            fornecedores_importados += 1
                    
                    self.carregar_dados()
                    QMessageBox.information(
                        self, 
                        "Importação Concluída", 
                        f"Importados {fornecedores_importados} fornecedores com sucesso!"
                    )
                    
            except Exception as e:
                QMessageBox.critical(self, "Erro na Importação", f"Erro ao importar CSV: {str(e)}")
    
    def exportar_csv(self):
        """Exporta fornecedores para um arquivo CSV."""
        arquivo, _ = QFileDialog.getSaveFileName(
            self, 
            "Exportar Fornecedores CSV", 
            f"fornecedores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", 
            "CSV Files (*.csv)"
        )
        
        if arquivo:
            try:
                fornecedores = self.db.listar_fornecedores()
                
                with open(arquivo, 'w', newline='', encoding='utf-8') as file:
                    fieldnames = ['empresa', 'representante', 'frequencia_compra', 'telefone', 'email', 'endereco', 'contato']
                    writer = csv.DictWriter(file, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    
                    for fornecedor in fornecedores:
                        writer.writerow({
                            'empresa': fornecedor['empresa'],
                            'representante': fornecedor['representante'] or '',
                            'frequencia_compra': fornecedor['frequencia_compra'] or '',
                            'telefone': fornecedor['telefone'] or '',
                            'email': fornecedor['email'] or '',
                            'endereco': fornecedor['endereco'] or '',
                            'contato': fornecedor['contato'] or ''
                        })
                
                QMessageBox.information(
                    self, 
                    "Exportação Concluída", 
                    f"Fornecedores exportados para: {arquivo}"
                )
                
            except Exception as e:
                QMessageBox.critical(self, "Erro na Exportação", f"Erro ao exportar CSV: {str(e)}")
    
    def verificar_estoque_baixo(self):
        """Verifica produtos com estoque baixo e permite envio de email para fornecedores."""
        produtos_baixo = self.db.verificar_produtos_estoque_baixo()
        
        if not produtos_baixo:
            QMessageBox.information(self, "Estoque OK", "Não há produtos com estoque baixo no momento.")
            return
        
        # Agrupar produtos por fornecedor
        produtos_por_fornecedor = {}
        for produto in produtos_baixo:
            fornecedor_nome = produto['fornecedor_nome'] or 'Sem fornecedor'
            if fornecedor_nome not in produtos_por_fornecedor:
                produtos_por_fornecedor[fornecedor_nome] = []
            produtos_por_fornecedor[fornecedor_nome].append(produto)
        
        # Abrir dialog para envio de emails
        dialog = DialogEstoqueBaixo(self.db, produtos_por_fornecedor)
        dialog.exec_()


class DialogEstoqueBaixo(QDialog):
    def __init__(self, db, produtos_por_fornecedor):
        super().__init__()
        self.db = db
        self.produtos_por_fornecedor = produtos_por_fornecedor
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Produtos com Estoque Baixo")
        self.setFixedSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        titulo = QLabel("Produtos com Estoque Baixo")
        titulo.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(titulo)
        
        self.produtos_text = QTextEdit()
        self.produtos_text.setReadOnly(True)
        
        texto_produtos = ""
        for fornecedor, produtos in self.produtos_por_fornecedor.items():
            texto_produtos += f"\n--- {fornecedor} ---\n"
            for produto in produtos:
                texto_produtos += f"• {produto['nome']} - Estoque: {produto['quantidade']} (Mínimo: {produto['estoque_minimo']})\n"
        
        self.produtos_text.setPlainText(texto_produtos)
        layout.addWidget(self.produtos_text)
        
        email_group = QGroupBox("Configurações de Email")
        email_layout = QFormLayout(email_group)
        
        self.smtp_server = QLineEdit("smtp.gmail.com")
        self.smtp_port = QSpinBox()
        self.smtp_port.setRange(1, 65535)
        self.smtp_port.setValue(587)
        self.email_usuario = QLineEdit()
        self.email_usuario.setPlaceholderText("seu.email@exemplo.com")
        self.email_senha = QLineEdit()
        self.email_senha.setEchoMode(QLineEdit.Password)
        self.email_senha.setPlaceholderText("Sua senha de email ou senha de app")
        
        email_layout.addRow("Servidor SMTP:", self.smtp_server)
        email_layout.addRow("Porta:", self.smtp_port)
        email_layout.addRow("Seu Email:", self.email_usuario)
        email_layout.addRow("Sua Senha:", self.email_senha)
        
        layout.addWidget(email_group)

        button_layout = QHBoxLayout()
        
        self.enviar_emails_btn = QPushButton(IconManager.get_icon('send', 'white'), " Enviar Emails para Fornecedores")
        self.enviar_emails_btn.setObjectName("primaryActionButton")
        self.enviar_emails_btn.clicked.connect(self.enviar_emails)

        self.fechar_btn = QPushButton(IconManager.get_icon('close'), " Fechar")
        self.fechar_btn.clicked.connect(self.accept)

        button_layout.addStretch()
        button_layout.addWidget(self.enviar_emails_btn)
        button_layout.addWidget(self.fechar_btn)

        layout.addLayout(button_layout)
    
    # ... O resto da classe DialogEstoqueBaixo permanece o mesmo ...
    def enviar_emails(self):
        """Envia emails para os fornecedores com produtos em estoque baixo."""
        if not self.email_usuario.text() or not self.email_senha.text():
            QMessageBox.warning(self, "Erro", "Preencha suas credenciais de email!")
            return
        
        progress = QProgressBar()
        progress.setRange(0, len(self.produtos_por_fornecedor))
        progress.setValue(0)
        
        self.layout().addWidget(progress)
        
        try:
            server = smtplib.SMTP(self.smtp_server.text(), self.smtp_port.value())
            server.starttls()
            server.login(self.email_usuario.text(), self.email_senha.text())
            
            emails_enviados = 0
            emails_falharam = 0
            
            for i, (fornecedor_nome, produtos) in enumerate(self.produtos_por_fornecedor.items()):
                fornecedor_email = self.obter_email_fornecedor(fornecedor_nome)
                
                if not fornecedor_email:
                    emails_falharam += 1
                    progress.setValue(i + 1)
                    continue
                
                msg = MIMEMultipart()
                msg['From'] = self.email_usuario.text()
                msg['To'] = fornecedor_email
                msg['Subject'] = f"Solicitação de Reposição de Estoque - {fornecedor_nome}"
                
                corpo = f"""
Prezado(a) {fornecedor_nome},

Espero que esta mensagem o(a) encontre bem.

Gostaríamos de solicitar a reposição dos seguintes produtos que estão com estoque baixo:

"""
                for produto in produtos:
                    corpo += f"• {produto['nome']} - Estoque atual: {produto['quantidade']} unidades (Mínimo: {produto['estoque_minimo']})\n"
                corpo += """
Por favor, entre em contato conosco para confirmar a disponibilidade e prazo de entrega.

Aguardamos seu retorno.

Atenciosamente,
Sistema de Gestão de Estoque
"""
                msg.attach(MIMEText(corpo, 'plain'))
                
                try:
                    text = msg.as_string()
                    server.sendmail(self.email_usuario.text(), fornecedor_email, text)
                    emails_enviados += 1
                except Exception as e:
                    print(f"Erro ao enviar email para {fornecedor_nome}: {e}")
                    emails_falharam += 1
                
                progress.setValue(i + 1)
            
            server.quit()
            
            self.layout().removeWidget(progress)
            progress.deleteLater()
            
            QMessageBox.information(
                self, 
                "Envio Concluído", 
                f"Emails enviados: {emails_enviados}\nEmails falharam: {emails_falharam}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao enviar emails: {str(e)}")
            try:
                self.layout().removeWidget(progress)
                progress.deleteLater()
            except:
                pass
    
    def obter_email_fornecedor(self, fornecedor_nome):
        """Obtém o email do fornecedor pelo nome da empresa."""
        try:
            fornecedores = self.db.listar_fornecedores()
            for fornecedor in fornecedores:
                if fornecedor['empresa'] == fornecedor_nome:
                    return fornecedor['email']
            return None
        except:
            return None


class FormularioFornecedor(QDialog):
    def __init__(self, db, fornecedor_id=None):
        super().__init__()
        self.db = db
        self.fornecedor_id = fornecedor_id
        self.fornecedor = None
        
        if fornecedor_id:
            self.fornecedor = self.db.obter_fornecedor(fornecedor_id)
            if not self.fornecedor:
                QMessageBox.warning(self, "Erro", "Fornecedor não encontrado!")
                self.reject()
        
        self.initUI()
        
        if self.fornecedor:
            self.carregar_dados_fornecedor()
    
    def initUI(self):
        self.setWindowTitle("Cadastro de Fornecedor")
        self.setFixedWidth(500)

        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Dados do Fornecedor")
        form_layout = QFormLayout(form_group)

        self.empresa_input = QLineEdit()
        self.representante_input = QLineEdit()
        self.frequencia_input = QComboBox()
        self.frequencia_input.addItems(["", "Alta", "Média", "Baixa"])
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        self.contato_input = QLineEdit()

        form_layout.addRow("Empresa (*):", self.empresa_input)
        form_layout.addRow("Representante:", self.representante_input)
        form_layout.addRow("Frequência de Compra:", self.frequencia_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Endereço:", self.endereco_input)
        form_layout.addRow("Contato:", self.contato_input)
        layout.addWidget(form_group)

        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton(IconManager.get_icon('save', 'white'), " Salvar")
        self.salvar_btn.setObjectName("primaryActionButton")
        self.salvar_btn.clicked.connect(self.salvar_fornecedor)

        self.cancelar_btn = QPushButton(IconManager.get_icon('cancel'), " Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        layout.addLayout(button_layout)
    
    # ... O resto da classe FormularioFornecedor permanece o mesmo ...
    def carregar_dados_fornecedor(self):
        """Carrega os dados do fornecedor nos campos do formulário."""
        self.empresa_input.setText(self.fornecedor['empresa'])
        self.representante_input.setText(self.fornecedor['representante'] or "")
        
        frequencia = self.fornecedor['frequencia_compra']
        if frequencia:
            index = self.frequencia_input.findText(frequencia, Qt.MatchFixedString)
            if index >= 0:
                self.frequencia_input.setCurrentIndex(index)
        
        self.telefone_input.setText(self.fornecedor['telefone'] or "")
        self.email_input.setText(self.fornecedor['email'] or "")
        self.endereco_input.setText(self.fornecedor['endereco'] or "")
        self.contato_input.setText(self.fornecedor['contato'] or "")
    
    def salvar_fornecedor(self):
        """Salva os dados do fornecedor no banco de dados."""
        if not self.empresa_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome da empresa é obrigatório!")
            return
        
        empresa = self.empresa_input.text().strip()
        representante = self.representante_input.text().strip()
        frequencia_compra = self.frequencia_input.currentText()
        telefone = self.telefone_input.text().strip()
        email = self.email_input.text().strip()
        endereco = self.endereco_input.text().strip()
        contato = self.contato_input.text().strip()
        
        try:
            if self.fornecedor_id:
                sucesso = self.db.atualizar_fornecedor(
                    self.fornecedor_id, empresa, representante, frequencia_compra, telefone, email, endereco, contato
                )
                mensagem = "Fornecedor atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_fornecedor(
                    empresa, representante, frequencia_compra, telefone, email, endereco, contato
                )
                mensagem = "Fornecedor cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o fornecedor.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar fornecedor: {str(e)}")