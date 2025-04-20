# 🛒 Sistema de Controle de Estoque para Bomboniere

Este é um sistema completo de controle de estoque desenvolvido com **Python** e **PyQt5**, focado na gestão de produtos, clientes, fornecedores e promoções para pequenas empresas como bombonieres, lojas de conveniência, mercadinhos, entre outros.

---

## 📋 Funcionalidades Principais

- ✅ Cadastro de produtos com validação de **data de validade**
- ✅ Controle de **entradas e saídas** de estoque
- ✅ Cadastro de **clientes**, **fornecedores** e **promoções**
- ✅ Alocação de produtos por categoria
- ✅ Alertas de produtos vencidos ou com estoque mínimo
- ✅ Interface gráfica moderna e responsiva com **Qt Designer + QSS**
- ✅ Banco de dados local utilizando **SQLite**
- ✅ Backup automático e relatórios gerenciais

---

## ✨ Funcionalidades Extras

- Relatórios em PDF/Excel
- Login com controle de permissões (admin, operador)
- Painel com gráficos (produtos mais vendidos, estoques críticos)
- Notificações visuais/sonoras
- Sistema de promoções com tempo de validade
- Busca inteligente com filtros

---

## 🖼️ Interface

> O sistema possui uma interface amigável e personalizável, com visual moderno baseado em QSS (estilo CSS para PyQt5). Ideal para ambientes comerciais com pouco conhecimento técnico.

---

## ⚙️ Tecnologias Utilizadas

- Python 3.x
- PyQt5
- SQLite3
- Qt Designer (para construção de interfaces)
- QSS (Qt Style Sheets)
- PyInstaller (para empacotar o sistema em `.exe`)

---

## 📦 Estrutura do Projeto

```
bomboniere_estoque/
│
├── main.py               # Arquivo principal do sistema
├── manager.py            # Lógica de banco de dados
│
├── ui/                   # Arquivos .ui (gerados no Qt Designer)
├── views/                # Telas Python geradas a partir do UI
├── style/                # Arquivos de estilo QSS
├── icons/                # Imagens e ícones utilizados
└── data/                 # Banco de dados e arquivos auxiliares
```

---

## 🚀 Como Executar

1. Clone o repositório:
```bash
git clone https://github.com/seuusuario/bomboniere-estoque.git
```

2. Instale as dependências:
```bash
pip install pyqt5
```

3. Execute o sistema:
```bash
python main.py
```

> **Dica:** Use o PyInstaller para gerar um executável `.exe`:
```bash
pyinstaller --noconsole --onefile main.py
```

---

## 🛡️ Requisitos do Sistema

- Python 3.8 ou superior
- Sistema operacional Windows, Linux ou macOS
- Qt5 (instalado via `pip install pyqt5`)

---

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

---


