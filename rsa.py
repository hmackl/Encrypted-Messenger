from random import randint, getrandbits

def miller(n, k=2):
    i = 0
    p = 1
    if (n < 3):
        return p
    elif (n % 2 == 0):
        return 0
    while (2 ** i < n):
        i += 1
        if ((n - 1) % (2 ** i) == 0):
            r = i
            d = int((n - 1) / (2 ** i))
            for _ in range(k):
                a = randint(2, n - 2)
                x = pow(a, d, n)
                if (x != 1 and x != n - 1):
                    for _ in range(r):
                        x = pow(x, 2, n)
                        if (x != n - 1):
                            p = 0
        break
    return p

def primeNumber():
    p = 0
    while p == 0:
        p = getrandbits(512)
        if (not miller(p)):
            p = 0
        else:
            exception = 'BIG Prime: %i' % p
            raise Exception(exception)
    
primeNumber()
