import sqlite3
from datetime import datetime
import shutil
import os

def migrar_tabela_produtos(cursor):
    """Migra a tabela produtos para a nova estrutura com novos campos."""
    cursor.execute("PRAGMA table_info(produtos)")
    colunas = cursor.fetchall()
    colunas_existentes = [col[1] for col in colunas]

    # Verificar se já está na nova estrutura
    if 'fracionado' in colunas_existentes and 'preco_unitario_fracao' in colunas_existentes:
        print("Tabela produtos já está atualizada. Nenhuma migração necessária.")
        return []

    print("Iniciando migração da tabela produtos...")

    # Criar tabela temporária com a nova estrutura
    cursor.execute('''
    CREATE TABLE produtos_temp (
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
        data_cadastro DATE DEFAULT CURRENT_DATE,
        fracionado INTEGER DEFAULT 0,
        unidade_medida TEXT DEFAULT 'unidade',
        qtd_por_embalagem REAL DEFAULT 1,
        preco_unitario_fracao REAL,
        estoque_fracionado REAL DEFAULT 0,
        FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
    )
    ''')

    # Copiar os dados existentes
    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    for produto in produtos:
        produto_dict = dict(produto)

        # Inserir dados na nova tabela
        cursor.execute('''
        INSERT INTO produtos_temp (
            id, codigo_barras, nome, descricao, quantidade, estoque_minimo,
            preco_compra, margem_lucro, preco_venda, data_validade,
            localizacao, fornecedor_id, data_cadastro,
            fracionado, unidade_medida, qtd_por_embalagem,
            preco_unitario_fracao, estoque_fracionado
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            produto_dict["id"],
            produto_dict.get("codigo_barras", ""),
            produto_dict["nome"],
            produto_dict.get("descricao", ""),
            produto_dict.get("quantidade", 0),
            produto_dict.get("estoque_minimo", 0),
            produto_dict.get("preco_compra", 0.0),
            produto_dict.get("margem_lucro", 30.0),
            produto_dict.get("preco_venda", 0.0),
            produto_dict.get("data_validade", None),
            produto_dict.get("localizacao", ""),
            produto_dict.get("fornecedor_id", None),
            produto_dict.get("data_cadastro", datetime.now().strftime("%Y-%m-%d")),
            0,                 # fracionado
            'unidade',         # unidade_medida
            1,                 # qtd_por_embalagem
            None,              # preco_unitario_fracao
            0.0                # estoque_fracionado
        ))

    # Substituir a tabela antiga
    cursor.execute("DROP TABLE produtos")
    cursor.execute("ALTER TABLE produtos_temp RENAME TO produtos")

    print("Tabela produtos migrada com sucesso!")
    return ["fracionado", "unidade_medida", "qtd_por_embalagem", "preco_unitario_fracao", "estoque_fracionado"]

def migrar_banco_dados_completo(db_path):
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        print("Migrando tabela de produtos...")
        migrar_tabela_produtos(cursor)

        conn.commit()
        conn.close()
        print("Migração completa com sucesso.")
        return True
    except Exception as e:
        print(f"Erro durante a migração: {e}")
        return False

def backup_banco_dados(db_path):
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{db_path}.backup_{timestamp}"
        shutil.copy2(db_path, backup_path)
        print(f"Backup criado com sucesso: {backup_path}")
        return True
    except Exception as e:
        print(f"Erro ao criar backup: {str(e)}")
        return False

if __name__ == "__main__":
    DB_PATH = "database/estoque.db"
    
    if backup_banco_dados(DB_PATH):
        if migrar_banco_dados_completo(DB_PATH):
            print("Migração concluída com sucesso!")
        else:
            print("Erro na migração.")
    else:
        print("Backup falhou. Migração cancelada.")
