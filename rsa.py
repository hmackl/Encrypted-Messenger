from random import randint, getrandbits
import threading
import time

def miller(n, k=2):
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

# p = 0
# start = time.time()
# while p == 0:
#     p = getrandbits(4096)
#     if (not miller(p)):
#         p = 0
#     else:
#         t = time.time() - start
#         print('Big prime: %i found in %i seconds' % (p, t))
#         raise Exception()

p = 0
while p == 0:
    p = getrandbits(32)
    if (not miller(p)):
        p = 0

q = 0
while q == 0:
    q = getrandbits(32)
    if (not miller(q)):
        q = 0

print('P: %i, Q: %i' % (p, q))
n = p * q
print('N: %i' % n)
def greatestFactor(a, b):
    x = 0
    y = 1
    u = 1
    v = 0
    while a != 0:
        q = b // a
        r = b % a
        m = x - u * q
        n = y - v * q
        b = a
        a = r
        x = u
        y = v
        u = m
        v = n
    gf = b
    return gf, x

en = ((p - 1) * (q - 1)) // greatestFactor(p - 1, q - 1)[0]
print('en %i' % en)
e = 65537
def modularInverse(a, m):
    factor, x = greatestFactor(a, m)
    if factor != 1:
        return None  # modular inverse does not exist
    else:
        return x % m
print(e, en)
privateKey = modularInverse(e, en)
print('modinv %i' % privateKey)
publicKey = n + e

def parse(word):
    borg = ''
    for i in word:
        uni = '00' + str(ord(i))
        borg += uni[3:]
    return int(borg)
p = parse('hello')

print('Encoded: %i' % p)
c = pow(p, e, n)
print('Encrypted: %i' % c)
print('Private key: %i' % privateKey)
m = pow(c, privateKey, n)
print('Decrypted: %i' % m)
