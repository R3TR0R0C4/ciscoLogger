from netmiko import ConnectHandler
import json
import re
from datetime import datetime
import time
startTime=datetime.now()

def read_device_config(filepath):
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
        return config.get('device', {})
    except FileNotFoundError:
        print(f"Error: Arxiu de configuració no trobat: {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: format JSON no valid {filepath}")
        return None
    

def get_interface_info(device_config, interfaces):
    """
    Returns:
        list: A list of strings, where each string contains the output of the
              'show interface' command for a specific interface. Returns an
              empty list if connection fails or no interfaces are provided.
    """
    if not device_config or not interfaces:
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

        for interface in interfaces:
            command = f"show interface {interface}"
            interface_output = net_connect.send_command(command)
            output_list.append(f"{interface_output}")

        net_connect.disconnect()

    except Exception as e:
        print(f"An error occurred during information retrieval: {e}")

    return output_list



"""def  get_interface_host_info(device_config, interfaces):
    if not device_config or not interfaces:
        return []
    
    device = {
        "device_type": "cisco_ios_telnet",
        "port": 23,
        **device_config
    }
    output_list = []

    try:
        net_connect = ConnectHandler(**device)
        print(f"Successfully connected to {device['host']} for host info")

        for interface in interfaces:
            command = f"show run int {interface}"
            print(command)
            interface_output = net_connect.send_command(command)
            output_list.append(f"{interface_output}")

        net_connect.disconnect()

    except Exception as e:
        print(f"An error occurred during information retrieval: {e}")

    return output_list"""

def get_interface_info_privileged(config_filepath, interfaces):
    """
    Returns:
        list: A list of strings, where each string contains the output of the
              'show interface' command for a specific interface after entering
              enable mode. Returns an empty list if connection fails, no
              interfaces are provided, or enable mode cannot be reached.
    """
    if not interfaces:
        return []

    device_config = read_device_config(config_filepath)
    if not device_config:
        return []

    device = {
        "device_type": "cisco_ios_telnet",
        "port": 23,
        **device_config
    }
    output_list = []

    try:
        net_connect = ConnectHandler(**device)
        print(f"Successfully connected to {device['host']}")

        if device.get("secret"):
            try:
                net_connect.enable()
                print(f"Successfully entered enable mode on {device['host']}")
            except netmiko.NetmikoAuthenticationException as e:
                print(f"Error entering enable mode on {device['host']}: {e}")
                net_connect.disconnect()
                return []
        else:
            print(f"No enable secret provided for {device['host']}, assuming no enable required.")

        for interface in interfaces:
            command = f"show interface {interface}"
            interface_output = net_connect.send_command(command)
            output_list.append(f"{interface_output}")

        net_connect.disconnect()

    except Exception as e:
        print(f"An error occurred during information retrieval from {device['host']}: {e}")

    return output_list







def parse_interface_info(interface_text):
    """
    Parses the text output of a network interface and extracts relevant information.
    Args:
        interface_text: A string containing the output of a 'show interface' command for a single interface.
    Returns:
        A dictionary containing the extracted interface information.
    """
    interface_info = {}

    # Extract interface name
    interface_name_match = re.search(r'^(\S+) is', interface_text, re.MULTILINE)
    interface_info['interface_name'] = interface_name_match.group(1).lower() if interface_name_match else "NULL"

    # Extract last input
    last_input_match = re.search(r'Last input (never|\d{2}:\d{2}:\d{2})', interface_text)
    interface_info['last_input'] = last_input_match.group(1) if last_input_match else "NULL"

    # Extract last output
    last_output_match = re.search(r'output (never|\d{2}:\d{2}:\d{2})', interface_text)
    interface_info['last_output'] = last_output_match.group(1) if last_output_match else "NULL"

    # Add current log time
    interface_info['log_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extract description
    description_match = re.search(r'Description: (.+)', interface_text)
    interface_info['description'] = description_match.group(1).strip() if description_match else "NULL"

    # Extract duplex status
    duplex_match = re.search(r'(Full-duplex|Half-duplex|Auto-duplex)', interface_text)
    interface_info['duplex_status'] = duplex_match.group(1) if duplex_match else "NULL"

    # Extract speed
    speed_match = re.search(r'(\d+Mb/s|\d+Gb/s|Auto-speed)', interface_text)
    interface_info['speed'] = speed_match.group(1) if speed_match else "NULL"

    # Extract line status
    state_match = re.search(r'is (down|administratively down|up), line protocol is (down|up)', interface_text)
    if state_match:
        admin_state = state_match.group(1)
        protocol_state = state_match.group(2)
        if admin_state == "down":
            interface_info['state'] = "Not connected"
        elif admin_state == "administratively down":
            interface_info['state'] = "Shutdown"
        elif admin_state == "up" and protocol_state == "up":
            interface_info['state'] = "Connected"
        else:
            interface_info['state'] = "Unknown"
    else:
        interface_info['state'] = "NULL"

    return interface_info


def main():
    # crida read_device_config on es fá una connexió telnet, utilitza var config_file per user un .json amb info del switch i dump 
    config_file = 'Python/config/device.json'
    device_info = read_device_config(config_file)
    
    # una vegada executada la connexió comprobem si és correcta, si ho és passem a recollir dades
    if device_info:
    # Llistat de interfícies a fer les queries
        target_interfaces = []
        for i in range(1,49):
            target_interfaces.append(f"gi1/0/{i}")

    #Recollim les dades de les interfaces, cada interface a un element de llista:
    interface_outputs = get_interface_info(device_info, target_interfaces)
    interface_host_outputs = get_interface_info_privileged(config_file, target_interfaces)
    #print(interface_outputs)

    for i in interface_outputs:
        print("")
        parsed_ints=parse_interface_info(i)
        print(parsed_ints)

    for i in interface_host_outputs:
        print(i)

main()











endTime=datetime.now()
final_time=endTime-startTime
print(final_time)

##--------parse_interface_info
#interface_info['interface_name']  - Interface Name,                              eg, GigabitEthernet1/0/1  
#interface_info['last_input']      - Interface last comunication input,           eg, 00:01:00 , Never
#interface_info['last_output ']    - Interface last comunication output,          eg, 00:01:00 , Never
#interface_info['log_time']        - Time of the logging,                         eg, DD-MM-YYYY HH:MM:SS:MS
#interface_info['description']     - Interface description,                       eg, ofta_pc2_ts-pb015
#interface_info['duplex_status']   - Interface status of Duple                    eg, Full-duplex , Half-duplex , Auto-duplex
#interface_info['speed']           - Interface speed                              eg, 10Mb/s , 100Mb/s , 1Gb/s , Auto-Speed
#interface_info['state']           - Administrative status of the interface       eg, Not Connected , Shutdown , Connected , Unknown , NULL 


#--------get_interface_host_info
#interface_host_info['switchport'] - Interface Switchport type                    eg, Mode Access , Mode trunk
#interface_host_info['vlan']       - Interface vlan                               eg, Trunk , 180 , 186 , 20 ...
#interface_host_info['']
