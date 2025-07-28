import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QLineEdit, QWidget, QVBoxLayout
)
from PyQt6.QtGui import QPixmap, QCursor, QIcon
from PyQt6.QtCore import Qt, QPoint


class HoverLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTextFormat(Qt.TextFormat.RichText)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self.setOpenExternalLinks(False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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

# --------------------------------------------------------------------------------

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

        # Logo centralizada no topo
        self.logo = QLabel()
        self.logo.setPixmap(
            QPixmap("assets/ScreenElements/MT-bandeira-logo.png")
            .scaledToWidth(250, Qt.TransformationMode.SmoothTransformation)
        )
        self.logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.logo)
        layout.addSpacing(40)

        # Campo de e-mail
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("E-mail")
        self.input_email.setFixedHeight(40)
        self.input_email.setMaximumWidth(500)
        self.input_email.setFixedWidth(300)
        self.input_email.setStyleSheet("""
            QLineEdit {
                padding-left: 10px;
                padding-top: 8px;
                padding-bottom: 8px;
                font-size: 14px;
                color: #000000;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        pixmap_icone_email = QPixmap("assets/ScreenElements/icons/mail_vector.png").scaled(
            34, 44,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        icone_email = QIcon(pixmap_icone_email)
        self.input_email.addAction(icone_email, QLineEdit.ActionPosition.LeadingPosition)
        layout.addWidget(self.input_email, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Campo de senha
        self.input_senha = QLineEdit()
        self.input_senha.setPlaceholderText("Senha")
        self.input_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_senha.setFixedHeight(40)
        self.input_senha.setMaximumWidth(600)
        self.input_senha.setFixedWidth(300)
        self.input_senha.setStyleSheet("""
            QLineEdit {
                padding-left: 10px;
                padding-top: 8px;
                padding-bottom: 8px;
                font-size: 14px;
                color: #000000;
            }
            QLineEdit::placeholder {
                color: #888888;
            }
        """)
        pixmap_icone = QPixmap("assets/ScreenElements/icons/password_vector.png").scaled(
            24, 24,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        icone_senha = QIcon(pixmap_icone)
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

        # label interativa de registro
        self.label_registro = HoverLabel()
        self.label_registro.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.label_registro.linkActivated.connect(self.abrir_tela_cadastro)
        layout.addWidget(self.label_registro)

        self.dec_imagens()

    def dec_imagens(self):
        # Superior esquerdo
        self.canto_esq_sup = QLabel(self)
        self.canto_esq_sup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.canto_esq_sup.setStyleSheet("background: transparent;") # VAI SER TRANSPARENTE SIM!
        pixmap = QPixmap("assets/ScreenElements/Viola-com-chita.png").scaled(
            900, 2000,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.canto_esq_sup.setPixmap(pixmap)
        self.canto_esq_sup.resize(pixmap.size())  
        self.canto_esq_sup.move(-400, -400)  
        self.canto_esq_sup.show()
        
        # Superior direito
        self.canto_dir_sup = QLabel(self)
        self.canto_dir_sup.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.canto_dir_sup.setStyleSheet("background: transparent;")
        pixmap = QPixmap("assets/ScreenElements/organic-chita-2.png").scaled(
            600, 350,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.canto_dir_sup.setPixmap(pixmap)
        self.canto_dir_sup.resize(pixmap.size())  
        self.canto_dir_sup.move(-120, -70)  
        self.canto_dir_sup.show()

        # Inferior esquerdo
        self.canto_esq_inf = QLabel(self)
        self.canto_esq_inf.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.canto_esq_inf.setStyleSheet("background: transparent;")
        pixmap = QPixmap("assets/ScreenElements/organic-chita.png").scaled(
            400, 550,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.canto_esq_inf.setPixmap(pixmap)
        self.canto_esq_inf.resize(pixmap.size())  
        self.canto_esq_inf.move(780, 550)  
        self.canto_esq_inf.show()

        # Inferior direito
        self.canto_dir_inf = QLabel(self)
        self.canto_dir_inf.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.canto_dir_inf.setStyleSheet("background: transparent;")
        pixmap = QPixmap("assets/ScreenElements/dance-chita.png").scaled(
            900, 2000,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.canto_dir_inf.setPixmap(pixmap)
        self.canto_dir_inf.resize(pixmap.size())  
        self.canto_dir_inf.move(700, -250)  
        self.canto_dir_inf.show()



    def abrir_tela_cadastro(self):
        print("Você clicou em 'Crie aqui'. Aqui você pode abrir outra tela!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = TelaLogin()
    janela.show()
    sys.exit(app.exec())
