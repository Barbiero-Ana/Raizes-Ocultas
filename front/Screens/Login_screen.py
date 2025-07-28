import sys
import re
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QLineEdit, QCheckBox, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QPixmap, QCursor, QIcon
from PyQt6.QtCore import Qt


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

        # Container central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        # Logo
        self.logo = QLabel()
        self.logo.setPixmap(
            QPixmap("assets/ScreenElements/MT-bandeira-logo.png")
            .scaledToWidth(250, Qt.TransformationMode.SmoothTransformation)
        )
        self.logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.logo)
        layout.addSpacing(40)

        # Email
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
        icone_email = QIcon(QPixmap("assets/ScreenElements/icons/mail_vector.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        self.input_email.addAction(icone_email, QLineEdit.ActionPosition.LeadingPosition)
        layout.addWidget(self.input_email, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Senha
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
        icone_senha = QIcon(QPixmap("assets/ScreenElements/icons/password_vector.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio))
        self.input_senha.addAction(icone_senha, QLineEdit.ActionPosition.LeadingPosition)
        layout.addWidget(self.input_senha, alignment=Qt.AlignmentFlag.AlignHCenter)


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

        # Label para registro
        self.label_registro = HoverLabel()
        self.label_registro.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label_registro.linkActivated.connect(self.abrir_tela_cadastro)
        layout.addWidget(self.label_registro)

        self.dec_imagens()

    def abrir_tela_cadastro(self):
        self.tela_cadastro = TelaCadastro(tela_login_callback=self.show)
        self.tela_cadastro.show()
        self.hide()

    def dec_imagens(self):
        self.decorar("Viola-com-chita.png", -400, -400, 900, 2000)
        self.decorar("organic-chita-2.png", -120, -70, 600, 350)
        self.decorar("organic-chita.png", 780, 550, 400, 550)
        self.decorar("dance-chita.png", 700, -250, 900, 2000)

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

# ---------------------------------- cadastro ---------------


class TelaCadastro(QMainWindow):
    def __init__(self, tela_login_callback):
        super().__init__()
        self.setWindowTitle("Raízes Ocultas - Cadastro")
        self.setFixedSize(400, 600)
        self.setStyleSheet("background-color: white;")
        self.tela_login_callback = tela_login_callback

        # Central widget e layout principal
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        layout.setSpacing(15)
        central.setLayout(layout)

        # Logo com transparência e aspecto mantido
        self.logo = QLabel()
        self.logo.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.logo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        pixmap = QPixmap("assets/ScreenElements/MT-bandeira-logo.png")
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            self.logo.setText("Logo não encontrada")
            self.logo.setStyleSheet("color: red; font-size: 14px;")
        self.logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.logo)

        estilo_input = """
            QLineEdit {
                padding-left: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
                color: #000;
            }
            QLineEdit::placeholder {
                color: #888;
            }
        """

        # Campos de entrada
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("E-mail")
        self.input_email.setFixedSize(320, 40)
        self.input_email.setStyleSheet(estilo_input)
        layout.addWidget(self.input_email)

        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_senha.setFixedSize(320, 40)
        self.input_senha.setStyleSheet(estilo_input)
        self.input_senha.textChanged.connect(self.atualiza_forca_senha)
        layout.addWidget(self.input_senha)

        self.label_forca_senha = QLabel("Força da senha: ")
        self.label_forca_senha.setStyleSheet("font-size: 12px; color: #555;")
        layout.addWidget(self.label_forca_senha)

        self.input_repetir_senha = QLineEdit()
        self.input_repetir_senha.setPlaceholderText("Repita a senha")
        self.input_repetir_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_repetir_senha.setFixedSize(320, 40)
        self.input_repetir_senha.setStyleSheet(estilo_input)
        layout.addWidget(self.input_repetir_senha)

        self.checkbox_termos = QCheckBox("Aceito os termos de uso e a política de privacidade")
        self.checkbox_termos.setStyleSheet("font-size: 13px; color: #333;")
        layout.addWidget(self.checkbox_termos)

        self.label_captcha = QLabel("Quanto é 3 + 4?")
        self.label_captcha.setStyleSheet("font-size: 13px;")
        layout.addWidget(self.label_captcha)

        self.input_captcha = QLineEdit()
        self.input_captcha.setPlaceholderText("Sua resposta")
        self.input_captcha.setFixedSize(320, 40)
        self.input_captcha.setStyleSheet(estilo_input)
        layout.addWidget(self.input_captcha)

        # Botão de cadastro
        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_cadastrar.setFixedSize(320, 40)
        self.btn_cadastrar.setStyleSheet("font-size: 14px;")
        self.btn_cadastrar.clicked.connect(self.tentar_cadastrar)
        layout.addWidget(self.btn_cadastrar)

        # Botão voltar
        self.btn_voltar = QPushButton("Voltar para Login")
        self.btn_voltar.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_voltar.setFixedSize(320, 30)
        self.btn_voltar.setStyleSheet("font-size: 13px;")
        self.btn_voltar.clicked.connect(self.voltar_login)
        layout.addWidget(self.btn_voltar)

        self.label_msg = QLabel("")
        self.label_msg.setWordWrap(True)
        self.label_msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_msg)

    def voltar_login(self):
        self.close()
        if self.tela_login_callback:
            self.tela_login_callback()

    def limpa_erro_estilo(self):
        estilo = """
            QLineEdit {
                padding-left: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                border-radius: 5px;
                background-color: white;
                color: #000;
            }
            QLineEdit::placeholder {
                color: #888;
            }
        """
        for campo in [self.input_email, self.input_senha, self.input_repetir_senha, self.input_captcha]:
            campo.setStyleSheet(estilo)

    def set_erro_estilo(self, widget):
        widget.setStyleSheet("""
            QLineEdit {
                padding-left: 10px;
                font-size: 14px;
                border: 2px solid red;
                border-radius: 5px;
                background-color: white;
                color: #000;
            }
            QLineEdit::placeholder {
                color: #888;
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
        self.limpa_erro_estilo()
        email = self.input_email.text().strip()
        senha = self.input_senha.text()
        repetir = self.input_repetir_senha.text()
        captcha = self.input_captcha.text().strip()
        termos = self.checkbox_termos.isChecked()

        erros = []

        if not email:
            erros.append("O campo e-mail é obrigatório.")
            self.set_erro_estilo(self.input_email)
        elif not self.valida_email(email):
            erros.append("Formato de e-mail inválido.")
            self.set_erro_estilo(self.input_email)

        if not senha:
            erros.append("O campo senha é obrigatório.")
            self.set_erro_estilo(self.input_senha)

        if not repetir:
            erros.append("Repita a senha no campo correspondente.")
            self.set_erro_estilo(self.input_repetir_senha)
        elif senha != repetir:
            erros.append("As senhas não conferem.")
            self.set_erro_estilo(self.input_senha)
            self.set_erro_estilo(self.input_repetir_senha)

        if not termos:
            erros.append("Você deve aceitar os termos de uso.")

        if captcha != "7":
            erros.append("Resposta do captcha incorreta.")
            self.set_erro_estilo(self.input_captcha)

        if erros:
            self.label_msg.setText("<br>".join(erros))
            self.label_msg.setStyleSheet("color: red; font-size: 12px;")
        else:
            self.label_msg.setText("Cadastro realizado com sucesso!")
            self.label_msg.setStyleSheet("color: green; font-size: 13px;")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaLogin()
    janela.show()
    sys.exit(app.exec())
