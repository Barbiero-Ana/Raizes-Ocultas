# Crie um novo arquivo listar_turmas_screen.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt

class ListarTurmasDialog(QDialog):
    def __init__(self, parent=None, id_usuario=None):
        super().__init__(parent)
        self.setWindowTitle("Minhas Turmas")
        self.setFixedSize(500, 400)
        self.id_usuario = id_usuario
        
        # Layout principal
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Título
        lbl_titulo = QLabel("Turmas Criadas")
        lbl_titulo.setStyleSheet("font-size: 18px; font-weight: bold;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        # Área de scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Carrega as turmas
        self.carregar_turmas(scroll_layout)
        
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)
        
        # Botão fechar
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        layout.addWidget(btn_fechar)
    
    def carregar_turmas(self, layout):
        from backend.cadastrar_turma import CadastrarTurma
        
        cadastro = CadastrarTurma(self.id_usuario)
        turmas = cadastro.listar_turmas_usuario(self.id_usuario)
        
        if not turmas:
            lbl_vazio = QLabel("Você ainda não criou nenhuma turma.")
            lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_vazio)
            return
        
        for turma in turmas:
            turma_id, nome, quantidade, serie = turma
            widget_turma = QWidget()
            widget_turma.setStyleSheet("""
                QWidget {
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    padding: 10px;
                    margin: 5px;
                }
            """)
            
            turma_layout = QVBoxLayout(widget_turma)
            
            lbl_nome = QLabel(f"<b>{nome}</b>")
            lbl_detalhes = QLabel(f"Série: {serie} | Alunos: {quantidade}")
            
            turma_layout.addWidget(lbl_nome)
            turma_layout.addWidget(lbl_detalhes)
            
            layout.addWidget(widget_turma)