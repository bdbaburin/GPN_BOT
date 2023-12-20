import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime, timedelta
import requests
import json
import telegram
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, Updater
from mpl_finance import candlestick_ohlc
import matplotlib.dates as mdates

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на ваш токен Telegram бота
TOKEN = 'YOUR TOKEN'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Добро пожаловать в RateRadar! Я бот для отслеживания курсов валют. Используй /exchange <валюта1> <валюта2>, чтобы получить обменный курс. Например, /exchange USD RUB\n /candlestick для построения свечного графика')

def exchange(update: Update, context: CallbackContext) -> None:
    try:
        base_currency = context.args[0].upper()
        target_currency = context.args[1].upper()

        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{base_currency}')
        data = response.json()

        if target_currency in data['rates']:
            exchange_rate = data['rates'][target_currency]
            update.message.reply_text(f'Обменный курс {base_currency} к {target_currency}: {exchange_rate}')

            # Получаем данные о курсе за последние 24 часа
            end_date = datetime.now()
            start_date = end_date - timedelta(days=1)
            currency_data = yf.download(f'{base_currency}{target_currency}=X', start=start_date, end=end_date)

            # Строим график изменения курса за последние 24 часа
            plt.plot(currency_data.index, currency_data['Close'])
            plt.title(f'Изменение обменного курса {base_currency}/{target_currency} за последние 24 часа')
            plt.xlabel('Дата')
            plt.ylabel('Курс')
            plt.savefig('exchange_rate.png')

            # Отправляем график пользователю
            update.message.reply_photo(photo=open('exchange_rate.png', 'rb'))
            update.message.reply_text('Используйте /candlestick для отображения свечного графика')
        else:
            update.message.reply_text(f'Не удалось найти обменный курс для {target_currency}')
    except IndexError:
        update.message.reply_text('Используйте команду в формате /exchange <валюта1> <валюта2>')


def candlestick(update: Update, context: CallbackContext) -> None:

    base_currency = context.args[0].upper()
    target_currency = context.args[1].upper()

    ticker = f"{base_currency}{target_currency}=X"  # Замените на нужный вам тикер
    end_date = datetime.now()

    start_date = end_date - timedelta(hours=12)

    data = yf.download(ticker, start=start_date, end=end_date, interval="1h")
    
    data['Date'] = mdates.date2num(data.index.to_pydatetime())
    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots()
    candlestick_ohlc(ax, data[['Date', 'Open', 'High', 'Low', 'Close']].values, width=0.03, colorup='g', colordown='r')

    ax.xaxis_date()
    ax.set_title(f'Candlestick Chart for {ticker[:-2]}')
    ax.set_xlabel('Date')
    # ax.set_xticks(rotation=90)
    ax.set_ylabel('Price')
    
    # Formatting Date 
    date_format = mdates.DateFormatter('%d-%m-%Y') 
    ax.xaxis.set_major_formatter(date_format) 
    fig.autofmt_xdate() 
    
    fig.tight_layout() 

    plt.savefig('candlestick_chart.png')
    update.message.reply_photo(photo=open('candlestick_chart.png', 'rb'))



def main() -> None:
    bot = telegram.Bot(token=TOKEN)
    updater = Updater(bot=bot, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("exchange", exchange))
    dispatcher.add_handler(CommandHandler("candlestick", candlestick))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()