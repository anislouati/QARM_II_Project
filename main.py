# Import packages
import pandas as pd
import numpy as np
from pathlib import Path
from scripts.classes import paths



#file_data_1 = Path.joinpath(paths.get('Data'), 'CRSP_Compustat_Merged_Fundamentals_Quarterly.sas7bdat')
#fundamentals_quarterly_data = pd.read_sas(file_data_1)

file_data_2 = Path.joinpath(paths.get('data'), 'CRSP_Compustat_Merged_Security_Monthly.sas7bdat')
security_monthly_data = pd.read_sas(file_data_2)

#file_data_3 = Path.joinpath(paths.get('data'), 'CRSP_Security_Files_Monthly_Stock.sas7bdat')
#security_monthly_data = pd.read_sas(file_data_3)
