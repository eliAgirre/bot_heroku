from flask import Flask, request
import telegram
import os
import random

import telebot
from telebot import types 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# variables globales
global bot
global TOKEN
global datos
global correct_answers
global wrong_answers

# constantes 
TOKEN = f'{os.environ["BOT_KEY"]}' 
URL = f'{os.environ["HEROKU_LINK"]}' 
QUEST_FILENAME = 'preguntas.txt'
READ_FILE      = 'r' 
PUNTO_COMA     = ';'
DOS_PUNTOS     = ':'
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
    ,'wiki'        : 'Busca información en la wikipedia.'
}

# variables
knownUsers = []  # todo: save these in a file, 
userStep = {}  # so they won't reset every time the bot restarts
contador = 0
datos = []
correct_answers = []
wrong_answers   = []

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
        print("substr :", substr) 
        
        if substr:
            if substr == '/wiki': 
                command_wiki(m)
        
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
    print("print_command")
    texto = 'El comando {} ha recibido el dato del chat: {}'.format(m.text, str(m.chat)) 
    save_logs(m, texto)
    print(texto)

def save_logs(m, log): 
    print("save_logs")
    texto = str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text 
    if os.path.exists(LOG_FILENAME): 
        file = open(LOG_FILENAME, APPEND_FILE) 
        #file = open(LOG_FILENAME, WRITE_FILE)
        file.write(texto + '\n') 
        file.write(str(log) + '\n\n')
        file.close() 

        #open and read the file after the appending:
        f = open(LOG_FILENAME, READ_FILE)
        print(f.read())
    else: 
        print('El fichero '+LOG_FILENAME+' no existe.') 
        file = open(LOG_FILENAME, WRITE_FILE) 
        file.write(texto + '\n') 
        file.write(str(log) + '\n\n') 
        file.close()

def callback_query(call, user_answer):
    global user
    global answer
    cid = call.message.chat.id
    if user_answer:
        #texto = "Tu respuesta ha sido: *"+user_answer+"*.\nPara saber tu puntuación puedes escribir el comando /score."
        if user_answer == OPCION_A:
            command_score(cid, user_answer)
        elif user_answer == OPCION_B:
            command_score(cid, user_answer)
        elif user_answer == OPCION_C:
            command_score(cid, user_answer)
        elif user_answer == OPCION_D:
            command_score(cid, user_answer)
            #bot.send_message(cid, texto, parse_mode="Markdown")
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
    bot.send_message(cid, help_text)  # send the generated help page

def command_quiz(m): 
    print('command_quiz') 
    print_command(m)
    global pregunta
    global datos
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
    if datos:
        print("array de datos antes de introducir: "+datos)

    datos.insert(0, enunciado)
    datos.insert(1, resp_correcta)
    if datos:
        print("array de datos después de introducir: "+datos[0]+" y "+datos[1])
    bot.send_message(m.chat.id, texto, parse_mode='Markdown', reply_markup=OPCIONES)
    #bot.send_message(m.chat.id, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")

def command_score(cid, user_answer):
    print('command_score') 
    #print_command(m)
    global correct_answers
    global wrong_answers
    global datos
    global contador
    enunciado = ''
    resp_correct = ''

    if datos:
        print("array de datos en commando score: "+datos[0]+" y "+datos[1])
    
    try:
        if datos:
            enunciado = datos[0]
            resp_correct = datos[1]
    except NameError:
        print("NameError Exception. El objeto datos está vacío.")

    print("enunciado: "+enunciado)
    print("resp correcta: "+resp_correct)
    print("rep usuario: "+user_answer)

    if enunciado and resp_correct and user_answer:
        contador += 1
        if user_answer == resp_correct: 
            correct_answers.append(enunciado) 
        elif user_answer != resp_correct: 
            wrong_answers.append(enunciado)
    else:
        print("Hubo un problema con obtener los datos del enunciado, la respuesta del usuario y la respuesta correcta.")

    print("resp correctas "+str(len(correct_answers)))
    print("resp incorrectas "+str(len(wrong_answers)))

    if enunciado and resp_correct and user_answer:
        bot.send_message(cid, "El enunciado ha sido: "+enunciado+"\nTu respuesta ha sido la *"+user_answer+"*.\n*La respuesta correcta es: "+resp_correct+"*", parse_mode='Markdown')
    else:
        bot.send_message(cid,"Hubo problemas al obtener los datos. Puede escribir el comando /stop y volver a empezar con el comando /quiz.")

    bot.send_message(cid, "Respuestas *correctas*: "+str(len(correct_answers))+".\nRespuestas *incorrectas*: "+str(len(wrong_answers))+".\nPara parar el test puedes escribir el comando /stop.", parse_mode= 'Markdown')
    
    if datos:
        print("array de datos antes de limpiar: "+datos[0]+" y "+datos[1])

    datos = []

    if datos:
        print("array de datos después de limpiar: "+datos)
    bot.send_message(cid, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")
    #command_quiz(m)

def command_stop(m):
    print('command_stop') 
    print_command(m)
    global contador
    global correct_answers
    global wrong_answers
    if contador and correct_answers and wrong_answers:
        bot.send_message(m.chat.id, "De las *"+str(contador)+"* preguntas.\nRespuestas *correctas* : "+str(len(correct_answers))+".\nRespuestas *incorrectas*: "+str(len(wrong_answers))+".", parse_mode= 'Markdown')
        contador = 0
        correct_answers = []
        wrong_answers = []
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
        paramlang = params[0].lower().split(DOS_PUNTOS)[0]
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
    substr  = msg[0:5]
    print(substr)
    if m.text != None and substr == '/wiki':
        if substr == '/wiki':
            command_wiki(m)
    else:
        bot.send_message(m.chat.id, "No te entiendo \"" + msg + "\"\nPuedes escribir el comando /help para saber qué comando utilizar") 

if __name__ == '__main__':
    app.run(threaded=True)
