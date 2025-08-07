from PyQt6.QtWidgets import QMessageBox
<<<<<<< Updated upstream
from database.criar_banco import Database, Funcoes_DataBase
=======
from Database.criar_banco import Database, Funcoes_DataBase
>>>>>>> Stashed changes
import sys
import os
from backend.validador import Validador
import sqlite3
import hashlib


class Login:
    def __init__(self):
        db_path = os.path.join("database", "raizes_ocultas.db")
        self.db = Funcoes_DataBase(db_path)
    
    def verificar_credenciais(self, email: str, senha: str) -> tuple:
        """
        Verifica as credenciais de login do usuário
        
        Args:
            email: Email do usuário
            senha: Senha em texto puro (será hasheada para comparação)
            
        Returns:
            tuple: (sucesso: bool, mensagem: str, id_usuario: int)
        """
        conn = self.db.db.conectar_no_banco()
        if conn is None:
            return False, "Erro ao conectar ao banco", None
            
        try:
            with conn:
                cursor = conn.cursor()
                
                # Hash da senha fornecida
                senha_hash = hashlib.sha256(senha.encode()).hexdigest()
                
                # Busca usuário pelo email
                cursor.execute("""
                    SELECT id_usuario, cripto_senha, deletado 
                    FROM Usuario 
                    WHERE email = ?
                """, (email,))
                
                usuario = cursor.fetchone()
                
                if not usuario:    
                    return False, "E-mail não cadastrado", None

                id_usuario, hash_armazenado, deletado = usuario
                
                if deletado:
                    return False, "Conta desativada", None
                    
                if senha_hash != hash_armazenado:
                    return False, "Senha incorreta", None
                    
                return True, "Login bem-sucedido", id_usuario
                
        except sqlite3.Error as e:
            print(f"Erro ao verificar login: {e}")
            return False, f"Erro no banco de dados: {e}", None
        finally:
            self.db.db.fechar_conexao()

    def realizar_login(self, email: str, senha: str) -> tuple:
        """
        Realiza o processo completo de login com validações
        
        Args:
            email: Email do usuário
            senha: Senha em texto puro
            
        Returns:
            tuple: (sucesso: bool, mensagem: str, id_usuario: int)
        """
        # Validação dos campos
        if not email.strip() or not senha.strip():
            return False, "Preencha todos os campos", None
            
        # Valida o email
        valido, msg = Validador.validar_email(email)
        if not valido:
            return False, msg, None
            
        # Verifica  no banco
        return self.verificar_credenciais(email, senha)