from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                           QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                           QMessageBox, QHeaderView, QDialog, QFrame, QDateEdit, QFileDialog)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from datetime import datetime
import csv
import os

class ClientesWindow(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.initUI()
        self.carregar_dados()
    
    def initUI(self):
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Título da página
        titulo = QLabel("Cadastro de Clientes")
        titulo.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(titulo)
        
        # Área de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar cliente...")
        self.search_button = QPushButton("Buscar")
        self.search_button.clicked.connect(self.pesquisar_clientes)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # Tabela de clientes
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Data Nascimento", "Telefone", 
                                              "Email", "Ações"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.verticalHeader().setVisible(False)
        layout.addWidget(self.tabela)
        
        # Botões de ação
        action_layout = QHBoxLayout()
        self.add_button = QPushButton("Adicionar Cliente")
        self.add_button.clicked.connect(self.abrir_formulario_cliente)
        
        # Botões de Import/Export
        self.importar_csv_button = QPushButton("Importar CSV")
        self.importar_csv_button.clicked.connect(self.importar_csv)
        
        self.exportar_csv_button = QPushButton("Exportar CSV")
        self.exportar_csv_button.clicked.connect(self.exportar_csv)
        
        action_layout.addWidget(self.add_button)
        action_layout.addWidget(self.importar_csv_button)
        action_layout.addWidget(self.exportar_csv_button)
        layout.addLayout(action_layout)
    
    def carregar_dados(self):
        """Carrega os clientes do banco de dados para a tabela."""
        clientes = self.db.listar_clientes()
        self.atualizar_tabela(clientes)
    
    def pesquisar_clientes(self):
        """Pesquisa clientes pelo termo digitado."""
        termo = self.search_input.text()
        if termo:
            clientes = self.db.listar_clientes(filtro=termo)
        else:
            clientes = self.db.listar_clientes()
        
        self.atualizar_tabela(clientes)
    
    def formatar_data_nascimento(self, data_nascimento):
        """Formata a data de nascimento para exibição."""
        if not data_nascimento:
            return ""
        
        try:
            # Se for string, converter para datetime
            if isinstance(data_nascimento, str):
                data = datetime.strptime(data_nascimento, '%Y-%m-%d')
            else:
                data = data_nascimento
            
            # Calcular idade
            hoje = datetime.now()
            idade = hoje.year - data.year - ((hoje.month, hoje.day) < (data.month, data.day))
            
            return f"{data.strftime('%d/%m/%Y')} ({idade} anos)"
        except:
            return str(data_nascimento)
    
    def atualizar_tabela(self, clientes):
        """Atualiza a tabela com os clientes fornecidos."""
        self.tabela.setRowCount(0)
        
        for row, cliente in enumerate(clientes):
            self.tabela.insertRow(row)
            
            # Adicionar dados às células
            self.tabela.setItem(row, 0, QTableWidgetItem(str(cliente['id'])))
            self.tabela.setItem(row, 1, QTableWidgetItem(cliente['nome']))
            self.tabela.setItem(row, 2, QTableWidgetItem(self.formatar_data_nascimento(cliente['data_nascimento'])))
            self.tabela.setItem(row, 3, QTableWidgetItem(cliente['telefone'] or ""))
            self.tabela.setItem(row, 4, QTableWidgetItem(cliente['email'] or ""))
            
            # Botões de ação
            acoes_widget = QWidget()
            acoes_layout = QHBoxLayout(acoes_widget)
            acoes_layout.setContentsMargins(0, 0, 0, 0)
            
            editar_btn = QPushButton("Editar")
            editar_btn.clicked.connect(lambda _, c_id=cliente['id']: self.abrir_formulario_cliente(c_id))
            
            excluir_btn = QPushButton("Excluir")
            excluir_btn.clicked.connect(lambda _, c_id=cliente['id']: self.excluir_cliente(c_id))
            
            acoes_layout.addWidget(editar_btn)
            acoes_layout.addWidget(excluir_btn)
            
            self.tabela.setCellWidget(row, 5, acoes_widget)
    
    def abrir_formulario_cliente(self, cliente_id=None):
        """Abre o formulário para adicionar ou editar um cliente."""
        dialog = FormularioCliente(self.db, cliente_id)
        if dialog.exec_() == QDialog.Accepted:
            self.carregar_dados()
    
    def excluir_cliente(self, cliente_id):
        """Exclui um cliente após confirmação."""
        confirmacao = QMessageBox.question(
            self, 
            "Confirmar Exclusão",
            "Tem certeza que deseja excluir este cliente?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirmacao == QMessageBox.Yes:
            if self.db.excluir_cliente(cliente_id):
                QMessageBox.information(self, "Sucesso", "Cliente excluído com sucesso!")
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível excluir o cliente.")
    
    def exportar_csv(self):
        """Exporta os clientes para um arquivo CSV."""
        try:
            # Solicitar local para salvar o arquivo
            arquivo, _ = QFileDialog.getSaveFileName(
                self,
                "Salvar arquivo CSV",
                "clientes.csv",
                "Arquivos CSV (*.csv);;Todos os arquivos (*)"
            )
            
            if not arquivo:
                return
            
            # Obter dados dos clientes
            clientes = self.db.listar_clientes()
            
            if not clientes:
                QMessageBox.warning(self, "Aviso", "Não há clientes para exportar.")
                return
            
            # Escrever no arquivo CSV
            with open(arquivo, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'nome', 'data_nascimento', 'telefone', 'email', 'endereco']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Escrever cabeçalho
                writer.writeheader()
                
                # Escrever dados dos clientes
                for cliente in clientes:
                    writer.writerow({
                        'id': cliente['id'],
                        'nome': cliente['nome'],
                        'data_nascimento': cliente['data_nascimento'],
                        'telefone': cliente['telefone'] or '',
                        'email': cliente['email'] or '',
                        'endereco': cliente['endereco'] or ''
                    })
            
            QMessageBox.information(
                self, 
                "Sucesso", 
                f"Dados exportados com sucesso!\nArquivo: {arquivo}\nTotal de clientes: {len(clientes)}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao exportar CSV: {str(e)}")
    
    def importar_csv(self):
        """Importa clientes de um arquivo CSV."""
        try:
            # Solicitar arquivo CSV
            arquivo, _ = QFileDialog.getOpenFileName(
                self,
                "Selecionar arquivo CSV",
                "",
                "Arquivos CSV (*.csv);;Todos os arquivos (*)"
            )
            
            if not arquivo:
                return
            
            # Verificar se o arquivo existe
            if not os.path.exists(arquivo):
                QMessageBox.warning(self, "Erro", "Arquivo não encontrado.")
                return
            
            # Ler arquivo CSV
            clientes_importados = []
            erros = []
            
            with open(arquivo, 'r', encoding='utf-8') as csvfile:
                # Detectar delimitador
                sample = csvfile.read(1024)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter
                
                reader = csv.DictReader(csvfile, delimiter=delimiter)
                
                for linha_num, row in enumerate(reader, start=2):  # Start=2 porque linha 1 é cabeçalho
                    try:
                        # Validar campos obrigatórios
                        nome = row.get('nome', '').strip()
                        if not nome:
                            erros.append(f"Linha {linha_num}: Nome é obrigatório")
                            continue
                        
                        # Processar data de nascimento
                        data_nascimento = row.get('data_nascimento', '').strip()
                        if data_nascimento:
                            # Tentar diferentes formatos de data
                            try:
                                # Formato YYYY-MM-DD
                                datetime.strptime(data_nascimento, '%Y-%m-%d')
                            except ValueError:
                                try:
                                    # Formato DD/MM/YYYY - converter para YYYY-MM-DD
                                    data_obj = datetime.strptime(data_nascimento, '%d/%m/%Y')
                                    data_nascimento = data_obj.strftime('%Y-%m-%d')
                                except ValueError:
                                    erros.append(f"Linha {linha_num}: Data de nascimento inválida ({data_nascimento})")
                                    continue
                        
                        telefone = row.get('telefone', '').strip()
                        email = row.get('email', '').strip()
                        endereco = row.get('endereco', '').strip()
                        
                        clientes_importados.append({
                            'nome': nome,
                            'data_nascimento': data_nascimento,
                            'telefone': telefone,
                            'email': email,
                            'endereco': endereco
                        })
                        
                    except Exception as e:
                        erros.append(f"Linha {linha_num}: Erro ao processar - {str(e)}")
            
            # Confirmar importação
            if clientes_importados:
                mensagem = f"Encontrados {len(clientes_importados)} clientes válidos para importar."
                if erros:
                    mensagem += f"\n{len(erros)} linha(s) com erro(s) serão ignoradas."
                
                mensagem += "\n\nDeseja continuar com a importação?"
                
                resposta = QMessageBox.question(
                    self,
                    "Confirmar Importação",
                    mensagem,
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if resposta == QMessageBox.Yes:
                    # Importar clientes
                    importados_com_sucesso = 0
                    for cliente in clientes_importados:
                        try:
                            if self.db.adicionar_cliente(
                                cliente['nome'],
                                cliente['data_nascimento'],
                                cliente['telefone'],
                                cliente['email'],
                                cliente['endereco']
                            ):
                                importados_com_sucesso += 1
                        except Exception as e:
                            erros.append(f"Erro ao salvar {cliente['nome']}: {str(e)}")
                    
                    # Atualizar tabela
                    self.carregar_dados()
                    
                    # Mostrar resultado
                    resultado = f"Importação concluída!\n"
                    resultado += f"Clientes importados com sucesso: {importados_com_sucesso}\n"
                    
                    if erros:
                        resultado += f"Erros encontrados: {len(erros)}\n\n"
                        resultado += "Primeiros 5 erros:\n"
                        resultado += "\n".join(erros[:5])
                        if len(erros) > 5:
                            resultado += f"\n... e mais {len(erros) - 5} erro(s)."
                    
                    QMessageBox.information(self, "Resultado da Importação", resultado)
            else:
                mensagem = "Nenhum cliente válido encontrado no arquivo."
                if erros:
                    mensagem += f"\n\nErros encontrados:\n"
                    mensagem += "\n".join(erros[:10])  # Mostrar até 10 erros
                
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
        # Configurar janela
        self.setWindowTitle("Cadastro de Cliente")
        self.setFixedWidth(500)
        
        # Layout principal
        layout = QVBoxLayout(self)
        
        # Formulário
        form_layout = QFormLayout()
        
        # Campos do formulário
        self.nome_input = QLineEdit()
        
        # Campo de data de nascimento
        self.data_nascimento_input = QDateEdit()
        self.data_nascimento_input.setCalendarPopup(True)
        self.data_nascimento_input.setDate(QDate.currentDate().addYears(-18))  # Data padrão: 18 anos atrás
        self.data_nascimento_input.setDisplayFormat("dd/MM/yyyy")
        
        self.telefone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.endereco_input = QLineEdit()
        
        # Adicionar campos ao formulário
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Data de Nascimento:", self.data_nascimento_input)
        form_layout.addRow("Telefone:", self.telefone_input)
        form_layout.addRow("Email:", self.email_input)
        form_layout.addRow("Endereço:", self.endereco_input)
        
        layout.addLayout(form_layout)
        
        # Separador
        separador = QFrame()
        separador.setFrameShape(QFrame.HLine)
        separador.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separador)
        
        # Botões
        button_layout = QHBoxLayout()
        self.salvar_btn = QPushButton("Salvar")
        self.salvar_btn.clicked.connect(self.salvar_cliente)
        self.cancelar_btn = QPushButton("Cancelar")
        self.cancelar_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.salvar_btn)
        button_layout.addWidget(self.cancelar_btn)
        
        layout.addLayout(button_layout)
    
    def carregar_dados_cliente(self):
        """Carrega os dados do cliente nos campos do formulário."""
        self.nome_input.setText(self.cliente['nome'])
        
        # Carregar data de nascimento
        if self.cliente['data_nascimento']:
            try:
                if isinstance(self.cliente['data_nascimento'], str):
                    data = datetime.strptime(self.cliente['data_nascimento'], '%Y-%m-%d')
                    qdate = QDate(data.year, data.month, data.day)
                    self.data_nascimento_input.setDate(qdate)
            except:
                pass  # Manter data padrão se houver erro
        
        self.telefone_input.setText(self.cliente['telefone'] or "")
        self.email_input.setText(self.cliente['email'] or "")
        self.endereco_input.setText(self.cliente['endereco'] or "")
    
    def salvar_cliente(self):
        """Salva os dados do cliente no banco de dados."""
        # Validar campos obrigatórios
        if not self.nome_input.text().strip():
            QMessageBox.warning(self, "Erro", "O nome do cliente é obrigatório!")
            return
        
        # Coletar dados do formulário
        nome = self.nome_input.text().strip()
        data_nascimento = self.data_nascimento_input.date().toString("yyyy-MM-dd")
        telefone = self.telefone_input.text().strip()
        email = self.email_input.text().strip()
        endereco = self.endereco_input.text().strip()
        
        try:
            # Inserir ou atualizar cliente
            if self.cliente_id:
                sucesso = self.db.atualizar_cliente(
                    self.cliente_id, nome, data_nascimento, telefone, email, endereco
                )
                mensagem = "Cliente atualizado com sucesso!"
            else:
                sucesso = self.db.adicionar_cliente(
                    nome, data_nascimento, telefone, email, endereco
                )
                mensagem = "Cliente cadastrado com sucesso!"
            
            if sucesso:
                QMessageBox.information(self, "Sucesso", mensagem)
                self.accept()
            else:
                QMessageBox.warning(self, "Erro", "Não foi possível salvar o cliente.")
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar cliente: {str(e)}")