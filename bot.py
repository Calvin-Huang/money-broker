import json
import logging
import os
import requests
from datetime import datetime, timedelta, timezone
from cacheout import Cache
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext)

APPNAME = os.environ["APPNAME"]
PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ["TOKEN"]
cache = Cache()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


@cache.memoize(ttl=10 * 60, typed=True)
def ask_mastercard_rate(update: Update, context: CallbackContext):
    update.message.reply_text('1 USD = {} TWD'.format(get_mastercard_rate()))


@cache.memoize(ttl=10 * 60, typed=True)
def get_mastercard_rate():
    headers = {'authority': 'www.mastercard.us',
               'pragma': 'no-cache',
               'cache-control': 'no-cache',
               'accept': 'application/json, text/plain, */*',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/86.0.4240.183 Safari/537.36',
               'sec-fetch-site': 'same-origin',
               'sec-fetch-mode': 'cors',
               'sec-fetch-dest': 'empty',
               'referer': 'https://www.mastercard.us/en-us/personal/get-support/convert-currency.html',
               'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7'}
    r = requests.get('https://www.mastercard.us/settlement/currencyrate/fxDate=0000-00-00;transCurr=USD;'
                     'crdhldBillCurr=TWD;bankFee=0;transAmt=1/conversion-rate',
                     headers=headers)
    obj = json.loads(r.text)
    return obj['data']['conversionRate']


@cache.memoize(ttl=10 * 60, typed=True)
def ask_visa_rate(update: Update, context: CallbackContext):
    update.message.reply_text('1 USD = {} TWD'.format(get_visa_rate()))


@cache.memoize(ttl=10 * 60, typed=True)
def get_visa_rate():
    r = requests.get(
        'https://www.visa.com.tw/travel-with-visa/exchange-rate-calculator.html?fromCurr=TWD&toCurr=USD&fee=0')
    soup = BeautifulSoup(r.text, 'html.parser')
    selector = 'span strong+ strong'
    rate = [i.text for i in soup.select(selector)][0]
    return rate


@cache.memoize(ttl=10 * 60, typed=True)
def ask_rate(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Mastercard: 1 USD = {} TWD\nVisa: 1 USD = {} TWD'.format(get_mastercard_rate(), get_visa_rate()))


@cache.memoize(ttl=3 * 60, typed=True)
def ask_bito(update: Update, context: CallbackContext):
    utc_now = datetime.now(timezone.utc)
    tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    price = get_bito_price(utc_now)
    if price > -1:
        update.message.reply_text('BitoPro {}\nUSDT = {} TWD'.format(tw_time, price))
    else:
        update.message.reply_text('BitoPro {}\n找不到資料'.format(tw_time))


@cache.memoize(ttl=3 * 60, typed=True)
def get_bito_price(utc_now: datetime):
    to_time = int(utc_now.timestamp())
    from_time = int((utc_now - timedelta(seconds=1800)).timestamp())
    r = requests.get(
        'https://api.bitopro.com/v3/trading-history/usdt_twd?resolution=1m&from={}&to={}'.format(from_time, to_time))
    obj = json.loads(r.text)
    if obj['data'] is None:
        return -1
    else:
        return float(obj['data'][0]['close'])


@cache.memoize(ttl=3 * 60, typed=True)
def ask_ace(update: Update, context: CallbackContext):
    utc_now = datetime.now(timezone.utc)
    tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    price = get_ace_price()
    if price > -1:
        update.message.reply_text('Ace {}\nUSDT = {} TWD'.format(tw_time, price))
    else:
        update.message.reply_text('Ace {}\n找不到資料'.format(tw_time, price))


@cache.memoize(ttl=3 * 60, typed=True)
def get_ace_price():
    r = requests.get(
        'https://www.ace.io/polarisex/quote/getKline?baseCurrencyId=1&tradeCurrencyId=14&limit=1')
    obj = json.loads(r.text)
    if not obj['attachment']:
        return -1
    else:
        return float(obj['attachment'][0]['closePrice'])


@cache.memoize(ttl=3 * 60, typed=True)
def ask_max(update: Update, context: CallbackContext):
    utc_now = datetime.now(timezone.utc)
    tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    price = get_max_price()
    if price > -1:
        update.message.reply_text('Max {}\nUSDT = {} TWD'.format(tw_time, price))
    else:
        update.message.reply_text('Max {}\n找不到資料'.format(tw_time, price))


@cache.memoize(ttl=3 * 60, typed=True)
def get_max_price():
    logger.info('get max price')
    headers = {'authority': 'max.maicoin.com',
               'pragma': 'no-cache',
               'cache-control': 'no-cache',
               'dnt': '1',
               'upgrade-insecure-requests': '1',
               'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                         '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/86.0.4240.183 Safari/537.36',
               'sec-fetch-site': 'none',
               'sec-fetch-mode': 'navigate',
               'sec-fetch-user': '?1',
               'sec-fetch-dest': 'document',
               'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7'}
    r = requests.get(
        'https://max.maicoin.com/trades/usdttwd/recent_trades',
        headers=headers)
    logger.info('get body:{}'.format(r.text))
    obj = json.loads(r.text)
    logger.info(obj)
    if not obj['data']:
        return -1
    else:
        return float(obj['data'][0]['price'])


@cache.memoize(ttl=3 * 60, typed=True)
def ask_usdt(update: Update, context: CallbackContext):
    utc_now = datetime.now(timezone.utc)
    logger.info(utc_now)
    tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    logger.info(tw_time)
    bito_price = get_bito_price(utc_now)
    logger.info(bito_price)
    ace_price = get_ace_price()
    logger.info(ace_price)
    max_price = get_max_price()
    logger.info(max_price)
    update.message.reply_text('USDT Price {}\nBitoPro: {} TWD\nAce: {} TWD\nMax: {} TWD'
                              .format(tw_time, bito_price, ace_price, max_price))


def main():
    logger.info('Token = {}'.format(TOKEN))
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_error_handler(error)
    dp.add_handler(CommandHandler('m', ask_mastercard_rate))
    dp.add_handler(CommandHandler('master', ask_mastercard_rate))
    dp.add_handler(CommandHandler('v', ask_visa_rate))
    dp.add_handler(CommandHandler('visa', ask_visa_rate))
    dp.add_handler(CommandHandler('r', ask_rate))
    dp.add_handler(CommandHandler('rate', ask_rate))
    dp.add_handler(CommandHandler('bito', ask_bito))
    dp.add_handler(CommandHandler('ace', ask_ace))
    dp.add_handler(CommandHandler('max', ask_max))
    dp.add_handler(CommandHandler('u', ask_usdt))
    dp.add_handler(CommandHandler('ust', ask_usdt))
    dp.add_handler(CommandHandler('usdt', ask_usdt))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(APPNAME, TOKEN))
    # updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
