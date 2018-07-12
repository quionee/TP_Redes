#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

def main():
    # cria um socket com IPv4 e TCP

    DELIMITADOR = bytes.fromhex('7e')

    HOST = '127.0.0.1'
    PORT = 50017
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((HOST, PORT))
    sock.listen(1)

    mensagemFimTransmissao = "#exit"
    while True:
        conexao, addr = sock.accept()
        print('Connected by', addr)

        cabecalho = conexao.recv(11)
        print(cabecalho[1])

        sequenciaACK = bytes([(cabecalho[2] & 0x80) + 1])
        origem = bytes(cabecalho[3:7])
        destino = bytes(cabecalho[7:11])
        print(origem, destino)

        tamanhoDado = cabecalho[1] + 2
        dado = conexao.recv(tamanhoDado)
        print(dado.decode('ascii'))

        confirmacao = DELIMITADOR

        # print(dado.decode('ascii'))
        conexao.sendall('ok'.encode('ascii'))


        conexao.shutdown(socket.SHUT_WR)
        conexao.close()
        if(dado.decode('ascii') == mensagemFimTransmissao):
            return

main()