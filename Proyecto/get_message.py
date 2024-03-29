from pyrogram import Client as ClientTg
from pyrogram.handlers import MessageHandler
from ToolsPyrogram import ToolsPyrogram
from environs import Env
import sys
from logging_base import loge

env = Env() #  pide los datos de la .env
env.read_env()
PROD = env.bool('PROD',False) #  indica si se esta en modo produccion (normalmente falso)
HISTORY = True
API_ID = env('API_ID_TELEGRAM') #  captura la key para la api de telegram
API_HASH = env('API_HASH_TELEGRAM')
NAME_SESSION = env('NAME_SESSION')
ID_CHAT_CONSOLE = env.int('ID_CHAT_CONSOLE') if PROD else env.int('ID_CHAT_CONSOLE_TEST')
CHANNEL_IDS = env.list("CHANNEL_IDS")

def main():
    app_tg=ClientTg(NAME_SESSION, API_ID, API_HASH) #  crea el cliente que se comunica con telegram
   
    init_message(app_tg)
    tools_pyrogram=ToolsPyrogram()
    
    message_id=281
    channel_id=-1001381384148

    ToolsPyrogram().get_message_from_history(client= app_tg,channel_id= channel_id,message_id= message_id, reverse=True, message_all=True)
    sys.exit()  
    app_tg.run()

def init_message(app_tg: ClientTg):
  """
    Informa el  del programa y si está en test o en produccion al canal de consola y ademas establece un ping con la API de Binance.
  """
  app_tg.start()
  app_tg.send_message(ID_CHAT_CONSOLE,'init read mode: '+('prod'if PROD else 'test')  + (' and geting hist' if HISTORY else ""))
  app_tg.stop()

if __name__ == '__main__':
  main()