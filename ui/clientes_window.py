from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame, QDateEdit, QFileDialog, 
                           QGroupBox, QSizePolicy, QProgressDialog)
from PyQt5.QtCore import Qt, QDate, QThread, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import datetime
import csv
import os
import math

# Importações necessárias
from ui.icon_manager import IconManager
from database.db_manager import DatabaseManager

# ================================================================= #
#       CLASSE WORKER PARA IMPORTAÇÃO DE CSV EM THREAD              #
# ================================================================= #

class ClienteCsvImportWorker(QThread):
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
                        nome = row.get('nome', '').strip()
                        if not nome:
                            raise ValueError("Nome do cliente é obrigatório.")
                        
                        data_nascimento = row.get('data_nascimento')
                        if data_nascimento:
                             try:
                                data_nascimento = datetime.strptime(data_nascimento, '%d/%m/%Y').strftime('%Y-%m-%d')
                             except ValueError:
                                # Tenta o formato ISO se o primeiro falhar
                                datetime.strptime(data_nascimento, '%Y-%m-%d')

                        self.local_db.adicionar_cliente(
                            nome=nome,
                            data_nascimento=data_nascimento,
                            telefone=row.get('telefone', '').strip(),
                            email=row.get('email', '').strip(),
                            endereco=row.get('endereco', '').strip()
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


class ClientesWindow(QWidget):
    dados_clientes_alterados = pyqtSignal()

    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors
        self.pagina_atual = 1
        self.itens_por_pagina = 50
        self.total_paginas = 1
        
        self.initUI()
        self.atualizar_visualizacao_dados()

    # NOVO MÉTODO: Centraliza a estilização dos botões
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
        """Atualiza as cores do tema e os ícones."""
        self.theme_colors = theme_colors
        self.update_button_icons()
        self.atualizar_visualizacao_dados() # Recarrega a tabela para atualizar ícones internos

    def update_button_icons(self):
        """Define ou atualiza os ícones de todos os botões com base no tema."""
        # Se você quer que os ícones dos botões secundários também mudem de cor com o tema
        icon_color = self.theme_colors.get('text_color', '#000') 
        
        self.search_button.setIcon(IconManager.get_icon('search', icon_color))
        
        # O botão primário sempre terá ícone branco para contrastar
        self.add_button.setIcon(IconManager.get_icon('add', 'white'))
        
        # Botões secundários
        self.importar_csv_button.setIcon(IconManager.get_icon('import', icon_color))
        self.exportar_csv_button.setIcon(IconManager.get_icon('export', icon_color))
        
        # Botões de paginação
        self.prev_page_btn.setIcon(IconManager.get_icon('angle-left', icon_color))
        self.next_page_btn.setIcon(IconManager.get_icon('angle-right', icon_color))

    def initUI(self):
        layout = QVBoxLayout(self)
        titulo = QLabel("Gerenciamento de Clientes")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)

        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar cliente por nome, telefone ou email...")
        self.search_input.returnPressed.connect(self.pesquisar_clientes)
        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar")
        self.search_button.clicked.connect(self.pesquisar_clientes)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addWidget(search_group)

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Nascimento (Idade)", "Telefone", "Email", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

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
        self.add_button = QPushButton(" Adicionar Cliente")
        self.add_button.setObjectName("primaryActionButton")
        self.add_button.clicked.connect(self.abrir_formulario_cliente)
        self.importar_csv_button = QPushButton(" Importar CSV")
        self.importar_csv_button.clicked.connect(self.importar_csv)
        self.exportar_csv_button = QPushButton(" Exportar CSV")
        self.exportar_csv_button.clicked.connect(self.exportar_csv)
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.importar_csv_button)
        action_layout.addWidget(self.exportar_csv_button)
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
    
    def pesquisar_clientes(self):
        self.pagina_atual = 1
        self.atualizar_visualizacao_dados()

    def atualizar_visualizacao_dados(self):
        filtros = {'termo_pesquisa': self.search_input.text()}
        total_itens = self.db.contar_clientes_filtrados(filtros)
        clientes = self.db.listar_clientes_paginado_e_filtrado(
            filtros, self.pagina_atual, self.itens_por_pagina
        )
        self.atualizar_tabela(clientes)
        self.total_paginas = math.ceil(total_itens / self.itens_por_pagina) or 1
        self.page_label.setText(f"Página {self.pagina_atual} de {self.total_paginas}")
        self.prev_page_btn.setEnabled(self.pagina_atual > 1)
        self.next_page_btn.setEnabled(self.pagina_atual < self.total_paginas)

    def formatar_data_nascimento(self, data_nascimento):
        """Formata a data e calcula a idade."""
        if not data_nascimento: return ""
        try:
            data = datetime.strptime(str(data_nascimento), '%Y-%m-%d')
            hoje = datetime.now()
            idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
            return f"{data.strftime('%d/%m/%Y')} ({idade} anos)"
        except (ValueError, TypeError):
            return str(data_nascimento)
    
    def atualizar_tabela(self, clientes):
        """Preenche a tabela com a lista de clientes fornecida."""
        self.tabela.setRowCount(0)
        icon_color = self.theme_colors.get('text_color', '#000')
        
        for row, cliente in enumerate(clientes):
            self.tabela.insertRow(row)
            self.tabela.setItem(row, 0, QTableWidgetItem(str(cliente['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(self.formatar_data_nascimento(cliente['data_nascimento'])))
            self.tabela.setItem(row, 3, QTableWidgetItem(cliente['telefone'] or ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(cliente['email'] or ""))
            
            # Botões de ação dentro da tabela
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(5, 2, 5, 2)
            acoes_layout.setSpacing(5)
            
            editar_btn = QPushButton(IconManager.get_icon('edit', icon_color), " ")
            editar_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            editar_btn.clicked.connect(lambda _, c_id=cliente['id']: self.abrir_formulario_cliente(c_id))
            
            excluir_btn = QPushButton(IconManager.get_icon('delete', icon_color), " ")
            excluir_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Ignored)
            excluir_btn.clicked.connect(lambda _, c_id=cliente['id']: self.excluir_cliente(c_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            self.tabela.setCellWidget(row, 5, acoes_widget)
            
    # ... O restante do código (abrir formulário, excluir, importar, exportar) permanece o mesmo ...
    def abrir_formulario_cliente(self, cliente_id=None):
        # Passe self.theme_colors e self (parent) para o diálogo
        dialog = FormularioCliente(self.db, self.theme_colors, cliente_id, self)
        
        # O resto do método continua o mesmo
        if dialog.exec_() == QDialog.Accepted:
            self.atualizar_visualizacao_dados()
            print("DEBUG: Formulário fechado com sucesso. Emitindo sinal 'dados_clientes_alterados'.")
            self.dados_clientes_alterados.emit()

    def excluir_cliente(self, cliente_id):
        confirmacao = QMessageBox.question(
            self, "Confirmar Exclusão", "Tem certeza que deseja excluir este cliente?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_cliente(cliente_id):
                QMessageBox.information(self, "Sucesso", "Cliente excluído.")
                self.atualizar_visualizacao_dados()
                
                # <<< EMITA O SINAL AQUI TAMBÉM! >>>
                print("DEBUG: Cliente excluído. Emitindo sinal 'dados_clientes_alterados'.")
                self.dados_clientes_alterados.emit()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir o cliente.")
    
    def exportar_csv(self):
        try:
            arquivo, _ = QFileDialog.getSaveFileName(
                self, "Salvar arquivo CSV", "clientes.csv",
                "Arquivos CSV (*.csv);;Todos os arquivos (*)"
            )
            if not arquivo: return
            
            clientes = self.db.listar_clientes()
            if not clientes:
                QMessageBox.warning(self, "Aviso", "Não há clientes para exportar.")
                return
            
            with open(arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'nome', 'data_nascimento', 'telefone', 'email', 'endereco']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for cliente in clientes:
                    writer.writerow({
                        'id': cliente['id'], 'nome': cliente['nome'],
                        'data_nascimento': cliente['data_nascimento'],
                        'telefone': cliente['telefone'] or '', 'email': cliente['email'] or '',
                        'endereco': cliente['endereco'] or ''
                    })
            
            QMessageBox.information(
                self, "Sucesso", 
                f"Dados exportados com sucesso!\nArquivo: {arquivo}\nTotal de clientes: {len(clientes)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar CSV: {str(e)}")
    
    def importar_csv(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Importar Clientes CSV", "", "CSV Files (*.csv)")
        if not file_path: return

        self.progress_dialog = QProgressDialog("Importando clientes...", "Cancelar", 0, 100, self)
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        
        self.import_thread = ClienteCsvImportWorker(self.db.db_path, file_path)
        self.import_thread.progress.connect(self.progress_dialog.setValue)
        self.import_thread.finished.connect(self.importacao_concluida)
        self.progress_dialog.canceled.connect(self.import_thread.terminate)
        self.import_thread.start()
        self.progress_dialog.exec_()

    def importacao_concluida(self, importados, erros, detalhes):
        self.progress_dialog.close()
        self.atualizar_visualizacao_dados()

        # <<< EMITA O SINAL SE PELO MENOS UM CLIENTE FOI IMPORTADO >>>
        if importados > 0:
            print("DEBUG: Importação CSV concluída. Emitindo sinal 'dados_clientes_alterados'.")
            self.dados_clientes_alterados.emit()

        msg = f"Importação concluída!\n\nSucesso: {importados}\nFalhas: {erros}"
        if erros > 0:
            msg += "\n\nPrimeiros erros:\n" + "\n".join(detalhes[:5])
            QMessageBox.warning(self, "Importação com Erros", msg)
        else:
            QMessageBox.information(self, "Importação Concluída", msg)


class FormularioCliente(QDialog):
    # 1. Construtor modificado para aceitar theme_colors
    def __init__(self, db, theme_colors, cliente_id=None, parent=None):
        super().__init__(parent)
        self.db = db
        self.theme_colors = theme_colors # Armazena o tema
        self.cliente_id = cliente_id
        self.cliente = None
        
        if cliente_id:
            self.cliente = self.db.obter_cliente(cliente_id)
            if not self.cliente:
                QMessageBox.warning(self, "Erro", "Cliente não encontrado!")
                self.reject()
        
        self.initUI()
        self.apply_styles() # 2. Aplica os estilos do tema
        
        if self.cliente:
            self.carregar_dados_cliente()
    
    def initUI(self):
        self.setWindowTitle("Cadastro de Cliente")
        self.setFixedWidth(500)
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Dados do Cliente")
        form_layout = QFormLayout(form_group)
        
        self.nome_input = QLineEdit()
        self.data_nascimento_input = QDateEdit(calendarPopup=True)
        # Define uma data inicial padrão mais realista
        self.data_nascimento_input.setDate(QDate.currentDate().addYears(-18))
        self.data_nascimento_input.setDisplayFormat("dd/MM/yyyy")

        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        
        form_layout.addRow("Nome (*):", self.nome_input)
        form_layout.addRow("Data de Nascimento:", self.data_nascimento_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Endereço:", self.endereco_input)
        layout.addWidget(form_group)
        
        button_layout = QHBoxLayout()
        # 3. Ícones agora usam as cores do tema
        self.salvar_btn = QPushButton(IconManager.get_icon('save', 'white'), " Salvar")
        self.salvar_btn.setObjectName("primaryButton")
        self.salvar_btn.clicked.connect(self.salvar_cliente)
        
        self.cancelar_btn = QPushButton(IconManager.get_icon('cancel', self.theme_colors['text_color']), " Cancelar")
        self.cancelar_btn.setObjectName("secondaryButton")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancelar_btn)
        button_layout.addWidget(self.salvar_btn)
        layout.addLayout(button_layout)

    # 4. NOVO MÉTODO para aplicar o estilo do tema
    def apply_styles(self):
        colors = self.theme_colors
        # Reutilizamos o mesmo estilo do formulário de fornecedor para manter a consistência
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {colors['bg_color']};
            }}
            QGroupBox {{
                font-weight: bold;
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                border-radius: 6px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }}
            QLabel, QDateEdit {{
                color: {colors['text_color']};
            }}
            QLineEdit, QDateEdit {{
                background-color: {colors['surface_color']};
                border: 1px solid {colors['border_color']};
                padding: 6px;
                border-radius: 4px;
            }}
            QLineEdit:focus, QDateEdit:focus {{
                border: 1px solid {colors['accent_color']};
            }}
            QDateEdit::down-arrow {{
                /* Você pode adicionar um ícone de seta aqui se desejar */
                width: 16px;
                height: 16px;
            }}
            QCalendarWidget QWidget {{
                alternate-background-color: {colors['button_hover']};
            }}
            #qt_calendar_navigationbar {{
                background-color: {colors['surface_color']};
            }}
            /* Botão Primário (Salvar) */
            #primaryButton {{
                background-color: {colors['accent_color']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            #primaryButton:hover {{
                background-color: #005bb5;
            }}
            /* Botão Secundário (Cancelar) */
            #secondaryButton {{
                background-color: {colors['surface_color']};
                color: {colors['text_color']};
                border: 1px solid {colors['border_color']};
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }}
            #secondaryButton:hover {{
                border-color: {colors['accent_color']};
            }}
        """)

    def carregar_dados_cliente(self):
        self.nome_input.setText(self.cliente['nome'])
        if self.cliente['data_nascimento']:
            try:
                data = datetime.strptime(str(self.cliente['data_nascimento']), '%Y-%m-%d')
                self.data_nascimento_input.setDate(QDate(data.year, data.month, data.day))
            except (ValueError, TypeError): pass
        self.telefone_input.setText(self.cliente['telefone'] or "")
        self.email_input.setText(self.cliente['email'] or "")
        self.endereco_input.setText(self.cliente['endereco'] or "")

    def salvar_cliente(self):
        nome = self.nome_input.text().strip()
        if not nome:
            QMessageBox.warning(self, "Erro", "O nome do cliente é obrigatório!")
            return
        
        data_nascimento = self.data_nascimento_input.date().toString("yyyy-MM-dd")
        telefone = self.telefone_input.text().strip()
        email = self.email_input.text().strip()
        endereco = self.endereco_input.text().strip()
        
        try:
            if self.cliente_id:
                sucesso = self.db.atualizar_cliente(self.cliente_id, nome, data_nascimento, telefone, email, endereco)
                mensagem = "Cliente atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_cliente(nome, data_nascimento, telefone, email, endereco)
                mensagem = "Cliente cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o cliente.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cliente: {str(e)}")