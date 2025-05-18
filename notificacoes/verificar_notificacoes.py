#!/usr/bin/env python3
import os
import sys
import argparse
from datetime import datetime

# Adiciona o diretório pai ao path para importar os módulos corretamente
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# Importa os módulos do sistema
from database.db_manager import DatabaseManager
from notificacao_service import NotificacaoService

def main():
    """
    Script principal para verificar condições de estoque e enviar notificações
    
    Uso:
        python verificar_notificacoes.py [--estoque] [--vencimento] [--all] [--force]
        
    Argumentos:
        --estoque: Verifica apenas produtos com estoque baixo
        --vencimento: Verifica apenas produtos próximos do vencimento
        --all: Verifica todas as condições (padrão se nenhum argumento for fornecido)
        --force: Força a verificação mesmo que tenha sido feita recentemente
    """
    parser = argparse.ArgumentParser(description='Verifica condições de estoque e envia notificações')
    parser.add_argument('--estoque', action='store_true', help='Verifica apenas produtos com estoque baixo')
    parser.add_argument('--vencimento', action='store_true', help='Verifica apenas produtos próximos do vencimento')
    parser.add_argument('--all', action='store_true', help='Verifica todas as condições')
    parser.add_argument('--force', action='store_true', help='Força a verificação mesmo que tenha sido feita recentemente')
    
    args = parser.parse_args()
    
    # Se nenhum argumento for fornecido, assume --all
    if not (args.estoque or args.vencimento or args.all):
        args.all = True
    
    print(f"Iniciando verificação em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # Inicializa o gerenciador de banco de dados
        db_path = os.path.join(parent_dir, 'database', 'estoque.db')
        db_manager = DatabaseManager(db_file=db_path)
        
        # Inicializa o serviço de notificações
        notificacao_service = NotificacaoService(db_manager)
        
        # Se forçar verificação, redefine última verificação
        if args.force:
            print("Forçando verificação (ignorando intervalo de tempo)...")
            if args.estoque or args.all:
                notificacao_service.config['notificacoes']['estoque_baixo']['ultima_verificacao'] = None
            if args.vencimento or args.all:
                notificacao_service.config['notificacoes']['vencimento']['ultima_verificacao'] = None
            notificacao_service._salvar_config()
        
        # Executa as verificações conforme os argumentos
        if args.all:
            print("Verificando todas as condições...")
            resultados = notificacao_service.verificar_todas_notificacoes()
            print(f"Resultados: {resultados}")
        else:
            if args.estoque:
                print("Verificando produtos com estoque baixo...")
                resultado = notificacao_service.verificar_estoque_baixo()
                print(f"Resultado estoque baixo: {'Verificado' if resultado else 'Não verificado/enviado'}")
            
            if args.vencimento:
                print("Verificando produtos próximos do vencimento...")
                resultado = notificacao_service.verificar_produtos_vencendo()
                print(f"Resultado produtos vencendo: {'Verificado' if resultado else 'Não verificado/enviado'}")
        
        print("Verificação concluída com sucesso.")
        
    except Exception as e:
        print(f"Erro durante a verificação: {e}")
        sys.exit(1)
    
    print(f"Verificação finalizada em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    sys.exit(0)

if __name__ == "__main__":
    main()