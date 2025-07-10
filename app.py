import requests

for i in range(100):
    r = requests.get('http://pengumuman.undip.ac.id')
    print(r)