#!/usr/bin/python3
from operator import le
import sys
import time
import telnetlib
import json
import re
import os
import statistics


def getOLTData(ip, user, password, port):
    placas = []
    data = {}
    pons = []
    a_sinal = []
    try:
        tn = telnetlib.Telnet(ip, port, 10)
    except Exception as e:
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
        tn.write("display board 0/{}\n".format(board).encode('utf-8'))
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
                
                os.system('zabbix_sender -z zabbix -s "{}" -k OntActive.[{}] -o {}'.format(hostname, pon, onu_provisionada))
                time.sleep(2)
                os.system('zabbix_sender -z zabbix -s "{}" -k OntOnline.[{}] -o {}'.format(hostname, pon, onu_online))
                time.sleep(2)

                     

    for pon in pons:
        f = pon.split('/')[0]
        s = pon.split('/')[1]
        p = pon.split('/')[2]
        tn.write("interface gpon {}/{}\n".format(f, s).encode('utf-8'))
        time.sleep(.3)
        tn.write("display ont optical-info {} all\n".format(p).encode('utf-8'))
        sinalList_return = tn.read_until('Control flag'.encode('utf-8'),
                                         3).decode('utf-8').splitlines()
        
        for linha in sinalList_return:

            if re.search(r'.*-[0-9]+\.[0-9]+', linha):
                srt_sinal = float(linha.split('-')[1].split(' ')[0])
                a_sinal.append(srt_sinal)
        if len(a_sinal) > 0:
            media = statistics.median_grouped(a_sinal)
            melhor = min(a_sinal, key=float)
            pior = max(a_sinal, key=float)
            #data[pon]["bestSinal"] = melhor * (-1)
            #data[pon]["mediaSinal"] = media * (-1)
            #data[pon]["poorSinal"] = pior * (-1)

        a_sinal = []
    

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
    


ip = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
port = sys.argv[4]
hostname = sys.argv[5]

getOLTData(ip, user, password, port, hostname)