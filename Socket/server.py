#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import random
from crc import CRC

# transforma um array de bytes em uma sequencia de bits
# entrada: lista de bytes
# retorno: sequência binária, onde cada byte da lista é codificada em oito bits
def transformaEmBit(listaBytes):
    resultado = "0b"

    for item in listaBytes:
        item = bin(int(str(item.hex()), 16))[2:]

        while(len(item) < 8):
            item = "0" + item
        resultado += item

    return resultado

# recebe uma sequência de bytes de uma conexão socket
# entrada: conexão socket e a quantidade de bytes que serão recebidos
# retorno: lista de bytes
def leBytes(conexao, qtdBytes):
    listaBytes = []

    for i in range(qtdBytes):
        byteLido = conexao.recv(1)
        # adiciona os dados do cabeçalho a uma lista de bytes
        listaBytes.append(byteLido)

    return listaBytes

# junta todos os bytes de uma lista de bytes
# entrada: uma lista de bytes
# retorno: uma sequência de bytes
def juntaBytes(listaDeBytes):
    resultado = b''

    for byte in listaDeBytes:
        resultado += byte

    return resultado

# import socket
def main(args):
    # variáveis para cálculos estatísticos
    MENSAGENS_RECEBIDAS = 0
    MENSAGENS_COM_ERROS_NO_CRC = 0
    MENSAGENS_DUPLICADAS = 0
    MENSAGENS_CORRETAS = 0
    
    
    # flag delimitadora ("~")
    DELIMITADOR = bytes.fromhex('7e')

    # host padrão
    HOST = '127.0.0.1'

    # se os IPs foram passados como argumentos, são atribuídos às suas respectivas variáveis
#     if(len(args) > 1):
#         print(args[1])
#         HOST = args[1]
        
    PORT = 50017

    # inicializa o socket do servidor
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)

    while True:
        conexao, addr = sock.accept()

        fimMensagem = False

        # mensagem enviada pelo usuário
        mensagemCompleta = ''

        # o último número de sequência recebido
        ultimoRecebido = '0b10000000'

        ipOrigem = None
        
        print('')
        # o loop termina quando a mensagem for totalmente enviada
        while (not fimMensagem):
            cabecalho = b''
            cabecalho += conexao.recv(1)

            if(len(cabecalho) <= 0):
                fimMensagem = True
                continue
            
            # incrementa mensagens recebidas
            MENSAGENS_RECEBIDAS += 1

            # lista com todos os bytes recebidos
            listaBytes = leBytes(conexao, 10)

            # cabeçalho é o conjunto dos 11 primeiros bytes recebidos
            cabecalho += juntaBytes(listaBytes)

            # o tamanho da mensagem contida no quadro é o segundo byte
            tamanhoDados = cabecalho[1]

            # recebe os bytes da mensagem
            listaDados = leBytes(conexao, tamanhoDados)
            listaBytes += listaDados
            dados = b'' + juntaBytes(listaDados)

            # recebe o codigo CRC gerado pelo cliente
            # e o adiciona à lista de bytes
            codigoCRC = conexao.recv(1)
            listaBytes.append(codigoCRC)
            codigoCRC = conexao.recv(1)
            listaBytes.append(codigoCRC)

            # transforma a lista de bytes em sequências binárias, 
            # completando com zeros à esquerda para que sejam sequências de 8 bits
            mensagemBin = transformaEmBit(listaBytes)

            # simulador de erro de transmissão com 5% de chance de alteração de um bit do quadro
            if(random.random() > 0.95):
                print("Invertendo")
                posicao = random.randrange(0, tamanhoDados)
                mensagemBin = list(mensagemBin)
                mensagemBin[posicao] = bin(int(mensagemBin[posicao]) ^ 0x01)[2:]
                
            # verifica o CRC da mensagem
            crc = CRC()
            sequenciaACK = bytes([(cabecalho[2] & 0x80) + 1])

                
            resultadoCRC = crc.verificaCRC(mensagemBin)
            # verifica se o número de sequência do último quadro recebido 
            # é diferente do quadro atual
            # também verifica (utilizando CRC) se os dados da mensagem foram corrompidos
            if((int(ultimoRecebido, 2) ^ (cabecalho[2] & 0x80)) and resultadoCRC):
#                 print("mensagem completa:", mensagemCompleta)
                mensagemCompleta += dados.decode("ascii")
                ultimoRecebido = bin(int(ultimoRecebido, 2) ^ 0x80)
            # caso alguma das duas verificações seja falsa, reenvia o ack do último quadro recebido
            else:
                sequenciaACK = bytes([int.from_bytes(sequenciaACK, byteorder='big') ^ 0x80])
                
                #
                if(resultadoCRC):
                    # incrementa erros de crc
                    MENSAGENS_COM_ERRO_NO_CRC += 1
                else:
                    #incrementa mensagens duplicadas
                    MENSAGENS_DUPLICADAS += 1
                

            origem = bytes(cabecalho[3:7])
            destino = bytes(cabecalho[7:11])
            
            ipOrigem = '{}.{}.{}.{}'.format(
                cabecalho[7], cabecalho[8], cabecalho[9], cabecalho[10]
            )
            
            # monta o cabeçalho de confirmação
            confirmacao = DELIMITADOR + sequenciaACK + destino + origem
            
            # incrementa mensagens corretas
            MENSAGENS_CORRETAS += 1
            
            #tenta enviar a confirmação, se ocorrer algum erro, ignora
            try:
                conexao.send(confirmacao)
            except:
                continue
        
        print('IP de origem:', ipOrigem)
        # escreve a mensagem recebida
        print("Mensagem:", mensagemCompleta)
        print("Estatísticas:")
        
        print("  - Quantidade de mensagens recebidas:", MENSAGENS_RECEBIDAS)
        
        print("  - Quantidade de mensagens com erros no CRC: {} | {:.2f}%".format(
            MENSAGENS_COM_ERROS_NO_CRC,
            MENSAGENS_COM_ERROS_NO_CRC/MENSAGENS_RECEBIDAS*100
        ))
        
        print("  - Quantidade de mensagens duplicadas: {} | {:.2f}%".format(
            MENSAGENS_DUPLICADAS,
            MENSAGENS_DUPLICADAS/MENSAGENS_RECEBIDAS*100
        ))
        
        print("  - Quantidade de mensagens corretas: {} | {:.2f}%".format(
            MENSAGENS_CORRETAS,
            MENSAGENS_CORRETAS/MENSAGENS_RECEBIDAS*100
        ))
        print()
        

        # tenta finalizar a conexão, caso ocorra um erro, ignora
        try:
            conexao.shutdown(socket.SHUT_WR)
        except:
            continue

        # fecha a conexão
        conexao.close()
        

main(sys.argv)