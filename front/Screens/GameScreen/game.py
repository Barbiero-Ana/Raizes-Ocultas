import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QFontDatabase, QKeySequence
from PyQt6.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve, QPoint

class GameScreen(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        # Variáveis de movimento
        self.movement_speed = 5
        self.keys_pressed = set()
        
        # Variáveis para sprites
        self.current_state = "idle"  # "idle" ou "moving"
        
        # Variáveis para o fade do fundo
        self.background_image = None
        self.background_fade_effect = None
        self.background_animation = None
        
        # Variáveis para o sistema de trilha
        self.narration_finished = False
        self.trail_mode = False
        self.background_x_offset = 0
        self.trail_distance = 0
        self.npc_met = False
        
        # NPC
        self.npc = None
        self.dialog_box = None
        self.in_dialog = False
        
        # Inicializar interface
        self.setup_game_ui()
        self.setup_character()
        self.setup_movement()
        self.setup_narration_timer()
        self.setup_background_fade_timer()
        
        # Dados da narração
        self.narration_texts = [
            "Bem-vindo à sua jornada, jovem explorador...",
            "Você se encontra nas terras místicas de Mato Grosso.",
            "Aqui, as raízes da cultura se entrelaçam com os segredos da natureza.",
            "Use as setas do teclado para movimentar seu personagem.",
            "Sua missão é descobrir e preservar o conhecimento ancestral.",
            "Explore cada canto desta terra sagrada com cuidado e respeito."
        ]
        self.current_narration_index = 0
        
    def setup_game_ui(self):
        """Configura a interface principal do jogo"""
        self.setWindowTitle("Raízes Ocultas - Jogo")
        self.setFixedSize(1000, 700)
        
        # Widget principal
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Fundo preto
        main_widget.setStyleSheet("""
            QWidget {
                background-color: #000000;
            }
        """)
        
        # Layout principal sem margens para ocupar toda a tela
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Área do jogo (onde o personagem se move)
        self.game_area = QFrame()
        self.game_area.setFixedSize(1000, 550)  # Deixa espaço para a narração
        self.game_area.setStyleSheet("background-color: #000000;")
        
        # Garantir que a área do jogo seja visível
        self.game_area.show()
        
        # Preparar imagem de fundo (inicialmente invisível)
        self.setup_background_image()
        
        main_layout.addWidget(self.game_area)
        
        # Área da narração na parte inferior
        self.setup_narration_area(main_layout)
        
    def setup_character(self):
        """Configura o personagem (boneco) no centro da tela"""
        self.character = QLabel(self.game_area)
        self.character.setFixedSize(60, 80)
        
        # Definir estilo base para o personagem
        self.character.setStyleSheet("""
            QLabel {
                background-color: transparent;
                border: none;
            }
        """)
        
        self.load_character_sprites()
        
        self.update_character_sprite()
        
        center_x = (self.game_area.width() - self.character.width()) // 2
        center_y = (self.game_area.height() - self.character.height()) // 2
        self.character.move(center_x, center_y)
        
        # Garantir que o personagem seja visível
        self.character.show()
        self.character.raise_()  
        self.character.setVisible(True)     
        if hasattr(self, 'background_image') and self.background_image:
            self.character.raise_()
        
    def load_character_sprites(self):
        """Carrega os sprites do personagem para diferentes estados"""
        # Inicializar dicionário de sprites
        self.character_sprites = {}
        
        # Definir caminhos das imagens (apenas 2 imagens)
        sprite_paths = {
            "idle": "../../../assets/ScreenElements/personagens/player-static.png",
            "moving": "../../../assets/ScreenElements/personagens/player-walking.png"
        }
        
        # Carregar cada sprite
        for state, path in sprite_paths.items():
            if os.path.exists(path):
                pixmap = QPixmap(path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        60, 80, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.character_sprites[state] = scaled_pixmap
        
        # Se não conseguiu carregar nenhum sprite, usar placeholder
        if not self.character_sprites:
            self.setup_placeholder_sprites()
    
    def setup_placeholder_sprites(self):
        placeholders = {
            "idle": "🧑‍🌾",
            "moving": "🚶‍♂️"
        }
        
        for state, emoji in placeholders.items():
            # Criar um QPixmap com o emoji/texto
            self.character_sprites[state] = emoji
            
    def update_character_sprite(self):
        sprite_key = self.current_state  # "idle" ou "moving"
        
        # Aplicar o sprite
        if sprite_key in self.character_sprites:
            sprite = self.character_sprites[sprite_key]
            
            if isinstance(sprite, QPixmap):
                # É uma imagem
                self.character.setPixmap(sprite)
                self.character.setText("")  # Limpar texto
                # Manter estilo básico
                self.character.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        border: none;
                    }
                """)
                self.character.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                # É um placeholder de texto/emoji
                self.character.setText(sprite)
                self.character.setPixmap(QPixmap())  # Limpar imagem
                self.set_character_placeholder_style()
        else:
            # Fallback para sprite idle
            self.set_character_placeholder()
        
    def set_character_placeholder(self):
        self.character.setText("🧑‍🌾")
        self.set_character_placeholder_style()
        
    def set_character_placeholder_style(self):
        self.character.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character.setStyleSheet("""
            QLabel {
                font-size: 40px;
                color: #FFD700;
                background-color: rgba(255, 215, 0, 0.2);
                border: 2px solid #FFD700;
                border-radius: 30px;
            }
        """)
        
    def setup_movement(self):
        # Timer para movimento contínuo
        self.movement_timer = QTimer()
        self.movement_timer.timeout.connect(self.update_movement)
        self.movement_timer.start(16)  # ~60 FPS
        
        # Foco na janela para capturar teclas
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def setup_narration_area(self, main_layout):
        # Container da narração
        narration_container = QFrame()
        narration_container.setFixedHeight(150)
        narration_container.setStyleSheet("""
            QFrame {
                background-color: #1a1a1a;
                border-top: 3px solid #FFD700;
            }
        """)
        
        # Layout da narração
        narration_layout = QVBoxLayout(narration_container)
        narration_layout.setContentsMargins(20, 15, 20, 15)
        narration_layout.setSpacing(10)
        
        # Label da narração
        self.narration_label = QLabel()
        self.narration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.narration_label.setWordWrap(True)
        
        # Configurar fonte da narração
        narration_font = QFont("Arial", 16)
        narration_font.setBold(True)
        self.narration_label.setFont(narration_font)
        
        self.narration_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                background-color: transparent;
                padding: 10px;
                line-height: 1.4;
            }
        """)
        
        # Inicialmente vazio
        self.narration_label.setText("")
        
        narration_layout.addWidget(self.narration_label)
        main_layout.addWidget(narration_container)
        
    def setup_narration_timer(self):
        """Configura o timer para iniciar a narração após 10 segundos"""
        self.narration_timer = QTimer()
        self.narration_timer.setSingleShot(True)
        self.narration_timer.timeout.connect(self.start_narration)
        self.narration_timer.start(10000)  # 10 segundos
        
    def setup_background_image(self):
        """Configura a imagem de fundo que aparecerá com fade"""
        # Criar QLabel para a imagem de fundo
        self.background_image = QLabel(self.game_area)
        self.background_image.setFixedSize(1000, 550)
        self.background_image.setScaledContents(True)
        
        # Tentar carregar imagem de fundo
        background_path = "../../../assets/ScreenElements/gamescreen/background-game.png"
        if os.path.exists(background_path):
            pixmap = QPixmap(background_path)
            if not pixmap.isNull():
                self.background_image.setPixmap(pixmap)
        else:
            # Fallback - criar um gradiente simples
            self.background_image.setStyleSheet("""
                QLabel {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 #1a3d2e, stop:0.3 #2d5a44, stop:0.7 #3f7159, stop:1 #4a8b6b);
                }
            """)
        
        # Configurar efeito de opacidade (inicialmente transparente)
        self.background_fade_effect = QGraphicsOpacityEffect()
        self.background_fade_effect.setOpacity(0.0)  # Totalmente transparente
        self.background_image.setGraphicsEffect(self.background_fade_effect)
        
        # Posicionar atrás de outros elementos
        self.background_image.lower()
        self.background_image.show()
        
    def setup_background_fade_timer(self):
        """Configura o timer para iniciar o fade do fundo após 20 segundos"""
        self.background_fade_timer = QTimer()
        self.background_fade_timer.setSingleShot(True)
        self.background_fade_timer.timeout.connect(self.start_background_fade)
        self.background_fade_timer.start(20000)  # 20 segundos
        
    def start_background_fade(self):
        """Inicia a animação de fade-in do fundo"""
        if self.background_fade_effect and self.background_image:
            # Criar animação de fade-in
            self.background_animation = QPropertyAnimation(self.background_fade_effect, b"opacity")
            self.background_animation.setDuration(3000)  # 3 segundos de transição
            self.background_animation.setStartValue(0.0)  # Totalmente transparente
            self.background_animation.setEndValue(0.7)    # 70% de opacidade
            self.background_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            
            # Iniciar animação
            self.background_animation.start()
            print("🎨 Iniciando fade-in do fundo...")
        
    def start_narration(self):
        """Inicia a narração do jogo"""
        if self.current_narration_index < len(self.narration_texts):
            self.show_narration_text(self.narration_texts[self.current_narration_index])
            self.current_narration_index += 1
            
            # Timer para próximo texto (5 segundos)
            QTimer.singleShot(5000, self.start_narration)
        else:
            # Fim da narração
            self.narration_label.setText("Caminhe até o canto inferior direito para seguir a trilha...")
            self.narration_finished = True
            print("📖 Narração finalizada - Trilha ativada!")
            
    def show_narration_text(self, text):
        """Mostra um texto de narração"""
        self.narration_label.setText(text)
        
        # Efeito de fade in
        self.narration_animation = QPropertyAnimation(self.narration_label, b"geometry")
        self.narration_animation.setDuration(500)
        self.narration_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
    def keyPressEvent(self, event):
        """Captura teclas pressionadas para movimentação e diálogo"""
        key = event.key()
        
        if self.in_dialog:
            # Durante diálogo, apenas ESPAÇO e ESC funcionam
            if key == Qt.Key.Key_Space:
                self.next_dialog()
            elif key == Qt.Key.Key_Escape:
                self.end_dialog()
        else:
            # Movimento normal
            if key in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right,
                       Qt.Key.Key_W, Qt.Key.Key_S, Qt.Key.Key_A, Qt.Key.Key_D]:
                self.keys_pressed.add(key)
            elif key == Qt.Key.Key_Escape:
                self.return_to_map()
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        """Captura teclas soltas"""
        key = event.key()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        super().keyReleaseEvent(event)
        
    def update_movement(self):
        """Atualiza a posição do personagem baseado nas teclas pressionadas"""
        previous_state = self.current_state
        
        if not self.keys_pressed or self.in_dialog:
            # Nenhuma tecla pressionada ou em diálogo - personagem parado
            self.current_state = "idle"
        else:
            # Teclas pressionadas - personagem se movendo
            self.current_state = "moving"
            
            current_pos = self.character.pos()
            new_x = current_pos.x()
            new_y = current_pos.y()
            
            # Movimento nas 4 direções
            if Qt.Key.Key_Up in self.keys_pressed or Qt.Key.Key_W in self.keys_pressed:
                new_y -= self.movement_speed
            if Qt.Key.Key_Down in self.keys_pressed or Qt.Key.Key_S in self.keys_pressed:
                new_y += self.movement_speed
            if Qt.Key.Key_Left in self.keys_pressed or Qt.Key.Key_A in self.keys_pressed:
                new_x -= self.movement_speed
            if Qt.Key.Key_Right in self.keys_pressed or Qt.Key.Key_D in self.keys_pressed:
                new_x += self.movement_speed
                
            # Verificar limites da área do jogo
            max_x = self.game_area.width() - self.character.width()
            max_y = self.game_area.height() - self.character.height()
            
            new_x = max(0, min(new_x, max_x))
            new_y = max(0, min(new_y, max_y))
            
            # Verificar se chegou na área trigger (canto inferior direito)
            if self.narration_finished and not self.trail_mode:
                trigger_x = max_x - 50  # 50 pixels do canto direito
                trigger_y = max_y - 50  # 50 pixels do canto inferior
                
                if new_x >= trigger_x and new_y >= trigger_y:
                    self.start_trail_mode()
            
            # Se em modo trilha, aplicar movimento de fundo
            if self.trail_mode and not self.npc_met:
                self.update_trail_movement(new_x, new_y)
            else:
                # Aplicar nova posição normalmente
                self.character.move(new_x, new_y)
        
        # Atualizar sprite se o estado mudou
        if self.current_state != previous_state:
            self.update_character_sprite()
            
    def start_trail_mode(self):
        """Inicia o modo trilha com movimento de fundo"""
        self.trail_mode = True
        self.narration_label.setText("Seguindo a trilha... Continue caminhando para a direita...")
        print("🛤️ Modo trilha ativado!")
        
        # Criar NPC no final da trilha
        self.setup_npc()
        
    def update_trail_movement(self, target_x, target_y):
        """Atualiza movimento durante o modo trilha"""
        # Movimentar personagem normalmente
        self.character.move(target_x, target_y)
        
        # Se movendo para a direita, criar efeito parallax
        if (Qt.Key.Key_Right in self.keys_pressed or Qt.Key.Key_D in self.keys_pressed) and self.background_image:
            self.background_x_offset -= 2  # Velocidade do parallax
            self.trail_distance += 2
            
            # Atualizar posição do fundo para criar efeito de movimento
            current_style = self.background_image.styleSheet()
            if "qlineargradient" not in current_style:  # Se tem imagem real
                # Para imagem real, pode usar transform ou reposicionamento
                pass
            else:
                # Para gradiente, alterar as cores ou posição
                pass
                
        # Verificar se chegou ao NPC (após certa distância)
        if self.trail_distance > 300 and self.npc and not self.npc_met:
            # Verificar colisão com NPC
            char_pos = self.character.pos()
            npc_pos = self.npc.pos()
            
            distance = ((char_pos.x() - npc_pos.x())**2 + (char_pos.y() - npc_pos.y())**2)**0.5
            if distance < 50:  # 50 pixels de distância
                self.meet_npc()
                
    def setup_npc(self):
        """Cria o NPC no final da trilha"""
        self.npc = QLabel(self.game_area)
        self.npc.setFixedSize(60, 80)
        
        # Tentar carregar imagem do NPC
        npc_image_path = "../../../assets/ScreenElements/gamescreen/NPCs/capivara-guia.png"
        if os.path.exists(npc_image_path):
            pixmap = QPixmap(npc_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    60, 80, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.npc.setPixmap(scaled_pixmap)
            else:
                self.setup_npc_placeholder()
        else:
            self.setup_npc_placeholder()
        
        # Posicionar NPC fora da tela inicialmente (será revelado durante a trilha)
        self.npc.move(self.game_area.width() + 100, 300)
        self.npc.show()
        
        # Animar NPC para entrar na tela após um tempo
        QTimer.singleShot(2000, self.animate_npc_entrance)
        
    def setup_npc_placeholder(self):
        """Define placeholder visual para o NPC"""
        self.npc.setText("🦫")
        self.npc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.npc.setStyleSheet("""
            QLabel {
                font-size: 40px;
                color: #8B4513;
                background-color: rgba(139, 69, 19, 0.2);
                border: 2px solid #8B4513;
                border-radius: 30px;
            }
        """)
        
    def animate_npc_entrance(self):
        """Anima a entrada do NPC na tela"""
        if self.npc:
            # Posição final do NPC (centro-direita da tela)
            final_x = self.game_area.width() - 150
            final_y = 300
            
            # Criar animação de movimento
            self.npc_animation = QPropertyAnimation(self.npc, b"pos")
            self.npc_animation.setDuration(2000)  # 2 segundos
            self.npc_animation.setStartValue(self.npc.pos())
            self.npc_animation.setEndValue(QPoint(final_x, final_y))
            self.npc_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
            
            self.npc_animation.start()
            print("🦫 NPC aparecendo na trilha!")
        
    def meet_npc(self):
        """Inicia o encontro com o NPC"""
        self.npc_met = True
        self.in_dialog = True
        
        # Parar movimento de fundo
        self.trail_mode = False
        
        # Mostrar diálogo
        self.start_dialog()
        
        print("🤝 Encontrou o NPC!")
        
    def start_dialog(self):
        """Inicia o sistema de diálogo"""
        dialog_texts = [
            "Olá, jovem explorador! Bem-vindo às terras de Mato Grosso.",
            "Sou o Guardião das Raízes Ocultas.",
            "Você chegou até aqui seguindo a trilha ancestral.",
            "Sua jornada de descoberta está apenas começando...",
            "Pressione ESPAÇO para continuar ou ESC para finalizar."
        ]
        
        self.current_dialog_index = 0
        self.dialog_texts = dialog_texts
        
        # Criar caixa de diálogo
        self.create_dialog_box()
        self.show_dialog_text()
        
    def create_dialog_box(self):
        """Cria a caixa de diálogo"""
        self.dialog_box = QLabel(self.game_area)
        self.dialog_box.setFixedSize(800, 120)
        self.dialog_box.setWordWrap(True)
        
        # Posicionar na parte inferior
        dialog_x = (self.game_area.width() - self.dialog_box.width()) // 2
        dialog_y = self.game_area.height() - 150
        self.dialog_box.move(dialog_x, dialog_y)
        
        # Estilo da caixa de diálogo
        self.dialog_box.setStyleSheet("""
            QLabel {
                background-color: rgba(139, 69, 19, 0.95);
                color: #FFD700;
                padding: 15px;
                border-radius: 15px;
                border: 3px solid #FFD700;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        
        self.dialog_box.show()
        
    def show_dialog_text(self):
        """Mostra o texto atual do diálogo"""
        if self.current_dialog_index < len(self.dialog_texts):
            text = self.dialog_texts[self.current_dialog_index]
            self.dialog_box.setText(text)
        else:
            self.end_dialog()
            
    def next_dialog(self):
        """Avança para o próximo texto do diálogo"""
        self.current_dialog_index += 1
        self.show_dialog_text()
        
    def end_dialog(self):
        """Finaliza o diálogo"""
        if self.dialog_box:
            self.dialog_box.hide()
            self.dialog_box = None
            
        self.in_dialog = False
        self.narration_label.setText("Diálogo finalizado. Use ESC para voltar ao mapa.")
        print("💬 Diálogo finalizado!")
        
    def return_to_map(self):
        """Retorna para o mapa (GameManager)"""
        if self.parent_window and hasattr(self.parent_window, 'show_map'):
            self.close()
            self.parent_window.show_map()
        else:
            self.close()
            
    def closeEvent(self, event):
        """Limpa recursos ao fechar"""
        if hasattr(self, 'movement_timer'):
            self.movement_timer.stop()
        if hasattr(self, 'narration_timer'):
            self.narration_timer.stop()
        if hasattr(self, 'background_fade_timer'):
            self.background_fade_timer.stop()
        if hasattr(self, 'background_animation') and self.background_animation:
            self.background_animation.stop()
        if hasattr(self, 'npc_animation') and self.npc_animation:
            self.npc_animation.stop()
        super().closeEvent(event)

def main():
    """Função main para testar a tela de jogo independentemente"""
    app = QApplication(sys.argv)
    game_screen = GameScreen()
    game_screen.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()