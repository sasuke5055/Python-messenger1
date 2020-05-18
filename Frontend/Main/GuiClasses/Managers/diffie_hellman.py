import random
import rsa

def miiller_test(d, n): 
    """Function check if n can be prime number

    If so returns true if not false
    d is an odd number such that n = 2^a * d
    """

    # Pick a random number in [2..n-2] 
    # Corner cases make sure that n > 4 
    a = 2 + random.randint(1, n - 4) 
  
    # Compute a^d % n 
    x = pow(a, d, n) 
  
    if (x == 1 or x == n - 1): 
        return True
  
    # Keep squaring x while one  
    # of the following doesn't  
    # happen 
    # (i) d does not reach n-1 
    # (ii) (x^2) % n is not 1 
    # (iii) (x^2) % n is not n-1 
    while (d != n - 1): 
        x = (x * x) % n 
        d *= 2
  
        if (x == 1): 
            return False 
        if (x == n - 1): 
            return True 
  
    # Return composite 
    return False
  

def is_prime_mrt( n, k): 
    """Function check if n can be prime

    If so retun true if not false
    It have more accuracy than raw miller_test
    k its the number of test
    """

    # Corner cases 
    if (n <= 1 or n == 4): 
        return False 
    if (n <= 3): 
        return True
  
    # Find r such that n =  
    # 2^d * r + 1 for some r >= 1 
    d = n - 1
    while d % 2 == 0: 
        d //= 2
  
    # Iterate given nber of 'k' times 
    for i in range(k): 
        if (miiller_test(d, n) == False): 
            return False 
  
    return True 


# Basic prime numbers
gen_list = [{"size":5, "prime":23, "gen":2},
        {"size":1536, "prime":2410312426921032588552076022197566074856950548502459942654116941958108831682612228890093858261341614673227141477904012196503648957050582631942730706805009223062734745341073406696246014589361659774041027169249453200378729434170325843778659198143763193776859869524088940195577346119843545301547043747207749969763750084308926339295559968882457872412993810129130294592999947926365264059284647209730384947211681434464714438488520940127459844288859336526896320919633919, "gen":2}, \
            {"size":2048, "prime":32317006071311007300338913926423828248817941241140239112842009751400741706634354222619689417363569347117901737909704191754605873209195028853758986185622153212175412514901774520270235796078236248884246189477587641105928646099411723245426622522193230540919037680524235519125679715870117001058055877651038861847280257976054903569732561526167081339361799541336476559160368317896729073178384589680639671900977202194168647225871031411336429319536193471636533209717077448227988588565369208645296636077250268955505928362751121174096972998068410554359584866583291642136218231078990999448652468262416972035911852507045361090559, "gen":2}]


class DiffieHelman:

    def __init__(self, prime_number=gen_list[2]["prime"], generator=gen_list[2]["gen"]):
        """By default use prime number with size 2048"""

        self.p = prime_number
        self.g = generator

        # Use safe SystemRandom to generate random int
        self.a = random.SystemRandom().randint(2, self.p - 2)

    def test_gen(self):
        if not is_prime_mrt((self.p-1) // 2, 100):
            return False
        if pow(self.g, (self.p-1) // 2, self.p) == 1:
            return True
        else:
            return False
    
    def gen_public_key(self):
        """Compute public key A = g^a"""
        
        return pow(self.g, self.a, self.p)

    def gen_private_key(self, B):
        """Compute key K = g^ab
        
        Where B = g^b
        """

        # First check if B is from correct Group
        if pow(B, (self.p - 1) // 2, self.p) == 1:
            self.private_key = pow(B, self.a, self.p)
            self.key_inverse = pow(B, ((self.p-1)//2 - self.a) % self.p, self.p)
            return self.private_key
        else:
            raise Exception("Incorrect public key B")

    def encrypt_message(self, message):
        """ encrypts message(int type)"""

        if hasattr(self, 'private_key') :
            return (message * self.private_key) % self.p 
        else:
            raise Exception("Private key hasn't been initialised yet")

    def decrypt_message(self, message):
        """ decrypts message(int type)"""

        return (message * self.key_inverse) % self.p

    def encrypt_key(self, priv_key):
        n = int(priv_key['n'])
        e = int(priv_key['e'])
        d = int(priv_key['d'])
        p = int(priv_key['p'])
        q = int(priv_key['q'])

        encrypted_key = {
                        'n': str(n),
                        'e': str(e),
                        'd': str(self.encrypt_message(d)),
                        'p': str(self.encrypt_message(p)),
                        'q': str(self.encrypt_message(q))
                        }
        return encrypted_key

    def decrypt_key(self, encrypted_key):
        n = int(encrypted_key['n'])
        e = int(encrypted_key['e'])
        d = int(encrypted_key['d'])
        p = int(encrypted_key['p'])
        q = int(encrypted_key['q'])
        return rsa.PrivateKey(n, e, self.decrypt_message(d), self.decrypt_message(p), self.decrypt_message(q))




