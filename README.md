# python-mpesa
Python wrapper for Mpesa's Daraja API

Quickly integrate Mpesa STK push/Mpesa Express into your application logic. Edit mpesa.py to suit your need

### Usage

`from mpesa import Mpesa`

`mpesa = Mpesa()`

`payload = mpesa.create_stk_push_payload(phone, amount, callback_url)`

`response = mpesa.send_stk_push(payload)`

### References

https://developer.safaricom.co.ke/APIs

### Support

Email: apisupport@safaricom.co.ke
