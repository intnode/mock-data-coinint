import talib as ta
import numpy as np
import pandas as pd
import copy
from typing import Sequence, Optional, Union, Callable
from numbers import Number
from itertools import compress
from tradingnode.utils import shift_elements, rolling_sum
from tradingnode.mathematic_functions import PeriodMAX, PeriodMIN
from numpy.typing import NDArray

def replace_eval_str(input_str, df_name):
  return_str = input_str
  for ind in ['Open','High','Close','Low','Volume','Constant']:
    return_str = return_str.replace(f"{ind}(",f"{ind}({df_name},")
  return return_str

## Data ##

def Open(data : pd.DataFrame, offset : int = 0) -> NDArray:
  """_summary_
  Get the Open price of each row (bar) from input dataframe of OHLCV with selected {offset} row to shifting backwards

  Args:
      data (pd.DataFrame): dataframe of OHLCV
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      NDArray: Array of Open price after shifting {offset} rows backwards
  """
  return shift_elements(data.Open,offset)

def High(data : pd.DataFrame, offset : int = 0) -> NDArray:
  """_summary_
  Get the High price of each row (bar) from input dataframe of OHLCV with selected {offset} row to shifting backwards

  Args:
      data (pd.DataFrame): dataframe of OHLCV
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      NDArray: Array of High price after shifting {offset} rows backwards
  """
  return shift_elements(data.High,offset)

def Close(data : pd.DataFrame, offset : int = 0) -> NDArray:
  """_summary_
  Get the Close price of each row (bar) from input dataframe of OHLCV with selected {offset} row to shifting backwards

  Args:
      data (pd.DataFrame): dataframe of OHLCV
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      NDArray: Array of Close price after shifting {offset} rows backwards
  """
  return shift_elements(data.Close,offset)

def Low(data : pd.DataFrame, offset : int = 0) -> NDArray:
  """_summary_
  Get the Low price of each row (bar) from input dataframe of OHLCV with selected {offset} row to shifting backwards

  Args:
      data (pd.DataFrame): dataframe of OHLCV
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      NDArray: Array of Low price after shifting {offset} rows backwards
  """
  return shift_elements(data.Low,offset)

def Volume(data : pd.DataFrame, offset : int = 0) -> NDArray:
  """_summary_
  Get the Volume of each row (bar) from input dataframe of OHLCV with selected {offset} row to shifting backwards

  Args:
      data (pd.DataFrame): dataframe of OHLCV
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      NDArray: Array of Volume after shifting {offset} rows backwards
  """
  return shift_elements(data.Volume,offset)

def Constant(data : Union[Sequence,NDArray,pd.Series,pd.DataFrame], number : float, offset=0) -> NDArray:
  """_summary_
  Get the array of constant values with same size as input data

  Args:
      data (Union[Sequence,NDArray,pd.Series,pd.DataFrame]): input sequence of (usually are Open, High, Low or Close).
      number (float): constant that use for each element of the output array.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of constant
  """
  return shift_elements(np.array([number]*len(data)),offset)

## Indicator ##

def SMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Simple Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Simple Moving Average after shifting {offset} rows backwards
  """
  return shift_elements(ta.SMA(data, period),offset)

def EMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Exponential Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Exponential Moving Average after shifting {offset} rows backwards
  """
  return shift_elements(ta.EMA(data, period),offset)

def WMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Weighted Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Weighted Moving Average after shifting {offset} rows backwards
  """
  return shift_elements(ta.WMA(data, period),offset)

def HMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Hull Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Weighted Moving Average after shifting {offset} rows backwards
  """
  hma = ta.WMA(2*ta.WMA(data, period/2)-ta.WMA(data, period),int(np.floor(np.sqrt(period))))
  return shift_elements(hma,offset)


def DEMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Double Exponential Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Double Exponential Moving Average after shifting {offset} rows backwards
  """
  return shift_elements(ta.DEMA(data, period),offset)

def TEMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Triple Exponential Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Triple Exponential Moving Average after shifting {offset} rows backwards
  """
  return shift_elements(ta.TEMA(data, period),offset)

def TRIMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Triangular Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Triangular Moving Average after shifting {offset} rows backwards
  """
  return shift_elements(ta.TRIMA(data, period),offset)

def TRIMA(data : Union[Sequence,NDArray,pd.Series], period : int = 9, offset :int=0) -> NDArray:
  """_summary_
  Get the Triangular Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Triangular Moving Average after shifting {offset} rows backwards
  """
  return shift_elements(ta.TRIMA(data, period),offset)

def VWMA(volume : Union[Sequence,NDArray,pd.Series], data : Union[Sequence,NDArray,pd.Series], 
         period : int = 20, offset :int=0) -> NDArray:
  """_summary_
  Get the Volume Weighted Moving Average from input sequence with selected {offset} row to shifting backwards

  Args:
      volume (Union[Sequence,NDArray,pd.Series]): input sequence of volume.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 20.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Triangular Moving Average after shifting {offset} rows backwards
  """
  PxV = data*volume
  vwma = rolling_sum(PxV,period)/rolling_sum(volume,period)
  return shift_elements(vwma,offset)

def RSI(data : Union[Sequence,NDArray,pd.Series], period : int = 14, offset :int=0) -> NDArray:
  """_summary_
  Get the Relative Stregth Index from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate moving average. Default is 14.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Relative Stregth Index after shifting {offset} rows backwards
  """
  return shift_elements(ta.RSI(data, period),offset)

def MACD(data : Union[Sequence,NDArray,pd.Series], fastperiod : int = 12, slowperiod : int = 26,
         signalperiod :int = 9 , offset :int=0) -> NDArray:
  """_summary_
  Get the Moving Average Convergence Divergence from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      fastperiod (int): number of fastperiod to calculate MACD. Default is 12.
      slowperiod (int): number of slowperiod to calculate MACD. Default is 26.
      signalperiod (int): number of signalperiod to calculate MACD signal. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Moving Average Convergence Divergence after shifting {offset} rows backwards
  """
  return shift_elements(ta.MACD(data,fastperiod,slowperiod,signalperiod)[0],offset)

def MACD_signal(data : Union[Sequence,NDArray,pd.Series], fastperiod : int = 12, slowperiod : int = 26,
         signalperiod :int = 9 , offset :int=0) -> NDArray:
  """_summary_
  Get the Moving Average Convergence Divergence Signal from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      fastperiod (int): number of fastperiod to calculate MACD. Default is 12.
      slowperiod (int): number of slowperiod to calculate MACD. Default is 26.
      signalperiod (int): number of signalperiod to calculate MACD signal. Default is 9.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Moving Average Convergence Divergence Signal after shifting {offset} rows backwards
  """
  return shift_elements(ta.MACD(data,fastperiod,slowperiod,signalperiod)[1],offset)

def UBB(data : Union[Sequence,NDArray,pd.Series], period : int = 20, dev : float = 2, offset : int=0) -> NDArray:
  """_summary_
  Get the Upper bound of Bollinger Bands from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate Bollinger Bands. Default is 20.
      dev (float): multiplier to calculate the Bollinger Bands. Default is 2.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Upper bound of Bollinger Bands after shifting {offset} rows backwards
  """
  return shift_elements(ta.BBANDS(data,period,dev,dev)[0],offset)

def MBB(data : Union[Sequence,NDArray,pd.Series], period : int = 20, dev : float = 2, offset : int=0) -> NDArray:
  """_summary_
  Get the Middle of Bollinger Bands from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate Bollinger Bands. Default is 20.
      dev (float): multiplier to calculate the Bollinger Bands. Default is 2.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Middle bound of Bollinger Bands after shifting {offset} rows backwards
  """
  return shift_elements(ta.BBANDS(data,period,dev,dev)[1],offset)

def LBB(data : Union[Sequence,NDArray,pd.Series], period : int = 20, dev : float = 2, offset : int=0) -> NDArray:
  """_summary_
  Get the Lower bound of Bollinger Bands from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate Bollinger Bands. Default is 20.
      dev (float): multiplier to calculate the Bollinger Bands. Default is 2.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Lower bound of Bollinger Bands after shifting {offset} rows backwards
  """
  return shift_elements(ta.BBANDS(data,period,dev,dev)[2],offset)

def MOM(data : Union[Sequence,NDArray,pd.Series], period : int = 10, offset :int=0) -> NDArray:
  """_summary_
  Get the Momentum from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate Momentum. Default is 10.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Momentum after shifting {offset} rows backwards
  """
  return shift_elements(ta.MOM(data,period),offset)

def BBP(high : Union[Sequence,NDArray,pd.Series],
        low : Union[Sequence,NDArray,pd.Series],
        data : Union[Sequence,NDArray,pd.Series], 
        period : int = 13, offset :int=0) -> NDArray:
  """_summary_
  Get the Bull Bear Power from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open, High, Low or Close).
      period (int): number of period to calculate Momentum. Default is 13.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Bull Bear Power after shifting {offset} rows backwards
  """
  ema = ta.EMA(data, period)
  bull_power = high - ema
  bear_power = low - ema
  bbp = bull_power+bear_power
  return shift_elements(bbp,offset)

def BullPower(high : Union[Sequence,NDArray,pd.Series],
              data : Union[Sequence,NDArray,pd.Series], 
              period : int = 13, offset :int=0) -> NDArray:
  """_summary_
  Get the Bull Power from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of (usually are Open or Close).
      period (int): number of period to calculate Momentum. Default is 13.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Bull Power after shifting {offset} rows backwards
  """
  ema = ta.EMA(data, period)
  bull_power = high - ema
  return shift_elements(bull_power,offset)

def BearPower(low : Union[Sequence,NDArray,pd.Series],
              data : Union[Sequence,NDArray,pd.Series], 
              period : int = 13, offset :int=0) -> NDArray:
  """_summary_
  Get the Bear Power from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      period (int): number of period to calculate Momentum. Default is 13.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Bear Power after shifting {offset} rows backwards
  """
  ema = ta.EMA(data, period)
  bear_power = low - ema
  return shift_elements(bear_power,offset)

def SAR(high : Union[Sequence,NDArray,pd.Series],
        low : Union[Sequence,NDArray,pd.Series], 
        acceleration : float = 0.02, maximum : float = 0.2, offset :int=0) -> NDArray:
  """_summary_
  Get the Parabolic SAR from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      acceleration (float): acceleration of SAR. Default is 0.02
      maximum (float): maximum of SAR. Default is 0.2
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Parabolic SAR after shifting {offset} rows backwards
  """
  return shift_elements(ta.SAR(high,low,acceleration,maximum),offset)

def CCI(high : Union[Sequence,NDArray,pd.Series],
        low : Union[Sequence,NDArray,pd.Series], 
        data : Union[Sequence,NDArray,pd.Series], 
        period : int = 14, offset :int=0) -> NDArray:
  """_summary_
  Get the Commodity Channel Index (CCI) from input sequence with selected {offset} row to shifting backwards
  CCI = (AveP - SMA_of_AveP) / (0.015 * Mean Deviation) where AveP = Average Price = (High + Low + Price) / 3

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      period (int): number of period to calculate CCI. Default is 14.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of CCI after shifting {offset} rows backwards
  """
  return shift_elements(ta.CCI(high,low,data,period),offset)

def STOCH_K(high : Union[Sequence,NDArray,pd.Series],
          low : Union[Sequence,NDArray,pd.Series], 
          data : Union[Sequence,NDArray,pd.Series], 
          k_fastperiod : int = 14, k_slowperiod : int = 3,
          d_slowperiod : int = 3, offset :int=0) -> NDArray:
  """_summary_
  Get the Stochastic %D from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      k_fastperiod (int): fast period to calculate Stochastic %K. Default is 14.
      k_slowperiod (int): slow period to calculate Stochastic %K. Default is 3.
      d_fastperiod (int): fast period to calculate Stochastic %D. Default is 3.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of  Stochastic %K after shifting {offset} rows backwards
  """
  return shift_elements(ta.STOCH(high,low,data,fastk_period=k_fastperiod,slowk_period=k_slowperiod,slowd_period=d_slowperiod),offset)[0]

def STOCH_D(high : Union[Sequence,NDArray,pd.Series],
          low : Union[Sequence,NDArray,pd.Series], 
          data : Union[Sequence,NDArray,pd.Series], 
          k_fastperiod : int = 14, k_slowperiod : int = 3,
          d_slowperiod : int = 3, offset :int=0) -> NDArray:
  """_summary_
  Get the Stochastic %D from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      k_fastperiod (int): fast period to calculate Stochastic %K. Default is 14.
      k_slowperiod (int): slow period to calculate Stochastic %K. Default is 3.
      d_fastperiod (int): fast period to calculate Stochastic %D. Default is 3.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of  Stochastic %D after shifting {offset} rows backwards
  """
  return shift_elements(ta.STOCH(high,low,data,fastk_period=k_fastperiod,slowk_period=k_slowperiod,slowd_period=d_slowperiod),offset)[1]

def STOCHRSI_K(
          data : Union[Sequence,NDArray,pd.Series], 
          rsi_period : int = 14,
          k_period : int = 3,
          d_period : int = 3, 
          offset :int=0) -> NDArray:
  """_summary_
  Get the Stochastic RSI %D from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of data (usually are Open, Close).
      rsi_period (int): rsi to calculate Stochastic RSI. Default is 14.
      k_period (int): fast period to calculate Stochastic %K. Default is 3.
      d_period (int): fast period to calculate Stochastic %D. Default is 3.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Stochastic RSI %D after shifting {offset} rows backwards
  """
  return shift_elements(ta.STOCHRSI(data,timeperiod=rsi_period,fastk_period=k_period,fastd_period=d_period),offset)[0]

def STOCHRSI_D(
          data : Union[Sequence,NDArray,pd.Series], 
          rsi_period : int = 14,
          k_period : int = 3,
          d_period : int = 3, 
          offset :int=0) -> NDArray:
  """_summary_
  Get the Stochastic RSI %D from input sequence with selected {offset} row to shifting backwards

  Args:
      data (Union[Sequence,NDArray,pd.Series]): input sequence of data (usually are Open, Close).
      rsi_period (int): rsi to calculate Stochastic RSI. Default is 14.
      k_period (int): fast period to calculate Stochastic %K. Default is 3.
      d_period (int): fast period to calculate Stochastic %D. Default is 3.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Stochastic RSI %D after shifting {offset} rows backwards
  """
  return shift_elements(ta.STOCHRSI(data,timeperiod=rsi_period,fastk_period=k_period,fastd_period=d_period),offset)[1]

def WILL_R(high : Union[Sequence,NDArray,pd.Series],
          low : Union[Sequence,NDArray,pd.Series], 
          data : Union[Sequence,NDArray,pd.Series], 
          period : int = 14, offset :int=0) -> NDArray:
  """_summary_
  Get the Williams' %R from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      period (int): period to calculate Williams' %R. Default is 14.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Williams' %R after shifting {offset} rows backwards
  """
  return shift_elements(ta.WILLR(high,low,data,timeperiod=period),offset)

def ADX(high : Union[Sequence,NDArray,pd.Series],
          low : Union[Sequence,NDArray,pd.Series], 
          data : Union[Sequence,NDArray,pd.Series], 
          period : int = 14, offset :int=0) -> NDArray:
  """_summary_
  Get the Average Directional Movement Index (ADX) from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      period (int): period to calculate ADX. Default is 14.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Directional Movement Index (ADX) after shifting {offset} rows backwards
  """
  return shift_elements(ta.ADX(high,low,data,timeperiod=period),offset)

def UO(high : Union[Sequence,NDArray,pd.Series],
       low : Union[Sequence,NDArray,pd.Series], 
       data : Union[Sequence,NDArray,pd.Series], 
       period1 : int = 7, period2 : int = 14, period3 : int = 28, offset :int=0) -> NDArray:
  """_summary_
  Get the Ultimate Oscillator (UO) from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      period1 (int): period1 to calculate UO. Default is 7.
      period2 (int): period2 to calculate UO. Default is 14.
      period3 (int): period3 to calculate UO. Default is 28.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Ultimate Oscillator (UO) after shifting {offset} rows backwards
  """
  return shift_elements(ta.ULTOSC(high,low,data,timeperiod1=period1,timeperiod2=period2,timeperiod3=period3),offset)

def Ichimoku_C(high : Union[Sequence,NDArray,pd.Series], 
             low : Union[Sequence,NDArray,pd.Series], 
             conversion_period : int = 9,
             baseline_period : int = 26,
             leading_period : int = 52,
             lagging_period : int = 26,
             offset : int = 0) -> NDArray :
  """_summary_
  Get the Ichimoku conversion line from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      conversion_period (int): conversion_period to calculate Ichimoku Cloud. Default is 9.
      baseline_period (int): baseline_period to calculate Ichimoku Cloud. Default is 26.
      leading_period (int): leading_period to calculate Ichimoku Cloud. Default is 52.
      lagging_period (int): lagging_period to calculate Ichimoku Cloud. Default is 26.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Ichimoku conversion line after shifting {offset} rows backwards
  """
  c_period_high = PeriodMAX(high, conversion_period)
  c_period_low = PeriodMIN(low, conversion_period)
  conversion_line = (c_period_high + c_period_low)/2
  return shift_elements(conversion_line,offset)

def Ichimoku_B(high : Union[Sequence,NDArray,pd.Series], 
             low : Union[Sequence,NDArray,pd.Series], 
             conversion_period : int = 9,
             baseline_period : int = 26,
             leading_period : int = 52,
             lagging_period : int = 26,
             offset : int = 0) -> NDArray :
  """_summary_
  Get the Ichimoku baseline from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      conversion_period (int): conversion_period to calculate Ichimoku Cloud. Default is 9.
      baseline_period (int): baseline_period to calculate Ichimoku Cloud. Default is 26.
      leading_period (int): leading_period to calculate Ichimoku Cloud. Default is 52.
      lagging_period (int): lagging_period to calculate Ichimoku Cloud. Default is 26.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of baseline after shifting {offset} rows backwards
  """
  b_period_high = PeriodMAX(high, baseline_period)
  b_period_low = PeriodMIN(low, baseline_period)
  baseline = (b_period_high + b_period_low)/2
  return shift_elements(baseline,offset)

def Ichimoku_LA(high : Union[Sequence,NDArray,pd.Series], 
             low : Union[Sequence,NDArray,pd.Series], 
             conversion_period : int = 9,
             baseline_period : int = 26,
             leading_period : int = 52,
             lagging_period : int = 26,
             offset : int = 0) -> NDArray :
  """_summary_
  Get the Ichimoku Leading Span A from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      conversion_period (int): conversion_period to calculate Ichimoku Cloud. Default is 9.
      baseline_period (int): baseline_period to calculate Ichimoku Cloud. Default is 26.
      leading_period (int): leading_period to calculate Ichimoku Cloud. Default is 52.
      lagging_period (int): lagging_period to calculate Ichimoku Cloud. Default is 26.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Leading Span A  after shifting {offset} rows backwards
  """
  c_period_high = PeriodMAX(high, conversion_period)
  c_period_low = PeriodMIN(low, conversion_period)
  conversion_line = (c_period_high + c_period_low)/2
  b_period_high = PeriodMAX(high, baseline_period)
  b_period_low = PeriodMIN(low, baseline_period)
  baseline = (b_period_high + b_period_low)/2
  leading_span_a = shift_elements((conversion_line + baseline) / 2, lagging_period)
  return shift_elements(leading_span_a,offset)

def Ichimoku_LB(high : Union[Sequence,NDArray,pd.Series], 
             low : Union[Sequence,NDArray,pd.Series], 
             conversion_period : int = 9,
             baseline_period : int = 26,
             leading_period : int = 52,
             lagging_period : int = 26,
             offset : int = 0) -> NDArray :
  """_summary_
  Get the Ichimoku Leading Span B from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      conversion_period (int): conversion_period to calculate Ichimoku Cloud. Default is 9.
      baseline_period (int): baseline_period to calculate Ichimoku Cloud. Default is 26.
      leading_period (int): leading_period to calculate Ichimoku Cloud. Default is 52.
      lagging_period (int): lagging_period to calculate Ichimoku Cloud. Default is 26.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Leading Span B after shifting {offset} rows backwards
  """
  lb_period_high = PeriodMAX(high, leading_period)
  lb_period_low = PeriodMIN(low, leading_period)
  leading_span_b =shift_elements((lb_period_high + lb_period_low)/2, baseline_period)
  return shift_elements(leading_span_b,offset)

def Ichimoku_LS(high : Union[Sequence,NDArray,pd.Series], 
             low : Union[Sequence,NDArray,pd.Series], 
             data : Union[Sequence,NDArray,pd.Series],
             conversion_period : int = 9,
             baseline_period : int = 26,
             leading_period : int = 52,
             lagging_period : int = 26,
             offset : int = 0) -> NDArray :
  """_summary_
  Get the Ichimoku Lagging span from input sequence with selected {offset} row to shifting backwards

  Args:
      high (Union[Sequence,NDArray,pd.Series]): input sequence of High.
      low (Union[Sequence,NDArray,pd.Series]): input sequence of Low.
      data (Union[Sequence,NDArray,pd.Series]): input sequence of price (usually are Open, Close).
      conversion_period (int): conversion_period to calculate Ichimoku Cloud. Default is 9.
      baseline_period (int): baseline_period to calculate Ichimoku Cloud. Default is 26.
      leading_period (int): leading_period to calculate Ichimoku Cloud. Default is 52.
      lagging_period (int): lagging_period to calculate Ichimoku Cloud. Default is 26.
      offset (int): number of rows to shift backwards. Default is 0.

  Returns:
      Sequence: Array of Lagging span after shifting {offset} rows backwards
  """
  lagging_span = shift_elements(data, -lagging_period)
  return shift_elements(lagging_span,offset)