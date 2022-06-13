from ta_calculator import *
import numpy as np

class Recommendation:
    buy = "long"
    strong_buy = "STRONG_BUY"
    sell = "short"
    strong_sell = "STRONG_SELL"
    neutral = "NEUTRAL"
    error = "ERROR"

class Compute:
    _df_symbol=None

    def __init__(self,df_symbol:pd.DataFrame):
        self._df_symbol=ta_all_occillators(df_symbol)

    def RSI(self)-> dict:
        """Compute Relative Strength Index
        Args:
            rsi (float): RSI value
            rsi1 (float): RSI[1] value
        Returns:
            string: "BUY", "SELL", or "NEUTRAL"
        """
        if self._df_symbol.columns.isin(["RSI_5","RSI_14"]).max():
            rsi= self._df_symbol.RSI_14.iloc[-1]
            rsi1=self._df_symbol.RSI_5.iloc[-1]

            if (rsi < 30 and rsi1 < rsi):
                recomendation= Recommendation.buy
            elif (rsi > 70 and rsi1 > rsi):
                recomendation= Recommendation.sell
            else:
                recomendation= Recommendation.neutral

            return {"RSI":recomendation}
        
        return {"RSI":np.nan}

    def Stoch(self) -> dict:
        """Compute Stochastic
        Args:
            k (float): Stoch.K value
            d (float): Stoch.D value
            k1 (float): Stoch.K[1] value
            d1 (float): Stoch.D[1] value
        Returns:.
            string: "BUY", "SELL", or "NEUTRAL"
        """
        if self._df_symbol.columns.isin(['STOCHk_14_3_3', 'STOCHd_14_3_3']).max():
            
            d= self._df_symbol['STOCHd_14_3_3'].iloc[-1]
            d1= self._df_symbol['STOCHd_14_3_3'].iloc[-2]
            k= self._df_symbol['STOCHk_14_3_3'].iloc[-1]
            k1= self._df_symbol['STOCHk_14_3_3'].iloc[-2]

            if (k < 20 and d < 20 and k > d and k1 < d1):
                recomendation= Recommendation.buy
            elif (k > 80 and d > 80 and k < d and k1 > d1):
                recomendation= Recommendation.sell
            else:
                recomendation= Recommendation.neutral
            
            return {"Stoch":recomendation}
        
        return {"Stoch":np.nan}

    def CCI20(self):
        """Compute Commodity Channel Index 20
        Args:
            cci20 (float): CCI20 value
            cci201 ([type]): CCI20[1] value
        Returns:
            string: "BUY", "SELL", or "NEUTRAL"
        """
        if self._df_symbol.columns.isin(['CCI_20_0.015']).max():
            
            cci20= self._df_symbol['CCI_20_0.015'].iloc[-1]
            cci201= self._df_symbol['CCI_20_0.015'].iloc[-2]
            
            if (cci20 < -100 and cci20 > cci201):
                recomendation= Recommendation.buy
            elif (cci20 > 100 and cci20 < cci201):
                recomendation= Recommendation.sell
            else:
                recomendation= Recommendation.neutral
            return {"CCI20":recomendation}
        
        return {"CCI20":np.nan}

    def ADX(self):
        """Compute Average Directional Index
        Args:
            adx (float): ADX value
            adxpdi (float): ADX+DI value
            adxndi (float): ADX-DI value
            adxpdi1 (float): ADX+DI[1] value
            adxndi1 (float): ADX-DI[1] value
        Returns:
            string: "BUY", "SELL", or "NEUTRAL"
        """
        if self._df_symbol.columns.isin(['ADX_14','DMP_14', 'DMN_14']).max():
            
            adx= self._df_symbol['ADX_14'].iloc[-1]
            adxpdi= self._df_symbol['DMP_14'].iloc[-1]
            adxpdi1= self._df_symbol['DMP_14'].iloc[-2]
            adxndi= self._df_symbol['DMN_14'].iloc[-1]
            adxndi1= self._df_symbol['DMN_14'].iloc[-2]

            if (adx > 20 and adxpdi1 < adxndi1 and adxpdi > adxndi):
                recomendation= Recommendation.buy
            elif (adx > 20 and adxpdi1 > adxndi1 and adxpdi < adxndi):
                recomendation= Recommendation.sell
            else:
                recomendation= Recommendation.neutral
            return {"ADX":recomendation}
        
        return {"ADX":np.nan}

    def AO(self):
        """Compute Awesome Oscillator
        Args:
            ao (float): AO value
            ao1 (float): AO[1] value
            ao2 (float): AO[2] value
        Returns:
            string: "BUY", "SELL", or "NEUTRAL"
        """

        if self._df_symbol.columns.isin(['AO_5_34']).max():
                      
            ao= self._df_symbol['AO_5_34'].iloc[-1]
            ao1= self._df_symbol['AO_5_34'].iloc[-2]
            ao2= self._df_symbol['AO_5_34'].iloc[-3]

            if (ao > 0 and ao1 < 0) or (ao > 0 and ao1 > 0 and ao > ao1 and ao2 > ao1):
                recomendation= Recommendation.buy
            elif (ao < 0 and ao1 > 0) or (ao < 0 and ao1 < 0 and ao < ao1 and ao2 < ao1):
                recomendation= Recommendation.sell
            else:
                recomendation= Recommendation.neutral
            return {"AO":recomendation}
        
        return {"AO":np.nan}

    def all_occillators(self) -> dict:
        d={}
        #occs=[self.AO(),self.RSI(),self.ADX(), self.CCI20(),self.Stoch()]
        occs=[self.AO(),self.RSI(),self.ADX(), self.CCI20(),self.Stoch()]
        for occ in occs:
            pop=occ.popitem()
            d[pop[0]]=pop[1]
        return d

    def apply_ta_recomendation(self):
        # capturar la señal
        # optener la fecha de publicación
        # capturar el simbolo
        # tener el historial del simbolo
        # slice el hitorial 1y atars de la publicacion
        # pasar los datos a formato de días
        # calcular las recomendaciones
        # guardar en db
        pass