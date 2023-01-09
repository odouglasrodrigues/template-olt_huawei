#!/usr/bin/python3
import os
import sys
import json


def CronModify(ip, user, password, port, hostname):
    return_cron = os.popen("cat /etc/cron.d/TemplateOLT").read().splitlines()

    for cron in return_cron:
        if hostname in cron:
            return
    os.system('sudo chmod 777 /etc/cron.d/TemplateOLT')
    time.sleep(.4)
    os.system(
        'sudo echo "27 */2 * * * zabbix python3 -u /usr/lib/zabbix/externalscripts/GetONUSignal.py {} {} {} {} {} &">>/etc/cron.d/TemplateOLT'
        .format(ip, user, password, port, hostname))
    time.sleep(.4)
    os.system(
        'sudo echo "*/6 * * * * zabbix python3 -u /usr/lib/zabbix/externalscripts/GetONUOnline.py {} {} {} {} {} &">>/etc/cron.d/TemplateOLT'
        .format(ip, user, password, port, hostname))
    time.sleep(.4)
    os.system('sudo chmod 644 /etc/cron.d/TemplateOLT')




def main(ip, community):

    export = {"data": []}

    cmd = 'snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.31.1.1.1.1 | grep -i "gpon"'.format(
        community, ip)
    return_snmpwalk = os.popen(cmd).read().splitlines()

    for linha in return_snmpwalk:
        pon = linha.split('GPON')[1].replace(' ', '').replace('"', '')
        index = linha.split('=')[0].split('.')[11].replace(' ', '')
        cmd_alias = 'snmpwalk -v 2c -c {} {} 1.3.6.1.2.1.31.1.1.1.18.{}'.format(
            community, ip, index)
        alias_return = os.popen(cmd_alias).read()
        alias = ""
        if "STRING" in alias_return:
            alias = alias_return.split(':')[1].replace(' ', '').replace(
                '"', '').lstrip().rstrip()
        export["data"].append({
            "{#PONNAME}": pon,
            "{#PONALIAS}": alias,
            "{#INDEX}": index
        })

    print(json.dumps(export))
    CronModify(ip, user, password, port, hostname)
    return


ip = sys.argv[1]
community = sys.argv[2]
hostname = sys.argv[3]
user = sys.argv[4]
password = sys.argv[5]
port = sys.argv[6]

main(ip, community)
