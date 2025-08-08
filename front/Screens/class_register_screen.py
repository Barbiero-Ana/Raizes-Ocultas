from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QWidget, QMessageBox
)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt
import sqlite3
from backend.cadastrar_turma import CadastrarTurma  # Moved import to top level


class ClassRegisterDialog(QDialog):
    def __init__(self, parent=None, id_usuario=None):
        super().__init__(parent)
        self.id_usuario = id_usuario  # Armazena o id_usuario
        self.setWindowTitle("Criar Nova Turma")
        self.setFixedSize(420, 580)
        self.setStyleSheet("background-color: #F8F8F8;")
        self.id_usuario = id_usuario  # Armazenar o ID do usuário

        main_widget = QWidget()
        layout = QVBoxLayout(main_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(12)
        self.setLayout(layout)

        # --- Logo ---
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pixmap = QPixmap("assets/ScreenElements/gamescreen/logo-temp.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaledToWidth(130, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)

        logo_container = QWidget()
        logo_layout = QHBoxLayout(logo_container)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.addWidget(self.logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_container)

        estilo_input = """
            QLineEdit, QComboBox {
                padding: 1px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: white;
                color: black;
            }
            QLineEdit::placeholder {
                color: #aaa;
            }
            QComboBox QAbstractItemView {
                color: #000;
                background-color: white;
                selection-background-color: #e0e0e0;
            }
        """

        def add_input(label_text, widget):
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 13px; color: #333; font-weight: bold;")
            layout.addWidget(label)
            layout.addWidget(widget)

        self.id_label = QLabel("ID da Turma: 001")
        self.id_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.id_label)

        self.nome_turma_input = QLineEdit()
        self.nome_turma_input.setPlaceholderText("Digite o nome da turma")
        self.nome_turma_input.setFixedSize(360, 40)
        self.nome_turma_input.setStyleSheet(estilo_input)
        add_input("Nome da Turma:", self.nome_turma_input)

        self.combo_qtd_alunos = QComboBox()
        self.combo_qtd_alunos.addItems([str(i) for i in range(10, 51)])
        self.combo_qtd_alunos.setFixedSize(360, 40)
        self.combo_qtd_alunos.setStyleSheet(estilo_input)
        add_input("Quantidade de Alunos:", self.combo_qtd_alunos)

        self.combo_serie = QComboBox()
        series = [
            "6º ano", "7º ano", "8º ano", "9º ano",
            "1º ano do Ensino Médio", "2º ano do Ensino Médio", "3º ano do Ensino Médio"
        ]
        self.combo_serie.addItems(series)
        self.combo_serie.setFixedSize(360, 40)
        self.combo_serie.setStyleSheet(estilo_input)
        add_input("Série da Turma:", self.combo_serie)

        self.btn_criar = QPushButton("Criar Turma")
        self.btn_criar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_criar.setFixedSize(360, 45)
        self.btn_criar.setStyleSheet("""
            QPushButton {
                background-color: #130060;
                color: white;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #110444;
            }
        """)
        layout.addWidget(self.btn_criar)
        self.btn_criar.clicked.connect(self.cadastrar_turma)

        self.btn_voltar = QPushButton("Voltar")
        self.btn_voltar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voltar.setFixedSize(360, 35)
        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #110444;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.btn_voltar.clicked.connect(self.reject)
        layout.addWidget(self.btn_voltar)

    def cadastrar_turma(self):
        """Função para cadastrar a turma usando os dados dos inputs"""
        nome = self.nome_turma_input.text().strip()
        quantidade = int(self.combo_qtd_alunos.currentText())
        serie = self.combo_serie.currentText()

        # Validar os dados
        if not nome:
            QMessageBox.warning(self, "Aviso", "O nome da turma é obrigatório!")
            return

        # Verifica se id_usuario está definido
        if self.id_usuario is None:
            QMessageBox.critical(self, "Erro", "Usuário não identificado. Faça login novamente.")
            return

        # Usar a classe CadastrarTurma para cadastrar
        cadastro = CadastrarTurma(self.id_usuario)
        sucesso, mensagem, turma_id = cadastro.cadastrar_turma(nome, quantidade, serie)

        if sucesso:
            QMessageBox.information(self, "Sucesso", mensagem)
            self.accept()  # Fechar o diálogo após cadastro bem-sucedido
        else:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Erro")
            msg_box.setText(mensagem)
            msg_box.setStyleSheet("QLabel{color: red;}")
            msg_box.exec()