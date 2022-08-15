import ssl
import time
import json
import urllib
import hmac, hashlib
from urllib import response
import requests
from urllib.parse import urlparse, urlencode
from urllib.request import Request, urlopen


class Exmo():

    def __init__(self, API_KEY, API_SECRET):
        self.API_KEY = API_KEY
        self.API_SECRET = bytes(API_SECRET, encoding='utf-8')

    def _sign(self, payload):
        
        payload = urlencode(payload)

        H = hmac.new(key = self.API_SECRET, digestmod=hashlib.sha512)

        H.update(payload.encode('utf-8'))

        sign = H.hexdigest()

        return sign

    def trades(self, base, quote) -> dict:
        '''
        Возвращает список последних сделок по текущей паре

        пример trades('btc', 'usd') -> вернёт список последних сделок по паре BTC/USD
        '''
        url = "https://api.exmo.com/v1.1/trades"

        
        payload = dict(
            pair = f'{base.upper()}_{quote.upper()}'
        )
        
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()
    
    def order_book (self, base, quote, limit = 100) -> dict:
        '''
        Возвращает список текущих ордеров по конкретной паре

        пример order_book('BTC','USD',100) -> вернет книгу ордеров на глубину 100
        '''
        url = "https://api.exmo.com/v1.1/order_book"

        payload = dict(
            pair = f'{base.upper()}_{quote.upper()}',
            limit = f'{str(limit)}'
        )

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()

    def tiker (self) -> dict:
        '''
        Метод возвращает статистику по всем текущим парам
        '''
        url = "https://api.exmo.com/v1.1/ticker"

        payload = {}

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()
    
    def pair_settings(self) -> dict:
        '''
        Возвращает настройки торговых пар
        '''
        url = "https://api.exmo.com/v1.1/pair_settings"

        payload={}

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()

    def currency (self) -> dict:
        '''
        Возвращает список доступных активов на бирже
        '''
        url = "https://api.exmo.com/v1.1/currency"

        payload={}
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()

    def _currency (self) -> dict:
        '''
        Возврат раширенного списка активов
        '''
        url = "https://api.exmo.com/v1.1/currency/list/extended"

        payload={}
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()

    def required_amount (self, base, quote, quantity) -> dict:
        '''
        Вернёт расчет суммы покупки определенного количества валюты для конкретной валютной пары
        '''
        url = "https://api.exmo.com/v1.1/required_amount"

        payload= dict(
            pair = f'{base.upper()}_{quote.upper()}',
            quantity = f'{quantity}'
        )

        headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()

    def candles_history(self, base, quote, resolution, limit) -> dict:
        '''
        Возвращает данные о свечах в данной торговой паре

        варианты resolution : {
            1 = 1 minute,
            5 = 5 minute,
            15 = 15 minute,
            30 = 30 minute,
            45 = 45 minute,
            60 = 60 minute,
            120 = 120 minute,
            180 = 180 minute,
            240 = 240 minute
            1440 = 1 day,
            10080 = 1 week
        }

        limit - количество свечей от текущей
        '''
        
        end = int(time.time())
        start = end - int(resolution)*60*int(limit)

        if resolution == 1440:
            resolution = 'D'
        if resolution == 10080:
            resolution = 'W'
        
        url = f'https://api.exmo.com/v1.1/candles_history?symbol={base.upper()}_{quote.upper()}&resolution={str(resolution)}&from={str(start)}&to={str(end)}'

        payload = {}

        headers = {}
        
        response = requests.request('GET', url, headers=headers, data=payload)

        return response.json()

    def payments_providers_crypto_list(self) -> dict:
        '''
        Возвращает список крипто провайдеров биржи
        '''

        url = "https://api.exmo.com/v1.1/payments/providers/crypto/list"

        payload={}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return response.json()

    def user_info (self) -> dict:

        url = 'https://api.exmo.com/v1.1/user_info'

        payload = dict()

        payload.update(nonce = int(time.time()*1000))


        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Key': self.API_KEY,
            'Sign': self._sign(payload)
        }
        
        response = requests.request('POST', url, headers=headers, data=payload)

        return response.json()

    def order_create(self, base, quote, type, quantity, price = 0) -> dict :
        url = 'https://api.exmo.com/v1.1/order_create'

        payload = dict(
            pair = f'{base.upper()}_{quote.upper()}',
            quantity = f'{quantity}',
            type = f'{type}',
            price = f'{price}'
        )
        payload.update(nonce = int(time.time()*1000))
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Key': self.API_KEY,
            'Sign': self._sign(payload)
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        return response.json()
        
    def open_orders (self) -> dict:

        '''
        Возвращает текущие открытые ордера
        '''    
        url = 'https://api.exmo.com/v1.1/user_open_orders'

        pair:tuple = self.pair_settings().keys()
        pair = ','.join(pair)
        payload = dict (
            pair = pair
        )
        payload.update(nonce = int(time.time()*1000))

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Key': self.API_KEY,
            'Sign': self._sign(payload)
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()

    def cancel_order (self, id) -> dict:
        url = 'https://api.exmo.com/v1.1/order_cancel'

        payload = dict(
            order_id = f'{id}'
        )
        payload.update(nonce = int(time.time()*1000))

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Key': self.API_KEY,
            'Sign': self._sign(payload)
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.json()