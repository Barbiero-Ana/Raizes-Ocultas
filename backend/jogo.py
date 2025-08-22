import sys
import sqlite3
import os
import random
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt

# Configurações do banco de dados
pasta_db = "database"
nome_banco = "raizes_ocultas.db"
caminho_completo = os.path.join(pasta_db, nome_banco)

class QuizGame(QWidget):
    def __init__(self, parent=None, nivel=None, id_turma=None, perguntas_anteriores=None):
        super().__init__(parent)
        # Resto do código permanece o mesmo...
        super().__init__()
        self.setWindowTitle("Quiz Game - Raízes Ocultas")
        self.setGeometry(200, 100, 800, 600)
        self.pergunta_atual = 0
        self.pontuacao = 0
        self.vidas = 3
        self.tempo_restante = 0
        self.nivel = nivel
        self.respostas_corretas_consecutivas = 0
        self.tempo_respostas = []
        self.bonus_disponivel = False
        self.id_turma = id_turma
        self.perguntas_anteriores = perguntas_anteriores or []
        self.timer = QTimer()
        self.timer.timeout.connect(self.atualizar_timer)

        if nivel and '-' in nivel:
            self.dificuldade, self.classe = map(int, nivel.split('-'))
        else:
            self.dificuldade, self.classe = 1, 1

        self.setup_ui()
        self.perguntas = self.carregar_perguntas_do_banco()

        if not self.perguntas:
            QMessageBox.critical(self, "Erro", "Nenhuma pergunta encontrada para este nível!")
            self.close()
            return

        self.TEMPOS = self.definir_tempos()
        self.carregar_pergunta()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.label_pergunta = QLabel("Carregando perguntas...")
        self.label_pergunta.setWordWrap(True)
        self.label_pergunta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_pergunta.setStyleSheet("font-size: 16px;")
        layout.addWidget(self.label_pergunta)

        self.botoes = []
        for i in range(4):
            btn = QPushButton("")
            btn.setFixedWidth(400)
            btn.setStyleSheet("font-size: 14px; padding: 8px;")
            btn.clicked.connect(lambda _, i=i: self.verificar_resposta(i))
            layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)
            self.botoes.append(btn)

        info_layout = QHBoxLayout()
        self.label_timer = QLabel("Tempo: --")
        self.label_vidas = QLabel(f"Vidas: {self.vidas}")
        info_layout.addWidget(self.label_timer)
        info_layout.addWidget(self.label_vidas)
        layout.addLayout(info_layout)

        self.setLayout(layout)

    def carregar_perguntas_do_banco(self):
        try:
            conn = sqlite3.connect(caminho_completo)
            cursor = conn.cursor()

            cursor.execute("""
                SELECT COUNT(*) FROM Perguntas 
                WHERE dificuldade_pergunta = ? AND classe_pergunta = ?
            """, (self.dificuldade, self.classe))
            total_perguntas = cursor.fetchone()[0]
            if total_perguntas == 0:
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

            conn.close()
            return perguntas

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao carregar perguntas: {str(e)}")
            return []

    def definir_tempos(self):
        tempos_base = {1: 120, 2: 90, 3: 60, 4: 30}
        return [tempos_base[self.dificuldade]] * len(self.perguntas)

    def carregar_pergunta(self):
        if self.pergunta_atual >= len(self.perguntas):
            QMessageBox.information(self, "Parabéns!", f"Você completou o quiz! Pontuação: {self.pontuacao}")
            self.close()
            return

        p = self.perguntas[self.pergunta_atual]
        self.label_pergunta.setText(f"{self.pergunta_atual+1}. {p['pergunta']}")

        for i, letra in enumerate(['A', 'B', 'C', 'D']):
            self.botoes[i].setText(p['opcoes'][i])
            self.botoes[i].setEnabled(True)

        self.tempo_restante = self.TEMPOS[self.pergunta_atual]
        self.atualizar_timer()
        self.timer.start(1000)

    def atualizar_timer(self):
        self.label_timer.setText(f"Tempo restante: {self.tempo_restante} segundos")
        if self.tempo_restante <= 0:
            self.perde_vida("Tempo esgotado!")
            return
        self.tempo_restante -= 1

    def verificar_resposta(self, indice):
        self.timer.stop()

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
            QMessageBox.information(self, "Correto!", mensagem)
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
        self.respostas_corretas_consecutivas = 0
        bonus = random.choice(["vida_extra", "segunda_chance", "tempo_extra"])

        if bonus == "vida_extra":
            self.vidas += 1
            self.label_vidas.setText(f"Vidas: {self.vidas}")
            QMessageBox.information(self, "Bônus!", "Você ganhou uma vida extra!")
        elif bonus == "segunda_chance":
            self.bonus_disponivel = True
            QMessageBox.information(self, "Bônus!", "Você ganhou uma segunda chance!")
        elif bonus == "tempo_extra":
            if self.pergunta_atual + 1 < len(self.TEMPOS):
                self.TEMPOS[self.pergunta_atual + 1] += 10
            QMessageBox.information(self, "Bônus!", "Você ganhou +10 segundos na próxima pergunta!")

    def perde_vida(self, motivo):
        if self.bonus_disponivel:
            self.bonus_disponivel = False
            QMessageBox.information(self, "Segunda Chance", "Você usou seu bônus!")
            self.pergunta_atual += 1
            self.carregar_pergunta()
            return

        self.vidas -= 1
        self.label_vidas.setText(f"Vidas: {self.vidas}")
        QMessageBox.warning(self, "Erro!", f"{motivo} Você perdeu uma vida.")

        if self.vidas <= 0:
            QMessageBox.critical(self, "Fim de Jogo", "Você perdeu todas as vidas!")
            self.close()
        else:
            self.pergunta_atual += 1
            self.carregar_pergunta()
