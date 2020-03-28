# imports
import os
from util.constantes import LOG_FILENAME, READ_FILE, APPEND_FILE, WRITE_FILE
from util.arrays import userStep, knownUsers

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