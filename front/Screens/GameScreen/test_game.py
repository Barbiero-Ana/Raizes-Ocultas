
import sys
from PyQt6.QtWidgets import QApplication
from game import GameScreen

def test_game():
    app = QApplication(sys.argv)
    

    game_screen = GameScreen()
    game_screen.show()
    
    print("Use as setas ou WASD para mover o personagem")
    print("Pressione ESC para sair")
    print(f"Sprites carregados: {list(game_screen.character_sprites.keys())}")
    
    # Executar aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    test_game()