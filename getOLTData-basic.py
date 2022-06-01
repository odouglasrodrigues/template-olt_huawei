#!/usr/bin/python3
from operator import le
import sys
import time
import telnetlib
import json


def getOLTData(ip, user, password, port):
    placas = []
    data = {}
    pons = []
    export={"data":[]}
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
    time.sleep(5)

    gponInterface_return = tn.read_until('Control flag'.encode('utf-8'),
                                         3).decode('utf-8').splitlines()

    for linha in gponInterface_return:
        if "interface gpon 0" in linha:
            srt_placa = linha.split('/')[1].lstrip().rstrip('\r')
            placas.append(srt_placa)
            time.sleep(5)

    for board in placas:
        tn.write("display board 0/{}\n".format(board).encode('utf-8'))
        time.sleep(3)
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
                data[pon] = {
                    "onuProvisionada": onu_provisionada,
                    "onuOnline": onu_online,
                    "bestSinal": 0.0,
                    "poorSinal": 0.0,
                    "mediaSinal": 0.0
                }

                pons.append(pon)
                export["data"].append({"{#PONNAME}":pon})

    print(json.dumps(export))        

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

getOLTData(ip, user, password, port)