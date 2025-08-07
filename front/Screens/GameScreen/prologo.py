import PyQt6.QtWidgets as QtWidgets
from database.criar_banco import Funcoes_DataBase
import os
from PyQt6 import QmainWindow, QtWidgets, QtCore, QtGui
import _tkinter as tinker

class PrologoScreen(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Raízes Ocultas - Prologo")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QtWidgets.QVBoxLayout()
        
        label = QtWidgets.QLabel("")
        layout.addWidget(label)
        
        self.setLayout(layout)