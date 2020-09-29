def encrypt(key, text):
    return '.'.join(str(ord(text[i]) ^ int(str(key)[i])) for i in range(len(text)))
def decrypt(key, text):
    text = text.split('.')
    plainText = ''.join(chr(int(text[i]) ^ int(str(key)[i])) for i in range(len(text)))
    return plainText
encrypted = encrypt(29384029, 'Helo')
print('Encrypted: ' + encrypted)
decrypted  = decrypt(29384029, encrypted)
print('Decrypted: ' + decrypted)