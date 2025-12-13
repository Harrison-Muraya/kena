import requests
from django.shortcuts import render, redirect
import os

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.getenv('PAYPAL_MODE')  # Use 'live' for production


# PayPal API URLs
if PAYPAL_MODE == 'sandbox':
    PAYPAL_API_BASE = 'https://api-m.sandbox.paypal.com'
else:
    PAYPAL_API_BASE = 'https://api-m.paypal.com'


def get_paypal_access_token():
    '''Get PayPal OAuth access token'''
    url = f'{PAYPAL_API_BASE}/v1/oauth2/token'
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US'
    }
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    )
    
    return response.json()['access_token']


