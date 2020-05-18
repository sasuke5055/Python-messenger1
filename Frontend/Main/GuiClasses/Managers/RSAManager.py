import rsa
import base64

encoding = 'ISO-8859-1'

class RSAManager():
    def __init__(self, rsa_dict):
        n = int(rsa_dict['n'])
        e = int(rsa_dict['e'])
        d = int(rsa_dict['d'])
        p = int(rsa_dict['p'])
        q = int(rsa_dict['q'])

        self.pub_key = rsa.PublicKey(n, e)
        self.priv_key = rsa.PrivateKey(n, e, d, p, q)

    def encrypt(self, message):
        message = message.encode(encoding)
        encrypted_message = rsa.encrypt(message, self.pub_key).decode(encoding)
        return encrypted_message
    
    def decrypt(self, message):
        try:
            encoded_message = message.encode(encoding)
            decrypted_message = rsa.decrypt(encoded_message, self.priv_key)
            decrypted_message = decrypted_message.decode(encoding)
            return decrypted_message
        except:
            return message
