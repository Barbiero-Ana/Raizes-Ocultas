import os
import hashlib
import sqlite3
from database.criar_banco import Funcoes_DataBase
from backend.validador import Validador

class Cadastrar:
    def __init__(self):
        # Garante que o diretório database existe
        if not os.path.exists("database"):
            os.makedirs("database")
            
        db_path = os.path.join("database", "raizes_ocultas.db")
        self.db = Funcoes_DataBase(db_path)
        
        # Verifica se o banco existe e tem as tabelas necessárias
        if not self.verificar_banco_pronto():
            raise Exception("Banco de dados não está pronto para uso")

    def verificar_banco_pronto(self):
        """Verifica se o banco de dados existe e tem a tabela Usuario"""
        try:
            conn = self.db.db.conectar_no_banco()
            if conn is None:
                return False
                
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Usuario'")
                return cursor.fetchone() is not None
                
        except Exception as e:
            print(f"Erro ao verificar banco: {e}")
            return False
        finally:
            self.db.db.fechar_conexao()
            
    def validar_dados_cadastro(self, nome: str, email: str, senha: str, confirmar_senha: str) -> tuple:
        """
        Valida os dados de cadastro
        
        Args:
            nome: Nome do usuário
            email: Email do usuário
            senha: Senha
            confirmar_senha: Confirmação da senha
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        # Validar campos obrigatórios
        if not nome.strip():
            return False, "Nome é obrigatório"
        
        if not email.strip():
            return False, "E-mail é obrigatório"
            
        if not senha:
            return False, "Senha é obrigatória"
            
        if not confirmar_senha:
            return False, "Confirmação de senha é obrigatória"
        
        # Validar formato do email
        valido, msg = Validador.validar_email(email)
        if not valido:
            return False, msg
        
        # Validar se as senhas coincidem
        if senha != confirmar_senha:
            return False, "As senhas não coincidem"
        
        # Validar força da senha
        if len(senha) < 6:
            return False, "Senha deve ter pelo menos 6 caracteres"
        
        return True, "Dados válidos"
    
    def cadastrar_usuario(self, nome: str, email: str, senha: str, confirmar_senha: str) -> tuple:
        """
        Cadastra um novo usuário
        
        Args:
            nome: Nome do usuário
            email: Email do usuário
            senha: Senha em texto puro
            confirmar_senha: Confirmação da senha
            
        Returns:
            tuple: (sucesso: bool, mensagem: str, id_usuario: int ou None)
        """
        # Validar dados
        valido, msg = self.validar_dados_cadastro(nome, email, senha, confirmar_senha)
        if not valido:
            return False, msg, None
        
        try:
            # Hash da senha
            senha_hash = hashlib.sha256(senha.encode()).hexdigest()
            
            # Inserir no banco
            user_id = self.db.inserir_cliente(nome.strip(), email.strip(), senha_hash)
            
            if user_id:
                return True, "Usuário cadastrado com sucesso!", user_id
            else:
                return False, "Erro ao inserir usuário no banco", None
                
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return False, "Este e-mail já está cadastrado", None
            else:
                return False, f"Erro de integridade: {str(e)}", None
        
        except Exception as e:
            return False, f"Erro ao cadastrar usuário: {str(e)}", None
    
    def verificar_email_existe(self, email: str) -> bool:
        """
        Verifica se um email já está cadastrado
        
        Args:
            email: Email para verificar
            
        Returns:
            bool: True se o email já existe, False caso contrário
        """
        try:
            conn = self.db.db.conectar_no_banco()
            if conn is None:
                return False
                
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id_usuario FROM Usuario WHERE email = ?", (email,))
                result = cursor.fetchone()
                return result is not None
                
        except Exception as e:
            print(f"Erro ao verificar email: {e}")
            return False
        finally:
            self.db.db.fechar_conexao()

def cadastrar_usuario_simples(nome: str, email: str, senha: str) -> tuple:
    """
    Função utilitária para cadastrar um usuário de forma simples
    
    Args:
        nome: Nome do usuário
        email: Email do usuário
        senha: Senha em texto puro
        
    Returns:
        tuple: (sucesso: bool, mensagem: str, id_usuario: int ou None)
    """
    cadastrador = Cadastrar()
    return cadastrador.cadastrar_usuario(nome, email, senha, senha)