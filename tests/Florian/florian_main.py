from pathlib import Path
from tests.Florian.scripts.florian_parameters import paths
from tests.Florian.scripts.florian_parameters import paths_florian
import pandas as pd
import numpy as np



#file_data_1 = Path.joinpath(paths.get('Data'), 'qcyz6yksc03op9l6w.sas7bdat')
#fundamentals_quarterly_data = pd.read_sas(file_data_1)

file_data_2 = Path.joinpath(paths.get('data'), 'qpnseppzotdph6x8j.sas7bdat')
security_monthly_data = pd.read_sas(file_data_2)


security_monthly_data_filter = security_monthly_data.sort_values(by=['GVKEY', 'DATADATE'])
security_monthly_data_filter = security_monthly_data_filter.loc[(security_monthly_data_filter['DATADATE'] >= '1990-01-01')]
security_monthly_data_filter = security_monthly_data_filter.loc[(security_monthly_data_filter['CSHTRM']*security_monthly_data_filter['PRCCM'] >= 100000000)]
security_monthly_data_filter = security_monthly_data_filter.loc[(security_monthly_data_filter['EXCHG'].isin([11,14]))]
security_monthly_data_filter = security_monthly_data_filter.loc[(security_monthly_data_filter['FIC'] == bytes('USA', 'utf-8'))]

security_monthly_data_filter = security_monthly_data_filter[['GVKEY','DATADATE', 'TIC', 'CONML', 'SECSTAT','GGROUP', 'GIND', 'GSECTOR', 'GSUBIND', 'IPODATE', 'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M']]




security_monthly_data_filter_2 = security_monthly_data_filter.loc[(security_monthly_data_filter['DATADATE'] < '1992-01-01')]
n = security_monthly_data_filter_2['GVKEY'].nunique()

n = security_monthly_data_filter['GVKEY'].nunique()
name = pd.DataFrame(np.unique(security_monthly_data_filter[['CONML']]))

