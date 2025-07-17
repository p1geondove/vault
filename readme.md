# Vault

### Password manager and file de/encrypter

### Use at own risk. I give no guarantees!!

GUI tool to de/encrypt files with AES.
You can turn specific json files to .vault files to then use them as safe-files for a password manager. Written in python, using `pygame` and `pycryptodome`
You see a example json in the project. This is the expected Format for the vault manager. Anything else will be counted as a regular file. You can use that to convert it to a vault file and look at the manager

## Usage

If you are on windows i suggest checking out the latest builds

### Download and launch from source
 - `git clone https://github.com/p1geondove/vault`
 - `cd vault`
 - `python -m venv .venv`
 - #### Linux
    - `.venv/bin/pip install -r requirements.txt`
    - `.venv/bin/python main.py`
 - #### Windows
    - `.venv\Scripts\pip.exe install -r requirements.txt`
    - `.venv\Scripts\python.exe main.py`
