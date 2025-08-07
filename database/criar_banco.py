import sqlite3
from sqlite3 import Error
import hashlib
from datetime import datetime
import os 

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        
    def banco_existe(self):
        try:
            return os.path.exists(self.db_name)  
        except Exception as e:
            print(f"Erro ao verificar existência do banco: {e}")
            return False
            
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
                #----------------- Professor ---------------------------
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Usuario(
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_usuario TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    cripto_senha TEXT NOT NULL,
                    deletado BOOLEAN DEFAULT 0,
                    data_delecao TEXT
                )
                """)
                #-------------------  Turma ------------------
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Turma(
                    id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_turma TEXT NOT NULL UNIQUE,
                    quantidade_turma INTEGER NOT NULL,
                    serie_turma TEXT NOT NULL, 
                    vida_max INTEGER NOT NULL,
                    vida_atual INTEGER NOT NULL,
                    pontos_acerto INTEGER NOT NULL DEFAULT 0,
                    pontos_erro INTEGER NOT NULL DEFAULT 0,
                    vivo BOOLEAN DEFAULT 1,
                    id_usuario INTEGER NOT NULL,
                    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
                )
                """)
                #-----------------  Inimigos --------------------------
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Inimigos(
                    id_inimigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_inimigo TEXT NOT NULL,
                    tipo_inimigo INTEGER NOT NULL CHECK(tipo_inimigo IN (3, 4, 5)),
                    vida_max INTEGER NOT NULL,
                    vida_atual INTEGER NOT NULL,
                    aparencia_inimigo TEXT NOT NULL,
                    vivo BOOLEAN DEFAULT 1
                )
                """)
                #--------------------  Boss ------------------------
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
                #------------- salvar o progresso das Turmas-------
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Dados_do_jogador(
                    id_progresso INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_turma INTEGER NOT NULL,
                    id_boss INTEGER NOT NULL,
                    flag_progresso BOOLEAN DEFAULT 0,
                    FOREIGN KEY (id_turma) REFERENCES Turma(id_turma) ON DELETE CASCADE,
                    FOREIGN KEY (id_boss) REFERENCES Boss(id_boss) ON DELETE CASCADE
                )
                """)
                #------------  salvar as questões -----------------
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Perguntas(
                    id_pergunta INTEGER PRIMARY KEY AUTOINCREMENT,
                    pergunta TEXT NOT NULL,
                    classe_pergunta INTEGER NOT NULL CHECK(classe_pergunta IN (3, 4, 5)),
                    dificuldade_pergunta INTEGER NOT NULL CHECK(dificuldade_pergunta IN (1, 2, 3, 4)),
                    opcao_a TEXT NOT NULL,
                    opcao_b TEXT NOT NULL,
                    opcao_c TEXT NOT NULL,
                    opcao_d TEXT NOT NULL,
                    resposta TEXT NOT NULL CHECK(resposta IN ('A','B','C','D'))
                )
                """)
                #----------------  Respostas das Turmas ---------------
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Time_Respostas(
                    id_tempo_resposta INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL, 
                    id_pergunta INTEGER NOT NULL,
                    tempo_resposta INTEGER NOT NULL,
                    time_out BOOLEAN DEFAULT 0,
                    FOREIGN KEY(id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
                    FOREIGN KEY(id_pergunta) REFERENCES Perguntas(id_pergunta) ON DELETE CASCADE
                )
                """)
                
            return True
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False

class Funcoes_DataBase:
    def __init__(self, db_name):
        self.db = Database(db_name)
        
    def inserir_turma(self, nome, quantidade, serie, vida_max, vida_atual, pontos_acerto, pontos_erro, vivo, id_usuario):
        conn = self.db.conectar_no_banco()
        if conn is None:
            raise Exception("Erro ao conectar ao banco")
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Turma (
                        nome_turma, quantidade_turma, serie_turma,
                        vida_max, vida_atual, pontos_acerto, pontos_erro, vivo, id_usuario
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (nome, quantidade, serie, vida_max, vida_atual, pontos_acerto, pontos_erro, vivo, id_usuario))
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise Exception("Esta turma já está cadastrada")
            raise Exception(f'Erro de integridade: {str(e)}')
        except Error as e:
            raise Exception(f"Erro ao inserir Turma: {str(e)}")
        finally:
            self.db.fechar_conexao()

    def salvar_turma(self, turma):
        if not self.validar_turma(turma):
            return False, "Dados da turma inválidos"
            
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
                    1 if getattr(turma, 'vivo', True) else 0,
                    turma.id_usuario
                )
                
                if hasattr(turma, 'id_turma') and turma.id_turma:
                    # Atualização
                    cursor.execute("""
                        UPDATE Turma SET
                            nome_turma = ?,
                            vida_max = ?,
                            vida_atual = ?,
                            vivo = ?
                        WHERE id_turma = ? AND id_usuario = ?
                    """, dados + (turma.id_turma, turma.id_usuario))
                    
                    if cursor.rowcount == 0:
                        return False, "Turma não encontrada ou não pertence ao usuário"
                        
                    return True, "Turma atualizada com sucesso"
                else:
                    # Inserção
                    cursor.execute("""
                        INSERT INTO Turma (
                            nome_turma, vida_max, vida_atual, vivo, id_usuario
                        ) VALUES (?, ?, ?, ?, ?)
                    """, dados)
                    
                    turma.id_turma = cursor.lastrowid
                    return True, "Turma criada com sucesso"
                    
        except Error as e:
            print(f"Erro ao salvar turma: {e}")
            return False, f"Erro no banco de dados: {e}"
        finally:
            self.db.fechar_conexao()
    
    def validar_turma(self, turma):
        """Valida os dados básicos da turma"""
        required_attrs = [
            'nome_turma', 'vida_max', 'vida_atual', 'id_usuario'
        ]
        
        for attr in required_attrs:
            if not hasattr(turma, attr):
                print(f"Atributo faltando: {attr}")
                return False
                
        # Validações 
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
                DELETE FROM Usuario 
                WHERE deletado = 1 
                AND data_delecao < date('now', ?)
                ''', (f'-{dias} days',))
                
                return True, f"{cursor.rowcount} usuários removidos"
        except Error as e:
            print(f"Erro ao limpar usuários: {e}")
            return False, f"Erro ao limpar usuários: {e}"
        finally:
            self.db.fechar_conexao()
    
    
    def inserir_cliente(self, nome, email, senha):
        """Insere um novo usuário no banco de dados"""
        conn = self.db.conectar_no_banco()  # Alterado de self.conectar_no_banco() para self.db.conectar_no_banco()
        if conn is None:
            raise Exception("Não foi possível conectar ao banco de dados")
            
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO Usuario (
                        nome_usuario, email, cripto_senha
                    ) VALUES (?, ?, ?)
                """, (nome, email, senha))
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise Exception("Este e-mail já está cadastrado")
            raise Exception(f"Erro de integridade: {str(e)}")
        except Error as e:
            raise Exception(f"Erro ao inserir usuário: {str(e)}")
        finally:
            self.db.fechar_conexao()  # Alterado de self.fechar_conexao() para self.db.fechar_conexao()
        
    def inserir_perguntas_padrao(self):
        """Insere as perguntas padrão no banco de dados"""
        perguntas_exemplo = [
            # Ato I — Raízes Esquecidas (Cultura Indígena) -> consulte o documento na pasta de docs
            {
                'pergunta': 'Qual destes animais é sagrado para o povo Bororo?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Onça-pintada',
                'opcao_b': 'Arara',
                'opcao_c': 'Jaburu',
                'opcao_d': 'Tatu',
                'resposta': 'C'
            },
            {
                'pergunta': 'A pintura corporal indígena é usada principalmente para...?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Proteção contra insetos',
                'opcao_b': 'Expressão cultural e identidade',
                'opcao_c': 'Camuflagem na floresta',
                'opcao_d': 'Decorar o corpo para festas',
                'resposta': 'B'
            },
            {
                'pergunta': 'Qual dança é tradicional em festas de rua mato-grossenses?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Samba',
                'opcao_b': 'Siriri',
                'opcao_c': 'Funk',
                'opcao_d': 'Forró',
                'resposta': 'B'
            },
            {
                'pergunta': 'O que é rasqueado?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Um prato típico',
                'opcao_b': 'Um ritmo musical',
                'opcao_c': 'Uma técnica de plantio',
                'opcao_d': 'Um tipo de artesanato',
                'resposta': 'B'
            },
            {
                'pergunta': 'Qual prato é feito com peixe e muito comum na região?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Moqueca',
                'opcao_b': 'Pacu assado',
                'opcao_c': 'Caldo de piranha',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            }
        ]
        
        inserir = Inserir_perguntas(self.db.db_name)
        return inserir.inserir_perguntas(perguntas_exemplo)

class Inserir_perguntas:
    def __init__(self, db_name):
        self.db = Database(db_name)
        
    def inserir_perguntas(self, lista_perguntas):
        conn = self.db.conectar_no_banco()
        if conn is None:
            return False, "Erro ao conectar ao banco"
        
        try:
            with conn:
                cursor = conn.cursor()                
                dados_insercao = []
                for pergunta in lista_perguntas:
                    # validando a bendita estrutura básica
                    campos_obrigatorios = [
                        'pergunta', 'classe_pergunta', 'dificuldade_pergunta',
                        'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'resposta'
                    ]
                    
                    if not all(campo in pergunta for campo in campos_obrigatorios):
                        return False, f"Estrutura inválida na pergunta: {pergunta}"
                    
                    # valid valores específicos
                    if pergunta['classe_pergunta'] not in (3, 4, 5):
                        return False, f"Classe inválida na pergunta: {pergunta['pergunta']}"
                    
                    if pergunta['dificuldade_pergunta'] not in (1, 2, 3, 4):
                        return False, f"Dificuldade inválida na pergunta: {pergunta['pergunta']}"
                    
                    if pergunta['resposta'].upper() not in ('A', 'B', 'C', 'D'):
                        return False, f"Resposta inválida na pergunta: {pergunta['pergunta']}"                    
                    dados_insercao.append((
                        pergunta['pergunta'],
                        pergunta['classe_pergunta'],
                        pergunta['dificuldade_pergunta'],
                        pergunta['opcao_a'],
                        pergunta['opcao_b'],
                        pergunta['opcao_c'],
                        pergunta['opcao_d'],
                        pergunta['resposta'].upper()
                    ))                
                cursor.executemany("""
                    INSERT INTO Perguntas (
                        pergunta, classe_pergunta, dificuldade_pergunta,
                        opcao_a, opcao_b, opcao_c, opcao_d, resposta
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, dados_insercao)
                
                return True, f"{len(lista_perguntas)} perguntas inseridas com sucesso"
                
        except Error as e:
            print(f"Erro ao inserir perguntas: {e}")
            return False, f"Erro ao inserir perguntas: {e}"
        finally:
            self.db.fechar_conexao()

if __name__ == "__main__":
    pasta_db = "database"
    nome_banco = "raizes_ocultas.db"
    caminho_completo = os.path.join(pasta_db, nome_banco)
    
    db = Database(caminho_completo)
    funcoes = Funcoes_DataBase(caminho_completo)
    
    if not db.banco_existe():
        print("Criando banco de dados e tabelas...")
        sucesso = db.criar_tabelas()
        
        if sucesso:
            print("Tabelas criadas com sucesso!")            
            print("Inserindo perguntas padrão...")
            sucesso, mensagem = funcoes.inserir_perguntas_padrao()
            print(mensagem)
        else:
            print("Erro ao criar tabelas.")
            exit(1)
    else:
        print("Banco de dados já existe.")        
        conn = db.conectar_no_banco()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Perguntas")
            count = cursor.fetchone()[0]
            if count == 0:
                print("Inserindo perguntas padrão...")
                sucesso, mensagem = funcoes.inserir_perguntas_padrao()
                print(mensagem)
            else:
                print(f"Banco já contém {count} perguntas.")
        except Error as e:
            print(f"Erro ao verificar perguntas: {e}")
        finally:
            db.fechar_conexao()