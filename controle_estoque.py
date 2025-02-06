import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
import pandas as pd


#======================
# VARIAVEIS GLOBAIS
# =====================
# Variáveis globais
NOME_BD = None
estoque_tree = None
root = None
restante_ui_carregado = False 
LISTA_ESTOQUES = ["ILP5", "IL01", "IL22", "IL23"]
# =====================================================================
# INTERFACE GRÁFICA PRINCIPAL
# =====================================================================
def main():
    global root
    root = tk.Tk()
    root.title("Sistema de Controle de Estoque")
    root.geometry("1000x700")
    #janela de configuração do estoque:
    criar_interface_configuracao_db()
    root.mainloop()

def carregar_ui():
    global restante_ui_carregado, root, estoque_tree, config_frame
    if restante_ui_carregado:
        return  # Evita recarregar a UI se já foi feita
    restante_ui_carregado = True
    
    # Barra de menu
    menu = tk.Menu(root)
    root.config(menu=menu)
    menu_relatorios = tk.Menu(menu, tearoff=0)
    menu_relatorios.add_command(label="Exportar para Excel", command=exportar_excel)
    menu_relatorios.add_command(label="Exibir Estatísticas", command=exibir_estatisticas)
    menu.add_cascade(label="Relatórios", menu=menu_relatorios)

    # Frame para os controles no lado esquerdo
    frame_controles = tk.Frame(root)
    frame_controles.pack(side="left", fill="y", padx=10, pady=10)

    botao_cadastrar = ttk.Button(frame_controles, text="Cadastrar Itens",
                                command=lambda: abrir_janela("cadastro_itens", "Cadastro produtos", "600x400", janela_cadastro_itens))
    botao_cadastrar.pack(fill="x", pady=5)
    botao_entrada = ttk.Button(frame_controles, text="Entrada de Produtos",
                            command=lambda: abrir_janela("entrada_produtos", "Entrada produtos", "600x400", janela_entrada_produtos))
    botao_entrada.pack(fill="x", pady=5)
    botao_saida = ttk.Button(frame_controles, text="Saída de Produtos",
                            command=lambda: abrir_janela("saida_produtos", "Saída produtos", "600x400", janela_saida_produtos))
    botao_saida.pack(fill="x", pady=5)
    botao_consulta = ttk.Button(frame_controles, text="Consulta de Saldo",
                                command=lambda: abrir_janela("consulta_saldo", "Consultar saldo", "800x500", consulta_saldo))
    botao_consulta.pack(fill="x", pady=5)
    botao_editar = ttk.Button(frame_controles, text="Editar Posição/Estoque",
                            command=lambda: abrir_janela("editar_estoque", "Editar estoque", "600x400", janela_editar_estoque))
    botao_editar.pack(fill="x", pady=5)
    botao_entradas = ttk.Button(frame_controles, text="Histórico de Entradas",
                                command=lambda: abrir_janela("historico_entrada", "Histório entradas de produtos", "1250x600", historico_entradas))
    botao_entradas.pack(fill="x", pady=5)
    botao_saidas = ttk.Button(frame_controles, text="Histórico de Saídas",
                            command=lambda: abrir_janela("historico_saida", "Histório saídas de produtos", "1250x600", historico_saidas))
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
    global estoque_tree
    estoque_tree = ttk.Treeview(frame_grid, columns=colunas, show="headings")
    for coluna in colunas:
        estoque_tree.heading(coluna, text=coluna.capitalize())
        estoque_tree.column(coluna, width=100, anchor="center")
    estoque_tree.pack(fill="both", expand=True)

        
    atualizar_grid()

    

# =====================================================================
# NOVA INTERFACE DE CONFIGURAÇÃO DO BANCO NA JANELA PRINCIPAL
# =====================================================================
def criar_interface_configuracao_db():
    global NOME_BD, db_config_label, config_frame
    config_frame = tk.Frame(root, bd=2, relief="groove")
    config_frame.pack(fill="x", padx=10, pady=5)

    tk.Label(config_frame, text="Informe o nome do estoque:").pack(side="left", padx=5)
    estoque_entry = ttk.Entry(config_frame)
    estoque_entry.pack(side="left", padx=5)

    def configurar():
        estoque = estoque_entry.get().strip().upper()
        if not estoque:
            messagebox.showwarning("Aviso", "Por favor, informe o estoque!")
        else:
            global NOME_BD
            # Define o caminho do banco com base no estoque informado
            if LISTA_ESTOQUES.__contains__(estoque):
                
                # ====================================================================
                # Altere para o diretorio onde ficará seu db :)
                NOME_BD = f"A:\\08 - Projeto ERP em pyhton\\db_Estoques\\{estoque}.db"
                db_config_label.config(text=f"Depósito: {estoque.upper()}")
                inicializar_bd()
                # Após configuração, carrega o restante da UI
                carregar_ui()
            else:
                messagebox.showwarning("Aviso","Estoque não encontrado.")
                estoque_entry.focus()

    ttk.Button(config_frame, text="Trocar/Conectar", command=configurar).pack(side="left", padx=5)
    db_config_label = tk.Label(config_frame, text="Depósito: Não configurado", fg="blue")
    db_config_label.pack(side="left", padx=10)




# =====================================================================
# EXPORTAR DADOS PARA EXCEL
# =====================================================================
def exportar_excel():
    conn = conectar_bd()
    if conn is None:
        return
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
    if conn is None:
        return
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
    if conn is None:
        return
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

# =====================================================================
# EXIBIR ESTATÍSTICAS
# =====================================================================
def exibir_estatisticas():
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT codigo, SUM(quantidade) as total_quantidade FROM ControleEstoque GROUP BY codigo ORDER BY total_quantidade DESC")
    data = cursor.fetchall()
    conn.close()

    if data:
        codigos, quantidades = zip(*data)
        fig, ax = plt.subplots()
        ax.bar(codigos, quantidades, color='skyblue')
        ax.set_xlabel('Código')
        ax.set_ylabel('Quantidade')
        ax.set_title('Estoque Atual por Item ILP5')
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showwarning("Aviso", "Não há dados no estoque para gerar o gráfico.")

# =====================================================================
# VALIDAÇÃO DE ENTRADA PARA NÚMEROS
# =====================================================================
def validar_numero(texto):
    return texto.isdigit() or texto == ""

# =====================================================================
# GERENCIAMENTO DE JANELAS (ÚNICA INSTÂNCIA POR TIPO)
# =====================================================================
janelas_abertas = {}
def abrir_janela(nome, titulo, tamanho, criador_func):
    global janelas_abertas
    if nome in janelas_abertas and janelas_abertas[nome].winfo_exists():
        janelas_abertas[nome].lift()
        return janelas_abertas[nome]
    janela = tk.Toplevel(root)
    janela.title(titulo)
    janela.geometry(tamanho)
    janelas_abertas[nome] = janela
    janela.protocol("WM_DELETE_WINDOW", lambda: fechar_janela(nome))
    criador_func(janela)
    return janela

def fechar_janela(nome):
    global janelas_abertas
    if nome in janelas_abertas:
        janelas_abertas[nome].destroy()
        del janelas_abertas[nome]

# =====================================================================
# FUNÇÕES PARA OS BOTÕES PRINCIPAIS (CADASTRO, ENTRADA, SAÍDA, ETC.)
# =====================================================================
def janela_cadastro_itens(janela):
    frame_tabela = tk.Frame(janela)
    frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)
    tabela = ttk.Treeview(frame_tabela, columns=("codigo", "descricao"), show="headings")
    tabela.heading("codigo", text="Código")
    tabela.heading("descricao", text="Descrição")
    tabela.pack(fill="both", expand=True)
    scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
    tabela.configure(yscroll=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    def editar_celula(event):
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
        try:
            dados_clipboard = root.clipboard_get()
            linhas = dados_clipboard.split('\n')
            for linha in linhas:
                if linha.strip():
                    tabela.insert("", "end", values=linha.split('\t'))
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao colar dados: {e}")

    def salvar_tabela():
        conn = conectar_bd()
        if conn is None:
            return
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

    frame_botoes = tk.Frame(janela)
    frame_botoes.pack(pady=10)
    ttk.Button(frame_botoes, text="Colar Dados (Ctrl+V)", command=colar_dados).pack(side="left", padx=5)
    ttk.Button(frame_botoes, text="Salvar Itens", command=salvar_tabela).pack(side="right", padx=5)
    root.bind_all('<Control-v>', lambda e: tabela.event_generate('<Double-1>'))

def janela_entrada_produtos(janela):
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
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Entradas (codigo, quantidade, data, posicao) VALUES (?, ?, ?, ?)",
                           (codigo, int(quantidade), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), posicao))
            cursor.execute(
                "INSERT INTO ControleEstoque (codigo, descricao, quantidade, posicao) VALUES (?, (SELECT descricao FROM BancoDeDados WHERE codigo=?), ?, ?) "
                "ON CONFLICT(codigo, posicao) DO UPDATE SET quantidade=quantidade + ?",
                (codigo, codigo, int(quantidade), posicao, int(quantidade))
            )
            conn.commit()
            messagebox.showinfo("Sucesso", "Entrada registrada com sucesso!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Código não encontrado!")
        finally:
            conn.close()
            atualizar_grid()
    def entrada_massa():
        janela_massa = tk.Toplevel(root)
        janela_massa.title("Entrada em massa")
        janela_massa.geometry("600x400")
        frame_tabela = tk.Frame(janela_massa)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=10)
        tabela = ttk.Treeview(frame_tabela, columns=("codigo", "quantidade", "posicao"), show="headings")
        tabela.heading("codigo", text="Código")
        tabela.heading("quantidade", text="Quantidade")
        tabela.heading("posicao", text="Posição")
        tabela.pack(fill="both", expand=True)
        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=tabela.yview)
        tabela.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        def editar_celula(event):
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
            try:
                dados_clipboard = root.clipboard_get()
                linhas = dados_clipboard.split('\n')
                for linha in linhas:
                    if linha.strip():
                        tabela.insert("", "end", values=linha.split('\t'))
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao colar dados: {e}")

        def salvar_tabela():
            conn = conectar_bd()
            if conn is None:
                return
            cursor = conn.cursor()
            for item in tabela.get_children():
                codigo, quantidade, posicao = tabela.item(item, "values")
                if not codigo or not quantidade or not posicao:
                    continue
                try:
                    cursor.execute("INSERT INTO Entradas (codigo, quantidade, data, posicao) VALUES (?, ?, ?, ?)",
                                   (codigo, int(quantidade), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), posicao))
                    cursor.execute(
                        "INSERT INTO ControleEstoque (codigo, descricao, quantidade, posicao) VALUES (?, (SELECT descricao FROM BancoDeDados WHERE codigo=?), ?, ?) "
                        "ON CONFLICT(codigo, posicao) DO UPDATE SET quantidade=quantidade + ?",
                        (codigo, codigo, int(quantidade), posicao, int(quantidade))
                    )
                    conn.commit()
                except sqlite3.IntegrityError:
                    messagebox.showerror("Erro", f"Código '{codigo}' já está cadastrado!")
            conn.commit()
            conn.close()
            messagebox.showinfo("Sucesso", "Itens cadastrados com sucesso!")
            atualizar_grid()
            janela_massa.destroy()
        frame_botoes = tk.Frame(janela_massa)
        frame_botoes.pack(pady=10)
        ttk.Button(frame_botoes, text="Colar Dados (Ctrl+V)", command=colar_dados).pack(side="left", padx=5)
        ttk.Button(frame_botoes, text="Salvar Itens", command=salvar_tabela).pack(side="right", padx=5)
    ttk.Button(janela, text="Registrar", command=registrar_entrada).pack(pady=20)
    ttk.Button(janela, text="Cadastro em massa", command=entrada_massa).pack(pady=20)

def janela_saida_produtos(janela):
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
        if conn is None:
            return
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
            atualizar_grid()
            janela.destroy()
    ttk.Button(janela, text="Registrar", command=registrar_saida).pack(pady=20)

def consulta_saldo(janela):
    tk.Label(janela, text="Digite os Códigos dos Produtos (separados por vírgula):").pack(pady=5)
    codigo_entry = tk.Entry(janela)
    codigo_entry.pack(pady=5)
    tree = ttk.Treeview(janela, columns=("codigo", "descricao", "quantidade"), show="headings")
    tree.heading("codigo", text="Código")
    tree.heading("descricao", text="Descrição")
    tree.heading("quantidade", text="Quantidade")
    for col in tree["columns"]:
        tree.column(col, anchor="center")
    tree.pack(fill="both", expand=True)

    def buscar_saldo():
        for item in tree.get_children():
            tree.delete(item)
        codigos = codigo_entry.get().strip()
        if not codigos:
            print("Por favor, insira ao menos um código válido.")
            return
        lista_codigos = [codigo.strip() for codigo in codigos.split(",")]
        conn = conectar_bd()
        if conn is None:
            return
        cursor = conn.cursor()
        placeholders = ", ".join(["?"] * len(lista_codigos))
        query = f"""
            SELECT codigo, descricao, SUM(quantidade) as total_quantidade 
            FROM ControleEstoque 
            WHERE codigo IN ({placeholders}) 
            GROUP BY codigo, descricao
        """
        cursor.execute(query, lista_codigos)
        resultados = cursor.fetchall()
        conn.close()
        if resultados:
            for resultado in resultados:
                tree.insert("", "end", values=resultado)
        else:
            tk.Label(janela, text="Nenhum produto encontrado.").pack(pady=10)
    tk.Button(janela, text="Buscar Saldo", command=buscar_saldo).pack(pady=10)

def janela_editar_estoque(janela):
    def buscar_produto():
        codigo = codigo_entry.get().strip()
        posicao = posicao_entry.get().strip()
        if not codigo or not posicao:
            messagebox.showwarning("Erro", "Preencha o código e a posição do produto!")
            return
        conn = conectar_bd()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute("SELECT descricao, quantidade FROM ControleEstoque WHERE codigo = ? AND posicao = ?", (codigo, posicao))
        resultado = cursor.fetchone()
        conn.close()
        if resultado:
            descricao_label.config(text=f"Descrição: {resultado[0]}")
            quantidade_label.config(text=f"Quantidade Atual: {resultado[1]}")
        else:
            messagebox.showerror("Erro", "Produto não encontrado para o código e posição informados!")

    def abrir_janela_atualizar():
        codigo = codigo_entry.get().strip()
        posicao = posicao_entry.get().strip()
        if not codigo or not posicao:
            messagebox.showwarning("Erro", "Preencha o código e a posição para atualizar!")
            return
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
        def atualizar_estoque():
            novo_codigo = novo_codigo_entry.get().strip()
            nova_quantidade = nova_quantidade_entry.get().strip()
            nova_posicao = nova_posicao_entry.get().strip()
            if not novo_codigo or not nova_quantidade or not nova_posicao:
                messagebox.showwarning("Erro", "Preencha todos os campos!")
                return
            conn = conectar_bd()
            if conn is None:
                return
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM ControleEstoque WHERE codigo = ? AND posicao = ?", (codigo, posicao))
                cursor.execute(
                    "INSERT INTO ControleEstoque (codigo, descricao, quantidade, posicao) VALUES (?, (SELECT descricao FROM BancoDeDados WHERE codigo = ?), ?, ?)",
                    (novo_codigo, novo_codigo, int(nova_quantidade), nova_posicao)
                )
                conn.commit()
                messagebox.showinfo("Sucesso", "Estoque atualizado com sucesso!")
                atualizar_grid()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao atualizar estoque: {e}")
            finally:
                conn.close()
                janela_atualizar.destroy()
        ttk.Button(janela_atualizar, text="Atualizar Estoque", command=atualizar_estoque).pack(pady=10)

    def excluir_item():
        codigo = codigo_entry.get().strip()
        posicao = posicao_entry.get().strip()
        if not codigo or not posicao:
            messagebox.showwarning("Erro", "Preencha o código e a posição para excluir!")
            return
        conn = conectar_bd()
        if conn is None:
            return
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM ControleEstoque WHERE codigo = ? AND posicao = ?", (codigo, posicao))
            if cursor.rowcount > 0:
                conn.commit()
                messagebox.showinfo("Sucesso", "Entrada excluída com sucesso!")
                atualizar_grid()
            else:
                messagebox.showerror("Erro", "Entrada não encontrada para o código e posição informados!")
        finally:
            conn.close()

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

def historico_entradas(janela):
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Entradas")
    resultados = cursor.fetchall()
    conn.close()
    tree = ttk.Treeview(janela, columns=("id", "codigo", "quantidade", "data", "posicao"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("quantidade", text="Quantidade")
    tree.heading("data", text="Data")
    tree.heading("posicao", text="Posição")
    for col in tree["columns"]:
        tree.column(col, anchor="center")
    for resultado in resultados:
        tree.insert("", "end", values=resultado)
    tree.pack(fill="both", expand=True)
    ttk.Button(janela, text="Exportar", command=exportar_Entradas).pack(pady=20)

def historico_saidas(janela):
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Saidas")
    resultados = cursor.fetchall()
    conn.close()
    tree = ttk.Treeview(janela, columns=("id", "codigo", "quantidade", "data", "posicao", "solicitante"), show="headings")
    tree.heading("id", text="ID")
    tree.heading("codigo", text="Código")
    tree.heading("quantidade", text="Quantidade")
    tree.heading("data", text="Data")
    tree.heading("posicao", text="Posição")
    tree.heading("solicitante", text="Solicitante")
    for col in tree["columns"]:
        tree.column(col, anchor="center")
    for resultado in resultados:
        tree.insert("", "end", values=resultado)
    tree.pack(fill="both", expand=True)
    ttk.Button(janela, text="Exportar", command=exportar_Saidas).pack(pady=20)

def conectar():
    conn = conectar_bd()
    if conn is None:
        return
    messagebox.showinfo("Sucesso", "Conectado ao banco de dados.")
    conn.close()

# =====================================================================
# FUNÇÃO PARA CONECTAR AO BANCO DE DADOS (COM VERIFICAÇÃO)
# =====================================================================
def conectar_bd():
    if NOME_BD is None:
        messagebox.showerror("Erro", "Banco de dados não configurado. Por favor, configure antes de continuar.")
        return None
    try:
        return sqlite3.connect(NOME_BD)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao conectar ao banco de dados: {e}")
        return None

# =====================================================================
# INICIALIZAR O BANCO DE DADOS
# =====================================================================
def inicializar_bd():
    conn = conectar_bd()
    if conn is None:
        return
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
    messagebox.showinfo("Sucesso", "Banco de dados inicializado com sucesso!")

# =====================================================================
# ATUALIZAR A GRID PRINCIPAL
# =====================================================================
def atualizar_grid(filtro=""):
    conn = conectar_bd()
    if conn is None:
        return
    cursor = conn.cursor()

    estoque_tree.delete(*estoque_tree.get_children())

    query = "SELECT codigo, descricao, quantidade, posicao FROM ControleEstoque"
    if filtro:
        query += f" WHERE codigo LIKE '%{filtro}%' OR descricao LIKE '%{filtro}%' OR posicao LIKE '%{filtro}%'"
    cursor.execute(query)
    for row in cursor.fetchall():
        estoque_tree.insert("", "end", values=row)
    conn.close()

if __name__=='__main__':
    main()