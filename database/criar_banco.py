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
        """Verifica se o banco de dados já existe"""
        try:
            return os.path.exists(self.db_name)  # Corrigido: self.db_name em vez de self.db.db_name
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
                #-----------------Tabela do Professor ---------------------------
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
                #------------------- Tabela da Turma ------------------
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
                #----------------- Tabela Inimigos --------------------------
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
                #-------------------- Tabela dos Boss ------------------------
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
                #------------- Tabela pra salvar o progresso das Turmas-------
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
                #------------ Tabela para salvar as questões -----------------
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
                #---------------- Tabela das Respostas das Turmas ---------------
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS Time_Respostas(
                    id_tempo_resposta INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_usuario INTEGER NOT NULL, 
                    id_pergunta INTEGER NOT NULL,
                    tempo_resposta INTEGER NOT NULL,  # Alterado de INTERVAL para INTEGER
                    time_out BOOLEAN DEFAULT 0,
                    FOREIGN KEY(id_usuario) REFERENCES Usuario(id_usuario) ON DELETE CASCADE
                )
                """)
                
            return True
        except Error as e:
            print(f"Erro ao criar tabelas: {e}")
            return False
#VIEW não é uma tabela no banco ela é como uma 

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
    
    def inserir_cliente(self, nome, email, senha):
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
    
    def inserir_perguntas_padrao(self):
        """Insere as perguntas padrão no banco de dados"""
        perguntas_exemplo = [
            # Ato I — Raízes Esquecidas (Cultura Indígena)
            # Fase 1 - Os Guardiões da Floresta
            {
                'pergunta': 'Qual destes animais é sagrado para o povo Bororo?',
                'classe_pergunta': 5,  # Cultura
                'dificuldade_pergunta': 1,  # Fácil
                'opcao_a': 'Onça-pintada',
                'opcao_b': 'Arara',
                'opcao_c': 'Jaburu',
                'opcao_d': 'Tatu',
                'resposta': 'C'  # Jaburu
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
                'opcao_b': 'Povo unido',
                'opcao_c': 'Água limpa',
                'opcao_d': 'Terra fértil',
                'resposta': 'C'
            },
            
            # Fase 2 - Saberes da Terra
            {
                'pergunta': 'Que povo indígena habita o Parque Nacional do Xingu?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,  # Média
                'opcao_a': 'Guarani',
                'opcao_b': 'Yanomami',
                'opcao_c': 'Kamayurá',
                'opcao_d': 'Tupi',
                'resposta': 'C'
            },
            {
                'pergunta': 'Qual instrumento é tradicional em rituais indígenas mato-grossenses?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Violão',
                'opcao_b': 'Flauta',
                'opcao_c': 'Maracá',
                'opcao_d': 'Tambor',
                'resposta': 'C'
            },
            {
                'pergunta': 'O que representa o urucum na cultura ancestral?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Alimento sagrado',
                'opcao_b': 'Medicina tradicional',
                'opcao_c': 'Pigmento para pintura',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            
            # Fase 3 - O Espírito da Floresta
            {
                'pergunta': 'O que significa o uso de grafismos corporais nas culturas indígenas do Mato Grosso?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Proteção espiritual',
                'opcao_b': 'Identidade étnica',
                'opcao_c': 'Comunicação não-verbal',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            {
                'pergunta': 'Qual a função do pajé nas aldeias?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Líder espiritual',
                'opcao_b': 'Curandeiro',
                'opcao_c': 'Conselheiro',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            {
                'pergunta': 'Qual é o papel da oralidade na preservação da cultura indígena?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 3,  # Difícil
                'opcao_a': 'Transmitir conhecimentos',
                'opcao_b': 'Preservar histórias',
                'opcao_c': 'Manter tradições',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            
            # Fase 4 - Boss: O Guardião da Neblina
            {
                'pergunta': 'Como os povos originários interpretam o tempo e os ciclos naturais?',
                'classe_pergunta': 5,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Como eventos aleatórios',
                'opcao_b': 'Como um relógio linear',
                'opcao_c': 'Como ciclos sagrados interconectados',
                'opcao_d': 'Como fenômenos científicos',
                'resposta': 'C'
            },
            
            # Ato II — Caminhos Ancestrais (Quilombos, Danças e Resistência)
            # Fase 1 - Batida dos Tambores
            {
                'pergunta': 'Qual dança é tradicional em festas de rua mato-grossenses?',
                'classe_pergunta': 4,  # Arte
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
            
            # Fase 2 - Cores e Ritmos Quilombolas
            {
                'pergunta': 'Que instrumentos são usados no siriri?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Violão e flauta',
                'opcao_b': 'Tamborim e pandeiro',
                'opcao_c': 'Moquém e ganzá',
                'opcao_d': 'Guitarra e bateria',
                'resposta': 'C'
            },
            {
                'pergunta': 'Qual a origem da expressão "quilombo"?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Do tupi, significa "esconderijo"',
                'opcao_b': 'Do banto, significa "acampamento"',
                'opcao_c': 'Do iorubá, significa "resistência"',
                'opcao_d': 'Do guarani, significa "liberdade"',
                'resposta': 'B'
            },
            {
                'pergunta': 'O que representa a Festa de São Benedito?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'A colheita',
                'opcao_b': 'A resistência cultural afro-brasileira',
                'opcao_c': 'O início do inverno',
                'opcao_d': 'A fundação de Cuiabá',
                'resposta': 'B'
            },
            
            # Fase 3 - A Voz da Ancestralidade
            {
                'pergunta': 'Qual a importância do congado para os povos afrodescendentes?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Celebração religiosa',
                'opcao_b': 'Manutenção de tradições',
                'opcao_c': 'Forma de resistência',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            {
                'pergunta': 'Como a musicalidade está presente nas manifestações quilombolas?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Apenas em festas',
                'opcao_b': 'Como forma de registro histórico',
                'opcao_c': 'No cotidiano e rituais',
                'opcao_d': 'Raramente é utilizada',
                'resposta': 'C'
            },
            {
                'pergunta': 'Como a dança funciona como resistência cultural nos quilombos?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Preservando movimentos ancestrais',
                'opcao_b': 'Transmitindo histórias de luta',
                'opcao_c': 'Fortalecendo a identidade comunitária',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            
            # Fase 4 - Boss: A Mãe da Memória Quilombola
            {
                'pergunta': 'Quais os principais elementos culturais dos quilombos mato-grossenses?',
                'classe_pergunta': 4,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Dança e música',
                'opcao_b': 'Culinária e medicina tradicional',
                'opcao_c': 'Narrativas orais e religiosidade',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            },
            
            # Ato III — Ecos do Cerrado (Tradições e Natureza)
            # Fase 1 - Caminho das Pedras Cantantes
            {
                'pergunta': 'O que é rasqueado?',
                'classe_pergunta': 3,  # Comida/Arte
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
                'opcao_b': 'Cactos gigantes',
                'opcao_c': 'Pinheiros',
                'opcao_d': 'Cocais',
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
            
            # Fase 2 - Mistérios da Serra
            {
                'pergunta': 'A Serra do Roncador é conhecida por quê?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Tesouros escondidos',
                'opcao_b': 'Mistérios e lendas',
                'opcao_c': 'Vegetação única',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
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
                'opcao_a': 'Calçado de bandeirantes',
                'opcao_b': 'Lenda sobre riquezas escondidas',
                'opcao_c': 'Artefato indígena',
                'opcao_d': 'Instrumento musical',
                'resposta': 'B'
            },
            
            # Fase 3 - O Espantalho do Esquecimento
            {
                'pergunta': 'Qual a função da viola de cocho na cultura musical mato-grossense?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Acompanhamento de danças',
                'opcao_b': 'Rituais religiosos',
                'opcao_c': 'Contação de histórias',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            {
                'pergunta': 'Em que ocasiões o siriri e o cururu são tradicionalmente apresentados?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Festas juninas',
                'opcao_b': 'Rituais de colheita',
                'opcao_c': 'Celebrações religiosas',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            {
                'pergunta': 'O que diferencia o rasqueado mato-grossense de outros ritmos brasileiros?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'O uso da viola de cocho',
                'opcao_b': 'A influência indígena e africana',
                'opcao_c': 'O ritmo característico',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            
            # Fase 4 - Boss: O Espantalho do Esquecimento
            {
                'pergunta': 'Como a oralidade e a música garantem a continuidade da identidade cultural do cerrado?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Transmitindo saberes tradicionais',
                'opcao_b': 'Preservando histórias locais',
                'opcao_c': 'Fortalecendo laços comunitários',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            },
            
            # Ato IV — O Coração do Pantanal (Gastronomia, Água e Mistério)
            # Fase 1 - Caminho das Águas
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
                'opcao_a': 'Um tipo de artesanato',
                'opcao_b': 'Um prato à base de peixe',
                'opcao_c': 'Uma dança típica',
                'opcao_d': 'Uma lenda pantaneira',
                'resposta': 'B'
            },
            {
                'pergunta': 'O pequi é usado em qual tipo de preparo?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 1,
                'opcao_a': 'Arroz com pequi',
                'opcao_b': 'Licor',
                'opcao_c': 'Frango com pequi',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            },
            
            # Fase 2 - Festa do Rio
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
                'opcao_a': 'Habitante do pantanal',
                'opcao_b': 'Trabalhador rural',
                'opcao_c': 'Pescador tradicional',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'Que animal é símbolo do Pantanal?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Tuiuiú',
                'opcao_b': 'Onça-pintada',
                'opcao_c': 'Ariranha',
                'opcao_d': 'Capivara',
                'resposta': 'A'
            },
            
            # Fase 3 - Encontro das Marés
            {
                'pergunta': 'Qual o papel do barco nas festas tradicionais pantaneiras?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Transporte de participantes',
                'opcao_b': 'Palco flutuante',
                'opcao_c': 'Elemento decorativo',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            },
            {
                'pergunta': 'Quais alimentos típicos são preparados durante as celebrações ribeirinhas no Pantanal?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 2,
                'opcao_a': 'Peixes assados',
                'opcao_b': 'Arroz carreteiro',
                'opcao_c': 'Sobá',
                'opcao_d': 'A e B',
                'resposta': 'D'
            },
            {
                'pergunta': 'Como os ciclos do rio afetam o modo de vida local?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Determinam épocas de pesca',
                'opcao_b': 'Influenciam a agricultura',
                'opcao_c': 'Regulam festividades',
                'opcao_d': 'Todos os anteriores',
                'resposta': 'D'
            },
            
            # Fase 4 - Boss: O Monstro das Águas Profundas
            {
                'pergunta': 'Como a cultura pantaneira une ecologia, misticismo e tradição?',
                'classe_pergunta': 3,
                'dificuldade_pergunta': 3,
                'opcao_a': 'Através de lendas sobre a natureza',
                'opcao_b': 'Nos rituais ligados aos rios',
                'opcao_c': 'Na culinária baseada em ciclos naturais',
                'opcao_d': 'Todas as alternativas',
                'resposta': 'D'
            }

        ]
        
        inserir = Inserir_perguntas(self.db.db_name)
        return inserir.inserir_perguntas(perguntas_exemplo)

    
class Logica_Login:
        def validar_usuario(self, email, password_hash):
            conn = self.get_connection()
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        SELECT * FROM usuarios 
                        WHERE email = ? AND password = ?
                    """, (email, password_hash))
                    return cursor.fetchone()
            except Error as e:
                print(f"Erro ao validar usuário: {e}")
                return None
        
        def obter_cliente_por_email(self,email):
            conn = self.get_connection()
            try:
                with conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT * FROM Usuarios WHERE email = ?",(email))
                    return cursor.fetchone()
            except Error as e:
                print(f"Erro ao obter usuario por E-mail: {e}")
                raise
            finally:
                self.close_connection()


class Inserir_perguntas:
    def __init__(self, db_name):
        self.db = Database(db_name)
        
    def inserir_perguntas(self, lista_perguntas):
        """
        Insere múltiplas perguntas na tabela Perguntas
        
        Args:
            lista_perguntas (list): Lista de dicionários com as perguntas
            
        Returns:
            tuple: (bool sucesso, str mensagem)
        """
        conn = self.db.conectar_no_banco()
        if conn is None:
            return False, "Erro ao conectar ao banco"
        
        try:
            with conn:
                cursor = conn.cursor()
                
                # Preparar os dados para inserção
                dados_insercao = []
                for pergunta in lista_perguntas:
                    # Validar estrutura básica
                    campos_obrigatorios = [
                        'pergunta', 'classe_pergunta', 'dificuldade_pergunta',
                        'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'resposta'
                    ]
                    
                    if not all(campo in pergunta for campo in campos_obrigatorios):
                        return False, f"Estrutura inválida na pergunta: {pergunta}"
                    
                    # Validar valores específicos
                    if pergunta['classe_pergunta'] not in (3, 4, 5):
                        return False, f"Classe inválida na pergunta: {pergunta['pergunta']}"
                    
                    if pergunta['dificuldade_pergunta'] not in (1, 2, 3, 4):
                        return False, f"Dificuldade inválida na pergunta: {pergunta['pergunta']}"
                    
                    if pergunta['resposta'].upper() not in ('A', 'B', 'C', 'D'):
                        return False, f"Resposta inválida na pergunta: {pergunta['pergunta']}"
                    
                    # Adicionar à lista de inserção
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
                
                # Executar inserção em lote
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

class Inserir_perguntas:
    def __init__(self, db_name):
        self.db = Database(db_name)
        
    def inserir_perguntas(self, lista_perguntas):
        """
        Insere múltiplas perguntas na tabela Perguntas
        
        Args:
            lista_perguntas (list): Lista de dicionários com as perguntas
            
        Returns:
            tuple: (bool sucesso, str mensagem)
        """
        conn = self.db.conectar_no_banco()
        if conn is None:
            return False, "Erro ao conectar ao banco"
        
        try:
            with conn:
                cursor = conn.cursor()
                
                # Preparar os dados para inserção
                dados_insercao = []
                for pergunta in lista_perguntas:
                    # Validar estrutura básica
                    campos_obrigatorios = [
                        'pergunta', 'classe_pergunta', 'dificuldade_pergunta',
                        'opcao_a', 'opcao_b', 'opcao_c', 'opcao_d', 'resposta'
                    ]
                    
                    if not all(campo in pergunta for campo in campos_obrigatorios):
                        return False, f"Estrutura inválida na pergunta: {pergunta}"
                    
                    # Validar valores específicos
                    if pergunta['classe_pergunta'] not in (3, 4, 5):
                        return False, f"Classe inválida na pergunta: {pergunta['pergunta']}"
                    
                    if pergunta['dificuldade_pergunta'] not in (1, 2, 3, 4):
                        return False, f"Dificuldade inválida na pergunta: {pergunta['pergunta']}"
                    
                    if pergunta['resposta'].upper() not in ('A', 'B', 'C', 'D'):
                        return False, f"Resposta inválida na pergunta: {pergunta['pergunta']}"
                    
                    # Adicionar à lista de inserção
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
                
                # Executar inserção em lote
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
    # Definir o caminho do banco de dados
    pasta_db = "database"
    nome_banco = "raizes_ocultas.db"
    
    # Criar a pasta se não existir
    if not os.path.exists(pasta_db):
        os.makedirs(pasta_db)
        print(f"Pasta '{pasta_db}' criada com sucesso!")
    
    # Caminho completo do banco de dados
    caminho_completo = os.path.join(pasta_db, nome_banco)
    
    # Inicializar o banco com o caminho completo
    db = Database(caminho_completo)
    funcoes = Funcoes_DataBase(caminho_completo)
    
    # Verificar se o banco existe e se as tabelas estão criadas
    if not db.banco_existe():
        print("Criando banco de dados e tabelas...")
        sucesso = db.criar_tabelas()
        
        if sucesso:
            print("Tabelas criadas com sucesso!")
            
            # Agora inserir as perguntas
            print("Inserindo perguntas padrão...")
            sucesso, mensagem = funcoes.inserir_perguntas_padrao()
            print(mensagem)
            
            if not sucesso:
                print("Ocorreu um erro ao inserir as perguntas")
        else:
            print("Erro ao criar tabelas.")
            exit(1)
    else:
        print("Banco de dados já existe. Verificando se as perguntas já foram inseridas...")
        
        # Verificar se já existem perguntas no banco
        conn = db.conectar_no_banco()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Perguntas")
            count = cursor.fetchone()[0]
            if count == 0:
                print("Inserindo perguntas padrão...")
                sucesso, mensagem = funcoes.inserir_perguntas_padrao()
                print(mensagem)
                if not sucesso:
                    print("Ocorreu um erro ao inserir as perguntas")
            else:
                print(f"O banco já contém {count} perguntas. Nada a fazer.")
        except Error as e:
            print(f"Erro ao verificar perguntas existentes: {e}")
        finally:
            db.fechar_conexao()