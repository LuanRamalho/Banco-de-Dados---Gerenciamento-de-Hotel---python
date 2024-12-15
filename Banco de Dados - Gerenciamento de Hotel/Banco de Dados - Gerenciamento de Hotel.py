import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime
import os

DATABASE_FILE = "reservas.json"

# Funções de leitura e escrita do banco de dados (já definidas anteriormente)
def ler_dados():
    if os.path.exists(DATABASE_FILE):
        with open(DATABASE_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def salvar_dados(dados):
    with open(DATABASE_FILE, "w") as f:
        json.dump(dados, f, indent=4)

def calcular_faturamento(dados):
    return sum(reserva.get("preco_total", 0) for reserva in dados)

def validar_data(data_str):
    try:
        datetime.datetime.strptime(data_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False

def salvar_reserva():
    nome = entry_nome.get()
    try:
        diaria = float(entry_diaria.get())
        dias = int(entry_dias.get())
    except ValueError:
        messagebox.showerror("Erro", "Preço da diária e dias devem ser números.")  # Mensagem de erro
        return

    chegada = entry_chegada.get()
    saida = entry_saida.get()

    if not validar_data(chegada) or not validar_data(saida):
        messagebox.showerror("Erro", "Data inválida. Use o formato DD-MM-YYYY")  # Mensagem de erro
        return

    dados = ler_dados()
    id = len(dados) + 1
    preco_total = diaria * dias

    reserva = {
        "id": id,
        "nome": nome,
        "diaria": diaria,
        "dias": dias,
        "preco_total": preco_total,
        "chegada": chegada,
        "saida": saida,
    }
    dados.append(reserva)
    salvar_dados(dados)
    atualizar_faturamento()
    messagebox.showinfo("Sucesso", "Reserva salva com sucesso!")  # Mensagem de sucesso


def atualizar_faturamento():
    dados = ler_dados()
    faturamento = calcular_faturamento(dados)
    label_faturamento["text"] = f"Faturamento Total: R$ {faturamento:.2f}"

def abrir_lista_reservas():
    global janela_reservas
    try:
        if janela_reservas.winfo_exists():
          janela_reservas.focus()
          return
    except NameError:
      pass
    janela_reservas = tk.Toplevel(root)
    janela_reservas.title("Lista de Reservas")
    janela_reservas.config(bg="#00038B")

    # Treeview (Tabela)
    tree = ttk.Treeview(janela_reservas, columns=("ID", "Nome", "Diária", "Dias", "Total", "Chegada", "Saída"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Diária", text="Diária")
    tree.heading("Dias", text="Dias")
    tree.heading("Total", text="Total")
    tree.heading("Chegada", text="Chegada")
    tree.heading("Saída", text="Saída")
    tree.grid(row=1, column=0, columnspan=4, sticky="nsew")
    janela_reservas.grid_columnconfigure(0, weight=1)
    janela_reservas.grid_rowconfigure(1, weight=1)

    def atualizar_tabela():
        for item in tree.get_children():
            tree.delete(item)
        dados = ler_dados()
        for reserva in dados:
            tree.insert("", "end", values=(reserva["id"], reserva["nome"], reserva["diaria"], reserva["dias"], reserva["preco_total"], reserva["chegada"], reserva["saida"]))
    
    atualizar_tabela()
    # Barra de Busca
    entry_busca = tk.Entry(janela_reservas, font=("Arial",12))
    entry_busca.grid(row=0, column=1, sticky="ew")

    def buscar():
        termo = entry_busca.get().lower()
        
        # Limpa a tabela antes de filtrar
        for item in tree.get_children():
            tree.delete(item)

        dados = ler_dados() # Lê os dados do JSON

        resultados = []

        # REMOVE a condição if termo != "":
        if termo == "": #verifica se o termo de busca está vazio
            resultados = dados
        else:
            for reserva in dados:
                nome = reserva["nome"].lower()
                chegada = reserva["chegada"]
                saida = reserva["saida"]

                if termo in nome or termo in chegada or termo in saida:
                    resultados.append(reserva)
        

        # Insere apenas os resultados filtrados na tabela
        for reserva in resultados:
            tree.insert("", "end", values=(reserva["id"], reserva["nome"], reserva["diaria"], reserva["dias"], reserva["preco_total"], reserva["chegada"], reserva["saida"]))


    botao_buscar = tk.Button(janela_reservas, text="Buscar", command=buscar, font=("Arial",12,"bold"), bg="#01DB20", fg="#60005F")
    botao_buscar.grid(row=0, column=2)

    def editar_reserva():
        item_selecionado = tree.selection()
        if not item_selecionado:
            messagebox.showinfo("Aviso", "Selecione uma reserva para editar.")
            return

        id_reserva = tree.item(item_selecionado[0])["values"][0]
        dados = ler_dados()
        reserva_index = -1

        for i, reserva in enumerate(dados):
            if reserva['id'] == id_reserva:
                reserva_index = i
                break

        if reserva_index == -1:
          return

        janela_edicao = tk.Toplevel(janela_reservas)
        janela_edicao.title("Editar Reserva")
        janela_edicao.config(bg="#5E4000")

        # Cria os inputs de edição
        label_nome_edicao = tk.Label(janela_edicao, text="Nome:", font=("Arial",12), bg="#5E4000", fg="#ffffff")
        label_nome_edicao.grid(row=0, column=0)
        entry_nome_edicao = tk.Entry(janela_edicao, font=("Arial",12))
        entry_nome_edicao.grid(row=0, column=1)
        entry_nome_edicao.insert(0, dados[reserva_index]['nome'])

        label_diaria_edicao = tk.Label(janela_edicao, text="Diária:", font=("Arial",12), bg="#5E4000", fg="#ffffff")
        label_diaria_edicao.grid(row=1, column=0)
        entry_diaria_edicao = tk.Entry(janela_edicao, font=("Arial",12))
        entry_diaria_edicao.grid(row=1, column=1)
        entry_diaria_edicao.insert(0, dados[reserva_index]['diaria'])

        label_dias_edicao = tk.Label(janela_edicao, text="Dias:", font=("Arial",12), bg="#5E4000", fg="#ffffff")
        label_dias_edicao.grid(row=2, column=0)
        entry_dias_edicao = tk.Entry(janela_edicao, font=("Arial",12))
        entry_dias_edicao.grid(row=2, column=1)
        entry_dias_edicao.insert(0, dados[reserva_index]['dias'])

        label_chegada_edicao = tk.Label(janela_edicao, text="Chegada:", font=("Arial",12), bg="#5E4000", fg="#ffffff")
        label_chegada_edicao.grid(row=3, column=0)
        entry_chegada_edicao = tk.Entry(janela_edicao, font=("Arial",12))
        entry_chegada_edicao.grid(row=3, column=1)
        entry_chegada_edicao.insert(0, dados[reserva_index]['chegada'])

        label_saida_edicao = tk.Label(janela_edicao, text="Saída:", font=("Arial",12), bg="#5E4000", fg="#ffffff")
        label_saida_edicao.grid(row=4, column=0)
        entry_saida_edicao = tk.Entry(janela_edicao, font=("Arial",12))
        entry_saida_edicao.grid(row=4, column=1)
        entry_saida_edicao.insert(0, dados[reserva_index]['saida'])
        
        def salvar_edicao():
          try:
            dados[reserva_index]['nome'] = entry_nome_edicao.get()
            dados[reserva_index]['diaria'] = float(entry_diaria_edicao.get())
            dados[reserva_index]['dias'] = int(entry_dias_edicao.get())
            dados[reserva_index]['chegada'] = entry_chegada_edicao.get()
            dados[reserva_index]['saida'] = entry_saida_edicao.get()
            dados[reserva_index]["preco_total"] = dados[reserva_index]['diaria'] * dados[reserva_index]['dias']
            if not validar_data(dados[reserva_index]['chegada']) or not validar_data(dados[reserva_index]['saida']):
              messagebox.showerror("Erro", "Data inválida. Use o formato DD-MM-YYYY")
              return
            salvar_dados(dados)
            atualizar_tabela()
            atualizar_faturamento()
            janela_edicao.destroy()
          except ValueError:
            messagebox.showerror("Erro", "Diária e Dias devem ser números!")

        botao_salvar_edicao = tk.Button(janela_edicao, text="Salvar Edição", command=salvar_edicao, font=("Arial",12,"bold"), bg="#8A008F", fg="#ffffff")
        botao_salvar_edicao.grid(row=5, column=0, columnspan=2)

    botao_editar = tk.Button(janela_reservas, text="Editar", command=editar_reserva, font=("Arial",12,"bold"), bg="#00E5BD", fg="#720101")
    botao_editar.grid(row=2, column=0)

    def excluir_reserva():
        item_selecionado = tree.selection()
        if not item_selecionado:
            messagebox.showinfo("Aviso", "Selecione uma reserva para excluir.")
            return

        if messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir esta reserva?"):
            try:
                id_reserva = int(tree.item(item_selecionado[0])["values"][0])
                dados = ler_dados()

                # Encontrar o índice da reserva a ser excluída
                for i, reserva in enumerate(dados):
                    if reserva["id"] == id_reserva:
                        del dados[i]
                        break

                #Reatribuir os ids das reservas
                for i, reserva in enumerate(dados):
                  dados[i]["id"] = i + 1
                
                salvar_dados(dados)
                atualizar_tabela()
                atualizar_faturamento()
                messagebox.showinfo("Sucesso", "Reserva excluída com sucesso.")
            except (ValueError, IndexError):
                messagebox.showerror("Erro", "Ocorreu um erro ao excluir a reserva.")

    botao_excluir = tk.Button(janela_reservas, text="Excluir", command=excluir_reserva, font=("Arial",12,"bold"), bg="#FF0303", fg="#224B00")
    botao_excluir.grid(row=2, columnspan=4)

root = tk.Tk()
root.title("Sistema de Gerenciamento de Hotel")
root.config(bg="#0BE800")

#Criação dos inputs e labels da interface
label_nome = tk.Label(root, text="Nome do Cliente:", font=("Arial",12), bg="#0BE800")
label_nome.grid(row=0, column=0, sticky="w")
entry_nome = tk.Entry(root, font=("Arial",12))
entry_nome.grid(row=0, column=1, sticky="ew")

label_diaria = tk.Label(root, text="Preço da Diária:", font=("Arial",12), bg="#0BE800")
label_diaria.grid(row=1, column=0, sticky="w")
entry_diaria = tk.Entry(root, font=("Arial",12))
entry_diaria.grid(row=1, column=1, sticky="ew")

label_dias = tk.Label(root, text="Quantidade de Dias:", font=("Arial",12), bg="#0BE800")
label_dias.grid(row=2, column=0, sticky="w")
entry_dias = tk.Entry(root, font=("Arial",12))
entry_dias.grid(row=2, column=1, sticky="ew")

label_chegada = tk.Label(root, text="Data de Chegada (DD-MM-AAAA):", font=("Arial",12), bg="#0BE800")
label_chegada.grid(row=3, column=0, sticky="w")
entry_chegada = tk.Entry(root, font=("Arial",12))
entry_chegada.grid(row=3, column=1, sticky="ew")

label_saida = tk.Label(root, text="Data de Saída (DD-MM-AAAA):", font=("Arial",12), bg="#0BE800")
label_saida.grid(row=4, column=0, sticky="w")
entry_saida = tk.Entry(root, font=("Arial",12))
entry_saida.grid(row=4, column=1, sticky="ew")

botao_salvar = tk.Button(root, text="Salvar Reserva", command=salvar_reserva, font=("Arial",12,"bold"), bg="#0004A0", fg="#ffffff")
botao_salvar.grid(row=5, column=0, columnspan=2)

botao_lista_reservas = tk.Button(root, text="Lista de Reservas", command=abrir_lista_reservas, font=("Arial",12,"bold"), bg="#9100A6", fg="#ffffff")
botao_lista_reservas.grid(row=7, column=0, columnspan=2)

label_faturamento = tk.Label(root, text="Faturamento Total: R$ 0.00", font=("Arial",15,"bold"), bg="#0BE800", fg="#454F01")
label_faturamento.grid(row=6, column=0, columnspan=2)

root.columnconfigure(1, weight=1)

atualizar_faturamento()
root.mainloop()