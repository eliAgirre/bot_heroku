# imports
from flask import Flask, request
import telegram
import telebot
from telebot import types 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# utilidades
from util.methods import print_command
from util.constantes import TOKEN, URL, KEYBOARD
from util.arrays import datos, correct_answers, wrong_answers
from util.commands import redirect_command, callback_query

# variables globales
global bot
global TOKEN

# config
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# rutas
@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    print("update: ", update)

    m = update.message
    cid = ''
    response = ''
    
    if m == None:
        call = update.callback_query
        if call != None:
            cid = call.message.chat.id
            user_answer = call.data
            print("call: ", call)
            print("data: ", user_answer)
            if user_answer != None:
                response = callback_query(call, user_answer)
                bot.send_message(cid, text=response, parse_mode='Markdown')
        elif call == None:
            print("Callback query None")
    elif m != None:
        cid = m.chat.id
        # Telegram understands UTF-8, so encode text for unicode compatibility 
        text = m.text.encode('utf-8').decode() 
        response = redirect_command(m, text)
        if text: 
            if text == '/quiz': 
                bot.send_message(cid, text=response, parse_mode='Markdown', reply_markup=KEYBOARD)
            elif text == '/stop':
                bot.send_message(cid, text=response, parse_mode='Markdown')
            else:
                bot.sendMessage(cid, text=response)
                
    return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/')
def index():
    return '.'

# main
if __name__ == '__main__':
    app.run(threaded=True)