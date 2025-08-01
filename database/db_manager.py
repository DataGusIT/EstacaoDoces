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
    
    def fechar(self):
        if self.conn:
            self.conn.close()
    
    def buscar_produto_por_codigo_barras(self, codigo_barras):
        """Busca produto por código de barras."""
        # CORREÇÃO: usar self.conn ao invés de self.conexao
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE codigo_barras = ?", (codigo_barras,))
        return cursor.fetchone()

    def buscar_produto_por_nome_exato(self, nome):
        """Busca produto por nome exato."""
        # CORREÇÃO: usar self.conn ao invés de self.conexao
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE LOWER(nome) = LOWER(?)", (nome,))
        return cursor.fetchone()
    
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
            margem_lucro REAL DEFAULT 30.0,
            preco_venda REAL,
            data_validade DATE,
            localizacao TEXT,
            fornecedor_id INTEGER,
            categoria TEXT,  -- NOVO CAMPO
            data_cadastro DATE DEFAULT CURRENT_DATE,

            -- Campos para controle de produtos fracionados
            fracionado INTEGER DEFAULT 0,
            unidade_medida TEXT DEFAULT 'unidade',
            qtd_por_embalagem REAL DEFAULT 1,
            preco_unitario_fracao REAL,
            estoque_fracionado REAL DEFAULT 0,

            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
        )
        ''')
        
        # Tabela de Fornecedores
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS fornecedores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            empresa TEXT NOT NULL,
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
            data_nascimento DATE,
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

        # Tabela de Configurações do Sistema (NOVA)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuracoes (
            chave TEXT PRIMARY KEY,
            valor TEXT NOT NULL
        )
        ''')

        # Tabela de Logs de Atividades (NOVA)
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            level TEXT NOT NULL, -- ex: INFO, WARNING, ERROR, ADMIN
            usuario_login TEXT,
            action TEXT NOT NULL,
            details TEXT
        )
        ''')
        
        # Verificar se existe pelo menos um usuário admin
        self.cursor.execute("SELECT COUNT(*) FROM usuarios WHERE tipo='admin'")
        count = self.cursor.fetchone()[0]

        if count == 0:
            # Criar um usuário admin padrão com hash de senha
            senha_plana = "admin123"
            senha_hash = hashlib.sha256(senha_plana.encode('utf-8')).hexdigest()
            
            self.cursor.execute('''
            INSERT INTO usuarios (nome, login, senha, email, tipo)
            VALUES (?, ?, ?, ?, ?)
            ''', ("Administrador", "admin", senha_hash, "admin@sistema.com", "admin"))

        # Commit das mudanças
        self.conn.commit()
    
    # --- MÉTODOS PARA OTIMIZAÇÃO DA TELA DE ESTOQUE (NOVOS E MODIFICADOS) ---

    def _construir_clausula_where_e_params(self, filtros):
        """
        Helper privado para construir a cláusula WHERE e a lista de parâmetros dinamicamente.
        Isso centraliza toda a lógica de filtragem e evita SQL Injection.
        """
        where_clauses = []
        params = []
        
        # Filtro por termo de pesquisa (nome, código de barras, descrição)
        if filtros.get('termo_pesquisa'):
            termo = f"%{filtros['termo_pesquisa']}%"
            where_clauses.append("(p.nome LIKE ? OR p.descricao LIKE ? OR p.codigo_barras LIKE ?)")
            params.extend([termo, termo, termo])

        # Filtro por categoria
        # O currentData do combo pode vir como None ou uma string vazia se "Todas" for selecionado
        if filtros.get('categoria') and filtros['categoria'] != "todas":
            where_clauses.append("p.categoria = ?")
            params.append(filtros['categoria'])

        # Filtro por nível de estoque
        nivel_estoque = filtros.get('estoque')
        if nivel_estoque and nivel_estoque != "todos":
            # A mesma lógica de cálculo de estoque total que você tinha, mas em SQL
            estoque_calculado_sql = "(CASE WHEN p.fracionado = 1 THEN (p.quantidade * p.qtd_por_embalagem + p.estoque_fracionado) ELSE p.quantidade END)"
            
            if nivel_estoque == "baixo":
                where_clauses.append(f"{estoque_calculado_sql} <= p.estoque_minimo AND p.estoque_minimo > 0")
            elif nivel_estoque == "medio":
                where_clauses.append(f"{estoque_calculado_sql} > p.estoque_minimo AND {estoque_calculado_sql} <= (p.estoque_minimo * 2)")
            elif nivel_estoque == "alto":
                where_clauses.append(f"{estoque_calculado_sql} > (p.estoque_minimo * 2)")

        # Filtro por data de vencimento
        filtro_vencimento = filtros.get('vencimento')
        if filtro_vencimento and filtro_vencimento != "todos":
            hoje = datetime.now().strftime('%Y-%m-%d')
            
            if filtro_vencimento == "vencidos":
                where_clauses.append("date(p.data_validade) < ?")
                params.append(hoje)
            elif filtro_vencimento == "15":
                data_limite = (datetime.now() + timedelta(days=15)).strftime('%Y-%m-%d')
                where_clauses.append("date(p.data_validade) BETWEEN ? AND ?")
                params.extend([hoje, data_limite])
            elif filtro_vencimento == "30":
                data_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
                where_clauses.append("date(p.data_validade) BETWEEN ? AND ?")
                params.extend([hoje, data_limite])

        if not where_clauses:
            return "", []
            
        return "WHERE " + " AND ".join(where_clauses), params

    def listar_produtos_paginado_e_filtrado(self, filtros, pagina, itens_por_pagina):
        """
        NOVO MÉTODO OTIMIZADO: Busca produtos com filtros e paginação.
        Este método substitui listar_produtos, filtrar_produtos e listar_produtos_com_fracionamento.
        """
        offset = (pagina - 1) * itens_por_pagina
        
        # Query base que já calcula o estoque total para produtos fracionados
        base_query = """
            SELECT p.*, f.empresa as fornecedor_nome,
                CASE 
                    WHEN p.fracionado = 1 THEN 
                        (p.quantidade * p.qtd_por_embalagem + p.estoque_fracionado)
                    ELSE p.quantidade
                END as estoque_total_calculado
            FROM produtos p 
            LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        """
        
        where_clause, params = self._construir_clausula_where_e_params(filtros)
        
        query_final = f"{base_query} {where_clause} ORDER BY p.nome LIMIT ? OFFSET ?"
        params.extend([itens_por_pagina, offset])
        
        self.cursor.execute(query_final, params)
        return self.cursor.fetchall()

    def contar_produtos_filtrados(self, filtros):
        """
        NOVO MÉTODO OTIMIZADO: Conta o número total de produtos que correspondem
        aos filtros, necessário para calcular o total de páginas.
        """
        base_query = "SELECT COUNT(p.id) FROM produtos p"
        
        where_clause, params = self._construir_clausula_where_e_params(filtros)
        
        query_final = f"{base_query} {where_clause}"
        
        self.cursor.execute(query_final, params)
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else 0

    # --- MÉTODOS PARA TRANSAÇÕES (PARA IMPORTAÇÃO RÁPIDA DE CSV) ---
    
    def begin_transaction(self):
        """Inicia uma transação."""
        try:
            self.conn.execute("BEGIN TRANSACTION")
        except sqlite3.OperationalError as e:
            # Lida com o caso de já haver uma transação ativa
            print(f"Aviso: {e}")


    def commit_transaction(self):
        """Confirma a transação atual."""
        self.conn.commit()

    def rollback_transaction(self):
        """Reverte a transação atual."""
        self.conn.rollback()

    # Métodos para Produtos (atualizados)
    def adicionar_produto(self, codigo_barras, nome, descricao, quantidade, estoque_minimo,
                preco_compra, margem_lucro, preco_venda, 
                data_validade, localizacao, fornecedor_id, categoria=None,  # NOVO PARÂMETRO
                fracionado=False, unidade_medida="unidade", qtd_por_embalagem=1, 
                preco_unitario_fracao=None, estoque_fracionado=0):

        self.cursor.execute('''
        INSERT INTO produtos (
            codigo_barras, nome, descricao, quantidade, estoque_minimo,
            preco_compra, margem_lucro, preco_venda, 
            data_validade, localizacao, fornecedor_id, categoria,
            fracionado, unidade_medida, qtd_por_embalagem, preco_unitario_fracao, estoque_fracionado
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            codigo_barras, nome, descricao, quantidade, estoque_minimo,
            preco_compra, margem_lucro, preco_venda, 
            data_validade, localizacao, fornecedor_id, categoria,
            1 if fracionado else 0, unidade_medida, qtd_por_embalagem, 
            preco_unitario_fracao, estoque_fracionado
        ))
        self.conn.commit()
        return self.cursor.lastrowid

    def atualizar_produto(self, id, codigo_barras, nome, descricao, quantidade, estoque_minimo,
                    preco_compra, margem_lucro, preco_venda, 
                    data_validade, localizacao, fornecedor_id, categoria=None,  # NOVO PARÂMETRO
                    fracionado=False, unidade_medida="unidade", qtd_por_embalagem=1, 
                    preco_unitario_fracao=None, estoque_fracionado=0):

        self.cursor.execute('''
        UPDATE produtos
        SET codigo_barras = ?, nome = ?, descricao = ?, quantidade = ?, estoque_minimo = ?,
            preco_compra = ?, margem_lucro = ?, preco_venda = ?,
            data_validade = ?, localizacao = ?, fornecedor_id = ?, categoria = ?,
            fracionado = ?, unidade_medida = ?, qtd_por_embalagem = ?, 
            preco_unitario_fracao = ?, estoque_fracionado = ?
        WHERE id = ?
        ''', (
            codigo_barras, nome, descricao, quantidade, estoque_minimo,
            preco_compra, margem_lucro, preco_venda,
            data_validade, localizacao, fornecedor_id, categoria,
            1 if fracionado else 0, unidade_medida, qtd_por_embalagem, 
            preco_unitario_fracao, estoque_fracionado, id
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
        query = 'SELECT p.*, f.empresa as fornecedor_nome FROM produtos p LEFT JOIN fornecedores f ON p.fornecedor_id = f.id'
        
        if filtro:
            query += f" WHERE p.nome LIKE '%{filtro}%' OR p.descricao LIKE '%{filtro}%' OR p.codigo_barras LIKE '%{filtro}%'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def listar_categorias_unicas(self):
        """Retorna lista de categorias únicas dos produtos."""
        self.cursor.execute('''
        SELECT DISTINCT categoria 
        FROM produtos 
        WHERE categoria IS NOT NULL AND categoria != ''
        ORDER BY categoria
        ''')
        return [row[0] for row in self.cursor.fetchall()]

    def verificar_produtos_vencidos(self):
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT p.*, f.empresa as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.data_validade < ?
        ORDER BY p.data_validade
        ''', (data_hoje,))
        
        return self.cursor.fetchall()

    def verificar_produtos_estoque_baixo(self):
        """Verifica produtos com estoque abaixo do mínimo definido."""
        self.cursor.execute('''
        SELECT p.*, f.empresa as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.quantidade <= p.estoque_minimo AND p.estoque_minimo > 0
        ORDER BY p.nome
        ''')
        
        return self.cursor.fetchall()

    def verificar_produtos_vencendo(self, dias=30):
        data_limite = (datetime.now() + timedelta(days=dias)).strftime('%Y-%m-%d')
        data_hoje = datetime.now().strftime('%Y-%m-%d')
        
        self.cursor.execute('''
        SELECT p.*, f.empresa as fornecedor_nome 
        FROM produtos p 
        LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
        WHERE p.data_validade <= ? AND p.data_validade >= ?
        ORDER BY p.data_validade
        ''', (data_limite, data_hoje))
        
        return self.cursor.fetchall()

    def filtrar_produtos(self, filtro_estoque, filtro_vencimento):
        """Filtra produtos por nível de estoque e data de vencimento."""
        hoje = datetime.now().strftime('%Y-%m-%d')
        
        # Base da consulta
        query = '''
        SELECT p.*, f.empresa as fornecedor_nome 
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
    
    def calcular_estoque_total_produto(self, produto_id):
        """Calcula o estoque total considerando embalagens + fracionado"""
        try:
            produto = self.obter_produto(produto_id)
            if not produto:
                return 0
            
            # Se não é fracionado, retorna apenas a quantidade normal
            if not produto['fracionado']:
                return produto['quantidade']
            
            # Se é fracionado, soma: (embalagens * qtd_por_embalagem) + estoque_fracionado
            estoque_embalagens = produto['quantidade'] * produto['qtd_por_embalagem']
            estoque_total = estoque_embalagens + produto['estoque_fracionado']
            
            return estoque_total
        except Exception as e:
            print(f"Erro ao calcular estoque total: {e}")
            return 0
        
    def atualizar_estoque_venda(self, produto_id, quantidade_vendida, is_embalagem):
        """
        Atualiza o estoque de um produto após a venda.
        Retorna (True, "Mensagem de Sucesso") ou (False, "Mensagem de Erro").
        """
        try:
            produto = self.obter_produto(produto_id)
            if not produto:
                return False, "Produto não encontrado."

            if is_embalagem:
                # Venda de embalagem inteira
                if produto['quantidade'] < quantidade_vendida:
                    return False, "Estoque de embalagens insuficiente."
                
                self.cursor.execute('''
                    UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?
                ''', (quantidade_vendida, produto_id))
            else:
                # Venda de unidade fracionada
                if not produto['fracionado']:
                    return False, "Este produto não é vendido de forma fracionada."

                if produto['estoque_fracionado'] < quantidade_vendida:
                    return False, f"Estoque fracionado insuficiente ({produto['estoque_fracionado']} unidades). Quebre uma embalagem na tela de estoque."
                
                self.cursor.execute('''
                    UPDATE produtos SET estoque_fracionado = estoque_fracionado - ? WHERE id = ?
                ''', (quantidade_vendida, produto_id))

            self.conn.commit()
            return True, "Estoque atualizado com sucesso."
        except Exception as e:
            print(f"Erro ao atualizar estoque de venda: {e}")
            return False, f"Erro interno ao atualizar estoque: {e}"

    def quebrar_embalagem(self, produto_id, quantidade_embalagens=1):
        """Quebra embalagens para criar estoque fracionado"""
        try:
            produto = self.obter_produto(produto_id)
            if not produto or not produto['fracionado']:
                return False
            
            if produto['quantidade'] < quantidade_embalagens:
                return False
            
            unidades_geradas = quantidade_embalagens * produto['qtd_por_embalagem']
            
            self.cursor.execute('''
                UPDATE produtos 
                SET quantidade = quantidade - ?, estoque_fracionado = estoque_fracionado + ?
                WHERE id = ?
            ''', (quantidade_embalagens, unidades_geradas, produto_id))
            
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Erro ao quebrar embalagem: {e}")
            return False

    def obter_info_estoque_fracionado(self, produto_id):
        """Retorna informações detalhadas do estoque de um produto fracionado"""
        try:
            produto = self.obter_produto(produto_id)
            if not produto:
                return None
            
            info = {
                'produto_id': produto_id,
                'nome': produto['nome'],
                'fracionado': bool(produto['fracionado']),
                'unidade_medida': produto['unidade_medida'],
                'embalagens_inteiras': produto['quantidade'],
                'estoque_fracionado': produto['estoque_fracionado'] if produto['fracionado'] else 0,
                'qtd_por_embalagem': produto['qtd_por_embalagem'] if produto['fracionado'] else 1,
                'preco_embalagem': produto['preco_venda'],
                'preco_unitario_fracao': produto['preco_unitario_fracao'] if produto['fracionado'] else produto['preco_venda']
            }
            
            if produto['fracionado']:
                # Calcular estoque total em unidades
                info['estoque_total_unidades'] = (produto['quantidade'] * produto['qtd_por_embalagem']) + produto['estoque_fracionado']
            else:
                info['estoque_total_unidades'] = produto['quantidade']
            
            return info
        except Exception as e:
            print(f"Erro ao obter info de estoque fracionado: {e}")
            return None
        
    def listar_produtos_com_fracionamento(self, filtro=None):
        """Lista produtos incluindo informações de fracionamento"""
        try:
            query = '''
            SELECT p.*, f.empresa as fornecedor_nome,
                CASE 
                    WHEN p.fracionado = 1 THEN 
                        (p.quantidade * p.qtd_por_embalagem + p.estoque_fracionado)
                    ELSE p.quantidade
                END as estoque_total_calculado
            FROM produtos p 
            LEFT JOIN fornecedores f ON p.fornecedor_id = f.id
            '''
            
            if filtro:
                query += f" WHERE p.nome LIKE '%{filtro}%' OR p.descricao LIKE '%{filtro}%' OR p.codigo_barras LIKE '%{filtro}%'"
            
            query += " ORDER BY p.nome"
            
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Erro ao listar produtos com fracionamento: {e}")
            return []

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
    def adicionar_fornecedor(self, empresa, representante, frequencia_compra, telefone, email, endereco, contato):
        self.cursor.execute('''
        INSERT INTO fornecedores (empresa, representante, frequencia_compra, telefone, email, endereco, contato)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (empresa, representante, frequencia_compra, telefone, email, endereco, contato))
        self.conn.commit()
        return self.cursor.lastrowid
    
    def atualizar_fornecedor(self, id, empresa, representante, frequencia_compra, telefone, email, endereco, contato):
        self.cursor.execute('''
        UPDATE fornecedores
        SET empresa = ?, representante = ?, frequencia_compra = ?, telefone = ?, email = ?, endereco = ?, contato = ?
        WHERE id = ?
        ''', (empresa, representante, frequencia_compra, telefone, email, endereco, contato, id))
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
            query += f" WHERE empresa LIKE '%{filtro}%' OR representante LIKE '%{filtro}%'"
        
        self.cursor.execute(query)
        return self.cursor.fetchall()
    
    def listar_fornecedores_paginado_e_filtrado(self, filtros, pagina, itens_por_pagina):
        """
        NOVO MÉTODO OTIMIZADO: Busca fornecedores com filtros e paginação.
        """
        offset = (pagina - 1) * itens_por_pagina
        params = []
        
        base_query = "SELECT * FROM fornecedores"
        where_clause = ""
        
        if filtros.get('termo_pesquisa'):
            termo = f"%{filtros['termo_pesquisa']}%"
            # Adicionado busca por mais campos para ser mais útil
            where_clause = "WHERE empresa LIKE ? OR representante LIKE ? OR email LIKE ? OR telefone LIKE ?"
            params.extend([termo, termo, termo, termo])
            
        query_final = f"{base_query} {where_clause} ORDER BY empresa LIMIT ? OFFSET ?"
        params.extend([itens_por_pagina, offset])
        
        self.cursor.execute(query_final, params)
        return self.cursor.fetchall()

    def contar_fornecedores_filtrados(self, filtros):
        """
        NOVO MÉTODO OTIMIZADO: Conta o número total de fornecedores que correspondem
        aos filtros, necessário para calcular o total de páginas.
        """
        params = []
        base_query = "SELECT COUNT(id) FROM fornecedores"
        where_clause = ""

        if filtros.get('termo_pesquisa'):
            termo = f"%{filtros['termo_pesquisa']}%"
            where_clause = "WHERE empresa LIKE ? OR representante LIKE ? OR email LIKE ? OR telefone LIKE ?"
            params.extend([termo, termo, termo, termo])

        query_final = f"{base_query} {where_clause}"
        
        self.cursor.execute(query_final, params)
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else 0
    
    # Métodos para Clientes Atualizados
    def adicionar_cliente(self, nome, data_nascimento, telefone, email, endereco):
        """Adiciona um novo cliente ao banco de dados."""
        try:
            self.cursor.execute('''
            INSERT INTO clientes (nome, data_nascimento, telefone, email, endereco)
            VALUES (?, ?, ?, ?, ?)
            ''', (nome, data_nascimento, telefone, email, endereco))
            self.conn.commit()
            return self.cursor.lastrowid
        except Exception as e:
            print(f"Erro ao adicionar cliente: {e}")
            return False

    def atualizar_cliente(self, id, nome, data_nascimento, telefone, email, endereco):
        """Atualiza os dados de um cliente existente."""
        try:
            self.cursor.execute('''
            UPDATE clientes
            SET nome = ?, data_nascimento = ?, telefone = ?, email = ?, endereco = ?
            WHERE id = ?
            ''', (nome, data_nascimento, telefone, email, endereco, id))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao atualizar cliente: {e}")
            return False

    def excluir_cliente(self, id):
        """Exclui um cliente do banco de dados."""
        try:
            self.cursor.execute('DELETE FROM clientes WHERE id = ?', (id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao excluir cliente: {e}")
            return False

    def obter_cliente(self, id):
        """Obtém os dados de um cliente específico."""
        try:
            self.cursor.execute('SELECT * FROM clientes WHERE id = ?', (id,))
            cliente = self.cursor.fetchone()
            if cliente:
                # Converter para dicionário para facilitar o acesso
                colunas = [description[0] for description in self.cursor.description]
                return dict(zip(colunas, cliente))
            return None
        except Exception as e:
            print(f"Erro ao obter cliente: {e}")
            return None

    def listar_clientes(self, filtro=None):
        """Lista todos os clientes ou filtra por termo de busca."""
        try:
            query = 'SELECT * FROM clientes'
            params = ()
            
            if filtro:
                query += " WHERE nome LIKE ? OR telefone LIKE ? OR email LIKE ?"
                filtro_param = f'%{filtro}%'
                params = (filtro_param, filtro_param, filtro_param)
            
            query += ' ORDER BY nome'
            
            self.cursor.execute(query, params)
            resultados = self.cursor.fetchall()
            
            # Converter para lista de dicionários
            clientes = []
            if resultados:
                colunas = [description[0] for description in self.cursor.description]
                for resultado in resultados:
                    clientes.append(dict(zip(colunas, resultado)))
            
            return clientes
        except Exception as e:
            print(f"Erro ao listar clientes: {e}")
            return []
    
    def listar_clientes_paginado_e_filtrado(self, filtros, pagina, itens_por_pagina):
        """
        NOVO MÉTODO OTIMIZADO: Busca clientes com filtros e paginação.
        """
        offset = (pagina - 1) * itens_por_pagina
        params = []
        
        base_query = "SELECT * FROM clientes"
        where_clause = ""
        
        if filtros.get('termo_pesquisa'):
            termo = f"%{filtros['termo_pesquisa']}%"
            where_clause = "WHERE nome LIKE ? OR telefone LIKE ? OR email LIKE ?"
            params.extend([termo, termo, termo])
            
        query_final = f"{base_query} {where_clause} ORDER BY nome LIMIT ? OFFSET ?"
        params.extend([itens_por_pagina, offset])
        
        self.cursor.execute(query_final, params)
        return self.cursor.fetchall()

    def contar_clientes_filtrados(self, filtros):
        """
        NOVO MÉTODO OTIMIZADO: Conta o número total de clientes que correspondem
        aos filtros para o cálculo de páginas.
        """
        params = []
        base_query = "SELECT COUNT(id) FROM clientes"
        where_clause = ""

        if filtros.get('termo_pesquisa'):
            termo = f"%{filtros['termo_pesquisa']}%"
            where_clause = "WHERE nome LIKE ? OR telefone LIKE ? OR email LIKE ?"
            params.extend([termo, termo, termo])

        query_final = f"{base_query} {where_clause}"
        
        self.cursor.execute(query_final, params)
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else 0
    
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
    
    def listar_promocoes_paginado_e_filtrado(self, filtros, pagina, itens_por_pagina):
        """
        NOVO MÉTODO OTIMIZADO: Busca promoções com filtros e paginação.
        A busca é feita pelo nome do produto associado.
        """
        offset = (pagina - 1) * itens_por_pagina
        params = []
        
        # A query base precisa do JOIN para pesquisar pelo nome do produto
        base_query = """
            SELECT p.*, pr.nome as produto_nome 
            FROM promocoes p 
            LEFT JOIN produtos pr ON p.produto_id = pr.id
        """
        where_clause = ""
        
        # Filtra pelo termo de pesquisa no nome do produto
        if filtros.get('termo_pesquisa'):
            termo = f"%{filtros['termo_pesquisa']}%"
            where_clause = "WHERE pr.nome LIKE ?"
            params.append(termo)
            
        # Ordena por data de fim mais recente, depois por nome
        query_final = f"{base_query} {where_clause} ORDER BY p.data_fim DESC, pr.nome LIMIT ? OFFSET ?"
        params.extend([itens_por_pagina, offset])
        
        self.cursor.execute(query_final, params)
        return self.cursor.fetchall()

    def contar_promocoes_filtradas(self, filtros):
        """
        NOVO MÉTODO OTIMIZADO: Conta o número total de promoções que correspondem
        aos filtros para o cálculo de páginas.
        """
        params = []
        
        # A query também precisa do JOIN para filtrar corretamente
        base_query = """
            SELECT COUNT(p.id) 
            FROM promocoes p 
            LEFT JOIN produtos pr ON p.produto_id = pr.id
        """
        where_clause = ""

        if filtros.get('termo_pesquisa'):
            termo = f"%{filtros['termo_pesquisa']}%"
            where_clause = "WHERE pr.nome LIKE ?"
            params.append(termo)

        query_final = f"{base_query} {where_clause}"
        
        self.cursor.execute(query_final, params)
        resultado = self.cursor.fetchone()
        return resultado[0] if resultado else 0
    
    # Métodos para Usuários
    def obter_usuario_por_id(self, usuario_id):
        """Retorna os dados de um usuário pelo ID, incluindo o status."""
        self.ensure_connection()
        self.cursor.execute('''
            SELECT id, nome, login, email, tipo, ativo, data_cadastro, ultimo_acesso
            FROM usuarios WHERE id = ?
        ''', (usuario_id,))
        
        usuario = self.cursor.fetchone()
        
        if usuario:
            # A conversão para dict(usuario) já inclui a coluna 'ativo'
            # pois ela está no SELECT.
            return dict(usuario)
        else:
            return None

    def autenticar_usuario(self, login, senha):
        """Verifica se o usuário e senha estão corretos usando hash."""
        # Cria o hash da senha fornecida pelo usuário
        senha_hash = hashlib.sha256(senha.encode('utf-8')).hexdigest()
        
        self.cursor.execute('''
            SELECT * FROM usuarios WHERE login = ? AND senha = ? AND ativo = 1
        ''', (login, senha_hash))
        
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

    def cadastrar_usuario(self, nome, login, senha_hash, email, tipo):
        """
        Cadastra um novo usuário.
        Recebe a senha já em formato hash.
        """
        try:
            self.cursor.execute("""
                INSERT INTO usuarios (nome, login, senha, email, tipo)
                VALUES (?, ?, ?, ?, ?)
            """, (nome, login, senha_hash, email, tipo))
            self.conn.commit()
            return True, "Usuário cadastrado com sucesso!"
        except sqlite3.IntegrityError:
            # Erro específico para login ou email duplicado
            return False, "Erro: Login ou e-mail já existem no sistema."
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
            senha_hash = hashlib.sha256(nova_senha.encode('utf-8')).hexdigest()
            
            self.cursor.execute('''
                UPDATE usuarios SET senha = ? WHERE id = ?
            ''', (senha_hash, usuario_id))
            
            self.conn.commit()
            return True, "Senha alterada com sucesso."
        except Exception as e:
            return False, f"Erro ao alterar senha: {str(e)}"
    
    def verificar_usuario_por_login_ou_email(self, identificador):
        """
        Verifica se um usuário existe com base no login ou e-mail.
        Retorna o login do usuário se encontrado, caso contrário, None.
        """
        self.cursor.execute('''
            SELECT login FROM usuarios WHERE (login = ? OR email = ?) AND ativo = 1
        ''', (identificador, identificador))
        resultado = self.cursor.fetchone()
        return resultado['login'] if resultado else None

    def atualizar_senha_por_login(self, login, nova_senha):
        """Atualiza a senha de um usuário com base no seu login."""
        try:
            nova_senha_hash = hashlib.sha256(nova_senha.encode('utf-8')).hexdigest()
            self.cursor.execute('''
                UPDATE usuarios SET senha = ? WHERE login = ?
            ''', (nova_senha_hash, login))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao atualizar senha por login: {e}")
            return False


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
        """
        Registra um item na tabela itens_venda. A atualização de estoque
        deve ser feita separadamente.
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO itens_venda 
                (venda_id, produto_id, quantidade, preco_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?)
            """, (venda_id, produto_id, quantidade, preco_unitario, subtotal))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Erro ao registrar item de venda: {e}")
            return False
    
    def obter_dados_dashboard(self, data_inicio, data_fim):
        """
        NOVA VERSÃO OTIMIZADA: Obtém um conjunto completo de dados para o dashboard,
        incluindo KPIs de vendas, alertas e contagens gerais.
        """
        try:
            if not self.ensure_connection():
                raise Exception("Não foi possível conectar ao banco de dados.")
            
            cursor = self.conn.cursor()

            # --- DADOS DE VENDAS (como antes) ---
            cursor.execute("""
                SELECT id FROM vendas 
                WHERE date(data_hora, 'localtime') BETWEEN ? AND ?
            """, (data_inicio, data_fim))
            venda_ids = tuple(row['id'] for row in cursor.fetchall())

            faturamento_periodo = 0
            num_vendas_periodo = 0
            lucro_periodo = 0
            produtos_mais_vendidos = []
            formas_pagamento = []
            melhores_clientes = []
            vendas_diarias = []

            if venda_ids: # Procede apenas se houver vendas no período
                query_in_ids = f"IN {venda_ids}" if len(venda_ids) > 1 else f"= {venda_ids[0]}"

                cursor.execute(f"SELECT COUNT(*) as num_vendas, SUM(valor_total) as faturamento FROM vendas WHERE id {query_in_ids}")
                vendas_resumo = cursor.fetchone()
                faturamento_periodo = vendas_resumo['faturamento'] or 0
                num_vendas_periodo = vendas_resumo['num_vendas'] or 0

                cursor.execute(f"""
                    SELECT SUM(i.subtotal - (i.quantidade * COALESCE(p.preco_compra, 0))) as lucro
                    FROM itens_venda i JOIN produtos p ON i.produto_id = p.id
                    WHERE i.venda_id {query_in_ids} AND p.preco_compra > 0
                """)
                lucro_resultado = cursor.fetchone()
                lucro_periodo = lucro_resultado['lucro'] if lucro_resultado and lucro_resultado['lucro'] is not None else 0

                cursor.execute(f"SELECT p.nome, SUM(i.quantidade) as quantidade, SUM(i.subtotal) as valor_total FROM itens_venda i JOIN produtos p ON i.produto_id = p.id WHERE i.venda_id {query_in_ids} GROUP BY p.id, p.nome ORDER BY valor_total DESC LIMIT 10")
                produtos_mais_vendidos = [dict(row) for row in cursor.fetchall()]

                cursor.execute(f"SELECT forma_pagamento as forma, SUM(valor_total) as valor_total FROM vendas WHERE id {query_in_ids} GROUP BY forma_pagamento ORDER BY valor_total DESC")
                formas_pagamento = [dict(row) for row in cursor.fetchall()]

                cursor.execute(f"SELECT COALESCE(c.nome, 'Cliente Não Identificado') as nome, COUNT(*) as compras, SUM(v.valor_total) as valor_total FROM vendas v LEFT JOIN clientes c ON v.cliente_id = c.id WHERE v.id {query_in_ids} GROUP BY v.cliente_id ORDER BY valor_total DESC LIMIT 10")
                melhores_clientes = [dict(row) for row in cursor.fetchall()]

            cursor.execute("SELECT date(data_hora, 'localtime') as data, SUM(valor_total) as valor FROM vendas WHERE date(data_hora, 'localtime') BETWEEN ? AND ? GROUP BY data ORDER BY data", (data_inicio, data_fim))
            vendas_diarias = [dict(row) for row in cursor.fetchall()]

            # --- NOVAS CONTAGENS GERAIS ---
            cursor.execute("SELECT COUNT(*) FROM produtos")
            total_produtos = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM clientes")
            total_clientes = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM fornecedores")
            total_fornecedores = cursor.fetchone()[0]
            
            hoje = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM promocoes WHERE data_inicio <= ? AND data_fim >= ?", (hoje, hoje))
            total_promocoes_ativas = cursor.fetchone()[0]

            # --- NOVOS ALERTAS OPERACIONAIS ---
            cursor.execute("SELECT COUNT(*) FROM produtos WHERE quantidade <= estoque_minimo AND estoque_minimo > 0")
            alert_estoque_baixo = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM produtos WHERE date(data_validade) < ?", (hoje,))
            alert_vencidos = cursor.fetchone()[0]

            data_limite_30d = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(*) FROM produtos WHERE date(data_validade) BETWEEN ? AND ?", (hoje, data_limite_30d))
            alert_vencendo_30d = cursor.fetchone()[0]
            
            # --- Monta o dicionário final com todos os dados ---
            resultado = {
                # Dados de Vendas
                'faturamento': faturamento_periodo,
                'num_vendas': num_vendas_periodo,
                'lucro': lucro_periodo,
                'produtos': produtos_mais_vendidos,
                'pagamentos': formas_pagamento,
                'clientes': melhores_clientes,
                'vendas_diarias': vendas_diarias,
                # Contagens Gerais
                'total_produtos': total_produtos,
                'total_clientes': total_clientes,
                'total_fornecedores': total_fornecedores,
                'total_promocoes_ativas': total_promocoes_ativas,
                # Alertas
                'alertas': {
                    'estoque_baixo': alert_estoque_baixo,
                    'vencidos': alert_vencidos,
                    'vencendo_30d': alert_vencendo_30d,
                }
            }

            return resultado
        except Exception as e:
            print(f"Erro detalhado ao obter dados para dashboard: {e}")
            self.registrar_log('ERROR', 'SISTEMA', 'DB_DASHBOARD_FETCH', str(e))
            return None
    
    # --- Métodos para Configurações do Sistema ---

    def obter_configuracao(self, chave, padrao=None):
        """Busca o valor de uma chave de configuração."""
        self.cursor.execute("SELECT valor FROM configuracoes WHERE chave = ?", (chave,))
        resultado = self.cursor.fetchone()
        return resultado['valor'] if resultado else padrao

    def definir_configuracao(self, chave, valor):
        """Define ou atualiza o valor de uma chave de configuração."""
        self.cursor.execute('''
            INSERT INTO configuracoes (chave, valor) VALUES (?, ?)
            ON CONFLICT(chave) DO UPDATE SET valor = EXCLUDED.valor
        ''', (chave, str(valor)))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # --- Métodos para Logs do Sistema ---

    def registrar_log(self, level, usuario_login, action, details=""):
        """Registra uma nova entrada de log."""
        try:
            self.cursor.execute('''
                INSERT INTO logs (level, usuario_login, action, details)
                VALUES (?, ?, ?, ?)
            ''', (level, usuario_login, action, details))
            self.conn.commit()
        except Exception as e:
            print(f"Erro ao registrar log: {e}")

    def listar_logs(self, data_inicio=None, data_fim=None, usuario=None, level=None):
        """Lista os logs com base em filtros."""
        query = "SELECT * FROM logs WHERE 1=1"
        params = []

        if data_inicio:
            query += " AND date(timestamp) >= ?"
            params.append(data_inicio)
        if data_fim:
            query += " AND date(timestamp) <= ?"
            params.append(data_fim)
        if usuario:
            query += " AND usuario_login LIKE ?"
            params.append(f"%{usuario}%")
        if level and level != "Todos":
            query += " AND level = ?"
            params.append(level)
            
        query += " ORDER BY timestamp DESC"
        
        self.cursor.execute(query, params)
        return self.cursor.fetchall()