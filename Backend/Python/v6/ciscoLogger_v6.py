import json
import netmiko
from netmiko import ConnectHandler 
from os import path
import re
from datetime import datetime
from zoneinfo import ZoneInfo


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

def get_interface_info(device_details,interface_type,interface_number):
    """
    Inputs:
        <device_details> Dictionary with the connection details 
        <interface_type> Type of interface (either gigabitethernet or fasterthernet)
        <interface_number> (number range ex 1-48 1-2)
    Return:
        List with the output of the command of each interface as one item
    """
    if not device_details:
        return []
    
    #Dict to make the connection info
    conn_info = { 
        "host": device_details['host'],
        "username": device_details['username'],
        "password": device_details['password'],
        "device_type": "cisco_ios_telnet",
        "port": 23,
    }

    #Try to connect and retrieve each of the interfaces current config
    try:
        net_connect = ConnectHandler(**conn_info)
        print(f"Retrieving interface information from {device_details['host']} for {interface_type}{interface_number}")

        #Transform the range (ex 1-48) to something usable ( range(1-49) )
        start, end = map(int, interface_number.split("-"))
        interface_range = range(start, end+1)

        #Command list
        interfaces_to_query=[]
        for interface in interface_range:
            interfaces_to_query.append(f"{interface_type}{interface}")

        #Connection and retrival of each interface
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


def get_interface_info_privileged(device_details, interface_type, interface_number):
    """
    Inputs:
        <device_details> Dictionary with the connection details
        <interface_type> Type of interface (either gigabitethernet or fasterthernet)
        <interface_number> (number range ex 1-48 1-2)
    Return:
        List with the output of the command of each interface as one item
    """
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

        print(f"Retrieving interface privileged information from {device_details['host']} for {interface_type}{interface_number}")

        # Transform the range (ex 1-48) to something usable ( range(1-49) )
        start, end = map(int, interface_number.split("-"))
        interface_range = range(start, end + 1)

        # Command list
        interfaces_to_query = []
        for interface in interface_range:
            interfaces_to_query.append(f"{interface_type}{interface}")

        # Connection and retrieval of each interface
        interface_output_list = []
        for interface in interfaces_to_query:
            command = f"show run interface {interface}"
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

def regex_processor(interface_text, privileged_interface_text, host):
    """
    Inputs:
        <switch_data> reciebes the switch data of each interface
    """
    interface_info = {}

    # Extract interface name
    interface_name_match = re.search(r'^(\S+) is', interface_text, re.MULTILINE)
    interface_info['interface_name'] = interface_name_match.group(1).lower() if interface_name_match else "NULL"

    # Extract last input time
    last_input_match = re.search(r'Last input (never|\d{2}:\d{2}:\d{2})', interface_text)
    interface_info['last_input'] = last_input_match.group(1) if last_input_match else "NULL"

    # Extract last output time
    last_output_match = re.search(r'output (never|\d{2}:\d{2}:\d{2})', interface_text)
    interface_info['last_output'] = last_output_match.group(1) if last_output_match else "NULL"

    # Log time 
    interface_info['log_time'] = datetime.now(ZoneInfo("Europe/Madrid")).strftime("%Y-%m-%d %H:%M:%S")

    # Description of the port
    description_match = re.search(r'Description: (.+)', interface_text)
    interface_info['description'] = description_match.group(1).strip() if description_match else "NULL"

    # Duplex type
    duplex_match = re.search(r'(Full-duplex|Half-duplex|Auto-duplex)', interface_text)
    interface_info['duplex_status'] = duplex_match.group(1) if duplex_match else "NULL"

    # Speed of the interface
    speed_match = re.search(r'(\d+Mb/s|\d+Gb/s|Auto-speed)', interface_text)
    interface_info['speed'] = speed_match.group(1) if speed_match else "NULL"

    # State of the interface
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

    #MAC interface of the connected device, set to NULL as no collection has been made yet
    interface_info['mac'] = "NULL"
    
    # Switchport mode of the interface
    switchport_mode_match = re.search(r'switchport\s+mode\s+(access|trunk|dynamic\s+(auto|desirable))', privileged_interface_text, re.IGNORECASE)
    if switchport_mode_match:
        mode = switchport_mode_match.group(1).title()
        interface_info['switchport_mode'] = mode
        if mode == "Access":
            vlan_match = re.search(r'switchport\s+access\s+vlan\s+(\d+)', privileged_interface_text, re.IGNORECASE)
            interface_info['vlan'] = int(vlan_match.group(1)) if vlan_match else None
        elif mode == "Trunk":
            trunk_vlan_match = re.search(r'switchport\s+trunk\s+allowed\s+vlan\s+(.+)', privileged_interface_text, re.IGNORECASE)
            interface_info['vlan'] = trunk_vlan_match.group(1) if trunk_vlan_match else "No VLAN Filtering"
        else:
            interface_info['vlan'] = "N/A"
    else: # exception if there is no switchport configurations
        interface_info['switchport_mode'] = None 
        interface_info['vlan'] = None
    
    interface_info['switch'] = host
    
    return interface_info



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

    # Iterate list of Switches from the json
    for switch_detail in json_switch_details: # type: ignore
        # Get regular interface info
        regular_ints_results=get_interface_info(switch_detail, switch_detail["interface_names"], switch_detail["interface_number"])
        # Get Privileged interface info
        privi_regular_ints_results=get_interface_info_privileged(switch_detail, switch_detail["interface_names"], switch_detail["interface_number"])

        # Get uplink interfaces info
        uplink_ints_results=get_interface_info(switch_detail, switch_detail["uplink_names"], switch_detail["uplink_number"] )
        # Get Privileged uplink info
        privi_uplink_ints_results=get_interface_info_privileged(switch_detail, switch_detail["uplink_names"], switch_detail["uplink_number"])

        for i in uplink_ints_results: # Append of all the uplink interfaces to the previous list to keep it all in one list
            regular_ints_results.append(i)

            
        for i in privi_uplink_ints_results: # Append of all the uplink interfaces to the previous list to keep it all in one list This is for privileged info
            privi_regular_ints_results.append(i)


        if len(regular_ints_results) != len(privi_regular_ints_results):
            print("The result of the interfaces info lookup and privileged interfaces info did not match, quitting.")
            exit
        else:
            for interface_run, privileged_interface_run in zip(regular_ints_results, privi_regular_ints_results):
                print(regex_processor(interface_run, privileged_interface_run, switch_detail["host"]))

orchestrator()
