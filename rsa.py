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
n = p * q
en = (p - 1) * (q - 1)
print('En:  %i' % en)
publicKey = n

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

e = 65537
def modularInverse(a, m):
    factor, x = greatestFactor(a, m)
    if factor != 1:
        return None  # modular inverse does not exist
    else:
        return x % m

privateKey = modularInverse(e, en)
publicKey = n + e

def parse(word):
    borg = ''
    for i in word:
        uni = '000' + str(ord(i))
        borg += uni[3:]
    return int(borg)
print(privateKey)
p = parse('hello')
p = 1230000
print('Encoded: %i' % p)
c = (p ** e) % n
print('Encrypted: %i' % c)
print('Private key: %i' % privateKey)

dp = privateKey % (p - 1)
print('a')
dq = privateKey % (q - 1)
print('b')
qinv = modularInverse(q, p)
print('c')
m1 = (c ** dp) % p
print('d')
m2 = (c ** dq) % q
print('e')
h = (qinv * (m1 - m2)) % p
print('f')
m = m2 + h * q
print('g')
print('Decrypted: %i' % m)

# altp = (c ** privateKey) % n
# print('Decrypted: %i' % altp)
