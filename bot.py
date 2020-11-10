import json
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext)

TOKEN = 'YOUR TOKEN HERE'


def mastercardRate(update: Update, context: CallbackContext):
    update.message.reply_text('1 USD = {} TWD'.format(getMastercardRate()))


def getMastercardRate():
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


def visaRate(update: Update, context: CallbackContext):
    update.message.reply_text('1 USD = {} TWD'.format(getVisaRate()))


def getVisaRate():
    r = requests.get('https://www.visa.com.tw/travel-with-visa/exchange-rate-calculator.html?fromCurr=TWD&toCurr=USD&fee=0')
    soup = BeautifulSoup(r.text, 'html.parser')
    selector = 'span strong+ strong'
    rate = [i.text for i in soup.select(selector)][0]
    return rate


def rate(update: Update, context: CallbackContext):
    update.message.reply_text('Mastercard: 1 USD = {} TWD\nVisa: 1 USD = {} TWD'.format(getMastercardRate(), getVisaRate()))


updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('m', mastercardRate))
updater.dispatcher.add_handler(CommandHandler('master', mastercardRate))
updater.dispatcher.add_handler(CommandHandler('v', visaRate))
updater.dispatcher.add_handler(CommandHandler('visa', visaRate))
updater.dispatcher.add_handler(CommandHandler('r', rate))
updater.dispatcher.add_handler(CommandHandler('rate', rate))
updater.start_polling()
updater.idle()