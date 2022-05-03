from datetime import datetime
from logging_base import loge
from Binance_get_data import get_all_binance
import pandas as pd
from mongo_db_crud import Mongodb 

class Backtecting:

    def __init__(self) -> None:
        pass

    def get_data_about_symbol(self,symbol=str,path=None):
        """Esta funcion retorna o actualiza el historial de precios de un simbolo determinado.

        Args:
            symbol (STR, optional): Idica la moneda a la cual se le va aplicar el proceso. Defaults to str.
            path (STR, optional): Direccions del historial de la moneda. Defaults to None.

        Returns:
            Data frame: Data frame del historial de precios del simbolo. 
        """
        df_symbol_data=get_all_binance(symbol=symbol,save=True,kline_size="5m")

        loge.info(f"Se creo el symbol_data {symbol}")
        return df_symbol_data

    def slice_df_by_date(self, df_symbol_data:pd.DataFrame,date_start:datetime,date_end:datetime=None):

        """Retorna un data frame sesgado entre dos fechas indicadas.

        Args:
            symbol_data (DataFrame): Idica el DataFrame al cual se quiere sesgar. Defaults to DataFrame.
            date_start (datetime): Tiempo más lejano para iniciar el sesgado. Defaults to Datetime.
            date_start (datetime, optional): Tiempo mas cercano para terminar el sesgado, si se coloca defaul este tiempo es simplemente la fecha del ultimo dato guardado. Defaults to None.

        
        Returns:
            Dataframe: Dataframe sesgado entre dos fechas dadas.
        """

        if date_end==None: # si no hay fecha de fin
            
            mask:pd.Series=df_symbol_data["date_myUTC"]

            loge.info(f"""date_start_by_sygnal: {str(date_start)}""") 
            loge.info(f"""last_date_symbol: {str(df_symbol_data["date_myUTC"].iloc[-1])}""") 
            
            mask=mask.between(date_start,df_symbol_data["date_myUTC"].iloc[-1]) # Usa la fecha del ultimo dato guardado - Between no funcionaba con los str???? no se por que.
            
            temp_df_symbol:pd.DataFrame=df_symbol_data[mask]
            loge.info(f"""symbol_data slice only start {str(date_start)} - {temp_df_symbol["date_myUTC"].iloc[-1]}""")
            return temp_df_symbol
        
        loge.info(f"""date_start: {str(date_start)}""") 
        loge.info(f"""date_end: {str(date_end)}""") 
        mask:pd.Series=df_symbol_data["date_myUTC"]
        mask=mask.between(date_start,date_end)
        temp_df_symbol=df_symbol_data[mask]
        loge.info(f"symbol_data slice {str(date_start)} - {str(date_end)}")
        return temp_df_symbol

    def find_in_OHLC_line(self,operates_data,df_symbol_data:pd.DataFrame)-> dict:
        
        """Consigue y compara los datos de operación con los precios indicados por el historial de precios.

        Args:
            operates_data: Idica la moneda a la cual se le va aplicar el proceso. Defaults to str.
            path (STR, optional): Direccions del historial de la moneda. Defaults to None. 
        
        Returns:
            Dict: Retorna un dictionary que contine los datos de operación evaluado y junto a este la fecha en la que el precio considió.
        """

        dates={}

        df_symbol_data.loc[:,["open","high","low","close"]]=df_symbol_data.loc[:,["open","high","low","close"]].astype(float) # Convertir lso datos numericos del precio en numeros flotantes.
        
        for operate in operates_data:        
            
            #loge.info(f"""operate: {type(operate)}""") 
            #loge.info(f"""df_symbol_data["open"]: {type(df_symbol_data["open"].iloc[0])}""") 

            mask=(df_symbol_data["open"]>=operate) | (df_symbol_data["high"]>=operate) | (df_symbol_data["low"]>=operate) | (df_symbol_data["close"]>=operate)

            date=df_symbol_data[mask].iloc[0]["date_myUTC"] # El primer valor (tiempo mas lejano) que cumple la mask.

            if date:
                dates[operate]=date
            else:
                date[operate]=False

        return dates

    def update_backtesting(self,_id, tagname, set,host="mongodb://localhost:27017/", collection="signals"):
        
        """Actualiza automaticamente los datos en la base de datos.
        """
        
        db=Mongodb(host)
        Mongodb().update_by_id(collection,_id, tagname, set)
        
    
    def backtest_operate(self,df_sygnal_data:pd.DataFrame,data_base="DB_test"):
        
        """Ejecuta todo el proceso de backtesting

        arg:
            df_sygnal_data (DataFrame): Indica el dataframe del historial de precios  del simbolo de la operación. Defaults to DataFrame.
            data_base (STR, opcional): Indica el nombre de la base de datos a actualizar. Defaults to "DB_test"

        """
        
        for i in range(2):#len(df_sygnal_data)):
            
            # Get symbol data
            loge.info(f"""get symbol data nro: {i} {df_sygnal_data.loc[i,"symbol"]}""")
            
            df_symbol_data = self.get_data_about_symbol(df_sygnal_data.loc[i,"symbol"])
           
            # Get date entry
            date_start=df_sygnal_data.loc[i,"date"]
            
            temp_df_symbol=self.slice_df_by_date(df_symbol_data=df_symbol_data,date_start=date_start)
            entry_targets=df_sygnal_data.iloc[i]["entry_targets"]
            
            loge.info(f"""entry_targets: {entry_targets} Type:  {type(entry_targets)}""")

            dates_entry:dict=self.find_in_OHLC_line(operates_data=entry_targets, df_symbol_data=temp_df_symbol)
            loge.info(f"dates_entry: {dates_entry}")
        #    
            # Get date stoploss
            date_start=list(dates_entry.values())[0]
            temp_df_symbol=self.slice_df_by_date(df_symbol_data=temp_df_symbol,date_start=date_start)

            stop_targets=df_sygnal_data.iloc[i]["stop_targets"]
            loge.info(f"""stop_targets: {stop_targets} Type:  {type(stop_targets)}""")
            
            dates_stoploss:dict=self.find_in_OHLC_line(operates_data=stop_targets, df_symbol_data=temp_df_symbol)
            loge.info(f"dates_stoploss: {dates_stoploss}")
        #    
        #    #Get dates_profit
        #    dates_end=list(dates_stoploss.values())[0]
        #    temp_df_symbol=self.slice_df_by_date(df_symbol_data=temp_df_symbol,date_start=date_start,date_end=dates_end)
        #    dates_profit:dict=self.find_in_OHLC_line(operates_data=stop_targets, df_symbol_data=temp_df_symbol)
        #    loge.info(f"dates_profit: {dates_profit}")  
        #    # Update db
        #    _id=df_sygnal_data.loc[i,"symbol"]
        #    self.update_backtesting(_id,"dates_entry",dates_entry)
        #    self.update_backtesting(_id,"dates_stoploss",dates_stoploss)
        #    self.update_backtesting(_id,"dates_profit",dates_profit)
        #print("all line backteting")

if __name__== "__main__":

    host="mongodb://localhost:27017/"
    db_name="Back_prueba"
    db=Mongodb(host).set_db(db_name)
    data=db.signals.find()
    list_data = list(data)
    df_sygnal_data=pd.DataFrame(list_data)
    Backtecting().backtest_operate(df_sygnal_data,db_name)