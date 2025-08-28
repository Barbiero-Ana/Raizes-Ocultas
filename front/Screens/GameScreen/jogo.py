import tkinter as tk
from tkinter import messagebox
import threading
import sqlite3
import os
import random
import time
from tkinter import ttk
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️ PIL não encontrado. Usando fallback para emojis.")

pasta_db = "database"
nome_banco = "raizes_ocultas.db"
caminho_completo = os.path.join(pasta_db, nome_banco)

class QuizGame:
    def __init__(self, root, nivel=None, id_turma=None, perguntas_anteriores=None):
        self.root = root
        self.root.title("Quiz Game - Raízes Ocultas")
        self.root.geometry("1000x700")
        self.root.configure(bg="#1a1a1a")
        
        self.root.update_idletasks()
        width = 1000
        height = 700
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.pergunta_atual = 0
        self.pontuacao = 0
        self.vidas = 3
        self.timer = None
        self.tempo_restante = 0
        self.nivel = nivel
        self.respostas_corretas_consecutivas = 0
        self.tempo_respostas = []
        self.bonus_disponivel = False
        self.id_turma = id_turma
        self.perguntas_anteriores = perguntas_anteriores or []  
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_quiz)
        
        if nivel and '-' in nivel:
            self.dificuldade, self.classe = map(int, nivel.split('-'))
        else:
            self.dificuldade, self.classe = 1, 1
        
        self.setup_ui()
        
        self.perguntas = self.carregar_perguntas_do_banco()
        
        if not self.perguntas:
            messagebox.showerror("Erro", "Nenhuma pergunta encontrada para este nível!")
            self.root.after(1000, self.fechar_quiz)
            return
        
        self.TEMPOS = self.definir_tempos()
        
        self.definir_boss_avatar()
        
        self.carregar_pergunta()

    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#1a1a1a")
        main_frame.pack(fill=tk.BOTH, expand=True)
        arena_frame = tk.Frame(main_frame, bg="#2a2a2a", height=490)
        arena_frame.pack(fill=tk.X, padx=0, pady=0)
        arena_frame.pack_propagate(False)
        
        status_frame = tk.Frame(arena_frame, bg="#1a1a1a", height=60)
        status_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        status_frame.pack_propagate(False)
        
        self.label_timer = tk.Label(status_frame, text="⏰ Tempo: --", 
                                   font=("Arial", 14, "bold"), 
                                   fg="#FFD700", bg="#654321", 
                                   padx=15, pady=8, relief="raised", bd=2)
        self.label_timer.pack(side=tk.LEFT)
        
        title_label = tk.Label(status_frame, text="QUIZ BATTLE", 
                              font=("Arial", 18, "bold"), fg="#FFD700", bg="#1a1a1a")
        title_label.pack(side=tk.LEFT, expand=True)
        
        self.label_vidas = tk.Label(status_frame, text="❤️ Vidas: 3", 
                                   font=("Arial", 14, "bold"), 
                                   fg="#FFD700", bg="#654321", 
                                   padx=15, pady=8, relief="raised", bd=2)
        self.label_vidas.pack(side=tk.RIGHT)
        
        battle_area = tk.Frame(arena_frame, bg="#2a2a2a")
        battle_area.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        player_frame = tk.Frame(battle_area, bg="#2a2a2a")
        player_frame.pack(side=tk.LEFT, anchor="sw", padx=(0, 20))
        
        self.player_avatar = tk.Label(player_frame, bg="#2a2a2a")
        self.carregar_sprite_player()
        self.player_avatar.pack()
        
        player_name = tk.Label(player_frame, text="JOGADOR", 
                              font=("Arial", 12, "bold"), 
                              fg="#4CAF50", bg="#2a2a2a")
        player_name.pack()
        
        boss_frame = tk.Frame(battle_area, bg="#2a2a2a")
        boss_frame.pack(side=tk.RIGHT, anchor="se", padx=(20, 0))
        
        self.boss_avatar = tk.Label(boss_frame, text="🐉", 
                                   font=("Arial", 80), bg="#2a2a2a")
        self.boss_avatar.pack()
        
        self.boss_name_label = tk.Label(boss_frame, text="DESAFIO", 
                            font=("Arial", 12, "bold"), 
                            fg="#F44336", bg="#2a2a2a")
        self.boss_name_label.pack()
        
        dialog_frame = tk.Frame(main_frame, bg="#1a1a1a", height=210)
        dialog_frame.pack(fill=tk.X, padx=0, pady=0)
        dialog_frame.pack_propagate(False)
        
        bubble_frame = tk.Frame(dialog_frame, bg="#3d2914", relief="raised", bd=3)
        bubble_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        self.label_pergunta = tk.Label(bubble_frame, text="Carregando perguntas...", 
                                      wraplength=900, font=("Arial", 14, "bold"), 
                                      fg="#f5e9c3", bg="#3d2914", pady=15)
        self.label_pergunta.pack(fill=tk.X)
        
        botoes_container = tk.Frame(bubble_frame, bg="#3d2914")
        botoes_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        self.botoes = []
        letras = ['A', 'B', 'C', 'D']
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]  
        
        for i in range(4):
            row, col = positions[i]
            btn = tk.Button(botoes_container, text="", 
                          font=("Arial", 11, "bold"), 
                          bg="#8B4513", fg="#FFD700",
                          activebackground="#A0522D", activeforeground="#FFD700",
                          relief="raised", bd=2, wraplength=350,
                          command=lambda i=i: self.verificar_resposta(i), 
                          state=tk.DISABLED)
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            self.botoes.append(btn)
        
        botoes_container.grid_rowconfigure(0, weight=1)
        botoes_container.grid_rowconfigure(1, weight=1)
        botoes_container.grid_columnconfigure(0, weight=1)
        botoes_container.grid_columnconfigure(1, weight=1)

    def fechar_quiz(self):
        if hasattr(self, 'timer') and self.timer:
            self.root.after_cancel(self.timer)
        self.root.destroy()

    def carregar_perguntas_do_banco(self):
        try:
            conn = sqlite3.connect(caminho_completo)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*) FROM Perguntas 
                WHERE dificuldade_pergunta = ? AND classe_pergunta = ?
            """, (self.dificuldade, self.classe))
            
            total_perguntas = cursor.fetchone()[0]
            print(f"Total de perguntas para nível {self.dificuldade}-{self.classe}: {total_perguntas}")
            
            if total_perguntas == 0:
                messagebox.showerror("Erro", f"Nenhuma pergunta encontrada para o nível {self.dificuldade}-{self.classe}!")
                conn.close()
                return []
            
            if self.perguntas_anteriores:
                placeholders = ','.join('?' * len(self.perguntas_anteriores))
                query = f"""
                    SELECT id_pergunta, pergunta, opcao_a, opcao_b, opcao_c, opcao_d, resposta 
                    FROM Perguntas 
                    WHERE dificuldade_pergunta = ? 
                    AND classe_pergunta = ?
                    AND id_pergunta NOT IN ({placeholders})
                    ORDER BY RANDOM()
                    LIMIT 10
                """
                params = [self.dificuldade, self.classe] + self.perguntas_anteriores
            else:
                query = """
                    SELECT id_pergunta, pergunta, opcao_a, opcao_b, opcao_c, opcao_d, resposta 
                    FROM Perguntas 
                    WHERE dificuldade_pergunta = ? 
                    AND classe_pergunta = ?
                    ORDER BY RANDOM()
                    LIMIT 10
                """
                params = [self.dificuldade, self.classe]
            
            cursor.execute(query, params)
            
            perguntas = []
            self.ids_perguntas_atual = []  
            for row in cursor.fetchall():
                self.ids_perguntas_atual.append(row[0])  
                perguntas.append({
                    "id_pergunta": row[0],
                    "pergunta": row[1],
                    "opcoes": [row[2], row[3], row[4], row[5]],
                    "resposta": row[6]
                })
            
            print(f"Perguntas carregadas: {len(perguntas)}")
            conn.close()
            return perguntas
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar perguntas: {str(e)}")
            print(f"Erro detalhado: {e}")
            return []

    def definir_tempos(self):
        tempos_base = {
            1: 120, 
            2: 90,
            3: 60,
            4: 30    
        }
        return [tempos_base[self.dificuldade]] * len(self.perguntas)
    
    def definir_boss_avatar(self):
        boss_names = {
            1: "ESPÍRITO DA NEBLINA",
            2: "GUARDIÃO", 
            3: "DRAGÃO ANCESTRAL",
            4: "MESTRE SUPREMO"
        }
        
        if PIL_AVAILABLE and hasattr(self, 'boss_avatar'):
            self.carregar_sprite_boss()
        else:
            boss_avatars = {
                1: "🐸",      
                2: "🐺",      
                3: "🐉",      
                4: "👹"      
            }
            if hasattr(self, 'boss_avatar'):
                avatar = boss_avatars.get(self.dificuldade, "🐉")
                self.boss_avatar.config(text=avatar)
            
        if hasattr(self, 'boss_name_label'):
            nome = boss_names.get(self.dificuldade, "DESAFIO")
            self.boss_name_label.config(text=nome)
    
    def carregar_sprite_player(self):
        if not PIL_AVAILABLE:
            self.player_avatar.config(text="🧙‍♂️", font=("Arial", 80))
            return
            
        sprite_path = "assets/ScreenElements/personagens/player-static.png"
        
        try:
            if os.path.exists(sprite_path):
                image = Image.open(sprite_path)
                image = image.resize((120, 160), Image.Resampling.LANCZOS)
                self.player_image = ImageTk.PhotoImage(image)
                self.player_avatar.config(image=self.player_image)
                
                self.player_image_normal = self.player_image
                self.criar_sprites_animacao()
            else:
                self.player_avatar.config(text="🧙‍♂️", font=("Arial", 80))
                print(f"⚠️ Sprite não encontrado: {sprite_path}")
                
        except Exception as e:
            self.player_avatar.config(text="🧙‍♂️", font=("Arial", 80))
            print(f"⚠️ Erro ao carregar sprite: {e}")
    
    def criar_sprites_animacao(self):
        if not PIL_AVAILABLE:
            return
            
        try:
            # Carregar sprite de vitória específico
            victory_path = "assets/ScreenElements/personagens/player-victory.png"
            if os.path.exists(victory_path):
                victory_image = Image.open(victory_path)
                victory_image = victory_image.resize((120, 160), Image.Resampling.LANCZOS)
                self.player_image_victory = ImageTk.PhotoImage(victory_image)
            else:
                # Fallback: criar versão modificada da imagem estática
                sprite_path = "assets/ScreenElements/personagens/player-static.png"
                if os.path.exists(sprite_path):
                    base_image = Image.open(sprite_path)
                    base_image = base_image.resize((120, 160), Image.Resampling.LANCZOS)
                    
                    victory_image = base_image.copy()
                    pixels = victory_image.load()
                    width, height = victory_image.size
                    for x in range(width):
                        for y in range(height):
                            r, g, b, a = pixels[x, y] if len(pixels[x, y]) == 4 else (*pixels[x, y], 255)
                            r = min(255, int(r * 1.3))
                            g = min(255, int(g * 1.2))
                            pixels[x, y] = (r, g, b, a) if len(pixels[x, y]) == 4 else (r, g, b)
                    
                    self.player_image_victory = ImageTk.PhotoImage(victory_image)
                else:
                    self.player_image_victory = self.player_image_normal
            
            # Criar sprite de erro
            sprite_path = "assets/ScreenElements/personagens/player-static.png"
            if os.path.exists(sprite_path):
                base_image = Image.open(sprite_path)
                base_image = base_image.resize((120, 160), Image.Resampling.LANCZOS)
                
                error_image = base_image.copy()
                pixels = error_image.load()
                width, height = error_image.size
                for x in range(width):
                    for y in range(height):
                        r, g, b, a = pixels[x, y] if len(pixels[x, y]) == 4 else (*pixels[x, y], 255)
                        r = int(r * 0.6)
                        g = int(g * 0.6)
                        b = int(b * 0.6)
                        pixels[x, y] = (r, g, b, a) if len(pixels[x, y]) == 4 else (r, g, b)
                
                self.player_image_error = ImageTk.PhotoImage(error_image)
            else:
                self.player_image_error = self.player_image_normal
                
        except Exception as e:
            print(f"⚠️ Erro ao criar sprites de animação: {e}")
            self.player_image_victory = self.player_image_normal
            self.player_image_error = self.player_image_normal
    
    def carregar_sprite_boss(self):
        if not PIL_AVAILABLE:
            return
            
        boss_sprites = {
            1: "assets/ScreenElements/gamescreen/boss/espirito-neblina/neblina-idle.png",
            2: "assets/ScreenElements/gamescreen/boss/espirito-neblina/neblina-idle.png", 
            3: "assets/ScreenElements/gamescreen/boss/espirito-neblina/neblina-bonuss.png", # Reutilizar para nível 3
            4: "assets/ScreenElements/gamescreen/boss/espirito-neblina/neblina-bonuss.png"  # Reutilizar para nível 4
        }
        
        sprite_path = boss_sprites.get(self.dificuldade, boss_sprites[1])
        
        try:
            if os.path.exists(sprite_path):
                image = Image.open(sprite_path)
                
                image = image.resize((140, 180), Image.Resampling.LANCZOS)
                self.boss_image = ImageTk.PhotoImage(image)
                self.boss_avatar.config(image=self.boss_image, text="")
                
                self.carregar_sprites_boss_animacao()
            else:
                print(f"⚠️ Sprite do boss não encontrado: {sprite_path}")
                boss_avatars = {1: "🐸", 2: "🐺", 3: "🐉", 4: "👹"}
                avatar = boss_avatars.get(self.dificuldade, "🐉")
                self.boss_avatar.config(text=avatar)
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar sprite do boss: {e}")
            boss_avatars = {1: "🐸", 2: "🐺", 3: "🐉", 4: "👹"}
            avatar = boss_avatars.get(self.dificuldade, "🐉")
            self.boss_avatar.config(text=avatar)
    
    def carregar_sprites_boss_animacao(self):
        if not PIL_AVAILABLE:
            return
            
        try:
            defeated_path = "assets/ScreenElements/gamescreen/boss/espirito-neblina/neblina-defeated.png"
            if os.path.exists(defeated_path):
                defeated_image = Image.open(defeated_path)
                defeated_image = defeated_image.resize((140, 180), Image.Resampling.LANCZOS)
                self.boss_image_defeated = ImageTk.PhotoImage(defeated_image)
            else:
                self.boss_image_defeated = None
            
            bonus_path = "assets/ScreenElements/gamescreen/boss/espirito-neblina/neblina-bonuss.png"
            if os.path.exists(bonus_path):
                bonus_image = Image.open(bonus_path)
                bonus_image = bonus_image.resize((140, 180), Image.Resampling.LANCZOS)
                self.boss_image_bonus = ImageTk.PhotoImage(bonus_image)
            else:
                self.boss_image_bonus = None
                
        except Exception as e:
            print(f"⚠️ Erro ao carregar sprites de animação do boss: {e}")
            self.boss_image_defeated = None
            self.boss_image_bonus = None

    def carregar_pergunta(self):
        if self.pergunta_atual >= len(self.perguntas):
            if hasattr(self, 'player_avatar'):
                if hasattr(self, 'player_image_victory'):
                    self.player_avatar.config(image=self.player_image_victory)
                else:
                    self.player_avatar.config(text="👑")  
            if hasattr(self, 'boss_avatar'):
                if hasattr(self, 'boss_image_defeated') and self.boss_image_defeated:
                    self.boss_avatar.config(image=self.boss_image_defeated)
                else:
                    self.boss_avatar.config(text="💀")  
            
            messagebox.showinfo("🏆 VITÓRIA!", f"Você derrotou o {self.boss_name_label.cget('text')}!\\nPontuação Final: {self.pontuacao}/{len(self.perguntas)}")
            self.fechar_quiz()
            return

        p = self.perguntas[self.pergunta_atual]
        self.label_pergunta.config(text=f"{self.pergunta_atual+1}. {p['pergunta']}")
        
        opcoes_mapeadas = {
            'A': p['opcoes'][0],
            'B': p['opcoes'][1],
            'C': p['opcoes'][2],
            'D': p['opcoes'][3]
        }
        
        for i, letra in enumerate(['A', 'B', 'C', 'D']):
            texto_botao = f"{letra}) {opcoes_mapeadas[letra]}"
            self.botoes[i].config(text=texto_botao, state=tk.NORMAL, height=2, 
                                bg="#8B4513", fg="#DC9D08")
            self.botoes[i].bind("<Enter>", lambda e, btn=self.botoes[i]: btn.config(bg="#A0522D", fg="#DC9D08"))
            self.botoes[i].bind("<Leave>", lambda e, btn=self.botoes[i]: btn.config(bg="#8B4513", fg="#DC9D08"))

        self.tempo_restante = self.TEMPOS[self.pergunta_atual]
        self.atualizar_timer()

    def atualizar_timer(self):
        if self.tempo_restante > 30:
            cor_timer = "#FFD700"
            bg_timer = "#654321"
        elif self.tempo_restante > 10:
            cor_timer = "#FFA500"
            bg_timer = "#8B4513"
            if hasattr(self, 'boss_avatar'):
                if hasattr(self, 'boss_image_bonus') and self.boss_image_bonus:
                    original_image = self.boss_avatar.cget("image") if self.boss_avatar.cget("image") else None
                    self.boss_avatar.config(image=self.boss_image_bonus)
                    if original_image:
                        self.root.after(300, lambda: self.boss_avatar.config(image=original_image))
                    else:
                        self.root.after(300, lambda: self.boss_avatar.config(image=self.boss_image))
                else:
                    original_avatar = self.boss_avatar.cget("text")
                    self.boss_avatar.config(text="😤")  
                    self.root.after(300, lambda: self.boss_avatar.config(text=original_avatar))
        else:
            cor_timer = "#FF4500"
            bg_timer = "#B22222"
            if hasattr(self, 'boss_avatar'):
                if hasattr(self, 'boss_image_bonus') and self.boss_image_bonus:
                    self.boss_avatar.config(image=self.boss_image_bonus)
                    self.root.after(200, lambda: self.boss_avatar.config(image=self.boss_image))
                else:
                    self.boss_avatar.config(text="⚡")  
                    self.root.after(200, lambda: self.boss_avatar.config(text="😈"))
        
        self.label_timer.config(text=f"⏰ Tempo: {self.tempo_restante}s", 
                               fg=cor_timer, bg=bg_timer)
        
        if self.tempo_restante <= 0:
            self.perde_vida("Tempo esgotado!")
            return

        self.tempo_restante -= 1
        self.timer = self.root.after(1000, self.atualizar_timer)

    def verificar_resposta(self, indice):
        if hasattr(self, 'timer') and self.timer:
            self.root.after_cancel(self.timer)
        
        tempo_gasto = self.TEMPOS[self.pergunta_atual] - self.tempo_restante
        letra_selecionada = ['A', 'B', 'C', 'D'][indice]
        resposta_correta = self.perguntas[self.pergunta_atual]['resposta']
        acertou = letra_selecionada == resposta_correta
        
        self.salvar_resposta_turma(acertou, tempo_gasto)
        
        if acertou:
            self.pontuacao += 1
            self.respostas_corretas_consecutivas += 1
            mensagem = "Você acertou!"
            
            if self.respostas_corretas_consecutivas >= 3 and tempo_gasto < (self.TEMPOS[self.pergunta_atual] / 2):
                self.conceder_bonus()
                mensagem += "\n\nVocê ganhou um bônus especial!"
            
            messagebox.showinfo("✅ Correto!", mensagem)
            if hasattr(self, 'player_image_victory'):
                self.player_avatar.config(image=self.player_image_victory)
                self.root.after(1000, lambda: self.player_avatar.config(image=self.player_image_normal))
            else:
                self.player_avatar.config(text="🎆")
                self.root.after(1000, lambda: self.player_avatar.config(text="🧙‍♂️"))
        else:
            self.respostas_corretas_consecutivas = 0
            self.perde_vida("Resposta incorreta!")
            return

        self.pergunta_atual += 1
        self.carregar_pergunta()

    def salvar_resposta_turma(self, acertou, tempo_gasto):
        if not self.id_turma:
            return
            
        try:
            conn = sqlite3.connect(caminho_completo)
            cursor = conn.cursor()
            
            id_pergunta = self.perguntas[self.pergunta_atual]['id_pergunta']
            
            cursor.execute("""
                INSERT OR IGNORE INTO Dados_do_jogador 
                (id_turma, id_pergunta, acertou, tempo_resposta)
                VALUES (?, ?, ?, ?)
            """, (self.id_turma, id_pergunta, int(acertou), tempo_gasto))
            
            conn.commit()
            conn.close()
            
            if id_pergunta not in self.perguntas_anteriores:
                self.perguntas_anteriores.append(id_pergunta)
                
        except Exception as e:
            print(f"Erro ao salvar resposta: {e}")

    def conceder_bonus(self):
        self.respostas_corretas_consecutivas = 0  # Reseta o contador
        
        bonus = random.choice([
            "vida_extra",
            "segunda_chance",
            "tempo_extra"
        ])
        
        if bonus == "vida_extra":
            self.vidas += 1
            self.label_vidas.config(text=f"❤️ Vidas: {self.vidas}")
            messagebox.showinfo("Bônus!", "Você ganhou uma vida extra!")
        
        elif bonus == "segunda_chance":
            self.bonus_disponivel = True
            messagebox.showinfo("Bônus!", "Você ganhou uma segunda chance! Poderá tentar novamente se errar a próxima pergunta.")
        
        elif bonus == "tempo_extra":
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
        self.label_vidas.config(text=f"❤️ Vidas: {self.vidas}")
        messagebox.showwarning("❌ Erro!", f"{motivo} Você perdeu uma vida.")
        if hasattr(self, 'player_image_error'):
            self.player_avatar.config(image=self.player_image_error)
            self.root.after(1500, lambda: self.player_avatar.config(image=self.player_image_normal))
        else:
            self.player_avatar.config(text="😵")
            self.root.after(1500, lambda: self.player_avatar.config(text="🧙‍♂️"))
        
        if self.vidas <= 0:
            if hasattr(self, 'player_avatar'):
                if hasattr(self, 'player_image_error'):
                    self.player_avatar.config(image=self.player_image_error)
                else:
                    self.player_avatar.config(text="💀")  
            if hasattr(self, 'boss_avatar'):
                # Usar sprite de boss bônus se disponível (representando vitória), senão emoji
                if hasattr(self, 'boss_image_bonus') and self.boss_image_bonus:
                    self.boss_avatar.config(image=self.boss_image_bonus)
                else:
                    self.boss_avatar.config(text="😈")  
            
            messagebox.showerror("💀 DERROTA!", f"O {self.boss_name_label.cget('text')} te derrotou!\\nVocê perdeu todas as vidas!")
            self.fechar_quiz()
        else:
            self.pergunta_atual += 1
            self.carregar_pergunta()

