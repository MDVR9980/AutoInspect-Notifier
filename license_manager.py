import base64
import json
import os
import uuid
import hashlib
from pathlib import Path
from datetime import datetime, date

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding


PUBLIC_KEY_B64 = """
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAsfH35yENLLeaYp6NbTNW
oy8+3UR05ID9iINWMntBw5EM2HLO2f7di2T5OwqOxi+LKoTHXuE5RBl0ATzQVcd2
xbWbCDCXX87ZMGOnsgVK00LnygWOFvuYGp2/t9OaCTpQHNY6QjFucBc2AFOyMCtD
fkXe6sZ11w5yY2VcQ1RVIiLgTnxiPRDsAKQOsmpSNSC8B4IBs+w9qac6B5Mx5JYl
yWF3xxNC7B/QjAn45zyID+eyHxA2ggpmkTsLD209/ec8vyh3t/k/vHUmifFT+lhu
g6p1flVKSzZ2OWh/A+y5dF8UNQrtWVk1knwGBzkKUnxDFa3/6jL+nzDsSH7K4D06
1wIDAQAB
"""

LICENSE_FILE = "C:/ProgramData/AutoInspectNotifier/license.dat"


class LicenseManager:
    def __init__(self):
        self.license_path = Path(LICENSE_FILE)
        self.public_key = self._load_public_key()
        self.hwid = self.get_hwid()

    def _load_public_key(self):
        pem_data = f"""-----BEGIN PUBLIC KEY-----
{PUBLIC_KEY_B64.strip()}
-----END PUBLIC KEY-----
""".encode("utf-8")
        return serialization.load_pem_public_key(pem_data)

    def get_hwid(self):
        node = str(uuid.getnode())
        return hashlib.sha256(node.encode("utf-8")).hexdigest()

    def get_activation_code(self):
        """
        کد نمایشی کوتاه برای نمایش به کاربر.
        این کد، خودِ لایسنس نیست و فقط برای شناسایی دستگاه استفاده می‌شود.
        """
        encoded = base64.urlsafe_b64encode(self.hwid.encode("utf-8")).decode("utf-8")
        short = encoded[:16]
        return "ACT-" + "-".join([short[i:i+4] for i in range(0, 16, 4)])

    def decode_activation_code(self, code: str):
        try:
            clean = code.replace("ACT-", "").replace("-", "")
            return base64.urlsafe_b64decode(clean + "==").decode("utf-8")
        except Exception:
            return None

    def _decode_token(self, token: str):
        outer = base64.b64decode(token.encode("utf-8")).decode("utf-8")
        obj = json.loads(outer)

        raw_data = base64.b64decode(obj["data"])
        signature = base64.b64decode(obj["signature"])
        payload = json.loads(raw_data.decode("utf-8"))

        return raw_data, signature, payload

    def verify_token(self, token: str):
        try:
            raw_data, signature, payload = self._decode_token(token)

            self.public_key.verify(
                signature,
                raw_data,
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            if payload.get("hwid") != self.hwid:
                return False, "این لایسنس برای این دستگاه صادر نشده است.", None

            expires = payload.get("expires")
            if expires:
                exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
                if date.today() > exp_date:
                    return False, "مدت اعتبار لایسنس به پایان رسیده است.", None

            max_users = payload.get("max_users", 1)
            if not isinstance(max_users, int) or not (1 <= max_users <= 3):
                return False, "تعداد کاربران مجاز لایسنس نامعتبر است.", None

            return True, "لایسنس معتبر است.", payload

        except Exception as e:
            return False, f"اعتبارسنجی ناموفق بود: {e}", None

    def save_license(self, payload):
        os.makedirs(self.license_path.parent, exist_ok=True)
        with open(self.license_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def load_license(self):
        if not self.license_path.exists():
            return None

        try:
            with open(self.license_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def is_activated(self):
        data = self.load_license()
        if not data:
            return False

        if data.get("hwid") != self.hwid:
            return False

        expires = data.get("expires")
        if expires:
            exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
            if date.today() > exp_date:
                return False

        return True

    def activate(self, key_input: str):
        """
        فعال‌سازی نرم‌افزار از روی کلید لایسنس ورودی.
        """

        try:
            # 🔥 بسیار مهم: حذف فاصله‌ها، newline، tab و هر کاراکتر whitespace
            cleaned_key = "".join(key_input.split())

            # 🔥 ارسال کلید تمیزشده برای اعتبارسنجی
            ok, message, payload = self.verify_token(cleaned_key)
            if not ok:
                return False, message

            # 📌 ثبت تاریخ صدور و اولین اعتبارسنجی
            payload["issued_at"] = datetime.now().strftime("%Y-%m-%d")
            payload["last_valid_date"] = datetime.now().strftime("%Y-%m-%d")

            # 📌 ذخیره‌سازی لایسنس
            self.save_license(payload)

            return True, "نرم‌افزار با موفقیت فعال شد."

        except Exception as e:
            return False, f"فعال‌سازی ناموفق بود: {e}"

    def check_valid(self):
        data = self.load_license()
        if not data:
            return False, "لایسنس یافت نشد."

        if data.get("hwid") != self.hwid:
            return False, "عدم تطابق دستگاه."

        today = datetime.now().date()

        last_valid = data.get("last_valid_date")
        if last_valid:
            last_check = datetime.strptime(last_valid, "%Y-%m-%d").date()
            if today < last_check:
                return False, "تغییر ساعت سیستم شناسایی شد."

        expires = data.get("expires")
        if expires:
            exp_date = datetime.strptime(expires, "%Y-%m-%d").date()
            if today > exp_date:
                return False, "لایسنس منقضی شده است."

        data["last_valid_date"] = today.strftime("%Y-%m-%d")
        self.save_license(data)

        return True, "معتبر"
