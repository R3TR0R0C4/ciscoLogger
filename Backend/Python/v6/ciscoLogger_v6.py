import json
import netmiko
import mariadb
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
        print(f"An error occurred during connection or command execution during connection for {device_details['host']}: {e}")
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
        print(f"An error occurred during connection or command execution during privileged connection for {device_details['host']}: {e}")
        # Only attempt to disconnect if net_connect object was successfully created
        if net_connect:
            try:
                net_connect.disconnect()
                print(f"Attempted to disconnect from {device_details['host']} after error.")
            except Exception as disconnect_e:
                print(f"Error during disconnect from {device_details['host']}: {disconnect_e}")
        interface_output_list = [f"Error on {device_details['host']}: {e}"]

    return interface_output_list

def get_interface_mac_address(device_details, interface_type, interface_number):
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

        print(f"Retrieving interface arp MAC {device_details['host']} for {interface_type}{interface_number}")

        # Transform the range (ex 1-48) to something usable ( range(1-49) )
        start, end = map(int, interface_number.split("-"))
        interface_range = range(start, end + 1)

        # Command list
        interfaces_to_query = []
        for interface in interface_range:
            interfaces_to_query.append(f"{interface_type}{interface}")

        # Connection and retrieval of each interface
        mac_output_list = []
        for interface in interfaces_to_query:
            command = f"show mac-address-table interface {interface}"
            interface_output = net_connect.send_command(command)
            mac_output_list.append(interface_output.strip()) # .strip() to clean whitespace
        net_connect.disconnect()

    except Exception as e:
        print(f"An error occurred during connection or command execution during retrieval of MAC connection for {device_details['host']}: {e}")
        # Only attempt to disconnect if net_connect object was successfully created
        if net_connect:
            try:
                net_connect.disconnect()
                print(f"Attempted to disconnect from {device_details['host']} after error.")
            except Exception as disconnect_e:
                print(f"Error during disconnect from {device_details['host']}: {disconnect_e}")
        mac_output_list = [f"Error on {device_details['host']}: {e}"]

    return mac_output_list


def regex_processor(interface_text, privileged_interface_text, mac_interface_address, host):
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

    mac_matches = re.findall(r'\b[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\.[0-9a-fA-F]{4}\b', mac_interface_address)
    unformatted_mac = mac_matches if mac_matches else []

    if len(unformatted_mac) == 1:
        raw = unformatted_mac[0].replace('.', '').upper()
        formatted_mac = ':'.join(raw[i:i+2] for i in range(0, 12, 2))
        interface_info['mac'] = formatted_mac
    elif len(unformatted_mac) > 1:
        formatted_mac = []
        for mac in unformatted_mac:
            raw = mac.replace('.', '').upper()
            formatted_mac.append(':'.join(raw[i:i+2] for i in range(0, 12, 2)))
        interface_info['mac'] = formatted_mac
    else:
        interface_info['mac'] = None




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

def mariadb_import1(json_database_details, interface_data):
    """
    Inputs:
        db_host, db_user, db_password, db_name: Information of the database connection
        interface_data: list of dictionaries containing each of the interface's status
    Returs:
        Inserts to a mariadb database
        prints of the results        
    """
    conn = None
    try:
        conn = mariadb.connect(
            host=json_database_details['host'],
            user=json_database_details['username'],
            password=json_database_details['password'],
            database=json_database_details['database']
        )
        cursor = conn.cursor()
    
        # The SQL INSERT statement
        insert_query = """
        INSERT INTO interface_stats (interface_name, last_input, last_output, log_time, description, duplex_status, speed, vlan, status, switchport, switch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        insert_count=0
        for item in interface_data:
            # Map the dictionary keys to the table columns
            interface_name = item.get('interface_name')
            last_input = item.get('last_input')
            last_output = item.get('last_output')
            log_time = item.get('log_time')
            description = item.get('description')
            duplex_status = item.get('duplex_status')
            speed = item.get('speed')
            vlan = item.get('vlan')
            status = item.get('state')  # Assuming 'state' in your data maps to 'status' in the table
            switchport_mode = item.get('switchport_mode')
            switch = item.get('switch')
    
            # Execute the insert statement
            try:
                cursor.execute(insert_query, (interface_name, last_input, last_output, log_time, description, duplex_status, speed, vlan, status, switchport_mode, switch))
            except mariadb.Error as e:
                print(f"Error inserting record: {e}")
                print(f"Problematic data: {item}")
                conn.rollback() # Rollback the transaction if an error occurs
            insert_count=+1
        # Commit the changes
        conn.commit()
        print(f"{insert_count} records inserted successfully.")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()

def mariadb_import(json_database_details, interface_data): # interface_data is now a single dictionary
    conn = None
    try:
        conn = mariadb.connect(
            host=json_database_details['host'],
            user=json_database_details['username'],
            password=json_database_details['password'],
            database=json_database_details['database']
        )
        cursor = conn.cursor()
    
        # The SQL INSERT statement
        insert_query = """
        INSERT INTO interface_stats (interface_name, last_input, last_output, log_time, description, duplex_status, speed, vlan, mac, status, switchport, switch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        insert_count=0
        
        # Directly use interface_data since it's already a dictionary
        interface_name = interface_data.get('interface_name')
        last_input = interface_data.get('last_input')
        last_output = interface_data.get('last_output')
        log_time = interface_data.get('log_time')
        description = interface_data.get('description')
        duplex_status = interface_data.get('duplex_status')
        speed = interface_data.get('speed')
        vlan = interface_data.get('vlan')
        mac = interface_data.get('mac')
        status = interface_data.get('state')  # Assuming 'state' in your data maps to 'status' in the table
        switchport_mode = interface_data.get('switchport_mode')
        switch = interface_data.get('switch')
    
        # Execute the insert statement
        try:
            cursor.execute(insert_query, (interface_name, last_input, last_output, log_time, description, duplex_status, speed, vlan, mac, status, switchport_mode, switch))
            insert_count = 1 # Only one record is processed per call
        except mariadb.Error as e:
            print(f"Error inserting record: {e}")
            print(f"Problematic data: {interface_data}") # Use interface_data directly
            conn.rollback() # Rollback the transaction if an error occurs

        # Commit the changes
        conn.commit()
        print(f"{insert_count} records inserted successfully.")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()

def orchestrator():
    """
    Orchestrates all other functions
    """

    # build of the pwd to open the directory config without problems
    base_dir = path.dirname(path.abspath(__file__)) 
    json_switch_filepath = path.join(base_dir, 'config', 'devices.json')
    
    #Reading the json file for devices and saving it to <json_switch_details>
    json_switch_details=read_json_configs(json_switch_filepath,'device')

    # Iterate list of Switches from the json
    for switch_detail in json_switch_details: # type: ignore
        # Get regular interface info
        regular_ints_results=get_interface_info(switch_detail, switch_detail["interface_names"], switch_detail["interface_number"])
        # Get Privileged interface info
        privi_regular_ints_results=get_interface_info_privileged(switch_detail, switch_detail["interface_names"], switch_detail["interface_number"])
        # Get Mac Address Table
        mac_address_ints_results=get_interface_mac_address(switch_detail, switch_detail["interface_names"], switch_detail["interface_number"])
        # Get uplink interfaces info
        uplink_ints_results=get_interface_info(switch_detail, switch_detail["uplink_names"], switch_detail["uplink_number"] )
        # Get Privileged uplink info
        privi_uplink_ints_results=get_interface_info_privileged(switch_detail, switch_detail["uplink_names"], switch_detail["uplink_number"])

        # Get Mac Address Table uplink interface
        uplink_mac_address_ints_results=get_interface_mac_address(switch_detail, switch_detail["interface_names"], switch_detail["interface_number"])
        print()


        for uplink in uplink_ints_results: # Append of all the uplink interfaces to the previous list to keep it all in one list
            regular_ints_results.append(uplink)

            
        for privileged_uplink in privi_uplink_ints_results: # Append of all the uplink interfaces to the previous list to keep it all in one list This is for privileged info
            privi_regular_ints_results.append(privileged_uplink)

        for mac_address in uplink_mac_address_ints_results: # Append of all the uplink interfaces to the previous list to keep it all in one list This is for privileged info
            mac_address_ints_results.append(mac_address)


        if len(regular_ints_results) != len(privi_regular_ints_results) and len(regular_ints_results) != len(mac_address_ints_results):
            print("The result of the interfaces info lookup and privileged interfaces info did not match, quitting.")
            exit
        else:
            processed_info=[]
            json_database_details=read_json_configs(json_switch_filepath,'database')
            json_database_details=json_database_details[0]
            for interface_run, privileged_interface_run, mac_interface_address in zip(regular_ints_results, privi_regular_ints_results, mac_address_ints_results):
                processed_info.append(regex_processor(interface_run, privileged_interface_run, mac_interface_address, switch_detail["host"]))

        print(json_database_details)
        #print(processed_info)
        for i in processed_info:
            mariadb_import(json_database_details,i)
orchestrator()



"""
interface_name       interface_name   -
last_input           last_input       -
last_output          last_output      -
log_time             log_time         -
description          description      -
duplex_status        duplex_status
Auto-speed           speed
state                status
mac                  mac  
switchport_mode      switchport
vlan                 vlan
switch               switch



"""