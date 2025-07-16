from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame, QDateEdit, QFileDialog, QGroupBox, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime
import csv
import os
from ui.icon_manager import IconManager


class ClientesWindow(QWidget):
    def __init__(self, db, theme_colors):
        super().__init__()
        self.db = db
        self.theme_colors = theme_colors  # Adiciona suporte a temas
        self.initUI()
        self.carregar_dados()

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
        """Atualiza as cores do tema e os ícones quando o tema principal muda."""
        self.theme_colors = theme_colors
        self.update_button_icons()
        # Recarregar os dados para que os ícones na tabela também sejam atualizados
        self.carregar_dados()

    def update_button_icons(self):
        """Define ou atualiza os ícones de todos os botões com base no tema atual."""
        icon_color = self.theme_colors.get('text_color', '#000')

        self.search_button.setIcon(IconManager.get_icon('search', icon_color))
        self.importar_csv_button.setIcon(IconManager.get_icon('import', icon_color))
        self.exportar_csv_button.setIcon(IconManager.get_icon('export', icon_color))

        # Botão de ação primária sempre terá ícone branco para bom contraste
        self.add_button.setIcon(IconManager.get_icon('add', 'white'))

    def initUI(self):
        """Inicializa a interface do usuário da janela."""
        layout = QVBoxLayout(self)

        titulo = QLabel("Gerenciamento de Clientes")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)

        # --- Área de Pesquisa ---
        search_group = QGroupBox("Pesquisa")
        search_layout = QHBoxLayout(search_group)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar cliente por nome, telefone ou email...")
        self.search_button = QPushButton()
        self.search_button.setToolTip("Buscar")
        self.search_button.clicked.connect(self.pesquisar_clientes)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addWidget(search_group)

        # --- Tabela de Clientes ---
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Nascimento (Idade)", "Telefone", "Email", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)

        # --- Botões de Ação Principais ---
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        botoes_acao = []
        
        self.add_button = QPushButton(" Adicionar Cliente")
        self.add_button.setObjectName("primaryActionButton") # Para estilo especial do tema
        self.add_button.clicked.connect(self.abrir_formulario_cliente)
        botoes_acao.append(self.add_button)

        self.importar_csv_button = QPushButton(" Importar CSV")
        self.importar_csv_button.clicked.connect(self.importar_csv)
        botoes_acao.append(self.importar_csv_button)
        
        self.exportar_csv_button = QPushButton(" Exportar CSV")
        self.exportar_csv_button.clicked.connect(self.exportar_csv)
        botoes_acao.append(self.exportar_csv_button)

        # Aplica política de expansão para preencher a largura
        for btn in botoes_acao:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            action_layout.addWidget(btn)

        layout.addLayout(action_layout)
        
        # Define os ícones pela primeira vez
        self.update_button_icons()
    
    def carregar_dados(self):
        """Busca os clientes do banco de dados e atualiza a tabela."""
        clientes = self.db.listar_clientes()
        self.atualizar_tabela(clientes)

    def pesquisar_clientes(self):
        """Filtra os clientes com base no termo de pesquisa."""
        termo = self.search_input.text()
        clientes = self.db.listar_clientes(filtro=termo) if termo else self.db.listar_clientes()
        self.atualizar_tabela(clientes)

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
        dialog = FormularioCliente(self.db, cliente_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_cliente(self, cliente_id):
        confirmacao = QMessageBox.question(
            self, "Confirmar Exclusão", "Tem certeza que deseja excluir este cliente?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_cliente(cliente_id):
                QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso!")
                self.carregar_dados()
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
        try:
            arquivo, _ = QFileDialog.getOpenFileName(
                self, "Selecionar arquivo CSV", "", "Arquivos CSV (*.csv);;Todos os arquivos (*)"
            )
            if not arquivo: return
            if not os.path.exists(arquivo):
                QMessageBox.warning(self, "Erro", "Arquivo não encontrado.")
                return
            
            clientes_importados, erros = [], []
            
            with open(arquivo, 'r', encoding='utf-8') as csvfile:
                sample = csvfile.read(1024)
                csvfile.seek(0)
                delimiter = csv.Sniffer().sniff(sample).delimiter
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for linha_num, row in enumerate(reader, start=2):
                    try:
                        nome = row.get('nome', '').strip()
                        if not nome:
                            erros.append(f"Linha {linha_num}: Nome é obrigatório")
                            continue
                        
                        data_nascimento = row.get('data_nascimento', '').strip()
                        if data_nascimento:
                            try:
                                data_obj = datetime.strptime(data_nascimento, '%d/%m/%Y')
                                data_nascimento = data_obj.strftime('%Y-%m-%d')
                            except ValueError:
                                try:
                                    datetime.strptime(data_nascimento, '%Y-%m-%d')
                                except ValueError:
                                    erros.append(f"Linha {linha_num}: Data de nascimento inválida ({data_nascimento})")
                                    continue
                        
                        clientes_importados.append({
                            'nome': nome, 'data_nascimento': data_nascimento,
                            'telefone': row.get('telefone', '').strip(),
                            'email': row.get('email', '').strip(),
                            'endereco': row.get('endereco', '').strip()
                        })
                    except Exception as e:
                        erros.append(f"Linha {linha_num}: Erro ao processar - {str(e)}")
            
            if clientes_importados:
                mensagem = f"Encontrados {len(clientes_importados)} clientes válidos para importar."
                if erros: mensagem += f"\n{len(erros)} linha(s) com erro(s) serão ignoradas."
                mensagem += "\n\nDeseja continuar com a importação?"
                
                resposta = QMessageBox.question(self, "Confirmar Importação", mensagem, QMessageBox.Yes | QMessageBox.No)
                
                if resposta == QMessageBox.Yes:
                    importados_com_sucesso = 0
                    for cliente in clientes_importados:
                        try:
                            if self.db.adicionar_cliente(cliente['nome'], cliente['data_nascimento'], cliente['telefone'], cliente['email'], cliente['endereco']):
                                importados_com_sucesso += 1
                        except Exception as e:
                            erros.append(f"Erro ao salvar {cliente['nome']}: {str(e)}")
                    
                    self.carregar_dados()
                    
                    resultado = f"Importação concluída!\nClientes importados: {importados_com_sucesso}\n"
                    if erros:
                        resultado += f"Erros: {len(erros)}\n\nPrimeiros 5 erros:\n" + "\n".join(erros[:5])
                        if len(erros) > 5: resultado += f"\n... e mais {len(erros) - 5} erro(s)."
                    QMessageBox.information(self, "Resultado da Importação", resultado)
            else:
                mensagem = "Nenhum cliente válido encontrado no arquivo."
                if erros: mensagem += f"\n\nErros encontrados:\n" + "\n".join(erros[:10])
                QMessageBox.warning(self, "Aviso", mensagem)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao importar CSV: {str(e)}")


class FormularioCliente(QDialog):
    def __init__(self, db, cliente_id=None):
        super().__init__()
        self.db = db
        self.cliente_id = cliente_id
        self.cliente = None
        
        if cliente_id:
            self.cliente = self.db.obter_cliente(cliente_id)
            if not self.cliente:
                QMessageBox.warning(self, "Erro", "Cliente não encontrado!")
                self.reject()
        
        self.initUI()
        
        if self.cliente:
            self.carregar_dados_cliente()
    
    def initUI(self):
        self.setWindowTitle("Cadastro de Cliente")
        self.setFixedWidth(500)
        layout = QVBoxLayout(self)
        
        form_group = QGroupBox("Dados do Cliente")
        form_layout = QFormLayout(form_group)
        
        self.nome_input = QLineEdit()
        self.data_nascimento_input = QDateEdit(calendarPopup=True, date=QDate.currentDate().addYears(-18))
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
        self.salvar_btn = QPushButton(IconManager.get_icon('save', 'white'), " Salvar")
        self.salvar_btn.setObjectName("primaryActionButton")
        self.salvar_btn.clicked.connect(self.salvar_cliente)
        
        self.cancelar_btn = QPushButton(IconManager.get_icon('cancel'), " Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        layout.addLayout(button_layout)

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