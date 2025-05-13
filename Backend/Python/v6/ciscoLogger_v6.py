import json
import netmiko
from netmiko import ConnectHandler 
from os import path


def read_json_configs(filepath, read_type):
    """
    Inputs: 
        <filepath> Takes a filepath of a .json
        <read_type> What is the json attribute to read (device or database)
    Return:
        output_config: The configuration used to connect to switches and their information
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

def get_interface_info(device_details,interface_type, interface_number):
    if not device_details:
        return []
    

    conn_info = {
        "host": device_details['host'],
        "username": device_details['username'],
        "password": device_details['password'],
        "device_type": "cisco_ios_telnet",
        "port": 23,
    }


    try:
        net_connect = ConnectHandler(**conn_info)

        print(f"Retrieving interface information from {device_details['host']} for {interface_type}{interface_number}")


        start, end = map(int, interface_number.split("-"))
        interface_range = range(start, end+1)

        interfaces_to_query=[]
        for interface in interface_range:
            interfaces_to_query.append(f"{interface_type}{interface}")

        interface=None
        interface_output_list=[]
        for interface in interfaces_to_query:
            command = f"show interface {interface}"
            interface_output = net_connect.send_command(command)
            interface_output_list.append(f"{interface_output}")
        net_connect.disconnect()


    except Exception as e:
        print(f"An error occurred: {e}")
        if 'net_connect' in locals():
            net_connect.disconnect()

    return interface_output_list




def orchestrator():
    """
    Orchestrates all other functions
    """

    # build of the pwd to open the directory config without problems
    base_dir = path.dirname(path.abspath(__file__)) 
    json_switch_filepath = path.join(base_dir, 'config', 'devices.json')
    
    #Reading the json file for devices and saving it to <json_switch_details>
    read_type='device'
    json_switch_details=read_json_configs(json_switch_filepath,read_type)


    switch_interface_detail=[]
    #Iterate list of Switches from the json
    for switch_detail in json_switch_details: # type: ignore
        #Get regular interface info
        regular_ints_results=get_interface_info(switch_detail, switch_detail["interface_names"], switch_detail["interface_number"])

        
        #Get uplink interfaces info
        uplink_ints_results=get_interface_info(switch_detail, switch_detail["uplink_names"], switch_detail["uplink_number"] )
        for i in uplink_ints_results:#Append of all the uplink interfaces to the previous list to keep it all in one list
            regular_ints_results.append(i)

        #print(regular_ints_results) #List with all the switch interfaces info.
        switch_interface_detail[switch_detail["host"]]=regular_ints_results

    print(switch_interface_detail)
    
orchestrator()
