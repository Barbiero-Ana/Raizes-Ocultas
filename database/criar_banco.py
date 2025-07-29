import sqlite3
from sqlite3 import Error
import hashlib
from datetime import datetime

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None

    def conectar_no_banco(self):
        try:
            if self.conn is None:
                self.conn = sqlite3.connect(self.db_name, timeout=10)
                self.conn.execute('PRAGMA journal_mode=WAL')
                self.conn.execute("PRAGMA foreign_keys = ON")
            return self.conn
        except Error as e:
            print(f'Erro ao Conectar: {e}')
            return None

    def fechar_conexao(self):
        if self.conn is not None:
            try:
                self.conn.close()
            except Exception as e:
                print(f'Erro ao Fechar Conexão: {e}')
            finally:
                self.conn = None

    def __del__(self):
        self.fechar_conexao()

    def criar_tabelas(self):
        conn = self.conectar_no_banco()
        if conn is None:
            return False

        try:
            with conn:
                cursor = conn.cursor()

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuario(
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_usuario TEXT NOT NULL,
                    email TEXT NOT NULL,
                    cripto_senha TEXT NOT NULL,
                    deletado BOOLEAN DEFAULT 0,
                    data_delecao TEXT
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Turma(
                    id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_turma TEXT NOT NULL,
                    vida_max INTEGER NOT NULL,
                    vida_atual INTEGER NOT NULL,
                    pontos_acerto INTEGER NOT NULL,
                    pontos_erro INTEGER NOT NULL,
                    vivo BOOLEAN DEFAULT 0,
                    id_usuario INTEGER NOT NULL,
                    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Inimigos(
                    id_inimigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_inimigo TEXT NOT NULL,
                    tipo_inimigo INTEGER NOT NULL CHECK(tipo_inimigo IN (3, 4, 5)),
                    vida_max INTEGER NOT NULL,
                    vida_atual INTEGER NOT NULL,
                    aparencia_inimigo TEXT NOT NULL,
                    vivo BOOLEAN DEFAULT 0
                )
                """)
                ##3 - Comida 4 - arte - 5 cultura 
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Boss(
                    id_boss INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_boss TEXT NOT NULL,
                    tipo_boss INTEGER NOT NULL CHECK(tipo_boss IN (3,4,5)),
                    vida_max INTEGER NOT NULL,
                    vida_atual INTEGER NOT NULL,
                    aparencia_boss TEXT NOT NULL
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS dados_do_jogador(
                    id_progresso INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_turma INTEGER NOT NULL,
                    id_boss INTEGER NOT NULL,
                    flag_progresso BOOLEAN DEFAULT 0,
                    FOREIGN KEY (id_turma) REFERENCES Turma(id_turma) ON DELETE CASCADE,
                    FOREIGN KEY (id_boss) REFERENCES Boss(id_boss) ON DELETE CASCADE
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS perguntas(
                    id_pergunta INTEGER PRIMARY KEY AUTOINCREMENT,
                    pergunta TEXT NOT NULL,
                    classe_pergunta INTEGER NOT NULL CHECK(classe_pergunta IN (3, 4, 5)),
                    dificuldade_pergunta INTEGER NOT NULL CHECK(dificuldade_pergunta IN (1, 2, 3)),
                    opcao_a TEXT NOT NULL,
                    opcao_b TEXT NOT NULL,
                    opcao_c TEXT NOT NULL,
                    opcao_d TEXT NOT NULL,
                    resposta TEXT NOT NULL CHECK(resposta IN ('A','B','C','D'))
                )
                """)

            return True
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False



class Funcoes_DataBase:
    def __init__(self, db_name):
        self.db = Database(db_name)
        
    def salvar_turma(self, turma):

        if not self.validar_turma(turma):
            return False, "Dados do turma inválidos"
            
        conn = self.db.conectar_no_banco()
        if conn is None:
            return False, "Erro ao conectar ao banco"
            
        try:
            with conn:
                cursor = conn.cursor()
                
                dados = (
                    turma.nome_turma,
                    turma.vida_max,
                    turma.vida_atual,
                    turma.experiencia,
                    1 if getattr(turma, 'vivo', True) else 0,
                    turma.id_usuario
                )
                
                if hasattr(turma, 'id_turma') and turma.id_turma:
                    # Atualização
                    cursor.execute("""
                        UPDATE personagens SET
                            nome_turma = ?,
                            vida_max = ?,
                            vida_atual = ?,
                            vivo = ?
                        WHERE id_turma = ? AND id_usuario = ?
                    """, dados + (turma.id_turma, turma.id_usuario))
                    
                    if cursor.rowcount == 0:
                        return False, "turma não encontrado ou não pertence ao usuário"
                        
                    return True, "turma atualizado com sucesso"
                else:
                    # Inserção
                    cursor.execute("""
                        INSERT INTO personagens (
                            nome_turma, vida_max, vida_atual, turma_selecionado,
                            vivo, id_usuario
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, dados)
                    
                    turma.id_turma = cursor.lastrowid
                    return True, "turma criado com sucesso"
                    
        except Error as e:
            print(f"Erro ao salvar turma: {e}")
            return False, f"Erro no banco de dados: {e}"
        finally:
            self.db.fechar_conexao()
    
    def validar_turma(self, turma):
        """Valida os dados básicos do turma"""
        required_attrs = [
            'nome_turma', 'vida_max', 'vida_atual', 
            'turma_selecionado', 'id_usuario'
        ]
        
        for attr in required_attrs:
            if not hasattr(turma, attr):
                print(f"Atributo faltando: {attr}")
                return False
                
        # Validações adicionais
        if turma.vida_atual > turma.vida_max:
            print("Vida atual maior que vida máxima")
            return False
            
            
        return True
    
    def limpar_usuarios_deletados(self, dias=30):
        """Remove usuários deletados há mais de X dias"""
        conn = self.db.conectar_no_banco()
        if conn is None:
            return False
            
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute('''
                DELETE FROM usuario 
                WHERE deletado = 1 
                AND data_delecao < date('now', ?)
                ''', (f'-{dias} days',))
                
                return True, f"{cursor.rowcount} usuários removidos"
        except Error as e:
            print(f"Erro ao limpar usuários: {e}")
            return False, f"Erro ao limpar usuários: {e}"
        finally:
            self.db.fechar_conexao()
    
    def inserir_cliente(self, nome, email, senha, cpf, endereco, telefone, data_nascimento, idade):
        conn = self.conectar_no_banco()
        if conn is None:
            return None
            
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Usuario (
                        nome_usuario, email, cripto_senha
                    ) VALUES (?, ?, ?)
                """, (nome, email, senha ))
                return cursor.lastrowid
        except Error as e:
            raise e
        finally:
            self.fechar_conexao()

if __name__ == "__main__":
    nome_banco = "rpg_game.db"
    db = Database(nome_banco)
    sucesso = db.criar_tabelas()

    if sucesso:
        print("Tabelas criadas com sucesso!")
        # Inserir perguntas
        funcoes = Funcoes_DataBase(nome_banco)
        funcoes.inserir_perguntas_padrao()
    else:
        print("Erro ao criar tabelas.")
