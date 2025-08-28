import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox, QMainWindow
from PyQt6.QtGui import QIcon

def setup_paths():
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    paths_to_add = [
        project_root,                                    
        os.path.join(project_root, 'front'),            
        os.path.join(project_root, 'front', 'Screens'), 
        os.path.join(project_root, 'assets')           
    ]
    
    for path in paths_to_add:
        if path not in sys.path:
            sys.path.insert(0, path)
    
    print(f"📁 Diretório do projeto: {project_root}")
    print("📂 Caminhos configurados:")
    for path in paths_to_add:
        exists = "✅" if os.path.exists(path) else "❌"
        print(f"  {exists} {path}")

def check_files():
    print("\nVerificando arquivos")
    
    required_files = [
        ('front/Screens/Login_screen.py', 'Tela de Login'),
        ('front/Screens/game_screen.py', 'Tela do Jogo'),
        ('backend/login.py', 'Sistema de Login'),
        ('backend/validador.py', 'Validador'),
        ('Database/criar_banco.py', 'Banco de Dados'),
    ]
    
    optional_files = [
        ('front/Screens/class_register_screen.py', 'Tela de Cadastro de Turma'),
        ('assets/ScreenElements/MT-bandeira-logo.png', 'Logo Principal'),
        ('assets/ScreenElements/gamescreen/logo-temp.png', 'Ícone do App')
    ]
    
    all_good = True
    
    print("📋 Arquivos obrigatórios:")
    for file_path, description in required_files:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
        exists = os.path.exists(full_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {description} - {file_path}")
        if not exists:
            all_good = False
    
    print("\n📝 Arquivos opcionais:")
    for file_path, description in optional_files:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), file_path)
        exists = os.path.exists(full_path)
        status = "✅" if exists else "⚠️"
        print(f"  {status} {description} - {file_path}")
    
    return all_good

def initialize_database():
    print("\nInicializando banco de dados...")
    try:
        from database.criar_banco import Database, Funcoes_DataBase
        
        db_path = os.path.join("Database", "raizes_ocultas.db")
        db = Database(db_path)
        funcoes = Funcoes_DataBase(db_path)
        
        if not db.banco_existe():
            print("Criando tabelas...")
            if db.criar_tabelas():
                print("✅ Tabelas criadas com sucesso!")
                
                print("Inserindo perguntas padrão...")
                sucesso, msg = funcoes.inserir_perguntas_padrao()
                print(f"{'✅' if sucesso else '❌'} {msg}")
            else:
                print("❌ Erro ao criar tabelas")
                return False
        else:
            print("✅ Banco de dados já existe")
        
        return True
    except ImportError as e:
        print(f"❌ Erro ao importar módulo do banco de dados: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {str(e)}")
        return False

def load_icon(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(base_dir, *relative_path.split('/'))
    
    if os.path.exists(icon_path):
        return QIcon(icon_path)
    print(f"⚠️ Ícone não encontrado: {icon_path}")
    return QIcon()  # Retorna ícone vazio se não encontrar

def main():    
    # Configuração para ícone na taskbar no Windows
    if sys.platform == 'win32':
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('raizes.ocultas.1.0')
    
    setup_paths()

    if not check_files():
        print("\n❌ ERRO: Arquivos obrigatórios não encontrados!")
        return 1

    if not initialize_database():
        print("\n❌ ERRO: Falha ao inicializar banco de dados!")
        return 1
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Raízes Ocultas")
        
        app_icon = load_icon('assets/ScreenElements/gamescreen/logo-temp.png')
        
        if not app_icon.isNull():
            app.setWindowIcon(app_icon)
            print("✅ Ícone principal carregado com sucesso")
        else:
            print("⚠️ Nenhum ícone principal carregado")
        
        app.setApplicationVersion("1.0")

        from front.Screens.Login_screen import TelaLogin        
        janela_login = TelaLogin()
        
        if not app_icon.isNull():
            janela_login.setWindowIcon(app_icon)
        
        janela_login.show()
        print("\n✅ Aplicação iniciada com sucesso!")
        print("=" * 50)
        
        return app.exec()
        
    except ImportError as e:
        print(f"\n❌ ERRO DE IMPORTAÇÃO: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())