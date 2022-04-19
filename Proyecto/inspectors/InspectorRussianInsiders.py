from environs import Env
from pyrogram.types.messages_and_media.message import Message
from inspectors.InspectorHippo import InspectorHippo

env = Env()
env.read_env()

ALL_LAVERAGE = env.bool('ALL_LAVERAGE',False)
PERCENT_ALL_LAVERAGE = env.int('PERCENT_ALL_LAVERAGE',5)

class InspectorRussianInsiders(InspectorHippo):

	_chat_id:int = -1001277174399
	_percent_leverage = PERCENT_ALL_LAVERAGE if ALL_LAVERAGE else 5
	_entry_targets_word:str = "ENTRY"
	_take_profit_targets_word:str = "🔘Target\s+\d+.+?(\d+(?:\.\d+)?)"
	_stop_targets_word:str = "🚫STOP LOSS:"
	_free = False

	# Constructor Herencia
	def __init__(self, message: Message):
		super().__init__(message)

	# Method for obtain the binance crypto symbol
	def _text_to_datas(self):
		"""
		Recorre todas las funciones del inspector que combierten el texto capturado por los inspectores_hijos
		en Data para ser enviado a binance.
		"""
		try:
			self._text_list = self._text_to_lines()
			self._symbol_message = self._get_symbol_message_by_text(search_word="$")
			self._symbol = self._get_symbol_by_text()
			self._currencies = self._get_currencies_by_text()
			self._is_future = self._get_is_future_by_text()
			self._is_long = self._get_is_long_by_text(search_long="LONG")
			self._leverage = super(InspectorHippo,self)._get_leverage_by_text()
			self._entry_targets = self._get_entry_targets_by_text()
			self._take_profit_targets = self._get_take_profit_targets_by_text()
			self._stop_targets = self._get_stop_targets_by_text()
			self._trailing_configuration = self._get_trailing_configuration_by_text()
		except:
			self.set_errors()

	def _get_symbol_message_by_text(self, search_word='#',seconds_currencies=("USD","USDT"),search_word_f=""):
		"""
			Busca una palabra clave en cada linea que permita ubicar los simbolos.
			El mismo que en Inspector padre
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
			symbol_line=symbol_line.replace(before_symbol,"")
		
		for currencie in seconds_currencies:
			if currencie in symbol_line:
				after_symbol=symbol_line.partition(currencie)[2]

		if after_symbol: 
			symbol_line= symbol_line.replace(after_symbol,"")
		
		symbol = symbol_line.replace("#","").replace(search_word,'').replace(search_word_f,'').replace('/',"").strip()
		return symbol

	def _get_entry_targets_by_text(self):
		try:
			entry_targets:list = []
			entry_targets = self._get_entry_zone_by_text(self._entry_targets_word)
			entry_targets = self._prepare_entry_zone_limits(entry_targets)
			return entry_targets
		except:
			self.set_errors()

	def _get_stop_targets_by_text(self):
		return super(InspectorHippo,self)._get_stop_targets_by_text(self._stop_targets_word)

	def _get_take_profit_targets_by_text(self):		
		return self._get_numbers_by_text(self._text,self._take_profit_targets_word)

	@staticmethod
	def is_valid(message: Message):
		"""
			Revisa los mensajes y los valida, para cada canal es distinto.
		"""
		if message.caption:
			return bool(("$" in message.caption or "Trade ID:" in message.caption) and "✅" not in message.caption)
		return False
