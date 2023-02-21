import talib as ta
import numpy as np
import pandas as pd
from typing import Sequence, Union, List
from numpy.typing import NDArray
from .utils import shift_elements
from itertools import compress


## Mathematics Function ##

def MAX(*series : Union[Sequence,NDArray,pd.Series]) -> NDArray:
  """_summary_
  Input multiple series with the same size, find the maximum value of them along axis 0 (columns).

  Args:
      *series (Union[Sequence,NDArray,pd.Series]): input series

  Returns:
      NDArray: Array of max values along axis 0with the same length as input series.
  """
  return np.max([*series],axis=0)

def MIN(*series : Union[Sequence,NDArray,pd.Series]) -> NDArray:
  """_summary_
  Input multiple series with the same size, find the minimum value of them along axis 0 (columns).

  Args:
      *series (Union[Sequence,NDArray,pd.Series]): input series

  Returns:
      NDArray: Array of min values along axis 0with the same length as input series.
  """
  return np.min([*series],axis=0)

def PeriodMAX(series : Union[Sequence,NDArray,pd.Series],
              period : int) -> NDArray:
  """_summary_
  Input serie and number of period to find the maximum value when lookback after {period} rows.

  Args:
      series (Union[Sequence,NDArray,pd.Series]): input serie
      period (int) : number of periods to lookback

  Returns:
      NDArray: Array of max values along axis 0 after lookback for {period} rows.
  """
  return np.max([shift_elements(series,i) for i in range(period)], axis=0)

def PeriodMIN(series : Union[Sequence,NDArray,pd.Series],
              period : int) -> NDArray:
  """_summary_
  Input serie and number of period to find the minimum value when lookback after {period} rows.

  Args:
      series (Union[Sequence,NDArray,pd.Series]): input serie
      period (int) : number of periods to lookback

  Returns:
      NDArray: Array of min values along axis 0 after lookback for {period} rows.
  """
  return np.min([shift_elements(series,i) for i in range(period)], axis=0)

def ABS(series : Union[Sequence,NDArray,pd.Series]) -> NDArray:
  """_summary_
  Input serie and find the absolute value of each element.

  Args:
      series (Union[Sequence,NDArray,pd.Series]): input serie
      
  Returns:
      NDArray: Array of absolute values.
  """
  return np.abs(series)

def CEIL(series : Union[Sequence,NDArray,pd.Series]) -> NDArray:
  """_summary_
  Input serie and find the ceiling value of each element.

  Args:
      series (Union[Sequence,NDArray,pd.Series]): input serie

  Returns:
      NDArray: Array of ceiling values.
  """
  return np.ceil(series)

def FLOOR(series : Union[Sequence,NDArray,pd.Series]) -> NDArray:
  """_summary_
  Input serie and find the floor value of each element.

  Args:
      series (Union[Sequence,NDArray,pd.Series]): input serie

  Returns:
      NDArray: Array of floor values.
  """
  return np.floor(series)

def ROUND(series : Union[Sequence,NDArray,pd.Series]) -> NDArray:
  """_summary_
  Input serie and find the rounding value of each element.

  Args:
      series (Union[Sequence,NDArray,pd.Series]): input serie

  Returns:
      NDArray: Array of rounding values.
  """
  return np.round(series)


'''
def COUNTFROMLAST(condition: Sequence[bool], default=np.inf) -> int:
  """_summary_
  Return the number of rows since the input condition is 'True',
  if never, return 'default'
  Args:
      condition (Sequence[bool]): Sequence of boolean
      default: value to return if no 'True' condition before that row. Defaults to np.inf.

  Returns:
      int: Number of rows since the last 'True'
  """
  return next(compress(range(len(condition)), reversed(condition)), default)
'''