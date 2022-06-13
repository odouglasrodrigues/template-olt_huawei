# Monitoramento OLT Huawei
##### Zabbix 5.0 +
##### Huawei R015 +


#### Baixe os arquivos .py e os coloque em: /usr/lib/zabbix/externalscripts/

##### Dê permissão de execução:
#
```sh
chmod +x /usr/lib/zabbix/externalscripts/*.py
```
#
##### Crie o arquivo de agendamento, dê permissão e reinicie o cron:
#
```sh
sudo echo "#ARQUIVO PARA AGENDAMENTO TEMPLATE OLT">/etc/cron.d/TemplateOLT
sudo chown root:zabbix /etc/cron.d/TemplateOLT
sudo chmod 777 /etc/cron.d/TemplateOLT
service cron restart
```
#

## License

MIT

**!**

