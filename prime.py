from random import randrange, getrandbits, randint
import math
def checkPrime(n, k=128):
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    for _ in range(k):
        a = randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

def generatePrimes(length):
    p = getrandbits(length)
    p |= (1 << length - 1) | 1
    return p

def prime(length=32):
    p = 4
    while not checkPrime(p, 128):
        p = generatePrimes(length)
    return p

def primeFactors(s, n):
    while (n % 2 == 0):
        s.add(2)
        n = n // 2
    for i in range(3, int(math.sqrt(n)), 2):
        while (n % i == 0):
            s.add(i)
            n = n // i
    if (n > 2):
        s.add(n)

def power(a, b, c):
    result = 1
    a = a % c
    while (b > 0):
        if (b & 1):
            result = (result * a) % c
        b = b >> 1
        a = (a * a) % c
    return result

def primitiveRoot(n):
    s = set()
    a = n - 1
    primeFactors(s, a)
    while True:
        x = randint(2, a)
        f = False
        for y in s:
            if (power(x, a // y, n) == 1):
                f = True
                break
        if f == False:
            return x
    return -1
