import requests

endpoint = 'likes'
data = {'likes': 1}
for i in range(10):
    data = {'likes':i}
    r = requests.post('http://localhost:8000/api/post/{}'.format(endpoint), json=data)

endpoint = 'likes'
r = requests.get('http://localhost:8000/api/get/{}'.format(endpoint))
print(r.text)
