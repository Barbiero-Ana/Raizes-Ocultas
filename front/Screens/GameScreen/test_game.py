#!/usr/bin/env python3

import sys
from PyQt6.QtWidgets import QApplication
from game import GameScreen

def test_game():
    """Teste simples para verificar se as imagens aparecem"""
    app = QApplication(sys.argv)
    
    # Criar a tela de jogo
    game_screen = GameScreen()
    game_screen.show()
    
    print("🎮 Jogo iniciado!")
    print("Use as setas ou WASD para mover o personagem")
    print("Pressione ESC para sair")
    print(f"Sprites carregados: {list(game_screen.character_sprites.keys())}")
    
    # Executar aplicação
    sys.exit(app.exec())

if __name__ == "__main__":
    test_game()