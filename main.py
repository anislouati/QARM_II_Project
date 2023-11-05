# Import packages
import pandas as pd
import numpy as np
from pathlib import Path
from scripts.classes import paths



#file_data_1 = Path.joinpath(paths.get('Data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat')
#fundamentals_quarterly_data = pd.read_sas(file_data_1)

file_data_2 = Path.joinpath(paths.get('data'), 'crsp_compustat_merged_security_monthly.sas7bdat')
security_monthly_data = pd.read_sas(file_data_2)

#file_data_3 = Path.joinpath(paths.get('data'), 'crsp_security_files_monthly_stock.sas7bdat')
#security_monthly_data = pd.read_sas(file_data_3)
