# Import packages
from pathlib import Path
from scripts.functions import paths
import numpy as np
import pandas as pd
import scripts.functions as fn

# Project settings
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)


# %%
# **************************************************
# *** Branch: DATA MANAGEMENT                    ***
# **************************************************

# Import raw data
df_fundamentals_quarterly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))
df_security_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_security_monthly.sas7bdat'))

# Filter selected cols

# Filter sele
# Filter selected col
ls_selected_cols_1 = ['GVKEY', 'DATADATE', 'FYEARQ', 'FQTR', 'CONM', 'TIC', 'CIK', 'EXCHG', 'GSECTOR', 'LOC',
                      'ACTQ', 'ATQ', 'CEQQ', 'CHEQ', 'COGSQ', 'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ',
                      'LCTQ', 'LTQ', 'MIBTQ', 'NIMQ', 'NIQ', 'PIQ', 'PSTKQ', 'REQ', 'REVTQ', 'TEQQ',
                      'TXPQ', 'WCAPQ', 'CAPXY', 'CSHTRQ', 'MKVALTQ', 'PRCCQ']
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
df_fundamentals_quarterly['FYEAR'] = df_fundamentals_quarterly['DATADATE'].dt.year.astype(float)
df_fundamentals_quarterly['FQTR'] = df_fundamentals_quarterly['DATADATE'].dt.quarter.astype(float)

df_security_monthly['FYEARQ'] = df_security_monthly['DATADATE'].dt.year.astype(float)
df_security_monthly['FQTR'] = df_security_monthly['DATADATE'].dt.quarter.astype(float)

ls_selected_cols_2 = ['GVKEY', 'DATADATE', 'FYEARQ', 'FQTR', 'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]






# Filter dates (min_year-)
min_year = 1990
max_year = 2023
df_fundamentals_quarterly = df_fundamentals_quarterly[(df_fundamentals_quarterly['FYEARQ'] >= min_year) & (df_fundamentals_quarterly['FYEARQ'] <= max_year)]
df_security_monthly = df_security_monthly[(df_security_monthly['FYEARQ'] >= min_year) & (df_security_monthly['FYEARQ'] <= max_year)]

df_fundamentals_quarterly[df_fundamentals_quarterly['FYEARQ'] == 2024]
# Summarize data
df_1 = df_fundamentals_quarterly.drop(columns=['GVKEY', 'DATADATE', 'CONM', 'TIC', 'CIK', 'GSECTOR', 'LOC'])
df_summary_1 = fn.tab_summary(df_1)

df_2 = df_security_monthly.drop(columns=['GVKEY', 'DATADATE'])
df_summary_2 = fn.tab_summary(df_2)

# Filter liquidity
# Filter stock exchanges
# Merge
# Missing values management
