from netmiko import ConnectHandler
import json

#Funcio per llegir el arxiu device.json amb la configuració del switch a connectar
def read_json_config(filepath):
    try:
        with open(filepath, 'r') as f:
            config = json.load(f)
        return config.get('device', {})
    except FileNotFoundError:
        print(f"Error: Arxiu de configuracio no trobat {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Format JSON no vàlid {filepath}")
        return None

config_file = 'config/device.json'

device_info = read_json_config(config_file)

#Connexió al switch i recollida d'informació
if device_info:
    device = {
        "device_type": "cisco_ios_telnet",
        "port": 23,
        **device_info
    }

    try:
        net_connect = ConnectHandler(**device)#Connexió al switch
        print(f"Connectat correctament {device['host']} via Telnet")


        #Recollida de l'estat de les interfícies
        output = ""
        for i in range(1, 49):
            command = f"show interface gi1/0/{i}"
            interface_output = net_connect.send_command(command)
            output += f"--- Output for {command} ---\n{interface_output}\n\n"

        print(output)

        net_connect.disconnect()
        print("Connexió tancada.")

    except Exception as e:
        print(f"Error: {e}")

else:
    print("error al carregar la configuracio, comproba arxiu device.json")

