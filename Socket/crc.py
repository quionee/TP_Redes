#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class CRC:
    polinomio = None
    polinomioDecimal = None
    grauPolinomio = None
    
    def __init__(self, polinomio):
        self.polinomio = '10011'
        self.polinomioDecimal = int(self.polinomio, base=2)
        self.grauPolinomio = len(self.polinomio) - 1
        
    
    def calculaCRC(self, mensagem):
        # mensagem = mensagem.encode('ascii')
        mensagem = list(bin(859 << len(self.polinomio)-1)[2:])
        print(''.join(mensagem))
        print(mensagem)
        for i in range(len(mensagem) - self.grauPolinomio-1):
            if(mensagem[i] == '1'):
                for j in range(len(self.polinomio)):
                    bitMensagem = int(mensagem[i+j])
                    bitPolinomio = int(self.polinomio[j])
                    mensagem[i + j] = str(bitMensagem ^ bitPolinomio)
                    # print(bitMensagem, "xor", bitPolinomio, "=", mensagem[i + j])
        print(''.join(mensagem))
        i = 0
        while(mensagem[i] == '0'):
            print(mensagem[i])
            mensagem.pop(i)
        print(mensagem)

        ## ESSE É O TESTE QUE TEREMOS QUE FAZER DO LADO CLIENTE ##
        # copiaMensagem = list(bin(859)[2:])
        # copiaMensagem = copiaMensagem + mensagem
        # print(''.join(copiaMensagem))
        # for i in range(len(copiaMensagem) - self.grauPolinomio-1):
        #     if(copiaMensagem[i] == '1'):
        #         for j in range(len(self.polinomio)):
        #             bitMensagem = int(copiaMensagem[i+j])
        #             bitPolinomio = int(self.polinomio[j])
        #             copiaMensagem[i + j] = str(bitMensagem ^ bitPolinomio)
        #             print(bitMensagem, "xor", bitPolinomio, "=", copiaMensagem[i + j])
        # print(''.join(copiaMensagem))

        # 45643
        # 263
    
        # 1101011011
        # 10011

def main():
    x = CRC("")
    x.calculaCRC("")
main()