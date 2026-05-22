import base64

def encrypt_seed(real_seed, key="change-me"): # you can generate one of these at https://www.random.org/strings/
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(real_seed))
    return base64.b64encode(encrypted.encode()).decode()

# CHANGE THIS
seed = "change-me"

print("Encrypted version:")
print(encrypt_seed(seed))