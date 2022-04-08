from pyrogram.types.messages_and_media.message import Message
# variables de entorno
from environs import Env
from inspectors.Inspector import Inspector
#toma las variables de entorno
env = Env()
env.read_env()
ALL_LAVERAGE = env.bool('ALL_LAVERAGE',False)
PERCENT_ALL_LAVERAGE = env.int('PERCENT_ALL_LAVERAGE',5)
COIN_COACH_PERCENT_TRAILING = env.int('COIN_COACH_PERCENT_TRAILING',2)
COIN_COACH_PERCENT_LEVERAGE = env.int('COIN_COACH_PERCENT_LEVERAGE',5)
COIN_COACH_PERCENT_SL = env.int('COIN_COACH_PERCENT_SL',3)

class InspectorCoinCoach(Inspector):

	_chat_id:int = -1001267170242
	_percent_trailing = COIN_COACH_PERCENT_TRAILING
	_percent_sl = COIN_COACH_PERCENT_SL
	_percent_leverage = PERCENT_ALL_LAVERAGE if ALL_LAVERAGE else COIN_COACH_PERCENT_LEVERAGE

	# Constructor
	def __init__(self, message:Message):
		super().__init__(message)
		
	def _get_is_long_by_text(self, search_short="SHORT"):
		return search_short not in self._text
				
	def _get_entry_targets_by_text(self):
		numbers = None
		for line in self._text_list:
			if (('LONG' in line.upper() or 'SHORT' in line.upper()) and self._has_numbers_in_text(line)):
				numbers = self._get_numbers_by_text(line)
				break
		if numbers:
			numbers = self._get_linspaces_by_numbers(numbers,5)
			numbers = self._add_one_with_percent(numbers)
			return numbers
		else:
			raise Exception('no entry_targets')

	# Method Capture targets
	def _get_take_profit_targets_by_text(self):
		return super()._get_take_profit_targets_by_text('TAKE PROFIT')

	def _get_stop_targets_by_text(self):
		return super()._get_stop_targets_by_text('SL')
		
	@staticmethod
	def is_valid(message:Message):
		text = getattr(message,'caption',False) or getattr(message,'text',False) or ''
		if text:
			return ("📊 FUTURES (BINANCE)" in text and "#" in text) or ('TAKE PROFIT:' in text and "#" in text) or ('Take Profit' in text)
		return False