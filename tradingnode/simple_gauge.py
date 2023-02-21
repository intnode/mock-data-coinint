import sys
from datetime import datetime as dt
import multiprocessing as mp
from tradingnode.indicators import *
from typing import Sequence, Optional, Union, Callable, List

def dict_to_eval_str(input_dict : dict) -> str:
  eval_str = ""
  for keys,values in input_dict.items():
    eval_str += f"{keys}={values},"
  return eval_str[:-1]

def get_moving_average_signal(data: Union[Sequence,NDArray,pd.Series], ind: dict):
  value = list(ind.values())[0]
  ma = eval(f"value['function'](Close(data,0),{dict_to_eval_str(value['param'])})")
  close = Close(data,0)
  if ma[-1] < close[-1]:
    return ma[-1], 1
  elif ma[-1] > close[-1]:
    return ma[-1], -1
  else:
    return ma[-1], 0

def get_rsi_signal(data: Union[Sequence,NDArray,pd.Series], ind: dict):
  value = list(ind.values())[0]
  rsi = eval(f"value['function'](Close(data,0),{dict_to_eval_str(value['param'])})")
  if rsi[-1] < 20 and rsi[-2] < rsi[-1]:
    return rsi[-1], 1
  elif rsi[-1] > 80 and rsi[-2] > rsi[-1]:
    return rsi[-1], -1
  else:
    return rsi[-1], 0

def get_mom_signal(data: Union[Sequence,NDArray,pd.Series], ind: dict):
  value = list(ind.values())[0]
  mom = eval(f"value['function'](Close(data,0),{dict_to_eval_str(value['param'])})")
  if mom[-2] < mom[-1]:
    return mom[-1], 1
  elif mom[-2] > mom[-1]:
    return mom[-1], -1
  else:
    return mom[-1], 0

def get_macd_signal(data: Union[Sequence,NDArray,pd.Series], ind: dict):
  macd = eval(f"ind['MACD']['function'](Close(data,0),{dict_to_eval_str(ind['MACD']['param'])})")
  macd_signal = eval(f"ind['MACD_signal']['function'](Close(data,0),{dict_to_eval_str(ind['MACD_signal']['param'])})")
  if macd[-1] > macd_signal[-1]:
    return [macd[-1],macd_signal[-1]] , 1
  elif macd[-1] < macd_signal[-1]:
    return [macd[-1],macd_signal[-1]], -1
  else:
    return [macd[-1],macd_signal[-1]], 0

def get_bband_signal(data: Union[Sequence,NDArray,pd.Series], ind: dict):
  ubb = eval(f"ind['UBB']['function'](Close(data,0),{dict_to_eval_str(ind['UBB']['param'])})")
  lbb = eval(f"ind['LBB']['function'](Close(data,0),{dict_to_eval_str(ind['LBB']['param'])})")
  close = Close(data,0)
  if close[-1] < lbb[-1]:
    return [ubb[-1],lbb[-1]], 1
  elif close[-1] > ubb[-1]:
    return [ubb[-1],lbb[-1]], -1
  else:
    return [ubb[-1],lbb[-1]], 0

def get_cci_signal(data: Union[Sequence,NDArray,pd.Series], ind: dict):
  cci = eval(f"ind['CCI']['function'](High(data),Low(data),Close(data),{dict_to_eval_str(ind['CCI']['param'])})")
  if cci[-1] < -100 and cci[-3] > cci[-2] and cci[-2] < cci[-1]:
    return cci[-1], 1
  elif cci[-1] > 100 and cci[-3] < cci[-2] and cci[-2] > cci[-1]:
    return cci[-1], 1
  else:
    return cci[-1], 0

def get_sar_signal(data: Union[Sequence,NDArray,pd.Series], ind: dict):
  sar = eval(f"ind['SAR']['function'](High(data),Low(data),{dict_to_eval_str(ind['SAR']['param'])})")
  open = data.Open
  if sar[-1] < open[-1]:
    return sar[-1], 1
  elif sar[-1] > open[-1]:
    return sar[-1], -1
  else:
    return sar[-1], 0

def gauge_conversion(gauge):
  if -1 <= gauge < -0.6:
    return "strong_sell"
  elif -0.6 <= gauge < -0.2:
    return "sell"
  elif -0.2 <= gauge <= 0.2:
    return "neutral"
  elif 0.2 < gauge <= 0.6:
    return "buy"
  elif 0.6 < gauge <= 1:
    return "strong_buy"

def simple_asset_gauge(data : pd.DataFrame, indicator : dict) -> List:
  signal_dict = {}
  for key, value in indicator.items():
    func = value["condition"]
    ma_value, signal = func(data,value["indicator"])
    signal_dict[key] = {"value":ma_value, "signal":signal}
  gauge_val = np.mean([r['signal'] for r in signal_dict.values()])
  gauge_str = gauge_conversion(gauge_val)
  return gauge_str, gauge_val, signal_dict

def weighted_asset_gauge(data : pd.DataFrame, indicator : dict, weight : NDArray) -> List:
  assert np.sum(weight) - len(indicator) < 1e-4
  signal_dict = {}
  for key, value in indicator.items():
    func = value["condition"]
    ma_value, signal = func(data,value["indicator"])
    signal_dict[key] = {"value":ma_value, "signal":signal}
  gauge_val = np.mean(np.array([r['signal'] for r in signal_dict.values()])*weight)
  gauge_str = gauge_conversion(gauge_val)
  return gauge_str, gauge_val, signal_dict

moving_average_oscillator_weight = np.array([0.5/13]*13 + [0.5/6]*6)*19

indicator_dict = {
    "Exponential Moving Average (10)":{"indicator":{"EMA":{"function":EMA,"param":{"period":10}}},"condition": get_moving_average_signal},
    "Exponential Moving Average (20)":{"indicator":{"EMA":{"function":EMA,"param":{"period":20}}},"condition": get_moving_average_signal},
    "Exponential Moving Average (30)":{"indicator":{"EMA":{"function":EMA,"param":{"period":30}}},"condition": get_moving_average_signal},
    "Exponential Moving Average (50)":{"indicator":{"EMA":{"function":EMA,"param":{"period":50}}},"condition": get_moving_average_signal},
    "Exponential Moving Average (100)":{"indicator":{"EMA":{"function":EMA,"param":{"period":100}}},"condition": get_moving_average_signal},
    "Exponential Moving Average (200)":{"indicator":{"EMA":{"function":EMA,"param":{"period":200}}},"condition": get_moving_average_signal},
    "Simple Moving Average (10)":{"indicator":{"SMA":{"function":SMA,"param":{"period":10}}},"condition": get_moving_average_signal},
    "Simple Moving Average (20)":{"indicator":{"SMA":{"function":SMA,"param":{"period":20}}},"condition": get_moving_average_signal},
    "Simple Moving Average (30)":{"indicator":{"SMA":{"function":SMA,"param":{"period":30}}},"condition": get_moving_average_signal},
    "Simple Moving Average (50)":{"indicator":{"SMA":{"function":SMA,"param":{"period":50}}},"condition": get_moving_average_signal},
    "Simple Moving Average (100)":{"indicator":{"SMA":{"function":SMA,"param":{"period":100}}},"condition": get_moving_average_signal},
    "Simple Moving Average (200)":{"indicator":{"SMA":{"function":SMA,"param":{"period":200}}},"condition": get_moving_average_signal},
    "Hull Moving Average (9)":{"indicator":{"HMA":{"function":HMA,"param":{"period":9}}},"condition": get_moving_average_signal},
    "Relative Strength Index (14)" :{"indicator":{"RSI":{"function":RSI,"param":{"period":14}}},"condition": get_rsi_signal},
    "Momentum (10)" :{"indicator":{"MOM":{"function":MOM,"param":{"period":10}}},"condition": get_mom_signal},
    "MACD" : {"indicator":{"MACD":{"function":MACD,"param":{"fastperiod":12,"slowperiod":26,"signalperiod":9}},
                           "MACD_signal":{"function":MACD_signal,"param":{"fastperiod":12,"slowperiod":26,"signalperiod":9}}},
              "condition": get_macd_signal},
    "Bollinger Bands (14,2,2)" : {"indicator":{"UBB":{"function":UBB,"param":{"period":14,"dev":2}},
                           "LBB":{"function":LBB,"param":{"period":14,"dev":2}}},
              "condition": get_bband_signal},
    "Commodity Channel Index (20)" :{"indicator":{"CCI":{"function":CCI,"param":{"period":20}}},"condition": get_cci_signal},
    "Parabolic SAR" :{"indicator":{"SAR":{"function":SAR,"param":{"acceleration ":0.02,"maximum":0.2}}},"condition": get_sar_signal},  }