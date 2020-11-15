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
    p = getrandbits(512)
    if (not miller(p)):
        p = 0

q = 0
while q == 0:
    q = getrandbits(512)
    if (not miller(q)):
        q = 0

n = p * q

publicKey = n
