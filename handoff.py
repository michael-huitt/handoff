from subprocess import run
from sys import argv
from os import remove, listdir
from os.path import isdir, join, dirname, abspath
from shutil import rmtree
from re import match

from constants import *

CONF_PATH = join(dirname(abspath(__file__)), "settings.conf")

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

##Get_sort() does a line by line pass through the given conf file looking for the 'sort' keyword
##and creates and returns a dictionary of the arguments listed under the sort keyword
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

##Parse a tuple of (key, operator, value) from a string representing the arguments intended to be processed by
##dynamic_sort().
def parse_sort(conditional: str) -> tuple:
    try:
        same = match(r"(\w+)\s*(==|!=|>=|<=|>|<)\s*(\w+)", conditional)
        
        if not same:
            raise ValueError(f"Invalid conditional: {conditional}")

        key, operator, value = same.groups()
        
        return key, operator, value

    except Exception as e:
        print(f"parse_sort error: {e}")

##Returns the number of files ending with the given tuple. It is expected that the tuple is a predefined global 
##variable.
def count_extension(path: str, extension: tuple) -> int:
    try: 
        if extension is None:
            raise ValueError("extension tuple cannot be None")

        count = 0 
        
        if isdir(path):
            for file in listdir(path):
                if file.lower().endswith(extension):
                    count += 1
                
                if isdir(join(path, file.lower())):
                    count += count_extension(join(path, file), extension)
        
        elif path.lower().endswith(extension):
            count += 1
    
        return count
    
    except Exception as e:
        print(f"count_extension error: {e}")

##Evaluate variables safely and return a boolean or raise a ValueError if the operator isn't supported 
def evaluate_expression(count: int, operator: str, value: int) -> bool:
    try:
        match operator:
            case "==":
                return (count == value)

            case "!=":
                return (count != value)

            case ">=":
                return (count >= value)

            case "<=":
                return (count <= value)

            case ">":
                return (count > value)

            case "<":
                return (count < value)
            
            case _:
                raise ValueError("Operator not matched to case")
    
    except Exception as e:
        print(f"evaluate_expression error: {e}")

##Given a dictionary representing sort arguments (returned by get_sort), parses the arguments and returns a string
##representing the path if a given argument matches, otherwise return None
def dynamic_sort(args: dict, client_path: str) -> str | None:
    try: 
        for arg in args:
            key, operator, value = parse_sort(arg)
            count = count_extension(client_path, globals().get(key, None))
            
            if evaluate_expression(count, operator, int(value)):
                return args[arg]
    
    except Exception as e:
        print(f"dynamic file sort error: {e}")

##Iterate through a list of flags and perform operations that should be performed PRIOR to the execution of auto_scp(),
##such as dynamic file sorting.
def handle_preflags(flags: list, client_path: str):
    try:
        for flag in flags:
            if flag == "-s":
                sort_output = dynamic_sort(get_sort(CONF_PATH), client_path)
                
                if sort_output:
                    sort_output = sort_output.strip()
                
                print(f"File matched to: {sort_output}") 
                
                return sort_output
            
            else:
                return None
    
    except Exception as e:
        print(f"pre-flag error: {e}")

##Iterate through a list of flags and operate on the client path depending on the flags (such as for cleanup using
##delete).
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
            raise ValueError("Usage: handoff.py <client path> <host path> <flags>")
        
        conf = get_conf(CONF_PATH)
        SSH_Conn = Conn(conf.get("user"), conf.get("hostname"), conf.get("port"))  
        client_path = argv[1]
        host_path = argv[2]
        
        preflag_output = handle_preflags(argv[3:], client_path)
        
        if preflag_output:
            host_path = preflag_output

        output = auto_scp(client_path, host_path, SSH_Conn, conf.get("flags"))
         
        print(output)
        handle_postflags(argv[3:], client_path)
    
    except Exception as e:
        print("error: ", repr(e))

if __name__ == "__main__":
    main()

