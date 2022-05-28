#!/usr/bin/python3
import os
import sys
import json

export = {"data": []}

IP = sys.argv[1]
COMMUNITY = sys.argv[2]
OID = '1.3.6.1.2.1.31.1.1.1.1'

HOSTNAME = sys.argv[3]
USER = sys.argv[4]
PASS = sys.argv[5]
PORT = sys.argv[6]


cmd = "snmpwalk -v 2c -c {} {} {}".format(COMMUNITY, IP, OID)
return_snmpwalk = os.popen(cmd).read().splitlines()

for linha in return_snmpwalk:
    if "GPON" in linha:
        pon = linha.split('GPON')[1].replace(' ', '').replace('"', '')
        export["data"].append({"{#PONNAME}": pon})


os.system('python3 /usr/lib/zabbix/externalscripts/getOLTData.py {} {} {} {} {} &'.format(IP, USER, PASS, PORT, HOSTNAME))

print(json.dumps(export))
