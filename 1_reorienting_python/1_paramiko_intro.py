import paramiko
import time

# conn_params = paramiko.SSHClient()
#
# conn_params.connect(
#     hostname="R1",
#     username="pyuser",
#     password="pypass"
# )
#
# conn = conn_params.invoke_shell()
# conn.send("show ip interface brief\n")
#
# # We may need to wait
# output = (conn.recv(65535))


def send_cmd(conn, command):
    """
    Given an open connection and a command, issue the command and wait
    1 second for the command to be processed.
    """
    conn.send(command + "\n")
    time.sleep(1.0)

def get_output(conn):
    """
    Given an open connection, read all the data from the buffer and
    decode the byte string as UTF-8
    """
    return conn.recv(65535).decode("utf-8")

def main():
    host_dict = {
        "R1": "show running-config | section vrf_definition",
        # "8.8.8.8": "ping -c 3",
        "R2": "show running-config vrf",
        # "10.0.1.1": "ping -c 3",
    }
    # For each host in the inventory dict, extract key and value
    print("Ready to ping")
    for hostname, vrf_cmd in host_dict.items():
        # Paramiko can be SSH client or server; use client here
        conn_params = paramiko.SSHClient()

        # We don't need paramiko to refuse connections due to missing SSH keys
        conn_params.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        print("Step 1")
        conn_params.connect(
            hostname=hostname,
            port=22,
            username="pyuser",
            password="pypass",
            look_for_keys=False,
            allow_agent=False,
        )

        # Get an interactive shell and wait a bit fo the prompt to appear
        print("Step 2")
        conn = conn_params.invoke_shell()
        time.sleep(1.0)
        print(f"Logged into {get_output(conn).strip()} successfully")

        # Iterate over the list of commands, sending each one in series
        # The final command in the list is the OS-specific VRF "show" command

        commands = [
            "terminal length 0",
            "show version | include Software",
            vrf_cmd,
        ]
        concat_output = ""

        for command in commands:
            # It helps to have a custom function to abstract sending
            # commands and reading output from the device
            send_cmd(conn, command)
            concat_output += get_output(conn)
        # Close session when we are done
        conn.close()

        # Open a new text file per host and write the output
        print(f"Writing {hostname} facts to file")
        with open(f"{hostname}_facts.txt", "w") as handle:
            handle.write(concat_output)

if __name__ == "__main__":
    main()
