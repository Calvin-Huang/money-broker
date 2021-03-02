import json
import logging
import os
import requests
from bs4 import BeautifulSoup
from cacheout import Cache
from datetime import datetime, timedelta, timezone
from telegram import Update
from lxml import html
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext)

APPNAME = os.environ["APPNAME"]
PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ["TOKEN"]
MOONPAYKEY = os.environ["MOONPAYKEY"]
cache = Cache()
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


@cache.memoize(ttl=10 * 60, typed=True)
def ask_mastercard_rate(update: Update, context: CallbackContext):
    update.message.reply_text('USD = {} TWD'.format(get_mastercard_rate_from_3rd()))


@cache.memoize(ttl=10 * 60, typed=True)
def get_mastercard_rate():
    try:
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
        logger.info(r.text)
        obj = json.loads(r.text)
        logger.info(obj['data'])
        logger.info(obj['data']['conversionRate'])
        return obj['data']['conversionRate']
    except:
        return '??'


@cache.memoize(ttl=10 * 60, typed=True)
def ask_visa_rate(update: Update, context: CallbackContext):
    update.message.reply_text('USD = {} TWD'.format(get_visa_rate_from_3rd()))


@cache.memoize(ttl=10 * 60, typed=True)
def get_visa_rate():
    try:
        r = requests.get(
            'https://www.visa.com.tw/travel-with-visa/exchange-rate-calculator.html?fromCurr=TWD&toCurr=USD&fee=0')
        soup = BeautifulSoup(r.text, 'html.parser')
        selector = 'span strong+ strong'
        rate = [i.text for i in soup.select(selector)][0]
        return rate
    except:
        return '??'

@cache.memoize(ttl=10 * 60, typed=True)
def ask_rate(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Mastercard: 1 USD = {} TWD\nVisa: 1 USD = {} TWD'.format(get_mastercard_rate_from_3rd(), get_visa_rate_from_3rd()))


@cache.memoize(ttl=3 * 60, typed=True)
def ask_bito(update: Update, context: CallbackContext):
    utc_now = datetime.now(timezone.utc)
    # tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    price = get_bito_price(utc_now)
    if price > -1:
        update.message.reply_text('BitoPro\nUSDT = {} TWD'.format(price))
    else:
        update.message.reply_text('BitoPro\n找不到資料')


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
    # tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    price = get_ace_price()
    if price > -1:
        update.message.reply_text('Ace\nUSDT = {} TWD'.format(price))
    else:
        update.message.reply_text('Ace\n找不到資料')


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
    # tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    price = get_max_price()
    if price > -1:
        update.message.reply_text('Max\nUSDT = {} TWD'.format(price))
    else:
        update.message.reply_text('Max\n找不到資料')


@cache.memoize(ttl=3 * 60, typed=True)
def get_max_price():
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
    obj = json.loads(r.text)
    if not obj['data']:
        return -1
    else:
        return float(obj['data'][0]['price'])


@cache.memoize(ttl=3 * 60, typed=True)
def ask_usdt(update: Update, context: CallbackContext):
    update.message.reply_text(get_usdt())


@cache.memoize(ttl=3 * 60, typed=True)
def get_usdt():
    utc_now = datetime.now(timezone.utc)
    # tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    bito_price = get_bito_price(utc_now)
    ace_price = get_ace_price()
    max_price = get_max_price()
    return 'USDT Price\nBitoPro: {} TWD\nAce: {} TWD\nMax: {} TWD'.format(bito_price, ace_price, max_price)


@cache.memoize(ttl=60 * 60 * 4, typed=True)
def ask_combine(update: Update, context: CallbackContext):
    update.message.reply_text('{}\n\nUSD Credit Card Rate\nMastercard: {} TWD\nVisa: {} TWD\nJCB: {} TWD'.format(get_usdt(), get_mastercard_rate_from_3rd(), get_visa_rate_from_3rd(), get_jcb_rate_from_3rd()))


def get_ust():
    r = requests.get(
            'https://api.moonpay.io/v3/currencies/ask_price?cryptoCurrencies=ust&fiatCurrencies=twd,usd&apiKey={}'.format(MOONPAYKEY))
    obj = json.loads(r.text)
    return obj['UST']['USD']


def ask_ust(update: Update, context: CallbackContext):
    update.message.reply_text('Mirror Wallet UST = {} USD'.format(get_ust()))


def get_mastercard_rate_from_3rd():
    r = requests.get('https://www.bestxrate.com/card/mastercard/usd.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    logger.info(r.text)
    selector = 'body > div > div:nth-child(3) > div > div > div.panel-body > div:nth-child(4) > div.col-md-10.col-xs-7 > b'
    logger.info(soup.select(selector))
    rate = [i.text for i in soup.select(selector)][0]

    # root = html.fromstring(r.content)
    # logger.info(r.content)
    # logger.info([x for x in root.xpath('//*[@id="table_comparison"]/tbody/tr[1]/td[2]')])    
    # rate = [x for x in root.xpath('//*[@id="table_comparison"]/tbody/tr[1]/td[2]')][0]
    return rate.replace('\xa0','').strip('0')


def get_visa_rate_from_3rd():
    r = requests.get('https://www.bestxrate.com/card/mastercard/usd.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    selector = '#comparison_huilv_Visa'
    rate = [i.text for i in soup.select(selector)][0]
    return rate.strip('0')


@cache.memoize(ttl=10 * 60, typed=True)
def ask_jcb_rate(update: Update, context: CallbackContext):
    update.message.reply_text('USD = {} TWD'.format(get_jcb_rate_from_3rd()))


def get_jcb_rate_from_3rd():
    r = requests.get('https://www.bestxrate.com/card/mastercard/usd.html')
    soup = BeautifulSoup(r.text, 'html.parser')
    selector = '#comparison_huilv_JCB'
    rate = [i.text for i in soup.select(selector)][0]
    return rate.strip('0')


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
    dp.add_handler(CommandHandler('usdt', ask_usdt))
    dp.add_handler(CommandHandler('howdoyouturnthison', ask_combine))
    dp.add_handler(CommandHandler('ust', ask_ust))
    dp.add_handler(CommandHandler('jcb', ask_jcb_rate))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(APPNAME, TOKEN))
    # updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
