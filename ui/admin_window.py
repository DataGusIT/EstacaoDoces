from PyQt5.QtWidgets import (QDialog, QTabWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
                             QLabel, QLineEdit, QComboBox, QFormLayout, QWidget, QGroupBox,
                             QSpinBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate

class AdminWindow(QDialog):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.init_ui()
        self.carregar_dados()
        
    def init_ui(self):
        self.setWindowTitle("Painel de Administração")
        self.setMinimumSize(800, 600)
        
        # Layout principal
        layout = QVBoxLayout()
        
        # Criar tabs
        self.tabs = QTabWidget()
        self.tab_usuarios = QWidget()
        self.tab_produtos = QWidget()
        self.tab_vendas = QWidget()
        self.tab_relatorios = QWidget()
        
        self.tabs.addTab(self.tab_usuarios, "Usuários")
        self.tabs.addTab(self.tab_produtos, "Produtos")
        self.tabs.addTab(self.tab_vendas, "Vendas")
        self.tabs.addTab(self.tab_relatorios, "Relatórios")
        
        # Configurar cada tab
        self.configurar_tab_usuarios()
        self.configurar_tab_produtos()
        self.configurar_tab_vendas()
        self.configurar_tab_relatorios()
        
        # Botões de controle
        btn_layout = QHBoxLayout()
        self.btn_fechar = QPushButton("Fechar")
        self.btn_fechar.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_fechar)
        
        # Adicionar widgets ao layout principal
        layout.addWidget(self.tabs)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def configurar_tab_usuarios(self):
        layout = QVBoxLayout()
        
        # Tabela de usuários
        self.tabela_usuarios = QTableWidget()
        self.tabela_usuarios.setColumnCount(5)
        self.tabela_usuarios.setHorizontalHeaderLabels(["ID", "Nome", "Login", "Tipo", "Ações"])
        self.tabela_usuarios.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Botões de controle
        btnLayout = QHBoxLayout()
        self.btn_novo_usuario = QPushButton("Novo Usuário")
        self.btn_novo_usuario.clicked.connect(self.mostrar_form_usuario)
        
        btnLayout.addWidget(self.btn_novo_usuario)
        btnLayout.addStretch()
        
        # Formulário para adicionar/editar usuário
        self.form_usuario = QGroupBox("Adicionar/Editar Usuário")
        self.form_usuario.setVisible(False)
        
        form_layout = QFormLayout()
        
        self.usuario_nome = QLineEdit()
        self.usuario_login = QLineEdit()
        self.usuario_senha = QLineEdit()
        self.usuario_senha.setEchoMode(QLineEdit.Password)
        self.usuario_tipo = QComboBox()
        self.usuario_tipo.addItems(["cliente", "operador", "admin"])
        
        form_layout.addRow("Nome:", self.usuario_nome)
        form_layout.addRow("Login:", self.usuario_login)
        form_layout.addRow("Senha:", self.usuario_senha)
        form_layout.addRow("Tipo:", self.usuario_tipo)
        
        btn_form_layout = QHBoxLayout()
        self.btn_salvar_usuario = QPushButton("Salvar")
        self.btn_salvar_usuario.clicked.connect(self.salvar_usuario)
        self.btn_cancelar_usuario = QPushButton("Cancelar")
        self.btn_cancelar_usuario.clicked.connect(lambda: self.form_usuario.setVisible(False))
        
        btn_form_layout.addWidget(self.btn_salvar_usuario)
        btn_form_layout.addWidget(self.btn_cancelar_usuario)
        
        form_layout.addRow("", btn_form_layout)
        self.form_usuario.setLayout(form_layout)
        
        # Adicionar widgets ao layout
        layout.addLayout(btnLayout)
        layout.addWidget(self.tabela_usuarios)
        layout.addWidget(self.form_usuario)
        
        self.tab_usuarios.setLayout(layout)
    
    def configurar_tab_produtos(self):
        layout = QVBoxLayout()
        
        # Tabela de produtos
        self.tabela_produtos = QTableWidget()
        self.tabela_produtos.setColumnCount(5)
        self.tabela_produtos.setHorizontalHeaderLabels(["ID", "Nome", "Preço", "Estoque", "Ações"])
        self.tabela_produtos.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        
        # Botões de controle
        btnLayout = QHBoxLayout()
        self.btn_novo_produto = QPushButton("Novo Produto")
        self.btn_novo_produto.clicked.connect(self.mostrar_form_produto)
        
        btnLayout.addWidget(self.btn_novo_produto)
        btnLayout.addStretch()
        
        # Formulário para adicionar/editar produto
        self.form_produto = QGroupBox("Adicionar/Editar Produto")
        self.form_produto.setVisible(False)
        
        form_layout = QFormLayout()
        
        self.produto_nome = QLineEdit()
        self.produto_preco = QLineEdit()
        self.produto_estoque = QSpinBox()
        self.produto_estoque.setRange(0, 10000)
        
        form_layout.addRow("Nome:", self.produto_nome)
        form_layout.addRow("Preço:", self.produto_preco)
        form_layout.addRow("Estoque:", self.produto_estoque)
        
        btn_form_layout = QHBoxLayout()
        self.btn_salvar_produto = QPushButton("Salvar")
        self.btn_salvar_produto.clicked.connect(self.salvar_produto)
        self.btn_cancelar_produto = QPushButton("Cancelar")
        self.btn_cancelar_produto.clicked.connect(lambda: self.form_produto.setVisible(False))
        
        btn_form_layout.addWidget(self.btn_salvar_produto)
        btn_form_layout.addWidget(self.btn_cancelar_produto)
        
        form_layout.addRow("", btn_form_layout)
        self.form_produto.setLayout(form_layout)
        
        # Adicionar widgets ao layout
        layout.addLayout(btnLayout)
        layout.addWidget(self.tabela_produtos)
        layout.addWidget(self.form_produto)
        
        self.tab_produtos.setLayout(layout)
    
    def configurar_tab_vendas(self):
        layout = QVBoxLayout()
        
        # Tabela de vendas
        self.tabela_vendas = QTableWidget()
        self.tabela_vendas.setColumnCount(5)
        self.tabela_vendas.setHorizontalHeaderLabels(["ID", "Data", "Cliente", "Total", "Detalhes"])
        self.tabela_vendas.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        
        filtros_layout.addWidget(QLabel("De:"))
        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate().addMonths(-1))
        filtros_layout.addWidget(self.data_inicio)
        
        filtros_layout.addWidget(QLabel("Até:"))
        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        filtros_layout.addWidget(self.data_fim)
        
        self.btn_filtrar = QPushButton("Filtrar")
        self.btn_filtrar.clicked.connect(self.filtrar_vendas)
        filtros_layout.addWidget(self.btn_filtrar)
        
        filtros_layout.addStretch()
        
        # Adicionar widgets ao layout
        layout.addLayout(filtros_layout)
        layout.addWidget(self.tabela_vendas)
        
        self.tab_vendas.setLayout(layout)
    
    def configurar_tab_relatorios(self):
        layout = QVBoxLayout()
        
        # Botões de relatórios
        self.btn_rel_vendas = QPushButton("Relatório de Vendas")
        self.btn_rel_vendas.clicked.connect(self.gerar_relatorio_vendas)
        
        self.btn_rel_estoque = QPushButton("Relatório de Estoque")
        self.btn_rel_estoque.clicked.connect(self.gerar_relatorio_estoque)
        
        self.btn_rel_clientes = QPushButton("Relatório de Clientes")
        self.btn_rel_clientes.clicked.connect(self.gerar_relatorio_clientes)
        
        # Adicionar widgets ao layout
        layout.addWidget(QLabel("Selecione um relatório para gerar:"))
        layout.addWidget(self.btn_rel_vendas)
        layout.addWidget(self.btn_rel_estoque)
        layout.addWidget(self.btn_rel_clientes)
        layout.addStretch()
        
        self.tab_relatorios.setLayout(layout)
    
    def carregar_dados(self):
        """Carrega todos os dados nas tabelas"""
        self.carregar_usuarios()
        self.carregar_produtos()
        self.carregar_vendas()
    
    def carregar_usuarios(self):
        """Carrega os usuários do banco de dados na tabela"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT id, nome, login, tipo FROM usuarios")
            usuarios = cursor.fetchall()
            
            self.tabela_usuarios.setRowCount(0)
            
            for i, usuario in enumerate(usuarios):
                self.tabela_usuarios.insertRow(i)
                
                # Adicionar dados
                for j, dado in enumerate(usuario):
                    self.tabela_usuarios.setItem(i, j, QTableWidgetItem(str(dado)))
                
                # Adicionar botões de ação
                btnEditar = QPushButton("Editar")
                btnEditar.clicked.connect(lambda _, row=i: self.editar_usuario(row))
                
                btnExcluir = QPushButton("Excluir")
                btnExcluir.clicked.connect(lambda _, id=usuario[0]: self.excluir_usuario(id))
                
                btnLayout = QHBoxLayout()
                btnLayout.addWidget(btnEditar)
                btnLayout.addWidget(btnExcluir)
                btnLayout.setContentsMargins(0, 0, 0, 0)
                
                widget = QWidget()
                widget.setLayout(btnLayout)
                self.tabela_usuarios.setCellWidget(i, 4, widget)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar usuários: {str(e)}")
    
    def carregar_produtos(self):
        """Carrega os produtos do banco de dados na tabela"""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT id, nome, preco, estoque FROM produtos")
            produtos = cursor.fetchall()
            
            self.tabela_produtos.setRowCount(0)
            
            for i, produto in enumerate(produtos):
                self.tabela_produtos.insertRow(i)
                
                # Adicionar dados
                for j, dado in enumerate(produto):
                    if j == 2:  # Formatar preço
                        item = QTableWidgetItem(f"R$ {float(dado):.2f}")
                    else:
                        item = QTableWidgetItem(str(dado))
                    self.tabela_produtos.setItem(i, j, item)
                
                # Adicionar botões de ação
                btnEditar = QPushButton("Editar")
                btnEditar.clicked.connect(lambda _, row=i: self.editar_produto(row))
                
                btnExcluir = QPushButton("Excluir")
                btnExcluir.clicked.connect(lambda _, id=produto[0]: self.excluir_produto(id))
                
                btnLayout = QHBoxLayout()
                btnLayout.addWidget(btnEditar)
                btnLayout.addWidget(btnExcluir)
                btnLayout.setContentsMargins(0, 0, 0, 0)
                
                widget = QWidget()
                widget.setLayout(btnLayout)
                self.tabela_produtos.setCellWidget(i, 4, widget)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar produtos: {str(e)}")
    
    def carregar_vendas(self):
        """Carrega as vendas do banco de dados na tabela"""
        try:
            cursor = self.db.cursor()
            # Adapte esta consulta conforme seu esquema de banco de dados
            cursor.execute("""
                SELECT v.id, v.data, u.nome, v.total 
                FROM vendas v
                JOIN usuarios u ON v.id_cliente = u.id
                ORDER BY v.data DESC
            """)
            vendas = cursor.fetchall()
            
            self.tabela_vendas.setRowCount(0)
            
            for i, venda in enumerate(vendas):
                self.tabela_vendas.insertRow(i)
                
                # Adicionar dados
                for j, dado in enumerate(venda):
                    if j == 1:  # Formatar data
                        item = QTableWidgetItem(str(dado).split()[0])
                    elif j == 3:  # Formatar total
                        item = QTableWidgetItem(f"R$ {float(dado):.2f}")
                    else:
                        item = QTableWidgetItem(str(dado))
                    self.tabela_vendas.setItem(i, j, item)
                
                # Adicionar botão de detalhes
                btnDetalhes = QPushButton("Ver Detalhes")
                btnDetalhes.clicked.connect(lambda _, id=venda[0]: self.ver_detalhes_venda(id))
                
                btnLayout = QHBoxLayout()
                btnLayout.addWidget(btnDetalhes)
                btnLayout.setContentsMargins(0, 0, 0, 0)
                
                widget = QWidget()
                widget.setLayout(btnLayout)
                self.tabela_vendas.setCellWidget(i, 4, widget)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar vendas: {str(e)}")
    
    # Métodos para usuários
    def mostrar_form_usuario(self):
        """Mostra o formulário para adicionar um novo usuário"""
        self.usuario_id = None
        self.usuario_nome.clear()
        self.usuario_login.clear()
        self.usuario_senha.clear()
        self.usuario_tipo.setCurrentIndex(0)
        self.form_usuario.setTitle("Adicionar Usuário")
        self.form_usuario.setVisible(True)
    
    def editar_usuario(self, row):
        """Abre o formulário para editar um usuário existente"""
        self.usuario_id = int(self.tabela_usuarios.item(row, 0).text())
        self.usuario_nome.setText(self.tabela_usuarios.item(row, 1).text())
        self.usuario_login.setText(self.tabela_usuarios.item(row, 2).text())
        self.usuario_senha.clear()  # Não carregamos a senha por segurança
        
        tipo = self.tabela_usuarios.item(row, 3).text()
        index = self.usuario_tipo.findText(tipo)
        if index >= 0:
            self.usuario_tipo.setCurrentIndex(index)
        
        self.form_usuario.setTitle("Editar Usuário")
        self.form_usuario.setVisible(True)
    
    def salvar_usuario(self):
        """Salva um usuário novo ou existente no banco de dados"""
        try:
            nome = self.usuario_nome.text()
            login = self.usuario_login.text()
            senha = self.usuario_senha.text()
            tipo = self.usuario_tipo.currentText()
            
            if not nome or not login:
                QMessageBox.warning(self, "Aviso", "Nome e login são obrigatórios.")
                return
            
            cursor = self.db.cursor()
            
            if self.usuario_id is None:
                # Novo usuário
                if not senha:
                    QMessageBox.warning(self, "Aviso", "Senha é obrigatória para novos usuários.")
                    return
                
                cursor.execute(
                    "INSERT INTO usuarios (nome, login, senha, tipo) VALUES (?, ?, ?, ?)",
                    (nome, login, senha, tipo)
                )
                QMessageBox.information(self, "Sucesso", "Usuário adicionado com sucesso!")
            else:
                # Editar usuário existente
                if senha:
                    cursor.execute(
                        "UPDATE usuarios SET nome = ?, login = ?, senha = ?, tipo = ? WHERE id = ?",
                        (nome, login, senha, tipo, self.usuario_id)
                    )
                else:
                    cursor.execute(
                        "UPDATE usuarios SET nome = ?, login = ?, tipo = ? WHERE id = ?",
                        (nome, login, tipo, self.usuario_id)
                    )
                QMessageBox.information(self, "Sucesso", "Usuário atualizado com sucesso!")
            
            self.db.commit()
            self.form_usuario.setVisible(False)
            self.carregar_usuarios()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar usuário: {str(e)}")
    
    def excluir_usuario(self, id_usuario):
        """Exclui um usuário do banco de dados"""
        confirma = QMessageBox.question(
            self, "Confirmar exclusão", 
            "Tem certeza que deseja excluir este usuário?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirma == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
                self.db.commit()
                QMessageBox.information(self, "Sucesso", "Usuário excluído com sucesso!")
                self.carregar_usuarios()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir usuário: {str(e)}")
    
    # Métodos para produtos
    def mostrar_form_produto(self):
        """Mostra o formulário para adicionar um novo produto"""
        self.produto_id = None
        self.produto_nome.clear()
        self.produto_preco.clear()
        self.produto_estoque.setValue(0)
        self.form_produto.setTitle("Adicionar Produto")
        self.form_produto.setVisible(True)
    
    def editar_produto(self, row):
        """Abre o formulário para editar um produto existente"""
        self.produto_id = int(self.tabela_produtos.item(row, 0).text())
        self.produto_nome.setText(self.tabela_produtos.item(row, 1).text())
        
        # Remover formatação do preço
        preco_texto = self.tabela_produtos.item(row, 2).text().replace("R$ ", "")
        self.produto_preco.setText(preco_texto)
        
        self.produto_estoque.setValue(int(self.tabela_produtos.item(row, 3).text()))
        
        self.form_produto.setTitle("Editar Produto")
        self.form_produto.setVisible(True)
    
    def salvar_produto(self):
        """Salva um produto novo ou existente no banco de dados"""
        try:
            nome = self.produto_nome.text()
            
            try:
                preco = float(self.produto_preco.text().replace(",", "."))
            except ValueError:
                QMessageBox.warning(self, "Aviso", "Preço inválido.")
                return
                
            estoque = self.produto_estoque.value()
            
            if not nome:
                QMessageBox.warning(self, "Aviso", "Nome é obrigatório.")
                return
            
            cursor = self.db.cursor()
            
            if self.produto_id is None:
                # Novo produto
                cursor.execute(
                    "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
                    (nome, preco, estoque)
                )
                QMessageBox.information(self, "Sucesso", "Produto adicionado com sucesso!")
            else:
                # Editar produto existente
                cursor.execute(
                    "UPDATE produtos SET nome = ?, preco = ?, estoque = ? WHERE id = ?",
                    (nome, preco, estoque, self.produto_id)
                )
                QMessageBox.information(self, "Sucesso", "Produto atualizado com sucesso!")
            
            self.db.commit()
            self.form_produto.setVisible(False)
            self.carregar_produtos()
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar produto: {str(e)}")
    
    def excluir_produto(self, id_produto):
        """Exclui um produto do banco de dados"""
        confirma = QMessageBox.question(
            self, "Confirmar exclusão", 
            "Tem certeza que deseja excluir este produto?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if confirma == QMessageBox.Yes:
            try:
                cursor = self.db.cursor()
                cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
                self.db.commit()
                QMessageBox.information(self, "Sucesso", "Produto excluído com sucesso!")
                self.carregar_produtos()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao excluir produto: {str(e)}")
    
    # Métodos para vendas
    def filtrar_vendas(self):
        """Filtra as vendas por data"""
        try:
            data_inicio = self.data_inicio.date().toString("yyyy-MM-dd")
            data_fim = self.data_fim.date().toString("yyyy-MM-dd")
            
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT v.id, v.data, u.nome, v.total 
                FROM vendas v
                JOIN usuarios u ON v.id_cliente = u.id
                WHERE date(v.data) BETWEEN ? AND ?
                ORDER BY v.data DESC
            """, (data_inicio, data_fim))
            
            vendas = cursor.fetchall()
            
            self.tabela_vendas.setRowCount(0)
            
            for i, venda in enumerate(vendas):
                self.tabela_vendas.insertRow(i)
                
                # Adicionar dados
                for j, dado in enumerate(venda):
                    if j == 1:  # Formatar data
                        item = QTableWidgetItem(str(dado).split()[0])
                    elif j == 3:  # Formatar total
                        item = QTableWidgetItem(f"R$ {float(dado):.2f}")
                    else:
                        item = QTableWidgetItem(str(dado))
                    self.tabela_vendas.setItem(i, j, item)
                
                # Adicionar botão de detalhes
                btnDetalhes = QPushButton("Ver Detalhes")
                btnDetalhes.clicked.connect(lambda _, id=venda[0]: self.ver_detalhes_venda(id))
                
                btnLayout = QHBoxLayout()
                btnLayout.addWidget(btnDetalhes)
                btnLayout.setContentsMargins(0, 0, 0, 0)
                
                widget = QWidget()
                widget.setLayout(btnLayout)
                self.tabela_vendas.setCellWidget(i, 4, widget)
                
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao filtrar vendas: {str(e)}")
    
    def ver_detalhes_venda(self, id_venda):
        """Mostra os detalhes de uma venda específica"""
        try:
            cursor = self.db.cursor()
            
            # Obter informações da venda
            cursor.execute("""
                SELECT v.id, v.data, u.nome, v.total 
                FROM vendas v
                JOIN usuarios u ON v.id_cliente = u.id
                WHERE v.id = ?
            """, (id_venda,))
            
            venda = cursor.fetchone()
            
            if not venda:
                QMessageBox.warning(self, "Aviso", "Venda não encontrada.")
                return
            
            # Obter itens da venda
            cursor.execute("""
                SELECT p.nome, i.quantidade, i.preco_unitario, (i.quantidade * i.preco_unitario) as subtotal
                FROM itens_venda i
                JOIN produtos p ON i.id_produto = p.id
                WHERE i.id_venda = ?
            """, (id_venda,))
            
            itens = cursor.fetchall()
            
            # Montar mensagem de detalhes
            mensagem = f"<h3>Venda #{venda[0]}</h3>"
            mensagem += f"<p><b>Data:</b> {str(venda[1]).split()[0]}</p>"
            mensagem += f"<p><b>Cliente:</b> {venda[2]}</p>"
            mensagem += f"<p><b>Total:</b> R$ {float(venda[3]):.2f}</p>"
            
            mensagem += "<h4>Itens:</h4>"
            mensagem += "<table border='1' cellspacing='0' cellpadding='5' width='100%'>"
            mensagem += "<tr><th>Produto</th><th>Qtd</th><th>Preço Unit.</th><th>Subtotal</th></tr>"
            
            for item in itens:
                mensagem += f"<tr><td>{item[0]}</td><td>{item[1]}</td><td>R$ {float(item[2]):.2f}</td><td>R$ {float(item[3]):.2f}</td></tr>"
            
            mensagem += "</table>"
            
            # Exibir diálogo com detalhes
            QMessageBox.information(self, f"Detalhes da Venda #{id_venda}", mensagem)
            
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar detalhes da venda: {str(e)}")
    
    