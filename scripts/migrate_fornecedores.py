import sqlite3
from datetime import datetime, timedelta

def migrar_banco_dados(db_path):
    """
    Migra o banco de dados para a nova estrutura de fornecedores.
    
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
        
        # Verificar se a tabela fornecedores existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fornecedores'")
        if not cursor.fetchone():
            print("Tabela de fornecedores não encontrada. Criando nova tabela...")
            criar_tabela_fornecedores(cursor)
        else:
            print("Migrando tabela de fornecedores existente...")
            migrar_tabela_fornecedores(cursor)
            
        conn.commit()
        conn.close()
        print("Migração concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False

def criar_tabela_fornecedores(cursor):
    """Cria a tabela de fornecedores com a nova estrutura."""
    cursor.execute('''
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

def migrar_tabela_fornecedores(cursor):
    """Migra a tabela existente para incluir os novos campos e remover documento."""
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(fornecedores)")
    colunas = cursor.fetchall()
    colunas_existentes = [coluna[1] for coluna in colunas]
    
    # Verificar se precisa fazer a migração
    precisa_migrar = "documento" in colunas_existentes or "representante" not in colunas_existentes or "frequencia_compra" not in colunas_existentes
    
    if not precisa_migrar:
        print("Tabela já está no formato mais recente. Não é necessário migrar.")
        return []
    
    print("Iniciando migração da tabela fornecedores...")
    
    # Criar tabela temporária com a nova estrutura
    cursor.execute('''
    CREATE TABLE fornecedores_temp (
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
    
    # Selecionar dados da tabela original
    cursor.execute("SELECT * FROM fornecedores")
    fornecedores = cursor.fetchall()
    
    # Inserir os dados na tabela temporária com a nova estrutura
    for fornecedor in fornecedores:
        # Converter de sqlite.Row para dicionário para fácil acesso
        fornecedor_dict = dict(fornecedor)
        
        # Valores padrão para os novos campos
        representante = ""
        frequencia_compra = "Média"  # Valor padrão
        
        # Se existe documento, usar ele como nome do representante (opcional)
        if "documento" in fornecedor_dict and fornecedor_dict["documento"]:
            representante = f"Migrado de documento: {fornecedor_dict['documento']}"
        
        # Preparar os dados para inserção
        cursor.execute('''
        INSERT INTO fornecedores_temp (
            id, nome, representante, frequencia_compra, telefone, email, endereco, contato, data_cadastro
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            fornecedor_dict["id"],
            fornecedor_dict["nome"],
            representante,
            frequencia_compra,
            fornecedor_dict.get("telefone", ""),
            fornecedor_dict.get("email", ""),
            fornecedor_dict.get("endereco", ""),
            fornecedor_dict.get("contato", ""),
            fornecedor_dict.get("data_cadastro", datetime.now().strftime("%Y-%m-%d"))
        ))
    
    # Deletar a tabela original
    cursor.execute("DROP TABLE fornecedores")
    
    # Renomear a tabela temporária para o nome original
    cursor.execute("ALTER TABLE fornecedores_temp RENAME TO fornecedores")
    
    print("Tabela fornecedores migrada com sucesso!")
    return ["representante", "frequencia_compra"]

def migrar_queries_fornecedores(cursor):
    """Verifica e atualiza consultas SQL que possam estar usando a antiga estrutura."""
    # Isso é opcional e depende de como as consultas são armazenadas no seu sistema
    # Aqui seria o lugar para atualizar views, triggers, etc. que façam referência ao campo documento
    pass

def backup_banco_dados(db_path):
    """Cria um backup do banco de dados antes da migração."""
    import shutil
    import os
    from datetime import datetime
    
    # Gerar nome do arquivo de backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}.backup_{timestamp}"
    
    # Criar cópia do arquivo
    try:
        shutil.copy2(db_path, backup_path)
        print(f"Backup criado com sucesso: {backup_path}")
        return True
    except Exception as e:
        print(f"Erro ao criar backup: {str(e)}")
        return False

if __name__ == "__main__":
    # Caminho padrão do banco de dados
    DB_PATH = "database/estoque.db"
    
    # Criar backup antes da migração
    if backup_banco_dados(DB_PATH):
        # Execute a migração
        sucesso = migrar_banco_dados(DB_PATH)
        
        if sucesso:
            print("Migração da tabela de fornecedores concluída com sucesso!")
        else:
            print("Falha na migração. Verifique os erros acima.")
    else:
        print("Migração cancelada devido à falha na criação do backup.")