import numpy as np
import pandas as pd
from typing import Union, Sequence, Sequence
from numpy.typing import NDArray

## utilility functions ##

def shift_elements(array : Union[Sequence,NDArray,pd.Series,pd.DataFrame], num : int, fill_value : float=np.nan) -> NDArray:
    result = np.empty_like(array)
    if num > 0:
        result[:num] = fill_value
        result[num:] = array[:-num]
    elif num < 0:
        result[num:] = fill_value
        result[:num] = array[-num:]
    else:
        result[:] = array
    return result

def rolling_sum(array : NDArray , n):
    if isinstance(array, pd.Series):
        array = array.to_numpy()
    cumsum = array.cumsum()
    cumsum[:n] = np.nan
    cumsum[n:] = cumsum[n:] - cumsum[:-n]
    return cumsum