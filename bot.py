import hmac
import json
import locale
import logging
import os
import threading
import time
from datetime import datetime, timedelta, timezone

import dotenv
import requests
from bs4 import BeautifulSoup
from cacheout import Cache
from telegram import Bot, Update
from telegram.ext import (
    CallbackContext,
    CommandHandler,
    Filters,
    MessageHandler,
    Updater,
)

dotenv.load_dotenv()

# TG BOT
TG_BOT_WEBHOOK_URL = os.getenv("TG_BOT_WEBHOOK_URL")
TG_BOT_PORT = int(os.getenv("TG_BOT_PORT", default=5000))
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_BOT_DEBUG_GROUP_ID = os.getenv("TG_BOT_DEBUG_GROUP_ID")
TG_NIPPLES_GROUP_ID = os.getenv("TG_NIPPLES_GROUP_ID")
TG_ADMIN_USER_ID = os.getenv("TG_ADMIN_USER_ID")
TG_ALERT_USER_NAME = os.getenv("TG_ALERT_USER_NAME")

# CAKEBNB
CAKEBNB_EMERGENCY_RATE = float(os.getenv("CAKEBNB_EMERGENCY_RATE"))
CAKEBNB_LOW_RATE = float(os.getenv("CAKEBNB_LOW_RATE"))
CAKEBNB_HIGH_RATE = float(os.getenv("CAKEBNB_HIGH_RATE"))

# API AUTH
MOONPAYKEY = os.getenv("MOONPAYKEY")
ETHERSCANKEY = os.getenv("ETHERSCANKEY")
FTX_KEY = os.getenv("FTX_KEY")
FTX_SECRET = os.getenv("FTX_SECRET")

cache = Cache()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def msg_listener(update: Update, context: CallbackContext):
    if update.message:
        msg = update.message
        if msg.text:
            txt = msg.text.strip()
            logger.info(
                f"chat={msg.chat.title}({msg.chat.id}), "
                f"user={msg.from_user.first_name} {msg.from_user.last_name} ({msg.from_user.id}), "
                f"text={txt}"
            )
            if "?gas" == txt.lower():
                msg.reply_text(get_gas())
            elif "啪" in txt or "沒了" in txt:
                msg.reply_sticker(
                    "CAACAgUAAxkBAAEBLAJgd99sMMuqwAfwa9FOzEtglxLn4AAClwIAArjQcVewe5BU0CNqSB8E"
                )
            elif "崩崩" in txt:
                msg.reply_sticker(
                    "CAACAgIAAxkBAAEBLAVgd-FvoMW8F3nVGqx0nOUyxIF-qAACYQQAAonq5QdmC3mfOHu_3h8E"
                )
            elif "梭哈" in txt and "/梭哈" != txt:
                msg.reply_sticker(
                    "CAACAgUAAxkBAAEBLAhgd-Grf4bTcZXHaHLUjOtNZMx3cwACNwQAAhwmkVfJpMRsyVY09B8E"
                )
            elif txt.startswith("?pcs ") and len(txt.split(" ")) == 2:
                msg.reply_text(f"/swap pancake 1 {txt.split(' ')[1]} wbnb busd")
            elif txt.startswith("?uni ") and len(txt.split(" ")) == 2:
                msg.reply_text(f"/swap uni 1 {txt.split(' ')[1]} weth usdt")
            elif txt.startswith("?sushi ") and len(txt.split(" ")) == 2:
                msg.reply_text(f"/swap sushi 1 {txt.split(' ')[1]} weth usdt")
            elif (
                txt.startswith("?pcs ")
                and len(txt.split(" ")) == 3
                and isfloat(txt.split(" ")[1])
            ):
                msg.reply_text(
                    f"/swap pancake {txt.split(' ')[1]} {txt.split(' ')[2]} wbnb busd"
                )
            elif (
                txt.startswith("?uni ")
                and len(txt.split(" ")) == 3
                and isfloat(txt.split(" ")[1])
            ):
                msg.reply_text(
                    f"/swap uni {txt.split(' ')[1]} {txt.split(' ')[2]} weth usdt"
                )
            elif (
                txt.startswith("?sushi ")
                and len(txt.split(" ")) == 3
                and isfloat(txt.split(" ")[1])
            ):
                msg.reply_text(
                    f"/swap sushi {txt.split(' ')[1]} {txt.split(' ')[2]} weth usdt"
                )
            elif (txt.endswith("=?") or txt.endswith("=$?") or txt.endswith("=$")) and (
                "+" in txt or "-" in txt or "*" in txt or "/" in txt or "^" in txt
            ):
                fomula = txt.split("=")[0].strip().replace("^", "**")
                try:
                    if txt.endswith("=$?") or txt.endswith("=$"):
                        locale.setlocale(locale.LC_ALL, "en_US.utf8")
                        result = locale.format("%.2f", eval(fomula), grouping=True)
                        msg.reply_text(f"={result}")
                    else:
                        msg.reply_text(f"={eval(fomula)}")
                except:
                    msg.reply_sticker(
                        "CAACAgUAAxkBAAEBLBFgd_tZGLLQLj5O7kuE-r7chp_LOAAC_wEAAmmSQVVx1ECQ0wcNAh8E"
                    )


@cache.memoize(ttl=10 * 60, typed=True)
def ask_mastercard_rate(update: Update, context: CallbackContext):
    update.message.reply_text(f"USD = {get_usd_rete_from_3rd()[0]} TWD")


@cache.memoize(ttl=10 * 60, typed=True)
def ask_visa_rate(update: Update, context: CallbackContext):
    update.message.reply_text(f"USD = {get_usd_rete_from_3rd()[1]} TWD")


@cache.memoize(ttl=10 * 60, typed=True)
def ask_jcb_rate(update: Update, context: CallbackContext):
    update.message.reply_text(f"USD = {get_usd_rete_from_3rd()[2]} TWD")


@cache.memoize(ttl=10 * 60, typed=True)
def ask_usd_rate(update: Update, context: CallbackContext):
    update.message.reply_text(get_usd_rate())


@cache.memoize(ttl=10 * 60, typed=True)
def ask_usd_rate_esunbank(update: Update, context: CallbackContext):
    update.message.reply_text("玉山買入USD = {get_usd_rate_esunbank()} TWD")


@cache.memoize(ttl=3 * 60, typed=True)
def ask_ace(update: Update, context: CallbackContext):
    price = get_ace_price()
    if price > -1:
        update.message.reply_text(f"Ace\nUSDT = {price} TWD")
    else:
        update.message.reply_text("Ace\n找不到資料(可能死了)")


@cache.memoize(ttl=3 * 60, typed=True)
def ask_bito(update: Update, context: CallbackContext):
    utc_now = datetime.now(timezone.utc)
    # tw_time = (utc_now + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    price = get_bito_price(utc_now)
    if price > -1:
        update.message.reply_text(f"BitoPro\nUSDT = {price} TWD")
    else:
        update.message.reply_text("BitoPro\n找不到資料(可能死了)")


@cache.memoize(ttl=3 * 60, typed=True)
def ask_max(update: Update, context: CallbackContext):
    price = get_max_price()
    if price > -1:
        update.message.reply_text(f"Max\nUSDT = {price} TWD")
    else:
        update.message.reply_text("Max\n找不到資料(可能死了)")


@cache.memoize(ttl=3 * 60, typed=True)
def ask_usdt(update: Update, context: CallbackContext):
    update.message.reply_text(get_usdt())


@cache.memoize(ttl=60 * 60 * 4, typed=True)
def ask_combine(update: Update, context: CallbackContext):
    update.message.reply_text(f"{get_usdt()}\n\n{get_usd_rate()}")


@cache.memoize(ttl=10 * 60, typed=True)
def ask_ust(update: Update, context: CallbackContext):
    update.message.reply_text(f"Mirror Wallet UST = {get_ust()} USD")


@cache.memoize(ttl=1, typed=True)
def ask_cakebnb(update: Update, context: CallbackContext):
    cake, bnb, cakebnb = get_cakebnb(Bot(token=TG_BOT_TOKEN))
    if cake == -1 or bnb == -1:
        update.message.reply_text("=error")
    else:
        update.message.reply_text(f"CAKE/BNB = {cake}/{bnb} = {cakebnb}")


def get_usd_rete_from_3rd():
    r = requests.get("https://www.bestxrate.com/card/mastercard/usd.html")
    soup = BeautifulSoup(r.text, "html.parser")
    masterCardRate = (
        [
            i.text
            for i in soup.select(
                "body > div > div:nth-child(3) > div > div > div.panel-body > div:nth-child(4) > div.col-md-10.col-xs-7 > b"
            )
        ][0]
        .replace("\xa0", "")
        .strip("0")
    )
    visaRate = [i.text for i in soup.select("#comparison_huilv_Visa")][0].strip("0")
    jcbRate = [i.text for i in soup.select("#comparison_huilv_JCB")][0].strip("0")
    return [masterCardRate, visaRate, jcbRate]


def get_usd_rate():
    usd_rate = get_usd_rete_from_3rd()
    esun_usd_rate = get_usd_rate_esunbank()
    return f"USD Rate\n[BUY]\nMastercard: {usd_rate[0]} TWD\nVisa: {usd_rate[1]} TWD\nJCB: {usd_rate[2]} TWD\n[SELL]\n玉山: {esun_usd_rate} TWD"


def get_usd_rate_esunbank():
    try:

        dayStr = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%Y-%m-%d")
        timeStr = (datetime.now(timezone.utc) + timedelta(hours=8)).strftime("%H:%M:%S")
        headers = {
            "Content-Type": "application/json",
            "Referer": "https://www.esunbank.com.tw/bank/personal/deposit/rate/forex/foreign-exchange-rates",
            "Host": "www.esunbank.com.tw",
        }

        r = requests.post(
            "https://www.esunbank.com.tw/bank/Layouts/esunbank/Deposit/DpService.aspx/GetForeignExchageRate",
            headers=headers,
            json={"day": dayStr, "time": timeStr},
        )

        obj = json.loads(r.text)
        if not obj["d"]:
            return -1
        else:
            rates = json.loads(obj["d"])
            # result = rates['Rates'][0]['BBoardRate']
            result = list(filter(lambda x: x["Name"] == "美元", rates["Rates"]))
            if not result:
                return -1
            else:
                return result[0]["BBoardRate"]
    except Exception as e:
        logger.info('except "%s"', e)
        return -1


def get_ace_price():
    try:
        r = requests.get(
            "https://www.ace.io/polarisex/quote/getKline?baseCurrencyId=1&tradeCurrencyId=14&limit=1"
        )
        obj = json.loads(r.text)
        if not obj["attachment"]:
            return -1
        else:
            return float(obj["attachment"][0]["closePrice"])
    except:
        return -1


def get_bito_price(utc_now: datetime):
    try:
        to_time = int(utc_now.timestamp())
        from_time = int((utc_now - timedelta(seconds=1800)).timestamp())
        r = requests.get(
            f"https://api.bitopro.com/v3/trading-history/usdt_twd?resolution=1m&from={from_time}&to={to_time}"
        )
        obj = json.loads(r.text)
        if obj["data"] is None:
            return -1
        else:
            return float(obj["data"][0]["close"])
    except:
        return -1


def get_max_price():
    try:
        headers = {
            "authority": "max.maicoin.com",
            "pragma": "no-cache",
            "cache-control": "no-cache",
            "dnt": "1",
            "upgrade-insecure-requests": "1",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,"
            "*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/86.0.4240.183 Safari/537.36",
            "sec-fetch-site": "none",
            "sec-fetch-mode": "navigate",
            "sec-fetch-user": "?1",
            "sec-fetch-dest": "document",
            "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7",
        }
        r = requests.get(
            "https://max.maicoin.com/trades/usdttwd/recent_trades", headers=headers
        )
        obj = json.loads(r.text)
        if not obj["data"]:
            return -1
        else:
            return float(obj["data"][0]["price"])
    except:
        return -1


def get_usdt():
    utc_now = datetime.now(timezone.utc)
    bito_price = str(get_bito_price(utc_now))
    if bito_price == "-1":
        bito_price = "死了(?)"
    else:
        bito_price = bito_price + " TWD"
    ace_price = str(get_ace_price())
    if ace_price == "-1":
        ace_price = "死了(?)"
    else:
        ace_price = ace_price + " TWD"
    max_price = str(get_max_price())
    if max_price == "-1":
        max_price = "死了(?)"
    else:
        max_price = max_price + " TWD"
    return f"USDT Price\nBitoPro: {bito_price}\nAce: {ace_price}\nMax: {max_price}"


def get_ust():
    r = requests.get(
        f"https://api.moonpay.io/v3/currencies/ask_price?cryptoCurrencies=ust&fiatCurrencies=twd,usd&apiKey={MOONPAYKEY}"
    )
    obj = json.loads(r.text)
    return obj["UST"]["USD"]


@cache.memoize(ttl=3, typed=True)
def get_gas():
    r = requests.get(
        f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCANKEY}",
        headers={
            "host": "etherscan.io",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
        },
    )
    try:
        obj = json.loads(r.text)
        return f"Low: {obj['result']['SafeGasPrice']}\nAvg: {obj['result']['ProposeGasPrice']}\nHigh: {obj['result']['FastGasPrice']}\nfrom etherscan.io"
    except:
        logger.info(r.text)


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def main():
    updater = Updater(TG_BOT_TOKEN)
    dp = updater.dispatcher
    dp.add_error_handler(error)
    dp.add_handler(
        CommandHandler(command="m", callback=ask_mastercard_rate, run_async=True)
    )
    dp.add_handler(
        CommandHandler(command="master", callback=ask_mastercard_rate, run_async=True)
    )
    dp.add_handler(CommandHandler(command="v", callback=ask_visa_rate, run_async=True))
    dp.add_handler(
        CommandHandler(command="visa", callback=ask_visa_rate, run_async=True)
    )
    dp.add_handler(CommandHandler(command="j", callback=ask_jcb_rate, run_async=True))
    dp.add_handler(CommandHandler(command="jcb", callback=ask_jcb_rate, run_async=True))
    dp.add_handler(CommandHandler(command="r", callback=ask_usd_rate, run_async=True))
    dp.add_handler(
        CommandHandler(command="rate", callback=ask_usd_rate, run_async=True)
    )
    dp.add_handler(CommandHandler(command="ace", callback=ask_ace, run_async=True))
    dp.add_handler(CommandHandler(command="bito", callback=ask_bito, run_async=True))
    dp.add_handler(CommandHandler(command="max", callback=ask_max, run_async=True))
    dp.add_handler(CommandHandler(command="u", callback=ask_usdt, run_async=True))
    dp.add_handler(CommandHandler(command="usdt", callback=ask_usdt, run_async=True))
    dp.add_handler(
        CommandHandler(
            command="howdoyouturnthison", callback=ask_combine, run_async=True
        )
    )
    dp.add_handler(CommandHandler(command="ust", callback=ask_ust, run_async=True))
    dp.add_handler(
        CommandHandler(command="esun", callback=ask_usd_rate_esunbank, run_async=True)
    )
    dp.add_handler(
        CommandHandler(command="cakebnb", callback=ask_cakebnb, run_async=True)
    )
    dp.add_handler(
        MessageHandler(filters=Filters.text, callback=msg_listener, run_async=True)
    )

    logger.info(f"Start Webhook, Port={TG_BOT_PORT}")
    updater.start_webhook(
        listen="0.0.0.0",
        port=TG_BOT_PORT,
        url_path=TG_BOT_TOKEN,
        webhook_url=f"{TG_BOT_WEBHOOK_URL}/{TG_BOT_TOKEN}",
    )
    # updater.start_polling()
    updater.idle()


def send_msg(bot: Bot, chat_id: str, text: str):
    bot.send_message(chat_id=chat_id, text=text, timeout=10)


def get_cakebnb(bot: Bot):
    bnb = round(get_ftx_price(bot, "BNB-PERP"), 3)
    cake = round(get_ftx_price(bot, "CAKE-PERP"), 3)
    cakebnb = round(cake / bnb, 4)
    return (cake, bnb, cakebnb)


def get_ftx_price(bot: Bot, name: str):
    try:
        url = f"https://ftx.com/api/markets/{name}"
        ts = int(time.time() * 1000)
        signature_payload = f"{ts}GET{url}".encode()
        signature = hmac.new(
            FTX_SECRET.encode(), signature_payload, "sha256"
        ).hexdigest()
        headers = {"FTX-KEY": FTX_KEY, "FTX-SIGN": signature, "FTX-TS": str(ts)}
        r = requests.get(url=url, headers=headers)
        if r.status_code == 200:
            robj = r.json()
            if robj["success"]:
                return robj["result"]["price"]
            else:
                return -1
        else:
            logger.error(f"[ERROR] get_ftx_price, [{r.status_code}] {r.text}")
            send_msg(
                bot,
                TG_ADMIN_USER_ID,
                f"[ERROR] ask {name} price got ({r.status_code}) {r.text}",
            )
            send_msg(
                bot,
                TG_BOT_DEBUG_GROUP_ID,
                f"[ERROR] ask {name} price got ({r.status_code}) {r.text}",
            )
    except Exception as e:
        logger.error(f"[ERROR] get_ftx_price, {e}")
        send_msg(bot, TG_ADMIN_USER_ID, f"[ERROR] ask {name} price got {e}")
        send_msg(bot, TG_BOT_DEBUG_GROUP_ID, f"[ERROR] ask {name} price got {e}")
        return -1


def loop_alert_cakebnb():
    bot = Bot(token=TG_BOT_TOKEN)
    try:
        while True:
            cake, bnb, cakebnb = get_cakebnb(bot)
            if cake != -1 and bnb != -1:
                msg = f"CAKE/BNB 價格比 {cakebnb} ({cake}/{bnb})"
                if cakebnb <= CAKEBNB_EMERGENCY_RATE:
                    msg = f"{msg}\r\n建議平倉止損"
                elif cakebnb <= CAKEBNB_LOW_RATE:
                    msg = f"{msg}\r\n建議加倉"
                elif cakebnb >= CAKEBNB_HIGH_RATE:
                    msg = f"{msg}\r\n建議平倉獲利"

                if cakebnb <= CAKEBNB_LOW_RATE or cakebnb >= CAKEBNB_HIGH_RATE:
                    send_msg(
                        bot,
                        TG_NIPPLES_GROUP_ID,
                        f"{msg}\r\n{TG_ALERT_USER_NAME}",
                    )
                    send_msg(bot, TG_ADMIN_USER_ID, msg)
                send_msg(bot, TG_BOT_DEBUG_GROUP_ID, msg)
            time.sleep(5)
    except Exception as e:
        logger.error(f"[ERROR] loop_alert_cakebnb, {e}")
        send_msg(bot, TG_ADMIN_USER_ID, f"[ERROR] loop_alert_cakebnb, {e}")


def print_env():
    logger.info(f"TG_BOT_WEBHOOK_URL={TG_BOT_WEBHOOK_URL}")
    logger.info(f"TG_BOT_PORT={TG_BOT_PORT}")
    logger.info(f"TG_BOT_TOKEN={TG_BOT_TOKEN}")
    logger.info(f"TG_BOT_DEBUG_GROUP_ID={TG_BOT_DEBUG_GROUP_ID}")
    logger.info(f"TG_NIPPLES_GROUP_ID={TG_NIPPLES_GROUP_ID}")
    logger.info(f"TG_ADMIN_USER_ID={TG_ADMIN_USER_ID}")
    logger.info(f"TG_ALERT_USER_NAME={TG_ALERT_USER_NAME}")
    logger.info(f"CAKEBNB_EMERGENCY_RATE={CAKEBNB_EMERGENCY_RATE}")
    logger.info(f"CAKEBNB_LOW_RATE={CAKEBNB_LOW_RATE}")
    logger.info(f"CAKEBNB_HIGH_RATE={CAKEBNB_HIGH_RATE}")
    logger.info(f"MOONPAYKEY={MOONPAYKEY}")
    logger.info(f"ETHERSCANKEY={ETHERSCANKEY}")
    logger.info(f"FTX_KEY={FTX_KEY}")
    logger.info(f"FTX_SECRET={FTX_SECRET}")


if __name__ == "__main__":
    print_env()
    t = threading.Thread(target=loop_alert_cakebnb)
    t.start()
    main()
