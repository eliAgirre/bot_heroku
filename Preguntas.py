class Pregunta:
	def __init__(self, enunciado, resp_correcta):
		self.enunciado = enunciado
		self.resp_correcta = resp_correcta

	def print_pregunta(self):
		print(self.enunciado, self.resp_correcta)
