from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QWidget
)
from PyQt6.QtGui import QPixmap, QCursor
from PyQt6.QtCore import Qt


class ClassRegisterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Criar Nova Turma")
        self.setFixedSize(420, 580)
        self.setStyleSheet("background-color: #F8F8F8;")

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

        # Criar um container só para centralizar a logo e evitar cortes
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

        # --- ID da turma ---
        self.id_label = QLabel("ID da Turma: 001")
        self.id_label.setStyleSheet("font-size: 14px; color: #333; font-weight: bold;")
        self.id_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.id_label)

        # --- Nome da turma ---
        self.nome_turma_input = QLineEdit()
        self.nome_turma_input.setPlaceholderText("Digite o nome da turma")
        self.nome_turma_input.setFixedSize(360, 40)
        self.nome_turma_input.setStyleSheet(estilo_input)
        add_input("Nome da Turma:", self.nome_turma_input)

        # --- Qtd alunos ---
        self.combo_qtd_alunos = QComboBox()
        self.combo_qtd_alunos.addItems([str(i) for i in range(10, 51)])
        self.combo_qtd_alunos.setFixedSize(360, 40)
        self.combo_qtd_alunos.setStyleSheet(estilo_input)
        add_input("Quantidade de Alunos:", self.combo_qtd_alunos)

        # --- turmas ---
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
