# 📦 Sistema de Controle de Estoque (Protótipo Python)

Este repositório contém um **sistema de gerenciamento de estoque desenvolvido em Python** utilizando **Tkinter** para a interface gráfica, **SQLite** para persistência local e ferramentas como **Pandas** e **Matplotlib** para relatórios e visualização de dados.

O projeto foi criado como um **protótipo inicial** de um sistema maior desenvolvido em C#. Serviu como base conceitual e teste piloto em um ambiente real não controlado, ajudando na validação de processos e fluxo de informações antes da implementação final.

---

## 🚀 Funcionalidades Principais

- **Cadastro de Produtos**: Interface para adicionar novos itens ao estoque, incluindo código e descrição.
- **Entrada de Produtos**: Controle de entradas de materiais, com registro de código, quantidade e posição.
- **Saída de Produtos**: Gerenciamento da saída de itens, incluindo controle de solicitante e quantidade retirada.
- **Consulta de Saldo**: Ferramenta para consultar o saldo atual de produtos por código.
- **Histórico de Entradas/Saídas**: Exibição de registros de movimentação para auditoria.
- **Edição de Estoque**: Permite alterar posição, quantidade ou remover itens do estoque.
- **Exportação de Dados**: Exportação dos dados para arquivos Excel.
- **Visualização Gráfica**: Geração de gráficos estatísticos baseados no estoque atual.
- **Entrada e Cadastro em Massa**: Suporte para inserção rápida de dados via colagem do clipboard.
- **Configuração Multi-Depósito**: Permite alternar entre diferentes bases de dados conforme o depósito.

---

## 🧰 Tecnologias Utilizadas

- **Python 3.x**
- **Tkinter** (Interface Gráfica)
- **SQLite** (Persistência de Dados)
- **Pandas** (Manipulação e Exportação de Dados)
- **Matplotlib** (Geração de Gráficos)

---

## 📝 Como Executar

1. Instale as dependências necessárias:

    ```bash
    pip install pandas matplotlib
    ```

2. Execute o script:

    ```bash
    python controle_estoque.py
    ```

---

## 🔮 Propósito do Protótipo

Este protótipo teve como objetivos:

- Validar regras e fluxo de controle de estoque em um ambiente real.
- Servir como prova de conceito para o projeto final em C#.
- Permitir testes rápidos e ajustes antes da transição para a tecnologia principal.

---

## 📊 Futuras Melhorias (Possíveis)

- Implementação de autenticação de usuários.
- Integração com sistemas externos via API.
- Geração de relatórios em PDF.
- Desenvolvimento de uma interface responsiva com melhorias visuais.

---

## 📂 Projeto Principal

A versão completa deste projeto está sendo desenvolvida em C# com Windows Forms:

➡️ [Controle de Estoque em C#](https://github.com/JoaoPauloPinheiroM/ControleEstoque.Alpha)

---

## 📃 Licença

Este projeto é de uso pessoal e acadêmico. Sinta-se à vontade para estudar, testar e adaptar!

1. Clone o repositório:

    ```bash
    git clone https://github.com/JoaoPauloPinheiroM/Controle_Estoque_py_prototipo.git
    cd Controle_Estoque_py_prototipo
    ```
