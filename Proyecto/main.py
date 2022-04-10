#dependencias
from pyrogram import Client as ClientTg
from pyrogram.handlers import MessageHandler
from ToolsPyrogram import ToolsPyrogram
from environs import Env


env = Env() #  pide los datos de la .env
env.read_env()
PROD = env.bool('PROD',False) #  indica si se esta en modo produccion (normalmente falso)
HISTORY = True
API_ID = env('API_ID_TELEGRAM') #  captura la key para la api de telegram
API_HASH = env('API_HASH_TELEGRAM')
PHONE = env('PHONE_NUMBER') 
NAME_SESSION = env('NAME_SESSION')
CHANNEL_ID_CONSOLE = env.int('CHANNEL_ID_CONSOLE') if PROD else env.int('CHANNEL_ID_CONSOLE_TEST')

def main():
  app_tg=ClientTg(NAME_SESSION, API_ID, API_HASH) #  crea el cliente que se comunica con telegram
   
  init_message(app_tg)
  tools_pyrogram=ToolsPyrogram()

  if HISTORY:
    ToolsPyrogram().get_history(app_tg,-1001267170242)
    
  else:
    app_tg.add_handler(MessageHandler(tools_pyrogram.send_message, tools_pyrogram.channel_filter_crypto())) #  Manejador de mensajes (funcion callback, filtro)

  app_tg.run()

def init_message(app_tg: ClientTg):
  """
    Informa el  del programa y si está en test o en produccion al canal de consola y ademas establece un ping con la API de Binance.
  """
  app_tg.start()
  app_tg.send_message(CHANNEL_ID_CONSOLE,'init read mode: '+('prod'if PROD else 'test')  + (' and geting hist' if HISTORY else ""))
  app_tg.stop()

if __name__ == '__main__':
  main()