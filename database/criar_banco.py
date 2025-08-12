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
    
    # Atualiza os Status da tumra 
    def atuaziar_status_turma(self,id_turma):
        cursor = self.conn.cursor()

        if id_turma: 
            cursor.execute("""
               UPDATE personagem SET 
                    vida_max = ?,
                    vida_atual = ?,
                    pontos_acertos = ?,
                    pontos_erros = ?,
                    vivo = ?,
                    WHERE id = ?  
            """,(
                id_turma.vida_max,
                id_turma.vida_atual,
                id_turma.pontos_acertos, 
                id_turma.pontos_erros,
                id_turma.vivo > 0,
                id_turma.id
            ))
        self.conn.commit()
        return id_turma
    
    # Carregar a as turmas para selecionar 
    def carregar_turma(self,id_usuario):
        from backend.turma import Turma
        cursor = self.conn.cursor()

        cursor.execute("SELECT * FROM Turma WHERE id_usuario ?",(id_usuario))
        
        rows = cursor.fetchall()

        turmas = []

        for row in rows: 
            turma = Turma(
                id_turma=row[0],
                nome = row[1],
                quantidade = [2],
                serie = row[3],
                vida = row[4],
                acertos = [6],
                erros = [7], 
            )
            turmas.vida_atual = row[5]

            turmas.append(turma)
        return turmas

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
        todas_perguntas = [
            # Ato I — O Chamado da Floresta (Mitologia e Povos Originários)
            # Fase 1 – Início da Jornada
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
                'pergunta': 'O que significa o termo "Xingu"?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Rio grande',
                'opcao_b': 'Povo guerreiro',
                'opcao_c': 'Terra fértil',
                'opcao_d': 'Lugar sagrado',
                'resposta': 'D'
            },
            # Fase 2 – Saberes da Terra
            {
                'pergunta': 'Que povo indígena habita o Parque Nacional do Xingu?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Guarani',
                'opcao_b': 'Yanomami',
                'opcao_c': 'Caiapó',
                'opcao_d': 'Vários povos diferentes',
                'resposta': 'D'
            },
            {
                'pergunta': 'Qual instrumento é tradicional em rituais indígenas mato-grossenses?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Violão',
                'opcao_b': 'Flauta de taquara',
                'opcao_c': 'Tambor',
                'opcao_d': 'Pandeiro',
                'resposta': 'B'
            },
            {
                'pergunta': 'O que representa o urucum na cultura ancestral?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Proteção espiritual',
                'opcao_b': 'Fertilidade',
                'opcao_c': 'Guerra',
                'opcao_d': 'Colheita abundante',
                'resposta': 'A'
            },
            # Fase 3 – O Espírito da Floresta
            {
                'pergunta': 'O que significa o uso de grafismos corporais nas culturas indígenas do Mato Grosso?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Status social',
                'opcao_b': 'Proteção espiritual',
                'opcao_c': 'Identidade cultural',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'Qual a função do pajé nas aldeias?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Líder político',
                'opcao_b': 'Guardião do conhecimento espiritual',
                'opcao_c': 'Caçador',
                'opcao_d': 'Artista',
                'resposta': 'B'
            },
            {
                'pergunta': 'Qual é o papel da oralidade na preservação da cultura indígena?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Transmitir conhecimentos entre gerações',
                'opcao_b': 'Manter viva a língua nativa',
                'opcao_c': 'Preservar histórias e tradições',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            # Fase 4 – Boss: O Guardião da Neblina
            {
                'pergunta': 'Como os povos originários interpretam o tempo e os ciclos naturais?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Como algo linear',
                'opcao_b': 'Como um ciclo contínuo',
                'opcao_c': 'Como algo controlado pelos deuses',
                'opcao_d': 'Como algo aleatório',
                'resposta': 'B'
            },
            
            # Ato II — Caminhos Ancestrais (Quilombos, Danças e Resistência)
            # Fase 1 – Batida dos Tambores
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
                'pergunta': 'O que é o cururu?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Um prato típico',
                'opcao_b': 'Uma dança folclórica',
                'opcao_c': 'Um instrumento musical',
                'opcao_d': 'Um tipo de artesanato',
                'resposta': 'B'
            },
            {
                'pergunta': 'Siriri é uma dança típica do estado? Sim ou não?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Sim',
                'opcao_b': 'Não',
                'opcao_c': '',
                'opcao_d': '',
                'resposta': 'A'
            },
            # Fase 2 – Cores e Ritmos Quilombolas
            {
                'pergunta': 'Que instrumentos são usados no siriri?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Violão e pandeiro',
                'opcao_b': 'Tambor e reco-reco',
                'opcao_c': 'Flauta e violino',
                'opcao_d': 'Guitarra e baixo',
                'resposta': 'B'
            },
            {
                'pergunta': 'Qual a origem da expressão "quilombo"?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Língua banto',
                'opcao_b': 'Tupi-guarani',
                'opcao_c': 'Português arcaico',
                'opcao_d': 'Língua yorubá',
                'resposta': 'A'
            },
            {
                'pergunta': 'O que representa a Festa de São Benedito?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'A colheita',
                'opcao_b': 'A resistência cultural afro-brasileira',
                'opcao_c': 'O início do inverno',
                'opcao_d': 'A fundação do estado',
                'resposta': 'B'
            },
            # Fase 3 – A Voz da Ancestralidade
            {
                'pergunta': 'Qual a importância do congado para os povos afrodescendentes?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Celebração religiosa',
                'opcao_b': 'Manutenção das tradições culturais',
                'opcao_c': 'Resistência política',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'Como a musicalidade está presente nas manifestações quilombolas?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Como forma de oração',
                'opcao_b': 'Como expressão cultural',
                'opcao_c': 'Como registro histórico',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'Como a dança funciona como resistência cultural nos quilombos?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Preservando tradições africanas',
                'opcao_b': 'Criando identidade coletiva',
                'opcao_c': 'Transmitindo conhecimentos',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            # Fase 4 – Boss: A Mãe da Memória Quilombola
            {
                'pergunta': 'Quais os principais elementos culturais dos quilombos mato-grossenses?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Dança e música',
                'opcao_b': 'Culinária',
                'opcao_c': 'Religiosidade',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            
            # Ato III — Ecos do Cerrado (Tradições e Natureza)
            # Fase 1 – Caminho das Pedras Cantantes
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
                'pergunta': 'Qual desses elementos está presente no cerrado?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Buriti',
                'opcao_b': 'Araucária',
                'opcao_c': 'Mangue',
                'opcao_d': 'Cacto gigante',
                'resposta': 'A'
            },
            {
                'pergunta': 'Qual o bioma predominante no centro do estado?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Amazônia',
                'opcao_b': 'Pantanal',
                'opcao_c': 'Cerrado',
                'opcao_d': 'Caatinga',
                'resposta': 'C'
            },
            # Fase 2 – Mistérios da Serra
            {
                'pergunta': 'A Serra do Roncador é conhecida por quê?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Sua biodiversidade',
                'opcao_b': 'Seus mistérios e lendas',
                'opcao_c': 'Sua altura',
                'opcao_d': 'Sua mineração',
                'resposta': 'B'
            },
            {
                'pergunta': 'Qual lenda fala de um ser gigante que abre caminhos?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Mãe-do-Ouro',
                'opcao_b': 'Saci-Pererê',
                'opcao_c': 'Curupira',
                'opcao_d': 'Anhangá',
                'resposta': 'C'
            },
            {
                'pergunta': 'O que é "botina de ouro" no folclore?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Um tesouro escondido',
                'opcao_b': 'Uma lenda sobre um garimpeiro',
                'opcao_c': 'Um tipo de calçado tradicional',
                'opcao_d': 'Uma dança folclórica',
                'resposta': 'B'
            },
            # Fase 3 – O Espantalho do Esquecimento
            {
                'pergunta': 'Qual a função da viola de cocho na cultura musical mato-grossense?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Acompanhamento de danças',
                'opcao_b': 'Solos em festivais',
                'opcao_c': 'Rituais religiosos',
                'opcao_d': 'Educação musical',
                'resposta': 'A'
            },
            {
                'pergunta': 'Em que ocasiões o siriri e o cururu são tradicionalmente apresentados?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Festas juninas',
                'opcao_b': 'Festas religiosas',
                'opcao_c': 'Casamentos',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'O que diferencia o rasqueado mato-grossense de outros ritmos brasileiros?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Seu ritmo acelerado',
                'opcao_b': 'A mistura de influências indígenas, africanas e europeias',
                'opcao_c': 'O uso de instrumentos únicos',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            # Fase 4 – Boss: O Espantalho do Esquecimento
            {
                'pergunta': 'Como a oralidade e a música garantem a continuidade da identidade cultural do cerrado?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Transmitindo conhecimentos tradicionais',
                'opcao_b': 'Preservando a língua local',
                'opcao_c': 'Mantendo vivas as histórias e lendas',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            
            # Ato IV — O Coração do Pantanal (Gastronomia, Água e Mistério)
            # Fase 1 – Caminho das Águas
            {
                'pergunta': 'Qual prato é feito com peixe e muito comum na região?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Moqueca',
                'opcao_b': 'Pacu assado',
                'opcao_c': 'Caldo de piranha',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'O que é mojica de pintado?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Um tipo de pesca',
                'opcao_b': 'Um prato feito com peixe pintado',
                'opcao_c': 'Uma dança tradicional',
                'opcao_d': 'Um instrumento musical',
                'resposta': 'B'
            },
            {
                'pergunta': 'O pequi é usado em qual tipo de preparo?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Arroz com pequi',
                'opcao_b': 'Licor de pequi',
                'opcao_c': 'Frango com pequi',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            },
            # Fase 2 – Festa do Rio
            {
                'pergunta': 'Qual instrumento é usado no rasqueado?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Violão',
                'opcao_b': 'Viola de cocho',
                'opcao_c': 'Guitarra',
                'opcao_d': 'Flauta',
                'resposta': 'B'
            },
            {
                'pergunta': 'Qual a origem do termo "pantaneiro"?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Do modo de vida no Pantanal',
                'opcao_b': 'De uma tribo indígena',
                'opcao_c': 'De um tipo de peixe',
                'opcao_d': 'De uma planta local',
                'resposta': 'A'
            },
            {
                'pergunta': 'Que animal é símbolo do Pantanal?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Onça-pintada',
                'opcao_b': 'Tuiuiú',
                'opcao_c': 'Arara-azul',
                'opcao_d': 'Jacaré',
                'resposta': 'B'
            },
            # Fase 3 – Encontro das Marés
            {
                'pergunta': 'Qual o papel do barco nas festas tradicionais pantaneiras?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Transporte de participantes',
                'opcao_b': 'Palco para apresentações',
                'opcao_c': 'Local para preparo de comida',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'Quais alimentos típicos são preparados durante as celebrações ribeirinhas no Pantanal?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Peixes assados',
                'opcao_b': 'Arroz com pequi',
                'opcao_c': 'Carne seca',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'Como os ciclos do rio afetam o modo de vida local?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Determinando épocas de pesca',
                'opcao_b': 'Influenciando a agricultura',
                'opcao_c': 'Definindo rotas de transporte',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            },
            # Fase 4 – Boss: O Monstro das Águas Profundas
            {
                'pergunta': 'Como a cultura pantaneira une ecologia, misticismo e tradição?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Através de lendas sobre a natureza',
                'opcao_b': 'Por práticas sustentáveis tradicionais',
                'opcao_c': 'Na relação harmoniosa com o ambiente',
                'opcao_d': 'Todas as anteriores',
                'resposta': 'D'
            }
        ]
        
        inserir = Inserir_perguntas(self.db.db_name)
        return inserir.inserir_perguntas(todas_perguntas)

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