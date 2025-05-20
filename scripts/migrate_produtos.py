import sqlite3
from datetime import datetime, timedelta

def migrar_banco_dados(db_path):
    """
    Migra o banco de dados para a nova estrutura com os campos adicionados.

    Args:
        db_path: Caminho para o arquivo do banco de dados SQLite

    Returns:
        bool: True se a migração foi bem-sucedida, False caso contrário
    """
    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Verificar se a tabela produtos existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produtos'")
        if not cursor.fetchone():
            print("Tabela de produtos não encontrada. Criando nova tabela...")
            criar_tabela_produtos(cursor)
        else:
            print("Migrando tabela de produtos existente...")
            migrar_tabela_produtos(cursor)

        conn.commit()
        conn.close()
        print("Migração concluída com sucesso!")
        return True

    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False

def criar_tabela_produtos(cursor):
    """Cria a tabela de produtos com a nova estrutura."""
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_barras TEXT,
        nome TEXT NOT NULL,
        descricao TEXT,
        quantidade INTEGER DEFAULT 0,
        estoque_minimo INTEGER DEFAULT 0,
        unidades_por_embalagem INTEGER DEFAULT 1,
        controle_fracionado BOOLEAN DEFAULT 0,
        unidades_restantes INTEGER DEFAULT 0,
        preco_compra REAL,
        margem_lucro REAL DEFAULT 30.0,
        preco_venda REAL,
        data_validade DATE,
        localizacao TEXT,
        fornecedor_id INTEGER,
        data_cadastro DATE DEFAULT CURRENT_DATE,
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
    )
    ''')

def migrar_tabela_produtos(cursor):
    """Migra a tabela existente para incluir os novos campos."""
    cursor.execute("PRAGMA table_info(produtos)")
    colunas = cursor.fetchall()
    colunas_existentes = [coluna[1] for coluna in colunas]

    if "codigo_barras" not in colunas_existentes:
        print("Adicionando coluna codigo_barras...")
        cursor.execute("ALTER TABLE produtos ADD COLUMN codigo_barras TEXT")

    if "estoque_minimo" not in colunas_existentes:
        print("Adicionando coluna estoque_minimo...")
        cursor.execute("ALTER TABLE produtos ADD COLUMN estoque_minimo INTEGER DEFAULT 0")

    if "margem_lucro" not in colunas_existentes:
        print("Adicionando coluna margem_lucro...")
        cursor.execute("ALTER TABLE produtos ADD COLUMN margem_lucro REAL DEFAULT 30.0")
        print("Calculando margem de lucro para produtos existentes...")
        cursor.execute('''
        UPDATE produtos 
        SET margem_lucro = ((preco_venda / preco_compra) - 1) * 100
        WHERE preco_compra > 0 AND preco_venda > 0
        ''')

    if "unidades_por_embalagem" not in colunas_existentes:
        print("Adicionando coluna unidades_por_embalagem...")
        cursor.execute("ALTER TABLE produtos ADD COLUMN unidades_por_embalagem INTEGER DEFAULT 1")

    if "controle_fracionado" not in colunas_existentes:
        print("Adicionando coluna controle_fracionado...")
        cursor.execute("ALTER TABLE produtos ADD COLUMN controle_fracionado BOOLEAN DEFAULT 0")

    if "unidades_restantes" not in colunas_existentes:
        print("Adicionando coluna unidades_restantes...")
        cursor.execute("ALTER TABLE produtos ADD COLUMN unidades_restantes INTEGER DEFAULT 0")

if __name__ == "__main__":
    DB_PATH = "database/estoque.db"
    sucesso = migrar_banco_dados(DB_PATH)

    if sucesso:
        print("Migração do banco de dados concluída com sucesso!")
    else:
        print("Falha na migração do banco de dados. Verifique os erros acima.")
