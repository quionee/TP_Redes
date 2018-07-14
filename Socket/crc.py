#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# x ^ 16 + x ^ 15 + x ^ 2 + 1
POLINOMIO = "11000000000000101"

class CRC:
    polinomio = None
    polinomioDecimal = None
    grauPolinomio = None
    
    def __init__(self, polinomio = POLINOMIO):
        self.polinomio = polinomio
        self.polinomioDecimal = int(self.polinomio, base=2)
        self.grauPolinomio = len(self.polinomio) - 1
        
    
    # retorna True se o resultado do CRC for 0 (exemplo: True)
    # entrada: mensagem com bits de verificação inclusos (exemplo: "0b1110111101")
    def verificaCRC(self, mensagem):
        mensagem = list(mensagem[2:])
        resultado = "0b" + ''.join(self.calculaCRC(mensagem))
        if(int(resultado, base = 2) == 0):
            return True
        return False


    # retorna: um binario com a sequencia de bits gerada pelo calculo do CRC (exemplo: '0b01001')
    # entrada: um valor binario (exemplo: '0b110100101001')
    def geraCRC(self, mensagem):
        mensagem = list(mensagem[2:] + ('0' * self.grauPolinomio))
        retorno = "0b" + ''.join(self.calculaCRC(mensagem))
        return retorno

    # retorna: lista com caracteres de valores 1 ou 0 (exemplo: ['1', '0', '1'])
    # entrada: recebe uma lista de caracteres com valores de 1 e 0 (exemplo: ['1', '0', '1'])
    def calculaCRC(self, mensagem):
        for i in range(len(mensagem) - self.grauPolinomio):
            if(mensagem[i] == '1'):
                for j in range(len(self.polinomio)):
                    bitMensagem = int(mensagem[i + j])
                    bitPolinomio = int(self.polinomio[j])
                    mensagem[i + j] = str(bitMensagem ^ bitPolinomio)

        mensagem = mensagem[-self.grauPolinomio:]
        return mensagem