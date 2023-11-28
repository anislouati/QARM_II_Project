# Import packages
from pathlib import Path
import numpy as np
import pandas as pd
from scripts.functions import paths


# %%
# **************************************************
# *** Branch: DATA MANAGEMENT                    ***
# **************************************************

# Import raw data
df_fundamentals_quarterly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))
df_security_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_security_monthly.sas7bdat'))

# Filter selected cols
ls_selected_cols_1 = ['GVKEY', 'DATADATE', 'FYEARQ', 'FQTR', 'CONM', 'TIC', 'CIK', 'EXCHG', 'GSECTOR', 'LOC',
                      'ACTQ', 'ATQ', 'CEQQ', 'CHEQ', 'COGSQ', 'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ',
                      'LCTQ', 'LTQ', 'MIBTQ', 'NIMQ', 'NIQ', 'PIQ', 'PSTKQ', 'REQ', 'REVTQ', 'TEQQ',
                      'TXPQ', 'WCAPQ', 'CAPXY', 'CSHTRQ', 'MKVALTQ', 'PRCCQ']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]

ls_selected_cols_2 = ['GVKEY', 'DATADATE', 'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]

# Sort raw data
df_fundamentals_quarterly = df_fundamentals_quarterly.sort_values(by=['GVKEY', 'DATADATE'], ascending=[True, True])
df_security_monthly = df_security_monthly.sort_values(by=['GVKEY', 'DATADATE'], ascending=[True, True])

# Create year and quarter cols
df_security_monthly['FYEARQ'] = df_security_monthly['DATADATE'].dt.year.astype(float)
df_security_monthly['FQTR'] = df_security_monthly['DATADATE'].dt.quarter.astype(float)

ls_selected_cols_2 = ['GVKEY', 'DATADATE', 'FYEARQ', 'FQTR', 'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]

# Create year and quarter column
# Filter dates (

print(df_fundamentals_quarterly[['DATADATE', 'NIY']].isna().sum())
print(df_fundamentals_quarterly[['DATADATE', 'NIQ']].isna().sum())
print(df_fundamentals_quarterly['DATADATE'])
print(df_fundamentals_quarterly.columns)
print(df_fundamentals_quarterly.head(5))
print(df_security_monthly.tail(500))
print(df_fundamentals_quarterly['GSECTOR'].head(100))
print(df_fundamentals_quarterly['GPOA'])