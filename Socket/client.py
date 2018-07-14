#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket
import binascii
import copy
import time
from crc import CRC

# converte o texto para uma sequencia de bytes com oito bits exatos cada
# retorno: binario (exemplo: "0b01101110")
# entrada: texto de caracteres ascii (exemplo: "abcde f g h ij k")
def completaASCII(texto):
    listaBinarios = "0b"
    
    for caracter in texto:
        # converte de ascii para binario
        novoCaracter = bin(int(binascii.hexlify(caracter.encode('ascii')), 16))
        novoCaracter = novoCaracter[2:]

        # acrescenta 0's a esquerda se necessario
        while(len(novoCaracter) < 8):
            novoCaracter = "0" + novoCaracter

        listaBinarios += novoCaracter

    return listaBinarios

def converteIpParaBinario(ip):
    # deixa o ip com 8 bits
    for i in range(len(ip)):
        ip[i] = bin(int(ip[i]))[2:]
        while(len(ip[i]) < 8):
            ip[i] = "0" + ip[i]
        ip[i] = "0b" + ip[i]
    return ip

# junta os bytes de um array de bytes codificados em bits
def uneBytes(bitsEnderecoIp):
    novaSequenciaBits = ''
    for byte in bitsEnderecoIp:
        novaSequenciaBits += byte[2:]
    return novaSequenciaBits

def geraQuadro(texto, ipOrigem, ipDestino, bitNumeroSequencia):
    # flag delimitador ("~")
    DELIMITADOR = "0b01111110"
    
    # tamanho do texto de entrada
    tamanho = bin(len(texto))
    tamanho = tamanho[2:]

    # deixa o tamanho com 8 bits
    while(len(tamanho) < 8):
        tamanho = "0" + tamanho
    tamanho = "0b" + tamanho
    
    print("TAMANHO", int(tamanho, 2))

    # deixa cada caractere do texto com 8 bits e 
    # junta os bits do texto
    bitsTexto = completaASCII(texto)

    # byte da sequencia-ack
    sequenciaACK = "0b" + bitNumeroSequencia + "0000000"

    destino = converteIpParaBinario(ipDestino)
    origem = converteIpParaBinario(ipOrigem)

    # junta os bytes do endereco de origem
    bitsEnderecoOrigem = "0b" + uneBytes(origem)

    # junta os bytes do endereco de destino
    bitsEnderecoDestino = "0b" + uneBytes(destino)

    # junta todos os bits
    mensagem =  tamanho + sequenciaACK[2:] + bitsEnderecoDestino[2:] 
    mensagem += bitsEnderecoOrigem[2:] + bitsTexto[2:]

    # calcula o crc com a sequencia de bytes ("0's a esquerda sao incluidos")
    crc = CRC()
    mensagem = DELIMITADOR + mensagem[2:] + crc.geraCRC(mensagem)[2:]
    mensagem = mensagem[2:]

    # converte o resultado retornado pelo CRC em bytes separados
    mensagemSeparada = []
    i = 0
    while(i < len(mensagem)):
        novaMensagem = "0b"
        novaMensagem += mensagem[i:(i+8)]
        mensagemSeparada.append(novaMensagem)
        i += 8

    # converte os bytes gerados logo antes em hexadecimal 
    # (se necessario acrescenta 0's para que cada byte tenha dois hexas)
    for i in range(len(mensagemSeparada)):
        mensagemSeparada[i] = str(hex(int(mensagemSeparada[i], 2)))[2:]
        while(len(mensagemSeparada[i]) < 2):
            mensagemSeparada[i] = "0" + mensagemSeparada[i] 
    
    # une todos os hexas
    mensagem = ""
    for item in mensagemSeparada:
        mensagem += item

    # converte os hexadecimais em um conjunto de bytes
    mensagem = bytes.fromhex(mensagem)
    return mensagem

# divide um texto em varios, cada um com tamanho TAM_DADOS
def divideTexto(texto, TAM_DADOS):
    mensagens = []
    posicao = 0
    
    while(posicao < len(texto)):
        if((posicao + TAM_DADOS) < len(texto)):
            mensagens.append(texto[posicao:posicao + TAM_DADOS])
        else:
            mensagens.append(texto[posicao:])
        posicao += TAM_DADOS
    
    return mensagens


def main(args):
    # tamanho limite de dados do quadro
    TAM_DADOS = 20
    # ip da maquina de destino
    ipDestino = "127.0.0.1"
    # ip da maquina de origem
    ipOrigem = "127.0.0.1"
    if(len(args) > 1):
        ipDestino = args[1]
    # divide o ip pelos pontos
    ipDestino = ipDestino.split(".")
    ipOrigem = ipOrigem.split(".")

    # print(ipOrigem, ipDestino)

    # leitura do texto de entrada
    texto = input()

    mensagens = divideTexto(texto, TAM_DADOS)

    for i in range (len(mensagens)):
        mensagens[i] = geraQuadro(mensagens[i], copy.deepcopy(ipOrigem), copy.deepcopy(ipDestino), str(i % 2))

    # OLHEM ISSO, BRENEEEEX !!!!!!!!!!!
    # O HOST NAO ERA PRA SER IP DESTINO??
    HOST = '127.0.0.1'
    PORT = 50017

    # cria socket e estabelece conexao
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    i = 0
    while(i < len(mensagens)):
        # recebe resposta
        sock.send(mensagens[i])
        time.sleep(1)
        delimitador = sock.recv(1)
        sequenciaAckResposta = sock.recv(1)
        origem = sock.recv(4)
        destino = sock.recv(4)
        print("DELMI", delimitador)
        print("seqAckR: ", sequenciaAckResposta)
        sequenciaAckResposta = int(binascii.hexlify(sequenciaAckResposta), 16)

        print("seqAckRCCCC: ", sequenciaAckResposta)
        if(not (sequenciaAckResposta & 1)):
            sock.send(mensagens[i])
            print("ENTREI NO IF")
            continue
        
        print('Received', repr(sequenciaAckResposta))
        i += 1
    sock.shutdown(socket.SHUT_WR)
    sock.close()

main(sys.argv)


# eu quero pao arroz queijo camerngbsfvsvos aea
