from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame
)
from PyQt6.QtGui import QPixmap, QCursor, QFontDatabase, QFont
from PyQt6.QtCore import Qt, QOperatingSystemVersion, QSysInfo


class GameScreen(QMainWindow):
    def __init__(self, tela_login=None):
        super().__init__()
        self.tela_login = tela_login 

        self.setWindowTitle("Raízes Ocultas - Jogo")
        self.setFixedSize(1000, 700)

        # --- Fonte
        import os

        # Caminho da fonte
        font_path = "assets/fonts/DUNGRG_.TTF"
        font_path = font_path.replace("\\", "/")  # Corrige as barras invertidas
        abs_font_path = os.path.abspath(font_path)

        # Verificar se o arquivo existe
        if os.path.exists(abs_font_path):
            print(f"A fonte foi encontrada: {abs_font_path}")
        else:
            print(f"Erro: Arquivo de fonte não encontrado em {abs_font_path}")

        # Carregar a fonte
        font_id = QFontDatabase.addApplicationFont(abs_font_path)
        print(f"Font ID: {font_id}")

        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            print(f"Families found: {families}")
            self.fonte_medieval = families[0] if families else "Georgia"
        else:
            print("Falha ao carregar a fonte!")
            self.fonte_medieval = "Georgia"

        # --- Central widget ---
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # --- Background 
        self.background_label = QLabel(central_widget)
        self.background_label.setPixmap(QPixmap("assets/ScreenElements/gamescreen/background-game.png"))
        self.background_label.setScaledContents(True)
        self.background_label.setGeometry(0, 0, 1000, 700)  
        self.background_label.lower()  

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # --- botão voltar ---
        topo_layout = QHBoxLayout()
        topo_layout.setContentsMargins(0, 0, 0, 0)

        self.btn_voltar = QPushButton("Sair")
        self.btn_voltar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voltar.setFixedSize(100, 50)

        self.adjust_button_font(self.btn_voltar)

        self.btn_voltar.setStyleSheet("""
            QPushButton {
                background-repeat: repeat;
                color: #d9c27f;
                font-weight: bold;
                padding: 10px 10px;
                border-radius: 14px;
                border: 3px solid #7a6f44;
            }
            QPushButton:hover {
                background-color: #556b2f88;
                border-color: #f5e86c;
                color: #fff8dc;
            }
            QPushButton:pressed {
                background-color: #3e4f1eaa;
                border-color: #cfc28c;
                color: #b9a75b;
            }
        """)

        self.btn_voltar.clicked.connect(self.voltar_para_login)
        topo_layout.addWidget(self.btn_voltar, alignment=Qt.AlignmentFlag.AlignLeft)
        topo_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(topo_layout)

        # --- logo 
        logo_layout = QHBoxLayout()
        logo_layout.setContentsMargins(0, -100, 0, 0)
        logo_layout.setSpacing(0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)  

        spacer_logo = QSpacerItem(370, -100, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        logo_layout.addItem(spacer_logo)

        self.logo_top = QLabel()
        pixmap_logo = QPixmap("assets/ScreenElements/gamescreen/logo-temp.png")
        if not pixmap_logo.isNull():
            self.logo_top.setPixmap(pixmap_logo.scaledToWidth(250, Qt.TransformationMode.SmoothTransformation))
        self.logo_top.setAlignment(Qt.AlignmentFlag.AlignCenter)

        logo_layout.addWidget(self.logo_top)
        main_layout.addLayout(logo_layout)

        # --- container dos botões ---
        botoes_container = QWidget()
        botoes_layout = QVBoxLayout(botoes_container)
        botoes_layout.setSpacing(25)
        botoes_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        estilo_botao = f"""
            QPushButton {{
                background-repeat: repeat;
                color: #d9c27f;
                font-weight: bold;
                font-size: 20px;
                padding: 14px 60px;
                border-radius: 14px;
                border: 3px solid #7a6f44;
                font-family: "{self.fonte_medieval}";
                qproperty-alignment: AlignCenter;
            }}
            QPushButton:hover {{
                background-color: #556b2f88;
                border-color: #f5e86c;
                color: #fff8dc;
                box-shadow: 0 0 15px #f5e86c;
            }}
            QPushButton:pressed {{
                background-color: #3e4f1eaa;
                border-color: #cfc28c;
                color: #b9a75b;
            }}
        """

        def criar_botao_com_icone(texto):
            botao_frame = QFrame()
            botao_frame.setFixedWidth(360)

            botao_layout = QHBoxLayout(botao_frame)
            botao_layout.setContentsMargins(0, 0, 0, 0)
            botao_layout.setSpacing(15)
            botao_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

            lbl_icone = QLabel()
            pixmap_icone = QPixmap("assets/ScreenElements/icons/runa.png").scaled(36, 36, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            lbl_icone.setPixmap(pixmap_icone)
            lbl_icone.setFixedSize(36, 36)
            botao_layout.addWidget(lbl_icone)

            btn = QPushButton(texto)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet(estilo_botao)
            btn.setFixedHeight(56)
            btn.setMinimumWidth(300) 
            btn.setMaximumWidth(300)
            self.adjust_button_font(btn)  # Ajustar a fonte dinamicamente
            botao_layout.addWidget(btn)

            return botao_frame, btn

        frame_novo, self.btn_novo_jogo = criar_botao_com_icone("Nova Turma")
        frame_carregar, self.btn_carregar_jogo = criar_botao_com_icone("Carregar Turma")
        frame_stats, self.btn_estatisticas = criar_botao_com_icone("Estatisticas")

        botoes_layout.addWidget(frame_novo)
        botoes_layout.addWidget(frame_carregar)
        botoes_layout.addWidget(frame_stats)

        main_layout.addWidget(botoes_container)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Botões no canto inferior direito ---
        botoes_inferiores = QWidget(central_widget)
        botoes_inferiores_layout = QHBoxLayout(botoes_inferiores)
        botoes_inferiores_layout.setSpacing(15)
        botoes_inferiores_layout.setContentsMargins(0, 0, 0, 0)
        botoes_inferiores_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        estilo_botao_pequeno = f"""
            QPushButton {{
                background-repeat: repeat;
                color: #d9c27f;
                font-weight: bold;
                font-size: 15px;
                padding: 10px 10px;
                border-radius: 12px;
                border: 2px solid #7a6f44;
                font-family: "{self.fonte_medieval}";
                qproperty-alignment: AlignCenter;
            }}
            QPushButton:hover {{
                background-color: #556b2f88;
                border-color: #f5e86c;
                color: #fff8dc;
                box-shadow: 0 0 12px #f5e86c;
            }}
            QPushButton:pressed {{
                background-color: #3e4f1eaa;
                border-color: #cfc28c;
                color: #b9a75b;
            }}
        """

        self.btn_equipe = QPushButton("Equipe")
        self.btn_equipe.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_equipe.setStyleSheet(estilo_botao_pequeno)
        self.btn_equipe.setFixedSize(100, 40)
        self.adjust_button_font(self.btn_equipe)

        self.btn_projeto = QPushButton("Projeto")
        self.btn_projeto.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_projeto.setStyleSheet(estilo_botao_pequeno)
        self.btn_projeto.setFixedSize(100, 40)
        self.adjust_button_font(self.btn_projeto)

        botoes_inferiores_layout.addWidget(self.btn_projeto)
        botoes_inferiores_layout.addWidget(self.btn_equipe)

        botoes_inferiores.setFixedWidth(230)
        botoes_inferiores.setFixedHeight(50)
        botoes_inferiores.move(self.width() - botoes_inferiores.width() - 20, self.height() - botoes_inferiores.height() - 20)
        botoes_inferiores.show()

    def adjust_button_font(self, button):
        screen_width = self.width()
        screen_height = self.height()

        if button == self.btn_voltar:
            font_size = int(screen_width * 0.015)  # Um valor menor para o botão "Sair"
        else:
            font_size = int(screen_width * 0.02)  # Para os outros botões

        font = QFont(self.fonte_medieval, font_size)
        button.setFont(font)


    def voltar_para_login(self):
        self.close()
        if self.tela_login:
            self.tela_login.show()
