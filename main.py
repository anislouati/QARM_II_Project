# Import packages
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from scripts.functions import paths
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle
import scripts.functions as fn
import warnings

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
ls_selected_cols_1 = ['LPERMNO', 'DATADATE', 'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR',
                      'ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ', 'REVTQ',
                      'WCAPQ', 'XINTQ', 'CAPXY']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]
df_fundamentals_quarterly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_2 = ['LPERMNO', 'DATADATE', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]
df_security_monthly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_3 = ['PERMNO', 'DATE', 'BID', 'ASK', 'VOL', 'SHROUT', 'SPRTRN']
df_stock_monthly = df_stock_monthly[ls_selected_cols_3]

# Create keys/identifiers (KEYQ, KEYM)
df_fundamentals_quarterly = fn.preprocessing_1(df_fundamentals_quarterly)
df_security_monthly = fn.preprocessing_1(df_security_monthly)
df_stock_monthly = fn.preprocessing_1(df_stock_monthly)

# Filter raw dates (min_year-max_year)
min_year = 1980
max_year = 2022
df_fundamentals_quarterly = df_fundamentals_quarterly[(df_fundamentals_quarterly['YEAR'] >= min_year) & (df_fundamentals_quarterly['YEAR'] <= max_year)]
df_security_monthly = df_security_monthly[(df_security_monthly['YEAR'] >= min_year) & (df_security_monthly['YEAR'] <= max_year)]
df_stock_monthly = df_stock_monthly[(df_stock_monthly['YEAR'] >= min_year) & (df_stock_monthly['YEAR'] <= max_year)]

# Filter stock exchanges (11: NYSE, 12: AMEX, 14: NASDAQ-NMS)
df_fundamentals_quarterly = df_fundamentals_quarterly[df_fundamentals_quarterly['EXCHG'].isin([11, 12, 14])]
ls_permnos = df_fundamentals_quarterly['PERMNO'].unique().tolist()
df_security_monthly = df_security_monthly[df_security_monthly['PERMNO'].isin(ls_permnos)]
df_stock_monthly = df_stock_monthly[df_stock_monthly['PERMNO'].isin(ls_permnos)]

# Sort data and reset index
df_fundamentals_quarterly = df_fundamentals_quarterly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
df_security_monthly = df_security_monthly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
df_stock_monthly = df_stock_monthly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Drop faulty FQTR and duplicates
df_fundamentals_quarterly = fn.preprocessing_2(df_fundamentals_quarterly)
df_security_monthly = fn.preprocessing_3(df_security_monthly)
df_stock_monthly = fn.preprocessing_3(df_stock_monthly)

# Checkpoint data
# df_fundamentals_quarterly.to_pickle(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'))
# df_security_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'))
# df_stock_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'), 'rb') as f:
    df_fundamentals_quarterly = pickle.load(f)
with open(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'), 'rb') as f:
    df_security_monthly = pickle.load(f)
with open(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'), 'rb') as f:
    df_stock_monthly = pickle.load(f)

# Merge datasets
df_fundamentals_quarterly = df_fundamentals_quarterly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYM'])
df_tmp = pd.merge(df_fundamentals_quarterly, df_security_monthly, on='KEYQ', how='inner')

df_stock_monthly = df_stock_monthly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ'])
df_data = pd.merge(df_stock_monthly, df_tmp, on='KEYM', how='inner')

# Fill missing dates with nans (by stock)
df_data = fn.preprocessing_4(df_data)
ls_selected_cols = ['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED', 'FQTR',
                    'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ',
                    'NIQ', 'PIQ', 'REQ', 'REVTQ', 'WCAPQ', 'XINTQ', 'CAPXY',
                    'PRCCM', 'TRT1M', 'BID', 'ASK', 'VOL', 'SHROUT', 'SPRTRN']
df_data = df_data[ls_selected_cols]
df_data = df_data.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Check filled data (by stock)
delta_months = (df_data.groupby('PERMNO')['DATE'].max().dt.to_period('M') - df_data.groupby('PERMNO')['DATE'].min().dt.to_period('M')).apply(attrgetter('n')) + 1
months_count = df_data.groupby('PERMNO')['DATE'].count()

pd_delta_months = pd.DataFrame()
pd_delta_months['Number of months'] = delta_months
pd_delta_months['Count of months'] = months_count
pd_delta_months['Check'] = delta_months - months_count

s_tmp = pd_delta_months['Check'].value_counts()
print('Stocks in dataset: {}'.format(len(df_data['PERMNO'].unique().tolist())))
print('Stocks with filled data: {}'.format(s_tmp[0]))

# Create/Modify variables
df_data = fn.preprocessing_5(df_data)
ls_selected_cols = ['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED', 'FQTR',
                    'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ',
                    'NIQ', 'PIQ', 'REQ', 'REVTQ', 'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ',
                    'PRCCM', 'TRT1M', 'BID', 'ASK', 'SPRDPCT', 'VOL', 'DVOL', 'SHROUT', 'SPRTRN']
df_data = df_data[ls_selected_cols]
df_data = df_data.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# ATTENTION: accounting data published in Q_t is available (out-of-sample) for investment decisions in Q_t_1
# Push forward fundamentals (out-of-sample) ==> Example: info published on 31/03 (Q_t) available starting 30/04 (Q_t_1)
df_data = fn.preprocessing_6(df_data)


# Checkpoint data
#df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)


# Create additional variables (fundamental metrics)
df_data = fn.preprocessing_7(df_data)

# Checkpoint data
#df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)

# %%
# **************************************************
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************

# Filter clean dates (min_year-max_year)
min_year = 1997
max_year = 2022
df_data = df_data[(df_data['YEAR'] >= min_year) & (df_data['YEAR'] <= max_year)]



# TODO: get_zscore(df_data, ls_vars) VAR_ZS

def get_ZS(df_data):
    df_out = df_data
    ls_vars = ['BE/ME', 'E/P', 'CF/P',
               'GPOA', 'ROE', 'ROA', 'CFOA', 'GMAR', 'ACC',
               'D_GPOA', 'D_ROE', 'D_ROA', 'D_CFOA', 'D_GMAR',
               'LEV', 'AZSCORE', 'NBETA',
               'CTRT1M']

    for var in ls_vars:
        df_out['RK_' + var] = df_out[var].rank(method='max', ascending=True)
    for var in ls_vars:
        df_out['ZS_' + var] = (df_out['RK_' + var] - df_out['RK_' + var].mean()) / df_out['RK_' + var].std()

    # Value
    ls_cols = [('ZS_' + var) for var in ['BE/ME', 'E/P', 'CF/P']]
    df_out['ZS_VAL'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Profitability
    ls_cols = [('ZS_' + var) for var in ['GPOA', 'ROE', 'ROA', 'CFOA', 'GMAR', 'ACC']]
    df_out['ZS_PROF'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Growth
    ls_cols = [('ZS_' + var) for var in ['D_GPOA', 'D_ROE', 'D_ROA', 'D_CFOA', 'D_GMAR']]
    df_out['ZS_GWTH'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Safety
    ls_cols = [('ZS_' + var) for var in ['LEV', 'AZSCORE', 'NBETA']]
    df_out['ZS_SAF'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Quality
    ls_cols = [('ZS_' + var) for var in ['PROF', 'GWTH', 'SAF']]
    df_out['ZS_QLT'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Momentum
    ls_cols = [('ZS_' + var) for var in ['CTRT1M']]
    df_out['ZS_MOM'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value and Quality
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT']]
    df_out['ZS_VAL_QLT'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value, Quality and Momentum
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'MOM']]
    df_out['ZS_VAL_QLT_MOM'] = df_out[ls_cols].mean(axis=1, skipna=False)
    return df_out


# Create data dictionary
dic_data = {}
ls_dates = sorted(df_data['DATE'].unique().tolist())

for date in tqdm(ls_dates):
    df_tmp = df_data[df_data['DATE'] == date]
    df_tmp = df_tmp.dropna(how='any')

    min_dvol = 25
    df_tmp = df_tmp[df_tmp['DVOL'] >= min_dvol]

    min_me = 250
    df_tmp = df_tmp[df_tmp['ME'] >= min_me]

    df_tmp = get_ZS(df_tmp)
    dic_data[date] = df_tmp


print(dic_data[ls_dates[0]])





# %%
# **************************************************
# *** Branch: COMMENTS                           ***
# **************************************************


'''
dic_test = dic_data[list(dic_data.keys())[332]]
dic_test = dic_test[dic_test['DVOL'] >= 40]

dic_test_2 = dic_data[list(dic_data.keys())[360]]
dic_test_2 = dic_test_2[dic_test_2['DVOL'] >= 40]
'''

'''
df_out['M_TRT1M'] = - df_out['M_TRT1M']
for i in range(0, n * 12):
    df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)
'''

'''
for i in range(0, n * 12):
    if i == 0:
        df_out['LS_TRT1M'] = df_out['TRT1M' + 't_' + str(i)].astype(str)
    else:
        df_out['LS_TRT1M'] = df_out['LS_TRT1M'] + ',' + df_out['TRT1M' + 't_' + str(i)].astype(str)
'''

# test_df.astype(str).agg(', '.join, axis=1)
# np.array(your_list,dtype=float)
# np.fromstring(df_out['LS_TRT1M'], dtype=float, sep=',')
# np.array(df_out['LS_TRT1M'].split(','),dtype=float)
# np.fromstring(df_out['LS_TRT1M'], dtype=float, sep=',')
# df_out[ls_cols_TRT1M].apply(lambda row: row.tolist(), axis=1)
'''
df_out['LS_TRT1M'] = df_out[ls_cols_TRT1M].astype(str).agg(','.join, axis=1)
print('Done')
df_out['LS_TRT1M'] = df_out['LS_TRT1M'].tolist()
'''
'''
df_out['LS_TRT1M'] = df_out[ls_cols_TRT1M].values.tolist()
'''
'''
n = 5
for i in range(n*12-1,-1,-1):
    df_data['TRT1M' + 't_' + str(i)] = df_data['TRT1M'].shift(periods=i)

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n * 4 * 3 - 1)  # Take n*12 months taking the current months: first date n*12 - 1
ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n*12-1,-1,-1)]

# Compute (-1)* mean return over the last n*12 months
df_data['M_TRT1M'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[ls_cols_TRT1M].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO

# Compute return + (-1) * mean return
for i in range(n*12-1,-1,-1):
    df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

df_data['M_TRT1M'] = -df_data['M_TRT1M']

for i in range(n*12-1,-1,-1):
    df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n*12-1,-1,-1)]
df_data['LS_TRT1M'] = df_data[ls_cols_TRT1M].values.tolist()

df_out = df_data.drop(columns=['TRT1M' + 't_' + str(i) for i in range(n*12-1,-1,-1)])
'''

'''
for n in range(n*12-1,-1,-1):
  print(n)
'''

'''
zzz = df_data['LS_TRT1M'].iloc[62][0]
zzzz= pd.DataFrame(df_data['LS_TRT1M'].iloc[62])
'''

'''
x = pd.DataFrame(df_data['LS_TRT1M'].iloc[60])
'''

'''
for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out['TRT1M'].shift(periods=(-i))

df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-3))
ls_cols = ['TRT1M_t' + str(i) for i in range(1, 4)]


df_out['M_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'],df_out[ls_cols].mean(axis=1, skipna=True), np.nan)


for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out[['TRT1M_t' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

df_out['M_TRT1M'] = -df_out['M_TRT1M']

for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out[['TRT1M_t' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)


for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out['TRT1M_t' + str(i)].fillna(0)


df_out['LS_NTRT1Q'] = df_out[ls_cols].values.tolist()
df_out.loc[df_out['FILLED'], 'LS_NTRT1Q'] = np.nan

df_out = df_out.drop(columns=['M_TRT1M'])
'''

'''
df_data_test = df_data[['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED', 'FQTR',
                    'CONM', 'TIC', 'EXCHG', 'GSECTOR','TRT1M','NTRT1M','NTRT1Q','NTRT1Y']]
'''