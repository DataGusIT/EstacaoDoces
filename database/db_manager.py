import sqlite3
import os
from datetime import datetime, timedelta

class DatabaseManager:
    def __init__(self, db_file='database/estoque.db'):
        # Garantir que o diretório exista
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        
        # Conectar ao banco de dados
        self.conn = sqlite3.connect(db_file)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        
        # Inicializar as tabelas
        self.criar_tabelas()
    
    def criar_tabelas(self):
        # Tabela de Produtos
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            quantidade INTEGER DEFAULT 0,
            preco_compra REAL,
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
            documento TEXT UNIQUE,
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
        
        # Commit das mudanças
        self.conn.commit()
    
    # Métodos para Produtos
    def adicionar_produto(self, nome, descricao, quantidade, preco_compra, preco_venda, 
                          data_validade, localizacao, fornecedor_id):
        self.cursor.execute('''
        INSERT INTO produtos (nome, descricao, quantidade, preco_compra, preco_venda, 
                             data_validade, localizacao, fornecedor_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, descricao, quantidade, preco_compra, preco_venda, 
             data_validade, localizacao, fornecedor_id))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def atualizar_produto(self, id, nome, descricao, quantidade, preco_compra, preco_venda, 
                         data_validade, localizacao, fornecedor_id):
        self.cursor.execute('''
        UPDATE produtos
        SET nome = ?, descricao = ?, quantidade = ?, preco_compra = ?, preco_venda = ?,
            data_validade = ?, localizacao = ?, fornecedor_id = ?
        WHERE id = ?
        ''', (nome, descricao, quantidade, preco_compra, preco_venda, 
             data_validade, localizacao, fornecedor_id, id))
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
            query += f" WHERE p.nome LIKE '%{filtro}%' OR p.descricao LIKE '%{filtro}%'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def verificar_produtos_vencendo(self, dias=30):
        data_limite = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT * FROM produtos 
        WHERE data_validade <= ? AND data_validade >= ?
        ORDER BY data_validade
        ''', (data_limite, data_hoje))
        
        return self.cursor.fetchall()
    
    def verificar_produtos_vencidos(self):
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT * FROM produtos 
        WHERE data_validade < ?
        ORDER BY data_validade
        ''', (data_hoje,))
        
        return self.cursor.fetchall()
    
    # Métodos para Fornecedores
    def adicionar_fornecedor(self, nome, documento, telefone, email, endereco, contato):
        self.cursor.execute('''
        INSERT INTO fornecedores (nome, documento, telefone, email, endereco, contato)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, documento, telefone, email, endereco, contato))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def atualizar_fornecedor(self, id, nome, documento, telefone, email, endereco, contato):
        self.cursor.execute('''
        UPDATE fornecedores
        SET nome = ?, documento = ?, telefone = ?, email = ?, endereco = ?, contato = ?
        WHERE id = ?
        ''', (nome, documento, telefone, email, endereco, contato, id))
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
            query += f" WHERE nome LIKE '%{filtro}%' OR documento LIKE '%{filtro}%'"
        
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
    
    def fechar(self):
        self.conn.close()