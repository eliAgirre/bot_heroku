# CONSTANTES
# constantes de entorno
import os
TOKEN = f'{os.environ["BOT_KEY"]}' 
URL = f'{os.environ["HEROKU_LINK"]}' 

# constantes ficheros
QUEST_FILENAME = 'preguntas.txt'
LOG_FILENAME   = 'logs.txt' 
READ_FILE      = 'r' 
APPEND_FILE    = 'a' 
WRITE_FILE     = 'w'

# constantes simbolos
PUNTO_COMA     = ';'
DOS_PUNTOS     = ':'

# constantes opciones
OPCION_A = 'a'
OPCION_B = 'b'
OPCION_C = 'c'
OPCION_D = 'd'

# constante teclado JSON
KEYBOARD = {"inline_keyboard": [[
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