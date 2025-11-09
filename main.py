from subprocess import run
from sys import argv

CONF_PATH = "settings.conf"

class Conn:
    def __init__(self, user, hostname, port):
        self.user = user 
        self.hostname = hostname
        self.port = port

        if port is None:
            self.port = 22

def get_conf(filepath: str) -> dict:
    try:
        conf_dict = {} 

        with open(filepath, "r") as file:
            for line in file:
                split_line = line.split('=', 1)
                conf_dict[split_line[0].strip()] = split_line[1].strip()
        
        if conf_dict.get("flags"):
            conf_dict["flags"] = conf_dict["flags"].split(" ") #when we use run() in auto_scp(), we split the "flags"
                                                               #item so that we can unpack the list, as run() expects
        return conf_dict                                       #str for its arguments

    except FileNotFoundError:
        print("The config file does not exist")

def auto_scp(client_path: str, host_path: str, SSH_Conn: Conn, flags: list) -> str:
    try:
        #combine the user@hostname and path into one argument for run() 
        if SSH_Conn.user: 
            destination_arg = SSH_Conn.user + "@" + SSH_Conn.hostname + ":" + host_path 
        
        else:
            destination_arg = SSH_Conn.hostname + ":" + host_path #so that scp defaults to the current session's user 

        Result = run(['scp','-P', SSH_Conn.port, *flags, client_path, destination_arg],
                    capture_output = True, text = True)
        
        if Result.returncode != 0:
            raise Exception(f"scp exited with code ({Result.returncode}): {Result.stderr.strip()}")

        else:
            return (f"Transfer succesful {client_path} -> {SSH_Conn.user}@{SSH_Conn.hostname}:{host_path}"
                    f"\n{Result.stderr}")

    except Exception as e:
        print(f"auto_scp error: {e}")

def main():
    try: 
        if len(argv) < 3:
            raise ValueError("Usage: main.py <client path> <host path>")
        
        conf = get_conf(CONF_PATH)
        SSH_Conn = Conn(conf.get("user"), conf.get("hostname"), conf.get("port"))  
        client_path = argv[1]
        host_path = argv[2]

        output = auto_scp(client_path, host_path, SSH_Conn, conf.get("flags"))
        
        print(output)
    
    except Exception as e:
        print("error: ", repr(e))

if __name__ == "__main__":
    main()
