from django.http import JsonResponse
import requests
import json
from .credentials import MpesaAccessToken, LipanaMpesaPassword
from django.shortcuts import render
from django.contrib import messages
import re
import logging
from decouple import config
from datetime import datetime
from .models import Transaction
from django.views.decorators.csrf import csrf_exempt

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler("mpesa_debug.log")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def home(request):
    """
    Renders the home page of the application.
    """
    return render(request, 'home.html', {'navbar': 'home'})

def token(request):
    """
    Demonstrates retrieving and displaying an M-Pesa Access Token.
    
    This view calls the MpesaAccessToken helper to get a valid token
    and renders it on the screen. It helps in verifying credentials.
    """
    try:
        access_token = MpesaAccessToken.get_access_token()
        if not access_token:
            messages.error(request, "Failed to obtain access token.")
            return render(request, 'token.html', {
                "token": None,
                "error": "No access token returned.",
                "environment": "Production",
                "current_time": datetime.now(),
                "short_code": config('MPESA_SHORT_CODE'),
                "callback_url": config('MPESA_CALLBACK_URL')
            })

        return render(request, 'token.html', {
            "token": access_token,
            "environment": "Production",
            "current_time": datetime.now(),
            "short_code": config('MPESA_SHORT_CODE'),
            "callback_url": config('MPESA_CALLBACK_URL')
        })

    except Exception as err:
        messages.error(request, f"An error occurred: {err}")
        logger.error(f"Error in token view: {err}")
        return render(request, 'token.html', {
            "token": access_token,
            "environment": "Production",
            "current_time": datetime.now(),
            "short_code": config('MPESA_SHORT_CODE'),
            "callback_url": config('MPESA_CALLBACK_URL'),
            "debug_token": access_token
        })


def pay(request):
    """
    Handles the STK Push payment process.
    
    GET: Renders the payment form.
    POST: Processes the form data, initiates an STK Push via Safaricom API, 
          and handles the immediate response (synchronous).
          
    Key steps:
    1. Validates phone number and amount.
    2. Generates an access token.
    3. Constructs the API payload (Shortcode, Timestamp, Password, etc.).
    4. Sends the request to Safaricom's STK Push endpoint.
    5. Stores the initial transaction details in the database.
    """
    debug_info = {}
    checkout_request_id = None

    if request.method == "POST":
        phone = request.POST.get('phone')
        amount = request.POST.get('amount')

        # Validate phone
        if not phone or not re.match(r'^\d{10,12}$', phone):
            msg = "Invalid phone number. Must be 10-12 digits (e.g., 254712345678)."
            messages.error(request, msg)
            logger.warning(msg)
            return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info})

        # Ensure phone starts with 254
        if not phone.startswith('254'):
            phone = '254' + phone[-9:]

        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            msg = "Invalid amount. Must be a positive number."
            messages.error(request, msg)
            logger.warning(msg)
            return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info})

        # Get access token
        access_token = MpesaAccessToken.get_access_token()
        if not access_token:
            msg = "Failed to obtain access token"
            messages.error(request, msg)
            logger.error(msg)
            return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info})

        # API request
        api_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}"}
        password, timestamp = LipanaMpesaPassword.generate_password()
        
        # Use callback URL from environment
        callback_url = config('MPESA_CALLBACK_URL')
        
        payload = {
            "BusinessShortCode": LipanaMpesaPassword.Business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": LipanaMpesaPassword.Business_short_code,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "AccountReference": "Your Mpesa-Test",
            "TransactionDesc": "Payment for your Company"
        }

        debug_info['request_payload'] = payload

        try:
            response = requests.post(api_url, json=payload, headers=headers, timeout=30)
            debug_info['status_code'] = response.status_code
            debug_info['response_text'] = response.text

            response.raise_for_status()
            res_data = response.json()
            debug_info['response_json'] = res_data
            logger.info(f"STK Push response: {res_data}")

            if res_data.get("ResponseCode") == "0":
                msg = "STK Push sent successfully. Check your phone."
                messages.success(request, msg)
                logger.info(msg)
                
                # Save transaction
                checkout_request_id = res_data.get("CheckoutRequestID")
                Transaction.objects.create(
                    checkout_request_id=checkout_request_id,
                    merchant_request_id=res_data.get("MerchantRequestID"),
                    phone_number=phone,
                    amount=amount,
                    status="Pending"
                )
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

        return render(request, 'pay.html', {'navbar': 'stk', 'debug': debug_info, 'checkout_request_id': checkout_request_id})

    return render(request, 'pay.html', {'navbar': 'stk'})

def stk(request):
    """
    Alias view for the pay page.
    """
    return render(request, 'pay.html', {'navbar': 'stk'})

@csrf_exempt
def callback(request):
    """
    Process the asynchronous callback from Safaricom.
    
    This endpoint is hit by Safaricom's servers after the user interacts (enters PIN or cancels) 
    with the STK push on their phone.
    
    It updates the transaction status in the database based on the ResultCode.
    """
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            logger.info(f"Callback received: {data}")
            
            stk_callback = data.get('Body', {}).get('stkCallback', {})
            checkout_request_id = stk_callback.get('CheckoutRequestID')
            result_code = stk_callback.get('ResultCode')
            result_desc = stk_callback.get('ResultDesc')
            
            if checkout_request_id:
                try:
                    transaction = Transaction.objects.get(checkout_request_id=checkout_request_id)
                    transaction.result_code = result_code
                    transaction.result_desc = result_desc
                    
                    if result_code == 0:
                        transaction.status = "Success"
                        # Extract receipt number if available
                        items = stk_callback.get('CallbackMetadata', {}).get('Item', [])
                        for item in items:
                            if item.get('Name') == 'MpesaReceiptNumber':
                                transaction.mpesa_receipt_number = item.get('Value')
                                break
                    else:
                        transaction.status = "Failed"
                    
                    transaction.save()
                    logger.info(f"Transaction {checkout_request_id} updated to {transaction.status}")
                except Transaction.DoesNotExist:
                    logger.error(f"Transaction with CheckoutRequestID {checkout_request_id} not found")
            
            return JsonResponse({"ResultCode": 0, "ResultDesc": "Success"})
        except json.JSONDecodeError:
            logger.error("Failed to parse callback JSON")
            return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid JSON"}, status=400)
    return JsonResponse({"ResultCode": 1, "ResultDesc": "Invalid request"}, status=400)

def check_status(request):
    """
    API endpoint to check the status of a transaction.
    
    Used by the frontend to poll for updates on a specific transaction
    (e.g., waiting for the user to enter their PIN).
    """
    checkout_request_id = request.GET.get('checkout_request_id')
    if not checkout_request_id:
        return JsonResponse({"error": "Missing checkout_request_id"}, status=400)
    
    try:
        transaction = Transaction.objects.get(checkout_request_id=checkout_request_id)
        return JsonResponse({
            "status": transaction.status,
            "result_code": transaction.result_code,
            "result_desc": transaction.result_desc,
            "receipt_number": transaction.mpesa_receipt_number
        })
    except Transaction.DoesNotExist:
        return JsonResponse({"error": "Transaction not found"}, status=404)
