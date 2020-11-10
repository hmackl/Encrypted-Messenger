from random import randint

def miller(num):
    i = 0
    while (2 ** i < num):
        i += 1
        if ((num - 1) % (2 ** i) == 0 and ((num - 1) / (2 ** i)) % 2 == 1):
            s = i
            d = num / (2 ** i)
            print('s: %i, d: %i' % (s, d))
            a = randint(2, num - 2)
            a = 174
            (a ** (2 ** ))
class RSA:
    def prime(self):
        r = randint(999, 10000)

miller(221)