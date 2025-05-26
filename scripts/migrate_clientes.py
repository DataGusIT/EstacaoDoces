import sqlite3
from datetime import datetime, timedelta
import os

def migrar_banco_clientes(db_path):
    """
    Migra o banco de dados para a nova estrutura de clientes,
    removendo o campo 'documento' e adicionando 'data_nascimento'.
    
    Args:
        db_path: Caminho para o arquivo do banco de dados SQLite
    
    Returns:
        bool: True se a migração foi bem-sucedida, False caso contrário
    """
    try:
        # Verificar se o arquivo existe
        if not os.path.exists(db_path):
            print(f"Arquivo de banco de dados não encontrado: {db_path}")
            return False
        
        # Conectar ao banco de dados
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Verificar se a tabela clientes existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='clientes'")
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            print("Tabela de clientes não encontrada. Criando nova tabela...")
            criar_tabela_clientes_nova(cursor)
        else:
            print("Migrando tabela de clientes existente...")
            migrar_tabela_clientes(cursor)
            
        conn.commit()
        conn.close()
        print("Migração de clientes concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False

def criar_tabela_clientes_nova(cursor):
    """Cria a tabela de clientes com a nova estrutura."""
    cursor.execute('''
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
    print("Nova tabela de clientes criada com sucesso!")

def migrar_tabela_clientes(cursor):
    """Migra a tabela existente para a nova estrutura."""
    
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(clientes)")
    colunas = cursor.fetchall()
    colunas_existentes = [coluna[1] for coluna in colunas]
    
    print(f"Colunas existentes: {colunas_existentes}")
    
    # Verificar se precisa fazer migração completa
    tem_documento = "documento" in colunas_existentes
    tem_data_nascimento = "data_nascimento" in colunas_existentes
    
    if tem_documento and not tem_data_nascimento:
        print("Executando migração completa: removendo 'documento' e adicionando 'data_nascimento'...")
        migrar_estrutura_completa(cursor)
    elif not tem_data_nascimento:
        print("Adicionando apenas campo 'data_nascimento'...")
        cursor.execute("ALTER TABLE clientes ADD COLUMN data_nascimento DATE")
    else:
        print("Tabela já está na estrutura correta!")
        return
    
    print("Migração da estrutura concluída!")

def migrar_estrutura_completa(cursor):
    """Executa a migração completa da estrutura da tabela."""
    
    # 1. Criar tabela temporária com nova estrutura
    cursor.execute('''
    CREATE TABLE clientes_temp (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        data_nascimento DATE,
        telefone TEXT,
        email TEXT,
        endereco TEXT,
        data_cadastro DATE DEFAULT CURRENT_DATE
    )
    ''')
    
    # 2. Copiar dados da tabela antiga (sem o campo documento)
    cursor.execute('''
    INSERT INTO clientes_temp (id, nome, telefone, email, endereco, data_cadastro)
    SELECT id, nome, telefone, email, endereco, 
           COALESCE(data_cadastro, date('now'))
    FROM clientes
    ''')
    
    # 3. Remover tabela antiga
    cursor.execute("DROP TABLE clientes")
    
    # 4. Renomear tabela temporária
    cursor.execute("ALTER TABLE clientes_temp RENAME TO clientes")
    
    print("Estrutura da tabela migrada com sucesso!")
    print("- Campo 'documento' removido")
    print("- Campo 'data_nascimento' adicionado")

def verificar_migracao(db_path):
    """Verifica se a migração foi bem-sucedida."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(clientes)")
        colunas = cursor.fetchall()
        
        print("\n=== VERIFICAÇÃO DA MIGRAÇÃO ===")
        print("Estrutura atual da tabela 'clientes':")
        for coluna in colunas:
            print(f"  - {coluna[1]} ({coluna[2]})")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM clientes")
        total_clientes = cursor.fetchone()[0]
        print(f"\nTotal de clientes na tabela: {total_clientes}")
        
        # Verificar se campos obrigatórios existem
        colunas_nomes = [coluna[1] for coluna in colunas]
        campos_esperados = ['id', 'nome', 'data_nascimento', 'telefone', 'email', 'endereco', 'data_cadastro']
        
        print("\nVerificação dos campos:")
        for campo in campos_esperados:
            status = "✓" if campo in colunas_nomes else "✗"
            print(f"  {status} {campo}")
        
        # Verificar se campo 'documento' foi removido
        if 'documento' not in colunas_nomes:
            print("  ✓ Campo 'documento' removido com sucesso")
        else:
            print("  ✗ Campo 'documento' ainda existe!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro na verificação: {str(e)}")
        return False

def backup_banco(db_path):
    """Cria um backup do banco antes da migração."""
    try:
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Copiar arquivo
        import shutil
        shutil.copy2(db_path, backup_path)
        
        print(f"Backup criado: {backup_path}")
        return backup_path
        
    except Exception as e:
        print(f"Erro ao criar backup: {str(e)}")
        return None

if __name__ == "__main__":
    # Caminho do banco de dados
    DB_PATH = "database/estoque.db"  # Ajuste conforme necessário
    
    print("=== MIGRAÇÃO DO BANCO DE DADOS - CLIENTES ===")
    print(f"Banco de dados: {DB_PATH}")
    
    # Criar backup antes da migração
    print("\n1. Criando backup...")
    backup_path = backup_banco(DB_PATH)
    
    if backup_path:
        print("Backup criado com sucesso!")
    else:
        resposta = input("Não foi possível criar backup. Continuar mesmo assim? (s/N): ")
        if resposta.lower() != 's':
            print("Migração cancelada.")
            exit()
    
    # Executar migração
    print("\n2. Executando migração...")
    sucesso = migrar_banco_clientes(DB_PATH)
    
    if sucesso:
        print("\n3. Verificando migração...")
        verificar_migracao(DB_PATH)
        print("\n=== MIGRAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Lembre-se de atualizar seu código para usar o novo campo 'data_nascimento'")
    else:
        print("\n=== FALHA NA MIGRAÇÃO ===")
        if backup_path:
            print(f"Restore o backup se necessário: {backup_path}")
        print("Verifique os erros acima e tente novamente.")