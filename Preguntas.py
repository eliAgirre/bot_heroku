class Pregunta:
	def __init__(self, enunciado, resp_correcta):
		self.enunciado = enunciado
		self.resp_correcta = resp_correcta

	def get_enunciado(self):
		return self.enunciado

	def get_resp_correcta(self):
		return self.resp_correcta
