import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QFrame, QGraphicsOpacityEffect
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QFontDatabase, QKeySequence
from PyQt6.QtCore import Qt, QTimer, QRect, QPropertyAnimation, QEasingCurve, QPoint

class GameScreen_Game(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        
        self.movement_speed = 5
        self.keys_pressed = set()
        
        self.current_state = "idle"  
        
        self.background_image = None
        self.background_fade_effect = None
        self.background_animation = None
        
        self.narration_finished = False
        self.trail_mode = False
        self.background_x_offset = 0
        self.trail_distance = 0
        self.npc_met = False
        
        self.trigger_zones = []
        self.removed_triggers = set()  # Para rastrear triggers removidos
        self.is_transitioning = False
        self.fade_widget = None
        self.fade_animation = None
        self.current_scene = "main"
        self.scenes = {}
        
        self.proximity_distance = 60  
        self.auto_dialog_triggered = False
        
        self.show_trigger_debug = False
        self.trigger_debug_widgets = []
        
        self.npc = None
        self.dialog_box = None
        self.in_dialog = False
        
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
            "Procure por áreas especiais que te levarão a novos lugares..."
        ]
        self.current_narration_index = 0
        
        self.load_trigger_config()
        self.setup_trigger_zones()  
        self.setup_scenes()
        
    def setup_game_ui(self):
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
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.game_area = QFrame()
        self.game_area.setFixedSize(1000, 550)  # Deixa espaço para a narração
        self.game_area.setStyleSheet("background-color: #000000;")
        
        self.game_area.show()        
        self.setup_background_image()
        
        main_layout.addWidget(self.game_area)        
        self.setup_narration_area(main_layout)
        
    def setup_character(self):
        self.character = QLabel(self.game_area)
        self.character.setFixedSize(60, 80)
        
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
        
        self.character.show()
        self.character.raise_()  
        self.character.setVisible(True)     
        if hasattr(self, 'background_image') and self.background_image:
            self.character.raise_()
            
        self.setup_fade_widget()
        
        self.setup_trigger_debug_visual()
        
    def load_character_sprites(self):
        # Inicializar dicionário de sprites
        self.character_sprites = {}
        
        # Definir caminhos das imagens (apenas 2 imagens)
        sprite_paths = {
            "idle": "assets/ScreenElements/personagens/player-static.png",
            "moving": "assets/ScreenElements/personagens/player-walking.png"
        }
        
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
        
        if not self.character_sprites:
            self.setup_placeholder_sprites()
    
    def setup_placeholder_sprites(self):
        placeholders = {
            "idle": "🧑‍🌾",
            "moving": "🚶‍♂️"
        }
        
        for state, emoji in placeholders.items():
            self.character_sprites[state] = emoji
            
    def update_character_sprite(self):
        sprite_key = self.current_state  
        
        if sprite_key in self.character_sprites:
            sprite = self.character_sprites[sprite_key]
            
            if isinstance(sprite, QPixmap):
                self.character.setPixmap(sprite)
                self.character.setText("") 
                self.character.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        border: none;
                    }
                """)
                self.character.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                self.character.setText(sprite)
                self.character.setPixmap(QPixmap()) 
                self.set_character_placeholder_style()
        else:
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
        self.movement_timer = QTimer()
        self.movement_timer.timeout.connect(self.update_movement)
        self.movement_timer.start(16)  # ~60 FPS
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
        
        narration_layout = QVBoxLayout(narration_container)
        narration_layout.setContentsMargins(20, 15, 20, 15)
        narration_layout.setSpacing(10)
        
        self.narration_label = QLabel()
        self.narration_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.narration_label.setWordWrap(True)
        
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
        
        self.narration_label.setText("")
        
        narration_layout.addWidget(self.narration_label)
        main_layout.addWidget(narration_container)
        
    def setup_narration_timer(self):
        self.narration_timer = QTimer()
        self.narration_timer.setSingleShot(True)
        self.narration_timer.timeout.connect(self.start_narration)
        self.narration_timer.start(5000)  
        
    def setup_background_image(self):
        self.background_image = QLabel(self.game_area)
        self.background_image.setFixedSize(1000, 550)
        self.background_image.setScaledContents(True)
        
        background_path = "assets/ScreenElements/gamescreen/game-test.png"
        if os.path.exists(background_path):
            pixmap = QPixmap(background_path)
            if not pixmap.isNull():
                self.background_image.setPixmap(pixmap)
        else:
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
        if self.current_narration_index < len(self.narration_texts):
            self.show_narration_text(self.narration_texts[self.current_narration_index])
            self.current_narration_index += 1
            
            QTimer.singleShot(5000, self.start_narration)
        else:
            self.narration_label.setText("Caminhe até o canto inferior direito para seguir a trilha...")
            self.narration_finished = True
            print("📖 Narração finalizada - Trilha ativada!")
            
    def show_narration_text(self, text):
        self.narration_label.setText(text)
        
        # Efeito de fade in
        self.narration_animation = QPropertyAnimation(self.narration_label, b"geometry")
        self.narration_animation.setDuration(500)
        self.narration_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
    def keyPressEvent(self, event):
        key = event.key()
        
        if self.in_dialog:
            # Durante diálogo, apenas ESPAÇO e ESC funcionam
            if key == Qt.Key.Key_Space:
                self.next_dialog()
            elif key == Qt.Key.Key_Escape:
                self.end_dialog()
        else:
            # Controles especiais para debug e personalização
            if key == Qt.Key.Key_T:  # T para Toggle trigger debug
                self.toggle_trigger_debug()
            elif key == Qt.Key.Key_F:  # F para ajuda
                self.show_trigger_customization_help()
            elif key == Qt.Key.Key_S and event.modifiers() == Qt.KeyboardModifier.ControlModifier:  # Ctrl+S para salvar
                self.save_trigger_config()
            # Movimento normal
            elif key in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right,
                       Qt.Key.Key_W, Qt.Key.Key_S, Qt.Key.Key_A, Qt.Key.Key_D]:
                self.keys_pressed.add(key)
            elif key == Qt.Key.Key_Escape:
                self.return_to_map()
        super().keyPressEvent(event)
        
    def keyReleaseEvent(self, event):
        key = event.key()
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        super().keyReleaseEvent(event)
        
    def update_movement(self):
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
            
            # Verificar trigger zones para transições
            if not self.is_transitioning:
                self.check_trigger_zones(new_x, new_y)
            
            # Verificar proximidade com NPCs
            if not self.in_dialog and not self.auto_dialog_triggered:
                self.check_npc_proximity(new_x, new_y)
            
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
        self.npc.setFixedSize(120, 160)  # Aumentado de 60x80 para 120x160
        
        # Tentar carregar imagem do NPC
        npc_image_path = "assets/ScreenElements/gamescreen/NPCs/espirito-serra.png"
        if os.path.exists(npc_image_path):
            pixmap = QPixmap(npc_image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    120, 160,  # Aumentado para corresponder ao novo tamanho
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.npc.setPixmap(scaled_pixmap)
            else:
                self.setup_npc_placeholder()
        else:
            self.setup_npc_placeholder()
        
        # Posicionar NPC fora da tela inicialmente (será revelado durante a trilha)
        self.npc.move(self.game_area.width() + 100, 200)  # Mudado de 300 para 200
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
            final_x = self.game_area.width() - 200  # Mais espaço devido ao tamanho maior
            final_y = 250  # Posição mais central
            
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
        
        self.trail_mode = False
        

    def start_dialog(self):
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
        if self.current_dialog_index < len(self.dialog_texts):
            text = self.dialog_texts[self.current_dialog_index]
            self.dialog_box.setText(text)
        else:
            self.end_dialog()
            
    def next_dialog(self):
        self.current_dialog_index += 1
        self.show_dialog_text()
        
    def end_dialog(self):
        if self.dialog_box:
            self.dialog_box.hide()
            self.dialog_box = None
            
        self.in_dialog = False
        self.narration_label.setText("Diálogo finalizado. Use ESC para voltar ao mapa.")
        print("💬 Diálogo finalizado!")
        
    def return_to_map(self):
        if self.parent_window and hasattr(self.parent_window, 'show_map'):
            self.close()
            self.parent_window.show_map()
        else:
            self.close()
            
    def setup_trigger_zones(self):
        # PERSONALIZÁVEL: Modifique as coordenadas e tamanhos dos trigger points aqui
        self.trigger_zones = [
            {
                'name': 'forest_entrance',
                # FLORESTA MÍSTICA - Posição personalizável
                'x': 700, 'y': 250, 'width': 80, 'height': 80,  
                'spawn_x': 800, 'spawn_y': 400,  
                'description': 'Portal para a Floresta Mística',
                'color': '#1a3d1a',  # Verde escuro para debug visual
                'target_scene': 'forest'
            },
            {
                'name': 'forest_secret_area',
                'x': 250, 'y': 250, 'width': 60, 'height': 60,
                'spawn_x': 200, 'spawn_y': 200,
                'description': 'Área Secreta da Floresta',
                'color': '#2d5a2d',  # Verde médio para debug visual
                'target_scene': 'secret_cave',
                'appears_in_scene': 'forest',  
                'disappears_after_use': True  
            }
        ]
        
        self.show_trigger_debug = False 
        
    def setup_scenes(self):
        self.scenes = {
            'main': {
                'background': "assets/ScreenElements/gamescreen/game-test.png",
                'npcs': [],
                'description': 'Cena principal'
            },
            'forest': {
                'background': "assets/ScreenElements/gamescreen/cerrado-background.png",
                'npcs': [{'x': 400, 'y': 300, 'type': 'sage'}],
                'description': 'Floresta mística'
            },
            'village': {
                'background': "assets/ScreenElements/gamescreen/village-scene.png",
                'npcs': [{'x': 500, 'y': 300, 'type': 'elder'}],
                'description': 'Vila tradicional'
            },
            'river': {
                'background': "assets/ScreenElements/gamescreen/river-scene.png",
                'npcs': [{'x': 200, 'y': 250, 'type': 'fisherman'}],
                'description': 'Margens do rio'
            },
            'secret_cave': {
                'background': "assets/ScreenElements/gamescreen/background/mt-forest.png",
                'npcs': [{'x': 400, 'y': 300, 'type': 'ribeirinha'}],
                'description': 'Caverna Secreta - Sem saídas visíveis'
            }
        }
        
    def setup_fade_widget(self):
        self.fade_widget = QLabel(self.game_area)
        self.fade_widget.setFixedSize(1000, 550)
        self.fade_widget.setStyleSheet("background-color: black;")
        
        self.fade_effect = QGraphicsOpacityEffect()
        self.fade_effect.setOpacity(0.0)  # Inicialmente transparente
        self.fade_widget.setGraphicsEffect(self.fade_effect)
        
        self.fade_widget.raise_()
        self.fade_widget.show()
        
    def check_trigger_zones(self, player_x, player_y):
        char_center_x = player_x + self.character.width() // 2
        char_center_y = player_y + self.character.height() // 2
        
        for zone in self.trigger_zones:
            # Pular triggers que já foram removidos
            if zone['name'] in self.removed_triggers:
                continue
                
            # Pular triggers que não devem aparecer na cena atual
            if zone.get('appears_in_scene') and zone['appears_in_scene'] != self.current_scene:
                continue
                
            if (zone['x'] <= char_center_x <= zone['x'] + zone['width'] and
                zone['y'] <= char_center_y <= zone['y'] + zone['height']):
                
                # Ativar transição
                self.start_scene_transition(zone)
                
                # Se o trigger deve desaparecer após o uso, marcá-lo como removido
                if zone.get('disappears_after_use', False):
                    self.removed_triggers.add(zone['name'])
                    self.hide_trigger_debug_widget(zone['name'])
                    self.narration_label.setText(f"{zone['description']} foi descoberta e desapareceu!")
                    
                break
                
    def start_scene_transition(self, zone):
        if self.is_transitioning:
            return
            
        self.is_transitioning = True
        target_scene = zone['target_scene']
        
        # Fade out
        self.fade_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_animation.setDuration(800)  # 0.8 segundos
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        # Quando o fade out terminar, trocar cena e fazer fade in
        self.fade_animation.finished.connect(lambda: self.change_scene(target_scene, zone['spawn_x'], zone['spawn_y']))
        self.fade_animation.start()
        
        # Mostrar mensagem de transição
        self.narration_label.setText(f"Entrando em: {zone['description']}...")
        
    def change_scene(self, scene_name, spawn_x, spawn_y):
        self.current_scene = scene_name
        scene_data = self.scenes.get(scene_name, self.scenes['main'])
        
        # Atualizar fundo
        self.update_scene_background(scene_data['background'])
        
        # Reposicionar personagem
        self.character.move(spawn_x, spawn_y)
        
        # Limpar NPCs antigos
        if hasattr(self, 'npc') and self.npc:
            self.npc.hide()
            self.npc = None
            
        # Criar novos NPCs da cena
        self.setup_scene_npcs(scene_data.get('npcs', []))
        
        # Atualizar trigger debug visual para a nova cena
        if self.show_trigger_debug:
            # Limpar widgets existentes
            for widget in getattr(self, 'trigger_debug_widgets', []):
                widget.hide()
                widget.deleteLater()
            self.trigger_debug_widgets = []
            # Recriar para a nova cena
            self.setup_trigger_debug_visual()
        
        # Fade in
        self.fade_in_animation = QPropertyAnimation(self.fade_effect, b"opacity")
        self.fade_in_animation.setDuration(800)
        self.fade_in_animation.setStartValue(1.0)
        self.fade_in_animation.setEndValue(0.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_in_animation.finished.connect(self.transition_complete)
        self.fade_in_animation.start()
        
        # Atualizar narração
        self.narration_label.setText(f"Você chegou em: {scene_data['description']}")
        
    def update_scene_background(self, background_path):
        if os.path.exists(background_path):
            pixmap = QPixmap(background_path)
            if not pixmap.isNull():
                self.background_image.setPixmap(pixmap)
                return
                
        # Fallback para gradientes baseados na cena
        scene_colors = {
            'forest': "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1a3d1a, stop:1 #2d5a2d);",
            'village': "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #8B4513, stop:1 #D2691E);",
            'river': "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #1e3a5f, stop:1 #2e5a8f);",
            'secret_cave': "background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #2b1810, stop:1 #4a2c1a);"
        }
        
        color_style = scene_colors.get(self.current_scene, scene_colors.get('main', ""))
        if color_style:
            self.background_image.setStyleSheet(f"QLabel {{ {color_style} }}")
            
    def setup_scene_npcs(self, npcs_data):
        for npc_data in npcs_data:
            self.create_scene_npc(npc_data['x'], npc_data['y'], npc_data['type'])
            
    def create_scene_npc(self, x, y, npc_type):
        npc = QLabel(self.game_area)
        npc.setFixedSize(120, 160)  # Aumentado para consistência
        
        # Caminhos das imagens dos NPCs
        npc_images = {
            'sage': 'assets/ScreenElements/gamescreen/NPCs/espirito-serra.png',
            'elder': '👴',
            'fisherman': '🎣',
            'capivara': '🦫',
            'ribeirinha': 'assets/ScreenElements/gamescreen/NPCs/parteira-ribeirinha.png'
        }
        
        npc_source = npc_images.get(npc_type, '🦫')
        
        # Verificar se é um caminho de imagem ou emoji
        if npc_source.endswith('.png') and os.path.exists(npc_source):
            # Carregar imagem
            pixmap = QPixmap(npc_source)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    120, 160,  # Aumentado para consistência
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                npc.setPixmap(scaled_pixmap)
                npc.setStyleSheet("""
                    QLabel {
                        background-color: transparent;
                        border: none;
                    }
                """)
                npc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            else:
                # Fallback para emoji se imagem não carregar
                self.setup_npc_emoji_fallback(npc, '🧙')
        else:
            # É um emoji - usar estilo de placeholder
            self.setup_npc_emoji_fallback(npc, npc_source)
        
        npc.move(x, y)
        npc.show()
        
        # Guardar referência do NPC
        if not hasattr(self, 'scene_npcs'):
            self.scene_npcs = []
        self.scene_npcs.append(npc)
        
        # Se é o primeiro NPC, definir como principal
        if not self.npc:
            self.npc = npc
    
    def setup_npc_emoji_fallback(self, npc, emoji):
        """Define estilo de emoji para NPCs quando imagem não está disponível"""
        npc.setText(emoji)
        npc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        npc.setStyleSheet("""
            QLabel {
                font-size: 40px;
                color: #8B4513;
                background-color: rgba(139, 69, 19, 0.3);
                border: 2px solid #8B4513;
                border-radius: 30px;
            }
        """)
            
    def check_npc_proximity(self, player_x, player_y):

        if not self.npc or self.in_dialog:
            return
            
        char_center_x = player_x + self.character.width() // 2
        char_center_y = player_y + self.character.height() // 2
        
        npc_center_x = self.npc.x() + self.npc.width() // 2
        npc_center_y = self.npc.y() + self.npc.height() // 2
        
        distance = ((char_center_x - npc_center_x)**2 + (char_center_y - npc_center_y)**2)**0.5
        
        if distance <= self.proximity_distance and not self.auto_dialog_triggered:
            self.auto_dialog_triggered = True
            self.start_automatic_dialog()
            
    def start_automatic_dialog(self):

        self.in_dialog = True
        
        # Diálogos baseados na cena atual
        scene_dialogs = {
            'main': [
                "Olá! Bem-vindo às terras de Mato Grosso.",
                "Sou um guardião das tradições locais.",
                "Explore as áreas ao redor para descobrir mais sobre nossa cultura!"
            ],
            'forest': [
                "A floresta guarda segredos ancestrais...",
                "Cada árvore tem uma história para contar.",
                "Respeite a natureza e ela te recompensará."
            ],
            'village': [
                "Esta é nossa vila tradicional.",
                "Aqui preservamos os costumes de nossos antepassados.",
                "Cada casa tem sua própria história familiar."
            ],
            'river': [
                "O rio é fonte de vida para nossa comunidade.",
                "As águas carregam as bênçãos dos espíritos.",
                "Pescar aqui é um ritual sagrado."
            ]
        }
        
        self.dialog_texts = scene_dialogs.get(self.current_scene, scene_dialogs['main'])
        self.current_dialog_index = 0
        
        self.create_dialog_box()
        self.show_dialog_text()
        
        self.narration_label.setText("NPC detectado! Diálogo iniciado automaticamente.")
        
    def setup_trigger_debug_visual(self):
        self.trigger_debug_widgets = []
        
        if self.show_trigger_debug:
            for zone in self.trigger_zones:
                # Pular triggers que foram removidos
                if zone['name'] in self.removed_triggers:
                    continue
                    
                # Pular triggers que não devem aparecer na cena atual
                if zone.get('appears_in_scene') and zone['appears_in_scene'] != self.current_scene:
                    continue
                    
                debug_widget = QLabel(self.game_area)
                debug_widget.setFixedSize(zone['width'], zone['height'])
                debug_widget.move(zone['x'], zone['y'])
                debug_widget.setObjectName(f"debug_{zone['name']}")  # Nome para identificação
                
                # Estilo visual para debug
                debug_widget.setStyleSheet(f"""
                    QLabel {{
                        background-color: {zone['color']};
                        opacity: 0.5;
                        border: 2px dashed white;
                        border-radius: 5px;
                    }}
                """)
                
                debug_widget.setText(zone['name'])
                debug_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
                debug_widget.setWordWrap(True)
                debug_widget.setStyleSheet(debug_widget.styleSheet() + """
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                """)
                
                debug_widget.show()
                self.trigger_debug_widgets.append(debug_widget)
    
    def hide_trigger_debug_widget(self, zone_name):
        """Remove o widget de debug visual para um trigger específico"""
        for widget in self.trigger_debug_widgets[:]:  # Usar slice para evitar problemas de modificação durante iteração
            if widget.objectName() == f"debug_{zone_name}":
                widget.hide()
                widget.deleteLater()
                self.trigger_debug_widgets.remove(widget)
                break
    
    def toggle_trigger_debug(self):
        self.show_trigger_debug = not self.show_trigger_debug
        
        # Limpar widgets existentes
        for widget in getattr(self, 'trigger_debug_widgets', []):
            widget.hide()
            widget.deleteLater()
        self.trigger_debug_widgets = []
        
        # Recriar se ativado
        self.setup_trigger_debug_visual()
        
        status = "ativada" if self.show_trigger_debug else "desativada"
        self.narration_label.setText(f"Visualização de trigger points {status}")
    
    def move_trigger_zone(self, zone_name, new_x, new_y, new_width=None, new_height=None):
        for zone in self.trigger_zones:
            if zone['name'] == zone_name:
                zone['x'] = new_x
                zone['y'] = new_y
                if new_width is not None:
                    zone['width'] = new_width
                if new_height is not None:
                    zone['height'] = new_height
                break
        
        if self.show_trigger_debug:
            self.setup_trigger_debug_visual()
            
        self.narration_label.setText(f"Trigger '{zone_name}' movido para ({new_x}, {new_y})")
    
    def show_trigger_customization_help(self):
        help_text = """
🎮 PERSONALIZAÇÃO DOS TRIGGER POINTS:

CONTROLES:
• Tecla T: Mostrar/ocultar visualização debug
• Tecla F: Esta mensagem de ajuda  
• Ctrl+S: Salvar configurações no JSON

COMO PERSONALIZAR:
1. Edite o arquivo trigger_config.json
2. Ou modifique diretamente no código (setup_trigger_zones)
3. Use os presets predefinidos

FLORESTA - já configurada para: (300, 150) - próximo à árvore especial
VILA - topo da tela: (450, 0)  
RIO - lateral direita: (950, 300)

Configure as posições ideais e pressione Ctrl+S para salvar!
        """.strip()
        
        self.narration_label.setText(help_text)
        
        # Timer para voltar ao texto normal
        QTimer.singleShot(8000, lambda: self.narration_label.setText("Pressione T para ver/ocultar trigger zones"))
    
    def set_forest_trigger_preset(self, preset_name):
        presets = {
            'center': {'x': 400, 'y': 250, 'width': 80, 'height': 80},
            'corner': {'x': 50, 'y': 50, 'width': 80, 'height': 80},
            'tree': {'x': 300, 'y': 150, 'width': 80, 'height': 80},
            'top_center': {'x': 450, 'y': 80, 'width': 80, 'height': 80},
            'left_side': {'x': 0, 'y': 200, 'width': 50, 'height': 100},  # Original
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.move_trigger_zone('forest_entrance', 
                                preset['x'], preset['y'], 
                                preset['width'], preset['height'])
            self.narration_label.setText(f"Floresta movida para preset: {preset_name}")
    
    def load_trigger_config(self):
        config_path = "trigger_config.json"
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                # Carregar configurações dos trigger zones
                trigger_config = config.get('trigger_zones', {})
                self.trigger_zones = []
                
                for zone_name, zone_data in trigger_config.items():
                    pos = zone_data['position']
                    spawn = zone_data['spawn_position']
                    
                    self.trigger_zones.append({
                        'name': zone_name,
                        'x': pos['x'],
                        'y': pos['y'], 
                        'width': pos['width'],
                        'height': pos['height'],
                        'target_scene': zone_data['target_scene'],
                        'spawn_x': spawn['x'],
                        'spawn_y': spawn['y'],
                        'description': zone_data['description'],
                        'color': zone_data['color']
                    })
                
                # Carregar configurações debug
                debug_config = config.get('debug_settings', {})
                self.show_trigger_debug = debug_config.get('show_triggers', False)
                self.proximity_distance = debug_config.get('proximity_distance', 60)
                
                print("✅ Configurações carregadas do trigger_config.json")
                return True
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar trigger_config.json: {e}")
            
        return False
    
    def save_trigger_config(self):
        config = {
            "trigger_zones": {},
            "debug_settings": {
                "show_triggers": self.show_trigger_debug,
                "proximity_distance": self.proximity_distance
            }
        }
        
        # Converter trigger zones para formato JSON
        for zone in self.trigger_zones:
            config["trigger_zones"][zone['name']] = {
                "position": {
                    "x": zone['x'],
                    "y": zone['y'],
                    "width": zone['width'],
                    "height": zone['height']
                },
                "target_scene": zone['target_scene'],
                "spawn_position": {
                    "x": zone['spawn_x'],
                    "y": zone['spawn_y']
                },
                "description": zone['description'],
                "color": zone['color']
            }
        
        try:
            with open("trigger_config.json", 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.narration_label.setText("✅ Configurações salvas em trigger_config.json")
            return True
            
        except Exception as e:
            self.narration_label.setText(f"❌ Erro ao salvar: {e}")
            return False

    def transition_complete(self):
        self.is_transitioning = False
        self.auto_dialog_triggered = False  # Reset para nova cena

    def closeEvent(self, event):
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
        if hasattr(self, 'fade_animation') and self.fade_animation:
            self.fade_animation.stop()
        if hasattr(self, 'fade_in_animation') and self.fade_in_animation:
            self.fade_in_animation.stop()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    game_screen = GameScreen_Game()
    game_screen.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()