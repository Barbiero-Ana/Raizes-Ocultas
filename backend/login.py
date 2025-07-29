from PyQt6.QtWidgets import (QApplication, QWidget, QMessageBox, QListWidgetItem, 
                            QLineEdit, QRadioButton, QCheckBox, QComboBox, QDateEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QDate
from PyQt6 import uic
from database.criar_banco import Database
import sys
from validador import Validador
import requests
import sqlite3
import hashlib

class Login:
    def __init__(self):
        super().__init__()
        self.db = Database("Raizes_Ocultas")
    
    def salvar_cliente(self):
        # Coleta dados dos campos
        campos = {
            'Nome': self.nome.text(),
            'Email': self.email.text(),
            'Senha': self.senha.text()
        }

        # Validar campos obrigatórios
        for campo, valor in campos.items():
            if not valor.strip():
                Validador.mostrar_erro(self, "Campo obrigatório", f"O campo {campo} é obrigatório")
                return

        # Validar CPF
        valido, msg = Validador.validar_cpf(campos['CPF'], self.db)
        if not valido:
            Validador.mostrar_erro(self, "CPF inválido", msg)
            return
        
        # Validar Email
        valido, msg = Validador.validar_email(campos['Email'])
        if not valido:
            Validador.mostrar_erro(self, "Email inválido", msg)
            return
        
        # Hash da senha
        senha_hash = hashlib.sha256(campos['Senha'].encode()).hexdigest()
        
        try:
            # Insere cliente no banco de dados
            id_cliente = self.db.inserir_cliente(
                nome=campos['Nome'].strip(),
                email=campos['Email'].strip(),
                senha=senha_hash
            )
            
            QMessageBox.information(self, "Sucesso", "Cliente cadastrado com sucesso!")
            return True
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                Validador.mostrar_erro(self, "Erro", "Este CPF ou Email já está cadastrado no sistema.")
            else:
                Validador.mostrar_erro(self, "Erro", f"Erro de integridade: {str(e)}")
            return False
        
        except Exception as e:
            QMessageBox.critical(self, "Erro", f'Erro ao cadastrar cliente: {str(e)}')
            return False