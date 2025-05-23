from yaml import safe_load
from netmiko import Netmiko
from jinja2 import Environment, FileSystemLoader

def main():
    with open("hosts.yml", "r") as handle:
        host_root = safe_load(handle)

    platform_map = {"ios": "cisco_ios", "iosxr": "cisco_xr"}

    for host in host_root["host_list"]:
        platform = platform_map[host["platform"]]

    with open(f"vars/{host['name']}_crfs.yml", "r") as handle:
        vrfs = safe_load(handle)

    j2_env = Environment(
        loader=FileSystemLoader("."), trim_blocks=True, autoescape=True
    )
    template = j2_env.get_template(f"templates/netmiko/{platform}_vpn.j2")
    new_vrf_config = template.render(data=vrfs)

    conn = Netmiko(
        host=host["name"],
        username="pyuser",
        password="pypass",
        device_type=platform,
    )

    print(f"Logged into {conn.find_prompt()} successfully")
    result = conn.send_config_set(new_vrf_config.split("\n"))

    print(result)

    conn.dissconnect()

if __name__ == "__main__":
    main()




