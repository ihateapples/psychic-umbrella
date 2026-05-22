# before you run this script, make sure you have your keys (run encrypt.py first)
import hashlib
import base64
import platform
import uuid

def decrypt_seed():
    encrypted = "change-me" # encrypted seed (from encrypt.py output)
    key = "change-me" # same key from encrypt.py
    data = base64.b64decode(encrypted)
    decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data.decode('utf-8', errors='ignore')))
    return decrypted.strip()

SECRET_SEED = decrypt_seed()
BOT_ID = hashlib.sha256(
    f"{platform.node()}|{':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 48, 8)])}".encode()
).hexdigest()[:32]

JWT_SECRET = hashlib.sha256(f"{SECRET_SEED}{BOT_ID[:16]}C2SALT2026".encode()).hexdigest()

print("="*60)
print("diagnostic output")
print("="*60)
print(f"SECRET_SEED     : {SECRET_SEED}")
print(f"BOT_ID          : {BOT_ID}")
print(f"BOT_ID[:16]     : {BOT_ID[:16]}")
print(f"JWT_SECRET      : {JWT_SECRET}")
print("="*60)