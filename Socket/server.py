#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
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


def main():
    # flag delimitadora
    DELIMITADOR = bytes.fromhex('7e')

    # ACHO QUE TEM ALGO ERRADO AQUI
    # OLHEMOS DEPOIS
    HOST = '127.0.0.1'
    PORT = 50017
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)

    while True:
        conexao, addr = sock.accept()
        print('Connected by', addr)
        # lista com todos os bytes recebidos
        listaBytes = []

        # recebe os bytes do cabecalho
        cabecalho = b''
        cabecalho += conexao.recv(1)
        print("CABECALHO: ", cabecalho)
        for i in range(10):
            byteLido = conexao.recv(1)
            cabecalho += byteLido
            # adiciona os dados do cabeçalho a uma lista de bytes
            listaBytes.append(byteLido)
        
        print("CABECALHO: ", cabecalho)




        tamanhoDados = cabecalho[1]

        # recebe os bytes de dados
        dados = b""
        for i in range(tamanhoDados):
            dado = conexao.recv(1)
            dados += dado
            #adiciona os dados da mensagem a lista de bytes
            listaBytes.append(dado)        

        # recebe o codigo CRC gerado pelo cliente
        # e o adiciona à lista de bytes
        codigoCRC = conexao.recv(1)
        listaBytes.append(codigoCRC)
        codigoCRC = conexao.recv(1)
        listaBytes.append(codigoCRC)
        
        print("lista de bytes:", listaBytes)

        # transforma a lista de bytes em bits, completando zeros à esquerda
        mensagemBin = transformaEmBit(listaBytes)
        
        # verifica o CRC da mensagem
        crc = CRC()
        if(not crc.verificaCRC(mensagemBin)):
            # conexao.sendall('nop'.encode('ascii'))
            print("CRC invalido")
            conexao.shutdown(socket.SHUT_WR)
            conexao.close()
            continue


        print("dados:", dados.decode("ascii"))

        sequenciaACK = bytes([(cabecalho[2] & 0x80) + 1])
        origem = bytes(cabecalho[3:7])
        destino = bytes(cabecalho[7:11])
        
        confirmacao = DELIMITADOR + sequenciaACK + destino + origem
        print("CONFIRMACAO: ", confirmacao)
        conexao.sendall(confirmacao)


        conexao.shutdown(socket.SHUT_WR)
        conexao.close()

main()