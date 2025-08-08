import random
from enum import Enum
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from database.criar_banco import Funcoes_DataBase

class SelecionarTurma:
    def __init__(self,root):
        self.root = root
        self.fdb = Funcoes_DataBase()
        self.id_usuario = None
        self.id_turma = None

    def menu_carregar_turma(self):
        turmas = self.fdb.carregar_turma()

        if not turmas:
            messagebox.showinfo("Sem Turma cadastrada","Nenhuma salva encontrada!")
            return 
        
        frame = tk.Frame(self.root)