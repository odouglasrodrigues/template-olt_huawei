#!/usr/bin/python3
import os
import sys
import json


def main(ip, community, oid, hostname, user, password, port):

    export = {"data": []}

    cmd = 'snmpwalk -v 2c -c {} {} {}| grep -i "gpon"'.format(community, ip, oid)
    return_snmpwalk = os.popen(cmd).read().splitlines()

    for linha in return_snmpwalk:
        pon = linha.split('GPON')[1].replace(' ', '').replace('"', '')
        index = linha.split('=')[0].split('.')[11].replace(' ', '')
        cmd_alias='snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.31.1.1.1.18.{}'.format(community, ip, index)
        alias_return = os.popen(cmd_alias).read()
        alias=""
        if "STRING" in alias_return:
            alias=alias_return.split(':')[1].replace(' ', '').replace('"', '').lstrip().rstrip()
        export["data"].append({"{#PONNAME}": pon, "{#PONALIAS}":alias, "{#INDEX}":index})
        

    print(json.dumps(export))
    return


ip = sys.argv[1]
community = sys.argv[2]
oid = '1.3.6.1.2.1.31.1.1.1.1'
oid_alias ='1.3.6.1.2.1.31.1.1.1.18'

hostname = sys.argv[3]
user = sys.argv[4]
password = sys.argv[5]
port = sys.argv[6]

main(ip, community, oid, hostname, user, password, port)

