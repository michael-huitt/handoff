# Handoff - An scp wrapper script written in Python
## Usage
The primary intent of this script is to automate media transfer from a client system to a host server. Included are
flags tailored for dynamically piping files to a specific directory on the host server based on preconfigured user
arguments. When a torrent finishes, do you want to sort your Movies and Shows into their respective libraries? Handoff
can help automate that for you. 
## How To Install
To install, clone the repository, and set up handoff.py however you wish. It is invoked with python3
## Formatting
handoff accepts upwards of 3 arguments: a client path, the host path, and any following flags
```
python3 handoff.py <client path> <host path> <flags>
```
### Currently Supported Flags
```
-d [deletes the directory/file upon succesful transfer. Prompts the user for comfirmation]
-s [Dynamically routes the file(s) based on the "sort" field found in settings.conf. 
    For example: if you have the arguments "/host/path/Movies[VIDEO==1], /host/path/Shows[VIDEO>1]", 
    the script will check if the number of files with the VIDEO extension (found in constants.py) 
    matches each argument, and if any match, then the file(s) will be routed to that directory. 
    NOTE: A destination path still needs to be passed to the script, as this is the default 
    path assuming no arguments are met.]
-y [automatically assume yes to any prompts that may arise.]
-q [quietly log stdout to a file called 'log.txt' found in the source directory. Note that this
    means you will not get stdout output. Make sure to use '-y' if you use any flags that
    require a prompt 
```
## Configuration
### Settings.conf
scp configuration is done through the included "settings.conf" file. Here is an example of what a configured file may
look like:
```
user=me
hostname=192.168.1.1
port=2222
flags=-r -v
sort=~/Music[AUDIO>1], ~/Movies[VIDEO==1], ~/Shows[VIDEO>1]
```
**Note** - -P does not need to specified within the flags. If port or user are left empty, scp will default to 22 and
the currently logged in user, respectively. Otherwise, **treat flags exactly how you would entering them into scp**.
### Custom Extension Sorting
If you wish to make a custom list of file extensions, you are encouraged to edit the included *"constants.py"* file,
which contains a list of tuples representing a basic list of file extensions to use in the "sort" field of
*"settings.conf"*. Simply follow the basic format of the included file to create custom lists of extensions 
## Development
### Requests
Small changes are welcome. If there is something you wish to add, make a pull request with a short description of the
changes and it will be considered.
### Dependencies
The only dependency for this script is Python 3.
### Licensing
This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

You may redistribute and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

See the [LICENSE](./LICENSE) file for details.
