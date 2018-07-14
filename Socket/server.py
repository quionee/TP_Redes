#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import sys
import random
from crc import CRC

# transforma um array de bytes em uma sequencia de bits
def transformaEmBit(listaBytes):
    resultado = "0b"
    for item in listaBytes:
        item = bin(int(str(item.hex()), 16))[2:]
        while(len(item) < 8):
            item = "0" + item
        resultado += item
    return resultado

def leBytes(conexao, qtdBytes):
    listaBytes = []
    for i in range(qtdBytes):
        byteLido = conexao.recv(1)
        # adiciona os dados do cabeçalho a uma lista de bytes
        listaBytes.append(byteLido)
    return listaBytes

def juntaBytes(listaDeBytes):
    resultado = b''
    for byte in listaDeBytes:
        resultado += byte
    return resultado

def main(args):
    SEQUENCIA_ZERO = bytes.fromhex('00')
    SEQUENCIA_UM = bytes.fromhex('80')
    # flag delimitadora
    DELIMITADOR = bytes.fromhex('7e')

    # ACHO QUE TEM ALGO ERRADO AQUI
    # OLHEMOS DEPOIS
    HOST = '127.0.0.1'
    if(len(args) > 1):
        print(args[1])
        HOST = args[1]
    PORT = 50017
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)
    while True:
        conexao, addr = sock.accept()
        print(conexao)
        fimMensagem = False
        mensagemCompleta = ''
        ultimoRecebido = '0b10000000'
        while (not fimMensagem):
            cabecalho = b''
            cabecalho += conexao.recv(1)
            if(len(cabecalho) <= 0):
                fimMensagem = True
                continue
            # lista com todos os bytes recebidos
            print('')
            listaBytes = leBytes(conexao, 10)

            # recebe os bytes do cabecalho
            # print("CABECALHO: ", cabecalho)  print("CABECALHO: ", cabecalho)

            cabecalho += juntaBytes(listaBytes)
            # print("CABECALHO: ", cabecalho)

            tamanhoDados = cabecalho[1]

            # recebe os bytes de dados
            listaDados = leBytes(conexao, tamanhoDados)
            listaBytes += listaDados
            dados = b'' + juntaBytes(listaDados)

            # print("dados: ", dados)

            # recebe o codigo CRC gerado pelo cliente
            # e o adiciona à lista de bytes
            codigoCRC = conexao.recv(1)
            listaBytes.append(codigoCRC)
            codigoCRC = conexao.recv(1)
            listaBytes.append(codigoCRC)
            
            # print("lista de bytes:", listaBytes)

            # transforma a lista de bytes em bits, completando zeros à esquerda
            mensagemBin = transformaEmBit(listaBytes)
            if(random.random() > 0.95):
                print("Invertendo")
                posicao = random.randrange(0, tamanhoDados)
                mensagemBin = list(mensagemBin)
                mensagemBin[posicao] = bin(int(mensagemBin[posicao]) ^ 0x01)[2:]
            
            # verifica o CRC da mensagem
            crc = CRC()
            sequenciaACK = bytes([(cabecalho[2] & 0x80) + 1])
            print("SEQUENCIA ACK: ", sequenciaACK)
            print("cabecalho 2:", (cabecalho[2] & 0x80))
            
            if((int(ultimoRecebido, 2) ^ (cabecalho[2] & 0x80)) and crc.verificaCRC(mensagemBin)):
                print("mensagem completa:", mensagemCompleta)
                mensagemCompleta += dados.decode("ascii")
                ultimoRecebido = bin(int(ultimoRecebido, 2) ^ 0x80)
            else:
                print("Seq ACK 1:", sequenciaACK)
                sequenciaACK = bytes([int.from_bytes(sequenciaACK, byteorder='big') ^ 0x80])
                print("Seq ACK 2:", sequenciaACK)

            print("ultimoRecebido", ultimoRecebido)

            origem = bytes(cabecalho[3:7])
            destino = bytes(cabecalho[7:11])
            
            confirmacao = DELIMITADOR + sequenciaACK + destino + origem
            # print("CONFIRMACAO: ", confirmacao)
            try:
                conexao.send(confirmacao)
            except:
                continue
        
        # print("TUDO:", mensagemCompleta)

        try:
            conexao.shutdown(socket.SHUT_WR)
        except:
            continue
        conexao.close()

main(sys.argv)