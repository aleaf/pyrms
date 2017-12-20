import numpy as np


prmsdtypes = {int: 1, float: 2, str: 4,
              np.int32: 1, np.int64: 1}
dtypes = {v:k for k, v in prmsdtypes.items()}
fmt = {1: '%d', 2: '%.16f', 4: '%s'}