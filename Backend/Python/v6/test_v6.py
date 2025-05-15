"""import json
import netmiko
from netmiko import ConnectHandler 
from os import path
import re
from datetime import datetime
from zoneinfo import ZoneInfo

def get_interface_info_privileged(device_details):
    if not device_details:
        return []

    # Dict to make the connection info
    conn_info = {
        "host": device_details['host'],
        "username": device_details['username'],
        "password": device_details['password'],
        "device_type": "cisco_ios_telnet",
        "port": 23,
        "global_delay_factor": 2
    }

    # Add enable password directly to conn_info for robustness with Netmiko's enable()
    if 'enable_password' in device_details:
        conn_info['secret'] = device_details['enable_password']

    net_connect = None # Initialize to None for error handling

    try:
        net_connect = ConnectHandler(**conn_info)

        # Explicitly enter enable mode if an enable password was provided
        if 'enable_password' in device_details:
            net_connect.enable()

        # Connection and retrieval of each interface
        interface_output_list = []
        
        command = f"sho mac-address-table int f0/33"
        interface_output = net_connect.send_command(command)
        interface_output_list.append(interface_output.strip()) # .strip() to clean whitespace
        net_connect.disconnect()

    except Exception as e:
        print(f"An error occurred during connection or command execution for {device_details['host']}: {e}")
        # Only attempt to disconnect if net_connect object was successfully created
        if net_connect:
            try:
                net_connect.disconnect()
                print(f"Attempted to disconnect from {device_details['host']} after error.")
            except Exception as disconnect_e:
                print(f"Error during disconnect from {device_details['host']}: {disconnect_e}")
        interface_output_list = [f"Error on {device_details['host']}: {e}"]

    return interface_output_list

json_switch_details= "connection data"

print(get_interface_info_privileged(json_switch_details))"""

import re
#No MAC
#data = ['Mac Address Table\n-------------------------------------------\n\nVlan    Mac Address       Type        Ports\n----    -----------       --------    -----']

#One MAC
#data = ['Mac Address Table\n-------------------------------------------\n\nVlan    Mac Address       Type        Ports\n----    -----------       --------    -----\n   6    0018.2750.e926    DYNAMIC     Fa0/34\nTotal Mac Addresses for this criterion: 1']


#More than one MAC
data = ['Mac Address Table\n-------------------------------------------\n\nVlan    Mac Address       Type        Ports\n----    -----------       --------    -----\n 180    8cec.4b9c.da11    DYNAMIC     Fa0/31\n 180    8cec.4ba4.79e0    DYNAMIC     Fa0/31\n 180    e4e7.4905.b325    DYNAMIC     Fa0/31\nTotal Mac Addresses for this criterion: 3']

mac_table_text = data[0]

# Extract MAC addresses
mac_matches = re.findall(r'\b[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\b', mac_table_text)
unformatted_mac = mac_matches if mac_matches else []


if len(unformatted_mac) == 1:
    formatted_mac = ':'.join("8CEC.4B9C.DA11".replace('.', '').upper()[i:i+2] for i in range(0, 12, 2)) 

elif len(unformatted_mac) > 1:
    formatted_mac=[]
    for i in unformatted_mac:
        formatted_mac.append(':'.join("8CEC.4B9C.DA11".replace('.', '').upper()[i:i+2] for i in range(0, 12, 2)))



print(formatted_mac)
