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
df_stock = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_security_files_monthly_stock.sas7bdat'))

# Filter selected cols
ls_selected_cols_1 = ['GVKEY', 'DATADATE', 'CONM', 'TIC', 'CIK', 'EXCHG', 'GSECTOR', 'LOC', 'ACTQ', 'ATQ',
                      'CEQQ', 'CHEQ', 'COGSQ', 'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ', 'LCTQ', 'LTQ',
                      'MIBTQ', 'NIMQ', 'NIQ', 'PIQ', 'PSTKQ', 'REQ', 'REVTQ', 'TEQQ', 'TXPQ', 'WCAPQ',
                      'CAPXY', 'CSHTRQ', 'MKVALTQ', 'PRCCQ']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]

ls_selected_cols_2 = ['GVKEY', 'DATADATE', 'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]

ls_selected_cols_3 = ['DATE', 'CUSIP', 'BID', 'ASK', 'VOL', 'SPREAD']
df_stock = df_stock[ls_selected_cols_3]

# Sort raw data
df_fundamentals_quarterly = df_fundamentals_quarterly.sort_values(by=['GVKEY', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)
df_security_monthly = df_security_monthly.sort_values(by=['GVKEY', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)

# Create fiscal year and quarter cols
df_fundamentals_quarterly['FYEAR'] = df_fundamentals_quarterly['DATADATE'].dt.year.astype(float)
df_fundamentals_quarterly['FQTR'] = df_fundamentals_quarterly['DATADATE'].dt.quarter.astype(float)
ls_selected_cols_1 = ls_selected_cols_1[:2] + ['FYEAR', 'FQTR'] + ls_selected_cols_1[2:]
df_fundamentals_quarterly = df_fundamentals_quarterly.reindex(columns=ls_selected_cols_1)

df_security_monthly['FYEAR'] = df_security_monthly['DATADATE'].dt.year.astype(float)
df_security_monthly['FQTR'] = df_security_monthly['DATADATE'].dt.quarter.astype(float)
ls_selected_cols_2 = ls_selected_cols_2[:2] + ['FYEAR', 'FQTR'] + ls_selected_cols_2[2:]
df_security_monthly = df_security_monthly.reindex(columns=ls_selected_cols_2)

# Filter dates (min_year-max_year)
min_year = 1990
max_year = 2023
df_fundamentals_quarterly = df_fundamentals_quarterly[(df_fundamentals_quarterly['FYEAR'] >= min_year) & (df_fundamentals_quarterly['FYEAR'] <= max_year)]
df_security_monthly = df_security_monthly[(df_security_monthly['FYEAR'] >= min_year) & (df_security_monthly['FYEAR'] <= max_year)]

# Filter stock exchanges (11: NYSE, 12: AMEX, 14: NASDAQ-NMS)
df_fundamentals_quarterly = df_fundamentals_quarterly[df_fundamentals_quarterly['EXCHG'].isin([11., 12., 14.])]
ls_gvkeys = df_fundamentals_quarterly['GVKEY'].unique()
df_security_monthly = df_security_monthly[df_security_monthly['GVKEY'].isin(ls_gvkeys)]



df_fundamentals_quarterly['DolVol'] = df_fundamentals_quarterly['']

df_security_monthly['DolVol'] = df_security_monthly['CSHTRM'] * df_security_monthly['PRCCM']




# Summarize data
df_1 = df_fundamentals_quarterly.drop(columns=['GVKEY', 'DATADATE', 'CONM', 'TIC', 'CIK', 'GSECTOR', 'LOC'])
df_summary_1 = fn.tab_summary(df_1)

df_2 = df_security_monthly.drop(columns=['GVKEY', 'DATADATE'])
df_summary_2 = fn.tab_summary(df_2)


AUM = 10AUM
2%*AUM <= 10%*(DolVol / 21)
# Filter liquidity

df_fundamentals_quarterly[df_fundamentals_quarterly['FYEAR'] == 1990]
df_security_monthly[df_security_monthly['FYEAR'] == 1990 & (df_security_monthly['DolVol'] >= df_security_monthly['DolVol'].median())]
# Merge
# Missing values management
print(df_security_monthly['DolVol'].median())

df_fundamentals_quarterly

df_security_monthly[df_security_monthly['']]

df_security_monthly['DolVol']

max_values = df_security_monthly.groupby('GVKEY')['DolVol'].max()
df = pd.DataFrame(max_values)
df = df[df['DolVol'] >= 100000000]
ls_gvkeys = df.index.to_list()

df_security_monthly = df_security_monthly[df_security_monthly['GVKEY'].isin(ls_gvkeys)]
df_fundamentals_quarterly = df_fundamentals_quarterly[df_fundamentals_quarterly['GVKEY'].isin(ls_gvkeys)]
ls_gvkeys = max_values