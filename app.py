from flask import Flask, request
import telegram
import os
import random 

import telebot 
from telebot import types 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

global bot
global TOKEN

# constantes 
TOKEN = f'{os.environ["BOT_KEY"]}' 
URL = f'{os.environ["HEROKU_LINK"]}' 
QUEST_FILENAME = 'preguntas.txt'
READ_FILE      = 'r' 
PUNTO_COMA     = ';' 

knownUsers = []  # todo: save these in a file, 
userStep = {}  # so they won't reset every time the bot restarts 

preguntas_file = []

bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

commands = {  # command description used in the "help" command 
    'start'       : 'Bienvenido al chatbot', 
    'help'        : 'Esta instrucción informa sobre los comandos de este bot',
    'quiz'        : 'Empezar el test'
} 

pregunta_enunciado = ''
correct_answer = ''

# rutas
@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    m = update.message 
    chat_id = update.message.chat.id 
    msg_id = update.message.message_id 

    # Telegram understands UTF-8, so encode text for unicode compatibility 
    text = update.message.text.encode('utf-8').decode() 
    print("texto :", text) 
    print("todo el mensaje :", m)

    if text: 
        if text == '/start': 
            command_start(m) 
        elif text == '/help': 
            command_help(m)
        elif text == '/quiz': 
            command_quiz(m)
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

def set_enunciado(enunciado):
    global pregunta_enunciado    
    if enunciado != None:
        pregunta_enunciado = enunciado

def set_correct_answer(correct):
    global correct_answer    
    if correct != None:
        correct_answer = correct

def cargar_preguntas(bloque): 
    global preguntas_file 
    if os.path.exists(QUEST_FILENAME): 
        with open(QUEST_FILENAME, READ_FILE) as f: 
            preguntas = f.read().strip().splitlines()[1:] 
            if bloque: 
                preguntas2 = [] 
                for pregunta in preguntas: 
                    if pregunta.split(PUNTO_COMA)[0].lower() == bloque.lower(): 
                        preguntas2.append(pregunta) 
                preguntas_file = preguntas2 
                return preguntas_file 
            else: 
                print('El bloque vacío') 
    else: 
        print('El fichero '+QUEST_FILENAME+' no encontrado.') 
        sys.exit() 

def get_bloque_params(params): 
    bloque = '' 
    bloques = ['b1','b2','b3','b4']
    if params: 
        if params[0].lower() == 'b1': 
            bloque = 'b1' 
        elif params[0].lower() == 'b2': 
            bloque = 'b2' 
        elif params[0].lower() == 'b3': 
            bloque = 'b3' 
        elif params[0].lower() == 'b4': 
            bloque = 'b4' 
    else:
        bloque = random.shuffle(bloques) 
    return bloque

def get_datos_pregunta(preguntas): 
    datos_pregunta = [] 
    filas = [] 
    bloque_fila = '' 
    autor       = '' 
    enunciado   = '' 
    opcion_a    = '' 
    opcion_b    = '' 
    opcion_c    = '' 
    opcion_d    = '' 
    resp_correcta = '' 
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

    datos_pregunta.append(bloque_fila) 
    datos_pregunta.append(autor) 
    datos_pregunta.append(enunciado) 
    datos_pregunta.append(opcion_a) 
    datos_pregunta.append(opcion_b) 
    datos_pregunta.append(opcion_c) 
    datos_pregunta.append(opcion_d) 
    datos_pregunta.append(resp_correcta) 
    
    return datos_pregunta

def gen_markup():
    markup = InlineKeyboardMarkup()
    markup.row_width = 4
    markup.add(InlineKeyboardButton("a", callback_data="a"),
               InlineKeyboardButton("b", callback_data="b"),
               InlineKeyboardButton("c", callback_data="c"),
               InlineKeyboardButton("d", callback_data="d"))
    return markup

# comandos
def command_start(m): 
    cid = m.chat.id 
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet: 
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later 
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command 
        bot.send_message(cid, "Bienvenido.") 
        bot.send_message(cid, "Ahora te conoczco.") 
        command_help(m)  # show the new user the help page 
    else: 
        bot.send_message(cid, "Ya te conozco") 

def command_help(m): 
    print(m) 
    cid = m.chat.id 
    help_text = "Los siguientes comando están disponibles para este bot: \n" 
    for key in commands:  # generate help text out of the commands dictionary defined at the top 
        help_text += "/" + key + ": " 
        help_text += commands[key] + "\n" 
    #return help_text 
    bot.send_message(cid, help_text)  # send the generated help page

def command_quiz(m): 
    print(m) 
    chatId  = m.chat.id 
    msg     = m.text
    reply = '' 
    params = msg.split(' ')[1:] 
    bloque = '' 
    filas = []
    bloqueMio = ''
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
    
    with open(QUEST_FILENAME, 'r') as f: 
        preguntas = f.read().strip().splitlines()[1:]
        if bloque: 
            preguntas2 = [] 
            for pregunta in preguntas: 
                if pregunta.split(';')[0].lower() == bloque.lower(): 
                    preguntas2.append(pregunta)
            preguntas = preguntas2
        random.shuffle(preguntas)
        i=0
        for question in preguntas:
            filas.append(preguntas[i].strip(';'))
            i += 1
        for fila in filas:
            bloqueMio = fila.split(';')[0]
            autor = fila.split(';')[1]
            enunciado = fila.split(';')[2]
            opcion_a = fila.split(';')[3]
            opcion_b = fila.split(';')[4]
            opcion_c = fila.split(';')[5]
            opcion_d = fila.split(';')[6]       
            #resp_correcta = fila.split(';')[7]

        texto = "* %s)* %s \n %s \n %s \n %s \n %s \n\n De *%s*" % (bloqueMio.upper(), enunciado, opcion_a, opcion_b, opcion_c, opcion_d, autor)
        set_enunciado(enunciado)
        set_correct_answer('a')
        bot.send_message(chatId, texto, parse_mode= 'Markdown')
        #bot.send_message(chatId, texto, parse_mode= 'Markdown', reply_markup=gen_markup())
        #bot.send_message(chatId, "Para saber la respuesta correcta puedes escribir el comando /answers.") 
        #bot.send_message(chatId, "Para saber tu puntuación puedes escribir el comando /score.") 
        bot.send_message(chatId, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")


def command_default(m): 
    bot.send_message(m.chat.id, "No te entiendo \"" + m.text + "\"\nPuedes escribir el comando /help para saber qué comando utilizar") 


if __name__ == '__main__':
    app.run(threaded=True)
