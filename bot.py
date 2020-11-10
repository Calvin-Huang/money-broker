import json
import logging
import os
import requests
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
def get_mastercard_rate(update: Update, context: CallbackContext):
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
def get_visa_rate(update: Update, context: CallbackContext):
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
def get_rate(update: Update, context: CallbackContext):
    update.message.reply_text(
        'Mastercard: 1 USD = {} TWD\nVisa: 1 USD = {} TWD'.format(get_mastercard_rate(), get_visa_rate()))


def main():
    logger.info('Token = {}'.format(TOKEN))
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_error_handler(error)
    dp.add_handler(CommandHandler('m', get_mastercard_rate))
    dp.add_handler(CommandHandler('master', get_mastercard_rate))
    dp.add_handler(CommandHandler('v', get_visa_rate))
    dp.add_handler(CommandHandler('visa', get_visa_rate))
    dp.add_handler(CommandHandler('r', get_rate))
    dp.add_handler(CommandHandler('rate', get_rate))
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=TOKEN)
    updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(APPNAME, TOKEN))
    # updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
