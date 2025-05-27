import threading
import time
import re
from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException

# --- Configuration ---
# Replace with your actual switch details
SWITCHES = [
    {
        'device_type': 'cisco_ios',
        'host': '192.168.1.101',
        'username': 'your_username',
        'password': 'your_password',
        'secret': 'your_enable_password', # If your user needs to enter enable mode
    },
    {
        'device_type': 'cisco_ios',
        'host': '192.168.1.102',
        'username': 'your_username',
        'password': 'your_password',
        'secret': 'your_enable_password',
    },
    # Add details for the remaining 9 switches
    # ...
]

# Regex pattern to capture interface status changes
# This pattern looks for messages like "%LINK-5-CHANGED: Interface GigabitEthernet0/1, changed state to down"
# or "%LINEPROTO-5-UPDOWN: Line protocol on Interface GigabitEthernet0/1, changed state to up"
INTERFACE_STATUS_PATTERN = re.compile(
    r'.*(?P<severity>\%\w+-\d-\w+): Interface (?P<interface>\S+), changed state to (?P<status>\S+).*'
)

# --- Global Data Structure for Results ---
# A thread-safe way to store results if multiple threads are writing to it
# For simplicity, we'll just print directly in this example.
# In a real-world scenario, consider a Queue or a shared list with a Lock.

# --- Functions ---

def monitor_switch(switch_details):
    host = switch_details['host']
    print(f"[{host}] Attempting to connect...")
    net_connect = None
    try:
        net_connect = ConnectHandler(**switch_details)
        print(f"[{host}] Connected. Entering enable mode and enabling terminal monitor.")
        
        # Enter enable mode if a secret is provided
        if 'secret' in switch_details and switch_details['secret']:
            net_connect.enable()

        # Enable terminal monitor
        net_connect.send_command("terminal monitor", expect_string=r"#")
        # Ensure full output is displayed, not paginated
        net_connect.send_command("terminal length 0", expect_string=r"#")
        # Also useful: logging monitor debugging (to see all syslog messages including debug)
        net_connect.send_command("logging monitor debugging", expect_string=r"#")

        print(f"[{host}] Monitoring for 60 seconds...")
        start_time = time.time()
        while time.time() - start_time < 60:
            # Read from the buffer
            # Use read_channel to directly read what's coming in
            output = net_connect.read_channel()
            if output:
                for line in output.splitlines():
                    match = INTERFACE_STATUS_PATTERN.match(line)
                    if match:
                        interface = match.group('interface')
                        status = match.group('status')
                        print(f"[{host}] Detected: Interface {interface} changed state to {status}")
            time.sleep(1) # Adjust sleep time as needed

    except NetmikoTimeoutException:
        print(f"[{host}] Connection timed out.")
    except NetmikoAuthenticationException:
        print(f"[{host}] Authentication failed. Check username/password/enable secret.")
    except Exception as e:
        print(f"[{host}] An error occurred: {e}")
    finally:
        if net_connect:
            # Important: Disable terminal monitor and terminal length 0 when done
            print(f"[{host}] Disabling terminal monitor and disconnecting.")
            try:
                net_connect.send_command("terminal no monitor", expect_string=r"#")
                net_connect.send_command("terminal length 24", expect_string=r"#") # Revert to default
            except Exception as e:
                print(f"[{host}] Error disabling terminal monitor/length: {e}")
            net_connect.disconnect()

# --- Main Script Execution ---

if __name__ == "__main__":
    threads = []
    for switch in SWITCHES:
        thread = threading.Thread(target=monitor_switch, args=(switch,))
        threads.append(thread)
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    print("Monitoring complete for all switches.")