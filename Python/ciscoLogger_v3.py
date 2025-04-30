from netmiko import ConnectHandler
import json
import re
from datetime import datetime

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
        print(f"Successfully connected to {device['host']} via Telnet")

        for interface in interfaces:
            command = f"show interface {interface}"
            interface_output = net_connect.send_command(command)
            output_list.append(f"{interface_output}")

        net_connect.disconnect()
        print("Telnet connection closed.")

    except Exception as e:
        print(f"An error occurred during information retrieval: {e}")

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
    speed_match = re.search(r'(\d+Mb/s|\d+Gb/s)', interface_text)
    interface_info['speed'] = speed_match.group(1) if speed_match else "NULL"

    return interface_info


config_file = 'Python/config/device.json'
device_info = read_device_config(config_file)

if device_info:
    #Llistat de interfícies a fer les queries
    target_interfaces = []
    for i in range(1,49):
        target_interfaces.append(f"gi1/0/{i}")

    #Corre la funcio per recollir la info de cada interfície
    interface_outputs = get_interface_info(device_info, target_interfaces)
    print(interface_outputs)
    if interface_outputs:
        interface_outputs=parse_interface_info(interface_outputs)
        for output in interface_outputs:
            parsed_info = parse_interface_info(output)
            print(f"Interface Name: {parsed_info['interface_name']}")
            print(f"Last Input: {parsed_info['last_input']}")
            print(f"Last Output: {parsed_info['last_output']}")
            print(f"Log Time: {parsed_info['log_time']}")
            print(f"Description: {parsed_info['description']}")
            print(f"Duplex Status: {parsed_info['duplex_status']}")
            print(f"Speed: {parsed_info['speed']}")
            print("-" * 20)

    else:
        print("No interface information retrieved.")

else:
    print("Failed to load device configuration. Please check the configuration file.")