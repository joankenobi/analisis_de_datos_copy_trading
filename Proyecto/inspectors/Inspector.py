from dataclasses import replace
import os, sys, re, numpy as np
from environs import Env
from pyrogram.types.messages_and_media.message import Message
from logging_base import loge
env = Env()
env.read_env()

ALL_LAVERAGE = env.bool('ALL_LAVERAGE',False)
PERCENT_ALL_LAVERAGE = env.int('PERCENT_ALL_LAVERAGE',5)
class Inspector:
	
	_chat_id:int = 0
	_icons = "⚡️⚡️"
	_entry_targets_word = "Entry Targets"
	_take_profit_targets_word = "Take-Profit Targets"
	_stop_targets_word = "Stop"
	_symbol = ""
	_symbol_message = ""
	_currencies = {}
	_is_future = False
	_signal = {}
	_is_long = False
	_leverage = {}
	_percent_amount = 0
	_percent_trailing = 2
	_percent_leverage = PERCENT_ALL_LAVERAGE if ALL_LAVERAGE else 5
	_percent_sl=3
	_free = False

	_is_entry_market = False # indica que la operacion entra con cualquier precio que este en el mercado siempre que este se encuentre en el rango de los precios de entrada.

	_entry_targets = []
	_take_profit_targets = []
	_stop_targets = []

	_trailing_configuration={}

	_errors=[]

	# Constructor
	def __init__(self, message:Message):
		"""
		Resive el mensaje del hadler, extrae el text y combierte toda la informacion en datos.
			parametros:
				message: objeto del tipo Message que contiene toda la informacion del mensaje de free sygnal.
		"""
		self._errors = []
		self._text = getattr(message,'caption') or getattr(message,'text',False) or ''
		self._text_to_datas()

	def get_errors(self):
		return {'errors':self._errors}

	def set_errors(self,info={}):
		exc_type, exc_obj, exc_tb = sys.exc_info()
		fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
		# print(exc_type, fname, exc_tb.tb_lineno)
		self._errors.append({
		'type': str(exc_type).replace('>','').replace('<',''),
		'message':str(exc_obj),
		'file':fname,
		'method':exc_tb.tb_frame.f_code.co_name,
		'line':exc_tb.tb_lineno,
		**info
		})

	def _text_to_datas(self):
		"""
		Recorre todas las funciones del inspector que combierten el texto capturado por los inspectores_hijos
		en Data para ser enviado a binance.
		"""
		try:
			self._text_list = self._text_to_lines()
			self._symbol_message = self._get_symbol_message_by_text()
			self._symbol = self._get_symbol_by_text()
			self._currencies = self._get_currencies_by_text()
			self._is_future = self._get_is_future_by_text()
			self._is_long = self._get_is_long_by_text()
			self._leverage = self._get_leverage_by_text()
			self._entry_targets = self._get_entry_targets_by_text()
			self._take_profit_targets = self._get_take_profit_targets_by_text()
			self._stop_targets = self._get_stop_targets_by_text()
			self._trailing_configuration = self._get_trailing_configuration_by_text()
		except:
			self.set_errors()

	# Method div text in a list of lines
	def _text_to_lines (self):
		"""
			Separa cada linea de la señal free y lo guarda en una lista
		"""
		lines = self._text.split("\n")
		# return lines
		return [line.strip() for line in lines if bool(line)]

	def _get_symbol_message_by_text(self, search_word='#',seconds_currencies=("USD","USDT"),search_word_f=""):
		"""
			Busca una palabra clave en cada linea que permita ubicar los simbolos.
		"""
		symbol = ''

		for line in self._text_list:
			if search_word in line:
				symbol_line = line
				break

		# si no lo tengo todavia, lo busco en cualquier palabra con USDT
		if not symbol_line:
			for word in self._text.upper().split():
				if 'USDT' in word:
					symbol_line = word
					break

		if not symbol_line:
			raise Exception('no word')

		before_symbol = symbol_line.partition(search_word)[0]
		
		if before_symbol:
			symbol_line = symbol_line.replace(before_symbol,"")
		
		for currencie in seconds_currencies:
			if currencie in symbol_line:
				after_symbol=symbol_line.partition(currencie)[2]

		if after_symbol: 
			symbol_line= symbol_line.replace(after_symbol,"")
		
		symbol = symbol_line.replace("#","").replace(search_word,'').replace(search_word_f,'').replace('/',"").strip()
		return symbol

	
	def _get_symbol_by_text(self):
		"""
			Retorna el simbolo del mensaje con que lo contiene.
		"""
		if self._symbol_message:
			return self._symbol_message
		else:
			raise Exception('no word')
	
	def _get_currencies_by_text(self, segundary:str = 'USDT'):
		if "USDT" in self._symbol:
			data = self._symbol.replace(segundary,'')
			return {
				'primary':data,
				'segundary':segundary,
			}

		elif "/" in self._symbol_message:
			symbol=self._symbol_message.strip().split("/")	
			data= symbol[0]
			segundary= symbol[1]

			return {
				'primary':data,
				'segundary':segundary,
			} 
		else:
			raise Exception('no word')
	
	def _get_is_future_by_text(self):
		return True

	def _get_is_long_by_text(self, search_long:str = "Long"):
		return search_long in self._text

	def _get_leverage_by_text(self):
		return {
			"type": None, 
			"is_cross": self._is_long, 
			"percent": self._percent_leverage
		}
			
	def _get_entry_targets_by_text(self, search_word:str = 'entry targets'):
		numbers = None
		for line in self._text_list:
			if search_word in line and self._has_numbers_in_text(line):
				numbers = self._get_numbers_by_text(line)
				break
		if numbers:
			numbers = self._get_linspaces_by_numbers(numbers,5)
			numbers = self._add_one_with_percent(numbers)
			return numbers
		else:
			raise Exception('no entry_targets')

	def _get_take_profit_targets_by_text(self, search_word:str = 'take profit targets'):
		numbers = []
		for line in self._text_list:
			if search_word.upper() in line.upper() and self._has_numbers_in_text(line):
				numbers = self._get_numbers_by_text(line)
				break
		return numbers
	
	def _get_stop_targets_by_text(self, search_word:str = 'stop targets'):
		try:
			numbers = []
			if search_word in self._text:	
				for line in self._text_list:
					if search_word in line and self._has_numbers_in_text(line):
						numbers = self._get_numbers_by_text(line)
						break
			else:
				numbers.append(self._get_stop_targets_by_percent())
			return numbers
		except:
			self.set_errors()

	def _get_trailing_configuration_by_text(self):
		return {
			'quantity':0,
			'percent':self._percent_trailing
		}

	def get_all(self):
		"""
			Return a dictionary (Json) with the data modified from the free sygnal.
		"""
		return {
			"symbol_message": self._symbol_message,
			"symbol": self._symbol,
			"currencies": self._currencies,
			"is_future": self._is_future,
			"is_long": self._is_long,
			"leverage": self._leverage,
			"percent_amount": self._percent_amount,
			"is_entry_market": self._is_entry_market,
			"entry_targets": self._entry_targets,
			"take_profit_targets": self._take_profit_targets,
			"stop_targets": self._stop_targets,
			"trailing_configuration": self._trailing_configuration,
			"quantity": "",
			"quantity_take_profit":"",
			"free":self._free
		}
		
	@staticmethod
	def is_valid(message:Message):
		"""
			Aplica un buscador de palabras clave para validar si el mensaje le corresponde al inspector.

				message: data type object Message	
		"""
		return bool(message)

	@staticmethod
	def _has_numbers_in_text(text:str):
		return bool(re.search(r'\d', text))

	@staticmethod
	def _get_numbers_by_text(text:str,pattern:str = '\d+\.\d+|\d+' ):
		numbers_s = re.findall(fr"{pattern}",text)
		numbers_f = [float(n) for n in numbers_s]
		return numbers_f

	def _get_linspaces_by_numbers(self,numbers:list,num:int):
		if len(numbers) == 2:
			new_numbers = np.linspace(min(numbers),max(numbers), num)
		elif len(numbers) == 1:
			more_numbers = self._add_one_with_percent(numbers,1,True)
			new_numbers = np.linspace(min(more_numbers),max(more_numbers), num)
		return new_numbers.tolist()
	
	def _get_num_with_percent_by_direction(self,numbers:list,percent:int=1,invert=False, invert_long:bool=False):
		if not len(numbers):
			raise Exception('no numbers')
		
		num_percent = percent/100
		is_long = self._is_long
		
		if invert_long:
			is_long = not is_long
		
		if invert:
			num_percent = -1 * num_percent
		
		if is_long:
			num = max(numbers)*(1+(num_percent))
			return num
		else:
			num = min(numbers)*(1-num_percent)
			return num

	def _add_one_with_percent(self, numbers:list, percent:int = 1, invert:bool = False):
		try:
			new_num = self._get_num_with_percent_by_direction(numbers, percent, invert)
			if new_num:
				numbers.append(new_num)
			return numbers
		except:
			self.set_errors()

	def _get_stop_targets_by_percent(self):
		percent = self._percent_sl
		numbers = self._entry_targets
		return self._get_num_with_percent_by_direction(numbers,percent,False,True)