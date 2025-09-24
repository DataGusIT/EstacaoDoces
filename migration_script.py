import sqlite3
import os
import sys
from datetime import datetime, timedelta
import math

# --- CONFIGURAÇÃO ---
# O script assume que o banco de dados está em uma pasta 'database' relativa
# ao local onde o seu executável (.exe) está instalado.
# O Inno Setup garante que essa estrutura de pastas seja mantida.
DB_FILE = os.path.join('database', 'estoque.db')
LOG_FILE = 'migration_log.txt'

def log(message):
    """Escreve uma mensagem no console e em um arquivo de log."""
    print(message)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")

def column_exists(cursor, table_name, column_name):
    """Verifica se uma coluna já existe em uma tabela."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall()]
    return column_name in columns

def add_column_if_not_exists(cursor, table_name, column_name, column_type):
    """Adiciona uma coluna a uma tabela apenas se ela não existir."""
    if not column_exists(cursor, table_name, column_name):
        log(f"Coluna '{column_name}' não encontrada na tabela '{table_name}'. Adicionando...")
        cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
        log(f"Coluna '{column_name}' adicionada com sucesso.")
    else:
        log(f"Coluna '{column_name}' já existe na tabela '{table_name}'. Nenhuma ação necessária.")

def calcular_consumo_medio_diario(cursor, produto_id, periodo_dias=90):
    """Copia a lógica de cálculo do db_manager para ser autossuficiente."""
    data_inicio = (datetime.now() - timedelta(days=periodo_dias)).strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""
        SELECT SUM(i.quantidade) 
        FROM itens_venda i
        JOIN vendas v ON i.venda_id = v.id
        WHERE i.produto_id = ? AND v.data_hora >= ?
    """, (produto_id, data_inicio))
    total_vendido = cursor.fetchone()[0]
    return (total_vendido / periodo_dias) if total_vendido else 0.0

def main():
    """Função principal que executa a migração."""
    log("--- INICIANDO SCRIPT DE MIGRAÇÃO DE BANCO DE DADOS ---")

    if not os.path.exists(DB_FILE):
        log(f"Banco de dados não encontrado em '{DB_FILE}'. Nenhuma migração necessária (provavelmente uma nova instalação).")
        log("--- MIGRAÇÃO CONCLUÍDA (NENHUMA AÇÃO) ---")
        return

    conn = None
    try:
        log(f"Conectando ao banco de dados: {DB_FILE}")
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # 1. ADICIONAR AS NOVAS COLUNAS À TABELA 'produtos'
        log("Passo 1: Verificando e adicionando novas colunas...")
        add_column_if_not_exists(cursor, 'produtos', 'tempo_reposicao_dias', 'INTEGER DEFAULT 7')
        add_column_if_not_exists(cursor, 'produtos', 'lote_reposicao', 'INTEGER DEFAULT 10')
        add_column_if_not_exists(cursor, 'produtos', 'consumo_medio_diario', 'REAL DEFAULT 0')
        add_column_if_not_exists(cursor, 'produtos', 'estoque_maximo', 'INTEGER DEFAULT 0')
        log("Verificação de colunas concluída.")

        # 2. MIGRAR DADOS ANTIGOS
        log("Passo 2: Migrando o valor do 'estoque_minimo' manual para o novo 'lote_reposicao'...")
        # Esta query só executa se a coluna 'estoque_minimo' existir
        if column_exists(cursor, 'produtos', 'estoque_minimo'):
            cursor.execute("UPDATE produtos SET lote_reposicao = estoque_minimo WHERE estoque_minimo > 0")
            log(f"{cursor.rowcount} produtos tiveram seu 'lote_reposicao' atualizado com base no 'estoque_minimo' antigo.")
        else:
            log("Coluna 'estoque_minimo' antiga não encontrada. Pulando a migração de dados.")

        # 3. RECALCULAR NÍVEIS DE ESTOQUE PARA TODOS OS PRODUTOS
        log("Passo 3: Recalculando os níveis de estoque dinâmicos para todos os produtos existentes...")
        cursor.execute("SELECT id, tempo_reposicao_dias, lote_reposicao FROM produtos")
        produtos = cursor.fetchall()
        
        total_produtos = len(produtos)
        for i, produto in enumerate(produtos):
            produto_id, tempo_reposicao, lote_reposicao = produto
            
            consumo_diario = calcular_consumo_medio_diario(cursor, produto_id)
            estoque_minimo_calc = math.ceil(consumo_diario * tempo_reposicao)
            estoque_maximo_calc = estoque_minimo_calc + lote_reposicao
            
            cursor.execute("""
                UPDATE produtos SET
                    consumo_medio_diario = ?,
                    estoque_minimo = ?,
                    estoque_maximo = ?
                WHERE id = ?
            """, (consumo_diario, estoque_minimo_calc, estoque_maximo_calc, produto_id))
            
            if (i + 1) % 50 == 0 or (i + 1) == total_produtos:
                log(f"  ... {i + 1} de {total_produtos} produtos recalculados.")

        log("Recálculo de todos os produtos concluído.")
        
        # 4. SALVAR AS MUDANÇAS
        conn.commit()
        log("Todas as alterações foram salvas no banco de dados com sucesso.")

    except Exception as e:
        log(f"!!! ERRO CRÍTICO DURANTE A MIGRAÇÃO: {e}")
        if conn:
            conn.rollback()
            log("Todas as alterações foram revertidas (rollback).")
        # Retorna um código de erro para o Inno Setup saber que algo falhou
        sys.exit(1)
        
    finally:
        if conn:
            conn.close()
            log("Conexão com o banco de dados fechada.")
    
    log("--- MIGRAÇÃO CONCLUÍDA COM SUCESSO ---")

if __name__ == '__main__':
    # Define o diretório de trabalho para o local do script,
    # importante para o Inno Setup encontrar os caminhos relativos.
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()