#!/usr/bin/python3
from operator import le
import sys
import time
import telnetlib
import json
import re


def getOLTData(ip, user, password, port):
    count = 0
    placas = []
    data = []
    pons = []
    a_sinal=[]
    DataReturn = {
        'status': "sucesso",
        'consulta': "sucesso",
        'message': "Consulta realizada com sucesso!"
    }

    try:
        tn = telnetlib.Telnet(ip, port, 10)
    except Exception as e:
        DataReturn["status"] = "erro"
        DataReturn["consulta"] = "erro"
        DataReturn["message"] = "Erro ao conectar na OLT"
        print(json.dumps(DataReturn))
        return

    tn.read_until(b"name:")
    tn.write(user.encode('utf-8') + b"\n")
    time.sleep(.3)
    tn.read_until(b"password:")
    tn.write(password.encode('utf-8') + b"\n")
    time.sleep(.3)

    tn.write(b"enable\n")
    time.sleep(.3)
    tn.write(b"config\n")
    time.sleep(.3)
    tn.write(b"undo smart\n")
    time.sleep(.3)
    tn.write(b"scroll\n")
    time.sleep(.3)
    tn.write(b"display current-configuration | include interface gpon\n")
    time.sleep(.3)

    gponInterface_return = tn.read_until('Control flag'.encode('utf-8'),
                                         3).decode('utf-8').splitlines()

    for linha in gponInterface_return:
        if "interface gpon 0" in linha:
            srt_placa = linha.split('/')[1].lstrip().rstrip('\r')
            placas.append(srt_placa)
            time.sleep(.3)

    for board in placas:
        tn.write("display board 0/{}\n".format(board))
        board_return = tn.read_until('Control flag'.encode('utf-8'),
                                     3).decode('utf-8').splitlines()
        for linha in board_return:
            if "port 0/" in linha:
                srt_pon = linha.split(',')
                pon = srt_pon[0].split('port')[1].lstrip().rstrip(
                    '\r').replace(' ', '')
                onu_provisionada = int(
                    srt_pon[1].split(':')[1].lstrip().rstrip('\r'))
                onu_online = int(
                    srt_pon[2].split(':')[1].lstrip().rstrip('\r'))
                data.append({
                    pon: {
                        "onuProvisionada": onu_provisionada,
                        "onuOnline": onu_online,
                        "bestSinal": '',
                        "poorSinal": '',
                        "mediaSinal": ''
                    }
                })
                pons.append(pon)

    for pon in pons:
        f = pon.split('/')[0]
        s = pon.split('/')[1]
        p = pon.split('/')[2]
        tn.write("interface gpon {}/{}\n".format(f, s))
        time.sleep(.3)
        tn.write("display ont optical-info {} all\n".format(p))
        sinalList_return = tn.read_until('Control flag'.encode('utf-8'),
        
                                         3).decode('utf-8').splitlines()
        print(pon)
        for linha in sinalList_return:
            
            if re.search(r'.*-[0-9]+\.[0-9]+', linha):
                srt_sinal=float(linha.split('-')[1].split(' ')[0])
                a_sinal.append(srt_sinal)
            if len(a_sinal)>0:
                media=0
                for sinal in a_sinal:
                    media+sinal
                media=(media/int(len(a_sinal)))
                print(media)
            a_sinal=[]    




            


    # Fechando conexao com a OLT
    tn.write(b"quit\n")
    time.sleep(.3)
    tn.write(b"quit\n")
    time.sleep(.3)
    tn.write(b"quit\n")
    time.sleep(.3)
    tn.write("y".encode('utf-8') + b"\n")
    time.sleep(.3)
    tn.close()
    print(json.dumps(DataReturn))


ip = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
port = sys.argv[4]

getOLTData(ip, user, password, port)