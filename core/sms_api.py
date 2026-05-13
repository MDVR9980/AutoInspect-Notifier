# autoinspect-notifier/core/sms_api.py

import requests
import logging
from settings import SMS_API_KEY # Import the API key from the central settings file

# --- Setup logging for this module ---
log = logging.getLogger(__name__)


class SmsApiClient:
    """
    A client to interact with the Ghasdak SMS API.

    This class handles the sending of SMS messages by making HTTP requests
    to the provider's API endpoint.
    """

    # The base URL for the Ghasdak API.
    API_URL = "http://api.ghasedaksms.com/v2/sms/send/simple"

    def __init__(self, api_key: str):
        """
        Initializes the SMS API client.

        Args:
            api_key (str): The API key for authenticating with the service.
        """
        # Store the API key provided during instantiation.
        self.api_key = api_key

    def send_sms(self, receptor: str, message: str) -> bool:
        """
        Sends a single SMS message to a specified recipient.

        Args:
            receptor (str): The recipient's mobile number.
            message (str): The text content of the message.

        Returns:
            bool: True if the message was sent successfully (API returned status 200),
                  False otherwise.
        """
        # Ensure the API key is set before proceeding.
        if not self.api_key or self.api_key == "YOUR_API_KEY_HERE":
            log.error("SMS API key is not configured in settings.py.")
            return False

        # Prepare the data payload for the POST request.
        # This structure is based on the Ghasdak API documentation.
        payload = {
            'receptor': receptor,
            'message': message,
        }
        
        # Prepare the headers for the HTTP request, including the API key.
        headers = {
            'apikey': self.api_key,
        }

        try:
            # Send the POST request to the API endpoint.
            # A timeout is set to prevent the application from hanging indefinitely.
            response = requests.post(self.API_URL, data=payload, headers=headers, timeout=10)
            
            # Raise an exception for bad status codes (4xx or 5xx).
            response.raise_for_status()

            # Log the successful response from the API.
            log.info(f"SMS sent successfully to {receptor}. Response: {response.json()}")
            return True

        except requests.exceptions.RequestException as e:
            # Catch any network-related errors (e.g., timeout, connection error).
            log.error(f"Failed to send SMS to {receptor}. Network or API error: {e}")
            return False

# --- Global Instance ---
# Create a single, reusable instance of the client using the key from settings.
# This instance can be imported and used by other parts of the application.
sms_client = SmsApiClient(api_key=SMS_API_KEY)
