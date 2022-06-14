import os, sys
import re

from pyrogram.types.messages_and_media.message import Message
#from TraderBinanceF import TraderBinanceF


class InspectorBFS:

	__icons = "⚡️⚡️"
	__entry_targets_word = "Entry Targets"
	__take_profit_targets_word = "Take-Profit Targets"
	__stop_targets_word = "Stop Targets"
	__symbol = ""
	__symbol_message = ""
	__currencies = {}
	__is_future = False
	__signal = {}
	__leverage = {}
	__percent_amount = 0

	__entry_zone = []
	__is_entry_zone = False

	__entry_targets = []
	__take_profit_targets = []
	__stop_targets = []

	__trailing_configuration={}

	__errors=[]

	# Constructor
	def __init__(self, message:Message):
		self.__errors = []
		self.__text = message.caption
		self.__text_to_datas()

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

	def __text_to_datas(self):
		try:
			self.__text_list = self.__text_to_lines()
			self.__symbol_message = self.__get_symbol_message_by_text(self.__text_list)
			self.__symbol = self.__get_symbol_by_text()
			self.__currencies = self.__get_currencies_by_text()
			# self.__is_future = self.__get_is_future_by_text(self.__text_list)
			self.__is_future = self.__get_is_future_by_text(self.__text)
			self.__leverage = self.__get_leverage_by_text(self.__text_list)
			self.__signal = self.__get_signal_by_text(self.__text_list)
			self.__percent_amount = self.__get_percent_amount_by_text(self.__text_list)
			self.__entry_targets = self.__get_targets_list(self.__entry_targets_word)
			self.__entry_zone = self.__get_entry_zone_by_text(self.__text_list)
			self.__take_profit_targets = self.__get_targets_list(self.__take_profit_targets_word)
			self.__stop_targets = self.__get_targets_list(self.__stop_targets_word)
			self.__trailing_configuration = self.__get_trailing_configuration_by_text(self.__text_list)
		except:
			self.set_errors()

	# Method div text in a list of lines
	def __text_to_lines (self):
		lines = self.__text.split("\n")
		# return lines
		return [line.strip() for line in lines if bool(line)]

	# Method for obtain the binance crypto symbol     
	def __get_symbol_message_by_text(self, list_text, search_word='⚡⚡', search_word_f='⚡️⚡️'):
		for line in list_text: 
			if re.match(search_word, line) or re.match(search_word_f, line):
				return line.replace("#","").replace(search_word,"").replace(search_word_f,"").strip()
			else:
				raise Exception('no word')

	def __get_symbol_by_text(self):
		if self.__symbol_message and self.__symbol_message != "no word":
			if not 'USDT' in self.__symbol_message:
				self.__symbol_message = self.__symbol_message.replace('USD','USDT')
			res = self.__symbol_message.replace('/',"").strip()
			return res
		else:
			raise Exception('no word')
	
	def __get_currencies_by_text(self):
		if self.__symbol_message and self.__symbol_message != "no word":
			data = self.__symbol_message.strip().split('/')
			return {
				'primary':data[0],
				'segundary':data[1],
			} 
		else:
			raise Exception('no word')

	# Method for obtain the binance crypto symbol     
	def __search_word_in_lines(self, list_text, search_word='Exchange'):
		index = 0
		for line in list_text:
			# if re.match(search_word, line):
			if search_word in line:
				index = list_text.index(line)
		return index

	# def __get_is_future_by_text(self, list_text, search_word='Exchange', search_future="Futures"):
		# index = self.__search_word_in_lines(list_text, search_word)
		# return search_future in list_text[index].split()

	def __get_is_future_by_text(self, text, search_future="Futures"):
		return search_future in text

	def __get_signal_by_text(self, list_text, search_word='Type', search_long="(Long)"):
		index = self.__search_word_in_lines(list_text, search_word)
		if not index:
				return 
		data = list_text[index].split(":")
		res = data[1].split()
		return {
				"type": res[0],
				"is_long": search_long == res[1]
				}

	def __get_leverage_by_text(self, list_text, search_word='Leverage', search_cross="Cross"):
		index = self.__search_word_in_lines(list_text, search_word)
		if not index:
				return 
		data = list_text[index].split(":")
		res = data[1].split()
		percent = 5
		if len(res)>1 and  bool(re.search(r'\d', data[1])):
			percent = int(res[1].replace('.0X','').replace('.0x','').replace('(','').replace(')',''))
		return {
			"type": res[0], 
			"is_cross": search_cross == res[0], 
			"percent": percent
		}

	def __get_percent_amount_by_text(self, list_text, search_word='Amount'):
		index = self.__search_word_in_lines(list_text, search_word)
		if not index:
				return 
		data = list_text[index].split(':')
		if data[1]:
			return int(data[1].replace('.0%',''))

	def __get_entry_zone_by_text(self, list_text, search_word='Entry Zone'):
		data = None
		index = self.__search_word_in_lines(list_text, search_word)
		if not index and not len(self.__entry_targets):
			index = self.__search_word_in_lines(list_text, self.__entry_targets_word)
		if not index:
			return
		data_in_line = list_text[index].split(':')[1]
		
		if data_in_line:
			data = data_in_line.replace(' ','').split('-')
		else:
			data_next_line = list_text[index+1]
			data = data_next_line.replace(' ','').split('-')

		if data:
			self.__is_entry_zone = True
			return {"min":min(data),"max":max(data)}

	# Method Capture targets
	def __get_targets_list( self, targest_type, select_data = "\d\)"):
		try:
			data_list=[]
			t_index = 0
			for line in self.__text_list: 
				if re.match(targest_type, line):
					t_index = self.__text_list.index(line)
				while t_index+1 < len(self.__text_list) and re.match(select_data, self.__text_list[t_index+1]):
					t_index += 1
					split_targets=self.__text_list[t_index].split()
					for data in split_targets:
						if re.match('\d', data) and not re.search('\)$', data) and not re.search('\%$', data):
							data_list.append(data)
			return data_list
		except:
			self.set_errors({"targest_type":targest_type}) 

	def __get_trailing_configuration_by_text(self, list_text, search_word='Trailing Configuration'):
		try:
			index = self.__search_word_in_lines(list_text, search_word)
			if not index:
					return 
			configurations = list_text[index+1:]
			res={}
			for configuration in configurations:
				data = configuration.split(':')
				res[data[0].strip()] = data[1].strip()
			if res:
				return res
		except:
			self.set_errors()

	def get_symbol_message(self):
		return self.__symbol_message

	def get_symbol(self):
		return self.__symbol

	def get_currencies(self):
		return self.__currencies

	def is_future(self):
		return self.__is_future

	def get_signal(self):
		return self.__signal

	def get_leverage(self):
		return self.__leverage

	def get_percent_amount(self):
		return self.__percent_amount

	def get_entry_zone(self):
		return self.__entry_zone

	def get_entry_targets(self):
		return self.__entry_targets

	def get_take_profit_targets(self):
		return self.__take_profit_targets

	def get_stop_targets(self):
		return self.__stop_targets

	def get_trailing_configuration(self):
		return self.__trailing_configuration

	def get_all(self):
		return {
			"symbol_message": self.__symbol_message,
			"symbol": self.__symbol,
			"currencies": self.__currencies,
			"is_future": self.__is_future,
			"signal": self.__signal,
			"leverage": self.__leverage,
			"percent_amount": self.__percent_amount,
			"is_entry_zone": self.__is_entry_zone,
			"entry_zone": self.__entry_zone,
			"entry_targets": self.__entry_targets,
			"take_profit_targets": self.__take_profit_targets,
			"stop_targets": self.__stop_targets,
			"trailing_configuration": self.__trailing_configuration,
		}
		
	@staticmethod
	def is_valid(message:Message):
		if message.caption:
			return bool("🏦 Exchange: binance" in message.caption)
		return False