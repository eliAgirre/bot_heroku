class Respuestas(): 

        def __init__(self): 
                self.correct_answers = [] 
                self.wrong_answers   = [] 

        def add_resp(self, enunciado, resp_correcta, user_answer): 
                if user_answer == resp_correcta: 
                        self.correct_answers.append(enunciado) 
                elif user_answer != resp_correcta: 
                        self.wrong_answers.append(enunciado) 

        def get_num_correct_resp(self): 
                return str(len(self.correct_answers)) 

        def get_num_wrong_resp(self): 
                return str(len(self.wrong_answers)) 

        def clean_resp(self): 
                self.correct_answers = [] 
                self.wrong_answers   = [] 
