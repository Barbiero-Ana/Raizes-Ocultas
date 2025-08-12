import os
from database.criar_banco import Funcoes_DataBase
import sqlite3

class CadastrarTurma:
    def __init__(self, id_usuario):
        self.id_usuario = id_usuario
        # Garante que o diretório database existe
        if not os.path.exists("database"):
            os.makedirs("database")
            
        db_path = os.path.join("database", "raizes_ocultas.db")
        self.db = Funcoes_DataBase(db_path)
        
        # Verifica se o banco existe e tem as tabelas necessárias
        if not self.verificar_banco_pronto():
            raise Exception("Banco de dados não está pronto para uso")
    
    def verificar_banco_pronto(self):
        """Verifica se o banco de dados existe e tem a tabela Turma"""
        try:
            conn = self.db.db.conectar_no_banco()
            if conn is None:
                return False
                
            with conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Turma'")
                return cursor.fetchone() is not None
                
        except Exception as e:
            print(f"Erro ao verificar banco: {e}")
            return False
        finally:
            self.db.db.fechar_conexao()

    def validar_dados_cadastro_turma(self, nome: str, quantidade: int, serie: str):
        if not nome.strip():
            return False, "Nome é obrigatório"
        
        if not quantidade or quantidade < 1:
            return False, "Quantidade de alunos é obrigatória"
        
        if not serie.strip():
            return False, "Série é obrigatória"

        return True, "Dados válidos"
    
    def cadastrar_turma(self, nome: str, quantidade: int, serie: str):
        """Cadastra uma nova turma associada ao usuário"""
        # Valores padrão para nova turma
        vida_max = 3
        vida_atual = 3
        pontos_acerto = 0
        pontos_erro = 0
        vivo = True
        
        try:
            # Valida os dados primeiro
            valido, msg = self.validar_dados_cadastro_turma(nome, quantidade, serie)
            if not valido:
                return False, msg, None

            # Inserir no banco com todos os campos necessários
            turma_id = self.db.inserir_turma(
                nome.strip(),
                quantidade,
                serie,
                vida_max,
                vida_atual,
                pontos_acerto,
                pontos_erro,
                vivo,
                self.id_usuario  # Usa o id_usuario armazenado
            )

            if turma_id:
                return True, "Turma cadastrada com sucesso!", turma_id
            else:
                return False, "Erro ao inserir turma no banco", None
            
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                return False, "Este nome para Turma já está sendo usado", None
            else:
                return False, f"Erro de integridade: {str(e)}", None  
        except Exception as e:
            return False, f"Erro ao cadastrar turma: {str(e)}", None
    
    def listar_turmas_usuario(self, id_usuario: int) -> list:
        """Retorna todas as turmas criadas por um usuário específico"""
        try:
            conn = self.db.db.conectar_no_banco()
            if conn is None:
                return []
                
            with conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id_turma,nome_turma,quantidade_turma,serie_turma FROM Turma
                        WHERE id_usuario = ?
                        ORDER BY id_turma DESC
                """, (id_usuario,))
                
                return cursor.fetchall()
                
        except Exception as e:
            print(f"Erro ao listar turmas: {e}")
            return []
        finally:
            self.db.db.fechar_conexao()        
    @staticmethod
    def cadastrar_turma_simples(nome: str, quantidade: int, serie: str, id_usuario: int) -> tuple:
        """Método estático simplificado para cadastro de turma"""
        cadastro = CadastrarTurma(id_usuario)
        return cadastro.cadastrar_turma(nome, quantidade, serie)
        
    def get_estatisticas_turma(self, id_turma):
        conn = sqlite3.connect("database/raizes_ocultas.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_perguntas,
                SUM(acertou) as acertos,
                COUNT(*) - SUM(acertou) as erros,
                AVG(tempo_resposta) as tempo_medio
            FROM Dados_do_jogador
            WHERE id_turma = ?
        """, (id_turma,))
        
        resultado = cursor.fetchone()
        conn.close()
        
        if resultado:
            return {
                'total': resultado[0],
                'acertos': resultado[1],
                'erros': resultado[2],
                'tempo_medio': resultado[3] or 0
            }
        return None