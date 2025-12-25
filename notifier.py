"""
notifier.py
-----------
Fixed version with HTML escaping for Telegram
"""

import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    A robust Telegram notification client.
    """
    
    def __init__(self, token: str, chat_id: str):
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        logger.info("TelegramNotifier initialized successfully")
    
    def send_message(self, message: str) -> bool:
        """
        Send a text message to Telegram.
        """
        if not message or not message.strip():
            logger.warning("Attempted to send empty message. Skipping.")
            return False
        
        endpoint = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": True
        }
        
        try:
            logger.info(f"Sending message to Telegram")
            response = requests.post(endpoint, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    logger.info("✅ Message sent successfully")
                    return True
                else:
                    logger.error(f"❌ Telegram error: {result.get('description')}")
                    return False
            else:
                logger.error(f"❌ HTTP Error {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.error("❌ No internet connection")
            return False
        except requests.exceptions.Timeout:
            logger.error("❌ Request timeout")
            return False
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return False


if __name__ == "__main__":
    TOKEN = "8329505275:AAFsbYpt2EAYyx1y5sfD9fU9eW9DrlVIsQ8"
    CHAT_ID = "1277763542"
    
    notifier = TelegramNotifier(token=TOKEN, chat_id=CHAT_ID)
    notifier.send_message("🔴 Test: The Sniper is active!")