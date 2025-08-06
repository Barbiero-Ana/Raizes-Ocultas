import os
from database.criar_banco import Funcoes_DataBase
import sqlite3

class CadastrarTurma:
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

    def validar_dados_cadastro_turma(self,nome:str, quantidade:int, serie:str):

        if not nome.strip():
            return False,"Nome é obrigatório"
        
        if not quantidade.strip():
            return False, "Quantidade é alunos obrigatoria"
        
        if not serie.strip():
            return False, "Serie é obrigatoria"


    def cadastrar_turma(self,nome:str, quantidade:int, serie:str):

        try:

            turma_id = self.db.inserir_turma(nome.strip(),quantidade, serie)

            if turma_id:
                return True,"Turma cadastrada com sucesso!", turma_id
            else:
                return False, "Erro ao inserir turma no banco", None
            
        except sqlite3.IntegrityError as e:
            if "UINIQUE constraint failed" in str(e):
                return False,"Este nome para Turma já esta sendo usado",None
            else:
                return False,f"Erro de integridade: {str(e)}",None  
            
    def verificar_se_nomeTurma_existe (self,nome:str) -> bool:

        try:
            conn = self.db.db.conectar_no_banco()
            if conn is None:
                return False
            
            with conn:
                cursor = conn.cursor()

                cursor.execute("SELECT id_turma FROM Turma WHERE nome_turma = ?",(nome))
                result = cursor.fetchone()
                return result is not None
        
        except Exception as e:
            print(f'Erro ao verificar nome da Turma: {e}')

        finally:
            self.db.db.fechar_conexao()
        
    def cadastrar_turma_simples(nome:str, quantidade:int,serie:str) -> tuple:

        inserir_turma = CadastrarTurma()
        return inserir_turma.cadastrar_turma(nome,quantidade,serie)