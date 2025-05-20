import sqlite3
import os
import hashlib
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_file='database/estoque.db'):
        self.db_path = db_file 

        # Garantir que o diretório exista
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        # Conectar ao banco de dados
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Inicializar as tabelas
        self.criar_tabelas()
        
    def connect_to_database(self):
        """Conecta ou reconecta ao banco de dados"""
        try:
            # Fechar conexão anterior se existir
            if hasattr(self, 'conn') and self.conn:
                try:
                    self.conn.close()
                except:
                    pass
            
            # Estabelecer nova conexão
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Para acessar colunas pelo nome
            self.cursor = self.conn.cursor()
            return True
        except Exception as e:
            print(f"Erro ao conectar ao banco de dados: {e}")
            return False
    
    def is_connection_active(self):
        """Verifica se a conexão com o banco de dados está ativa"""
        try:
            # Tenta executar uma query simples para verificar a conexão
            self.cursor.execute("SELECT 1")
            return True
        except (sqlite3.ProgrammingError, sqlite3.OperationalError):
            # Se ocorrer erro, a conexão está fechada
            return False
    
    def ensure_connection(self):
        """Garante que a conexão está ativa antes de executar operações"""
        if not self.is_connection_active():
            return self.connect_to_database()
        return True
    
    def criar_tabelas(self):
        # Tabela de Produtos (com novos campos)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_barras TEXT,
            nome TEXT NOT NULL,
            descricao TEXT,
            quantidade INTEGER DEFAULT 0,
            estoque_minimo INTEGER DEFAULT 0,
            preco_compra REAL,
            margem_lucro REAL,
            preco_venda REAL,
            data_validade DATE,
            localizacao TEXT,
            fornecedor_id INTEGER,
            data_cadastro DATE DEFAULT CURRENT_DATE,
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
        )
        ''')
        
        # Tabela de Fornecedores
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS fornecedores (
             id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            representante TEXT,
            frequencia_compra TEXT,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            contato TEXT,
            data_cadastro DATE DEFAULT CURRENT_DATE
        )
        ''')
        
        # Tabela de Clientes
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            documento TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            data_cadastro DATE DEFAULT CURRENT_DATE
        )
        ''')
        
        # Tabela de Promoções
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            preco_antigo REAL,
            preco_promocional REAL,
            data_inicio DATE,
            data_fim DATE,
            descricao TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        ''')
        
        # Tabela de Caixas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS caixas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_fechamento TIMESTAMP,
            saldo_inicial REAL NOT NULL,
            saldo_final_sistema REAL,
            saldo_final_informado REAL,
            diferenca REAL,
            operador TEXT,
            status TEXT DEFAULT 'Aberto',
            observacao TEXT
        )
        ''')
        
        # Tabela de Movimentos de Caixa
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS movimentos_caixa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            caixa_id INTEGER NOT NULL,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tipo TEXT NOT NULL, -- 'Entrada' ou 'Saída'
            descricao TEXT NOT NULL,
            valor REAL NOT NULL,
            forma_pagamento TEXT,
            referencia_id INTEGER, -- ID da venda ou outra entidade
            tipo_referencia TEXT, -- 'Venda', 'Despesa', etc.
            operador TEXT,
            observacao TEXT,
            FOREIGN KEY (caixa_id) REFERENCES caixas (id)
        )
        ''')
        
        # Tabela de Vendas
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            cliente_id INTEGER,
            valor_total REAL NOT NULL,
            desconto REAL DEFAULT 0,
            forma_pagamento TEXT,
            parcelas INTEGER DEFAULT 1,
            observacao TEXT,
            status TEXT DEFAULT 'Concluída',
            operador TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes (id)
        )
        ''')
        
        # Tabela de Itens de Venda
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS itens_venda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venda_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venda_id) REFERENCES vendas (id),
            FOREIGN KEY (produto_id) REFERENCES produtos (id)
        )
        ''')

       # Tabela de Usuários (nova)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            login TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL,
            email TEXT UNIQUE,
            tipo TEXT DEFAULT 'comum', -- 'admin' ou 'comum'
            ativo INTEGER DEFAULT 1,   -- 0 para inativo, 1 para ativo
            data_cadastro DATE DEFAULT CURRENT_DATE,
            ultimo_acesso TIMESTAMP
        )
        ''')
        
        # Verificar se existe pelo menos um usuário admin
        self.cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='admin'")
        count = self.cursor.fetchone()[0]
        
        if count == 0:
            # Criar um usuário admin padrão se não existir nenhum
            # Senha padrão: admin123 (em produção, use hash adequado)
            import hashlib
            senha_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            self.cursor.execute('''
            INSERT INTO usuarios (nome, login, senha, email, tipo)
            VALUES (?, ?, ?, ?, ?)
            ''', ("Administrador", "admin", senha_hash, "admin@sistema.com", "admin"))
        
        # Commit das mudanças
        self.conn.commit()
    
    # Métodos para Produtos (atualizados)
    def adicionar_produto(self, codigo_barras, nome, descricao, quantidade, estoque_minimo,
                        preco_compra, margem_lucro, preco_venda, 
                        data_validade, localizacao, fornecedor_id):
        self.cursor.execute('''
        INSERT INTO produtos (
            codigo_barras, nome, descricao, quantidade, estoque_minimo,
            preco_compra, margem_lucro, preco_venda, 
            data_validade, localizacao, fornecedor_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            codigo_barras, nome, descricao, quantidade, estoque_minimo,
            preco_compra, margem_lucro, preco_venda, 
            data_validade, localizacao, fornecedor_id
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def atualizar_produto(self, id, codigo_barras, nome, descricao, quantidade, estoque_minimo,
                        preco_compra, margem_lucro, preco_venda, 
                        data_validade, localizacao, fornecedor_id):
        self.cursor.execute('''
        UPDATE produtos
        SET codigo_barras = ?, nome = ?, descricao = ?, quantidade = ?, estoque_minimo = ?,
            preco_compra = ?, margem_lucro = ?, preco_venda = ?,
            data_validade = ?, localizacao = ?, fornecedor_id = ?
        WHERE id = ?
        ''', (
            codigo_barras, nome, descricao, quantidade, estoque_minimo,
            preco_compra, margem_lucro, preco_venda,
            data_validade, localizacao, fornecedor_id, id
        ))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def excluir_produto(self, id):
        self.cursor.execute('DELETE FROM produtos WHERE id = ?', (id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def obter_produto(self, id):
        self.cursor.execute('SELECT * FROM produtos WHERE id = ?', (id,))
        return self.cursor.fetchone()

    def listar_produtos(self, filtro=None):
        query = 'SELECT p.*, f.nome as fornecedor_nome FROM produtos p LEFT JOIN fornecedores f ON p.fornecedor_id = f.id'
        
        if filtro:
            query += f" WHERE p.nome LIKE '%{filtro}%' OR p.descricao LIKE '%{filtro}%' OR p.codigo_barras LIKE '%{filtro}%'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def verificar_produtos_vencendo(self, dias=30):
        data_limite = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT p.*, f.nome as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.data_validade <= ? AND p.data_validade >= ?
        ORDER BY p.data_validade
        ''', (data_limite, data_hoje))
        
        return self.cursor.fetchall()

    def verificar_produtos_vencidos(self):
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT p.*, f.nome as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.data_validade < ?
        ORDER BY p.data_validade
        ''', (data_hoje,))
        
        return self.cursor.fetchall()

    def verificar_produtos_estoque_baixo(self):
        """Verifica produtos com estoque abaixo do mínimo definido."""
        self.cursor.execute('''
        SELECT p.*, f.nome as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.quantidade <= p.estoque_minimo AND p.estoque_minimo > 0
        ORDER BY p.nome
        ''')
        
        return self.cursor.fetchall()

    def filtrar_produtos(self, filtro_estoque, filtro_vencimento):
        """Filtra produtos por nível de estoque e data de vencimento."""
        hoje = datetime.now().strftime('%Y-%m-%d')
        
        # Base da consulta
        query = '''
        SELECT p.*, f.nome as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE 1=1
        '''
        
        params = []
        
        # Aplicar filtro de estoque
        if filtro_estoque == "baixo":
            query += " AND p.quantidade <= p.estoque_minimo AND p.estoque_minimo > 0"
        elif filtro_estoque == "medio":
            query += " AND p.quantidade > p.estoque_minimo AND p.quantidade <= (p.estoque_minimo * 2)"
        elif filtro_estoque == "alto":
            query += " AND p.quantidade > (p.estoque_minimo * 2)"
        
        # Aplicar filtro de vencimento
        if filtro_vencimento == "30":
            data_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            query += " AND p.data_validade <= ? AND p.data_validade >= ?"
            params.extend([data_limite, hoje])
        elif filtro_vencimento == "15":
            data_limite = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
            query += " AND p.data_validade <= ? AND p.data_validade >= ?"
            params.extend([data_limite, hoje])
        elif filtro_vencimento == "vencidos":
            query += " AND p.data_validade < ?"
            params.append(hoje)
        
        query += " ORDER BY p.nome"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    # Método para migrar a tabela existente para a nova estrutura
    def migrar_tabela_produtos(self):
        """Migra a tabela de produtos para incluir os novos campos."""
        try:
            # Verificar se a coluna código de barras já existe
            self.cursor.execute("PRAGMA table_info(produtos)")
            colunas = self.cursor.fetchall()
            colunas_existentes = [coluna[1] for coluna in colunas]
            
            # Adicionar novas colunas se necessário
            if "codigo_barras" not in colunas_existentes:
                self.cursor.execute("ALTER TABLE produtos ADD COLUMN codigo_barras TEXT")
            
            if "estoque_minimo" not in colunas_existentes:
                self.cursor.execute("ALTER TABLE produtos ADD COLUMN estoque_minimo INTEGER DEFAULT 0")
            
            if "margem_lucro" not in colunas_existentes:
                self.cursor.execute("ALTER TABLE produtos ADD COLUMN margem_lucro REAL DEFAULT 30.0")
                
                # Atualizar a margem de lucro baseado nos preços existentes
                self.cursor.execute('''
                UPDATE produtos 
                SET margem_lucro = ((preco_venda / preco_compra) - 1) * 100
                WHERE preco_compra > 0 AND preco_venda > 0
                ''')
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao migrar tabela de produtos: {str(e)}")
            return False
        
    # Métodos para Fornecedores
    def adicionar_fornecedor(self, nome, representante, frequencia_compra, telefone, email, endereco, contato):
        self.cursor.execute('''
        INSERT INTO fornecedores (nome, representante, frequencia_compra, telefone, email, endereco, contato)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (nome, representante, frequencia_compra, telefone, email, endereco, contato))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def atualizar_fornecedor(self, id, nome, representante, frequencia_compra, telefone, email, endereco, contato):
        self.cursor.execute('''
        UPDATE fornecedores
        SET nome = ?, representante = ?, frequencia_compra = ?, telefone = ?, email = ?, endereco = ?, contato = ?
        WHERE id = ?
        ''', (nome, representante, frequencia_compra, telefone, email, endereco, contato, id))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def excluir_fornecedor(self, id):
        self.cursor.execute('DELETE FROM fornecedores WHERE id = ?', (id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def obter_fornecedor(self, id):
        self.cursor.execute('SELECT * FROM fornecedores WHERE id = ?', (id,))
        return self.cursor.fetchone()
    
    def listar_fornecedores(self, filtro=None):
        query = 'SELECT * FROM fornecedores'
        
        if filtro:
            query += f" WHERE nome LIKE '%{filtro}%' OR representante LIKE '%{filtro}%'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # Métodos para Clientes
    def adicionar_cliente(self, nome, documento, telefone, email, endereco):
        self.cursor.execute('''
        INSERT INTO clientes (nome, documento, telefone, email, endereco)
        VALUES (?, ?, ?, ?, ?)
        ''', (nome, documento, telefone, email, endereco))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def atualizar_cliente(self, id, nome, documento, telefone, email, endereco):
        self.cursor.execute('''
        UPDATE clientes
        SET nome = ?, documento = ?, telefone = ?, email = ?, endereco = ?
        WHERE id = ?
        ''', (nome, documento, telefone, email, endereco, id))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def excluir_cliente(self, id):
        self.cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def obter_cliente(self, id):
        self.cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
        return self.cursor.fetchone()
    
    def listar_clientes(self, filtro=None):
        query = 'SELECT * FROM clientes'
        
        if filtro:
            query += f" WHERE nome LIKE '%{filtro}%' OR documento LIKE '%{filtro}%'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    # Métodos para Promoções
    def adicionar_promocao(self, produto_id, preco_antigo, preco_promocional, 
                           data_inicio, data_fim, descricao):
        self.cursor.execute('''
        INSERT INTO promocoes (produto_id, preco_antigo, preco_promocional, 
                               data_inicio, data_fim, descricao)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (produto_id, preco_antigo, preco_promocional, 
             data_inicio, data_fim, descricao))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def atualizar_promocao(self, id, produto_id, preco_antigo, preco_promocional, 
                           data_inicio, data_fim, descricao):
        self.cursor.execute('''
        UPDATE promocoes
        SET produto_id = ?, preco_antigo = ?, preco_promocional = ?, 
            data_inicio = ?, data_fim = ?, descricao = ?
        WHERE id = ?
        ''', (produto_id, preco_antigo, preco_promocional, 
             data_inicio, data_fim, descricao, id))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def excluir_promocao(self, id):
        self.cursor.execute('DELETE FROM promocoes WHERE id = ?', (id,))
        self.conn.commit()
        return self.cursor.rowcount > 0
    
    def obter_promocao(self, id):
        self.cursor.execute('SELECT * FROM promocoes WHERE id = ?', (id,))
        return self.cursor.fetchone()
    
    def listar_promocoes(self, filtro=None):
        query = '''
        SELECT p.*, pr.nome as produto_nome 
        FROM promocoes p 
        LEFT JOIN produtos pr ON p.produto_id = pr.id
        '''
        
        if filtro:
            query += f" WHERE pr.nome LIKE '%{filtro}%' OR p.descricao LIKE '%{filtro}%'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def listar_promocoes_ativas(self):
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT p.*, pr.nome as produto_nome 
        FROM promocoes p 
        LEFT JOIN produtos pr ON p.produto_id = pr.id
        WHERE p.data_inicio <= ? AND p.data_fim >= ?
        ''', (data_hoje, data_hoje))
        
        return self.cursor.fetchall()
    
    # Métodos para Usuários
    def obter_usuario_por_id(self, usuario_id):
        """Retorna os dados de um usuário pelo ID"""
        self.cursor.execute('''
        SELECT id, nome, login, email, tipo, data_cadastro, ultimo_acesso
        FROM usuarios WHERE id = ?
        ''', (usuario_id,))
        
        usuario = self.cursor.fetchone()
        
        if usuario:
            return dict(usuario)
        else:
            return None

    def autenticar_usuario(self, login, senha):
        """Verifica se o usuário e senha estão corretos"""
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        self.cursor.execute('''
            SELECT * FROM usuarios WHERE login = ? AND senha = ? AND ativo = 1
        ''', (login, senha))
        
        usuario = self.cursor.fetchone()
        
        if usuario:
            # Atualizar o campo de último acesso
            self.cursor.execute('''
                UPDATE usuarios SET ultimo_acesso = CURRENT_TIMESTAMP WHERE id = ?
            ''', (usuario['id'],))
            self.conn.commit()
            return dict(usuario)
        else:
            return None

    def cadastrar_usuario(self, nome, login, senha, email, tipo):
        try:
            self.cursor.execute("""
                INSERT INTO usuarios (nome, login, senha, email, tipo)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, login, senha, email, tipo))
            self.conn.commit()
            return True, "Usuário cadastrado com sucesso!"
        except Exception as e:
            return False, f"Erro ao cadastrar usuário: {str(e)}"
        
    def listar_usuarios(self):
        """Retorna a lista de todos os usuários"""
        try:
            self.cursor.execute('''
                SELECT id, nome, login, email, tipo, ativo, data_cadastro, ultimo_acesso
                FROM usuarios
                ORDER BY nome
            ''')
            
            usuarios = self.cursor.fetchall()
            return [dict(usuario) for usuario in usuarios]
        except Exception as e:
            print(f"Erro ao listar usuários: {str(e)}")
            return []

    def excluir_usuario(self, usuario_id):
        """Exclui um usuário pelo ID (ou desativa, se preferir não excluir)"""
        try:
            # Verificar se não é o último administrador
            self.cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='admin'")
            count_admin = self.cursor.fetchone()[0]
            
            # Verificar se o usuário a ser excluído é um admin
            self.cursor.execute("SELECT tipo FROM usuarios WHERE id=?", (usuario_id,))
            user_tipo = self.cursor.fetchone()
            
            if user_tipo and user_tipo['tipo'] == 'admin' and count_admin <= 1:
                return False, "Não é possível excluir o último administrador do sistema."
            
            # Ao invés de excluir, você pode apenas desativar o usuário
            self.cursor.execute('''
                UPDATE usuarios SET ativo = 0 WHERE id = ?
            ''', (usuario_id,))
            
            # Se quiser realmente excluir, use:
            # self.cursor.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            
            self.conn.commit()
            return True, "Usuário desativado com sucesso."
        except Exception as e:
            return False, f"Erro ao excluir usuário: {str(e)}"

    def atualizar_usuario(self, usuario_id, nome, login, email, tipo, ativo=1):
        """Atualiza os dados de um usuário"""
        try:
            # Verificar se não é o último administrador
            if tipo != 'admin':
                self.cursor.execute("SELECT tipo FROM usuarios WHERE id=?", (usuario_id,))
                user_tipo = self.cursor.fetchone()
                
                if user_tipo and user_tipo['tipo'] == 'admin':
                    self.cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='admin'")
                    count_admin = self.cursor.fetchone()[0]
                    
                    if count_admin <= 1:
                        return False, "Não é possível remover o nível de administrador do último administrador."
            
            # Atualizar os dados
            self.cursor.execute('''
                UPDATE usuarios 
                SET nome = ?, login = ?, email = ?, tipo = ?, ativo = ?
                WHERE id = ?
            ''', (nome, login, email, tipo, ativo, usuario_id))
            
            self.conn.commit()
            return True, "Usuário atualizado com sucesso."
        except Exception as e:
            return False, f"Erro ao atualizar usuário: {str(e)}"

    def alterar_senha_usuario(self, usuario_id, nova_senha):
        """Altera a senha de um usuário"""
        try:
            import hashlib
            senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
            
            self.cursor.execute('''
                UPDATE usuarios SET senha = ? WHERE id = ?
            ''', (senha_hash, usuario_id))
            
            self.conn.commit()
            return True, "Senha alterada com sucesso."
        except Exception as e:
            return False, f"Erro ao alterar senha: {str(e)}"


    # Métodos para Caixas
    def abrir_caixa(self, saldo_inicial, operador, observacao=""):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Verificar se já existe um caixa aberto
            cursor.execute("SELECT id FROM caixas WHERE status = 'Aberto'")
            if cursor.fetchone():
                conn.close()
                return False
            
            # Registrar abertura de caixa
            cursor.execute("""
                INSERT INTO caixas (saldo_inicial, operador, observacao)
                VALUES (?, ?, ?)
            """, (saldo_inicial, operador, observacao))
            
            caixa_id = cursor.lastrowid
            
            # Registrar movimento de entrada do saldo inicial
            if saldo_inicial > 0:
                cursor.execute("""
                    INSERT INTO movimentos_caixa 
                    (caixa_id, tipo, descricao, valor, forma_pagamento, operador)
                    VALUES (?, 'Entrada', 'Saldo Inicial', ?, 'Dinheiro', ?)
                """, (caixa_id, saldo_inicial, operador))
            
            conn.commit()
            conn.close()
            
            return caixa_id
        except Exception as e:
            print(f"Erro ao abrir caixa: {e}")
            return False
    
    def fechar_caixa(self, caixa_id, saldo_final_informado, diferenca, operador, observacao=""):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Calcular saldo final do sistema
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN tipo = 'Entrada' THEN valor ELSE -valor END) 
                FROM movimentos_caixa 
                WHERE caixa_id = ?
            """, (caixa_id,))
            
            saldo_final_sistema = cursor.fetchone()[0] or 0
            
            # Atualizar registro do caixa
            cursor.execute("""
                UPDATE caixas SET 
                data_fechamento = CURRENT_TIMESTAMP,
                saldo_final_sistema = ?,
                saldo_final_informado = ?,
                diferenca = ?,
                status = 'Fechado',
                observacao = ?
                WHERE id = ?
            """, (saldo_final_sistema, saldo_final_informado, diferenca, observacao, caixa_id))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Erro ao fechar caixa: {e}")
            return False
    
    def buscar_produto_por_codigo_barras(self, codigo_barras):
        query = "SELECT * FROM produtos WHERE codigo_barras = ?"
        self.cursor.execute(query, (codigo_barras,))
        produto = self.cursor.fetchone()
        
        if produto:
            # Converter resultado para dicionário
            colunas = [desc[0] for desc in self.cursor.description]
            return dict(zip(colunas, produto))
        return None
    
    def obter_caixa_aberto(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM caixas WHERE status = 'Aberto'
            """)
            
            caixa = cursor.fetchone()
            conn.close()
            
            if caixa:
                return dict(caixa)
            else:
                return None
        except Exception as e:
            print(f"Erro ao buscar caixa aberto: {e}")
            return None
    
    def obter_saldo_atual(self, caixa_id):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN tipo = 'Entrada' THEN valor ELSE -valor END) 
                FROM movimentos_caixa 
                WHERE caixa_id = ?
            """, (caixa_id,))
            
            saldo = cursor.fetchone()[0] or 0
            conn.close()
            
            return float(saldo)
        except Exception as e:
            print(f"Erro ao obter saldo: {e}")
            return 0.0
    
    def registrar_movimento_caixa(self, caixa_id, tipo, descricao, valor, forma_pagamento="Dinheiro", 
                                 referencia_id=None, tipo_referencia=None, operador="Sistema", observacao=""):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO movimentos_caixa 
                (caixa_id, tipo, descricao, valor, forma_pagamento, referencia_id, tipo_referencia, operador, observacao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (caixa_id, tipo, descricao, valor, forma_pagamento, referencia_id, 
                 tipo_referencia, operador, observacao))
            
            movimento_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return movimento_id
        except Exception as e:
            print(f"Erro ao registrar movimento: {e}")
            return False
    
    def listar_movimentos_caixa(self, caixa_id):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, datetime(data_hora, 'localtime') as data_hora, tipo, descricao, 
                       valor, forma_pagamento, referencia_id, tipo_referencia
                FROM movimentos_caixa 
                WHERE caixa_id = ?
                ORDER BY data_hora DESC
            """, (caixa_id,))
            
            movimentos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return movimentos
        except Exception as e:
            print(f"Erro ao listar movimentos: {e}")
            return []
    
    def listar_movimentos_por_periodo(self, caixa_id, data_inicio, data_fim):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, datetime(data_hora, 'localtime') as data_hora, tipo, descricao, 
                       valor, forma_pagamento, referencia_id, tipo_referencia
                FROM movimentos_caixa 
                WHERE caixa_id = ? AND date(data_hora) BETWEEN ? AND ?
                ORDER BY data_hora DESC
            """, (caixa_id, data_inicio, data_fim))
            
            movimentos = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return movimentos
        except Exception as e:
            print(f"Erro ao listar movimentos por período: {e}")
            return []
    
    def obter_detalhes_caixa(self, caixa_id):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Buscar dados do caixa
            cursor.execute("""
                SELECT 
                    id, datetime(data_abertura, 'localtime') as data_abertura,
                    datetime(data_fechamento, 'localtime') as data_fechamento,
                    saldo_inicial, saldo_final_sistema, saldo_final_informado,
                    diferenca, operador, status, observacao
                FROM caixas 
                WHERE id = ?
            """, (caixa_id,))
            
            caixa = cursor.fetchone()
            if not caixa:
                conn.close()
                return None
            
            detalhes = dict(caixa)
            
            # Buscar entradas e saídas
            cursor.execute("""
                SELECT tipo, SUM(valor) as total
                FROM movimentos_caixa
                WHERE caixa_id = ?
                GROUP BY tipo
            """, (caixa_id,))
            
            for row in cursor.fetchall():
                if row['tipo'] == 'Entrada':
                    detalhes['total_entradas'] = row['total']
                else:
                    detalhes['total_saidas'] = row['total']
            
            # Garantir valores mesmo que não existam
            if 'total_entradas' not in detalhes:
                detalhes['total_entradas'] = 0
            if 'total_saidas' not in detalhes:
                detalhes['total_saidas'] = 0
            
            # Buscar vendas
            cursor.execute("""
                SELECT COUNT(*) as total_vendas, SUM(valor_total) as valor_vendas
                FROM vendas v
                JOIN movimentos_caixa m ON v.id = m.referencia_id AND m.tipo_referencia = 'Venda'
                WHERE m.caixa_id = ?
            """, (caixa_id,))
            
            vendas = cursor.fetchone()
            if vendas:
                detalhes['total_vendas'] = vendas['total_vendas'] or 0
                detalhes['valor_vendas'] = vendas['valor_vendas'] or 0
            else:
                detalhes['total_vendas'] = 0
                detalhes['valor_vendas'] = 0
            
            conn.close()
            return detalhes
        except Exception as e:
            print(f"Erro ao obter detalhes do caixa: {e}")
            return None
    
    def gerar_relatorio_periodo(self, data_inicio, data_fim):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Movimentos de caixa
            cursor.execute("""
                SELECT tipo, SUM(valor) as total
                FROM movimentos_caixa
                WHERE date(data_hora) BETWEEN ? AND ?
                GROUP BY tipo
            """, (data_inicio, data_fim))
            
            movimentos_resumo = {'total_entradas': 0, 'total_saidas': 0}
            
            for row in cursor.fetchall():
                if row['tipo'] == 'Entrada':
                    movimentos_resumo['total_entradas'] = row['total']
                else:
                    movimentos_resumo['total_saidas'] = row['total']
            
            # Vendas
            cursor.execute("""
                SELECT COUNT(*) as qtd, SUM(valor_total) as total, SUM(desconto) as descontos
                FROM vendas
                WHERE date(data_hora) BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            
            vendas_resumo = cursor.fetchone()
            
            # Formas de pagamento
            cursor.execute("""
                SELECT forma_pagamento, SUM(valor_total) as total
                FROM vendas
                WHERE date(data_hora) BETWEEN ? AND ?
                GROUP BY forma_pagamento
            """, (data_inicio, data_fim))
            
            pagamentos = {}
            for row in cursor.fetchall():
                pagamentos[row['forma_pagamento']] = row['total']
            
            # Produtos mais vendidos
            cursor.execute("""
                SELECT p.id, p.nome, SUM(i.quantidade) as quantidade, SUM(i.subtotal) as valor_total
                FROM itens_venda i
                JOIN produtos p ON i.produto_id = p.id
                JOIN vendas v ON i.venda_id = v.id
                WHERE date(v.data_hora) BETWEEN ? AND ?
                GROUP BY p.id, p.nome
                ORDER BY quantidade DESC
            """, (data_inicio, data_fim))
            
            produtos = [dict(row) for row in cursor.fetchall()]
            
            # Lista de movimentos
            cursor.execute("""
                SELECT id, datetime(data_hora, 'localtime') as data_hora, tipo, descricao, 
                       valor, forma_pagamento, referencia_id, tipo_referencia
                FROM movimentos_caixa 
                WHERE date(data_hora) BETWEEN ? AND ?
                ORDER BY data_hora DESC
            """, (data_inicio, data_fim))
            
            movimentos = [dict(row) for row in cursor.fetchall()]
            
            # Lista de vendas
            cursor.execute("""
                SELECT v.id, datetime(v.data_hora, 'localtime') as data_hora, 
                       COALESCE(c.nome, 'Cliente Não Identificado') as cliente,
                       v.valor_total, v.desconto, v.forma_pagamento
                FROM vendas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE date(v.data_hora) BETWEEN ? AND ?
                ORDER BY v.data_hora DESC
            """, (data_inicio, data_fim))
            
            vendas = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            # Montar resultado
            resultado = {
                'total_entradas': movimentos_resumo['total_entradas'],
                'total_saidas': movimentos_resumo['total_saidas'],
                'saldo_periodo': movimentos_resumo['total_entradas'] - movimentos_resumo['total_saidas'],
                'qtd_vendas': vendas_resumo['qtd'] or 0,
                'valor_vendas': vendas_resumo['total'] or 0,
                'valor_medio_venda': (vendas_resumo['total'] / vendas_resumo['qtd']) if vendas_resumo['qtd'] else 0,
                'total_descontos': vendas_resumo['descontos'] or 0,
                'pagamentos': pagamentos,
                'produtos_mais_vendidos': produtos,
                'movimentos': movimentos,
                'vendas': vendas
            }
            
            return resultado
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
            return None
    
    def registrar_venda(self, cliente_id, valor_total, desconto=0, forma_pagamento="Dinheiro", 
                       parcelas=1, observacao="", status="Concluída", operador="Sistema"):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO vendas 
                (cliente_id, valor_total, desconto, forma_pagamento, parcelas, observacao, status, operador)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cliente_id, valor_total, desconto, forma_pagamento, parcelas, 
                 observacao, status, operador))
            
            venda_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            return venda_id
        except Exception as e:
            print(f"Erro ao registrar venda: {e}")
            return False
    
    def registrar_item_venda(self, venda_id, produto_id, quantidade, preco_unitario, subtotal):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Registrar item
            cursor.execute("""
                INSERT INTO itens_venda 
                (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (venda_id, produto_id, quantidade, preco_unitario, subtotal))
            
            # Atualizar estoque
            cursor.execute("""
                UPDATE produtos 
                SET quantidade = quantidade - ?
                WHERE id = ?
            """, (quantidade, produto_id))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"Erro ao registrar item de venda: {e}")
            return False
    
    def obter_dados_dashboard(self, data_inicio, data_fim):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Faturamento e número de vendas
            cursor.execute("""
                SELECT COUNT(*) as num_vendas, SUM(valor_total) as faturamento
                FROM vendas
                WHERE date(data_hora) BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            
            vendas_resumo = cursor.fetchone()
            
            # Lucro (com base na diferença entre preço de venda e preço de compra)
            cursor.execute("""
                SELECT SUM((i.preco_unitario - p.preco_compra) * i.quantidade) as lucro
                FROM itens_venda i
                JOIN produtos p ON i.produto_id = p.id
                JOIN vendas v ON i.venda_id = v.id
                WHERE date(v.data_hora) BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            
            # Aqui está o problema: É necessário atribuir o resultado a variável lucro
            lucro_resultado = cursor.fetchone()
            lucro = lucro_resultado['lucro'] if lucro_resultado['lucro'] is not None else 0
            
            # Produtos mais vendidos
            cursor.execute("""
                SELECT p.nome, SUM(i.quantidade) as quantidade, SUM(i.subtotal) as valor_total
                FROM itens_venda i
                JOIN produtos p ON i.produto_id = p.id
                JOIN vendas v ON i.venda_id = v.id
                WHERE date(v.data_hora) BETWEEN ? AND ?
                GROUP BY p.id, p.nome
                ORDER BY quantidade DESC
                LIMIT 10
            """, (data_inicio, data_fim))
            
            produtos = [dict(row) for row in cursor.fetchall()]
            
            # Formas de pagamento
            cursor.execute("""
                SELECT forma_pagamento as forma, SUM(valor_total) as valor_total
                FROM vendas
                WHERE date(data_hora) BETWEEN ? AND ?
                GROUP BY forma_pagamento
                ORDER BY valor_total DESC
            """, (data_inicio, data_fim))
            
            pagamentos = [dict(row) for row in cursor.fetchall()]
            
            # Melhores clientes
            cursor.execute("""
                SELECT 
                    COALESCE(c.nome, 'Cliente Não Identificado') as nome,
                    COUNT(*) as compras,
                    SUM(v.valor_total) as valor_total
                FROM vendas v
                LEFT JOIN clientes c ON v.cliente_id = c.id
                WHERE date(v.data_hora) BETWEEN ? AND ?
                GROUP BY v.cliente_id
                ORDER BY valor_total DESC
                LIMIT 10
            """, (data_inicio, data_fim))
            
            clientes = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            
            # Montar resultado
            resultado = {
                'faturamento': vendas_resumo['faturamento'] or 0,
                'num_vendas': vendas_resumo['num_vendas'] or 0,
                'lucro': lucro,  # Agora a variável lucro está definida
                'produtos': produtos,
                'pagamentos': pagamentos,
                'clientes': clientes
            }

            return resultado
        except Exception as e:
            print(f"Erro ao obter dados para dashboard: {e}")
            return None
    
    def fechar(self):
        self.conn.close()