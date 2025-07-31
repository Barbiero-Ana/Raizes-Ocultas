from PyQt6.QtWidgets import (QApplication, QWidget, QMessageBox, )
from database.criar_banco import Database, Funcoes_DataBase
import sys
from validador import Validador
import requests
import sqlite3
import hashlib
from front.Screens.Login_screen import TelaLogin

# Pensar nos módulos como seres mais independentes

class Login:
    def __init__(self):
        self.db = Funcoes_DataBase("Raizes_Ocultas.db")
    
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
                """, (email,))  # Corrigido: adicionada vírgula para criar tupla
                
                usuario = cursor.fetchone()
                
                if not usuario:    
                    resposta = QMessageBox.question(
                        self,
                        "E-mail não cadastrado",
                        "E-mail não encontrado. Deseja se cadastrar ?",
                        QMessageBox.standardButton.YES | QMessageBox.standardButton.No
                    )
                    if resposta == QMessageBox.standardButton.Yes:
                        TelaLogin.abrir_tela_cadastro()
                
                                 
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
        # Validação básica dos campos
        if not email.strip() or not senha.strip():
            return False, "Preencha todos os campos", None
            
        # Valida formato do email
        valido, msg = Validador.validar_email(email)
        if not valido:
            return False, msg, None
            
        # Verifica credenciais no banco
        return self.verificar_credenciais(email, senha)
    

    # Adicione este novo método à classe TelaLogin:
    def validar_e_abrir_jogo(self):
        """Valida as credenciais antes de abrir o jogo"""
        email = self.input_email.text().strip()
        senha = self.input_senha.text().strip()
        
        # Cria instância do sistema de login, passando self como parent_window
        login_system = Login(parent_window=self)
        
        # Valida as credenciais
        sucesso, mensagem, id_usuario = login_system.realizar_login(email, senha)
        
        if sucesso:
            # Salva o ID do usuário se necessário
            self.id_usuario = id_usuario
            
            # Se as credenciais estiverem corretas, abre o jogo
            self.abrir_game_animacao()
        else:
            # Mostra mensagem de erro
            QMessageBox.warning(self, "Acesso Negado", mensagem)
            
            # Opcional: oferecer cadastro se o email não existir
            if "não cadastrado" in mensagem:
                resposta = QMessageBox.question(
                    self,
                    "Cadastro",
                    "Deseja criar uma nova conta?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if resposta == QMessageBox.StandardButton.Yes:
                    self.abrir_tela_cadastro()