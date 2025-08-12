# Crie um novo arquivo listar_turmas_screen.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, 
    QScrollArea, QWidget, QMessageBox,QHBoxLayout,QButtonGroup,
    QRadioButton
)
from PyQt6.QtCore import Qt

class ListarTurmasDialog(QDialog):
    def __init__(self, parent=None, id_usuario=None):
        super().__init__(parent)
        self.setWindowTitle("Minhas Turmas")
        self.setFixedSize(500, 400)
        self.id_usuario = id_usuario
        self.turma_selecionada = None
        
        # Layout principal
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Título
        lbl_titulo = QLabel("Selecione uma Turma para Jogar")
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
        
        # Botões
        btn_layout = QHBoxLayout()
        
        self.btn_selecionar = QPushButton("Selecionar Turma")
        self.btn_selecionar.clicked.connect(self.selecionar_turma)
        self.btn_selecionar.setEnabled(False)
        btn_layout.addWidget(self.btn_selecionar)
        
        btn_fechar = QPushButton("Fechar")
        btn_fechar.clicked.connect(self.close)
        btn_layout.addWidget(btn_fechar)
        
        layout.addLayout(btn_layout)
    
    def carregar_turmas(self, layout):
        from backend.cadastrar_turma import CadastrarTurma
        
        cadastro = CadastrarTurma(self.id_usuario)
        turmas = cadastro.listar_turmas_usuario(self.id_usuario)
        
        if not turmas:
            lbl_vazio = QLabel("Você ainda não criou nenhuma turma.")
            lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_vazio)
            return
        
        self.radio_group = QButtonGroup(self)
        
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
            
            turma_layout = QHBoxLayout(widget_turma)
            
            radio = QRadioButton()
            radio.toggled.connect(lambda checked, tid=turma_id: self.turma_selecionada_handler(checked, tid))
            self.radio_group.addButton(radio, turma_id)
            
            lbl_nome = QLabel(f"<b>{nome}</b> - Série: {serie} | Alunos: {quantidade}")
            
            turma_layout.addWidget(radio)
            turma_layout.addWidget(lbl_nome)
            turma_layout.addStretch()
            
            layout.addWidget(widget_turma)
    
    def turma_selecionada_handler(self, checked, turma_id):
        self.turma_selecionada = turma_id if checked else None
        self.btn_selecionar.setEnabled(checked)
    
    def selecionar_turma(self):
        if self.turma_selecionada:
            self.accept()  # Fecha o diálogo com resultado positivo
        else:
            QMessageBox.warning(self, "Aviso", "Selecione uma turma para continuar")
    
    @staticmethod
    def get_turma_selecionada(parent=None, id_usuario=None):
        dialog = ListarTurmasDialog(parent, id_usuario)
        result = dialog.exec()
        return dialog.turma_selecionada if result == QDialog.DialogCode.Accepted else None