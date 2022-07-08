
#%%
import itertools # para el manejo de varias configuraciones, Mas obciones para iteradores.
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
#from matplotlib import pyplot as plt
from datetime import date
#%%
#
#import matplotlib
#from plotly import offline as py # otro graficador
#
#plt.rcParams["figure.figsize"] = (20,10)





class ToolsProphet:

    def __init__(self) -> None:
        pass

    def to_days_data(self,df:pd.DataFrame,column_time:str,column_value:str="close") -> pd.DataFrame:

      df_temp=df.copy()
      df_temp[column_time]=pd.to_datetime(df_temp[column_time])
      df_temp.set_index(column_time,drop=False,inplace=True) # combierte la columna en index y mantiene la columna 
      return df_temp

    def to_data_for_prophet(self,df:pd.DataFrame,column_value:str)-> pd.DataFrame:
      df_temp=df.copy()
      df_for_prophet=pd.DataFrame()
      df_for_prophet["y"]=pd.to_numeric(df_temp[column_value],errors="coerce")
      df_for_prophet["ds"]=df_temp.index
      df_for_prophet["ds"]=pd.to_datetime(df_for_prophet["ds"],errors="coerce")
      return df_for_prophet

    def train_and_test(self,df:pd.DataFrame, hours_test:int) -> tuple:
      df_train=df[:len(df) - hours_test]
      df_test=df[len(df) - hours_test:]

      print(f'df_train len: {len(df_train["ds"])}')
      print(f'df_train time range: {df_train["ds"].min()} - {df_train["ds"].max()}')
      print(f'df_test time range: {df_test["ds"].min()} - {df_test["ds"].max()}')
      return df_train, df_test

    def apply_prophet(self,df_train, times_future, best_params:dict=None):
    
      m=Prophet()
      if best_params:
        m=Prophet(**best_params)
    
      m.fit(df_train)
      df_future=m.make_future_dataframe(periods=times_future, freq="5min")
      print(f'df_future time range: {df_future["ds"].min()} - {df_future["ds"].max()}')
      forecast_future=m.predict(df_future)
      print(f'forecast_future time range: {forecast_future["ds"].min()} - {forecast_future["ds"].max()}')
      forecast_future["name_day"]=forecast_future.ds.dt.day_name()
      forescast_days=forecast_future[len(forecast_future)-times_future:]["trend"]
      forescast_trend="long"
      if forescast_days.iloc[0]>forescast_days.iloc[-1]:
        forescast_trend="short"
      return forecast_future, forescast_trend

    def plot_prediction(self,forecast_future:pd.DataFrame, df_train:pd.DataFrame, df_test:pd.DataFrame=[], x_range_show:list=None, figsize:list=None,saved_name:str=None):
      # Plot the predictions
      plt.rcParams.update({'font.size': 14, 'figure.figsize': [18, 10]})
      list_legends=['y', 'trend','Yhat',"Yhat_lower","yhat_upper"]
      
      if figsize:
        plt.rcParams.update({'font.size': 14, 'figure.figsize': figsize})

      ax = df_train.plot(x='ds', y='y', style='b-', grid=True)
      #ax = df_test.plot(x='ds', y='y', style='m-', grid=True)
      #x_range_show=[date(2021,1,1),date(2022,5,15)]

      # Plot the predictions
      ax.plot(forecast_future['ds'], forecast_future.trend, marker='.')
      ax.plot(forecast_future['ds'], forecast_future.yhat, marker='.')
      ax.plot(forecast_future['ds'], forecast_future.yhat_lower, marker='.')
      ax.plot(forecast_future['ds'], forecast_future.yhat_upper, marker='.')
      if len(df_test):
        ax.plot(df_test['ds'], df_test["y"])
        list_legends.append("test")

      ax.set_xlabel("date")
      ax.set_ylabel("USD")
      ax.legend(list_legends)
      if x_range_show:
        ax.set_xlim(x_range_show)
      if saved_name!= None:
        plt.savefig(saved_name)
      plt.show()

    def get_best_hyperparameters(self,df_train:pd.DataFrame,initial_days:int=364, period:int=1, horizon:int=1, param_grid:dict=None)-> dict:
      if param_grid==None:
          param_grid = {
            #"growth":['linear','logistic'],
            'changepoint_prior_scale': [2.5],  # default 0.05 Increasing changepoint_prior_scale will make the trend more flexible and result in overfitting. Decreasing the changepoint_prior_scale will make the trend less flexible and result in underfitting.
            'seasonality_prior_scale': [10, 0.01],  # default 10
            'seasonality_mode': ["additive", "multiplicative"],
            #'daily_seasonality':[True,False]
            }
      
      all_params = [dict(zip(param_grid.keys(), v))
                  for v in itertools.product(*param_grid.values())]
      maes = []  # Store the MAEs for each params here
      mapes = []  # Store the MAEs for each params here
      rmses = []  # Store the MAEs for each params here
      counter = 1
    # Use cross validation to evaluate all parameters
      for params in all_params:
        m = Prophet(**params,)
        #m.add_seasonality()
        print(counter)
        counter = counter + 1

        m.fit(df_train)  # Fit model with given params

        df_cv = cross_validation(
            m, initial=f"{initial_days}"+' days', period=f"{period}"+' days', horizon=f"{horizon}"+' hours', parallel="processes")
        df_p = performance_metrics(df_cv, rolling_window=5, )

        rmses.append(df_p['rmse'].values[0])
        mapes.append(df_p['mape'].values[0])
        maes.append(df_p['mae'].values[0])

      tuning_results = pd.DataFrame(all_params)

      tuning_results['rmse'] = rmses
      tuning_results['mape'] = mapes
      tuning_results['mae'] = maes
      print(tuning_results.sort_values("mae"))
      best_params = all_params[np.argmin(maes)]
      print(f"best params: {best_params}, maes: {maes[np.argmin(maes)]}, mapes: {mapes[np.argmin(maes)]}, rmses: {rmses[np.argmin(maes)]}, ind: {np.argmin(maes)}")
      
      score={}
      score["mae"]=maes[np.argmin(maes)]
      score["rmse"]=rmses[np.argmin(rmses)]
      score["mape"]=mapes[np.argmin(mapes)]
      
      return best_params,score

    def get_lowerupper_day(self,forecast_future:pd.DataFrame)-> dict:
    
      days_value=forecast_future.groupby("name_day").agg({"weekly_lower":["mean"]})
      days_value=days_value["weekly_lower"].sort_values("mean")["mean"].to_dict()
      return days_value

#%%
if __name__== "__main__":


    df=pd.read_pickle("/home/joan/Documentos/Programacion/Python/Pasantias/BCHUSDT-5m-data.pickle")
    df=ToolsProphet().to_days_data(df=df, column_time="date_myUTC", column_value="close")
    df.sample(5)
#%%
 
    df=ToolsProphet().to_data_for_prophet(df=df, column_value="close")
#%%
    df_train, df_test= ToolsProphet().train_and_test(df=df, hours_test= 20)
#%%
    #best_params=ToolsProphet.get_best_hyperparameters(df_train=df_train,initial_days=1000,period=100,horizon=20)
    #best_params={'changepoint_prior_scale': 0.1, 'seasonality_prior_scale': 10, 'seasonality_mode': 'multiplicative'}
    best_params={'changepoint_prior_scale': 2.5, 'seasonality_prior_scale': 0.005, 'seasonality_mode': 'multiplicative'}
#%%
    forecast_future, forecast_trend=ToolsProphet().apply_prophet(df_train=df_train, times_future=20, best_params=None)
    print(forecast_trend)
#%%
    ToolsProphet.plot_prediction(df_train=df_train, df_test=df_test,forecast_future=forecast_future, saved_name="grafica",x_range_show=[date(2021,1,1),date(2022,5,15)])
#%%
    day_value=ToolsProphet.get_lowerupper_day(forecast_future)
    print(day_value)