import sys
import re
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QMessageBox,
    QLineEdit, QCheckBox, QWidget, QVBoxLayout, QGraphicsOpacityEffect,
)
from PyQt6.QtGui import QPixmap, QCursor, QIcon
from PyQt6.QtCore import Qt, QPropertyAnimation
import random

class HoverLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.setOpenExternalLinks(False)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.default_color = "#020EB6"
        self.hover_color = "#010055"
        self.hovered = False
        self.text_template = (
            '<span style="color:#333333;">Não tem uma conta? </span>'
            '<a href="#" style="color:{color}; text-decoration:none; font-weight:bold;">'
            'Crie aqui</a>'
        )
        self.update_text()

    def enterEvent(self, event):
        self.hovered = True
        self.update_text()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.hovered = False
        self.update_text()
        super().leaveEvent(event)

    def update_text(self):
        color = self.hover_color if self.hovered else self.default_color
        self.setText(self.text_template.format(color=color))

    def mouseReleaseEvent(self, event):
        self.linkActivated.emit("#")
        super().mouseReleaseEvent(event)

# ---------------------------------- login ---------------

class TelaLogin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Raízes Ocultas - Login")
        self.setFixedSize(1000, 700)
        self.setStyleSheet("background-color: white;")
        self.id_usuario = None  # Para armazenar ID do usuário
        
        # Container central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Logo
        self.logo = QLabel()
        logo_path = "assets/ScreenElements/MT-bandeira-logo.png"
        if os.path.exists(logo_path):
            self.logo.setPixmap(
                QPixmap(logo_path).scaledToWidth(250, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.logo.setText("🎮 RAÍZES OCULTAS 🎮")
            self.logo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        
        self.logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.logo)
        layout.addSpacing(40)

        # --- Email ---
        label_email = QLabel("E-mail")
        label_email.setStyleSheet("font-size: 13px; color: #333; font-weight: bold;")
        layout.addWidget(label_email, alignment=Qt.AlignmentFlag.AlignLeft)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("E-mail")
        self.input_email.setFixedSize(300, 40)
        self.input_email.setStyleSheet("""
            QLineEdit {
                padding-left: 10px;
                font-size: 14px;
                color: #979797;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        # Ícone do email (com fallback)
        email_icon_path = "assets/ScreenElements/icons/mail_vector.png"
        if os.path.exists(email_icon_path):
            icone_email = QIcon(QPixmap(email_icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
            self.input_email.addAction(icone_email, QLineEdit.ActionPosition.LeadingPosition)
        
        layout.addWidget(self.input_email, alignment=Qt.AlignmentFlag.AlignLeft)

        # --- Senha ---
        label_senha = QLabel("Senha")
        label_senha.setStyleSheet("font-size: 13px; color: #333; font-weight: bold;")
        layout.addWidget(label_senha, alignment=Qt.AlignmentFlag.AlignLeft)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_senha.setFixedSize(300, 40)
        self.input_senha.setStyleSheet("""
            QLineEdit {
                padding-left: 10px;
                font-size: 14px;
                color: #979797;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        """)
        
        # Ícone da senha (com fallback)
        senha_icon_path = "assets/ScreenElements/icons/password_vector.png"
        if os.path.exists(senha_icon_path):
            icone_senha = QIcon(QPixmap(senha_icon_path).scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
            self.input_senha.addAction(icone_senha, QLineEdit.ActionPosition.LeadingPosition)
        
        layout.addWidget(self.input_senha, alignment=Qt.AlignmentFlag.AlignLeft)

        # Botão acessar
        self.botao_acessar = QPushButton("Acessar")
        self.botao_acessar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.botao_acessar.setFixedHeight(40)
        self.botao_acessar.setStyleSheet("""
            background-color: #2B1D61;
            color: white;
            font-weight: bold;
            font-size: 16px;
            border-radius: 5px;
        """)
        layout.addWidget(self.botao_acessar)
        self.botao_acessar.clicked.connect(self.validar_e_abrir_jogo)

        # Label para mensagens de erro
        self.label_mensagem = QLabel("")
        self.label_mensagem.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label_mensagem.setStyleSheet("color: red; font-size: 12px; margin-top: 10px;")
        self.label_mensagem.setWordWrap(True)
        layout.addWidget(self.label_mensagem)

        # Label para registro
        self.label_registro = HoverLabel()
        self.label_registro.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label_registro.linkActivated.connect(self.abrir_tela_cadastro)
        layout.addWidget(self.label_registro)

        # Elementos decorativos
        self.dec_imagens()

    def validar_e_abrir_jogo(self):
        email = self.input_email.text().strip()
        senha = self.input_senha.text().strip()
        
        # Limpar mensagens anteriores
        self.label_mensagem.setText("")
        
        # Validações básicas
        if not email:
            self.label_mensagem.setText("Por favor, digite seu e-mail.")
            return
        
        if not senha:
            self.label_mensagem.setText("Por favor, digite sua senha.")
            return
        
        try:
            projeto_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            if projeto_root not in sys.path:
                sys.path.insert(0, projeto_root)
            
            from backend.login import Login
            
            login_system = Login()
            
            sucesso, mensagem, id_usuario = login_system.realizar_login(email, senha)
            
            if sucesso:
                self.id_usuario = id_usuario
                print(f"Login bem-sucedido! ID do usuário: {id_usuario}")
                
                self.abrir_game_animacao()
            else:
                self.label_mensagem.setText(mensagem)
                
                if "não cadastrado" in mensagem.lower():
                    resposta = QMessageBox.question(
                        self,
                        "Cadastro",
                        "E-mail não encontrado. Deseja criar uma nova conta?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if resposta == QMessageBox.StandardButton.Yes:
                        self.abrir_tela_cadastro()
                        
        except Exception as e:
            print(f"Erro ao fazer login: {e}")
            print("⚠️  Usando modo de teste - login sem validação")
            self.abrir_game_animacao()

    def abrir_tela_cadastro(self):
        self.tela_cadastro = TelaCadastro(tela_login_callback=self.show)
        self.tela_cadastro.show()
        self.hide()

    def dec_imagens(self):
        imagens_decorativas = [
            ("Viola-com-chita.png", -400, -400, 900, 2000),
            ("organic-chita-2.png", -120, -70, 600, 350),
            ("organic-chita.png", 780, 550, 400, 550),
            ("dance-chita.png", 700, -250, 900, 2000)
        ]
        
        for nome_img, x, y, w, h in imagens_decorativas:
            caminho = f"assets/ScreenElements/{nome_img}"
            if os.path.exists(caminho):
                self.decorar(nome_img, x, y, w, h)

    def decorar(self, nome_img, x, y, w, h):
        label = QLabel(self)
        label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        label.setStyleSheet("background: transparent;")
        pixmap = QPixmap(f"assets/ScreenElements/{nome_img}").scaled(
            w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        label.setPixmap(pixmap)
        label.resize(pixmap.size())
        label.move(x, y)
        label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        label.show()

    # ----------- game screen transition ---------------
    def abrir_game_animacao(self):
        self.animar_transicao(self.ir_game_screen)

    def animar_transicao(self, ao_terminar_callback):
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)

        self.animacao = QPropertyAnimation(self.effect, b"opacity")
        self.animacao.setDuration(700)
        self.animacao.setStartValue(1.0)
        self.animacao.setEndValue(0.0)
        self.animacao.finished.connect(lambda: (
            self.setGraphicsEffect(None),  
            ao_terminar_callback(fade_in=True)
        ))
        self.animacao.start()

    def ir_game_screen(self, fade_in=False):
        try:
            # Import dinâmico do GameScreen
            from game_screen import GameScreen
            
            self.tela_game = GameScreen(tela_login=self)
            self.tela_game.show()

            if fade_in:
                effect_new = QGraphicsOpacityEffect(self.tela_game)
                self.tela_game.setGraphicsEffect(effect_new)

                self.anim_in = QPropertyAnimation(effect_new, b"opacity")  
                self.anim_in.setDuration(700)
                self.anim_in.setStartValue(0.0)
                self.anim_in.setEndValue(1.0)
                self.anim_in.start()

                self.close()
            else:
                self.close()
                
        except ImportError as e:
            print(f"Erro ao importar GameScreen: {e}")
            QMessageBox.information(self, "Sucesso", "Login realizado com sucesso!\n(Tela do jogo não disponível)")

# ---------------------------------- cadastro ---------------

class TelaCadastro(QMainWindow):
    def __init__(self, tela_login_callback):
        super().__init__()
        self.setWindowTitle("Raízes Ocultas - Cadastro")
        self.setFixedSize(420, 640)
        self.setStyleSheet("background-color: #F8F8F8;")
        self.tela_login_callback = tela_login_callback

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(10)
        central.setLayout(layout)

        # Logo
        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_path = "assets/ScreenElements/MT-bandeira-logo.png"
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                self.logo.setPixmap(pixmap.scaled(160, 80, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            self.logo.setText("📝 CADASTRO")
            self.logo.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
            
        layout.addWidget(self.logo)

        estilo_input = """
            QLineEdit {
                padding: 9px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: white;
                color: black;
            }
            QLineEdit::placeholder {
                color: #aaa;
            }
        """

        def add_input(label_text, line_edit):
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 13px; color: #333;")
            layout.addWidget(label)
            layout.addWidget(line_edit)

        # Email
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("exemplo@email.com")
        self.input_email.setFixedSize(360, 40)
        self.input_email.setStyleSheet(estilo_input)
        add_input("E-mail:", self.input_email)

        # Senha
        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Digite sua senha")
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_senha.setFixedSize(360, 40)
        self.input_senha.setStyleSheet(estilo_input)
        self.input_senha.textChanged.connect(self.atualiza_forca_senha)
        add_input("Senha:", self.input_senha)

        # Força da senha
        self.label_forca_senha = QLabel("")
        self.label_forca_senha.setStyleSheet("font-size: 12px; color: #666;")
        layout.addWidget(self.label_forca_senha)

        # Repetir Senha
        self.input_repetir_senha = QLineEdit()
        self.input_repetir_senha.setPlaceholderText("Repita a senha")
        self.input_repetir_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_repetir_senha.setFixedSize(360, 40)
        self.input_repetir_senha.setStyleSheet(estilo_input)
        add_input("Confirmar senha:", self.input_repetir_senha)

        # Checkbox Termos
        self.checkbox_termos = QCheckBox("Li e aceito os Termos de Uso e Política de Privacidade.")
        self.checkbox_termos.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                color: #444;
                margin-top: 8px;
                margin-bottom: 8px;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid #130060;
                border-radius: 4px;
                background-color: #fff;
            }
            QCheckBox::indicator:checked {
                background-color: #130060;
                border: 2px solid #130060;
            }
            QCheckBox:hover {
                color: #130060;
            }
        """)
        layout.addWidget(self.checkbox_termos)

        # Captcha
        self.num1 = random.randint(1, 10)
        self.num2 = random.randint(1, 10)
        self.resultado_captcha = self.num1 + self.num2

        self.label_captcha = QLabel(f"Pergunta de segurança: Quanto é {self.num1} + {self.num2}?")
        self.label_captcha.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(self.label_captcha)

        self.input_captcha = QLineEdit()
        self.input_captcha.setPlaceholderText("Sua resposta")
        self.input_captcha.setFixedSize(360, 40)
        self.input_captcha.setStyleSheet(estilo_input)
        layout.addWidget(self.input_captcha)

        # Botão Cadastrar
        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cadastrar.setFixedSize(360, 45)
        self.btn_cadastrar.setStyleSheet("""
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
        self.btn_cadastrar.clicked.connect(self.tentar_cadastrar)
        layout.addWidget(self.btn_cadastrar)

        # Botão Voltar
        self.btn_voltar = QPushButton("Voltar para Login")
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
        self.btn_voltar.clicked.connect(self.voltar_login)
        layout.addWidget(self.btn_voltar)

        # Mensagem
        self.label_msg = QLabel("")
        self.label_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_msg.setWordWrap(True)
        layout.addWidget(self.label_msg)

    def voltar_login(self):
        self.close()
        if self.tela_login_callback:
            self.tela_login_callback()

    def limpa_erro_estilo(self):
        for campo in [self.input_email, self.input_senha, self.input_repetir_senha, self.input_captcha]:
            campo.setStyleSheet("""
                QLineEdit {
                    padding: 9px;
                    font-size: 14px;
                    border: 1px solid #ccc;
                    border-radius: 6px;
                    background-color: white;
                    color: #000;
                }
                QLineEdit::placeholder {
                    color: #aaa;
                }
            """)

    def set_erro_estilo(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                padding: 9px;
                font-size: 14px;
                border: 2px solid red;
                border-radius: 6px;
                background-color: white;
                color: #000;
            }
            QLineEdit::placeholder {
                color: #aaa;
            }
        """)

    def valida_email(self, email):
        return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email) is not None

    def atualiza_forca_senha(self):
        senha = self.input_senha.text()
        força = self.calcula_forca_senha(senha)
        texto = "Força da senha: "
        if força < 2:
            texto += "<span style='color: red;'>Fraca</span>"
        elif força == 2:
            texto += "<span style='color: orange;'>Média</span>"
        else:
            texto += "<span style='color: green;'>Forte</span>"
        self.label_forca_senha.setText(texto)

    def calcula_forca_senha(self, senha):
        força = sum(bool(re.search(p, senha)) for p in [r'.{8,}', r'[A-Z]', r'[0-9]', r'[\W_]'])
        return min(força, 3)

    def tentar_cadastrar(self):
        """Tenta realizar o cadastro do usuário"""
        self.limpa_erro_estilo()
        email = self.input_email.text().strip()
        senha = self.input_senha.text()
        repetir = self.input_repetir_senha.text()
        captcha = self.input_captcha.text().strip()
        termos = self.checkbox_termos.isChecked()

        erros = []

        # Validações locais
        if not email:
            erros.append("Informe o e-mail.")
            self.set_erro_estilo(self.input_email)
        elif not self.valida_email(email):
            erros.append("Formato de e-mail inválido.")
            self.set_erro_estilo(self.input_email)

        if not senha:
            erros.append("Digite sua senha.")
            self.set_erro_estilo(self.input_senha)

        if not repetir:
            erros.append("Repita a senha.")
            self.set_erro_estilo(self.input_repetir_senha)
        elif senha != repetir:
            erros.append("As senhas não coincidem.")
            self.set_erro_estilo(self.input_senha)
            self.set_erro_estilo(self.input_repetir_senha)

        if not termos:
            erros.append("Você precisa aceitar os termos de uso.")

        if captcha != str(self.resultado_captcha):
            erros.append(f"Resposta incorreta. A resposta correta era {self.resultado_captcha}.")
            self.set_erro_estilo(self.input_captcha)

        # mostrar a budega do erro
        if erros:
            self.label_msg.setText("<br>".join(erros))
            self.label_msg.setStyleSheet("color: red; font-size: 12px;")
            return

        try:
            import hashlib
            from Database.criar_banco import Funcoes_DataBase
            import os
            
            db_path = os.path.join("Database", "raizes_ocultas.db")
            funcoes_db = Funcoes_DataBase(db_path)
            
            # Hash da senha
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            
            user_id = funcoes_db.inserir_cliente("Usuário", email, senha_hash)
            
            if user_id:
                self.label_msg.setText("✅ Cadastro realizado com sucesso!")
                self.label_msg.setStyleSheet("color: green; font-size: 13px;")
                
                self.input_email.clear()
                self.input_senha.clear()
                self.input_repetir_senha.clear()
                self.input_captcha.clear()
                self.checkbox_termos.setChecked(False)
                
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Sucesso")
                msg_box.setText("✅ Cadastro realizado com sucesso!")
                msg_box.setInformativeText(f"Email: {email}\nID: {user_id}\n\nAgora você pode fazer login!")
                msg_box.setIcon(QMessageBox.Icon.Information)
                
                msg_box.setStyleSheet("""
                    QMessageBox {
                        background-color: white;
                        color: black;
                    }
                    QMessageBox QLabel {
                        color: black;
                        font-size: 14px;
                    }
                    QMessageBox QPushButton {
                        background-color: #2B1D61;
                        color: white;
                        padding: 8px 16px;
                        border-radius: 4px;
                        font-weight: bold;
                        min-width: 80px;
                    }
                    QMessageBox QPushButton:hover {
                        background-color: #1a1040;
                    }
                """)
                
                msg_box.exec()
                
                # Voltar para tela de login
                self.voltar_login()
            else:
                self.label_msg.setText("❌ Erro ao cadastrar usuário.")
                self.label_msg.setStyleSheet("color: red; font-size: 12px;")
                
        except Exception as e:
            error_msg = str(e)
            if "UNIQUE constraint failed" in error_msg:
                self.label_msg.setText("❌ Este e-mail já está cadastrado.")
                self.set_erro_estilo(self.input_email)
            else:
                self.label_msg.setText(f"❌ Erro ao cadastrar: {error_msg}")
            
            self.label_msg.setStyleSheet("color: red; font-size: 12px;")
            print(f"Erro ao cadastrar: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaLogin()
    janela.show()
    sys.exit(app.exec())