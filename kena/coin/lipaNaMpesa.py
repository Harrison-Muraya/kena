import os
import requests

def format_phone_number(phone_number):
    """Convert phone number to 254 format."""
    if phone_number.startswith('0'):
        # Replace leading 0 with 254 (Kenya's country code)
        return '254' + phone_number[1:]
    elif phone_number.startswith('+'):
        # Remove the + sign if present
        return phone_number[1:]
    return phone_number


def getAccessToken():
    consumer_key = os.getenv('MPESA_CONSUMER_KEY')
    consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
    api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    response = requests.get(api_url, auth=(consumer_key, consumer_secret))
    token = response.json().get("access_token")
    
    return token

def lipaNaMpesaOnline(phone_number, amount, account_reference, transaction_desc):
    phone_number = format_phone_number(phone_number)  # Ensure correct phone format
    access_token = getAccessToken()
    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "BusinessShortCode": os.getenv('MPESA_SHORTCODE'),
        "Password": os.getenv('MPESA_PASSWORD'),
        "Timestamp": "20241003010101",
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # Use formatted phone number
        "PartyB": os.getenv('MPESA_SHORTCODE'),
        "PhoneNumber": phone_number,  # Use formatted phone number
        "CallBackURL": "https://yourdomain.com/payments/callback/",
        "AccountReference": "Buy Kena",
        "TransactionDesc": "Kena paymants"    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()





# import requests

# url = "https://api.safaricom.co.ke/YOUR_ENDPOINT"
# payload = {
#   "Password": "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMjUxMjA1MDAwNjM4",
#   "BusinessShortCode": "174379",
#   "Timestamp": "20251205000638",
#   "Amount": "1",
#   "PartyA": "254708374149",
#   "PartyB": "174379",
#   "TransactionType": "CustomerPayBillOnline",
#   "PhoneNumber": "254726688832",
#   "TransactionDesc": "Test",
#   "AccountReference": "Test",
#   "CallBackURL": "https://mydomain.com/mpesa-express-simulate/"
# }

# headers = {
#     "Content-Type": "application/json",
#     "Authorization": "Bearer <ACCESS_TOKEN>"
# }

# response = requests.post(url, json=payload, headers=headers)
# print(response.json())
