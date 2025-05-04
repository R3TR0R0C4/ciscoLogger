import json
import netmiko
from netmiko import ConnectHandler 


def read_json_configs(filepath, read_type):
    """
    Inputs: 
        <filepath> Takes a filepath of a .json
        <read_type> What is the json attribute to read (device or database)
    Return:

    """
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
        return config.get(read_type, {})
    except FileNotFoundError:
        print(f"Error: Arxiu de configuració no trobat: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: format JSON no valid {filepath}")
        return None
    
def get_interface_info(device_config, interface_name, interface_number):
    """
    Inputs:
        device_config: The telnet information to connect to the device        
        interfaces: List of interfaces to query
    Sortida:
        output_list: List with each item being the result of the query
        'show interface' of each interface given by var 'interfaces'
    """
    if not device_config or interface_number or interface_name:
        return []

    device = {
        "device_type": "cisco_ios_telnet",
        "port": 23,
        **device_config
    }
    output_list = []

    try:
        net_connect = ConnectHandler(**device)
        print(f"Successfully connected to {device['host']} for interface status")
        print("Collecting interface status information")


        interfaces=[]
        if interface_name=="GigabitEthernet1/0/":
            for i in range(interface_number):
                interfaces.append(f"GigabitEthernet1/0/{i}")
        elif interface_name=="FastEthernet0/":
            for i in range(interface_number):
                interfaces.append(f"FastEthernet0/{i}")

        for interface in interfaces:
            command = f"show interface {interface}"
            interface_output = net_connect.send_command(command)
            output_list.append(f"{interface_output}")

        net_connect.disconnect()

    except Exception as e:
        print(f"There was a problem collecting information on regular mode: {e}")

    return output_list



def orchestrator():
    """
    Orchestrates all other functions
    """

    #1. Reading the json file for devices and saving it to <json_switch_details>
    json_switch_filepath="config/devices.json"
    read_type='device'
    json_switch_details=read_json_configs(json_switch_filepath,read_type)

    #2. Executing retrieval of "show interfaces" for regular interfaces
    regular_interfaces_names=json_switch_details['interface_names']
    regular_interfaces_number=json_switch_details['interface_number']

    regular_interface_output=None
    for i in range (len(json_switch_details)):
        regular_interface_output.append(get_interface_info(json_switch_details, regular_interfaces_names, regular_interfaces_number))

    print(regular_interface_output)


orchestrator()