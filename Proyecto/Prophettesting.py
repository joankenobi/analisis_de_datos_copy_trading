# Vale esta clase debe:
# - Indicar el valor del dia en el que publicó la operación, si el dia suele ser bajo o alto.
# - Indicar la tendencia dada segun prophet usando el pasado hasta la fecha de publicación.
# - 

import pandas as pd
import matplotlib.pyplot as plt



from ToolsProphet import *



from datetime import date, datetime, timedelta
from logging_base import loge
from mongo_db_crud import Mongodb

class Prophettesting:

    def __init__(self) -> None:
        pass

    def get_date_range(self,df_sygnal_data: pd.DataFrame,i):
        # Debe obtener las fechas para el df_train
        date=df_sygnal_data.loc[i,"date"]
        return date

    def get_sygnals_data():
        # Debe revisar cual es la moneda
        # Ver si hay data de la misma
        # Si no hay, debe descargarla
        # Esta data es la que hará de df_train
        pass

    def slice_data():
        # debe picar la symbol_data dentro del date_range
        # Esta es definitivamente el df_train 
        pass

    def get_public_day_status():
        # Revisa el dia de la publicacion
        # Lo compara con el los day_value
        # Lo guarda como estado del dia.
        pass

    def get_forecast_20_trend():
        # Obtiene la tendencia de los proximos 20 dias segun prophet
        # Guardar esa info junto al sygnal_data
        pass

    def apply_prophettesting(self,df_sygnal_data:pd.DataFrame,data_base="DB_test"):

        for i in range(len(df_sygnal_data)):

        ### Get date range 
            date=self.get_date_range(df_sygnal_data,i)
            loge.info(f"""date= {date} """)    
            loge.info(f"""date_type= {type(date)} """)    
        
        ### Get symbol data

            loge.info(
                f"""get symbol data nro: {i} {df_sygnal_data.loc[i,"symbol"]}""")

            #df_symbol_data = self.get_data_about_symbol(
            #    df_sygnal_data.loc[i, "symbol"])
#
            #is_long=df_sygnal_data.iloc[i]["is_long"]

        print("all line prophetteting.....")

if __name__ == "__main__":

    host = "mongodb://localhost:27017/"
    db_name = "back_prueba"
    db = Mongodb(host).set_db(db_name)
    data = db.signals.find()
    list_data = list(data)
    df_sygnal_data = pd.DataFrame(list_data)
    Prophettesting().apply_prophettesting(df_sygnal_data, db_name)