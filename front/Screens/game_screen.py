from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtGui import QPixmap, QCursor, QFontDatabase
from PyQt6.QtCore import Qt


class GameScreen(QMainWindow):
    def __init__(self, tela_login=None):
        super().__init__()
        self.tela_login = tela_login  # referência opcional para tela login

        self.setWindowTitle("Raízes Ocultas - Jogo")
        self.setFixedSize(1000, 700)

        # --- Fonte medieval ---
        font_id = QFontDatabase.addApplicationFont("assets/fonts/AnalogWhispers.ttf")
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            self.fonte_medieval = families[0] if families else "Georgia"
        else:
            self.fonte_medieval = "Georgia"

        # --- Central widget ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Background com cover, mas para manter aspecto use 'contain' (imagem toda visível)
        central_widget.setStyleSheet("""
            QWidget {
                background-image: url('assets/ScreenElements/gamescreen/background-game.png');
                background-repeat: no-repeat;
                background-position: center;
                background-size: contain;
                background-color: #1a1a1a; /* cor base escura */
            }
        """)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # --- Top bar com botão voltar ---
        topo_layout = QHBoxLayout()
        topo_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_voltar = QPushButton("← Voltar")
        self.btn_voltar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voltar.setFixedSize(100, 40)
        self.btn_voltar.setStyleSheet(f"""
            QPushButton {{
                background-color: #4B3B8A;
                color: #FFD700;
                font-weight: bold;
                font-size: 14px;
                border-radius: 8px;
                border: 2px solid #6A52A3;
                font-family: "{self.fonte_medieval}", serif;
                text-shadow: 1px 1px 2px #000000bb;
            }}
            QPushButton:hover {{
                background-color: #5A4AA0;
                border-color: #FFD700;
                color: #FFFACD;
                box-shadow: 0 0 10px #FFD700;
            }}
            QPushButton:pressed {{
                background-color: #3E3278;
                border-color: #B8860B;
                color: #FFC107;
            }}
        """)
        self.btn_voltar.clicked.connect(self.voltar_para_login)

        topo_layout.addWidget(self.btn_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        topo_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(topo_layout)

        # --- Logo topo central ---
        self.logo_top = QLabel()
        pixmap_logo = QPixmap("assets/ScreenElements/logo_game.png")
        if not pixmap_logo.isNull():
            self.logo_top.setPixmap(pixmap_logo.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation))
        self.logo_top.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.logo_top.setStyleSheet(f"""
            font-family: "{self.fonte_medieval}", serif;
            font-size: 32px;
            color: #cfc28c;
            text-shadow: 2px 2px 4px #000000cc;
        """)
        main_layout.addWidget(self.logo_top)

        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Container dos botões ---
        botoes_container = QWidget()
        botoes_layout = QVBoxLayout(botoes_container)
        botoes_layout.setSpacing(25)
        botoes_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Estilo base botão com textura, bordas e sombra dourada
        estilo_botao = f"""
            QPushButton {{
                background-image: url('assets/textures/leather_texture.png');
                background-repeat: repeat;
                color: #d9c27f;
                font-weight: bold;
                font-size: 20px;
                padding: 14px 40px 14px 60px; /* padding left maior p/ ícone */
                border-radius: 14px;
                border: 3px solid #7a6f44;
                box-shadow: 3px 3px 10px rgba(0, 0, 0, 0.7);
                font-family: "{self.fonte_medieval}", serif;
                text-shadow: 2px 2px 3px #000000cc;
            }}
            QPushButton:hover {{
                background-color: #556b2f88; /* verde escuro translúcido sobre couro */
                border-color: #f5e86c;
                color: #fff8dc;
                box-shadow: 0 0 15px #f5e86c;
            }}
            QPushButton:pressed {{
                background-color: #3e4f1eaa;
                border-color: #cfc28c;
                color: #b9a75b;
                box-shadow: inset 0 0 5px #9a8f50;
            }}
        """

        # --- Criar botões com ícone runa à esquerda ---
        def criar_botao_com_icone(texto):
            botao_frame = QFrame()
            botao_layout = QHBoxLayout(botao_frame)
            botao_layout.setContentsMargins(0, 0, 0, 0)
            botao_layout.setSpacing(15)
            botao_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            lbl_icone = QLabel()
            pixmap_icone = QPixmap("assets/icons/runa.png").scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_icone.setPixmap(pixmap_icone)
            lbl_icone.setFixedSize(36, 36)
            botao_layout.addWidget(lbl_icone)

            btn = QPushButton(texto)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(estilo_botao)
            btn.setFixedHeight(56)
            botao_layout.addWidget(btn)

            return botao_frame, btn

        # Criar botões
        frame_novo, self.btn_novo_jogo = criar_botao_com_icone("Novo Jogo")
        frame_carregar, self.btn_carregar_jogo = criar_botao_com_icone("Carregar Jogo")
        frame_stats, self.btn_estatisticas = criar_botao_com_icone("Estatísticas")

        botoes_layout.addWidget(frame_novo)
        botoes_layout.addWidget(frame_carregar)
        botoes_layout.addWidget(frame_stats)

        main_layout.addWidget(botoes_container)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def voltar_para_login(self):
        self.close()
        if self.tela_login:
            self.tela_login.show()
