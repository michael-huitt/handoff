from subprocess import run
from sys import argv
from os import remove
from os.path import isdir
from shutil import rmtree

CONF_PATH = "settings.conf"

##Fancy struct that sets the port to 22 if not specified, represents generic SSH connection info.
class Conn:
    def __init__(self, user, hostname, port):
        self.user = user 
        self.hostname = hostname
        self.port = port

        if port is None:
            self.port = 22

##Read in the configuration file and return a dictionary where the prefix and postfix of '=' are
##the key value pair.
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


##Run the scp command given the client path, host path, a Conn object, and a list of scp flags. Returns a string that
##gives details on the operation, first a generic "success" message followed by anything scp might return.
def auto_scp(client_path: str, host_path: str, SSH_Conn: Conn, flags: list) -> str:
    try:
        #combine the user@hostname and path into one argument for run() 
        if SSH_Conn.user: 
            destination_arg = SSH_Conn.user + "@" + SSH_Conn.hostname + ":" + host_path 
        
        else:
            destination_arg = SSH_Conn.hostname + ":" + host_path #so that scp defaults to the current session's user 
                                                                  #if not specified
        Result = run(['scp','-P', SSH_Conn.port, *flags, client_path, destination_arg],
                    capture_output = True, text = True)
        
        if Result.returncode != 0:
            raise Exception(f"scp exited with code ({Result.returncode}): {Result.stderr.strip()}")

        else:
            if Result.stderr != '': #returned on non-verbose scp success 
                return (f"Transfer succesful {client_path} -> {SSH_Conn.user}@{SSH_Conn.hostname}:{host_path}"
                        f"\n{Result.stderr}")
            else:
                return (f"Transfer succesful {client_path} -> {SSH_Conn.user}@{SSH_Conn.hostname}:{host_path}")

    except Exception as e:
        print(f"auto_scp error: {e}")

def get_sort(filepath: str) -> dict:
    try:
        sort_dict = {} 

        with open(filepath, "r") as file:
            for line in file:
                split_line = line.split('=', 1)
                
                if split_line[0] == "sort":
                    sort_args = split_line[1].strip().split(",")
                    
                    for arg in sort_args:
                        path, condition = arg.split("[", 1)
                        condition = condition.rstrip("]")
                        sort_dict[condition] = path

                    return sort_dict

    except Exception as e:
        print(f"get_sort error: {e}")

def dynamic_sort(args: dict, client_path: str) -> str:
    try: 
        sort_dict = get_sort(CONF_PATH)
    
        print(sort_dict)
    
    except Exception as e:
        print(f"dynamic file sort error: {e}")

def handle_preflags(flags: list, client_path: str):
    try:
        for flag in flags:
            if flag == "-s":
                dynamic_sort(get_sort(CONF_PATH), client_path)

    except Exception as e:
        print(f"pre-flag error: {e}")

##Iterate through a list of flags and operate on the client path depending on the flags.
def handle_postflags(flags: list, client_path: str):
    try:
        for flag in flags:
            if flag == "-d":
                if isdir(client_path):
                    rmtree(client_path)

                else: 
                    remove(client_path)
                
                print(f"{client_path} removed succesfully") 
            
    except Exception as e:
        print(f"post-flag error: {e}")

def main():
    try: 
        if len(argv) < 3:
            raise ValueError("Usage: handoff.py <client path> <host path>")
        
        conf = get_conf(CONF_PATH)
        SSH_Conn = Conn(conf.get("user"), conf.get("hostname"), conf.get("port"))  
        client_path = argv[1]
        host_path = argv[2]
        
        handle_preflags(argv[3:], client_path)

        output = auto_scp(client_path, host_path, SSH_Conn, conf.get("flags"))
         
        print(output)
        handle_postflags(argv[3:], client_path)
    
    except Exception as e:
        print("error: ", repr(e))

if __name__ == "__main__":
    main()
