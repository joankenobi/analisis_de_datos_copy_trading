# IMPORTS
import pandas as pd
import math
import os.path
import time
from binance.client import Client
from datetime import timedelta, datetime
from dateutil import parser
from environs import Env
from logging_base import loge

env = Env()
env.read_env()

PROD = env.bool('PROD',False)
### API
API_KEY_BINANCE = env('API_KEY_BINANCE')
SECRET_KEY_BINANCE = env('SECRET_KEY_BINANCE')

### CONSTANTS
binsizes = {"1m": 1, "5m": 5, "1h": 60, "1d": 1440}
batch_size = 750
binance_client = Client(api_key=API_KEY_BINANCE, api_secret=SECRET_KEY_BINANCE)

### FUNCTIONS
def minutes_of_new_data(symbol:str, kline_size:str, data:pd.DataFrame, source="Binance"):
    """Retorna el datetime del dato mas viejo y el mas nuevo.

    Args:
        symbol (srt): Simbolo que se desea conseguir los datos (BTCUSDT)
        kline_size (str): Indica es tipo de periodo de los datos, los valores pueden ser: "1m", "5m", "1h", "1d". 
        data (df): df de datos ya creado anteriormente.
        source (str): Origen de los datos, siempre Binance

    Returns:
        Tuple: los datetime (old, new)
    """
    if len(data) > 0:
        # hay que pasar una fecha Unix
        str_time=str(data["date_myUTC"].iloc[-1])
        parse_time=parser.parse(str_time)
        post_oldtime=timedelta(minutes=binsizes[kline_size]) #tiempo despues de la ultima data, for not repeat  
        old=datetime.utcfromtimestamp(parse_time.timestamp())+post_oldtime

        loge.info(f"""old: {old}""")
    
    elif source == "binance": 
        old = datetime.strptime(
            '1 Jan 2017', '%d %b %Y'
            )# si no hay data y la fuente es binance la fecha vieja es del 2017
        loge.info(f"""old: {old}""")

    if source == "binance": 
        new=datetime.utcfromtimestamp(
            binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0]/1000
            )
        loge.info(f"""new: {new}""")
        #new = pd.to_datetime(binance_client.get_klines(symbol=symbol, interval=kline_size)[-1][0], unit='ms')

    return old, new

def get_all_binance(symbol:str, kline_size:str, save = False):
    """Genera un dataframe con todos los datos historicos posibles de un simbolo.

    Args:
        symbol (str): Simbolo que se desea conseguir los datos (BTCUSDT)
        kline_size (str): Indica es tipo de periodo de los datos, los valores pueden ser: "1m", "5m", "1h", "1d".
        save (bool, optional): Idica si se guarda o no el df en formato .pickle. Defaults to False.

    Returns:
        df: Dataframe de los datos historicos para el simbolo indicado.
    """
    filename = '%s-%s-data.pickle' %(symbol, kline_size)

    if os.path.isfile(filename): # si consigue el archivo lo lee
        data_df = pd.read_pickle(filename)
        loge.info(f"""filename conseguido: {filename}""")

    else: 
        data_df = pd.DataFrame() # si no crea el df
        loge.info(f"""filename no conseguido: {filename}""")

    oldest_point, newest_point = minutes_of_new_data(
        symbol, kline_size, data_df, source = "binance"
        ) # obtiene los datetime de old y new data

    delta_min = (newest_point - oldest_point).total_seconds()/60 # funcion unica para la resta entre dos datetime, obtiene los minutos

    available_data = math.ceil(
        delta_min/binsizes[kline_size]
        ) # Retorna en cantida de tiempo de data diponible para cargar
    
    loge.info(f"""
    oldest_point: {oldest_point}
    newest_point: {newest_point} 
    delta_min: {delta_min} mins
    available_data: {available_data} 5m flags""")

    if oldest_point == datetime.strptime('1 Jan 2017', '%d %b %Y'): # si la data mas vieja es la indicada entonces imprime cuanta data hay disponible para bajar.
        print(
            'Downloading all available %s data for %s. Be patient..!' % (kline_size, symbol)
            )
    else: 
        print(
            'Downloading %d minutes of new data available for %s, i.e. %d instances of %s data.' % (delta_min, symbol, available_data, kline_size)
            )

    klines = binance_client.get_historical_klines(
        symbol, kline_size, oldest_point.strftime("%d %b %Y %H:%M:%S"), 
        newest_point.strftime("%d %b %Y %H:%M:%S")) # obtiene los datos del simbol desde oldest to newest
    
    loge.info(f"""Colectando datos dentro de estas dos fechas:
    oldest_point.strftime: {oldest_point.strftime('%d %b %Y %H:%M:%S')} UNIX
    newest_point.strftime: {newest_point.strftime('%d %b %Y %H:%M:%S')} UNIX""")

    data = pd.DataFrame(klines, columns = [
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 
        'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore']) # cosntruye el data frame con los datos

    data['date_myUTC'] = data['timestamp'].apply(lambda x: datetime.fromtimestamp(x/1000))
    
    if len(data_df) > 0: # si hay data existente crea un df temp y la agrga a la data existentente
        temp_df = pd.DataFrame(data)
        temp_df.set_index('timestamp', inplace=True)
        data_df = pd.concat([data_df,temp_df])

    else: 
        data_df = data
        data_df.set_index('timestamp', inplace=True)
    
    
    if save: #Si activamos el save guarga el documento
        data_df.to_pickle(filename)
    print('All caught up..!')
    return data_df

if __name__ == "__main__":
    get_all_binance("BTCUSDT","5m",True)