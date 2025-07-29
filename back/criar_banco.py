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
                CREATE TABLE IF NOT EXISTS usuario(
                    id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_usuario TEXT NOT NULL,
                    email TEXT NOT NULL,
                    cripto_senha TEXT NOT NULL,
                    deletado BOOLEAN DEFAULT 0,
                    data_delecao TEXT
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS personagens(
                    id_personagem INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome_personagem TEXT NOT NULL,
                    vida_max INTEGER NOT NULL,
                    vida_atual INTEGER NOT NULL,
                    pontos_acerto INTEGER NOT NULL,
                    pontos_erro INTEGER NOT NULL,
                    vivo BOOLEAN DEFAULT 0,
                    id_usuario INTEGER NOT NULL,
                    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS inimigos(
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
                CREATE TABLE IF NOT EXISTS boss(
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
                    id_personagem INTEGER NOT NULL,
                    id_boss INTEGER NOT NULL,
                    flag_progresso BOOLEAN DEFAULT 0,
                    FOREIGN KEY (id_personagem) REFERENCES personagens(id_personagem) ON DELETE CASCADE,
                    FOREIGN KEY (id_boss) REFERENCES boss(id_boss) ON DELETE CASCADE
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS perguntas_e_respostas(
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
        
    def salvar_personagem(self, personagem):

        if not self.validar_personagem(personagem):
            return False, "Dados do personagem inválidos"
            
        conn = self.db.conectar_no_banco()
        if conn is None:
            return False, "Erro ao conectar ao banco"
            
        try:
            with conn:
                cursor = conn.cursor()
                
                dados = (
                    personagem.nome_personagem,
                    personagem.vida_max,
                    personagem.vida_atual,
                    personagem.experiencia,
                    1 if getattr(personagem, 'vivo', True) else 0,
                    personagem.id_usuario
                )
                
                if hasattr(personagem, 'id_personagem') and personagem.id_personagem:
                    # Atualização
                    cursor.execute("""
                        UPDATE personagens SET
                            nome_personagem = ?,
                            vida_max = ?,
                            vida_atual = ?,
                            experiencia = ?,
                            vivo = ?
                        WHERE id_personagem = ? AND id_usuario = ?
                    """, dados + (personagem.id_personagem, personagem.id_usuario))
                    
                    if cursor.rowcount == 0:
                        return False, "Personagem não encontrado ou não pertence ao usuário"
                        
                    return True, "Personagem atualizado com sucesso"
                else:
                    # Inserção
                    cursor.execute("""
                        INSERT INTO personagens (
                            nome_personagem, vida_max, vida_atual, personagem_selecionado,
                            vivo, id_usuario
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, dados)
                    
                    personagem.id_personagem = cursor.lastrowid
                    return True, "Personagem criado com sucesso"
                    
        except Error as e:
            print(f"Erro ao salvar personagem: {e}")
            return False, f"Erro no banco de dados: {e}"
        finally:
            self.db.fechar_conexao()
    
    def validar_personagem(self, personagem):
        """Valida os dados básicos do personagem"""
        required_attrs = [
            'nome_personagem', 'vida_max', 'vida_atual', 
            'personagem_selecionado', 'id_usuario'
        ]
        
        for attr in required_attrs:
            if not hasattr(personagem, attr):
                print(f"Atributo faltando: {attr}")
                return False
                
        # Validações adicionais
        if personagem.vida_atual > personagem.vida_max:
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
# (continuando o código anterior...)

# class Funcoes_DataBase:
#     def __init__(self, db_name):
#         self.db = Database(db_name)
        
#     def salvar_personagem(self, personagem):
#         # ... [mesmo conteúdo anterior] ...
#         return True
    
#     def validar_personagem(self, personagem):
#         # ... [mesmo conteúdo anterior] ...
#         return True
    
#     def limpar_usuarios_deletados(self, dias=30):
#         # ... [mesmo conteúdo anterior] ...
#         return True

#     # def inserir_perguntas_padrao(self):
#     #     perguntas = [
#     #         # Fáceis
#     #         ("Qual é o peixe mais tradicional da culinária mato-grossense?", 3, 1, "Tilápia", "Tambaqui", "Pacu", "Piranha", "C"),
#     #         ("O que é 'Maria Isabel' na culinária de Mato Grosso?", 3, 1, "Um tipo de peixe assado", "Um bolo típico", "Arroz com carne seca", "Um suco regional", "C"),
#     #         ("A 'farofa de banana' é feita com qual tipo de banana?", 3, 1, "Banana-da-terra", "Banana-nanica", "Banana-prata", "Banana-maçã", "A"),
#     #         # Médias
#     #         ("Qual desses ingredientes é típico no preparo do 'moquém', prato indígena tradicional?", 3, 2, "Frango grelhado", "Peixe defumado", "Milho assado", "Feijão preto", "B"),
#     #         ("A 'chipa', muito consumida em Mato Grosso, tem origem em qual país vizinho?", 3, 2, "Bolívia", "Argentina", "Paraguai", "Uruguai", "C"),
#     #         ("Qual desses pratos é comum em festas típicas no interior de Mato Grosso?", 3, 2, "Feijoada carioca", "Galinhada", "Pirão de peixe", "Sushi", "C"),
#     #         ("A bebida 'guaraná ralado' é tradicionalmente preparada com o guaraná em qual forma?", 3, 2, "Em pó industrializado", "Em bastão ralado na hora", "Em cápsulas", "Em folhas fervidas", "B"),
#     #         ("O que acompanha tradicionalmente o arroz com pequi em algumas regiões de Mato Grosso?", 3, 2, "Frango caipira", "Pão de queijo", "Costelinha suína", "Ovos mexidos", "A"),
#     #         ("O que diferencia o 'quibebe' mato-grossense de outras versões do prato?", 3, 2, "Uso de abóbora cabotiá", "Uso de leite de coco", "É doce, não salgado", "É assado, não cozido", "A"),
#     #         # Difícil
#     #         ("Qual é a influência culinária predominante nas receitas típicas da região de Vila Bela da Santíssima Trindade (MT)?", 3, 3, "Italiana", "Árabe", "Africana", "Alemã", "C")
#     #     ]

#     #     conn = self.db.conectar_no_banco()
#     #     if conn is None:
#     #         print("Erro ao conectar para inserir perguntas.")
#     #         return

#     #     try:
#     #         with conn:
#     #             cursor = conn.cursor()
#     #             cursor.executemany("""
#     #                 INSERT INTO perguntas_e_respostas (
#     #                     pergunta, classe_pergunta, dificuldade_pergunta,
#     #                     opcao_a, opcao_b, opcao_c, opcao_d, resposta
#     #                 ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     #             """, perguntas)
#     #             print(f"{cursor.rowcount} perguntas inseridas com sucesso.")
#     #     except Error as e:
#     #         print(f"Erro ao inserir perguntas: {e}")
#     #     finally:
#     #         self.db.fechar_conexao()


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
