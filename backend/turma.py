
class Turma:
    def __init__(self,nome,vida,acertos,erros, quantidade,serie
                 ,id_usuario = None, id_turma = None):
        self.turma = id_turma
        self.nome = nome
        self.quantidade_turma = quantidade
        self.serie_turma = serie
        self.vida_max = vida
        self.vida_atual = vida
        self.pontos_acertos = acertos
        self.pontos_erros = erros
        self.usuario = id_usuario
   
    

