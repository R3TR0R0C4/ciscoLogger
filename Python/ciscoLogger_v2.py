from netmiko import ConnectHandler
import json

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
            output_list.append(f"--- Output for {command} ---\n{interface_output}")

        net_connect.disconnect()
        print("Telnet connection closed.")

    except Exception as e:
        print(f"An error occurred during information retrieval: {e}")

    return output_list


config_file = 'Python/config/device.json'

device_info = read_device_config(config_file)

if device_info:
    #Llistat de interfícies a fer les queries

    target_interfaces = []
    for i in range(1,49):
        target_interfaces.append(f"gi1/0/{i}")

    #Corre la funcio per recollir la info de cada interfície
    interface_outputs = get_interface_info(device_info, target_interfaces)

    if interface_outputs:
        print("\n".join(interface_outputs))
    else:
        print("No interface information retrieved.")

else:
    print("Failed to load device configuration. Please check the configuration file.")