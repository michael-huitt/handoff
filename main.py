from subprocess import run
from sys import argv

CONF_PATH = "settings.conf"

def get_conf(filepath: str) -> dict:
    try:
        conf_dict = {} 

        with open(filepath, "r") as file:
            for line in file:
                split_line = line.split('=', 1)
                conf_dict[split_line[0].strip()] = split_line[1].strip()
    
        return conf_dict

    except FileNotFoundError:
        print("The config file does not exist")

def auto_scp(client_path: str, host_path: str, hostname: str, port: str):
    pass

def main():
    try: 
        conf_dict = get_conf(CONF_PATH)
        if len(argv) < 3:
            raise ValueError("Usage: main.py <client path> <host path>")
    
    except Exception as e:
        print("error: ", repr(e))

if __name__ == "__main__":
    main()
