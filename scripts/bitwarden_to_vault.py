import json
import os
from file_handler import FileInterface

bitwarden_file = 'bitwarden_export_20250712102616.json'
bitwarden_json = json.load(open(bitwarden_file,'rb'))['items']
vault_list = []

for entry in bitwarden_json:
    name = entry['name']
    user = entry['login']['username']
    password = entry['login']['password']

    name = name if name else ''
    user = user if user else ''
    password = password if password else ''

    if 'sound' in name:
        print(f'soundcloud password = {password}')
    vault_list.append([name,user,password])

with open('bitwarden.json', 'wt') as f:
    passwords_json = json.dump(vault_list, f)

FileInterface('bitwarden.json').lock('Qwerdenker1!?')

os.rename('bitwarden.json.lock', 'password.vault')

#print(passwords_json)
