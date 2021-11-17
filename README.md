# Installation

        python3.6 setup.py install

# Configuration parameters

Edit your ***setup.yaml*** file according to your environment.

```
zabbix_instance:
    ip: localhost 
    port: 80 #default is 80
    user: Admin
    password: zabbix
srlinux_setup:
    ip_range: "172.19.19.2-4,138.203.19.67"
    user_name: "admin"
    password: "admin"
    json_rpc_port: "80" 
    snmp_community: "public" #snmp comunity configured on SR Linux Devices
```

# Load the SR Linux template and create the discovery rules

```
zabbix_setup_srlinux_env -f templates/ -s setup.yaml
```

The SR Linux Template ***srlinux_template.yaml*** is loaded on zabbix instance and the discovery rule is created.

Note: The zabbix discovery rule uses snmp to discover the SR Linux host-name
The following configuration enabled the SNMP deamon on SR Linux

```
A:3-node-srlinux-A# info system snmp                                                                                                                                                               
    system {
        snmp {
            community public 
            network-instance mgmt {
                admin-state enable
            }
        }
    }
```
