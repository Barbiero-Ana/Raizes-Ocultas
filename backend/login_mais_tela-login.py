from login import Login
from front.Screens.Login_screen import TelaLogin
from database.criar_banco import Logica_Login
from front.Screens.Login_screen import TelaLogin
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


class Tela_Login(QWidget):

    def buscar_cadastro(self):
        login = self.login.text().strip()
        senha = self.senha.text().strip()

        if not login or not senha:
            QMessageBox.warning(self,'AVISO',"Por favor preencher todos os campos")
            return
        
        senha_hash = self.db.validar_usuario(login,senha_hash)
        
        if Validador.validar_email(login)[0]:
            usuario = self.db.obter_ususario_por_email(login)

            if not usuario:
                resposta = QMessageBox.question(
                    self,
                    "E-mail não cadastrado",
                    "E-mail não encontrado. Deseja se cadastrar ?",
                    QMessageBox.standardButton.YES | QMessageBox.standardButton.No
                )
                if resposta == QMessageBox.standardButton.Yes:
                    TelaLogin.abrir_tela_cadastro()
            