#!/usr/bin/env python3
"""
EXEMPLO: Como personalizar trigger points do jogo Raízes Ocultas

Este arquivo mostra diferentes formas de personalizar as posições dos trigger points.
Execute este script para testar diferentes configurações.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from front.Screens.GameScreen.game import GameScreen
from PyQt6.QtWidgets import QApplication

def customize_triggers(game_screen):
    """Exemplos de como personalizar os trigger points"""
    
    # EXEMPLO 1: Mover floresta para o centro da tela
    print("🌲 Movendo trigger da floresta para o centro...")
    game_screen.move_trigger_zone('forest_entrance', 400, 250, 100, 100)
    
    # EXEMPLO 2: Usar preset predefinido
    print("🌲 Aplicando preset 'tree' para floresta...")
    game_screen.set_forest_trigger_preset('tree')
    
    # EXEMPLO 3: Personalização manual completa
    print("🏘️ Movendo vila para posição customizada...")
    game_screen.move_trigger_zone('village_path', 600, 100, 120, 80)
    
    # EXEMPLO 4: Ativar debug visual
    print("👁️ Ativando visualização debug...")
    game_screen.toggle_trigger_debug()
    
    return game_screen

def main():
    """Teste das funcionalidades de customização"""
    app = QApplication(sys.argv)
    
    # Criar instância do jogo
    game_screen = GameScreen()
    
    # Personalizar triggers
    game_screen = customize_triggers(game_screen)
    
    # Mostrar instruções
    game_screen.narration_label.setText("""
🎮 CONTROLES DE PERSONALIZAÇÃO:
• Tecla T: Mostrar/ocultar trigger zones
• Tecla F: Ajuda de personalização
• Mova o personagem para testar as zonas
    """.strip())
    
    # Mostrar jogo
    game_screen.show()
    
    return app.exec()

if __name__ == "__main__":
    main()