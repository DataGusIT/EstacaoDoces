import sqlite3
from datetime import datetime
import os

def migrar_banco_fornecedores(db_path):
    """
    Migra o banco de dados para a nova estrutura de fornecedores,
    renomeando o campo 'nome' para 'empresa'.
    
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
        
        # Verificar se a tabela fornecedores existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fornecedores'")
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            print("Tabela de fornecedores não encontrada. Criando nova tabela...")
            criar_tabela_fornecedores_nova(cursor)
        else:
            print("Migrando tabela de fornecedores existente...")
            migrar_tabela_fornecedores(cursor)
            
        conn.commit()
        conn.close()
        print("Migração de fornecedores concluída com sucesso!")
        return True
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        return False

def criar_tabela_fornecedores_nova(cursor):
    """Cria a tabela de fornecedores com a nova estrutura."""
    cursor.execute('''
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
    print("Nova tabela de fornecedores criada com sucesso!")

def migrar_tabela_fornecedores(cursor):
    """Migra a tabela existente para a nova estrutura."""
    
    # Verificar colunas existentes
    cursor.execute("PRAGMA table_info(fornecedores)")
    colunas = cursor.fetchall()
    colunas_existentes = [coluna[1] for coluna in colunas]
    
    print(f"Colunas existentes: {colunas_existentes}")
    
    # Verificar se precisa fazer migração
    tem_nome = "nome" in colunas_existentes
    tem_empresa = "empresa" in colunas_existentes
    
    if tem_nome and not tem_empresa:
        print("Executando migração: renomeando 'nome' para 'empresa'...")
        migrar_estrutura_fornecedores(cursor)
    elif tem_empresa:
        print("Tabela já está na estrutura correta!")
        return
    else:
        print("Tabela não possui campo 'nome' nem 'empresa'. Adicionando campo 'empresa'...")
        cursor.execute("ALTER TABLE fornecedores ADD COLUMN empresa TEXT NOT NULL DEFAULT ''")
    
    print("Migração da estrutura concluída!")

def migrar_estrutura_fornecedores(cursor):
    """Executa a migração completa da estrutura da tabela."""
    
    # 1. Criar tabela temporária com nova estrutura
    cursor.execute('''
    CREATE TABLE fornecedores_temp (
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
    
    # 2. Copiar dados da tabela antiga (renomeando 'nome' para 'empresa')
    cursor.execute('''
    INSERT INTO fornecedores_temp (
        id, empresa, representante, frequencia_compra, 
        telefone, email, endereco, contato, data_cadastro
    )
    SELECT 
        id, 
        COALESCE(nome, '') as empresa,
        representante,
        frequencia_compra,
        telefone,
        email,
        endereco,
        contato,
        COALESCE(data_cadastro, date('now'))
    FROM fornecedores
    ''')
    
    # 3. Remover tabela antiga
    cursor.execute("DROP TABLE fornecedores")
    
    # 4. Renomear tabela temporária
    cursor.execute("ALTER TABLE fornecedores_temp RENAME TO fornecedores")
    
    print("Estrutura da tabela migrada com sucesso!")
    print("- Campo 'nome' renomeado para 'empresa'")

def verificar_migracao(db_path):
    """Verifica se a migração foi bem-sucedida."""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("PRAGMA table_info(fornecedores)")
        colunas = cursor.fetchall()
        
        print("\n=== VERIFICAÇÃO DA MIGRAÇÃO ===")
        print("Estrutura atual da tabela 'fornecedores':")
        for coluna in colunas:
            print(f"  - {coluna[1]} ({coluna[2]})")
        
        # Contar registros
        cursor.execute("SELECT COUNT(*) FROM fornecedores")
        total_fornecedores = cursor.fetchone()[0]
        print(f"\nTotal de fornecedores na tabela: {total_fornecedores}")
        
        # Verificar se campos obrigatórios existem
        colunas_nomes = [coluna[1] for coluna in colunas]
        campos_esperados = ['id', 'empresa', 'representante', 'frequencia_compra', 
                           'telefone', 'email', 'endereco', 'contato', 'data_cadastro']
        
        print("\nVerificação dos campos:")
        for campo in campos_esperados:
            status = "✓" if campo in colunas_nomes else "✗"
            print(f"  {status} {campo}")
        
        # Verificar se campo 'nome' foi removido
        if 'nome' not in colunas_nomes:
            print("  ✓ Campo 'nome' removido com sucesso")
        else:
            print("  ✗ Campo 'nome' ainda existe!")
        
        # Mostrar alguns registros como exemplo
        if total_fornecedores > 0:
            cursor.execute("SELECT id, empresa, representante FROM fornecedores LIMIT 3")
            registros = cursor.fetchall()
            print("\nExemplo de registros migrados:")
            for registro in registros:
                print(f"  ID: {registro[0]} | Empresa: {registro[1]} | Representante: {registro[2]}")
        
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
    
    print("=== MIGRAÇÃO DO BANCO DE DADOS - FORNECEDORES ===")
    print(f"Banco de dados: {DB_PATH}")
    print("Migração: campo 'nome' → 'empresa'")
    
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
    sucesso = migrar_banco_fornecedores(DB_PATH)
    
    if sucesso:
        print("\n3. Verificando migração...")
        verificar_migracao(DB_PATH)
        print("\n=== MIGRAÇÃO CONCLUÍDA COM SUCESSO! ===")
        print("Lembre-se de atualizar seu código para usar o novo campo 'empresa'")
        print("Exemplo: cursor.execute('SELECT empresa FROM fornecedores')")
    else:
        print("\n=== FALHA NA MIGRAÇÃO ===")
        if backup_path:
            print(f"Restore o backup se necessário: {backup_path}")
        print("Verifique os erros acima e tente novamente.")