import json
import rsa
import os


from .diffie_hellman import DiffieHelman
from .RSAManager import RSAManager

class KeyManager():
    def __init__(self, user_id):
        filename = '{}.txt'.format(user_id)
        self.filename = os.path.join('keys', filename)

        if not os.path.exists(self.filename):
            with open(self.filename, 'a') as f:
                f.write('{}')
        with open(self.filename) as infile:
            self.keys = json.load(infile)

        self.initialised_dh = {}

    def contains_conversation(self, conversation_id):
        return str(conversation_id) in self.keys

    def add_key(self, conversation_id, key):
        if str(conversation_id) not in self.keys:
            key_json = {'rsa_key':
                            {
                            'n': key.n,
                            'e': key.e,
                            'd': key.d,
                            'p': key.p,
                            'q': key.q
                            }
                        }

            self.keys[str(conversation_id)] = key_json

            with open(self.filename, 'w') as outfile:
                json.dump(self.keys, outfile)

    def get_key(self, conversation_id):
        return self.keys.get(str(conversation_id), None)

    def get_rsa_manager(self, conversation_id):
        if self.contains_conversation(conversation_id):
            return RSAManager(self.get_key(conversation_id)['rsa_key'])
        return None

    def generate_key(self, bits=512):
        _, priv_key = rsa.newkeys(bits)
        return priv_key

    def initialise_dh(self, conversation_id):
        self.initialised_dh[conversation_id] = DiffieHelman()
        return self.initialised_dh[conversation_id]

    def remove_dh(self, conversation_id):
        self.initialised_dh.pop(conversation_id, 'None')

    def get_dh(self, conversation_id):
        return self.initialised_dh.get(conversation_id, None)


