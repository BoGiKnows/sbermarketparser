import requests
import json


url = 'https://sbermegamarket.ru/catalog/noutbuki/page-1'
find = 'Mobikwik Offer'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'}

response = requests.get(url, headers=headers)
print(response.json())
# data = response['data']
#
# print(data)