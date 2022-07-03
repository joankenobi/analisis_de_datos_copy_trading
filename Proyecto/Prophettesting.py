# Vale esta clase debe:
# - Indicar el valor del dia en el que publicó la operación, si el dia suele ser bajo o alto.
# - Indicar la tendencia dada segun prophet usando el pasado hasta la fecha de publicación.
# - 

# from calendar import day_name, week
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os


# import ToolsProphet5min import *
from ToolsProphet import*
from Binance_get_data import get_all_binance
from Backtesting import Backtecting

from datetime import date, datetime, timedelta
from logging_base import loge
from mongo_db_crud import Mongodb

class Prophettesting:
    """Procesa la obtención de todos los datos relacionados con FB_prophet, como lo son la tendencia del forecast y las tendencias del día.

    Ademas guarda los parametros usados para el forecast.
    """

    def __init__(self) -> None:
        pass

    def get_date_range(self,df_sygnal_data: pd.DataFrame,i: int)-> datetime:
        """Retorna la fecha de publicacion de la señal

        Args:
            df_sygnal_data (pd.DataFrame): data frame que contiene todas las señales a procesar.
            i (_type_): indice de la señal evaluada.

        Returns:
            _type_: pandas.DataFrame

        """
        # Debe obtener las fechas para el df_train
        date=df_sygnal_data.loc[i,"date"]
        return date

    
    def get_symbol_data(self,df_sygnal_data: pd.DataFrame,i: int)-> pd.DataFrame:
        """Retorna los datos historicos del simbolo a evaluar, si no los consigue, los pide a Binance por medio de la Api.

        Args:
            df_sygnal_data (pd.DataFrame): data frame que contiene todas las señales a procesar.
            i (int): indice de la señal evaluada.

        Returns:
            _type_: pandas.DataFrame

        """

        # Debe revisar cual es la moneda
        loge.info(f"""i= {i} """)    
        symbol=df_sygnal_data.loc[i,"symbol"]
        loge.info(f"""symbol= {symbol} """)    
        # Ver si hay data de la misma
        filename = '%s-%s-data.pickle' %(symbol, "5m")

        if os.path.isfile(filename): # si consigue el archivo lo lee
            df_symbol = pd.read_pickle(filename)
            return df_symbol
        loge.info(f"""filename conseguido: {filename}""")
        # Si no hay, debe descargarla
        df_symbol=get_all_binance(symbol=symbol,kline_size="5m",save=True)
        # Esta data es la que hará de df_symbol
        return df_symbol

    def to_day_and_slice_time_for_period(self,df_symbol:pd.DataFrame, column_time:str,end_date:str,period:str="1Y",column_value="close")-> pd.DataFrame:
        """Pasa los datos historicos del simbolo a un periodo de tiempo de dias y aplica un corte desde la fecha dada hasta un periodo atars de esa fecha.
        Args:
            df_symbol (pd.DataFrame): data frame que contiene todo el dato historico del simbolo.
            i (int): indice de la señal evaluada.
            column_time (str): columna que contiene los datos de tiempo en el df.
            end_date (str): fecha final para realizar el corte.
            period (str): rango de tiempo para cortar antes de end_date. Si se coloca "1Y" el df solo mostrará desde end_dat hasta una año atrás. Default: "1Y"
            column_value (str): columna que contiene el valor principal para agrupar en periodo de 1 día. Default: "close"

        Returns:
            _type_: pandas.DataFrame

        """
 
        # debe picar la symbol_data dentro del date_range
        # Esta es definitivamente el df_train 
        #df_symbol[column_time]=pd.to_datetime(df_symbol[column_time])
        # pass to a day period
        loge.info("call prophet")
        prophet=ToolsProphet()
        loge.info("to days data")
        df_symbol=prophet.to_days_data(df=df_symbol,column_time=column_time, column_value=column_value)
        df_train=df_symbol[df_symbol[column_time]<=end_date].last(period)
        return df_train

    def get_public_day_status(self,df_sygnal_data:pd.DataFrame,i:int, day_value: dict)-> str:
        # Revisa el dia de la publicacion
        day_name=df_sygnal_data.loc[i,"date"].day_name()
        # Lo compara con el los day_value
        
        # capturar la fecha del dia siguiente de la publicacion
        next_day_name=df_sygnal_data.loc[i,"date"]+timedelta(days=1)
        # convertirlo en day_name
        next_day_name=next_day_name.day_name()
        # convertirlo en day_status
        next_day_status=day_value[next_day_name]
        day_status=day_value[day_name]
        # evaluar si day1 > day2 y determinar la tendencia.
        if next_day_status > day_status:
            trend="long"
        elif next_day_status < day_status:
            trend="short"
        else:
            trend="neutral"
        return trend
        # Lo guarda como estado del dia.


    def get_forecast_20_trend(self,df__sygnal_data:pd.DataFrame,i: int, df_train:pd.DataFrame):
        prophet=ToolsProphet()
        # pasar los datos a un formato prophet
        df_train=prophet.to_data_for_prophet(df=df__sygnal_data,column_value="close")
        # obtener los mejores hiperparametros
        best_params,score=prophet.get_best_hyperparameters(df_train=df_train,initial_days=59,period=2,horizon=1)
        # Obtiene la tendencia de los proximos 20 tiempos (5mins) segun prophet
        forecast_future, forecast_trend=prophet.apply_prophet(df_train=df_train, times_future=20, best_params=best_params)
        # Guardar esa info junto al sygnal_data
        return best_params,forecast_future,forecast_trend,score

    def apply_prophettesting(self,df_sygnal_data:pd.DataFrame,data_base="DB_test",pass_sygnal=False):

        #i=0
        #if i==0:
        for i in range(len(df_sygnal_data)):
            if ("Colocar lo que iba antes" in df_sygnal_data.iloc[i].dropna(inplace=False).index or "score" in df_sygnal_data.iloc[i].dropna(inplace=False).index) and pass_sygnal:
                
                loge.info(f"""se salto la señal ya testeada nro {i}""")    
                pass 
            
            else:    
                try:

                ### Get date range 
                    loge.info(f"""---Get date range """)    

                    date=self.get_date_range(df_sygnal_data,i)
                    loge.info(f"""date= {date} """)    

                ### Get symbol data
                    loge.info(f"""---Get symbol data """)    

                    df_symbol=self.get_symbol_data(df_sygnal_data,i)
                    loge.info(f"""df_symbol= {df_symbol.columns} """)    

                ### slice data
                    loge.info(f"""---slice data """)    

                    df_train=self.to_day_and_slice_time_for_period(df_symbol=df_symbol,column_time='date_myUTC', end_date=date, period="1440H",) # period="1440H = 60D
                    loge.info(f"""df_train= {df_train.shape} """)    

                ### apply prophet
                    loge.info(f"""---apply prophet """)    

                    best_params,forecast_future,forecast_trend,score=self.get_forecast_20_trend(df__sygnal_data=df_train,i=i,df_train=df_train)
                    loge.info(f"""forecast_future= {forecast_future.shape} """)    
                    loge.info(f"""forecast_trend= {forecast_trend} """)    

                ### get value_day
                    loge.info(f"""---get value_day """)    
                    day_value=ToolsProphet().get_lowerupper_day(forecast_future)
                    loge.info(f"""day_value= {day_value.items()} """)    

                ### compare value_day
                    loge.info(f"""---compare value_day """)    
                    trend_day=self.get_public_day_status(df_sygnal_data=df_sygnal_data,i=i,day_value=day_value)
                    #loge.info(f"""{day_name} = {trend_day} """)


                ### Update db
                    _id=df_sygnal_data.loc[i,"_id"]    
                    Backtecting().update_backtesting(_id,"forecast_trend",forecast_trend)
                    Backtecting().update_backtesting(_id,"day_value",day_value)
                    Backtecting().update_backtesting(_id,"trend_day",trend_day)
                    Backtecting().update_backtesting(_id,"best_params",best_params)
                    Backtecting().update_backtesting(_id,"score",score)
                    Backtecting().update_backtesting(_id,"error_prophettesting",np.nan)

                except Exception as e:
                    error_prophettesting=datetime.now()
                    loge.error(f"---error----signal:{df_sygnal_data.iloc[i].loc['message_link']}, {e}")
                    _id=df_sygnal_data.loc[i,"_id"]
                    Backtecting().update_backtesting(_id,"error_prophettesting",error_prophettesting)
                    pass
            
        print("all line prophettested.....")

if __name__ == "__main__":

    host = "mongodb://localhost:27017/"
    db_name = "back_prueba"
    db = Mongodb(host).set_db(db_name)
    data = db.signals.find()
    list_data = list(data)
    df_sygnal_data = pd.DataFrame(list_data)
    df_sygnal_data = df_sygnal_data.iloc[:2]
    Prophettesting().apply_prophettesting(df_sygnal_data, db_name,pass_sygnal=False)