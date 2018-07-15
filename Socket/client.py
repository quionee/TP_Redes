#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import socket
import binascii
import copy
import time
import os
import signal
from crc import CRC

# classe utilizada no cálculo do time-out para tratamento de exceção
class TimeoutError(Exception):
    pass

# função utilizada no cálculo do time-out para tratamento de exceção
def handle_timeout(signum, frame):
    import errno
    raise TimeoutError(os.strerror(errno.ETIME))

# converte um texto para uma sequência binária, onde cada caractere será transformado em 8 bits
# retorno: binario (exemplo: "0b01101110")
# entrada: texto de caracteres ascii (exemplo: "abcde f g h ij kl m")
def completaASCII(texto):
    listaBinarios = "0b"
    
    for caracter in texto:
        # converte de ascii para binario
        novoCaracter = bin(int(binascii.hexlify(caracter.encode('ascii')), 16))
        novoCaracter = novoCaracter[2:]

        # acrescenta 0's a esquerda se necessario para completar os 8 bits de cada
        while(len(novoCaracter) < 8):
            novoCaracter = "0" + novoCaracter

        listaBinarios += novoCaracter

    return listaBinarios

# converte os decimais do endereço IP para sequências de binários
# entrada: lista com endereço IP (exemplo: ['127','0','0','1'])
# retorno: lista com endereço IP em binário com 8 bits cada
#          (exemplo: ['0b01111111','0b00000000','0b00000000','0b00000001'])
def converteIpParaBinario(ip):
    for i in range(len(ip)):
        ip[i] = bin(int(ip[i]))[2:]

        while(len(ip[i]) < 8):
            ip[i] = "0" + ip[i]
        ip[i] = "0b" + ip[i]

    return ip

# junta em uma única string binária os bytes (codificados em bits) em um array
# entrada: lista com endereço IP em binário com 8 bits cada
#          (exemplo: ['0b01111111','0b00000000','0b00000000','0b00000001'])
# retorno: um binário com todo o endereço IP concatenado
#          (exemplo: '0b01111111000000000000000000000001')
def uneBytes(bitsEnderecoIp):
    novaSequenciaBits = ''

    for byte in bitsEnderecoIp:
        novaSequenciaBits += byte[2:]

    return novaSequenciaBits

# gera um quadro para uma sequência de caracteres
# entrada: texto original, IP de origem, IP de destino, número de sequência do quadro
# retorno: quadro codificado em bytes
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

    # deixa cada caractere do texto com 8 bits e junta os bits do texto
    bitsTexto = completaASCII(texto)

    # byte da sequencia-ack codificado em binário
    sequenciaACK = "0b" + bitNumeroSequencia + "0000000"

    destino = converteIpParaBinario(ipDestino)
    origem = converteIpParaBinario(ipOrigem)

    # junta os bytes do endereco de origem
    bitsEnderecoOrigem = "0b" + uneBytes(origem)

    # junta os bytes do endereco de destino
    bitsEnderecoDestino = "0b" + uneBytes(destino)

    # junta todos os bits a serem enviados, exceto o delimitador
    mensagem =  tamanho + sequenciaACK[2:] + bitsEnderecoDestino[2:] 
    mensagem += bitsEnderecoOrigem[2:] + bitsTexto[2:]

    # calcula o crc com a sequencia de bytes ("0's a esquerda sao incluídos")
    crc = CRC()
    mensagem = DELIMITADOR + mensagem[2:] + crc.geraCRC(mensagem)[2:]
    mensagem = mensagem[2:]

    # converte o resultado retornado pelo CRC em bytes (codificados em bits) separados
    mensagemSeparada = []
    i = 0
    while(i < len(mensagem)):
        novaMensagem = "0b"
        novaMensagem += mensagem[i:(i + 8)]
        mensagemSeparada.append(novaMensagem)
        i += 8

    # converte os bytes (codificados em bits), gerados anteriormente, em hexadecimal
    # (se necessario acrescenta 0's para que cada byte tenha dois hexas)
    for i in range(len(mensagemSeparada)):
        mensagemSeparada[i] = str(hex(int(mensagemSeparada[i], 2)))[2:]
        while(len(mensagemSeparada[i]) < 2):
            mensagemSeparada[i] = "0" + mensagemSeparada[i] 

    # une todos os hexas (e consegue um Brasil hexa-campeão)
    mensagem = ""
    for item in mensagemSeparada:
        mensagem += item

    # converte os hexadecimais em um conjunto de bytes
    mensagem = bytes.fromhex(mensagem)

    return mensagem

# divide um texto em varios, cada um com tamanho máximo TAM_DADOS
# entrada: mensagem a ser dividida (exemplo: 'ab c e d f s ddsg g')
#          e a quantidade de caracteres máxima de cada partição
# retorno: lista com partições de texto divididas
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

# entrada: IP de origem e IP de destino (opcionais)
def main(args):
    # tamanho limite de dados do quadro
    TAM_DADOS = 255

    # ip da maquina de destino
    ipDestino = "127.0.0.1"
    # ip da maquina de origem
    ipOrigem = "127.0.0.1"

    # verifica se foram passados argumentos
    if(len(args) == 2):
        print("Número de argumentos inválido. Use zero ou dois argumentos.")
        return

    # se os IPs foram passados como argumentos, são atribuídos às suas respectivas variáveis
    if(len(args) > 1):
        ipOrigem = args[1]
        ipDestino = args[2]
    
    HOST = ipDestino
    PORT = 50017
    
    # divide o ip pelos pontos
    ipDestino = ipDestino.split(".")
    ipOrigem = ipOrigem.split(".")

    # leitura do texto de entrada
    texto = input()

    # divide o texto em pedaços
    mensagens = divideTexto(texto, TAM_DADOS)

    # gera um quadro para cada pedaço do texto
    for i in range (len(mensagens)):
        mensagens[i] = geraQuadro(mensagens[i], copy.deepcopy(ipOrigem), copy.deepcopy(ipDestino), str(i % 2))

    # cria socket e estabelece conexao
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    numeroSequenciaQuadro = 0
    i = 0
    while(i < len(mensagens)):
        # atribui time-out para receber a confirmação da mensagem enviada
        signal.signal(signal.SIGALRM, handle_timeout)
        signal.alarm(1)

        try:
            # descomente a linha abaixo para simular estouro do time-out
            # time.sleep(0.9987)
            sock.send(mensagens[i])

            # cancela excecao criada por estouro de tempo
            signal.alarm(0)

            # recebe resposta
            delimitador = sock.recv(1)
            sequenciaAckResposta = sock.recv(1)
            
            origem = sock.recv(4)
            destino = sock.recv(4)
            
            # converte a confirmação da mensagem para número inteiro
            sequenciaAckResposta = int(binascii.hexlify(sequenciaAckResposta), 16)

            # se o bit da confirmação for zero, significa que ocorreu um erro
            # e a mensagem é reenviada
            if(not(sequenciaAckResposta & 1)):
                print("Ocorreu um erro no envio da mensagem: confirmação inválida")
                continue

            sequenciaAckResposta = sequenciaAckResposta & 0xf0

            # se o ack de confirmação não for referente ao último quadro enviado,
            # reenvia o quadro
            if(numeroSequenciaQuadro ^ sequenciaAckResposta):
                print("ACK DUPLICADO")
                continue

            # calcula o próximo número de sequência
            numeroSequenciaQuadro = numeroSequenciaQuadro ^ 0x80
            print("OK")
            i += 1

        # trata excecao gerada por estouro do time-out
        except TimeoutError:
            print("Perdeu pacote")

        # cancela a excecao gerada por estouro de time-out
        finally:
            signal.alarm(0)

    # finaliza transmissão
    sock.shutdown(socket.SHUT_WR)
    sock.close()

main(sys.argv)


# testes aleatorios:
# eu quero pao arroz queijo camerngbsfvsvos aea
# mensagem imensa feita pra teste pq nao tenho paciencia de digitar porras muito grandes o tempo todo pq e chato p carai digitar toda hora uma mensagem afs a mensagem ta indo rapido jao desce mais pelamodedeus