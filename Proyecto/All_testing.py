import pandas as pd
from Backtesting import Backtecting
from mongo_db_crud import Mongodb
from Prophettesting import Prophettesting
from ta_recomendation import apply_ta_recomendation

# aplicar todos los testing
# aplicar el backtesting
# aplicar el prophettesting
# aplicar el ta_recomendation

def apply_all_testing(db_name,host=None,pass_sygnal_backtest=False,pass_sygnal_prophet=False,pass_sygnal_recomendation=False):
    """
        Aplica todos los testing a los datos de la db.

            host: dirección del cluster de mongo.
            db_name: nombre de la db a la que se quiere conectar.
            pass_sygnal_backtest: si es True aplicará el backtesting.
            pass_sygnal_prophet: si es True aplicará el prophettesting.
            pass_sygnal_recomendation: si es True aplicará el ta_recomendation.
    """

    #host = "mongodb://localhost:27017/"
    #db_name = "back_prueba"
    db = Mongodb(host).set_db(db_name)
    data = db.signals.find()
    list_data = list(data)
    df_sygnal_data = pd.DataFrame(list_data)
    #mask=~df_sygnal_data["error_backtesting"].isna()
    #df_sygnal_data[mask]
    df_sygnal_data = df_sygnal_data.sort_values('symbol').reset_index()
    #df_sygnal_data = df_sygnal_data.iloc[6:7,:].reset_index()
    Backtecting().backtest_operate(df_sygnal_data, db_name,pass_sygnal=pass_sygnal_backtest)
    # Prophettesting().apply_prophettesting(df_sygnal_data, db_name,pass_sygnal=pass_sygnal_prophet)
    apply_ta_recomendation(df_sygnal_data=df_sygnal_data,pass_sygnal=pass_sygnal_recomendation)

if __name__== "__main__":
    host = "mongodb://localhost:27017/"
    db_name = "db_pasanti"
    apply_all_testing(host=host,db_name=db_name,pass_sygnal_backtest=True, pass_sygnal_recomendation=True, pass_sygnal_prophet=True)