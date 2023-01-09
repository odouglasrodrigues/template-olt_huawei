#!/usr/bin/python3
import sys
import time
import telnetlib
import re
import os
import statistics


def getOLTData(ip, user, password, port, hostname):
    # start_time = time.time()
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
    tn.write(b"display ont info 0 all | include port 0\n")
    time.sleep(20)

    board_return = tn.read_until('Control flag'.encode('utf-8'),
                                 3).decode('utf-8').splitlines()

    for linha in board_return:
        if "port 0/" in linha:
            srt_pon = linha.split(',')
            pon = srt_pon[0].split('port')[1].lstrip().rstrip('\r').replace(
                ' ', '')
            pons.append(pon)

    for pon in pons:
        f = pon.split('/')[0]
        s = pon.split('/')[1]
        p = pon.split('/')[2]
        tn.write("interface gpon {}/{}\n".format(f, s).encode('utf-8'))
        time.sleep(.3)
        tn.write("display ont optical-info {} all\n".format(p).encode('utf-8'))
        time.sleep(12)
        sinalList_return = tn.read_until('Control flag'.encode('utf-8'),
                                         3).decode('utf-8').splitlines()

        for linha in sinalList_return:
            if re.search(r'.*-[0-9]+\.[0-9]+', linha):
                try:
                    srt_sinal = float(linha.split('-')[2].split(' ')[0])
                    a_sinal.append(srt_sinal)
                except:
                    continue
        if len(a_sinal) > 0:
            media = statistics.median_grouped(a_sinal) * (-1)
            melhor = min(a_sinal, key=float) * (-1)
            pior = max(a_sinal, key=float) * (-1)
            os.system(
                'zabbix_sender -z 127.0.0.1 -s "{}" -k OntBestSinal.[{}] -o {}'.
                format(hostname, pon, melhor))
            time.sleep(1)
            os.system(
                'zabbix_sender -z 127.0.0.1 -s "{}" -k OntPoorSinal.[{}] -o {}'.
                format(hostname, pon, pior))
            time.sleep(1)
            os.system(
                'zabbix_sender -z 127.0.0.1 -s "{}" -k OntMediaSinal.[{}] -o {}'.
                format(hostname, pon, media))
            time.sleep(1)

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
    # finish_time = time.time()
    # tempo_gasto = (finish_time - start_time)
    # print("O Script foi executado em {} segundos".format(tempo_gasto))


ip = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
port = sys.argv[4]
hostname = sys.argv[5]

getOLTData(ip, user, password, port, hostname)
