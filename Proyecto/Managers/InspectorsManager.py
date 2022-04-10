from typing import Dict
from pyrogram.types.messages_and_media.message import Message
from inspectors.Inspector import Inspector
from inspectors.InspectorBitcoinBullets import InspectorBitcoinBullets
from inspectors.InspectorCoinCoach import InspectorCoinCoach
from inspectors.InspectorHippo import InspectorHippo
from inspectors.InspectorRussianInsiders import InspectorRussianInsiders
from logging_base import loge

#import time
class InspectorsManager:
	"""
		Contiene los inspectores de los canales y los ejecuta si son validos sus mensajes.
	"""
	__inspectors:Dict[int,Inspector] = {
		1:InspectorHippo,
		2:InspectorCoinCoach,
		3:InspectorRussianInsiders,
		4:InspectorBitcoinBullets
	}
	__is_valid = False
	__trader_f = None
	__text = ''
	__once = ''
	__message = ''
	__data = []
	__errors = []

  # Constructor
	def __init__(self): 
		None

	
	def set_message(self,message:Message):
		"""
			Captura el object menssage y lo guarda como atributo.

				message: data type object Message
		"""
		self.__message = message

	def is_once(self):
		"""
			Revisa si el atributo del mensaje ya ha sigo guardado antes, si no, lo guarda y devuelve true
			el objetivo es evitar que se utilice un mensaje mas de una vez
		"""
		text = getattr(self.__message,'caption',False) or getattr(self.__message,'text',False) or ''
		if self.__once != text:

			loge.info(f"is_once?: {bool(self.__once != text)}")
			
			self.__once = text
			return True
		else:
			return False

	def is_valid(self, chat_id:int)-> bool:
		"""
			Revisa si is_once se cumple para el mensaje y aplica un inspector valido segun el canal de telegram .
			Si no se cumple devuelve false.

				chat_id: es el numero ID del canal del mensaje.
		"""
		loge.debug(f"Inicia el manager is_valid")
		is_valid = False
		once = self.is_once()
		if once:
			loge.info(f"once?: {once}")

			for key in self.__inspectors:

				loge.debug(f"""
					self.__inspectors[key].is_valid(self.__message): {self.__inspectors[key].is_valid(self.__message)}
					""")
				
				if self.__inspectors[key].is_valid(self.__message) and self.__inspectors[key]._chat_id == chat_id:


					is_valid = key
					break	
		if is_valid:
			self.__is_valid = is_valid
			loge.debug(f"{__name__}... value is: {is_valid}")
		return bool(is_valid)

	def get_data_inspector(self):
		"""
			Guarda todos los datos de interes capturados por el inspector correspondiente del mensaje,
			 siempre que no haya habido ningun error en el proceso de obtenerlos.

			Retorna True si no hay error de lo contrario False. 
		"""
		#start_time = time.time()
		inspect = self.__inspectors[self.__is_valid](self.__message)
		data = []
		e_inspect = []
		e_inspect = inspect.get_errors()
		if len(e_inspect['errors']):
			self.__errors = e_inspect
			return False
		data = inspect.get_all()
		self.__data = data
		#TODO Aqui deberia instanciarse y usarse el prepare
		#print("--- %s seconds ---" % (time.time() - start_time))
		return bool(data)

	def get_data(self):
		"""
			Retorna los datos de interes guardados del mensaje.
		"""
		return self.__data

	def get_errors(self):
		"""
			Retorna los errores obtenidos en el proceso.
		"""
		return self.__errors