# Sistema de Controle de Estoque para Bomboniere

> Sistema completo de gestão de estoque desenvolvido em Python com interface gráfica moderna

[![Status](https://img.shields.io/badge/Status-Finalizado-success)](https://github.com/seu-usuario/bomboniere-estoque)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB)](https://python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-Interface-41CD52)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## Sobre

Sistema completo de controle de estoque focado em pequenas empresas como bombonieres, lojas de conveniência e mercadinhos. Desenvolvido com Python e PyQt5, oferece uma interface intuitiva e funcionalidades robustas para gestão empresarial.

## Funcionalidades

### 📦 Gestão de Produtos
- Cadastro completo com validação de data de validade
- Controle de entradas e saídas de estoque
- Organização por categorias
- Alertas para produtos vencidos ou com estoque baixo

### 👥 Gestão de Relacionamentos
- Cadastro de clientes com histórico de compras
- Gerenciamento de fornecedores
- Sistema de promoções com prazo de validade

### 📊 Relatórios e Analytics
- Relatórios em PDF e Excel
- Painel com gráficos de vendas
- Análise de produtos mais vendidos
- Controle de estoques críticos

### 🔐 Controle de Acesso
- Sistema de login com níveis de permissão
- Perfis de administrador e operador
- Backup automático de dados

### 🔍 Recursos Avançados
- Busca inteligente com filtros
- Notificações visuais e sonoras
- Interface responsiva e personalizável

## Tecnologias

### Core
- **Python 3.8+** - Linguagem principal
- **PyQt5** - Framework para interface gráfica
- **SQLite3** - Banco de dados local
- **Qt Designer** - Design de interfaces

### Ferramentas
- **QSS (Qt Style Sheets)** - Estilização personalizada
- **PyInstaller** - Empacotamento para executável
- **ReportLab** - Geração de relatórios PDF

## Pré-requisitos

- [Python 3.8+](https://python.org/downloads/)
- Sistema operacional Windows, Linux ou macOS
- 50MB de espaço livre em disco

## Instalação

1. **Clone o repositório**
   ```bash
   git clone https://github.com/seu-usuario/bomboniere-estoque.git
   cd bomboniere-estoque
   ```

2. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
   
   Ou instale manualmente:
   ```bash
   pip install pyqt5 sqlite3 reportlab
   ```

3. **Execute o sistema**
   ```bash
   python main.py
   ```

### Gerar Executável

Para criar um executável standalone:

```bash
pip install pyinstaller
pyinstaller --noconsole --onefile --name "Sistema-Estoque" main.py
```

O executável será gerado na pasta `dist/`.

## Uso

### Primeiro Acesso

1. Execute o sistema
2. Por padrão as credenciais são 'admin' e 'admin123'
3. Configure as categorias de produtos
4. Cadastre fornecedores e produtos iniciais

### Operação Diária

1. **Entrada de Produtos**: Registre chegada de mercadorias
2. **Vendas**: Lance saídas do estoque
3. **Relatórios**: Acompanhe performance através dos dashboards
4. **Manutenção**: Configure alertas e faça backups regulares

### Banco de Dados

O sistema cria automaticamente o banco SQLite na primeira execução. Para configurações avançadas, edite `manager.py`:

```python
# Configurações do banco
DB_PATH = 'data/estoque.db'
BACKUP_INTERVAL = 24  # horas
```

## Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## FAQ

**P: O sistema funciona offline?**
R: Sim, totalmente offline usando SQLite local.

**P: Posso personalizar a interface?**
R: Sim, através dos arquivos QSS e Qt Designer.

**P: Há limite de produtos?**
R: Não há limite técnico, apenas de hardware disponível.

## Suporte

Para suporte técnico ou dúvidas:

- **Email**: [g.moreno.souza05@gmail.com](mailto:g.moreno.souza05@gmail.com)  

## Licença

Este projeto está licenciado sob uma Licença Proprietária - veja o arquivo [LICENSE](LICENSE) para detalhes.

**Uso Restrito**: Este software é de propriedade exclusiva do autor. Uso comercial ou redistribuição requer autorização expressa.

---

<div align="center">
  Desenvolvido por Gustavo Moreno e Adiel Salviano  
  <br>
  <a href="https://www.linkedin.com/in/gustavomorenoit" target="_blank">
    🌐 LinkedIn
  </a>
</div>

