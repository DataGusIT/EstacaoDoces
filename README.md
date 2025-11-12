# GestorX - Sistema de Gestão Empresarial

> Sistema de gestão para desktop, focado em pequenos e médios negócios. Desenvolvido em Python como um projeto piloto acadêmico, baseado nas necessidades de um cliente real.

[![Status](https://img.shields.io/badge/Status-Desenvolvimento-success)](https://github.com/seu-usuario/gestorx)
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB)](https://python.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-Interface-41CD52)](https://pypi.org/project/PyQt5/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

## Sobre o Projeto

O **GestorX** é uma aplicação desktop completa para gestão empresarial, ideal para pequenos e médios comércios. O sistema nasceu de um projeto piloto universitário, onde tivemos a oportunidade de trabalhar com um cliente real e desenvolver uma solução sob medida para suas dores e necessidades operacionais.

Com uma interface gráfica moderna e intuitiva construída em Python e PyQt5, o GestorX centraliza as operações mais importantes de um negócio em um único lugar.

## 🖼️ Demonstração Visual

| Dashboard | Controle de Estoque | Ponto de Venda (PDV) |
| :---: | :---: | :---: |
| ![Dashboard do GestorX](link-para-sua-imagem-do-dashboard-aqui) | ![Tela de Estoque](link-para-sua-imagem-do-estoque-aqui) | ![Tela do PDV](link-para-sua-imagem-do-pdv-aqui) |

## ✨ Funcionalidades

### 📊 Painel de Controle (Dashboard)
- Visão geral com gráficos e indicadores de performance.
- Resumo de vendas diárias, fluxo de caixa e produtos mais vendidos.
- Alertas de estoque baixo e outras notificações importantes.

### 📦 Ponto de Venda (PDV) e Estoque
- **PDV:** Interface rápida e otimizada para registro de vendas.
- **Controle de Estoque:** Cadastro de produtos, controle de entradas e saídas e ajuste de inventário.
- **Movimentações:** Histórico detalhado de todas as operações de estoque.

### 👥 Gestão de Relacionamentos
- Cadastro completo de clientes e fornecedores.
- Histórico de compras por cliente.
- **Sistema de Promoções:** Crie promoções com regras e prazo de validade.

### 💰 Financeiro e Relatórios
- **Relatórios de Caixa:** Acompanhe o fluxo de caixa, lucros e despesas.
- Geração de relatórios em PDF e Excel para análise aprofundada.
- Análise de performance de vendas por período.

### 🔐 Administração e Segurança
- **Controle de Usuários:** Sistema de login com perfis (Administrador e Operador).
- **Notificações por E-mail:** Envio automático de resumos diários ou alertas críticos.
- Backup automático e manual do banco de dados para garantir a segurança dos dados.

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
  Desenvolvido por Gustavo Moreno  
  <br><br>
  <a href="https://www.linkedin.com/in/gustavomoreno05" target="_blank">
    <img src="https://cdn-icons-png.flaticon.com/512/174/174/174857.png" width="24" alt="LinkedIn"/>
  </a>
</div>
