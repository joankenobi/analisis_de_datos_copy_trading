import re, numpy as np
from environs import Env
from pyrogram.types.messages_and_media.message import Message
from inspectors.Inspector import Inspector

env = Env()
env.read_env()

ALL_LAVERAGE = env.bool('ALL_LAVERAGE',False)
PERCENT_ALL_LAVERAGE = env.int('PERCENT_ALL_LAVERAGE',5)

class InspectorHippo(Inspector):

	_chat_id:int = -1001381384148
	_percent_leverage = PERCENT_ALL_LAVERAGE if ALL_LAVERAGE else 5
	_free = True

	# Constructor Herencia
	def __init__(self, message: Message):
		super().__init__(message)
	
	# Method for obtain the binance crypto symbol
	def _get_symbol_message_by_text(self, search_word='⚡⚡', search_word_f='⚡️⚡️'):
		for line in self._text_list:
			if search_word in line or search_word_f in line:
				return line.replace("#", "").replace(search_word, "").replace(search_word_f, "").strip()
		raise Exception('no word')

	def _get_symbol_by_text(self):
		if self._symbol_message:
			if not 'USDT' in self._symbol_message:
				self._symbol_message = self._symbol_message.replace('USD', 'USDT')
			res = self._symbol_message.replace('/', "").strip()
			return res
		else:
			raise Exception('no word')

	def _get_leverage_by_text(self, search_word='Leverage', search_cross="Cross"):
		#default
		res = {
				"type": 'cross default', 
				"is_cross": self._is_long,
				"percent": self._percent_leverage
			}
		try:
			if not search_word in self._text:
				return res
			index = self._search_word_in_lines(self._text_list, search_word)
			if not index:
				return 
			data = self._text_list[index].split(":")
			split = data[1].split()
			if len(split)>1 and self._has_numbers_in_text(data[1]):
				percent = self._percent_leverage
				if not ALL_LAVERAGE:
					numbers = self._get_numbers_by_text(data[1])
					percent = int(numbers[0]) or self._percent_leverage
				res = {
					"type": split[0],
					"is_cross": search_cross in data[1], 
					"percent": percent
				}
			return res
		except:
			res = {
				"type": 'default', 
				"is_cross": self._is_long, 
				"percent": self._percent_leverage
			}
			return res

	def _get_entry_zone_by_text(self, search_word='Entry Zone'):
		try:
			data = []
			index = None
			if len(self._entry_targets):
				return
			if not search_word in self._text:
				index = self._search_word_in_lines(self._text_list, self._entry_targets_word)
			else:
				index = self._search_word_in_lines(self._text_list, search_word)
			if not index:
				return
			data_in_line = self._text_list[index].split(':')[1]

			if data_in_line:
				data = data_in_line.replace(' ','').split('-')
			else:
				data_next_line = self._text_list[index+1]
				data = data_next_line.replace(' ','').split('-')

			if data:
				self._is_entry_market = True
				return [float(n) for n in data]
		except:
			self.set_errors()

	def _get_entry_targets_by_text(self):
		entry_targets = []
		entry_targets = self._get_targets_list(self._entry_targets_word)
		if not entry_targets:
			entry_targets = self._get_entry_zone_by_text()
			entry_targets = self._prepare_entry_zone_limits(entry_targets)
		return entry_targets

	# Method Capture targets
	def _get_take_profit_targets_by_text(self):
		return self._get_targets_list(self._take_profit_targets_word)

	def _get_stop_targets_by_text(self):
		return self._get_targets_list(self._stop_targets_word)

	@staticmethod
	def is_valid(message: Message):
		if message.text:
			return bool(("⚡⚡ #" in message.text or "⚡️⚡️ #" in message.text or "⚡⚡#" in message.text or "⚡️⚡️#" in message.text) and "✅" not in message.text and "#Successful Result" not in message.text)
		return False

	# Method Capture targets
	def _get_targets_list( self, targest_type:str, select_data = "\d\)"):
		try:
			if not targest_type in self._text:
				return []
			data_list=[]
			t_index = 0
			t_index = self._search_word_in_lines(self._text_list, targest_type) 
			while t_index+1 < len(self._text_list) and re.match(select_data, self._text_list[t_index+1]):
				t_index += 1
				split_targets=self._text_list[t_index].split()
				for data in split_targets:
					if re.match('\d', data) and not re.search('\)$', data) and not re.search('\%$', data):
						data_list.append(float(data))
			return data_list
		except:
			self.set_errors({"targest_type":targest_type})

	def _search_word_in_lines(self, list_text, search_word:str = 'Exchange'):
		for i,line in enumerate(list_text):
			if search_word in line:
				return i
		return 0

	@staticmethod
	def _prepare_entry_zone_limits(entry_zone):
		entry_zone_limits = np.linspace(float(min(entry_zone)),float(max(entry_zone)),num=3)
		return entry_zone_limits.tolist()