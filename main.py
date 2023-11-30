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
df_stock_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_security_files_monthly_stock.sas7bdat'))

# Filter selected cols
ls_selected_cols_1 = ['GVKEY', 'LPERMCO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'ACTQ', 'ATQ',
                      'CEQQ', 'CHEQ', 'COGSQ', 'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ', 'LCTQ', 'LTQ',
                      'MIBTQ', 'NIQ', 'PIQ', 'PSTKQ', 'REQ', 'REVTQ', 'TXPQ', 'WCAPQ', 'CAPXY']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]
df_fundamentals_quarterly.rename(columns={'LPERMCO': 'PERMCO'}, inplace=True)

ls_selected_cols_2 = ['GVKEY', 'LPERMCO', 'DATADATE', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]
df_security_monthly.rename(columns={'LPERMCO': 'PERMCO'}, inplace=True)

ls_selected_cols_3 = ['PERMCO', 'DATE', 'ASK', 'BID', 'VOL', 'SHROUT']
df_stock_monthly = df_stock_monthly[ls_selected_cols_3]

# Sort raw data
df_fundamentals_quarterly = df_fundamentals_quarterly.sort_values(by=['PERMCO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)
df_security_monthly = df_security_monthly.sort_values(by=['PERMCO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)
df_stock_monthly = df_stock_monthly.sort_values(by=['PERMCO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Create year, quarter and month cols
df_fundamentals_quarterly['YEAR'] = df_fundamentals_quarterly['DATADATE'].dt.year.astype(float)
df_fundamentals_quarterly['QTR'] = df_fundamentals_quarterly['DATADATE'].dt.quarter.astype(float)
ls_selected_cols_1 = df_fundamentals_quarterly.columns.to_list()

df_security_monthly['YEAR'] = df_security_monthly['DATADATE'].dt.year.astype(float)
df_security_monthly['QTR'] = df_security_monthly['DATADATE'].dt.quarter.astype(float)
df_security_monthly['MTH'] = df_security_monthly['DATADATE'].dt.month.astype(float)
ls_selected_cols_2 = df_security_monthly.columns.to_list()

df_stock_monthly['YEAR'] = df_stock_monthly['DATE'].dt.year.astype(float)
df_stock_monthly['QTR'] = df_stock_monthly['DATE'].dt.quarter.astype(float)
df_stock_monthly['MTH'] = df_stock_monthly['DATE'].dt.month.astype(float)
ls_selected_cols_3 = df_stock_monthly.columns.to_list()

# Filter dates (min_year-max_year)
min_year = 1990
max_year = 2023
df_fundamentals_quarterly = df_fundamentals_quarterly[(df_fundamentals_quarterly['YEAR'] >= min_year) & (df_fundamentals_quarterly['YEAR'] <= max_year)]
df_security_monthly = df_security_monthly[(df_security_monthly['YEAR'] >= min_year) & (df_security_monthly['YEAR'] <= max_year)]
df_stock_monthly = df_stock_monthly[(df_stock_monthly['YEAR'] >= min_year) & (df_stock_monthly['YEAR'] <= max_year)]

# Filter stock exchanges (11: NYSE, 12: AMEX, 14: NASDAQ-NMS)
df_fundamentals_quarterly = df_fundamentals_quarterly[df_fundamentals_quarterly['EXCHG'].isin([11., 12., 14.])]
ls_permcos = df_fundamentals_quarterly['PERMCO'].unique().tolist()
df_security_monthly = df_security_monthly[df_security_monthly['PERMCO'].isin(ls_permcos)]
df_stock_monthly = df_stock_monthly[df_stock_monthly['PERMCO'].isin(ls_permcos)]

# Merge datasets
df_security_monthly['MERGEKEY'] = df_security_monthly['PERMCO'].astype(str) + '-' + df_security_monthly['YEAR'].astype(str) + '-' + df_security_monthly['MTH'].astype(str)
df_stock_monthly['MERGEKEY'] = df_stock_monthly['PERMCO'].astype(str) + '-' + df_stock_monthly['YEAR'].astype(str) + '-' + df_stock_monthly['MTH'].astype(str)
df_stock_monthly = df_stock_monthly.drop(columns=['PERMCO', 'DATE', 'YEAR', 'QTR', 'MTH'])
df_data = pd.merge(df_security_monthly, df_stock_monthly, on='MERGEKEY', how='inner')
# TODO: check merger, why more rows after inner join...






# Compute additional variables
df_stock_monthly['MID'] = (df_stock_monthly['ASK'] + df_stock_monthly['BID']) / 2
df_stock_monthly['SPREADPCT'] = (df_stock_monthly['ASK'] - df_stock_monthly['BID']) / df_stock_monthly['ASK']
df_stock_monthly['DVOL'] = df_stock_monthly['MID'] * df_stock_monthly['VOL']

# Filter out illiquid stocks
s_max_dvols = df_stock_monthly.groupby('PERMCO')['DVOL'].max()
df = pd.DataFrame(s_max_dvols)
df = df[df['DolVol'] >= 100000000]
ls_gvkeys = df.index.to_list()

# Summarize data
df_1 = df_fundamentals_quarterly.drop(columns=['GVKEY', 'LPERMCO', 'DATADATE', 'CONM', 'TIC', 'GSECTOR', 'LOC'])
df_summary_1 = fn.tab_summary(df_1)

df_2 = df_security_monthly.drop(columns=['GVKEY', 'LPERMCO', 'DATADATE'])
df_summary_2 = fn.tab_summary(df_2)

df_3 = df_stock_monthly.drop(columns=['PERMCO', 'DATE'])
df_summary_3 = fn.tab_summary(df_3)

# Missing values management [...]

