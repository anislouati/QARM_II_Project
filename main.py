# Import packages
from pathlib import Path
import numpy as np
import pandas as pd



# Project directories paths
paths = {'main': Path.cwd()}
paths.update({'data': Path.joinpath(paths.get('main'), 'data'),
              'output': Path.joinpath(paths.get('main'), 'output'),
              'scripts': Path.joinpath(paths.get('main'), 'scripts')})

# Import raw data
df_fundamentals_quarterly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))
df_security_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_security_monthly.sas7bdat'))
