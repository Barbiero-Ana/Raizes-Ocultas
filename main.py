import sys
import os
from PyQt6.QtWidgets import QApplication, QMessageBox

def setup_paths():

    project_root = os.path.dirname(os.path.abspath(__file__))
    

    paths_to_add = [
        project_root,                                    
        os.path.join(project_root, 'front'),            #  front
        os.path.join(project_root, 'front', 'Screens'), #  telas
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
    # n aguento mais debugar código meu jesus cristo
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
    ]
    
    all_good = True
    
    print("📋 Arquivos obrigatórios:")
    for file_path, description in required_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {description} - {file_path}")
        if not exists:
            all_good = False
    
    print("\n📝 Arquivos opcionais:")
    for file_path, description in optional_files:
        exists = os.path.exists(file_path)
        status = "✅" if exists else "⚠️ "
        print(f"  {status} {description} - {file_path}")
    
    return all_good

def initialize_database():
    print("\nBanco iniciado e funcionando !")
    try:
        from database.criar_banco import Database, Funcoes_DataBase
        
        # Caminho do banco
        db_path = os.path.join("Database", "raizes_ocultas.db")
        db = Database(db_path)
        funcoes = Funcoes_DataBase(db_path)
        
        if not db.banco_existe():
            print("criando tabela")
            if db.criar_tabelas():
                print("FUNCIONOU! TEMOS TABELAS!")
                
                print("ajustando perguntas")
                sucesso, msg = funcoes.inserir_perguntas_padrao()
                print(f"{'✅' if sucesso else '❌'} {msg}")
            else:
                print("❌ Erro ao criar tabelas")
                return False
        else:
            print("✅ Banco de dados já existe")
        
        return True
    except Exception as e:
        print(f"❌ Erro ao inicializar banco: {e}")
        return False

def main():
    print("🎮 === INICIANDO RAÍZES OCULTAS ===\n")
    
    # CAMINHOS
    setup_paths()

    if not check_files():
        print("\n❌ ERRO: Arquivos obrigatórios não encontrados!")
        print("💡 Certifique-se de que todos os arquivos estão no local correto.")
        return 1

    if not initialize_database():
        print("\n❌ ERRO: Falha ao inicializar banco de dados!")
        return 1
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Raízes Ocultas")
        app.setApplicationVersion("1.0")
        print("✅ Aplicação Qt criada")

        from front.Screens.Login_screen import TelaLogin        
        janela_login = TelaLogin()
        janela_login.show()
        print("✅ Interface pronta para uso\n")
        print("=" * 50)
        
        # exedcuta tufd principal
        return app.exec()
        
    except ImportError as e:
        print(f"\n❌ ERRO DE IMPORTAÇÃO: {e}")
        
        import traceback
        print("\n🔍 Detalhes:")
        traceback.print_exc()
        return 1
        
    except Exception as e:
        print(f"\n❌ ERRO INESPERADO: {e}")
        print("\nDetalhes:")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())