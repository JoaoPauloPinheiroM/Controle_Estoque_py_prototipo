import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import pandas as pd

NOME_BD = "estoque.db"

# Conectar ao banco de dados
def conectar_bd():
    return sqlite3.connect(NOME_BD)

# Inicializar o banco de dados
def inicializar_bd():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS BancoDeDados (
        codigo TEXT PRIMARY KEY,
        descricao TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Entradas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        quantidade INTEGER,
        data TEXT,
        posicao TEXT,
        FOREIGN KEY (codigo) REFERENCES BancoDeDados (codigo)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Saidas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        quantidade INTEGER,
        data TEXT,
        posicao TEXT,
        solicitante TEXT,
        FOREIGN KEY (codigo) REFERENCES BancoDeDados (codigo)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ControleEstoque (
        codigo TEXT,
        descricao TEXT,
        quantidade INTEGER,
        posicao TEXT,
        PRIMARY KEY (codigo, posicao),
        FOREIGN KEY (codigo) REFERENCES BancoDeDados (codigo)
    )
    ''')

    conn.commit()
    conn.close()





# Atualizar a grid principal
def atualizar_grid(filtro=""):
    conn = conectar_bd()
    cursor = conn.cursor()

    estoque_tree.delete(*estoque_tree.get_children())

    query = "SELECT codigo, descricao, quantidade, posicao FROM ControleEstoque"
    if filtro:
        query += f" WHERE codigo LIKE '%{filtro}%' OR descricao LIKE '%{filtro}%' OR posicao LIKE '%{filtro}%'"

    cursor.execute(query)
    for row in cursor.fetchall():
        estoque_tree.insert("", "end", values=row)

    conn.close()




# Exportar dados para Excel
def exportar_excel():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM ControleEstoque")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(data, columns=columns)
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Arquivos Excel", "*.xlsx")])
    if caminho_arquivo:
        df.to_excel(caminho_arquivo, index=False)
        messagebox.showinfo("Sucesso", "Relatório exportado com sucesso!")

    conn.close()

def exportar_Saidas():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Saidas")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(data, columns=columns)
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Arquivos Excel", "*.xlsx")])
    if caminho_arquivo:
        df.to_excel(caminho_arquivo, index=False)
        messagebox.showinfo("Sucesso", "Relatório exportado com sucesso!")

    conn.close()

def exportar_Entradas():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Entradas")
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    df = pd.DataFrame(data, columns=columns)
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx",
                                                   filetypes=[("Arquivos Excel", "*.xlsx")])
    if caminho_arquivo:
        df.to_excel(caminho_arquivo, index=False)
        messagebox.showinfo("Sucesso", "Relatório exportado com sucesso!")

    conn.close()



# Exibir estatísticas
def exibir_estatisticas():
    conn = conectar_bd()
    cursor = conn.cursor()

    cursor.execute("SELECT codigo, quantidade FROM ControleEstoque")
    data = cursor.fetchall()

    if data:
        descricoes, quantidades = zip(*data)
        plt.bar(descricoes, quantidades)
        plt.title("Estoque Atual por Item")
        plt.xlabel("codigo")
        plt.ylabel("Quantidade")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showwarning("Aviso", "Não há dados no estoque para gerar o gráfico.")

    conn.close()

# Validação de entrada para números
def validar_numero(texto):
    return texto.isdigit() or texto == ""




# Funções para os botões principais
def janela_cadastro_itens():
    janela = tk.Toplevel(root)
    janela.title("Cadastrar Itens")
    janela.geometry("600x400")

    # Configuração da tabela editável
    frame_tabela = tk.Frame(janela)
    frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)

    tabela = ttk.Treeview(frame_tabela, columns=("codigo", "descricao"), show="headings")
    tabela.heading("codigo", text="Código")
    tabela.heading("descricao", text="Descrição")
    tabela.pack(fill="both", expand=True)

    # Adicionar um scrollbar
    scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def editar_celula(event):
        # Editar célula ao clicar
        item = tabela.identify('item', event.x, event.y)
        column = tabela.identify_column(event.x)
        if item and column:
            col_index = int(column.replace('#', '')) - 1
            old_value = tabela.item(item, 'values')[col_index]

            def salvar_edicao(event):
                tabela.set(item, column=col_index, value=entry.get())
                entry.destroy()

            entry = ttk.Entry(frame_tabela)
            entry.insert(0, old_value)
            entry.bind('<Return>', salvar_edicao)
            entry.place(x=event.x, y=event.y)

    tabela.bind('<Double-1>', editar_celula)

    def colar_dados():
        # Pegar dados do clipboard e colar na grid
        try:
            dados_clipboard = root.clipboard_get()
            linhas = dados_clipboard.split('\n')
            for linha in linhas:
                if linha.strip():
                    tabela.insert("", "end", values=linha.split('\t'))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao colar dados: {e}")

    def salvar_tabela():
        # Salvar os dados para o banco
        conn = conectar_bd()
        cursor = conn.cursor()

        for item in tabela.get_children():
            codigo, descricao = tabela.item(item, "values")
            if not codigo or not descricao:
                continue
            try:
                cursor.execute("INSERT INTO BancoDeDados (codigo, descricao) VALUES (?, ?)", (codigo, descricao))
            except sqlite3.IntegrityError:
                messagebox.showerror("Erro", f"Código '{codigo}' já está cadastrado!")

        conn.commit()
        conn.close()
        messagebox.showinfo("Sucesso", "Itens cadastrados com sucesso!")
        atualizar_grid()
        janela.destroy()

    # Botões
    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=10)

    ttk.Button(frame_botoes, text="Colar Dados (Ctrl+V)", command=colar_dados).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Salvar Itens", command=salvar_tabela).pack(side="right", padx=5)

    # Adicionar suporte para colar com Ctrl+V
    root.bind_all('<Control-v>', lambda e: tabela.event_generate('<Double-1>'))
    
    
    
    
def janela_entrada_produtos():
    janela = tk.Toplevel(root)
    janela.title("Entrada de Produtos")
    janela.geometry("400x300")

    tk.Label(janela, text="Código:").pack(pady=5)
    codigo_entry = ttk.Entry(janela)
    codigo_entry.pack()

    tk.Label(janela, text="Quantidade:").pack(pady=5)
    quantidade_entry = ttk.Entry(janela, validate="key", validatecommand=(janela.register(validar_numero), "%P"))
    quantidade_entry.pack()

    tk.Label(janela, text="Posição:").pack(pady=5)
    posicao_entry = ttk.Entry(janela)
    posicao_entry.pack()

    def registrar_entrada():
        codigo = codigo_entry.get().strip()
        quantidade = quantidade_entry.get().strip()
        posicao = posicao_entry.get().strip()

        if not codigo or not quantidade or not posicao:
            messagebox.showwarning("Erro", "Preencha todos os campos!")
            return

        conn = conectar_bd()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Entradas (codigo, quantidade, data, posicao) VALUES (?, ?, ?, ?)",
                           (codigo, int(quantidade), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), posicao))
            cursor.execute("INSERT INTO ControleEstoque (codigo, descricao, quantidade, posicao) VALUES (?, (SELECT descricao FROM BancoDeDados WHERE codigo=?), ?, ?) "
                           "ON CONFLICT(codigo, posicao) DO UPDATE SET quantidade=quantidade + ?",
                           (codigo, codigo, int(quantidade), posicao, int(quantidade)))
            conn.commit()
            messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código não encontrado!")
        finally:
            conn.close()
            atualizar_grid()

    ttk.Button(janela, text="Registrar", command=registrar_entrada).pack(pady=20)





def janela_saida_produtos():
    janela = tk.Toplevel(root)
    janela.title("Saída de Produtos")
    janela.geometry("400x400")

    tk.Label(janela, text="Código:").pack(pady=5)
    codigo_entry = ttk.Entry(janela)
    codigo_entry.pack()

    tk.Label(janela, text="Quantidade:").pack(pady=5)
    quantidade_entry = ttk.Entry(janela, validate="key", validatecommand=(janela.register(validar_numero), "%P"))
    quantidade_entry.pack()

    tk.Label(janela, text="Posição:").pack(pady=5)
    posicao_entry = ttk.Entry(janela)
    posicao_entry.pack()

    tk.Label(janela, text="Solicitante:").pack(pady=5)
    solicitante_entry = ttk.Entry(janela)
    solicitante_entry.pack()
    





    def registrar_saida():
        codigo = codigo_entry.get().strip()
        quantidade = quantidade_entry.get().strip()
        posicao = posicao_entry.get().strip()
        solicitante = solicitante_entry.get().strip()

        if not codigo or not quantidade or not posicao or not solicitante:
            messagebox.showwarning("Erro", "Preencha todos os campos!")
            return

        conn = conectar_bd()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Saidas (codigo, quantidade, data, posicao, solicitante) VALUES (?, ?, ?, ?, ?)",
                           (codigo, int(quantidade), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), posicao, solicitante))
            cursor.execute("UPDATE ControleEstoque SET quantidade = quantidade - ? WHERE codigo = ? AND posicao = ? AND quantidade >= ?",
                           (int(quantidade), codigo, posicao, int(quantidade)))
            if cursor.rowcount == 0:
                raise ValueError("Estoque insuficiente ou código/posição inválidos.")
            conn.commit()
            messagebox.showinfo("Sucesso", "Saída registrada com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))
        finally:
            conn.close()
            janela.destroy()
            atualizar_grid()

    ttk.Button(janela, text="Registrar", command=registrar_saida).pack(pady=20)







def consulta_saldo():
    # Criar a janela principal
    janela = tk.Toplevel(root)
    janela.title("Consulta de Saldo")
    janela.geometry("800x350")

    # Rótulo e campo de entrada para os códigos do produto
    tk.Label(janela, text="Digite os Códigos dos Produtos (separados por vírgula):").pack(pady=5)
    codigo_entry = tk.Entry(janela)
    codigo_entry.pack(pady=5)

    # Criação da árvore para exibir os resultados (apenas uma vez)
    tree = ttk.Treeview(janela, columns=("codigo", "descricao", "quantidade"), show="headings")
    tree.heading("codigo", text="Código")
    tree.heading("descricao", text="Descrição")
    tree.heading("quantidade", text="Quantidade")
    
    # Alinhamento centralizado para todas as colunas
    for col in tree["columns"]:
        tree.column(col, anchor="center")

    # Exibindo a Treeview
    tree.pack(fill="both", expand=True)

    def buscar_saldo():
        # Limpar os resultados anteriores da Treeview
        for item in tree.get_children():
            tree.delete(item)
        
        # Obter os códigos inseridos pelo usuário
        codigos = codigo_entry.get().strip()
        
        # Verifica se há códigos inseridos
        if not codigos:
            print("Por favor, insira ao menos um código válido.")
            return
        
        # Separar os códigos por vírgulas e remover espaços
        lista_codigos = [codigo.strip() for codigo in codigos.split(",")]

        # Conecta ao banco de dados
        conn = conectar_bd()
        cursor = conn.cursor()

        # Montar consulta SQL dinâmica com base na quantidade de códigos
        placeholders = ", ".join(["?"] * len(lista_codigos))
        query = f"""
            SELECT codigo, descricao, SUM(quantidade) as total_quantidade 
            FROM ControleEstoque 
            WHERE codigo IN ({placeholders}) 
            GROUP BY codigo, descricao
        """
        cursor.execute(query, lista_codigos)
        resultados = cursor.fetchall()  # Obter todos os resultados
        
        conn.close()

        # Exibir os resultados na Treeview
        if resultados:
            for resultado in resultados:
                tree.insert("", "end", values=resultado)
        else:
            tk.Label(janela, text="Nenhum produto encontrado.").pack(pady=10)

    # Botão para buscar o saldo
    tk.Button(janela, text="Buscar Saldo", command=buscar_saldo).pack(pady=10)






# Função para atualizar o estoque
def janela_editar_estoque():
    # Janela principal para buscar produto
    janela = tk.Toplevel(root)
    janela.title("Editar Estoque")
    janela.geometry("400x400")

    # Função para buscar produto
    def buscar_produto():
        codigo = codigo_entry.get().strip()
        posicao = posicao_entry.get().strip()

        if not codigo or not posicao:
            messagebox.showwarning("Erro", "Preencha o código e a posição do produto!")
            return

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT descricao, quantidade 
            FROM ControleEstoque 
            WHERE codigo = ? AND posicao = ?
        """, (codigo, posicao))
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            descricao_label.config(text=f"Descrição: {resultado[0]}")
            quantidade_label.config(text=f"Quantidade Atual: {resultado[1]}")
        else:
            messagebox.showerror("Erro", "Produto não encontrado para o código e posição informados!")

    # Função para abrir a janela de atualização
    def abrir_janela_atualizar():
        codigo = codigo_entry.get().strip()
        posicao = posicao_entry.get().strip()

        if not codigo or not posicao:
            messagebox.showwarning("Erro", "Preencha o código e a posição para atualizar!")
            return

        # Janela de atualização
        janela_atualizar = tk.Toplevel(janela)
        janela_atualizar.title("Atualizar Dados")
        janela_atualizar.geometry("400x300")

        ttk.Label(janela_atualizar, text="Novo Código:").pack(pady=5)
        novo_codigo_entry = ttk.Entry(janela_atualizar)
        novo_codigo_entry.pack()

        ttk.Label(janela_atualizar, text="Nova Quantidade:").pack(pady=5)
        nova_quantidade_entry = ttk.Entry(janela_atualizar)
        nova_quantidade_entry.pack()

        ttk.Label(janela_atualizar, text="Nova Posição:").pack(pady=5)
        nova_posicao_entry = ttk.Entry(janela_atualizar)
        nova_posicao_entry.pack()

        # Função para atualizar estoque
        def atualizar_estoque():
            novo_codigo = novo_codigo_entry.get().strip()
            nova_quantidade = nova_quantidade_entry.get().strip()
            nova_posicao = nova_posicao_entry.get().strip()

            if not novo_codigo or not nova_quantidade or not nova_posicao:
                messagebox.showwarning("Erro", "Preencha todos os campos!")
                return

            conn = conectar_bd()
            cursor = conn.cursor()
            try:
                # Apagar a entrada antiga
                cursor.execute("""
                    DELETE FROM ControleEstoque 
                    WHERE codigo = ? AND posicao = ?
                """, (codigo, posicao))

                # Criar a nova entrada
                cursor.execute("""
                    INSERT INTO ControleEstoque (codigo, descricao, quantidade, posicao) 
                    VALUES (?, (SELECT descricao FROM BancoDeDados WHERE codigo = ?), ?, ?)
                """, (novo_codigo, novo_codigo, int(nova_quantidade), nova_posicao))

                conn.commit()
                messagebox.showinfo("Sucesso", "Estoque atualizado com sucesso!")
                atualizar_grid()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar estoque: {e}")
            finally:
                conn.close()
                janela_atualizar.destroy()

        ttk.Button(janela_atualizar, text="Atualizar Estoque", command=atualizar_estoque).pack(pady=10)

    # Função para excluir entrada
    def excluir_item():
        codigo = codigo_entry.get().strip()
        posicao = posicao_entry.get().strip()

        if not codigo or not posicao:
            messagebox.showwarning("Erro", "Preencha o código e a posição para excluir!")
            return

        conn = conectar_bd()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM ControleEstoque 
                WHERE codigo = ? AND posicao = ?
            """, (codigo, posicao))

            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Sucesso", "Entrada excluída com sucesso!")
                atualizar_grid()
            else:
                messagebox.showerror("Erro", "Entrada não encontrada para o código e posição informados!")
        finally:
            conn.close()

    # Layout da janela principal
    ttk.Label(janela, text="Código:").pack(pady=5)
    codigo_entry = ttk.Entry(janela)
    codigo_entry.pack()

    ttk.Label(janela, text="Posição:").pack(pady=5)
    posicao_entry = ttk.Entry(janela)
    posicao_entry.pack()

    ttk.Button(janela, text="Buscar", command=buscar_produto).pack(pady=10)

    descricao_label = ttk.Label(janela, text="Descrição:")
    descricao_label.pack(pady=5)

    quantidade_label = ttk.Label(janela, text="Quantidade Atual:")
    quantidade_label.pack(pady=5)

    ttk.Button(janela, text="Atualizar", command=abrir_janela_atualizar).pack(pady=10)
    ttk.Button(janela, text="Excluir Entrada", command=excluir_item).pack(pady=10)
    
    
    
    
def historico_entradas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Entradas")
    resultados = cursor.fetchall()
    conn.close()

    janela = tk.Toplevel(root)
    janela.title("Histórico de Entradas")

    tree = ttk.Treeview(janela, columns=("id", "codigo", "quantidade", "data", "posicao"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("quantidade", text="Quantidade")
    tree.heading("data", text="Data")
    tree.heading("posicao", text="Posição")
    # Alinhamento centralizado para todas as colunas
    for col in tree["columns"]:
        tree.column(col, anchor="center")

    # Inserindo os resultados na Treeview
    for resultado in resultados:
        tree.insert("", "end", values=resultado)
    
    # Exibindo a Treeview
    tree.pack(fill="both", expand=True)
    ttk.Button(janela, text="Exportar", command=exportar_Entradas).pack(pady=20)




def historico_saidas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Saidas")
    resultados = cursor.fetchall()
    conn.close()

    janela = tk.Toplevel(root)
    janela.title("Histórico de Saídas")

    tree = ttk.Treeview(janela, columns=("id", "codigo", "quantidade", "data", "posicao", "solicitante"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("quantidade", text="Quantidade")
    tree.heading("data", text="Data")
    tree.heading("posicao", text="Posição")
    tree.heading("solicitante", text="Solicitante")
    # Alinhamento centralizado para todas as colunas
    for col in tree["columns"]:
        tree.column(col, anchor="center")

    # Inserindo os resultados na Treeview
    for resultado in resultados:
        tree.insert("", "end", values=resultado)
    
    # Exibindo a Treeview
    tree.pack(fill="both", expand=True)
    ttk.Button(janela, text="Exportar", command=exportar_Saidas).pack(pady=20)




# Inicializar o banco de dados
inicializar_bd()

# Interface gráfica principal
root = tk.Tk()
root.title("Sistema de Controle de Estoque")
root.geometry("1000x700")

# Barra de menu
menu = tk.Menu(root)
root.config(menu=menu)

menu_relatorios = tk.Menu(menu, tearoff=0)
menu_relatorios.add_command(label="Exportar para Excel", command=exportar_excel)
menu_relatorios.add_command(label="Exibir Estatísticas", command=exibir_estatisticas)
menu.add_cascade(label="Relatórios", menu=menu_relatorios)

# Frame para os controles
frame_controles = tk.Frame(root)
frame_controles.pack(side="left", fill="y", padx=10, pady=10)

# Botões principais
botao_cadastrar = ttk.Button(frame_controles, text="Cadastrar Itens", command=janela_cadastro_itens)
botao_cadastrar.pack(fill="x", pady=5)

botao_entrada = ttk.Button(frame_controles, text="Entrada de Produtos", command=janela_entrada_produtos)
botao_entrada.pack(fill="x", pady=5)

botao_saida = ttk.Button(frame_controles, text="Saída de Produtos", command=janela_saida_produtos)
botao_saida.pack(fill="x", pady=5)

botao_consulta = ttk.Button(frame_controles, text="Consulta de Saldo", command=consulta_saldo)
botao_consulta.pack(fill="x", pady=5)

botao_editar = ttk.Button(frame_controles, text="Editar Posição/Estoque", command=janela_editar_estoque)
botao_editar.pack(fill="x", pady=5)

botao_entradas = ttk.Button(frame_controles, text="Histórico de Entradas", command=historico_entradas)
botao_entradas.pack(fill="x", pady=5)

botao_saidas = ttk.Button(frame_controles, text="Histórico de Saídas", command=historico_saidas)
botao_saidas.pack(fill="x", pady=5)




# Campo de busca
frame_busca = tk.Frame(root)
frame_busca.pack(fill="x", padx=10, pady=10)
tk.Label(frame_busca, text="Buscar:").pack(side="left", padx=5)
busca_entry = ttk.Entry(frame_busca)
busca_entry.pack(side="left", fill="x", expand=True, padx=5)
ttk.Button(frame_busca, text="Buscar", command=lambda: atualizar_grid(busca_entry.get())).pack(side="left")



# Grid principal
frame_grid = tk.Frame(root)
frame_grid.pack(fill="both", expand=True, padx=10, pady=10)

colunas = ("codigo", "descricao", "quantidade", "posicao")
estoque_tree = ttk.Treeview(frame_grid, columns=colunas, show="headings")
for coluna in colunas:
    estoque_tree.heading(coluna, text=coluna.capitalize())
    estoque_tree.column(coluna, width=100, anchor="center")

estoque_tree.pack(fill="both", expand=True)



# Inicializar grid
atualizar_grid()

# Executar aplicação
root.mainloop()