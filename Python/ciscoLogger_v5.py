from netmiko import ConnectHandler 
import netmiko
import json
import re
from datetime import datetime
import mariadb

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
            command = f"show run interface {interface}"
            interface_output = net_connect.send_command(command)
            output_list.append(f"{interface_output}")

        net_connect.disconnect()

    except Exception as e:
        print(f"An error occurred during information retrieval from {device['host']}: {e}")

    return output_list

def parse_interface_info(interface_text, interface_host_text):
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

    interface_info['mac'] = "NULL"
    
    switchport_mode_match = re.search(r'switchport\s+mode\s+(access|trunk|dynamic\s+(auto|desirable))', interface_host_text, re.IGNORECASE)
    if switchport_mode_match:
        mode = switchport_mode_match.group(1).title()  # Capitalize first letter
        interface_info['switchport_mode'] = mode
        if mode == "Access":
            vlan_match = re.search(r'switchport\s+access\s+vlan\s+(\d+)', interface_host_text, re.IGNORECASE)
            interface_info['vlan'] = int(vlan_match.group(1)) if vlan_match else None # Use None if no VLAN found
        elif mode == "Trunk":
            trunk_vlan_match = re.search(r'switchport\s+trunk\s+allowed\s+vlan\s+(.+)', interface_host_text, re.IGNORECASE)
            interface_info['vlan'] = trunk_vlan_match.group(1) if trunk_vlan_match else "No VLAN Filtering"#None # Use None if no VLANs found
        else:
            interface_info['vlan'] = "N/A" # Or None
    else:
        interface_info['switchport_mode'] = None
        interface_info['vlan'] = None

    interface_info['switch'] = "192.168.180.238"

    return interface_info

def mariadb_import(db_host, db_user, db_password, db_name, interface_data):
    try:
        conn = mariadb.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()
    
        # The SQL INSERT statement
        insert_query = """
        INSERT INTO interface_stats (interface_name, last_input, last_output, log_time, description, duplex_status, speed, vlan, status, switchport, switch)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
    
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
    
        # Commit the changes
        conn.commit()
        print(f"{cursor.rowcount} records inserted successfully.")

    except mariadb.Error as e:
        print(f"Error connecting to MariaDB: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        # Close the connection
        if conn:
            conn.close()


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
    #Recollim les dades de configuració com vlan mode access o troncal
    interface_host_outputs = get_interface_info_privileged(config_file, target_interfaces)

    parsed_info_result=[]
    for i in range(len(interface_outputs)):
        parsed_info = parse_interface_info(interface_outputs[i], interface_host_outputs[i])
        parsed_info_result.append(parsed_info) 
    #print(parsed_info_result)
    
    db_host = "localhost"
    db_user = "logger"
    db_password = "logger"
    db_name = "ciscoLogger"

    mariadb_import(db_host, db_user, db_password, db_name, parsed_info_result)



main()




endTime=datetime.now()
final_time=endTime-startTime
print(final_time)

#--------parse_interface_info--------
#interface_info['interface_name']  - Interface Name,                              eg, GigabitEthernet1/0/1  
#interface_info['last_input']      - Interface last comunication input,           eg, 00:01:00 , Never
#interface_info['last_output ']    - Interface last comunication output,          eg, 00:01:00 , Never
#interface_info['log_time']        - Time of the logging,                         eg, DD-MM-YYYY HH:MM:SS:MS
#interface_info['description']     - Interface description,                       eg, ofta_pc2_ts-pb015
#interface_info['duplex_status']   - Interface status of Duple                    eg, Full-duplex , Half-duplex , Auto-duplex
#interface_info['speed']           - Interface speed                              eg, 10Mb/s , 100Mb/s , 1Gb/s , Auto-Speed
#interface_info['state']           - Administrative status of the interface       eg, Not Connected , Shutdown , Connected , Unknown , NULL 


#--------get_interface_host_inf--------
#interface_host_info['switchport'] - Interface Switchport type                    eg, Mode Access , Mode trunk
#interface_host_info['vlan']       - Interface vlan                               eg, Trunk , 180 , 186 , 20 ...
#interface_host_info['']


#{'interface_name': 'gigabitethernet1/0/1', 'last_input': 'never', 'last_output': 'never', 'log_time': '2025-05-02 09:29:33', 'description': 'NULL', 'duplex_status': 'Auto-duplex', 'speed': 'Auto-speed', 'state': 'Shutdown', 'mac': 'NULL', 'switchport_mode': None, 'vlan': None}}