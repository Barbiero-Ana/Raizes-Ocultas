import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QPainter, QColor, QFontDatabase
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    pyqtSignal, QRect
)

class FontManager:    
    def __init__(self):
        self.loaded_fonts = {}
        self.debug_mode = True  # Ativar para ver mensagens de debug
    
    def load_font(self, font_path: str, font_name: str = None) -> str:
        """
        Args:
            font_path: assets/fonts/Ghost theory 2.ttf)
            font_name: FonteJogo
        
        Returns:
            Nome da família da fonte carregada
        """
        if self.debug_mode:
            print(f"🔍 Tentando carregar fonte: {font_path}")
        
        if not os.path.exists(font_path):
            print(f"❌ ERRO: Fonte não encontrada em {font_path}")
            print(f"📁 Diretório atual: {os.getcwd()}")
            print(f"📁 Caminho absoluto tentado: {os.path.abspath(font_path)}")
            return "Arial"  # Fonte padrão fallback
        
        # Carregar a fonte no banco de dados de fontes
        font_id = QFontDatabase.addApplicationFont(font_path)
        
        if font_id == -1:
            print(f"❌ ERRO: Não foi possível carregar a fonte {font_path}")
            return "Arial"
        
        # Obter o nome da família da fonte
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        
        if not font_families:
            print(f"❌ ERRO: Nenhuma família de fonte encontrada em {font_path}")
            return "Arial"
        
        font_family = font_families[0]
        
        # Armazenar a fonte carregada
        key = font_name if font_name else os.path.basename(font_path)
        self.loaded_fonts[key] = font_family
        
        if self.debug_mode:
            print(f"✅ Fonte carregada com sucesso!")
            print(f"   📝 Família da fonte: {font_family}")
            print(f"   🔑 Chave armazenada: {key}")
            print(f"   📋 Todas as famílias disponíveis: {font_families}")
        
        return font_family
    
    def get_font(self, font_key: str, size: int = 12, bold: bool = False, italic: bool = False) -> QFont:
        """
        Args:
            font_key: FontJogo
            size: Tamanho da fonte
            bold: Se a fonte deve ser negrito
            italic: Se a fonte deve ser itálica
        
        Returns:
            Objeto QFont configurado
        """
        if self.debug_mode:
            print(f"🎨 Criando fonte: {font_key}, tamanho {size}")
        
        if font_key in self.loaded_fonts:
            font_family = self.loaded_fonts[font_key]
            if self.debug_mode:
                print(f"   ✅ Fonte encontrada: {font_family}")
        else:
            print(f"   ❌ Fonte {font_key} não encontrada, usando Arial")
            print(f"   📋 Fontes disponíveis: {list(self.loaded_fonts.keys())}")
            font_family = "Arial"
        
        font = QFont(font_family, size)
        font.setBold(bold)
        font.setItalic(italic)
        
        # Verificar se a fonte foi aplicada corretamente
        if self.debug_mode:
            print(f"   🔧 Fonte criada: {font.family()}, {font.pointSize()}px")
            print(f"   ⚡ Fonte exata disponível: {font.exactMatch()}")
            
            # Verificação adicional: testar se a fonte está realmente disponível
            available_families = QFontDatabase.families()
            font_available_in_system = font_family in available_families
            print(f"   🖥️ Fonte disponível no sistema: {font_available_in_system}")
            
            if not font_available_in_system and font_family != "Arial":
                print(f"   🔄 Forçando carregamento da fonte novamente...")
                # Tentar carregar novamente se não estiver disponível
                test_font = QFont()
                test_font.setFamily(font_family)
                print(f"   🧪 Teste de família: {test_font.family()}")
        
        return font
    
    def list_system_fonts(self):
        """Lista todas as fontes disponíveis no sistema"""
        if self.debug_mode:
            families = QFontDatabase.families()
            print(f"📚 Fontes do sistema ({len(families)} disponíveis):")
            for i, family in enumerate(families[:10]):  # Mostrar apenas as 10 primeiras
                print(f"   {i+1}. {family}")
            if len(families) > 10:
                print(f"   ... e mais {len(families) - 10} fontes")

class TypewriterLabel(QLabel):
    typing_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_text = ""
        self.current_text = ""
        self.current_index = 0
        self.typing_speed = 50  # ms entre cada caractere
        self.timer = QTimer()
        self.timer.timeout.connect(self.add_next_character)
        
    def start_typing(self, text: str, speed: int = 50):
        self.full_text = text
        self.current_text = ""
        self.current_index = 0
        self.typing_speed = speed
        self.setText("")
        self.timer.start(self.typing_speed)
    
    def add_next_character(self):
        if self.current_index < len(self.full_text):
            self.current_text += self.full_text[self.current_index]
            self.setText(self.current_text)
            self.current_index += 1
        else:
            self.timer.stop()
            self.typing_finished.emit()
    
    def skip_typing(self):
        if self.timer.isActive():
            self.timer.stop()
            self.current_text = self.full_text
            self.setText(self.current_text)
            self.typing_finished.emit()

class BubbleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bubble_color = QColor(240, 240, 240, 230)
        self.border_color = QColor(100, 100, 100)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Desenhar o bubble principal
        rect = self.rect().adjusted(10, 10, -10, -40)
        painter.setBrush(self.bubble_color)
        painter.setPen(self.border_color)
        painter.drawRoundedRect(rect, 20, 20)
        
        # Desenhar a "cauda" do bubble apontando para cima
        tail_points = [
            rect.center().x() - 15, rect.top(),
            rect.center().x() + 15, rect.top(),
            rect.center().x(), rect.top() - 20
        ]
        
        painter.drawPolygon([
            rect.center() + QRect(-15, -rect.height()//2, 0, 0).topLeft(),
            rect.center() + QRect(15, -rect.height()//2, 0, 0).topLeft(),
            rect.center() + QRect(0, -rect.height()//2 - 20, 0, 0).topLeft()
        ])

class PrologoRPG(QMainWindow):
    
    def __init__(self, on_finish_callback=None):
        super().__init__()
        self.on_finish_callback = on_finish_callback
        self.current_text_index = 0
        
        print("🚀 Iniciando Prólogo RPG...")
        
        # Inicializar gerenciador de fontes
        self.font_manager = FontManager()
        
        # Debug: mostrar algumas fontes do sistema
        self.font_manager.list_system_fonts()
        
        # Carregar fontes personalizadas
        self.load_custom_fonts()
        
        # Textos do prólogo
        self.prologo_texts = [
            "Há muito tempo, nas terras místicas de Mato Grosso...",
            "Onde as raízes da cultura se entrelaçam com os segredos da natureza...",
            "Um jovem professor descobriu que o conhecimento ancestral estava desaparecendo...",
            "As tradições dos povos originários, quilombolas e pantaneiros corriam perigo...",
            "Apenas através da educação e da aventura seria possível preservar essa sabedoria...",
            "Sua jornada começa agora... Você está pronto para desvendar as Raízes Ocultas?"
        ]
        
        self.setup_ui()
        self.setup_animations()
    
    def load_custom_fonts(self):
        print("\n📂 Carregando fontes personalizadas...")
        
        # Verificar se o diretório de fontes existe
        fonts_dir = "assets/fonts"
        if not os.path.exists(fonts_dir):
            print(f"❌ Diretório de fontes não existe: {fonts_dir}")
            print(f"📁 Criando diretório...")
            try:
                os.makedirs(fonts_dir, exist_ok=True)
                print(f"✅ Diretório criado: {fonts_dir}")
            except:
                print(f"❌ Não foi possível criar o diretório")
        
        # Lista de arquivos no diretório de fontes
        if os.path.exists(fonts_dir):
            print(f"📋 Arquivos em {fonts_dir}:")
            for file in os.listdir(fonts_dir):
                print(f"   📄 {file}")
        
        # Defina aqui os caminhos para suas fontes
        font_paths = {
            "titulo": "assets/fonts/Gameplay.ttf",          # Para título do jogo
            "narração": "assets/fonts/evanescent.ttf",      # Para texto de narração
            "botoes": "assets/fonts/firstorder.ttf",        # Para texto dos botões
            "dialogo": "assets/fonts/AnalogWhispers.ttf",   # Para diálogos de personagens
        }
        
        # Carregar cada fonte (se existir)
        for font_name, font_path in font_paths.items():
            self.font_manager.load_font(font_path, font_name)
        
        print(f"🎯 Fontes carregadas: {list(self.font_manager.loaded_fonts.keys())}")
        
        # Teste adicional: tentar carregar manualmente se não funcionou
        if not self.font_manager.loaded_fonts:
            print("🔄 Tentando carregamento manual...")
            manual_font_path = "assets/fonts/Elementary_Gothic_Bookhand.ttf"
            if os.path.exists(manual_font_path):
                print(f"📁 Arquivo existe: {manual_font_path}")
                # Teste direto com QFontDatabase
                font_id = QFontDatabase.addApplicationFont(manual_font_path)
                print(f"🆔 Font ID retornado: {font_id}")
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"👨‍👩‍👧‍👦 Famílias encontradas: {families}")
                    if families:
                        self.font_manager.loaded_fonts["manual"] = families[0]
                        print(f"✅ Fonte carregada manualmente: {families[0]}")
            else:
                print(f"❌ Arquivo não existe: {manual_font_path}")
                
        # Lista final de fontes carregadas
        print(f"📚 RESUMO - Fontes finais carregadas:")
        for key, family in self.font_manager.loaded_fonts.items():
            print(f"   🔑 {key} -> {family}")
        
    def setup_ui(self):
        self.setWindowTitle("Raízes Ocultas - Prólogo")
        self.setFixedSize(1000, 700)
        
        print("🎨 Configurando interface...")
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === FUNDO ===
        self.background_label = QLabel()
        self.background_label.setGeometry(0, 0, 1000, 700)
        
        # Criar fundo gradiente
        self.background_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.3 #16213e, stop:0.7 #0f3460, stop:1 #533a7d);
            }
        """)
        
        # === TÍTULO DO JOGO ===
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel("Raízes Ocultas")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Aplicar fonte personalizada ao título
        title_font = self.font_manager.get_font("titulo", size=32, bold=True)
        self.title_label.setFont(title_font)
        print(f"🏷️ Fonte do título aplicada: {title_font.family()}")
        
        self.title_label.setStyleSheet("""
            QLabel {
                color: #f0f0f0;
                margin: 20px;
                padding: 10px;
                background: rgba(0, 0, 0, 0.3);
                border-radius: 10px;
                border: 2px solid rgba(255, 255, 255, 0.2);
            }
        """)
        
        title_layout.addWidget(self.title_label)
        main_layout.addLayout(title_layout)
        
        # === PERSONAGEM NARRADOR ===
        character_layout = QVBoxLayout()
        character_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        character_layout.setSpacing(20)
        
        # Container do personagem
        character_container = QWidget()
        character_container.setFixedSize(200, 250)
        character_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 15px;
                border: 2px solid rgba(255, 255, 255, 100);
            }
        """)
        
        # Imagem do personagem (ou placeholder)
        self.character_image = QLabel()
        self.character_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_image.setFixedSize(180, 200)
        
        # Tentar carregar imagem do personagem
        character_path = "assets/ScreenElements/gamescreen/NPCs/capivara-guia.png"
        if os.path.exists(character_path):
            pixmap = QPixmap(character_path).scaled(
                180, 200, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.character_image.setPixmap(pixmap)
        else:
            # Placeholder se não encontrar a imagem
            self.character_image.setText("🧙‍♂️")
            placeholder_font = self.font_manager.get_font("dialogo", size=60)
            self.character_image.setFont(placeholder_font)
            self.character_image.setStyleSheet("""
                color: #f0f0f0;
                background: transparent;
            """)
        
        # Layout do personagem
        char_layout = QVBoxLayout(character_container)
        char_layout.addWidget(self.character_image)
        
        character_layout.addWidget(character_container)
        main_layout.addLayout(character_layout)
        
        # === ESPAÇAMENTO ===
        main_layout.addSpacing(30)
        
        # === BUBBLE DE TEXTO ===
        bubble_container = QWidget()
        bubble_container.setFixedHeight(200)
        
        # Bubble customizado
        self.bubble = BubbleWidget()
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(30, 25, 30, 50)
        
        # Label de texto com efeito de digitação
        self.text_label = TypewriterLabel()
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        
        # Aplicar fonte personalizada ao texto de narração
        narration_font = self.font_manager.get_font("narração", size=18, bold=False)  # Removendo bold para testar
        self.text_label.setFont(narration_font)
        print(f"📝 Fonte da narração aplicada: {narration_font.family()}")
        
        # Remover font-weight do CSS para não conflitar
        self.text_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background: transparent;
                line-height: 1.4;
            }
        """)
        
        # Conectar sinal de fim da digitação
        self.text_label.typing_finished.connect(self.on_typing_finished)
        
        bubble_layout.addWidget(self.text_label)
        
        # Layout do bubble
        bubble_outer_layout = QHBoxLayout(bubble_container)
        bubble_outer_layout.addWidget(self.bubble)
        
        main_layout.addWidget(bubble_container)
        
        # === BOTÃO CONTINUAR ===
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.continue_button = QPushButton("Continuar ▶")
        self.continue_button.setFixedSize(150, 45)
        self.continue_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        # Aplicar fonte personalizada ao botão
        button_font = self.font_manager.get_font("botoes", size=14, bold=True)
        self.continue_button.setFont(button_font)
        print(f"🔘 Fonte do botão aplicada: {button_font.family()}")
        
        # Remover font-weight do CSS para não conflitar com a fonte
        self.continue_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #2c5bb8);
                color: white;
                border: none;
                border-radius: 22px;
                padding: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #3c6bc8);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3a80d2, stop:1 #1c4ba8);
            }
        """)
        
        self.continue_button.clicked.connect(self.next_text)
        self.continue_button.hide()  # Inicialmente escondido
        
        button_layout.addWidget(self.continue_button)
        button_layout.addSpacing(50)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
    def setup_animations(self):
        # Animação de fade in do fundo
        self.background_fade = QGraphicsOpacityEffect()
        self.background_label.setGraphicsEffect(self.background_fade)
        
        self.fade_animation = QPropertyAnimation(self.background_fade, b"opacity")
        self.fade_animation.setDuration(2000)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        # Animação de aparição do botão
        self.button_fade = QGraphicsOpacityEffect()
        self.continue_button.setGraphicsEffect(self.button_fade)
        
        self.button_animation = QPropertyAnimation(self.button_fade, b"opacity")
        self.button_animation.setDuration(800)
        self.button_animation.setStartValue(0.0)
        self.button_animation.setEndValue(1.0)
        
    def start_prologue(self):
        print("▶️ Iniciando prólogo...")
        # Iniciar animação do fundo
        self.fade_animation.start()
        
        # Aguardar um pouco e iniciar o primeiro texto
        QTimer.singleShot(1000, self.show_first_text)
    
    def show_first_text(self):
        if self.current_text_index < len(self.prologo_texts):
            text = self.prologo_texts[self.current_text_index]
            self.text_label.start_typing(text, 50)  # 50ms entre caracteres
    
    def on_typing_finished(self):
        self.continue_button.show()
        self.button_animation.start()
    
    def next_text(self):
        self.continue_button.hide()
        self.current_text_index += 1
        
        if self.current_text_index < len(self.prologo_texts):
            # Próximo texto
            QTimer.singleShot(500, self.show_first_text)
        else:
            # Fim do prólogo
            self.finish_prologue()
    
    def finish_prologue(self):
        print("🏁 Prólogo finalizado!")
        if self.on_finish_callback:
            self.on_finish_callback()
        else:
            self.close()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.text_label.skip_typing()
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space or event.key() == Qt.Key.Key_Return:
            if self.continue_button.isVisible():
                self.next_text()
            else:
                self.text_label.skip_typing()
        elif event.key() == Qt.Key.Key_Escape:
            self.finish_prologue()

# Função para usar em outros módulos
def show_prologue(parent=None, on_finish=None):
    prologue = PrologoRPG(on_finish)
    prologue.show()
    prologue.start_prologue()
    return prologue

# Teste independente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    def on_prologue_finish():
        print("Prólogo finalizado!")
        app.quit()
    
    prologue = PrologoRPG(on_prologue_finish)
    prologue.show()
    prologue.start_prologue()
    
    sys.exit(app.exec())