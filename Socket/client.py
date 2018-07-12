#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket

def main():
    # cria um socket com IPv4 e TCP

    DELIMITADOR = bytes.fromhex('7e')
    
    # texto = 'Hello, I\'m here.'
    texto = input()
    tamanho = bytes([len(texto)])
    dado = texto.encode('ascii')
    
    sequenciaACK = bytes.fromhex('00')
    
    destino = bytes.fromhex('7f078001')
    origem = bytes.fromhex('7f000001')

    mensagem = DELIMITADOR + tamanho + sequenciaACK + destino + origem + dado
    print(mensagem)

    HOST = '127.0.0.1'
    PORT = 50017
    codigoFimTransmissao = "#exit"
    while True:
        # mensagem = input()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.sendall(mensagem)
        # sock.send(str(DELIMITADOR).encode('ascii'))
        sock.shutdown(socket.SHUT_WR)
        buf = sock.recv(1024)
        if not buf:
            return
        dado = buf
        sock.close()
        print('Received', repr(dado.decode('ascii')))
        break
        if(mensagem == codigoFimTransmissao):
            return

main()