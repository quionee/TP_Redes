#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class CRC:
    polinomio = None
    polinomioDecimal = None
    grauPolinomio = None
    
    def __init__(self, polinomio):
        self.polinomio = '100000111'
        self.polinomioDecimal = int(self.polinomio, base=2)
        self.grauPolinomio = len(self.polinomio) - 1
        
    
    def calculaCRC(self, mensagem):
        # mensagem = mensagem.encode('ascii')
        mensagem = list(bin(45643 << 8)[2:])
        print(''.join(mensagem))

        resultado = ""
        for i in range(len(mensagem) - self.grauPolinomio):
            if(mensagem[i] == '1'):
                for j in range(len(self.polinomio)):
                    bitMensagem = int(mensagem[i])
                    bitPolinomio = int(self.polinomio[j])
                    mensagem[i + j] = str(bitMensagem ^ bitPolinomio)
                    print(bitMensagem, "xor", bitPolinomio, "=", mensagem[i + j])
            resultado += mensagem[i]
        print(''.join(mensagem))
        print(resultado)


        # resto = dx  % self.polinomioDecimal
        # resultado = int(('0b') + (bin(mensagem)[2:]) + (bin(resto)[2:]), base = 2)
        # print(resultado)

        # print(resultado % self.polinomioDecimal)

    
        # 45643
        # 263
    
        # 1101011011
        # 10011

def main():
    x = CRC("")
    x.calculaCRC("")
main()