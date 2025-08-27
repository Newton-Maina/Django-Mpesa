from django.http import HttpResponse
import requests
from requests.auth import HTTPBasicAuth
import json
from .credentials import MpesaAccessToken, LipanaMpesaPpassword
from django.shortcuts import render
from django.contrib import messages
import re
import logging

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("mpesa_debug.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def home(request):
    return render(request, 'home.html', {'navbar': 'home'})


def token(request):
    consumer_key = '77bgGpmlOxlgJu6oEXhEgUgnu0j2WYxA'
    consumer_secret = 'viM8ejHgtEmtPTHd'
    api_URL = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    try:
        r = requests.get(api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        r.raise_for_status()  # Raise exception for HTTP errors
        mpesa_access_token = r.json()
        validated_mpesa_access_token = mpesa_access_token.get("access_token")

        if not validated_mpesa_access_token:
            messages.error(request, "Failed to get access token")
            return render(request, 'token.html', {"token": None})

        return render(request, 'token.html', {"token": validated_mpesa_access_token})
    except requests.RequestException as e:
        messages.error(request, f"Error fetching token: {str(e)}")
        return render(request, 'token.html', {"token": None})



def pay(request):
    debug_info = {}  # Optional: pass to template for real-time viewing

    if request.method == "POST":
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        # Validate phone
        if not phone or not re.match(r'^\d{10,12}$', phone):
            msg = "Invalid phone number"
            messages.error(request, msg)
            logger.warning(msg)
            return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info})

        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            msg = "Invalid amount"
            messages.error(request, msg)
            logger.warning(msg)
            return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info})

        # Get access token
        access_token = MpesaAccessToken.validated_mpesa_access_token
        if not access_token:
            msg = "Access token is missing or invalid"
            messages.error(request, msg)
            logger.error(msg)
            return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info})

        # API request
        api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        payload = {
            "BusinessShortCode": LipanaMpesaPpassword.Business_short_code,
            "Password": LipanaMpesaPpassword.decode_password,
            "Timestamp": LipanaMpesaPpassword.lipa_time,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": LipanaMpesaPpassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": "https://your-domain.com/callback",
            "AccountReference": "NMG Softwares",
            "TransactionDesc": "Web Development Charges"
        }

        debug_info['request_payload'] = payload

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            debug_info['status_code'] = response.status_code
            debug_info['response_text'] = response.text

            response.raise_for_status()  # HTTP errors
            res_data = response.json()
            debug_info['response_json'] = res_data
            logger.info(f"STK Push response: {res_data}")

            if res_data.get("ResponseCode") == "0":
                msg = "STK Push sent successfully. Check your phone."
                messages.success(request, msg)
                logger.info(msg)
            else:
                err_msg = res_data.get('errorMessage') or res_data.get('message') or "Unknown error"
                messages.error(request, f"STK Push failed: {err_msg}")
                logger.error(f"STK Push failed: {err_msg}")

        except requests.Timeout:
            msg = "Request timed out"
            messages.error(request, msg)
            logger.error(msg)
        except requests.ConnectionError as e:
            msg = f"Connection error: {str(e)}"
            messages.error(request, msg)
            logger.error(msg)
        except requests.HTTPError as e:
            msg = f"HTTP error: {str(e)}"
            messages.error(request, msg)
            logger.error(msg)
        except json.JSONDecodeError:
            msg = "Failed to parse response JSON"
            messages.error(request, msg)
            logger.error(msg)
        except Exception as e:
            msg = f"Unexpected error: {str(e)}"
            messages.error(request, msg)
            logger.exception(msg)

        return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info})

    return render(request, 'pay.html', {'navbar': 'stk'})



def stk(request):
    return render(request, 'pay.html', {'navbar': 'stk'})
