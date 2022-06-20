import json, sys, os
from typing import List #  libreria para pasar Json a ditc e inversa, Libreria que maneja variables en el interprete.
from datetime import datetime as dt
from environs import Env 
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
from Managers.InspectorsManager import InspectorsManager
from mongo_db_crud import Mongodb
from logging_base import loge

env = Env()
env.read_env()
PROD = env.bool('PROD',False) 
CHANNEL_IDS = env.list('CHANNEL_IDS'if PROD else'CHANNEL_IDS_TEST',subcast=int) #  captura los canales.id de produccion o test
CHANNEL_NAMES = env.list('CHANNEL_NAMES') if PROD else env.list('CHANNEL_NAMES_TEST') #  captura los canales.nombres de produccion o test
CHANNEL_ID_CONSOLE = env.int('CHANNEL_ID_CONSOLE') if PROD else "-1001771813711" #env.int('CHANNEL_ID_CONSOLE_TEST')
ID_MY_CHANNEL_SEND_MESSAGE = env.int('ID_MY_CHANNEL_SEND_MESSAGE') if PROD else env.int('ID_MY_CHANNEL_SEND_MESSAGE_TEST')

class ToolsPyrogram:

	__errors=[] #  guardará los errores

	# Constructor
	def __init__(self):
		self.__inspectM = InspectorsManager()

	async def send_message(self,client:Client, message: Message):
		"""
			Se encarga de enviar la data de interes a su destino, como los canales de observación y preprocesamiento de trading.

				client: cliente conectado a telegram por pyrogram.

				message: objeto de tipo Message, usado para reenviarlos a los canales de observación.

			Si no hay datos envia informacion de error.
		"""
	#todos lo await deben ir dentro de la palabra clave "async"
		try:
			data = await self.get_data(client)	#  Guarda los datos de interes del mensaje
						
			if len(data): #  si el tamaño de la data != 0
				
				await message.forward(CHANNEL_ID_CONSOLE) #  envia el mensaje al canal consola
				text = self.prepare_text(data)
				await client.send_message(CHANNEL_ID_CONSOLE, text) #  envia la data preparada al canal de consola
			
				e_trader = ""
				if len(e_trader['errors']):
						text = self.prepare_text(e_trader, True, data['symbol_message'])
						await client.send_message(CHANNEL_ID_CONSOLE, text) #  Envia los errores de trading al canal de consola

		except:
			self.set_errors()
			text = json.dumps(self.get_errors(), indent=2)
			await client.send_message(CHANNEL_ID_CONSOLE, text) # envia los errores del proceso al canal de consola.

	async def get_data(self,client):
		"""
			Revisa si el Inspector Manager tiene los datos de interes del mensaje guardados
			y retorna.

			Si no hay datos, optiene los posibles errores y retorna una lista vacia.
		
				client: cliente conectado a telegram por pyrogram.
		"""
		if self.__inspectM.get_data_inspector():
			return self.__inspectM.get_data()
		errors = self.__inspectM.get_errors()
		mg = self.prepare_text(errors, True)
		await client.send_message(CHANNEL_ID_CONSOLE, mg) #  envia los errores al canal de consola
		return []

	def channel_filter_crypto(self):
		"""
			Crear filtro
		"""
		return filters.create(self.new_filter_crypto)

	async def new_filter_crypto(self, client, message: Message):
		"""
			Filtro para los mensajes entrantes, guarda el mensaje de interes y lo envia al manejador de inspectores 
			para aplicarle un inspector correspondiente.

				client: cliente conectado a telegram por pyrogram

				message: objeto de tipo Message

			Tiene una segunda función que es leer los mensajes entrantes al canal de TEST
			para obtener informacion de los canales sin tener que usar otro programa.	
		"""
		chat_id = message.chat.id
		if message.chat.title=="test read binance":
			#captura los ide de los canales cual se reenvia un mensaje a test binance
			print(str(message.forward_from_chat.id) +"="+ message.forward_from_chat.title)
			#print(message.text)
			#print(message.caption)
			chat_id = message.forward_from_chat.id

		if (message.text or message.caption) and message.chat and message.chat.type == "channel" and message.chat.id in CHANNEL_IDS:
			self.__inspectM.set_message(message) #  pasa el mensaje al inspector manager
			value=self.__inspectM.is_valid(chat_id)
			loge.debug(f"value is: {value}")
			return value

	def prepare_text(self,data, is_errors = False, symbol = ''):
		"""
			Prepara el un texto informativo de cuales fueron los datos enviados para ejecutar la orden.
			Este texto es enviado al canal de consola.
		"""
		text=''
		head = '#'+ symbol +'\n' if symbol else ''
		if data : 
			head_errors = '#ERRORS: \n'
			str_data = json.dumps(data, indent=2)
			if not is_errors :
				head = '#'+data['symbol_message']+'\n'
				text = head + str_data
			else:
				text = head + head_errors + str_data
				if len(text) > 4096:
					print(text)
					text = 'The message text is over 4096 characters'
			return text
		text='Sin data'
		return text
		
	def get_errors(self):
		return {'errors':self.__errors}

	def set_errors(self,info={}):
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		# print(exc_type, fname, exc_tb.tb_lineno)
		self.__errors.append({
		'type': str(exc_type).replace('>','').replace('<',''),
		'message':str(exc_obj),
		'file':fname,
		'method':exc_tb.tb_frame.f_code.co_name,
		'line':exc_tb.tb_lineno,
		**info
		})

	def get_history(self,client:Client, channel_id,limit=None,host="mongodb://localhost:27017/", data_base="DB_test",reverse=False):
		"""
			Retorna todos los mensajes publicados en el canal o el chat.
				
				reverse: es True retorna desde el más viejo al más nuevo. Default to False
				
				client: la variable cliente creada para pyrogram.
				
				channel_id: es el numero ide del canal, grupo o chat.

				limit: cantidad de datos a guardar.
		"""

		db=Mongodb(host).set_db(data_base)
		if limit==None:
			limit=int(input("Ingrese la cantidad de datos a guardar: "))
		n=0
		with client:
			try:
				message:Message
				for message in client.iter_history(channel_id, reverse=reverse):
					loge.debug(f"El menssage es: {message.message_id}")
						
					if (message.text or message.caption) and message.chat and message.chat.type == "channel":
							self.__inspectM.set_message(message) #  pasa el mensaje al inspector manager
							value=self.__inspectM.is_valid(message.chat.id)
							loge.debug(f"value is: {value}")
						
							if  value and self.__inspectM.get_data_inspector():
								data = self.__inspectM.get_data()						

								id= Mongodb().Insert_data("signals",data).inserted_id # obtiene el id with mongo
								Mongodb().update_by_id("signals",id,"timeStamp_Tg",message["date"]) #  Nota: La fecha del mensaje en el objeto tipo Message esta en la zona horraria adecuada, pero al sacar el atributo aparece en UTC=+00
								Mongodb().update_by_id("signals",id,"date",dt.fromtimestamp(message["date"])) # con datetime.fromtimestamp la fecha es extraida en el timezone correcto
								Mongodb().update_by_id("signals",id,"message_id",message["message_id"])
								Mongodb().update_by_id("signals",id,"channel",message.chat.title)
								Mongodb().update_by_id("signals",id,"channel_id",message.chat.id)
								Mongodb().update_by_id("signals",id,"message_link",message.link)
								n+=1
							loge.info(f"n:{n}")
							if n==limit:
								break
					else:
						loge.debug(f"""no se cumplio la primera condicion 
								message.chat.id: {message.chat.id}
								message.chat.id in list?: {bool(message.chat.id in CHANNEL_IDS)}
								message.text or message.caption: {bool(message.text or message.caption)}
								message.chat.type: {message.chat.type}
								message.chat: {bool(message.chat)}
							""")
					
			except Exception as e:
					loge.error(f"Algo pasa con el id:{channel_id} error: {e}")
			
	def get_message_from_history(self,client:Client, channel_id=None, message_id=None,reverse=False, message_all=False)-> Message:
		"""Retorna el mensaje indicado por el id y el canal.

		Args:
			client (Client): Cliente para conectar con la API
			reverse (Bool): si es True busca desde los mas viejos hasta los mas nuevos. Defaults to False.
			channel_id (int, optional): id del canal donde se encuentra el mensaje. Defaults to None.
			message_id (int, optional): id del mensaje buscado. Defaults to None.
			message_all (Bool): "True" si se quiere de retorno todo el objeto message. Default to False.
		"""
		
		with client:
			try:
				message:Message
				for message in client.iter_history(channel_id,reverse=reverse):
					if message.message_id == message_id:
						print(f"El message.date.real: {message.date.real}")
						print(f"El message.date: {message.date}")
						print(f"El message.link: {message.link}")

						# metodo ideal para capturar la fecha aportada por telegram directamente de message
						message_list:list=message.__str__().splitlines()
						for line in message_list:
							if '"date"' in line:
								fecha=line.replace('"','').replace('date','').strip()
								print(f"""El message.date. my zone: {fecha}""")
						if message_all==True:
							print(message)
			except Exception as e:
				loge.error(f"Algo pasa con el id:{channel_id} error: {e}")