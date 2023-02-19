from flask import Flask, request
from flask import Response
from tokens import cmc_token
import requests
from pprint import pprint
import json
from tokens import telegram_token

# импортируем модуль для работы с ssl (понадобится для сервера)
from flask_sslify import SSLify


import re

app = Flask(__name__)
# тут создадим инстанс sslify и в аргументы положим наш app от flask
sslify = SSLify(app)

# 1. Get crypto prices from CMC API
# 2. Create a Telegram Bot with BotFather
# 3. Create a Flask app and handle requests from Telegram(recieving & sending msg). Test it with a tunnel
# 4. Combine CMC pasrser and the Telegram bot
# 5. Deploy to PythonAnywhere and install Flask-SSlfy


def write_json(data, filename='response.json'):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_cmc_data(crypto):
    url = ' https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest'
    symbol = {'symbol': crypto, 'convert': 'USD'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': cmc_token,
    }
    r = requests.get(url, params=symbol, headers=headers).json()
    price = r['data'][crypto][0]['quote']['USD']['price']

    return price


def parse_message(message):
    chat_id = message['message']['chat']['id']
    txt = message['message']['text']

    pattern = r'/[a-zA-Z]{2,4}'

    ticker = re.findall(pattern, txt)  # [....]

    if ticker:
        symbol = ticker[0][1:].upper()  # /btc -> BTC   .strip('/')
    else:
        symbol = ''

    return chat_id, symbol


def send_message(chat_id, text='bla-bla-bla'):
    url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': text}
    r = requests.post(url, json=payload, headers={})

    return r


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        msg = request.get_json()
        chat_id, symbol = parse_message(msg)

        if not symbol:
            send_message(chat_id, 'wrong data')
            return Response('ok', status=200)

        price = get_cmc_data(symbol)
        send_message(chat_id, price)

        # write_json(msg, 'telegram_request.json')

        return Response('Ok', status=200)
    else:
        return '<h1>CoinMarket Bot</h1>'


def main():
    print(get_cmc_data('BTC'))


if __name__ == '__main__':
    # main()
    app.run(debug=True)
