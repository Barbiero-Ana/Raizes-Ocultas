import tkinter as tk
from tkinter import messagebox
import threading
import sqlite3
import os
import random
import time


# Configurações do banco de dados
pasta_db = "database"
nome_banco = "raizes_ocultas.db"
caminho_completo = os.path.join(pasta_db, nome_banco)

class QuizGame:
    def __init__(self, root, nivel="1-1"):
        self.root = root
        self.root.title("Quiz Game")
        self.root.geometry("600x400")
        self.pergunta_atual = 0
        self.pontuacao = 0
        self.vidas = 3
        self.timer = None
        self.tempo_restante = 0
        self.nivel = nivel
        self.respostas_corretas_consecutivas = 0
        self.tempo_respostas = []  # Armazena o tempo gasto em cada resposta
        self.bonus_disponivel = False
        
        # Parse do nível para obter dificuldade e classe
        self.dificuldade, self.classe = map(int, nivel.split('-'))
        
        # Carrega as perguntas do banco de dados
        self.perguntas = self.carregar_perguntas_do_banco()
        
        # Configura os tempos baseados na dificuldade
        self.TEMPOS = self.definir_tempos()
        
        # Elementos da interface
        self.label_pergunta = tk.Label(root, text="", wraplength=500, font=("Arial", 14))
        self.label_pergunta.pack(pady=20)

        self.botoes = []
        for i in range(4):
            btn = tk.Button(root, text="", width=25, font=("Arial", 12), command=lambda i=i: self.verificar_resposta(i))
            btn.pack(pady=5)
            self.botoes.append(btn)

        self.label_timer = tk.Label(root, text="", font=("Arial", 12))
        self.label_timer.pack(pady=10)

        self.label_vidas = tk.Label(root, text="Vidas: 3", font=("Arial", 12))
        self.label_vidas.pack()

        if self.perguntas:
            self.carregar_pergunta()
        else:
            messagebox.showerror("Erro", "Nenhuma pergunta encontrada para este nível!")
            self.root.quit()

    def carregar_perguntas_do_banco(self):
        """Carrega perguntas do banco de dados baseado no nível selecionado"""
        try:
            conn = sqlite3.connect(caminho_completo)
            cursor = conn.cursor()
            
            # Busca perguntas com a dificuldade e classe especificadas
            # No método carregar_perguntas_do_banco(), modifique a query SQL para:
            cursor.execute("""
                SELECT pergunta, opcao_a, opcao_b, opcao_c, opcao_d, resposta 
                FROM Perguntas 
                WHERE dificuldade_pergunta = ? AND classe_pergunta = ?
                ORDER BY RANDOM()
                LIMIT 10  # Limita a 10 perguntas por jogo
            """, (self.dificuldade, self.classe))
                        
            perguntas = []
            for row in cursor.fetchall():
                perguntas.append({
                    "pergunta": row[0],
                    "opcoes": [row[1], row[2], row[3], row[4]],
                    "resposta": row[5]  # A, B, C ou D
                })
            
            conn.close()
            return perguntas
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar perguntas: {str(e)}")
            return []

    def definir_tempos(self):
        """Define os tempos baseados na dificuldade da pergunta"""
        # Quanto maior a dificuldade, menos tempo o jogador tem
        tempos_base = {
            1: 120,  # Fácil - mais tempo
            2: 90,
            3: 60,
            4: 30    # Difícil - menos tempo
        }
        return [tempos_base[self.dificuldade]] * len(self.perguntas)

    def carregar_pergunta(self):
        if self.pergunta_atual >= len(self.perguntas):
            messagebox.showinfo("Parabéns!", f"Você completou o quiz! Pontuação: {self.pontuacao}")
            self.root.quit()
            return

        p = self.perguntas[self.pergunta_atual]
        self.label_pergunta.config(text=f"{self.pergunta_atual+1}. {p['pergunta']}")
        
        # Mapeia as opções para os botões
        opcoes_mapeadas = {
            'A': p['opcoes'][0],
            'B': p['opcoes'][1],
            'C': p['opcoes'][2],
            'D': p['opcoes'][3]
        }
        
        for i, letra in enumerate(['A', 'B', 'C', 'D']):
            self.botoes[i].config(text=opcoes_mapeadas[letra])

        self.tempo_restante = self.TEMPOS[self.pergunta_atual]
        self.atualizar_timer()

    def atualizar_timer(self):
        self.label_timer.config(text=f"Tempo restante: {self.tempo_restante} segundos")
        if self.tempo_restante <= 0:
            self.perde_vida("Tempo esgotado!")
            return

        self.tempo_restante -= 1
        self.timer = self.root.after(1000, self.atualizar_timer)

    def verificar_resposta(self, indice):
        self.root.after_cancel(self.timer)
        
        # Obtém a letra da opção selecionada (A, B, C ou D)
        letra_selecionada = ['A', 'B', 'C', 'D'][indice]
        resposta_correta = self.perguntas[self.pergunta_atual]['resposta']
        
        if letra_selecionada == resposta_correta:
            self.pontuacao += 1
            messagebox.showinfo("Correto!", "Você acertou!")
        else:
            self.perde_vida("Resposta incorreta!")
            return

        self.pergunta_atual += 1
        self.carregar_pergunta()

    
    def verificar_resposta(self, indice):
        self.root.after_cancel(self.timer)
        
        # Calcula o tempo gasto para responder
        tempo_gasto = self.TEMPOS[self.pergunta_atual] - self.tempo_restante
        self.tempo_respostas.append(tempo_gasto)
        
        letra_selecionada = ['A', 'B', 'C', 'D'][indice]
        resposta_correta = self.perguntas[self.pergunta_atual]['resposta']
        
        if letra_selecionada == resposta_correta:
            self.pontuacao += 1
            self.respostas_corretas_consecutivas += 1
            mensagem = "Você acertou!"
            
            # Verifica se o jogador merece um bônus
            if self.respostas_corretas_consecutivas >= 3 and tempo_gasto < (self.TEMPOS[self.pergunta_atual] / 2):
                self.conceder_bonus()
                mensagem += "\n\nVocê ganhou um bônus especial!"
            
            messagebox.showinfo("Correto!", mensagem)
        else:
            self.respostas_corretas_consecutivas = 0
            self.perde_vida("Resposta incorreta!")
            return

        self.pergunta_atual += 1
        self.carregar_pergunta()

    def conceder_bonus(self):
        """Concede um bônus aleatório ao jogador"""
        self.respostas_corretas_consecutivas = 0  # Reseta o contador
        
        # Tipos de bônus disponíveis
        bonus = random.choice([
            "vida_extra",
            "segunda_chance",
            "tempo_extra"
        ])
        
        if bonus == "vida_extra":
            self.vidas += 1
            self.label_vidas.config(text=f"Vidas: {self.vidas}")
            messagebox.showinfo("Bônus!", "Você ganhou uma vida extra!")
        
        elif bonus == "segunda_chance":
            self.bonus_disponivel = True
            messagebox.showinfo("Bônus!", "Você ganhou uma segunda chance! Poderá tentar novamente se errar a próxima pergunta.")
        
        elif bonus == "tempo_extra":
            # Adiciona 10 segundos à próxima pergunta
            if self.pergunta_atual + 1 < len(self.TEMPOS):
                self.TEMPOS[self.pergunta_atual + 1] += 10
            messagebox.showinfo("Bônus!", "Você ganhou +10 segundos para a próxima pergunta!")

    def perde_vida(self, motivo):
        if self.bonus_disponivel:
            self.bonus_disponivel = False
            messagebox.showinfo("Segunda Chance", "Você usou seu bônus de segunda chance!")
            self.pergunta_atual += 1
            self.carregar_pergunta()
            return
            
        self.vidas -= 1
        self.label_vidas.config(text=f"Vidas: {self.vidas}")
        messagebox.showwarning("Erro!", f"{motivo} Você perdeu uma vida.")
        
        if self.vidas <= 0:
            messagebox.showerror("Fim de Jogo", "Você perdeu todas as vidas!")
            self.root.quit()
        else:
            self.pergunta_atual += 1
            self.carregar_pergunta()

    def carregar_perguntas_do_banco(self):
        """Carrega perguntas do banco de dados baseado no nível selecionado"""
        try:
            conn = sqlite3.connect(caminho_completo)
            cursor = conn.cursor()
            
            # Primeiro, verifique quais perguntas existem
            cursor.execute("SELECT DISTINCT dificuldade_pergunta, classe_pergunta FROM Perguntas")
            niveis_disponiveis = cursor.fetchall()
            print("Níveis disponíveis no banco:", niveis_disponiveis)
            
            # Sua query original continua aqui...
            cursor.execute("""
                SELECT pergunta, opcao_a, opcao_b, opcao_c, opcao_d, resposta 
                FROM Perguntas 
                WHERE dificuldade_pergunta = ? AND classe_pergunta = ?
                ORDER BY RANDOM()
            """, (self.dificuldade, self.classe))
            
            perguntas = []
            for row in cursor.fetchall():
                perguntas.append({
                    "pergunta": row[0],
                    "opcoes": [row[1], row[2], row[3], row[4]],
                    "resposta": row[5]
                })
            
            print(f"Encontradas {len(perguntas)} perguntas para dificuldade {self.dificuldade} e classe {self.classe}")
            conn.close()
            return perguntas
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar perguntas: {str(e)}")
            return []

if __name__ == "__main__":
    root = tk.Tk()
    
    # Exemplos corretos:
    # Ato I (Classe 5) - Fase Fácil (Dificuldade 1)
    # jogo = QuizGame(root, nivel="1-5")  # Dificuldade 1, Classe 5
    
    # Ato II (Classe 4) - Fase Média (Dificuldade 2)
    jogo = QuizGame(root, nivel="2-4")
    
    # Ato III (Classe 3) - Fase Difícil (Dificuldade 3)
    # jogo = QuizGame(root, nivel="3-3")
    
    root.mainloop()