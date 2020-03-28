import random

from util.methods import print_command, get_user_step
from util.arrays import userStep, knownUsers, commands, datos, correct_answers, wrong_answers
from util.constantes import READ_FILE, QUEST_FILENAME, PUNTO_COMA, DOS_PUNTOS, OPCION_A, OPCION_B, OPCION_C, OPCION_D

# COMANDOS
def command_start(m):
    print('command_start') 
    print_command(m) 
    cid = m.chat.id 
    response = ''
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet: 
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later 
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command 
        response = "Bienvenido.\nEste es un chat para practicar preguntas sobre la oposición de TAI.\nAprende constestando las preguntas y tienes la opción de ver youtube (@youtube) y de realizar las búsquedas en la wikipedia (@wiki)."
        command_help(m)  # show the new user the help page 
    else: 
        response = "Ya te conozco, eres "+m.chat.first_name+".\nPara ver los comandos puedes escribir /help."
    return response

def command_help(m): 
    print('command_help') 
    print_command(m) 
    help_text = "Los siguientes comando están disponibles para este bot: \n" 
    for key in commands:  # generate help text out of the commands dictionary defined at the top 
        help_text += "/" + key + ": " 
        help_text += commands[key] + "\n" 
    return help_text

def command_quiz(m): 
    print('command_quiz') 
    get_user_step(m.chat.id)
    print_command(m)
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

    datos.insert(0, enunciado)
    datos.insert(1, resp_correcta)
    if datos:
        print("array de datos después de introducir: "+datos[0]+" y "+datos[1])
    return texto
    #bot.send_message(m.chat.id, texto, parse_mode='Markdown', reply_markup=KEYBOARD)
    #bot.send_message(m.chat.id, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")

def command_score(cid, user_answer):
    print('command_score') 
    #print_command(m)
    global datos
    global correct_answers
    global wrong_answers
    enunciado = ''
    resp_correct = ''
    response = ''
    if datos:
        print("array de datos en commando score: "+datos[0]+" y "+datos[1])
        enunciado = datos[0]
        resp_correct = datos[1]
    else:
        print("Los datos del array están vacíos.")
    
    print("enunciado: "+enunciado)
    print("resp correcta: "+resp_correct)
    print("rep usuario: "+user_answer)

    if enunciado and resp_correct and user_answer:
        if user_answer == resp_correct: 
            correct_answers.append(enunciado) 
        elif user_answer != resp_correct: 
            wrong_answers.append(enunciado)
    else:
        print("Hubo un problema con obtener los datos del enunciado, la respuesta del usuario y la respuesta correcta.")

    print("resp correctas "+str(len(correct_answers)))
    print("resp incorrectas "+str(len(wrong_answers)))

    if enunciado and resp_correct and user_answer:
        response = "El enunciado ha sido: "+enunciado+"\nTu respuesta ha sido la *"+user_answer+"*.\n*La respuesta correcta es: "+resp_correct+"*\n"
        #bot.send_message(cid, "El enunciado ha sido: "+enunciado+"\nTu respuesta ha sido la *"+user_answer+"*.\n*La respuesta correcta es: "+resp_correct+"*", parse_mode='Markdown')
    else:
        response = "Hubo problemas al obtener los datos. Puede escribir el comando /stop y volver a empezar con el comando /quiz.\n"
        #bot.send_message(cid,"Hubo problemas al obtener los datos. Puede escribir el comando /stop y volver a empezar con el comando /quiz.")

    response += "Respuestas *correctas*: "+str(len(correct_answers))+".\nRespuestas *incorrectas*: "+str(len(wrong_answers))+".\nPara parar el test puedes escribir el comando /stop.\n"
    #bot.send_message(cid, "Respuestas *correctas*: "+str(len(correct_answers))+".\nRespuestas *incorrectas*: "+str(len(wrong_answers))+".\nPara parar el test puedes escribir el comando /stop.", parse_mode= 'Markdown')
    
    if datos:
        print("array de datos antes de limpiar: "+datos[0]+" y "+datos[1])

    datos = []
    response += "Para que el bot te haga otra pregunta puedes escribir el comando /quiz."
    #bot.send_message(cid, "Para que el bot te haga otra pregunta puedes escribir el comando /quiz.")
    #command_quiz(m)
    return response

def command_stop(m):
    print('command_stop') 
    print_command(m)
    global correct_answers
    global wrong_answers
    contador = 0
    response = ''
    if len(correct_answers) > 0 or len(wrong_answers) > 0:
        contador = len(correct_answers)+len(wrong_answers)
        response = "De las *"+str(contador)+"* preguntas.\nRespuestas *correctas* : "+str(len(correct_answers))+".\nRespuestas *incorrectas*: "+str(len(wrong_answers))+".\n"
        #bot.send_message(m.chat.id, "De las *"+str(contador)+"* preguntas.\nRespuestas *correctas* : "+str(len(correct_answers))+".\nRespuestas *incorrectas*: "+str(len(wrong_answers))+".", parse_mode= 'Markdown')
        contador = 0
        correct_answers = []
        wrong_answers = []
        response += "Para empezar hacer el test puedes escribir el comando /quiz."
        #bot.send_message(m.chat.id, "Para empezar hacer el test puedes escribir el comando /quiz.")
        #bot.send_message(m.chat.id, "Para realizar el test de algún puedes escribir el comando /b1 o /b2 o /b3 o /b4.")
    else:
        response = "No hay puntuación, ya que no has respondido al test.\nPara empezar hacer el test puedes escribir el comando /quiz y después hacer clic en alguna de las opciones correspondientes."
        #bot.send_message(m.chat.id, "No hay puntuación, ya que no has respondido al test.\nPara empezar hacer el test puedes escribir el comando /quiz y después hacer clic en alguna de las opciones correspondientes.")
    return response

def command_wiki(m):
    print('command_wiki') 
    print_command(m)
    msg     = m.text
    params  = msg[6:]
    response = ''
    if params:
        lang = 'es'
        paramlang = params[0].lower().split(DOS_PUNTOS)[0]
        search = ''.join(params)
        search = search.lstrip('%s:' % paramlang)
        if paramlang in ['en', 'fr', 'de', 'pt']:
            lang = paramlang
        response = "https://%s.wikipedia.org/wiki/%s" % (lang, params)
    else:
        response = 'No has puesto nada después de /wiki para buscarlo.'
    return response

def command_default(m):
    print('command_default') 
    print_command(m) 
    msg     = m.text
    substr  = msg[0:5]
    search  = msg[6:]
    trim = search.strip()
    response = ''
    print("msg text: "+msg)
    print("substring: "+substr)
    print("search: "+search)
    print("longitud trim: "+str(len(trim)))
    if m.text != None and substr == '/wiki':
        if substr == '/wiki':
            if len(trim) is 0:
                print("Lo que busca está vacío.")
                response = 'No has puesto nada después de /wiki para buscarlo.'
            elif len(trim) > 0:
                response = command_wiki(m)
                #response = 'command wiki'
        else:
            response = "No te entiendo \"" + msg + "\"\nPuedes escribir el comando /help para saber qué comando utilizar"
    else:
        response = "No te entiendo \"" + msg + "\"\nPuedes escribir el comando /help para saber qué comando utilizar"
    return response

def redirect_command(m, text):
    print('redirect_command') 
    print_command(m)
    print("todo el mensaje: ", m)
    msg = m.message_id
    substr  = text[0:5]
    search  = text[6:]
    trim    = search.strip()
    response = ''
    print("texto: ", text)
    print("substr: ", substr) 
    print("search: ", search)
    print("longitud trim: ", str(len(trim)))

    if text and substr:
        if substr == '/wiki': 
            if len(trim) is 0:
                print("Lo que busca está vacío.")
                response = 'No has puesto nada después de /wiki para buscarlo.'
    
    if text: 
        if text == '/start': 
            response = command_start(m) 
        elif text == '/help': 
            response =  command_help(m)
        elif text == '/quiz': 
            response = command_quiz(m)
        elif text == '/stop': 
            response = command_stop(m)
        else: 
            response = command_default(m)
    return response

# callback query
def callback_query(call, user_answer):
    cid = call.message.chat.id
    response = ''
    if user_answer:
        #texto = "Tu respuesta ha sido: *"+user_answer+"*.\nPara saber tu puntuación puedes escribir el comando /score."
        if user_answer == OPCION_A:
            response = command_score(cid, user_answer)
        elif user_answer == OPCION_B:
            response =  command_score(cid, user_answer)
        elif user_answer == OPCION_C:
            response = command_score(cid, user_answer)
        elif user_answer == OPCION_D:
            response = command_score(cid, user_answer)
            #bot.send_message(cid, texto, parse_mode="Markdown")
    else:
        response = "No has respondido a la pregunta"
        #bot.send_message(cid, "No has respondido a la pregunta")
    return response