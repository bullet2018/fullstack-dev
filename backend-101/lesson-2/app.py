import requests
response = requests.get('https://google.com')
print (f"Status code: {response.status_code}")