#dependencias
from pyrogram import Client as ClientTg
from pyrogram.handlers import MessageHandler
from ToolsPyrogram import ToolsPyrogram
from All_testing import apply_all_testing
from environs import Env
import sys
from logging_base import loge

env = Env() #  pide los datos de la .env
env.read_env()
PROD = env.bool('PROD',False) #  indica si se esta en modo produccion (normalmente falso)
HISTORY = False
TESTING = True
HOST = env('MONGO_URL')
DB_NAME = env('MONGO_DB')
API_ID = env('API_ID_TELEGRAM') #  captura la key para la api de telegram
API_HASH = env('API_HASH_TELEGRAM')
NAME_SESSION = env('NAME_SESSION')
ID_CHAT_CONSOLE = env.int('ID_CHAT_CONSOLE') if PROD else env.int('ID_CHAT_CONSOLE_TEST')
CHANNELS_IDS = env.list("CHANNELS_IDS")

def main():
  app_tg=ClientTg(NAME_SESSION, API_ID, API_HASH) #  crea el cliente que se comunica con telegram
   
  init_message(app_tg)
  tools_pyrogram=ToolsPyrogram()

  if HISTORY:
      #for id in CHANNELS_IDS:
      if 1: 
        id=-1001381384148
        
        loge.info(f"----id-channel: {id}")
        data_base=DB_NAME
        host = HOST
        ToolsPyrogram().get_history(client=app_tg,channel_id=int(id),limit=3000,data_base=data_base,reverse=True)
      if TESTING:
         apply_all_testing(host=host,db_name=data_base)
      sys.exit()
  else:
    app_tg.add_handler(MessageHandler(tools_pyrogram.send_message, tools_pyrogram.channel_filter_crypto())) #  Manejador de mensajes (funcion callback, filtro)

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