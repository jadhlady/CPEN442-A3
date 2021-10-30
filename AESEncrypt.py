import base64
from Crypto.Cipher import AES
from Crypto import Random

class AESCipher:
    def __init__( self, key ):
        self.key = key

    def encrypt( self, raw ):
        raw = pad(raw)
        iv = Random.new().read( AES.block_size )
        cipher = AES.new( self.key, AES.MODE_CBC, iv )
        return base64.b64encode( iv + cipher.encrypt( raw ) ) 

    def decrypt( self, enc ):
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv )
        return unpad(cipher.decrypt( enc[16:] ))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]






string = "Hello World"
key = "asdfghjkloqiwueys"
Enc = AESCipher(key)

ciphertext = Enc.encrypt(string)

cleartext = Enc.decrypt(ciphertext)

print(string, ciphertext, cleartext)

# Gotten from stack overflow
# https://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256