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
        print("Error: The config file does not exist")

def auto_scp(path: str):
    pass

def main():
    conf_dict = get_conf(CONF_PATH)

if __name__ == "__main__":
    main()
