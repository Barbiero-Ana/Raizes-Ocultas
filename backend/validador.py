from PyQt6.QtWidgets import QMessageBox
import re

class Validador:
    @staticmethod
    def validar_cpf(cpf: str, db=None, id_cliente=None) -> tuple:
        """Valida CPF (formato, dígitos verificadores e se já está cadastrado)"""
        cpf = ''.join(filter(str.isdigit, cpf))
        
        # Verifica tamanho
        if len(cpf) != 11:
            return (False, "CPF deve conter 11 dígitos")
            
        # Verifica dígitos repetidos
        if cpf == cpf[0] * 11:
            return (False, "CPF inválido")
            
        # Cálculo dos dígitos verificadores
        for i in range(9, 11):
            valor = sum((int(cpf[num]) * ((i+1) - num) for num in range(0, i)))
            digito = ((valor * 10) % 11) % 10
            if digito != int(cpf[i]):
                return (False, "CPF inválido")
        
        # Verifica se CPF já está cadastrado (se db foi fornecido)
        if db:
            cpf_formatado = Validador.formatar_cpf(cpf)
            cliente_existente = db.obter_cliente_por_cpf(cpf_formatado)
            if cliente_existente and (id_cliente is None or cliente_existente[0] != id_cliente):
                return (False, f"CPF {cpf_formatado} já está cadastrado para outro cliente")
                
        return (True, "")

    @staticmethod
    def validar_email(email: str) -> tuple:
        """Valida formato de email com regex"""
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return (False, "Email inválido")
        return (True, "")
    
    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """Formata um CPF (xxx.xxx.xxx-xx) e remove caracteres inválidos."""
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) > 11:
            cpf = cpf[:11]
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:11]}"
        return cpf  # Retorna sem formatação se não tiver 11 dígitos