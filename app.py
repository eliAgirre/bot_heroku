from flask import Flask, request
import telegram
import os
import random

import telebot
from Question import Question

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

# config
bot = telegram.Bot(token=TOKEN)
app = Flask(__name__)

# lista comandos
commands = {  # command description used in the "help" command 
    'start'       : 'Bienvenido al chatbot', 
    'help'        : 'Esta instrucción informa sobre los comandos de este bot',
    'quiz'        : 'Empezar el test',
    'stop'        : 'Se para el test y te da un resumen de tu puntuación.',
    'wiki'        : 'Busca información en la wikipedia.'
} 

# variables globales
knownUsers = []  # todo: save these in a file, 
userStep = {}  # so they won't reset every time the bot restarts 
preguntas_file = []
correctAnswers = []
wrongAnswers = []
questions = []
contador = 0
cont = 0

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
    substr  = text[0:5]
    print("texto :", text) 
    #print("substr :", substr) 
    print("todo el mensaje :", m)

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

# comandos
def command_start(m):
    print_command(m) 
    cid = m.chat.id 
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet: 
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later 
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command 
        bot.send_message(cid, "Bienvenido.") 
        bot.send_message(cid, "Ahora te conozco.") 
        command_help(m)  # show the new user the help page 
    else: 
        bot.send_message(cid, "Ya te conozco") 

def command_help(m): 
    print_command(m) 
    cid = m.chat.id 
    help_text = "Los siguientes comando están disponibles para este bot: \n" 
    for key in commands:  # generate help text out of the commands dictionary defined at the top 
        help_text += "/" + key + ": " 
        help_text += commands[key] + "\n" 
    #return help_text 
    bot.send_message(cid, help_text)  # send the generated help page

def command_quiz(m): 
    print_command(m)
    global questions
    markup = ''
    chatId  = m.chat.id 
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
        questions = [Question(enunciado, resp_correcta)]
        bot.send_message(chatId, texto, parse_mode='Markdown')
        #bot.send_message(chatId, texto, parse_mode= 'Markdown', reply_markup=reply_markup)
        #bot.edit_message_text(chat_id=chatId, message_id=msg, text=texto, reply_markup=reply_markup)
        bot.send_message(chatId, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")

def command_score(m, user_answer):
    print_command(m)
    global correctAnswers
    global wrongAnswers
    global contador
    global questions

    enunciado  = questions[0].enunciado
    resp_correcta  = questions[0].resp_correcta

    print("resp usuario "+user_answer)
    print("enunciado "+enunciado)
    print("resp correcta "+resp_correcta)

    if enunciado and user_answer and resp_correcta:
        contador += 1
        if user_answer == resp_correcta:
            correctAnswers.append(enunciado)
        else:
            wrongAnswers.append(enunciado)
    else:
        print("Hubo un problema con obtener los datos del enunciado, la respuesta del usuario y la respuesta correcta.")

    print("resp correctas "+str(len(correctAnswers)))
    print("resp incorrectas "+str(len(wrongAnswers)))

    if enunciado and user_answer and resp_correcta:
        bot.send_message(m.chat.id, "El enunciado ha sido: "+enunciado+"\n")
        bot.send_message(m.chat.id, "Tu respuesta ha sido la *"+user_answer+"*.\n*La respuesta correcta es: "+resp_correcta+"*", parse_mode= 'Markdown')
    else:
        bot.send_message(m.chat.id,"Hubo problemas al obtener los datos. Puede escribir el comando /stop y volver a empezar con el comando /quiz.")

    bot.send_message(m.chat.id, "Respuestas *correctas*: "+str(len(correctAnswers))+".\nRespuestas *incorrectas*: "+str(len(wrongAnswers))+".", parse_mode= 'Markdown')
    bot.send_message(m.chat.id, "Para parar el test puedes escribir el comando /stop.")
    command_quiz(m)

def command_stop(m):
    print_command(m)
    global correctAnswers
    global wrongAnswers
    global contador
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
    print_command(m) 
    msg     = m.text
    substr  = msg[0:5]
    print(substr)
    if m.text != None and substr != '/wiki':
        if m.text.lower() == "a":
            command_score(m, m.text.lower())
        elif m.text.lower() == "b":
            command_score(m, m.text.lower())
        elif m.text.lower() == "c":
            command_score(m, m.text.lower())
        elif m.text.lower() == "d":
            command_score(m, m.text.lower())
        else:
            bot.send_message(m.chat.id, "No te entiendo \"" + m.text + "\"\nPuedes escribir el comando /help para saber qué comando utilizar") 

if __name__ == '__main__':
    app.run(threaded=True)
