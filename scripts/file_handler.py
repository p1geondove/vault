from Crypto.Cipher import AES
from hashlib import pbkdf2_hmac
import os
import json
import secrets
from pathlib import Path

try:
    from .const import Misc
    from .twister import MersenneTwister
except:
    from const import Misc
    from twister import MersenneTwister

PEPPER = Misc.pepper
SEPERATOR = Misc.seperator
KEYSIZE = 32

def jumble(data:bytes, seed:int):
    mt = MersenneTwister(seed)
    indecies = list(range(len(data)))
    mt.shuffle(indecies)
    return bytes(data[i] for i in indecies)

def dejumble(data:bytes, seed:int):
    mt = MersenneTwister(seed)
    indecies = list(range(len(data)))
    mt.shuffle(indecies)
    new_data = bytearray(len(data))
    for i, idx in enumerate(indecies):
        new_data[idx] = data[i]
    return bytes(new_data)

class CrypTor:
    def __init__(self, content:bytes):
        self.content = content

    def pass_to_key(self, password:str, salt:bytes|None = None):
        if salt is None:
            salt = secrets.token_bytes(KEYSIZE) # this maximum password lenght = 32
        key = password.encode() + PEPPER
        key = pbkdf2_hmac('sha256', key, salt, 100000)
        return key[:KEYSIZE], salt

    def lock(self, password:str):
        key, salt = self.pass_to_key(password)
        cipher = AES.new(key, AES.MODE_EAX)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(self.content)
        return jumble(SEPERATOR.join([ciphertext, tag, nonce, salt]), sum(bytearray(PEPPER)))
    
    def unlock(self, password:str):
        contents = dejumble(self.content, sum(bytearray(PEPPER))).split(bytearray(SEPERATOR))

        if not len(contents) == 4:
            raise Exception('broken file')
        
        ciphertext, tag, nonce, salt = contents
        key, _ = self.pass_to_key(password, salt)
        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
        plaintext = cipher.decrypt(ciphertext)
        cipher.verify(tag)
        return plaintext
        
class FileInterface:
    def __init__(self, file_path:Path|str = Path('password.vault')):
        self.extension = '.lock'
        self.file_path = Path(file_path)

        with open(self.file_path,'rb') as file:
            self.file_content = file.read()

    def lock(self, password:str, out_path:str|Path|None = None):
        if out_path is None:
            out_path = str(self.file_path) + self.extension
        out_path = Path(out_path)
        self.file_content = CrypTor(self.file_content).lock(password)
        self.file_content = jumble(self.file_content, sum(bytearray(PEPPER)))
        with open(out_path,'wb') as file:
            file.write(self.file_content)
    
    def unlock(self, password:str, out_path:str|Path|None = None):
        if out_path is None:
            out_path = str(self.file_path).removesuffix(self.extension)
        out_path = Path(out_path)
        content = dejumble(self.file_content, sum(bytearray(PEPPER)))
        plaintext = CrypTor(content).unlock(password)
        if plaintext:
            with open(out_path,'wb') as file:
                file.write(plaintext)

    def update(self, password:str, content:bytes):
        data = dejumble(self.file_content, sum(bytearray(PEPPER)))
        if not CrypTor(data).unlock(password): return
        with open(self.file_path, 'wb') as f:
            content = CrypTor(content).lock(password)
            f.write(jumble(content, sum(bytearray(PEPPER))))
    
    def get_passwords(self, password:str):
        data = dejumble(self.file_content, sum(bytearray(PEPPER)))
        data = CrypTor(data).unlock(password)
        return json.loads(data)

if __name__ == '__main__': # tests
    from shutil import copyfile
    from ntimer import timer
    @timer
    def test():
        file_path = 'test.file'
        password = 'test'
        data = os.urandom(128)
        data2 = os.urandom(128)

        print('testing CrypTor')
        a = CrypTor(data).lock(password)
        b = CrypTor(a).unlock(password)
        assert b == data
        a = CrypTor(data).lock(password*100)
        b = CrypTor(a).unlock(password*101)
        assert b != data
        a = CrypTor(data).lock(password*100)
        b = CrypTor(a).unlock(password*100)
        assert b == data

        print('testing FileInterface')
        with open(file_path, 'wb') as f:
            f.write(data)
        FileInterface(file_path).lock(password)
        os.remove(file_path)
        copyfile(file_path+'.lock',file_path+'.vault')
        FileInterface(file_path+'.lock').unlock(password)
        os.remove(file_path+'.lock')
        with open(file_path, 'rb') as f:
            new_data = f.read()
        os.remove(file_path)
        assert new_data == data
        FileInterface(file_path+'.vault').update(password,data2)
        FileInterface(file_path+'.vault').unlock(password)
        with open(file_path+'.vault', 'rb') as f:
            new_data = f.read()
        os.remove(file_path+'.vault')
        assert new_data == data2
        print('All tests succeded !')
    test()