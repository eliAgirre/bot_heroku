# arrays
knownUsers = []  # todo: save these in a file
datos = []
correct_answers = []
wrong_answers   = []

# listas
userStep = {}  # so they won't reset every time the bot restarts

commands = {  # command description used in the "help" command 
    'start'       : 'Bienvenido al chatbot', 
    'help'        : 'Esta instrucción informa sobre los comandos de este bot',
    'quiz'        : 'Empezar el test',
    'stop'        : 'Se para el test y te da un resumen de tu puntuación.',
    'wiki'        : 'Busca información en la wikipedia.'
}