from random import randint

def miller(n):
    i = 0
    while (2 ** i < n):
        i += 1
        if ((n - 1) % (2 ** i) == 0):
            r = i
            d = int((n - 1) / (2 ** i))
            print('r: %i, d: %i' % (r, d))
            a = randint(2, n - 2)
            a = 174
            x = (a ** d) % n
            print('x ', x)
            print('n ', n)
            if (x == 1 or x == n - 1):
                print('c')
                for i in range(r - 1):
                    x = (x ** 2) % n
                    if (x == n - 1):
                        return 0
    return 1

class RSA:
    def prime(self):
        r = randint(999, 10000)

print(miller(221))
