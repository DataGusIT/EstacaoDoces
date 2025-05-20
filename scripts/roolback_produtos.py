import sqlite3

def desfazer_migracao(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Etapa 1: Renomear a tabela antiga
        cursor.execute("ALTER TABLE produtos RENAME TO produtos_antiga")

        # Etapa 2: Criar a nova tabela sem os campos adicionados pela migração
        cursor.execute('''
        CREATE TABLE produtos (
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
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores (id)
        )
        ''')

        # Etapa 3: Copiar os dados antigos para a nova tabela (excluindo colunas adicionadas)
        cursor.execute('''
        INSERT INTO produtos (
            id, codigo_barras, nome, descricao, quantidade,
            estoque_minimo, preco_compra, margem_lucro, preco_venda,
            data_validade, localizacao, fornecedor_id, data_cadastro
        )
        SELECT 
            id, codigo_barras, nome, descricao, quantidade,
            estoque_minimo, preco_compra, margem_lucro, preco_venda,
            data_validade, localizacao, fornecedor_id, data_cadastro
        FROM produtos_antiga
        ''')

        # Etapa 4: Remover a tabela antiga
        cursor.execute("DROP TABLE produtos_antiga")

        conn.commit()
        conn.close()
        print("Migração desfeita com sucesso!")
        return True

    except Exception as e:
        print(f"Erro ao desfazer a migração: {str(e)}")
        return False

if __name__ == "__main__":
    DB_PATH = "database/estoque.db"
    desfazer_migracao(DB_PATH)
