# psychic-umbrella

a simple reverse shell C2 backend with websocket communication with a web panel actively being developed.

**for proof of concept purposes. dont do illegal shit with this pls**

## first step is to generate your encryption key.

run `encrypt.py` first to generate your encrypted seed.

```python
import base64

def encrypt_seed(real_seed, key="change-me"): # you can generate one of these at https://www.random.org/strings/
    encrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(real_seed))
    return base64.b64encode(encrypted.encode()).decode()

# CHANGE THIS
seed = "change-me"

print("Encrypted version:")
print(encrypt_seed(seed))
```
copy and save both the encrypted key and the seed.

---

## server setup

1. install packages:
   ```bash
   npm install express helmet socket.io jsonwebtoken dotenv
   ```

2. rename `example.env` to `.env` and edit it to fit your configuration.
   ```env
   JWT_SECRET=change-me
   C2_PATH=/api/v3/sync
   PORT=3000
   ```

3. start the server:
   ```bash
   node server.js
   ```

---

## client setup

1. update `client.py` with your encrypted seed and key.

2. install python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. run the script:
   ```bash
   python client.py
   ```

---

## debug tool

run `debug.py` to verify your keys and bot configuration. (edit it to include your encrypted seed and key.)
