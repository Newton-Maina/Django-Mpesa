import base64
import logging
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from decouple import config

logger = logging.getLogger(__name__)

class MpesaC2bCredential:
    """
    Configuration class for M-Pesa API credentials.
    
    Reads sensitive configuration (Consumer Key, Secret, API URL) from environment variables.
    """
    consumer_key = config("MPESA_CONSUMER_KEY")
    consumer_secret = config("MPESA_CONSUMER_SECRET")
    api_URL = config("MPESA_API_URL")  # https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials


class MpesaAccessToken:
    """
    Handles generation and caching of M-Pesa OAuth access tokens.
    
    Implements a singleton-like pattern to cache the token until it expires,
    reducing unnecessary calls to the Safaricom API.
    """
    validated_mpesa_access_token = None
    token_expiry = None

    @classmethod
    def get_access_token(cls):
        """
        Retrieves a valid access token.
        
        Checks if a valid, non-expired token exists in the class cache.
        If not, it requests a new one from Safaricom using the Consumer Key and Secret.
        
        Returns:
            str: The access token string if successful.
            None: If the request fails.
        """
        if cls.validated_mpesa_access_token and cls.token_expiry and cls.token_expiry > datetime.now():
            logger.info(f"Using cached access token: {cls.validated_mpesa_access_token}")
            return cls.validated_mpesa_access_token

        try:
            response = requests.get(
                MpesaC2bCredential.api_URL,
                auth=HTTPBasicAuth(MpesaC2bCredential.consumer_key, MpesaC2bCredential.consumer_secret),
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")

            if not access_token:
                logger.error("No access token returned in response")
                return None

            cls.validated_mpesa_access_token = access_token
            # Default expiry is 3599 seconds (1 hour)
            cls.token_expiry = datetime.now() + timedelta(seconds=int(data.get("expires_in", 3599)))
            logger.info(f"New access token fetched successfully: {access_token}")
            return access_token

        except requests.RequestException as e:
            logger.error(f"Error fetching access token: {str(e)}")
            return None


class LipanaMpesaPassword:
    """
    Utilities for generating the secure password required for STK Push requests.
    """
    Business_short_code = config("MPESA_SHORT_CODE")
    passkey = config("MPESA_PASSKEY")

    @classmethod
    def generate_password(cls):
        """
        Generates the base64-encoded password for STK Push.
        
        The password is a combination of Shortcode + Passkey + Timestamp,
        encoded in Base64.
        
        Returns:
            tuple: (encoded_password, timestamp_string)
        """
        cls.lipa_time = datetime.now().strftime('%Y%m%d%H%M%S')
        data_to_encode = cls.Business_short_code + cls.passkey + cls.lipa_time
        online_password = base64.b64encode(data_to_encode.encode())
        cls.decode_password = online_password.decode('utf-8')
        return cls.decode_password, cls.lipa_time