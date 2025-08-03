#!/usr/bin/env python3
"""
Raízes Ocultas - Main Application
Ponto de entrada principal da aplicação
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

def setup_paths():

    project_root = os.path.dirname(os.path.abspath(__file__))
    

    paths_to_add = [
        project_root,                           
        os.path.join(project_root, 'front'),    
        os.path.join(project_root, 'front', 'Screens'),  
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    print(f"Diretório do projeto: {project_root}")
    print(f"Caminhos adicionados ao Python path:")
    for path in paths_to_add:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {exists} {path}")

def check_dependencies():
    """Verifica se as dependências estão disponíveis"""
    print("\n=== Verificando dependências ===")
    
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6 disponível")
    except ImportError as e:
        print(f"❌ PyQt6 não encontrado: {e}")
        return False
    
    login_file = os.path.join('front', 'Screens', 'Login_screen.py')
    if os.path.exists(login_file):
        print("✅ Login_screen.py encontrado")
    else:
        print(f"❌ {login_file} não encontrado")
        return False
    
    game_file = os.path.join('front', 'Screens', 'game_screen.py')
    if os.path.exists(game_file):
        print("✅ game_screen.py encontrado")
    else:
        print(f"⚠️  {game_file} não encontrado - será criado automaticamente")
    
    return True

def create_missing_files():
    """Cria arquivos que estão faltando"""
    game_screen_path = os.path.join('front', 'Screens', 'game_screen.py')
    
    if not os.path.exists(game_screen_path):
        print(f"Criando {game_screen_path}...")
        
        os.makedirs(os.path.dirname(game_screen_path), exist_ok=True)
        
        game_screen_content = '''from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QWidget, QVBoxLayout
from PyQt6.QtCore import Qt

class GameScreen(QMainWindow):
    def __init__(self, tela_login=None):
        super().__init__()
        self.tela_login = tela_login
        self.setWindowTitle("Raízes Ocultas - Jogo")
        self.setFixedSize(800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        label = QLabel("🎮 Bem-vindo ao Raízes Ocultas! 🎮")
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        btn_voltar = QPushButton("← Voltar ao Login")
        btn_voltar.clicked.connect(self.voltar_para_login)
        layout.addWidget(btn_voltar)
    
    def voltar_para_login(self):
        self.close()
        if self.tela_login:
            self.tela_login.show()
'''
        
        try:
            with open(game_screen_path, 'w', encoding='utf-8') as f:
                f.write(game_screen_content)
            print(f"✅ {game_screen_path} criado com sucesso")
        except Exception as e:
            print(f"❌ Erro ao criar {game_screen_path}: {e}")

def main():
    """Função principal da aplicação"""
    print("=== INICIANDO RAÍZES OCULTAS ===\n")
    
    # Configurar caminhos
    setup_paths()
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Erro: Dependências não encontradas")
        return 1
    
    # Criar arquivos faltando
    create_missing_files()
    
    try:
        # Criar a aplicação Qt
        app = QApplication(sys.argv)
        app.setApplicationName("Raízes Ocultas")
        app.setApplicationVersion("1.0")
        
        print("\n=== Importando tela de login ===")
        
        # Importar a tela de login
        from front.Screens.Login_screen import TelaLogin
        
        print("✅ Tela de login importada com sucesso")
        
        # Criar e mostrar a janela principal
        janela_login = TelaLogin()
        janela_login.show()
        
        print("✅ Aplicação iniciada com sucesso!")
        print("=== Executando aplicação ===\n")
        
        # Executar o loop principal da aplicação
        return app.exec()
        
    except ImportError as e:
        print(f"\n❌ Erro de importação: {e}")
        print("Dica: Verifique se todos os arquivos estão no local correto")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())