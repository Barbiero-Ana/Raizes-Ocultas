import sys
import os
import sqlite3
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton, 
    QVBoxLayout, QHBoxLayout, QGraphicsOpacityEffect, QStackedWidget
)
from PyQt6.QtGui import QPixmap, QFont, QCursor, QPainter, QColor, QFontDatabase
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, 
    pyqtSignal, QRect, QPoint
)

class FontManager:    
    def __init__(self):
        self.loaded_fonts = {}
        self.debug_mode = True  
    
    def load_font(self, font_path: str, font_name: str = None) -> str:
        """
        Args:
            font_path: assets/fonts/White Storm.otf)
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
            return "Arial" 
        

        font_id = QFontDatabase.addApplicationFont(font_path)
        
        if font_id == -1:
            print(f"❌ ERRO: Não foi possível carregar a fonte {font_path}")
            return "Arial"
        

        font_families = QFontDatabase.applicationFontFamilies(font_id)
        
        if not font_families:
            print(f"❌ ERRO: Nenhuma família de fonte encontrada em {font_path}")
            return "Arial"
        
        font_family = font_families[0]
        

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
        
        if self.debug_mode:
            print(f"   🔧 Fonte criada: {font.family()}, {font.pointSize()}px")
            print(f"   ⚡ Fonte exata disponível: {font.exactMatch()}")
        
        return font
    
    

class MapButton(QPushButton):
    location_clicked = pyqtSignal(str, str)  #
    
    def __init__(self, location_name: str, level: str, x: int, y: int, parent=None):
        super().__init__(parent)
        self.location_name = location_name
        self.level = level 
        self.setFixedSize(40, 40)
        self.move(x, y)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:1 #FFA500);
                color: #8B4513;
                border: 3px solid #8B4513;
                border-radius: 20px;
                font-size: 14px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFF00, stop:1 #FFD700);
                transform: scale(1.1);
            }}
            QPushButton:pressed {{
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA500, stop:1 #FF8C00);
            }}
        """)
        
        level_number = level.split('-')[0] if '-' in level else level
        self.setText(level_number)
        
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.clicked.connect(self.on_clicked)
    
    def on_clicked(self):
        self.location_clicked.emit(self.location_name, self.level) 

class MenuScreen(QMainWindow):
    
    def __init__(self, font_manager=None, parent=None, map_screen=None, game_screen=None):
        super().__init__(parent)
        self.font_manager = font_manager
        self.map_screen = map_screen
        self.game_screen = game_screen
        self.setup_menu_ui()
    
    def setup_menu_ui(self):
        self.setWindowTitle("Menu - Raízes Ocultas")
        self.setFixedSize(400, 300)
        
        game_manager = self.parent()
        if hasattr(self.parent(), 'parent') and self.parent().parent():
            game_manager = self.parent().parent()
        
        if game_manager:
            parent_geometry = game_manager.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - 400) // 2
            y = parent_geometry.y() + (parent_geometry.height() - 300) // 2
            self.setGeometry(x, y, 400, 300)
        else:
            from PyQt6.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = (screen.width() - 400) // 2
            y = (screen.height() - 300) // 2
            self.setGeometry(x, y, 400, 300)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        main_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8B4513, stop:0.5 #A0522D, stop:1 #654321);
                border: 4px solid #FFD700;
                border-radius: 20px;
            }
        """)
        
        title_label = QLabel("☰ MENU")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if self.font_manager:
            title_font = self.font_manager.get_font("titulo", size=24, bold=True)
            title_label.setFont(title_font)
        
        title_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                background: transparent;
                border: none;
                padding: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
            }
        """)
        
        main_layout.addWidget(title_label)
        
        main_layout.addSpacing(20)
        
        self.continue_button = QPushButton("▶ Continuar")
        self.continue_button.setFixedSize(250, 50)
        self.continue_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if self.font_manager:
            button_font = self.font_manager.get_font("botoes", size=14, bold=True)
            self.continue_button.setFont(button_font)
        
        self.continue_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #32CD32, stop:1 #228B22);
                color: #FFFFFF;
                border: 3px solid #228B22;
                border-radius: 25px;
                padding: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3CB371, stop:1 #2E8B57);
                border-color: #3CB371;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #228B22, stop:1 #006400);
                transform: translateY(0px);
            }
        """)
        
        self.continue_button.clicked.connect(self.close_menu)
        main_layout.addWidget(self.continue_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addSpacing(10)
        
        self.exit_button = QPushButton("🚪 Sair")
        self.exit_button.setFixedSize(250, 50)
        self.exit_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if self.font_manager:
            button_font = self.font_manager.get_font("botoes", size=14, bold=True)
            self.exit_button.setFont(button_font)
        
        self.exit_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #780000, stop:1 #B22222);
                color: #FFFFFF;
                border: 3px solid #B22222;
                border-radius: 25px;
                padding: 10px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FF1493, stop:1 #DC143C);
                border-color: #FF1493;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #B22222, stop:1 #8B0000);
                transform: translateY(0px);
            }
        """)
        
        self.exit_button.clicked.connect(self.exit_to_game_screen)
        main_layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        main_layout.addStretch()
    
    def close_menu(self):
        self.close()
    
    def exit_to_game_screen(self):
        self.close()
        
        game_manager = None
        if hasattr(self.map_screen, 'parent') and self.map_screen.parent():
            game_manager = self.map_screen.parent()
        
        if game_manager and hasattr(game_manager, 'show_game_screen'):
            game_manager.show_game_screen()
        else:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app:
                for widget in app.allWidgets():
                    if widget.__class__.__name__ == 'GameScreen' and hasattr(widget, 'show'):
                        if game_manager:
                            game_manager.close()
                        widget.show()
                        return
            
            print("⚠️ Criando nova instância do GameScreen")
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from game_screen import GameScreen
            
            if game_manager:
                game_manager.close()
            
            game_screen = GameScreen(tela_login=None, id_usuario=None)
            game_screen.show()

class MapScreen(QMainWindow):
    location_selected_signal = pyqtSignal(str, int, int)  
    
    def __init__(self, font_manager=None, parent=None):
        super().__init__(parent)
        self.font_manager = font_manager
        self.setup_map_ui()
    def setup_background(self, main_widget):
        background_path = "assets/ScreenElements/gamescreen/Map/game-map-3.png"
        
        print(f"🔍 Verificando imagem de fundo:")
        print(f"   📁 Caminho: {background_path}")
        print(f"   ✅ Arquivo existe: {os.path.exists(background_path)}")
        
        if os.path.exists(background_path):            
            original_pixmap = QPixmap(background_path)
            self.background_label = QLabel(main_widget)
            self.background_label.setGeometry(0, 0, 1000, 700)
            self.background_label.lower()
            scaled_pixmap = original_pixmap.scaled(
                1000, 700, 
                Qt.AspectRatioMode.IgnoreAspectRatio,  
                Qt.TransformationMode.SmoothTransformation  
            )
            
            self.background_label.setPixmap(scaled_pixmap)
            
            main_widget.setStyleSheet("""
                QWidget {
                    border: 10px solid #8B4513;
                    border-radius: 15px;
                    background: transparent;
                }
            """)
            
            return True
        else:
            print(f"❌ Imagem não encontrada: {background_path}")
            main_widget.setStyleSheet("""
                QWidget {
                    background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                        stop:0 #4A7C8B, stop:0.3 #5A8C6B, stop:0.7 #6A9C5B, stop:1 #7AAC4B);
                    border: 10px solid #8B4513;
                    border-radius: 15px;
                }
            """)
            return False
            
    def setup_map_ui(self):
        self.setWindowTitle("Raízes Ocultas - Mapa")
        self.setFixedSize(1000, 700)
        
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        

        self.map_area = main_widget  
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setup_background(main_widget)
        
        self.create_map_locations()
        
        map_buttons_layout = QHBoxLayout()
        map_buttons_layout.addStretch()
        
        # btn menu
        self.back_button = QPushButton("☰ Menu")
        self.back_button.setFixedSize(120, 40)
        self.back_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if self.font_manager:
            button_font = self.font_manager.get_font("botoes", size=12, bold=True)
            self.back_button.setFont(button_font)
        
        self.back_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8B4513, stop:1 #654321);
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #A0522D, stop:1 #8B4513);
            }
        """)
        
        map_buttons_layout.addWidget(self.back_button)
        map_buttons_layout.addSpacing(20)
        
        self.skip_button = QPushButton("Começar Jogo")
        self.skip_button.setFixedSize(150, 40)
        self.skip_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        if self.font_manager:
            skip_font = self.font_manager.get_font("botoes", size=12, bold=True)
            self.skip_button.setFont(skip_font)
        
        self.skip_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #32CD32, stop:1 #228B22);
                color: #FFFFFF;
                border: 2px solid #228B22;
                border-radius: 20px;
                padding: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #3CB371, stop:1 #2E8B57);
                color: #FFFFFF;
                transform: translateY(-1px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #228B22, stop:1 #006400);
            }
        """)
        
        map_buttons_layout.addWidget(self.skip_button)
        map_buttons_layout.addStretch()
        
        main_layout.addLayout(map_buttons_layout)
        
        main_layout.addSpacing(20)
        
    def create_map_locations(self):

        locations = [
            # Lado esquerdo (aldeias indígenas)
            {"name": "Aldeia Bororo", "level": "1-5", "x": 225, "y": 240},
            {"name": "Aldeia Xavante", "level": "2-5", "x": 180, "y": 230},
            {"name": "Aldeia Karajá", "level": "2-5", "x": 160, "y": 300},
            {"name": "Aldeia Terena", "level": "3-5", "x": 180, "y": 370},
            
            # lado esquerdo inferior
            {"name": "Centro Geodésico", "level": "2-1", "x": 257, "y": 480},
            {"name": "Chapada dos Guimarães", "level": "2-2", "x": 310, "y": 515},
            {"name": "Porto de Cáceres", "level": "2-3", "x": 115, "y": 492},
            {"name": "Vila Bela", "level": "2-4", "x": 170, "y": 503},
            
            # Lado direito (castelo e vilas)
            {"name": "Castelo dos Bandeirantes", "level": "4-1", "x": 810, "y": 250},            
            # lado direito inferior
            {"name": "Pantanal Norte", "level": "3-1", "x": 725, "y": 572},
            {"name": "Pantanal Sul", "level": "3-2", "x": 788, "y": 543},
            {"name": "Pantanal Ancestral", "level": "3-3", "x": 840, "y": 500},
            {"name": "Corumbá", "level": "3-4", "x": 758, "y": 437},
        ]
        
        for location in locations:
            map_button = MapButton(
                location["name"], 
                location["level"], 
                location["x"], 
                location["y"], 
                self.map_area
            )
            map_button.location_clicked.connect(self.on_location_selected)
            
            if self.font_manager:
                button_font = self.font_manager.get_font("botoes", size=12, bold=True)
                map_button.setFont(button_font)

    def on_location_selected(self, location_name: str, level: str):
        print(f"🗺️ Local selecionado: {location_name} (Nível {level})")        
        self.show_location_info(location_name, level)
        
        if hasattr(self, 'location_selected_signal'):
            try:
                if '-' in level:
                    dificuldade, classe = map(int, level.split('-'))
                    self.location_selected_signal.emit(location_name, dificuldade, classe)
                else:
                    print(f"⚠️ Formato de nível inválido: {level}, usando padrão (1,1)")
                    self.location_selected_signal.emit(location_name, 1, 1)
            except ValueError as e:
                print(f"❌ Erro ao parsear nível {level}: {e}")
                self.location_selected_signal.emit(location_name, 1, 1)
    def show_location_info(self, location_name: str, level: str):
            if hasattr(self, 'info_popup') and self.info_popup:
                self.info_popup.hide()
                self.info_popup.deleteLater()        
            self.info_popup = QLabel(f"📍 {location_name}\n🎯 Nível: {level}\n🎮 Local disponível!", self.map_area)
            self.info_popup.setGeometry(350, 150, 300, 120)
            self.info_popup.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if self.font_manager:
                info_font = self.font_manager.get_font("narração", size=14, bold=True)
                self.info_popup.setFont(info_font)
            
            self.info_popup.setStyleSheet("""
                QLabel {
                    background: rgba(139, 69, 19, 0.95);
                    color: #FFD700;
                    padding: 15px;
                    border-radius: 15px;
                    border: 3px solid #FFD700;
                    text-align: center;
                    font-weight: bold;
                }
            """)
            
            self.info_popup.show()
            QTimer.singleShot(4000, lambda: self.info_popup.hide() if self.info_popup else None)        
            
            if self.font_manager:
                info_font = self.font_manager.get_font("narração", size=14, bold=True)
                self.info_popup.setFont(info_font)
            
            self.info_popup.setStyleSheet("""
                QLabel {
                    background: rgba(139, 69, 19, 0.95);
                    color: #FFD700;
                    padding: 15px;
                    border-radius: 15px;
                    border: 3px solid #FFD700;
                    text-align: center;
                    font-weight: bold;
                }
            """)
            
            self.info_popup.show()
            # Auto-ocultar -> 3000 = 3 segundos (presta atenção nisso ANAAAAAAAAA)
            QTimer.singleShot(4000, lambda: self.info_popup.hide() if self.info_popup else None)

            return level
    def show_menu(self):
        game_screen = None
        if hasattr(self.parent(), 'game_screen'):
            game_screen = self.parent().game_screen
        
        self.menu_screen = MenuScreen(
            font_manager=self.font_manager,
            parent=self,
            map_screen=self,
            game_screen=game_screen
        )
        
        self.menu_screen.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.menu_screen.show()


class GameManager(QMainWindow):
    def __init__(self, original_game_screen=None, tela_login=None, id_usuario=None, id_turma=None):
        super().__init__()
        self.setWindowTitle("Raízes Ocultas")
        self.setFixedSize(1000, 700)
        
        self.id_turma = id_turma
        print(f"Turma selecionada: {self.id_turma}")
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.font_manager = FontManager()
        self.load_fonts()
        
        self.original_game_screen = original_game_screen
        self.tela_login = tela_login
        self.id_usuario = id_usuario
        
        self.prologue_screen = PrologoRPG(self.show_map)
        self.map_screen = MapScreen(self.font_manager, parent=self)
        
        self.stacked_widget.addWidget(self.prologue_screen)
        self.stacked_widget.addWidget(self.map_screen)
        
        self.map_screen.back_button.clicked.connect(self.map_screen.show_menu)
        self.map_screen.skip_button.clicked.connect(self.start_game)
        
        self.show_prologue()

        self.map_screen.location_selected_signal.connect(self.iniciar_quiz)
        
    def iniciar_quiz(self, location_name, dificuldade, classe):
        print(f"🎮 Iniciando quiz: {location_name}, Dificuldade: {dificuldade}, Classe: {classe}")
        
        perguntas_respondidas = self.obter_perguntas_respondidas()
        
        try:
            import subprocess
            import sys
            import os
            
            current_dir = os.path.dirname(os.path.abspath(__file__))
            quiz_launcher_path = os.path.join(current_dir, "quiz_launcher.py")
            
            print(f"🔍 Procurando quiz_launcher.py em: {quiz_launcher_path}")
            print(f"📁 Diretório atual: {current_dir}")
            print(f"📋 Arquivos no diretório: {os.listdir(current_dir)}")
            
            if not os.path.exists(quiz_launcher_path):
                print(f"❌ Arquivo quiz_launcher.py não encontrado!")
                print(f"📁 Caminho verificado: {quiz_launcher_path}")
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.critical(self, "Erro", f"Arquivo do quiz não encontrado em:\n{quiz_launcher_path}")
                return
            
            args = [
                sys.executable, quiz_launcher_path,
                str(dificuldade), str(classe), 
                str(self.id_turma) if self.id_turma else "None",
                str(perguntas_respondidas)
            ]
            
            print(f"Executando: {' '.join(args)}")
            self.quiz_process = subprocess.Popen(args)
            
        except Exception as e:
            print(f"❌ Erro ao iniciar quiz: {e}")
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Erro", f"Não foi possível iniciar o quiz: {str(e)}")

    def ao_fechar_quiz(self, quiz_root):
        try:
            quiz_root.destroy()
            # Mostrar novamente a janela do mapa
            self.show()
            self.raise_()  # Traz para frente
            self.activateWindow()  # Ativa a janela
        except:
            pass
    
    def obter_perguntas_respondidas(self):
        pasta_db = "database"
        nome_banco = "raizes_ocultas.db"
        caminho_completo = os.path.join(pasta_db, nome_banco)
        if not self.id_turma:
            return []
            
        try:
            conn = sqlite3.connect(caminho_completo)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id_pergunta FROM Dados_do_jogador 
                WHERE id_turma = ?
            """, (self.id_turma,))
            
            perguntas_respondidas = [row[0] for row in cursor.fetchall()]
            conn.close()
            return perguntas_respondidas
            
        except Exception as e:
            print(f"Erro ao obter perguntas respondidas: {e}")
            return []
    def load_fonts(self):
        font_paths = {
            "titulo": "assets/fonts/Ghost theory 2.ttf",
            "narração": "assets/fonts/White Storm.otf",
            "botoes": "assets/fonts/firstorder.ttf",
            "dialogo": "assets/fonts/Elementary_Gothic_Bookhand.ttf",
        }
        
        for font_name, font_path in font_paths.items():
            self.font_manager.load_font(font_path, font_name)
    
    def show_prologue(self):
        self.stacked_widget.setCurrentWidget(self.prologue_screen)
        self.prologue_screen.start_prologue()
    
    def show_map(self):
        print("🗺️ Abrindo mapa...")
        self.stacked_widget.setCurrentWidget(self.map_screen)
        self.show()  
    def start_game(self):
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from game import GameScreen_Game
        self.game_screen = GameScreen_Game()
        self.game_screen.show()
        
        self.hide()
    
    def show_game_screen(self):
        self.close()
        
        if self.original_game_screen:
            self.original_game_screen.show()
        else:
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from game_screen import GameScreen
            
            game_screen = GameScreen(tela_login=self.tela_login, id_usuario=self.id_usuario)
            game_screen.show()

class BubbleWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.bubble_color = QColor(240, 240, 240, 230)
        self.border_color = QColor(100, 100, 100)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect().adjusted(10, 10, -10, -40)
        painter.setBrush(self.bubble_color)
        painter.setPen(self.border_color)
        painter.drawRoundedRect(rect, 20, 20)
        
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

class TypewriterLabel(QLabel):
    typing_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.full_text = ""
        self.current_text = ""
        self.current_index = 0
        self.typing_speed = 50  
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

class PrologoRPG(QMainWindow):
    
    def __init__(self, on_finish_callback=None):
        super().__init__()
        self.on_finish_callback = on_finish_callback
        self.current_text_index = 0
        
        
        self.font_manager = FontManager()
        
        self.load_custom_fonts()
        
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
            "titulo": "assets/fonts/Ghost theory 2.ttf",   #tittle
            "narração": "assets/fonts/White Storm.otf",     #narracao
            "botoes": "assets/fonts/firstorder.ttf",       #buttons
            "dialogo": "assets/fonts/Elementary_Gothic_Bookhand.ttf",  #dialogs
        }
        
        for font_name, font_path in font_paths.items():
            self.font_manager.load_font(font_path, font_name)
        
        print(f"Fontes carregadas: {list(self.font_manager.loaded_fonts.keys())}")
        
        
    def setup_ui(self):
        self.setWindowTitle("Raízes Ocultas - Prólogo")
        self.setFixedSize(1000, 700)
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # === FUNDO ===
        self.background_label = QLabel()
        self.background_label.setGeometry(0, 0, 1000, 700)
        
        self.background_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:0.3 #16213e, stop:0.7 #0f3460, stop:1 #533a7d);
            }
        """)
        
        # === TÍTULO DO JOGO ===
        title_layout = QHBoxLayout()
        title_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.title_label = QLabel("Raizes Ocultas")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
        
        character_container = QWidget()
        character_container.setFixedSize(200, 250)
        character_container.setStyleSheet("""
            QWidget {
                background-color: rgba(255, 255, 255, 20);
                border-radius: 15px;
                border: 2px solid rgba(255, 255, 255, 100);
            }
        """)
        
        self.character_image = QLabel()
        self.character_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_image.setFixedSize(180, 200)
        
        character_path = "assets/ScreenElements/gamescreen/NPCs/capivara-guia.png"
        if os.path.exists(character_path):
            pixmap = QPixmap(character_path).scaled(
                180, 200, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.character_image.setPixmap(pixmap)

        else:
            self.character_image.setText("🧙‍♂️")
            placeholder_font = self.font_manager.get_font("dialogo", size=60)
            self.character_image.setFont(placeholder_font)
            self.character_image.setStyleSheet("""
                color: #f0f0f0;
                background: transparent;
            """)
        
        char_layout = QVBoxLayout(character_container)
        char_layout.addWidget(self.character_image)
        
        character_layout.addWidget(character_container)
        main_layout.addLayout(character_layout)
        
        # === ESPACAMENTO ===
        main_layout.addSpacing(30)
        
        # === BUBBLE DE TEXTO ===
        bubble_container = QWidget()
        bubble_container.setFixedHeight(200)
        
        self.bubble = BubbleWidget()
        bubble_layout = QVBoxLayout(self.bubble)
        bubble_layout.setContentsMargins(30, 25, 30, 50)
        self.text_label = TypewriterLabel()
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)

        narration_font = self.font_manager.get_font("narração", size=22, bold=False)
        self.text_label.setFont(narration_font)
        print(f"📝 Fonte da narração aplicada: {narration_font.family()}")
        
        self.text_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                background: transparent;
                line-height: 1.4;
            }
        """)
        
        self.text_label.typing_finished.connect(self.on_typing_finished)
        
        bubble_layout.addWidget(self.text_label)
        
        bubble_outer_layout = QHBoxLayout(bubble_container)
        bubble_outer_layout.addWidget(self.bubble)
        
        main_layout.addWidget(bubble_container)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.skip_button = QPushButton("⏭️ Pular")
        self.skip_button.setFixedSize(150, 45)
        self.skip_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        skip_font = self.font_manager.get_font("botoes", size=14, bold=True)
        self.skip_button.setFont(skip_font)
        
        self.skip_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #696969, stop:1 #2F2F2F);
                color: #E0E0E0;
                border: none;
                border-radius: 22px;
                padding: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #808080, stop:1 #404040);
                color: #FFFFFF;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #505050, stop:1 #1F1F1F);
            }
        """)
        
        self.skip_button.clicked.connect(self.skip_prologue)
        
        button_layout.addWidget(self.skip_button)
        button_layout.addSpacing(20)
        
        self.continue_button = QPushButton("Continuar ▶")
        self.continue_button.setFixedSize(150, 45)
        self.continue_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        button_font = self.font_manager.get_font("botoes", size=14, bold=True)
        self.continue_button.setFont(button_font)
        print(f"Fonte do botão aplicada: {button_font.family()}")
        
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
        self.continue_button.hide()  
        
        button_layout.addWidget(self.continue_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
    def setup_animations(self):
        self.background_fade = QGraphicsOpacityEffect()
        self.background_label.setGraphicsEffect(self.background_fade)
        
        self.fade_animation = QPropertyAnimation(self.background_fade, b"opacity")
        self.fade_animation.setDuration(2000)
        self.fade_animation.setStartValue(0.0)
        self.fade_animation.setEndValue(1.0)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
        self.button_fade = QGraphicsOpacityEffect()
        self.continue_button.setGraphicsEffect(self.button_fade)
        
        self.button_animation = QPropertyAnimation(self.button_fade, b"opacity")
        self.button_animation.setDuration(800)
        self.button_animation.setStartValue(0.0)
        self.button_animation.setEndValue(1.0)
        
    def start_prologue(self):
        print("▶️ Iniciando prólogo...")
        self.fade_animation.start()
        
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
            QTimer.singleShot(500, self.show_first_text)
        else:
            self.show_start_button()
    
    def show_start_button(self):
        self.bubble.hide()
        
        self.start_button = QPushButton("🎮 Começar Aventura")
        self.start_button.setFixedSize(250, 60)
        self.start_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        
        start_font = self.font_manager.get_font("botoes", size=18, bold=True)
        self.start_button.setFont(start_font)
        
        self.start_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFD700, stop:1 #FFA500);
                color: #8B4513;
                border: 4px solid #8B4513;
                border-radius: 30px;
                padding: 15px;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
            }
            QPushButton:hover {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFF00, stop:1 #FFD700);
                transform: translateY(-3px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFA500, stop:1 #FF8C00);
                transform: translateY(0px);
            }
        """)
        
        self.start_button.clicked.connect(self.start_game)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.start_button)
        button_layout.addStretch()
        
        main_layout = self.centralWidget().layout()
        main_layout.addLayout(button_layout)
        
        self.start_button_fade = QGraphicsOpacityEffect()
        self.start_button.setGraphicsEffect(self.start_button_fade)
        
        self.start_button_animation = QPropertyAnimation(self.start_button_fade, b"opacity")
        self.start_button_animation.setDuration(1000)
        self.start_button_animation.setStartValue(0.0)
        self.start_button_animation.setEndValue(1.0)
        self.start_button_animation.start()
    
    def skip_prologue(self):        
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        
        if hasattr(self, 'fade_animation') and self.fade_animation.state() == QPropertyAnimation.State.Running:
            self.fade_animation.stop()
        
        if hasattr(self, 'button_animation') and self.button_animation.state() == QPropertyAnimation.State.Running:
            self.button_animation.stop()
        
        if self.on_finish_callback:
            self.on_finish_callback()
        else:
            self.close()
    
    def start_game(self):
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from game import GameScreen_Game
            
            self.game_screen = GameScreen_Game()
            self.game_screen.show()
            
            self.close()
            
        except ImportError as e:
            print(f"Erro ao importar game.py: {e}")
            if self.on_finish_callback:
                self.on_finish_callback()
    
    def finish_prologue(self):
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
            self.skip_prologue() 
        elif event.key() == Qt.Key.Key_S:
            self.skip_prologue()  


def show_prologue(parent=None, on_finish=None):
    prologue = PrologoRPG(on_finish)
    prologue.show()
    prologue.start_prologue()
    return prologue


def start_game_with_prologue(original_game_screen=None, tela_login=None, id_usuario=None):
    game_manager = GameManager(
        original_game_screen=original_game_screen,
        tela_login=tela_login,
        id_usuario=id_usuario
    )
    game_manager.show()
    return game_manager

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    game = GameManager()
    game.show()
    
    sys.exit(app.exec())