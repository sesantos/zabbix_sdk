from pyzabbix import ZabbixAPI, ZabbixAPIException
import os
import sys
import glob
import argparse
import yaml


def main():

    parser = argparse.ArgumentParser(description="Uploads SRLinux template to Zabbix Instance")
    parser.add_argument("-folder", "--f", nargs=1, metavar="templates folder name", required=True, help="folder containing .yaml SR Linux Template")
    parser.add_argument("-setup", "--s", nargs=1, metavar="setup configuration file", required=True, help="setup.yaml zabbix envirnoment file")

        
    args = parser.parse_args()


    if args.s:
        if args.s[0].endswith(".yaml"):
            file = os.path.abspath(args.s[0])
            print(file)
            with open(file, "r") as stream:
                try:
                    setup=yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)

        

    zabbix_ip=setup['zabbix_instance']['ip']
    zabbix_port=setup['zabbix_instance']['port']
    zabbix_user=setup['zabbix_instance']['user']
    zabbix_password=setup['zabbix_instance']['password']

    srlinux_iprange=setup['srlinux_setup']['ip_range']
    srlinux_username=setup['srlinux_setup']['user_name']
    srlinux_password=setup['srlinux_setup']['password']
    srlinux_jsonrpc_port=setup['srlinux_setup']['json_rpc_port']
    srlinux_jsonrpc_proto=setup['srlinux_setup']['proto']
    
    if srlinux_jsonrpc_proto not in ['http','https']:
        print("Only protocols http or https are allowed, please fix you srlinux_setup:proto in setup.yaml")
        exit(1)
        
    srlinux_snmp_comunity=setup['srlinux_setup']['snmp_community']



    zapi = ZabbixAPI("http://"+str(zabbix_ip)+":"+str(zabbix_port))
    zapi.login(zabbix_user, zabbix_password)
    # You can also authenticate using an API token instead of user/pass with Zabbix >= 5.4
    # zapi.login(api_token='xxxxx')
    print("Connected to Zabbix API Version %s" % zapi.api_version())

    rules = {
        'discoveryRules': {
            'createMissing': True,
            'updateExisting': True
        },
        'graphs': {
            'createMissing': True,
            'updateExisting': True
        },
        'groups': {
            'createMissing': True,
            'updateExisting': True
        },
        'hosts': {
            'createMissing': True,
            'updateExisting': True
        },
        'images': {
            'createMissing': True,
            'updateExisting': True
        },
        'items': {
            'createMissing': True,
            'updateExisting': True
        },
        'maps': {
            'createMissing': True,
            'updateExisting': True
        },
        'templateLinkage': {
            'createMissing': True,
        },
        'templates': {
            'createMissing': True,
            'updateExisting': True
        },
        'templateDashboards': {
            'createMissing': True,
            'updateExisting': True
        },
        'triggers': {
            'createMissing': True,
            'updateExisting': True
        },
        'valueMaps': {
            'createMissing': True,
            'updateExisting': True
        },
    }

    if os.path.isdir(args.f[0]):
        #path = path/*.xml
        files = glob.glob(args.f[0]+'/*.yaml')
        for file in files:
            print(file)
            with open(file, 'r') as f:
                template = f.read()
                try:
                    template=zapi.confimport('yaml', template, rules)
                except ZabbixAPIException as e:
                    print(e)
            print('')
    elif os.path.isfile(args.f[0]):
        files = glob.glob(args.f[0])
        for file in files:
            with open(file, 'r') as f:
                template = f.read()
                try:
                    template=zapi.confimport('yaml', template, rules)
                except ZabbixAPIException as e:
                    print(e)
        else:
            print('I need a .yaml file')
            exit(1)


    groupid=zapi.hostgroup.get(output="id",filter={"name":"SRLinux"})
    groupid=groupid[0]['groupid']

    templateid=zapi.template.get(output="id",filter={"name":"SRLinux_Template"})
    templateid=templateid[0]['templateid']

    zapi.template.update(templateid=templateid,macros=[{"macro":"{$PWD}","value":srlinux_password}, 
                                                    {"macro":"{$JSONPORT}","value":srlinux_jsonrpc_port}, 
                                                    {"macro":"{$PROTO}","value":srlinux_jsonrpc_proto},
                                                    {"macro":"{$USER}","value":srlinux_username}, 
                                                    {"macro":"{$IPADDR}", "value":""}])

    drulesrlinux = { 
                    "name": "srlinux",
                    "iprange": srlinux_iprange,
                    "delay": "5s",
                    "dchecks": [
                    {
                        "type": "4",
                        "ports": "80",
                        "uniq": "0"
                    },
                    {
                        "type": "11",
                        "ports": "161",
                        "snmp_community": srlinux_snmp_comunity,
                        "key_": "sysName.0",
                        "uniq": "0",
                        "host_source": "3",
                        "name_source": "3"	
                    },
                    ]
                    }




    druleid=zapi.drule.get(output="id",filter={"name":"srlinux"})

    if druleid:
        drule_action=zapi.action.get(output="id",filter={"name":"SR Linux Discovery action"})
        if drule_action:
            zapi.action.delete(params=drule_action[0]['actionid'])
            zapi.drule.delete(params=druleid[0]['druleid'])

    druleid=zapi.drule.create(drulesrlinux)
    druleid=druleid["druleids"][0]


    dactionsrlinux = {
            "name": "SR Linux Discovery action",
            "eventsource": 1,
            "status": 0,
            "esc_period": "0s",
            "filter": {
                "evaltype": 0,
                "conditions": [
                    {
                        "conditiontype": 18,
                        "operator": "0",
                        "value": druleid
                    },
                ]
            },
            "operations": [
                {
                    "opgroup": [
                        {
                            "groupid": groupid,
                        }
                    ],
                    "operationtype": 4,
                },
                {
                    "optemplate": [
                        {
                            "templateid": templateid,
                        }
                    ],
                    "operationtype": 6,
                },
                {
                    "opinventory": {
                        "inventory_mode": 1,
                    },
                    "operationtype": 10,
                },
                
            ]


    }

    zapi.action.create(dactionsrlinux)

if __name__ == "__main__":
    main()