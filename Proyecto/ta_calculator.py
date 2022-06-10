import pandas_ta as ta
import pandas as pd



# TA computers
def ta_rsi_14_5(df_symbol):
    df_symbol=pd.concat([df_symbol,df_symbol.ta.rsi(length=14),
    df_symbol.ta.rsi(length=5)], axis=1)
    return df_symbol
def ta_stoch(df_symbol):
    df_symbol=pd.concat([df_symbol,df_symbol.ta.stoch()], axis=1)
    return df_symbol
def ta_cci20(df_symbol):
    df_symbol=pd.concat([df_symbol,df_symbol.ta.cci(length=20)], axis=1)
    return df_symbol
def ta_adx(df_symbol):
    df_symbol=pd.concat([df_symbol,df_symbol.ta.adx(length=14)], axis=1)
    return df_symbol
def ta_ao(df_symbol):
    df_symbol=pd.concat([df_symbol,df_symbol.ta.ao()], axis=1)
    return df_symbol

def ta_all_occillators(df_symbol):
    df_symbol=ta_adx(df_symbol)
    df_symbol=ta_rsi_14_5(df_symbol)
    df_symbol=ta_ao(df_symbol)
    df_symbol=ta_cci20(df_symbol)
    df_symbol=ta_stoch(df_symbol)
    return df_symbol