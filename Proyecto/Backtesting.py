from datetime import datetime
from Binance_get_data import get_all_binance
import pandas as pd

class Backtecting:

    def __init__(self) -> None:
        pass

    def get_data_about_symbol(symbol=str,path=None):
        
        df_symbol_data=get_all_binance(symbol=symbol,save=True)

        return df_symbol_data

    def slice_df_by_date(df_symbol_data,date_start:datetime,date_end:datetime=None):

        if date_end==None:
            mask:pd.Series=df_symbol_data["date_myUTC"]
            mask=mask.between(str(date_start),str(df_symbol_data["date_myUTC"].iloc[-1]))
            temp_df_symbol=df_symbol_data[mask]
            return temp_df_symbol
        
        mask:pd.Series=df_symbol_data["date_myUTC"]
        mask=mask.between(str(date_start),str(date_end))
        temp_df_symbol=df_symbol_data[mask]
        return temp_df_symbol

    def find_in_OHLC_line(operate_data,OHCL_line):

        if operate_data in OHCL_line:
            return True
        return False
    
    def backtest_operate():
        pass