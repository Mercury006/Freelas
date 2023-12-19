import tkinter as tk
from tkinter import messagebox
from customtkinter import *
import mysql.connector
from mysql.connector import Error

class PadroesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Padrões")

        self.conectar_bd()
        self.criar_interface()
        self.carregar_padroes_do_bd()

    def conectar_bd(self):
        try:
            self.conn = mysql.connector.connect(
                host='localhost',
                user='root',
                password='',
                database='padroes'
            )
            self.criar_tabela()
        except Error as e:
            messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao MariaDB: {e}")
            self.conn = None

    def criar_tabela(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS padroes (
                              id INT AUTO_INCREMENT PRIMARY KEY,
                              sequencia TEXT)''')
            self.conn.commit()
            cursor.close()

    def carregar_padroes_do_bd(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id, sequencia FROM padroes ORDER BY id DESC LIMIT 10')
            padroes = cursor.fetchall()
            for id, sequencia in padroes:
                self.atualizar_lista(f"{id}: {sequencia}")
            cursor.close()

    def criar_interface(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # Defina a largura (width) desejada aqui (80 pixels)
        width = 80

        self.nova_sequencia_entry = CTkEntry(self.root, width=width)
        self.nova_sequencia_entry.pack(pady=20)
        self.nova_sequencia_entry.bind('<Return>', self.on_enter_press)

        adicionar_botao = CTkButton(self.root, text="Adicionar Padrão", command=self.adicionar_sequencia, width=width)
        adicionar_botao.pack(pady=20)

        self.lista_padroes = tk.Listbox(self.root, width=width, bg="#262626", fg="white", font="Arial", highlightcolor="#3b0487", highlightbackground="#3b0487", selectbackground="#3b0487")
        self.lista_padroes.pack(pady=20, padx=80)

        self.root.bind('<space>', self.on_space_press)

    def atualizar_lista(self, item):
        self.lista_padroes.insert(tk.END, item)

    def sequencia_existe(self, sequencia):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute('SELECT id FROM padroes WHERE sequencia = %s', (sequencia,))
            data = cursor.fetchone()
            cursor.close()
            return data is not None
        return False

    def adicionar_sequencia(self, event=None):
        sequencia = self.nova_sequencia_entry.get().strip()
        if sequencia:
            if not self.sequencia_existe(sequencia):
                if self.conn:
                    cursor = self.conn.cursor()
                    cursor.execute('INSERT INTO padroes (sequencia) VALUES (%s)', (sequencia,))
                    self.conn.commit()
                    cursor.close()
                    self.atualizar_lista_apos_adicao()
                self.nova_sequencia_entry.delete(0, tk.END)
            else:
                messagebox.showinfo("Padrão Existente", "Essa sequência já existe no banco de dados.")
        else:
            messagebox.showwarning("Sequência Vazia", "Por favor, insira uma sequência para adicionar.")

    def atualizar_lista_apos_adicao(self):
        self.lista_padroes.delete(0, tk.END)
        self.carregar_padroes_do_bd()

    def on_enter_press(self, event):
        self.adicionar_sequencia()

    def on_space_press(self, event):
        self.adicionar_sequencia()

if __name__ == "__main__":
    root = CTk()
    app = PadroesApp(root)
    root.geometry("600x400")
    root.mainloop()
