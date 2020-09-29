import prime
password = 'thisismyuserpasswordwhichisveryvyerlong'
privateKey = 0
for c in password: privateKey += ord(c)
keys = []
keys.append(prime.prime())
keys.append(prime.primitiveRoot(keys[0]))
keys.append(keys[1] ** privateKey % keys[0])
print('Keys 1: prime: %s, root: %s, privatekey: %s' % (keys[0], keys[1], keys[2]))

def encrypt(key, text):
    return '.'.join(str(ord(text[i]) ^ int(str(key)[i])) for i in range(len(text)))
def decrypt(key, text):
    return ''.join(chr(int(text[i]) ^ int(str(key)[i])) for i in range(len(text)))

encrypted = encrypt(29384029, 'Helo')
print('Encrypted: ' + encrypted)
decrypted  = decrypt(29384029, encrypted.split('.'))
print('Decrypted: ' + decrypted)
