import requests
import json

resp = requests.post('http://127.0.0.1:8000/pools/', json={'x_init':1000, 'y_init':2000})
print('status', resp.status_code)
print(resp.text)
