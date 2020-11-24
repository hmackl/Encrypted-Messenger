from random import randint, getrandbits
import threading
import time

class RSA:
    def generateKey(self, l=512):
        def checkPrime(n, k=3):
            r = 0
            if (n % 2 == 0 or n <= 1 or n == 4):
                return False
            elif (n <= 3):
                return True
            d = n - 1
            while (d % 2 == 0): 
                d //= 2
                r += 1
            for _ in range(k):
                try:
                    a = randint(2, n - 2)
                    x = pow(a, d, n)
                    if (x == 1 or x == n - 1):
                        continue
                    for _ in range(r):
                        x = pow(x, 2, n)
                        if (x == 1):
                            return False
                        elif (x == n - 1):
                            raise Exception('Continue')
                    return False
                except Exception:
                    continue
            return True
        def getPrime():
            while 1:
                prime = getrandbits(l)
                if (checkPrime(prime)):
                    return prime
        def greatestFactor(a, b):
            x, y, u, v = 0, 1, 1, 0
            while a != 0:
                q = b // a
                r = b % a
                m = x - u * q
                n = y - v * q
                b, a, x, y, u, v = a, r, u, v, m, n
            factor = b
            return factor, x
        def modularInverse(a, m):
            factor, x = greatestFactor(a, m)
            if factor != 1:
                return None  # modular inverse does not exist
            else:
                return x % m
        privateKey = 0
        while privateKey == 0:
            p = getPrime()
            q = getPrime()
            en = ((p - 1) * (q - 1)) // greatestFactor(p - 1, q - 1)[0]
            publicKey = p * q
            privateKey = modularInverse(65537, en)
            if (privateKey == None):
                privateKey = 0
        return publicKey, privateKey

    def encrypt(self, plain, key):
        encoded = ''
        for i in plain:
            encoded += str(ord(i) + 1000)
        print('Encoded: %s' % encoded)
        return pow(int(encoded), 65537, key)

    def decrypt(self, cypher, privateKey, publicKey):
        encoded = str(pow(cypher, publicKey, privateKey))
        print('decrypted: %s' % encoded)
        plain = ''
        for i in range(0, len(encoded), 4):
            plain += chr(int(encoded[i:i+4]) - 1000)
        return plain
        