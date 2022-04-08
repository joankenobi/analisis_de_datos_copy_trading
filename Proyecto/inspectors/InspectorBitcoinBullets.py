import re
from typing import Match
from environs import Env
from pyrogram.types.messages_and_media.message import Message
from inspectors.InspectorHippo import InspectorHippo

env = Env()
env.read_env()

ALL_LAVERAGE = env.bool('ALL_LAVERAGE',False)
PERCENT_ALL_LAVERAGE = env.int('PERCENT_ALL_LAVERAGE',5)

class InspectorBitcoinBullets(InspectorHippo):

	_chat_id:int = -1001196351154
	_percent_leverage = PERCENT_ALL_LAVERAGE if ALL_LAVERAGE else 5
	_entry_targets_regex:str = "ENTRY\s+(\d+(?:\.\d+)?)[\s\S]+?(\d+(?:\.\d+)?)"
	_take_profit_targets_word:str = "TARGETS"
	_stop_targets_word:str = "SL"
	_free = False

	# Method for obtain the binance crypto symbol
	def _text_to_datas(self):
		"""
		Recorre todas las funciones del inspector que combierten el texto capturado por los inspectores_hijos
		en Data para ser enviado a binance.
		"""
		try:
			self._text_list = self._text_to_lines()
			self._symbol_message = super(InspectorHippo,self)._get_symbol_message_by_text(search_word="📌$")
			self._symbol = self._get_symbol_by_text()
			self._currencies = self._get_currencies_by_text()
			self._is_future = self._get_is_future_by_text()
			self._is_long = self._get_is_long_by_text(search_long="LONG")
			self._leverage = super(InspectorHippo,self)._get_leverage_by_text()
			self._entry_targets = self._get_entry_targets_by_text(self._entry_targets_regex)
			self._take_profit_targets = self._get_take_profit_targets_by_text()
			self._stop_targets = self._get_stop_targets_by_text()
			self._trailing_configuration = self._get_trailing_configuration_by_text()
		except:
			self.set_errors()

	
	def _get_entry_targets_by_text(self, regex:str):
		match:Match = re.search(fr'{regex}',self._text)
		data = match.groups()
		return [float(n) for n in data]
	
	
	# Method Capture targets
	def _get_targets_list( self, targest_type:str):
		try:
			if not targest_type in self._text:
				return []
			data_list=[]
			t_index = 0
			t_index = self._search_word_in_lines(self._text_list, targest_type) 
			while t_index+1 < len(self._text_list) and re.match('\d', self._text_list[t_index+1]):
				t_index += 1
				data = self._text_list[t_index].strip()
				data_list.append(float(data))
			return data_list
		except:
			self.set_errors({"targest_type":targest_type})


	def _get_take_profit_targets_by_text(self):
		return self._get_targets_list(self._take_profit_targets_word)
		

	def _get_stop_targets_by_text(self):
		return self._get_targets_list(self._stop_targets_word)
	

	@staticmethod
	def is_valid(message: Message):
		"""
			Revisa los mensajes y los valida, para cada canal es distinto.
		"""
		if message.caption:
			return bool("📌$" in message.caption and "OTE:" in message.caption and "✅" not in message.caption)
		return False
