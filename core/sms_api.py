"""
مدیریت ارسال پیامک از طریق API قاصدک
"""
import requests
import logging
from typing import Optional
from settings import SMS_TEMPLATE

logger = logging.getLogger(__name__)


class SMSManager:
    def __init__(self, api_key: str, line_number: str):
        self.api_key = api_key
        self.line_number = line_number
        self.base_url = "https://api.ghasedak.me/v2/sms/send/simple"

    def build_message(self, plate: str, expire_date: str) -> str:
        """
        ساخت متن پیامک
        """
        message = SMS_TEMPLATE.format(
            plate=plate,
            expire_date=expire_date
        )
        
        return message

    def send_sms(
        self,
        phone: str,
        plate: str,
        expire_date: str
    ) -> bool:
        """
        ارسال پیامک به یک شماره
        """
        try:
            message = self.build_message(plate, expire_date)

            payload = {
                "message": message,
                "receptor": phone,
                "linenumber": self.line_number
            }

            headers = {
                "apikey": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded"
            }

            response = requests.post(
                self.base_url,
                data=payload,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()

                if result.get("result", {}).get("code") == 200:
                    logger.info(
                        f"SMS sent successfully to {phone}"
                    )
                    return True
                else:
                    logger.error(
                        f"SMS API error: {result}"
                    )
                    return False
            else:
                logger.error(
                    f"HTTP error {response.status_code}: {response.text}"
                )
                return False

        except requests.exceptions.Timeout:
            logger.error(f"SMS timeout for {phone}")
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"SMS request error: {e}")
            return False

        except Exception as e:
            logger.error(f"SMS send error: {e}")
            return False

    def send_bulk_sms(
        self,
        subscribers: list
    ) -> dict:
        """
        ارسال دسته‌ای پیامک
        
        بازگشت:
        {
            "success": تعداد موفق,
            "failed": تعداد ناموفق
        }
        """
        success_count = 0
        failed_count = 0

        for subscriber in subscribers:
            phone = subscriber.get("phone")
            plate = subscriber.get("plate")
            expire_date = subscriber.get("expire_date")

            if self.send_sms(phone, plate, expire_date):
                success_count += 1
            else:
                failed_count += 1

        logger.info(
            f"Bulk SMS: {success_count} success, {failed_count} failed"
        )

        return {
            "success": success_count,
            "failed": failed_count
        }
