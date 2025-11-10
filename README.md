# Handoff - An scp wrapper script written in Python
## How To Install
To install, clone the repository, and set up handoff.py however you wish. It is invoked with python3
## Formatting
handoff accepts upwards of 3 arguments: a client path, the host path, and any following flags
```
python3 handoff.py <client path> <host path> <flags>
```
### Supported Flags
```
-d [deletes the directory/file upon succesful transfer]
```
## Configuration
scp configuration is done through the included "settings.conf" file. Here is an example of what a configured file may
look like:
```
user=me
hostname=192.168.1.1
port=2222
flags=-r -v
```
**Note** - -P does not need to specified within the flags. If port or user are left empty, scp will default to 22 and
the currently logged in user, respectively. Otherwise, **treat flags exactly how you would entering them into scp**.
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
