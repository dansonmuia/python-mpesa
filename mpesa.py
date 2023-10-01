import os
import json
import base64
from datetime import datetime, timedelta

import requests

ACCESS_TOKEN_URL = 'https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
STK_PUSH_URL = 'https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest'

# Get values from env
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_PASS_KEY = os.getenv('MPESA_PASS_KEY')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')


class Mpesa:
    consumer_key = None
    consumer_secret = None
    mpesa_passkey = None
    mpesa_shortcode = None
    basic_token = None
    access_token = None
    access_token_expiry = None  # In seconds
    access_token_generated_at = None

    def __init__(self):
        self.consumer_key = MPESA_CONSUMER_KEY
        self.consumer_secret = MPESA_CONSUMER_SECRET
        self.mpesa_passkey = MPESA_PASS_KEY
        self.mpesa_shortcode = MPESA_SHORTCODE

    def generate_basic_token(self):
        if self.consumer_secret is None or self.consumer_key is None:
            raise ValueError('Consumer key and consumer secret cannot be None')

        to_encode = f'{self.consumer_key}:{self.consumer_secret}'
        self.basic_token = base64.b64encode(to_encode.encode("utf-8")).decode("utf-8")

        return self.basic_token

    def generate_access_token(self):
        basic_token = self.basic_token or self.generate_basic_token()
        print('Generating access token')
        response = requests.get(ACCESS_TOKEN_URL, headers={'Authorization': f'Basic {basic_token}'})
        print('Token generation status code: ', response.status_code)
        if response.status_code != 200:
            print('Unable to generate access token')
            print('Status code: ', response.status_code)
        else:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.access_token_expiry = int(token_data['expires_in'])
            self.access_token_generated_at = datetime.now()
            return self.access_token

    def access_token_is_valid(self):
        valid = False
        if self.access_token_generated_at and self.access_token_expiry:
            now = datetime.now()
            valid = self.access_token_generated_at + timedelta(seconds=(self.access_token_expiry - 10)) > now

        return valid

    def stk_password_timestamp(self):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

        to_encode = f'{self.mpesa_shortcode}{self.mpesa_passkey}{timestamp}'
        password = base64.b64encode(to_encode.encode("utf-8")).decode("utf-8")

        return password, timestamp

    def create_stk_push_payload(self, phone, amount, callback_url):
        password, timestamp = self.stk_password_timestamp()

        stk_payload = {
            "BusinessShortCode": self.mpesa_shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "Amount": amount,
            "PartyA": phone,
            "PartyB": self.mpesa_shortcode,
            "PhoneNumber": phone,
            "CallBackURL": callback_url,
            "TransactionType": "CustomerPayBillOnline",
            "AccountReference": "Payment",
            "TransactionDesc": "Payment online"
        }

        return stk_payload

    def send_stk_push(self, payload):
        print('Sending stk push')
        access_token = self.access_token if self.access_token_is_valid() else self.generate_access_token()
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        response = requests.post(STK_PUSH_URL, data=json.dumps(payload), headers=headers)
        print('Stk push status code: ', response.status_code)
        return response
