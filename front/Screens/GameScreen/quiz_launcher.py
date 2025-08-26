import tkinter as tk
from jogo import QuizGame
import sys
import ast

if __name__ == "__main__":
    # Obter argumentos da linha de comando
    if len(sys.argv) >= 4:
        dificuldade = int(sys.argv[1])
        classe = int(sys.argv[2])
        id_turma = int(sys.argv[3]) if sys.argv[3] != "None" else None
        perguntas_anteriores = ast.literal_eval(sys.argv[4]) if len(sys.argv) > 4 else []
        
        root = tk.Tk()
        root.title('Quiz - Raízes Ocultas')
        
        quiz_game = QuizGame(
            root, 
            nivel=f'{dificuldade}-{classe}', 
            id_turma=id_turma,
            perguntas_anteriores=perguntas_anteriores
        )
        
        root.mainloop()