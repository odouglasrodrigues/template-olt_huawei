#!/usr/bin/python3
import sys
import time
import telnetlib
import os


def getOLTData(ip, user, password, port, hostname):
    #    start_time = time.time()
    totalProvisionado = 0
    totalOnline = 0
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
            onu_provisionada = int(
                srt_pon[1].split(':')[1].lstrip().rstrip('\r'))
            onu_online = int(srt_pon[2].split(':')[1].lstrip().rstrip('\r'))

            totalProvisionado = (totalProvisionado + onu_provisionada)
            totalOnline = (totalOnline + onu_online)

            os.system(
                'zabbix_sender -z zabbix -s "{}" -k OntOnline.[{}] -o {}'.
                format(hostname, pon, onu_online))
            time.sleep(1)
            os.system(
                'zabbix_sender -z zabbix -s "{}" -k OntOffline.[{}] -o {}'.
                format(hostname, pon, onu_provisionada-onu_online))
            time.sleep(1)

    os.system('zabbix_sender -z zabbix -s "{}" -k TotalOntActive -o {}'.format(
        hostname, totalProvisionado))
    time.sleep(1)
    os.system('zabbix_sender -z zabbix -s "{}" -k TotalOntOnline -o {}'.format(
        hostname, totalOnline))
    time.sleep(1)
    os.system('zabbix_sender -z zabbix -s "{}" -k TotalOntOffline -o {}'.format(
        hostname, totalProvisionado-totalOnline))
    time.sleep(1)

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


#   finish_time = time.time()
#   tempo_gasto = (finish_time - start_time)
#   print('O Script foi executado em {} segundos'.format(tempo_gasto))

ip = sys.argv[1]
user = sys.argv[2]
password = sys.argv[3]
port = sys.argv[4]
hostname = sys.argv[5]

getOLTData(ip, user, password, port, hostname)
