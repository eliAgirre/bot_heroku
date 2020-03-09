from flask import Flask, request
import telegram
import os
import random

import telebot
from Pregunta import Pregunta
from telebot import types 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# variables globales
global bot
global TOKEN

# constantes 
TOKEN = f'{os.environ["BOT_KEY"]}' 
URL = f'{os.environ["HEROKU_LINK"]}' 
QUEST_FILENAME = 'preguntas.txt'
READ_FILE      = 'r' 
PUNTO_COMA     = ';'
LOG_FILENAME   = 'logs.txt' 
WRITE_FILE     = 'w' 
APPEND_FILE    = 'a' 
OPCION_A = 'a'
OPCION_B = 'b'
OPCION_C = 'c'
OPCION_D = 'd'
OPCIONES = {"inline_keyboard": [[
                {
                    "text": OPCION_A,
                    "callback_data": OPCION_A            
                }, 
                {
                    "text": OPCION_B,
                    "callback_data": OPCION_B            
                },
                                {
                    "text": OPCION_C,
                    "callback_data": OPCION_C            
                },
                                {
                    "text": OPCION_D,
                    "callback_data": OPCION_D            
                }
            ]]
            }


# config
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# lista comandos
commands = {  # command description used in the "help" command 
    'start'       : 'Bienvenido al chatbot', 
    'help'        : 'Esta instrucción informa sobre los comandos de este bot',
    'quiz'        : 'Empezar el test',
    'score'       : 'Se obtiene la puntuación',
    'stop'        : 'Se para el test y te da un resumen de tu puntuación.'
    #,'wiki'        : 'Busca información en la wikipedia.'
} 

# variables
knownUsers = []  # todo: save these in a file, 
userStep = {}  # so they won't reset every time the bot restarts 
correctAnswers = []
wrongAnswers = []
contador = 0
pregunta = Pregunta('','')
res_user = ''

# rutas
@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    print("update: ", update)

    m = update.message
    
    if m == None:
        call = update.callback_query
        if call != None:
            data = call.data
            print("call: ", call)
            print("data: ", data)
            if data != None:
                callback_query(call, data)
        elif call == None:
            print("Callback query None")
    elif m != None:
        print("todo el mensaje: ", m)
        # Telegram understands UTF-8, so encode text for unicode compatibility 
        text = m.text.encode('utf-8').decode() 
        substr  = text[0:5]
        print("texto: ", text)
        #print("substr :", substr) 
        '''
        if substr:
            if substr == '/wiki': 
                command_wiki(m)
        '''
        if text: 
            if text == '/start': 
                command_start(m) 
            elif text == '/help': 
                command_help(m)
            elif text == '/quiz': 
                command_quiz(m)
            elif text == '/score': 
                command_score(m)
            elif text == '/stop': 
                command_stop(m)
            else: 
                command_default(m)

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

# metodos
# error handling if user isn't known yet 
# (obsolete once known users are saved to file, because all users 
#   had to use the /start command and are therefore known to the bot) 
def get_user_step(uid): 
    if uid in userStep: 
        return userStep[uid] 
    else: 
        knownUsers.append(uid) 
        userStep[uid] = 0 
        print("Nuevo usuario detectado que todavía no ha utilizado el comando \"/start\" .") 
        return 0

def print_command(m):
    texto = 'El comando {} ha recibido el dato del chat: {}'.format(m.text, str(m.chat)) 
    save_logs(m, texto)
    print(texto)

def save_logs(m, log): 
    texto = str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text 
    if os.path.exists(LOG_FILENAME): 
        #file = open(LOG_FILENAME, APPEND_FILE) 
        file = open(LOG_FILENAME, WRITE_FILE)
        file.write(texto + '\n') 
        file.write(str(log) + '\n\n') 
        file.close() 
    else: 
        print('El fichero '+LOG_FILENAME+' no existe.') 
        file = open(LOG_FILENAME, WRITE_FILE) 
        file.write(texto + '\n') 
        file.write(str(log) + '\n\n') 
        file.close()

def callback_query(call, user_answer):
    global resp_user
    cid = call.message.chat.id
    if user_answer:
        resp_user = user_answer
        texto = "Tu respuesta ha sido: *"+user_answer+"*.\nPara saber tu puntuación puedes escribir el comando /score."
        if user_answer == OPCION_A:
            bot.send_message(cid, texto, parse_mode="Markdown")
        elif user_answer == OPCION_B:
            bot.send_message(cid, texto, parse_mode="Markdown")
        elif user_answer == OPCION_C:
            bot.send_message(cid, texto, parse_mode="Markdown")
        elif user_answer == OPCION_D:
            bot.send_message(cid, texto, parse_mode="Markdown")
    else:
        bot.send_message(cid, "No has repondido a la pregunta.")

# comandos
def command_start(m):
    print('command_start') 
    print_command(m) 
    cid = m.chat.id 
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet: 
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later 
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command 
        bot.send_message(cid, "Bienvenido.") 
        bot.send_message(cid, "Este es un chat para practicar preguntas sobre la oposición de TAI.\nAprende constestando las preguntas y tienes la opción de ver youtube (@youtube) y de realizar las búsquedas en la wikipedia (@wiki).") 
        command_help(m)  # show the new user the help page 
    else: 
        bot.send_message(cid, "Ya te conozco, eres "+m.chat.first_name+".\nPara ver los comandos puedes escribir /help.") 

def command_help(m): 
    print('command_help') 
    print_command(m) 
    cid = m.chat.id 
    help_text = "Los siguientes comando están disponibles para este bot: \n" 
    for key in commands:  # generate help text out of the commands dictionary defined at the top 
        help_text += "/" + key + ": " 
        help_text += commands[key] + "\n" 
    #return help_text 
    bot.send_message(cid, help_text)  # send the generated help page

def command_quiz(m): 
    print('command_quiz') 
    print_command(m)
    global pregunta
    msg     = m.text
    reply = '' 
    params = msg.split(' ')[1:] 
    bloque = '' 
    filas = []
    bloque_fila = ''
    autor = ''
    enunciado = ''
    opcion_a = ''
    opcion_b = ''
    opcion_c = ''
    opcion_d = ''
    resp_correcta = ''
    if params: 
        if params[0].lower() == 'b1': 
            bloque = 'b1' 
        elif params[0].lower() == 'b2': 
            bloque = 'b2' 
        elif params[0].lower() == 'b3': 
            bloque = 'b3' 
        elif params[0].lower() == 'b4': 
            bloque = 'b4' 
    
    with open(QUEST_FILENAME, READ_FILE) as f: 
        preguntas = f.read().strip().splitlines()[1:]
        if bloque: 
            preguntas2 = [] 
            for pregunta in preguntas: 
                if pregunta.split(PUNTO_COMA)[0].lower() == bloque.lower(): 
                    preguntas2.append(pregunta)
            preguntas = preguntas2
        random.shuffle(preguntas)
        i=0
        for question in preguntas:
            filas.append(preguntas[i].strip(PUNTO_COMA))
            i += 1
        for fila in filas:
            bloque_fila = fila.split(PUNTO_COMA)[0]
            autor       = fila.split(PUNTO_COMA)[1]
            enunciado   = fila.split(PUNTO_COMA)[2]
            opcion_a    = fila.split(PUNTO_COMA)[3]
            opcion_b    = fila.split(PUNTO_COMA)[4]
            opcion_c    = fila.split(PUNTO_COMA)[5]
            opcion_d    = fila.split(PUNTO_COMA)[6]
            resp_correcta = fila.split(PUNTO_COMA)[7] 

        texto = "* %s)* %s \n %s \n %s \n %s \n %s \n\n De *%s*" % (bloque_fila.upper(), enunciado, opcion_a, opcion_b, opcion_c, opcion_d, autor)
        pregunta.enunciado = enunciado
        pregunta.resp_correcta = resp_correcta
        pregunta.print_pregunta()
        bot.send_message(m.chat.id, texto, parse_mode='Markdown', reply_markup=OPCIONES)
        #bot.send_message(m.chat.id, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")

def command_score(m):
    print('command_score') 
    print_command(m)
    global correctAnswers
    global wrongAnswers
    global contador
    global resp_user
    chatId  = m.chat.id 

    print("resp usuario "+resp_user)

    if pregunta:
        pregunta.print_pregunta()

    if pregunta:
        if pregunta.enunciado and resp_user and pregunta.resp_correcta:
            contador += 1
            if resp_user == pregunta.resp_correcta:
                correctAnswers.append(pregunta.enunciado)
            else:
                wrongAnswers.append(pregunta.enunciado)
        else:
            print("Hubo un problema con obtener los datos del enunciado, la respuesta del usuario y la respuesta correcta.")
    else:
        print("Hubo un problema con obtener el objeto pregunta")

    print("resp correctas "+str(len(correctAnswers)))
    print("resp incorrectas "+str(len(wrongAnswers)))

    if pregunta.enunciado and resp_user and pregunta.resp_correcta:
        bot.send_message(chatId, "El enunciado ha sido: "+pregunta.enunciado+"\nTu respuesta ha sido la *"+resp_user+"*.\n*La respuesta correcta es: "+pregunta.resp_correcta+"*", parse_mode='Markdown')
    else:
        bot.send_message(chatId,"Hubo problemas al obtener los datos. Puede escribir el comando /stop y volver a empezar con el comando /quiz.")

    bot.send_message(chatId, "Respuestas *correctas*: "+str(len(correctAnswers))+".\nRespuestas *incorrectas*: "+str(len(wrongAnswers))+".\nPara parar el test puedes escribir el comando /stop.", parse_mode= 'Markdown')
    resp_user = ''
    command_quiz(m)

def command_stop(m):
    print('command_stop') 
    print_command(m)
    global contador
    global correctAnswers
    global wrongAnswers
    if contador:
        bot.send_message(m.chat.id, "De las *"+str(contador)+"* preguntas.\nRespuestas *correctas* : "+str(len(correctAnswers))+".\nRespuestas *incorrectas*: "+str(len(wrongAnswers))+".", parse_mode= 'Markdown')
        contador = 0
        correctAnswers = []
        wrongAnswers = []
        bot.send_message(m.chat.id, "Para empezar hacer el test puedes escribir el comando /quiz.")
        #bot.send_message(m.chat.id, "Para realizar el test de algún puedes escribir el comando /b1 o /b2 o /b3 o /b4.")
    else:
        bot.send_message(m.chat.id, "No hay puntuación, ya que no has respondido al test.\nPara empezar hacer el test puedes escribir el comando /quiz y después hacer clic en alguna de las opciones correspondientes.")

def command_wiki(m):
    print('command_wiki') 
    print_command(m)
    msg     = m.text
    params  = msg[6:]
    if params:
        lang = 'es'
        paramlang = params[0].lower().split(':')[0]
        search = ''.join(params)
        search = search.lstrip('%s:' % paramlang)
        if paramlang in ['en', 'fr', 'de', 'pt']:
            lang = paramlang
        reply = "https://%s.wikipedia.org/wiki/%s" % (lang, params)
        bot.send_message(m.chat.id, reply, parse_mode='HTML')

def command_default(m):
    print('command_default') 
    print_command(m) 
    msg     = m.text
    #substr  = msg[0:5]
    #print(substr)
    #if m.text != None and substr != '/wiki':
        #commando_wiki(m)
    #else:
    bot.send_message(m.chat.id, "No te entiendo \"" + msg + "\"\nPuedes escribir el comando /help para saber qué comando utilizar") 

if __name__ == '__main__':
    app.run(threaded=True)
