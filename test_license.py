import base64
import json
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

# همان کلیدی که داخل license_manager.py است
from license_manager import PUBLIC_KEY_B64

key = input("Paste license key:\n").strip()

print("1) Input length:", len(key))

outer = base64.b64decode(key)
print("2) Outer base64 decoded OK, length:", len(outer))

outer_json = json.loads(outer.decode())
print("3) Outer JSON parsed OK")
print("   keys:", list(outer_json.keys()))

data_b64 = outer_json["data"]
sig_b64 = outer_json["signature"]

raw = base64.b64decode(data_b64)
print("4) Inner data base64 decoded OK, length:", len(raw))
print("   raw data:", raw.decode())

signature = base64.b64decode(sig_b64)
print("5) Signature base64 decoded OK, length:", len(signature))

# ساخت PEM دقیقاً مثل license_manager.py
pem = f"""-----BEGIN PUBLIC KEY-----
{PUBLIC_KEY_B64.strip()}
-----END PUBLIC KEY-----
""".encode()

public_key = serialization.load_pem_public_key(pem)
print("6) Public key loaded OK")

try:
    public_key.verify(
        signature,
        raw,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    print("7) ✅ Signature VALID")
except Exception as e:
    print("7) ❌ Signature verification FAILED:", e)
