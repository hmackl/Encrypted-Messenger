from random import randint, getrandbits
from math import ceil
import threading

sbox = [
        '63', '7c', '77', '7b', 'f2', '6b', '6f', 'c5', '30', '01', '67', '2b', 'fe', 'd7', 'ab', '76',
        'ca', '82', 'c9', '7d', 'fa', '59', '47', 'f0', 'ad', 'd4', 'a2', 'af', '9c', 'a4', '72', 'c0',
        'b7', 'fd', '93', '26', '36', '3f', 'f7', 'cc', '34', 'a5', 'e5', 'f1', '71', 'd8', '31', '15',
        '04', 'c7', '23', 'c3', '18', '96', '05', '9a', '07', '12', '80', 'e2', 'eb', '27', 'b2', '75',
        '09', '83', '2c', '1a', '1b', '6e', '5a', 'a0', '52', '3b', 'd6', 'b3', '29', 'e3', '2f', '84',
        '53', 'd1', '00', 'ed', '20', 'fc', 'b1', '5b', '6a', 'cb', 'be', '39', '4a', '4c', '58', 'cf',
        'd0', 'ef', 'aa', 'fb', '43', '4d', '33', '85', '45', 'f9', '02', '7f', '50', '3c', '9f', 'a8',
        '51', 'a3', '40', '8f', '92', '9d', '38', 'f5', 'bc', 'b6', 'da', '21', '10', 'ff', 'f3', 'd2',
        'cd', '0c', '13', 'ec', '5f', '97', '44', '17', 'c4', 'a7', '7e', '3d', '64', '5d', '19', '73',
        '60', '81', '4f', 'dc', '22', '2a', '90', '88', '46', 'ee', 'b8', '14', 'de', '5e', '0b', 'db',
        'e0', '32', '3a', '0a', '49', '06', '24', '5c', 'c2', 'd3', 'ac', '62', '91', '95', 'e4', '79',
        'e7', 'c8', '37', '6d', '8d', 'd5', '4e', 'a9', '6c', '56', 'f4', 'ea', '65', '7a', 'ae', '08',
        'ba', '78', '25', '2e', '1c', 'a6', 'b4', 'c6', 'e8', 'dd', '74', '1f', '4b', 'bd', '8b', '8a',
        '70', '3e', 'b5', '66', '48', '03', 'f6', '0e', '61', '35', '57', 'b9', '86', 'c1', '1d', '9e',
        'e1', 'f8', '98', '11', '69', 'd9', '8e', '94', '9b', '1e', '87', 'e9', 'ce', '55', '28', 'df',
        '8c', 'a1', '89', '0d', 'bf', 'e6', '42', '68', '41', '99', '2d', '0f', 'b0', '54', 'bb', '16'
]
sboxInv = [
        '52', '09', '6a', 'd5', '30', '36', 'a5', '38', 'bf', '40', 'a3', '9e', '81', 'f3', 'd7', 'fb',
        '7c', 'e3', '39', '82', '9b', '2f', 'ff', '87', '34', '8e', '43', '44', 'c4', 'de', 'e9', 'cb',
        '54', '7b', '94', '32', 'a6', 'c2', '23', '3d', 'ee', '4c', '95', '0b', '42', 'fa', 'c3', '4e',
        '08', '2e', 'a1', '66', '28', 'd9', '24', 'b2', '76', '5b', 'a2', '49', '6d', '8b', 'd1', '25',
        '72', 'f8', 'f6', '64', '86', '68', '98', '16', 'd4', 'a4', '5c', 'cc', '5d', '65', 'b6', '92',
        '6c', '70', '48', '50', 'fd', 'ed', 'b9', 'da', '5e', '15', '46', '57', 'a7', '8d', '9d', '84',
        '90', 'd8', 'ab', '00', '8c', 'bc', 'd3', '0a', 'f7', 'e4', '58', '05', 'b8', 'b3', '45', '06',
        'd0', '2c', '1e', '8f', 'ca', '3f', '0f', '02', 'c1', 'af', 'bd', '03', '01', '13', '8a', '6b',
        '3a', '91', '11', '41', '4f', '67', 'dc', 'ea', '97', 'f2', 'cf', 'ce', 'f0', 'b4', 'e6', '73',
        '96', 'ac', '74', '22', 'e7', 'ad', '35', '85', 'e2', 'f9', '37', 'e8', '1c', '75', 'df', '6e',
        '47', 'f1', '1a', '71', '1d', '29', 'c5', '89', '6f', 'b7', '62', '0e', 'aa', '18', 'be', '1b',
        'fc', '56', '3e', '4b', 'c6', 'd2', '79', '20', '9a', 'db', 'c0', 'fe', '78', 'cd', '5a', 'f4',
        '1f', 'dd', 'a8', '33', '88', '07', 'c7', '31', 'b1', '12', '10', '59', '27', '80', 'ec', '5f',
        '60', '51', '7f', 'a9', '19', 'b5', '4a', '0d', '2d', 'e5', '7a', '9f', '93', 'c9', '9c', 'ef',
        'a0', 'e0', '3b', '4d', 'ae', '2a', 'f5', 'b0', 'c8', 'eb', 'bb', '3c', '83', '53', '99', '61',
        '17', '2b', '04', '7e', 'ba', '77', 'd6', '26', 'e1', '69', '14', '63', '55', '21', '0c', '7d'
]
rCon = [0x8d, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80, 0x1b, 0x26]

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
        return hex(publicKey), hex(privateKey)

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

class AES:
    def subWord(self, byteArray):
        sByteArray = []
        for byte in byteArray:
            index = (16 * int(byte[0], 16)) + int(byte[1], 16)
            sByteArray.append(sbox[index])
        return sByteArray
    def rotate(self, chars, offset=1):
        for _ in range(offset):
            chars = [chars[1], chars[2], chars[3], chars[0]]
        return chars
    def keySchedule(self, key):
        def huffmanTree(plain):
            c = {}
            tree = []
            for char in plain:
                if (char not in c):
                    c[char] = plain.count(char)
            for key in sorted(c, key=c.__getitem__):
                tree.append([key, c[key]])
                c[key] = c.pop(key)
            while len(tree) > 2:
                childs = [tree.pop(0), tree.pop(0)]
                node = [childs[0][0] + childs[1][0], childs[0][1] + childs[1][1], childs]
                for leaf in range(len(tree)):
                    if (tree[leaf][1] > node[1]):
                        tree = tree[:leaf] + [node] + tree[leaf:]
                        break
                    elif(leaf + 1== len(tree)):
                        tree += [node]
                        break
            def traverse(tree, branch=''):
                for l in range(2):
                    if (len(tree[l]) == 3):
                        traverse(tree[l][2], str(l) + branch)
                    else:
                        c[tree[l][0]] = str(int(branch + str(l), 2))
            traverse(tree)
            encoded = ''
            for i in range(len(plain)):
                encoded += c[plain[i]]
            return ('0' * 32 + hex(int(encoded))[2:])[-32:]
        key = huffmanTree(key)
        key = [key[i:i+2] for i in range(0, len(key), 2)]
        N = 4
        K = [key[i:i+4] for i in range(0, 16, 4)]
        R = 11
        W = [None] * ((4*R) - 1)
        for i in range((4*R) - 1):
            w = W[i-1]
            if (i < N):
                W[i] = K[i]
            else:
                if (i % 4 == 0):
                    w = self.subWord(self.rotate(w))
                    w = [('0'+hex(rCon[i//4] ^ int(w[x], 16))[2:])[-2:] for x in range(4)]
                W[i] = [('0'+hex(int(W[i-4][x], 16) ^ int(str(w[x]), 16))[2:])[-2:] for x in range(4)]
        return W
    def encrypt(self, plain, keys):
        def mixColumns(state):
            def timesTwo(v):
                s = v << 1
                s &= 0xff
                if (v & 128) != 0:
                    s = s ^ 0x1b
                return s
            def timesThree(v):
                return timesTwo(v) ^ v
            def mixColumn(column):
                r = [
                    timesTwo(column[0]) ^ timesThree(
                        column[1]) ^ column[2] ^ column[3],
                    timesTwo(column[1]) ^ timesThree(
                        column[2]) ^ column[3] ^ column[0],
                    timesTwo(column[2]) ^ timesThree(
                        column[3]) ^ column[0] ^ column[1],
                    timesTwo(column[3]) ^ timesThree(
                        column[0]) ^ column[1] ^ column[2],
                ]
                return r
            mixstate = [[], [], [], []]
            for i in range(4):
                col = [int(state[j][i], 16) for j in range(4)]
                col = mixColumn(col)
                for i in range(4):
                    mixstate[i].append(('0'+hex(col[i])[2:])[-2:])
            return mixstate
        #producing states
        states = []
        for i in range(0, len(plain), 8):
            states.append([])
            for x in range(0, 8, 2):
                states[-1].append(plain[i:i+8][x:x+2])
        for state in range(0, len(states), 4):
            state = states[state:state+4]
            #add round key
            for row in range(len(state)):
                for i in range(len(state[row])):
                    state[row][i] = ('0'+hex(int(state[row][i], 16) ^ int(keys[row][i], 16))[2:])[-2:]
            #subBytes and rotate
            for i in range(9):
                for row in range(len(state)):
                    state[row] = self.rotate(self.subWord(state[row]), row)
                state = mixColumns(state)
                for row in range(len(state)):
                    state[row] = [('0' + hex(int(state[row][c], 16) ^ int(keys[(4*i)+row][c], 16))[2:])[-2:] for c in range(4)]
            #final round
            state = [self.subWord(state[row]) for row in range(len(state))]
            state = [self.rotate(state[row])]
            #need to add round key
            #https://en.wikipedia.org/wiki/Advanced_Encryption_Standard


aes = AES()
rsa = RSA()
syncKeys = aes.keySchedule('password')
asyncKey = rsa.generateKey()
public = asyncKey[0]
private = asyncKey[1]
aes.encrypt(public[2:], syncKeys)
#print(public, private)