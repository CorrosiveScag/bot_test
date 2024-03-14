import telebot
from telebot import types
import csv
from datetime import datetime, timedelta

DATA_FILENAME = "data.csv"

TOKEN = ""
bot = telebot.TeleBot(TOKEN)

rub = None
usd = None

nums = {
    "balance_bank": 0,
    "balance_bybit": 0,
    "balance_exnode": 0,
    "balance_cc": 0,
    "balance_aifory": 0,
    "balance_payscrow": 0,
    "losses": 0
}

def sum_rub():
    return nums["balance_bank"]+nums["balance_cc"]+nums["balance_aifory"]+nums["balance_payscrow"]
def sum_usd():
    return nums["balance_bybit"]+nums["balance_exnode"]

@bot.message_handler(commands=['start'])
def handle_start(message):
    markup = types.ReplyKeyboardMarkup()
    btn1 = types.KeyboardButton("Расчёт")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Введите значения для bank, bybit, exnode, cc, aifory, payscrow:", reply_markup=markup)
    bot.register_next_step_handler(message, text_handler)

def on_click(message, bal):
    if message.text=="Расчёт":
        rub = sum_rub()
        us = sum_usd()
        bot.send_message(message.chat.id, f'Общий баланс в рублях: {rub}\n Общий баланс в USDT: {us}\n Всего вложений за 24 часа\n {bal}')

@bot.message_handler(commands=[comm for comm in nums.keys()])
def handle_input_nums(message):
    try:
        command = message.text[1:]
        print(command)
        bot.send_message(message.chat.id, "Введите число")
        @bot.message_handler(content_types=['text'])
        def message_input_step(message):
            nums[command] = int(message.text)
            bot.reply_to(message, f'{command}, {int(message.text)}, {nums[command]}')
        bot.register_next_step_handler(message, message_input_step)
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите число.")
    
@bot.message_handler(content_types=['text'])
def text_handler(message):
    if message.text == "Расчёт":
        time = datetime.fromtimestamp(message.date)
        bal = timer(time)
        on_click(message, bal)
        writing(time)
    else:
        bot.reply_to(message, "!!")

def timer(current_date):
    with open('data.csv', 'r') as file:
        num_lines = len(file.readlines()) - 1
        file.seek(0)
        
        start_date = current_date - timedelta(hours=24)
        total_balance_rub = 0
        total_balance_us = 0

        for line in csv.DictReader(file):
            date = datetime.strptime(line["Date"] + " " + line["Time"], '%Y-%m-%d %H:%M:%S')
            if date >= start_date:
                total_balance_rub += int(line["Total_Balance_Bank"]) + int(line["CC"]) + int(line["Aifory"]) + int(line["PayScrow"]) - int(line["Losses"])
                total_balance_us += int(line["ByBit_USDT"]) + int(line["Exnode_USDT"])
        
        return f'RUB: {total_balance_rub}, USDT: {total_balance_us}'

def writing(time):
    date, time = str(time).split()
    data = {"Date": date, "Time": time, 
         "Total_Balance_Bank": nums["balance_bank"], 
         "ByBit_USDT": nums["balance_bybit"], 
         "Exnode_USDT": nums["balance_exnode"], 
         "CC": nums["balance_cc"], 
         "Aifory": nums["balance_aifory"], 
         "PayScrow": nums["balance_payscrow"], 
         "Losses": nums["losses"]}
    
    with open("data.csv", "a", newline="") as file:
        fieldnames = ["Date", "Time", "Total_Balance_Bank", "ByBit_USDT", "Exnode_USDT", "CC", "Aifory", "PayScrow", "Losses"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:
            writer.writeheader()

        writer.writerow(data)

    
bot.polling()