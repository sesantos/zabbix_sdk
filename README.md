# Installation

python3.6 setup.py install

# Configuration parameters

Edit your setup.yaml file according to your environment.

bash-4.4# more setup.yaml 
zabbix_instance:
    ip: localhost 
    port: 8081 #default is 8080
    user: Admin
    password: zabbix
srlinux_setup:
    ip_range: "172.19.19.2-4,138.203.19.67"
    user_name: "admin"
    password: "admin"
    json_rpc_port: "80"
    snmp_community: "public"