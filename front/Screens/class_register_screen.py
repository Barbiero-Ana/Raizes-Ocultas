# class_register_screen.py
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QHBoxLayout
)
from PyQt6.QtCore import Qt

class ClassRegisterScreen(QMainWindow):
    def __init__(self, game_screen_callback):
        super().__init__()
        self.setWindowTitle("Raízes Ocultas - Criar Turmas")
        self.setFixedSize(420, 640)
        self.setStyleSheet("background-color: #F8F8F8;")
        self.game_screen_callback = game_screen_callback

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(10)
        central.setLayout(layout)

        # Título da tela
        title_label = QLabel("Criar Nova Turma")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        layout.addWidget(title_label)

        # Botão para voltar para a tela de game_screen
        btn_voltar = QPushButton("Voltar para Jogo")
        btn_voltar.setFixedSize(360, 45)
        btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: #130060;
                color: white;
                border-radius: 6px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #110444;
            }
        """)
        btn_voltar.clicked.connect(self.voltar_para_game_screen)
        layout.addWidget(btn_voltar)

        # Aqui você pode adicionar mais elementos como campos de entrada para criar a turma
        # e outros botões se necessário

    def voltar_para_game_screen(self):
        self.close()
        if self.game_screen_callback:
            self.game_screen_callback()

