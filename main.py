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

# Filter dates (min_year-max_year)
min_year = 1990
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

# Check data preprocessing (4)
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

# Checkpoint data
# df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)

# Filter out illiquid stocks (max dollar volume (monthly) < $100mil.)
min_dvol = 40
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 40]
ls_permnos = df_tmp['PERMNO'].unique().tolist()
df_data = df_data[df_data['PERMNO'].isin(ls_permnos)]

# Checkpoint data
# df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)


# TODO: rewrite preprocessing_6 (takes 6h)
# TODO: get_zscore(df_data, ls_vars) VAR_ZS
# TODO: shift by 3 fondamental_quarterly, by permno, put nan when delisted

# Push forward fundamentals (out-of-sample)

def preprocessing_6(df_data):
    df_out = df_data
    df_out = df_out.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
    ls_vars = ['ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ', 'REVTQ', 'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ']
    ls_permnos = df_out['PERMNO'].unique().tolist()

    for permno in tqdm(ls_permnos, desc='Preprocessing (6)'):
        idx_tmp = df_out[df_out['PERMNO'] == permno].index
        s_tmp = df_out.loc[idx_tmp[0], ls_vars]
        df_out.loc[idx_tmp[0], ls_vars] = np.nan

        for i in range(1, len(idx_tmp) - 1):
            if df_out.loc[idx_tmp[i], 'QTR'] == df_out.loc[idx_tmp[i - 1], 'QTR']:
                df_out.loc[idx_tmp[i], ls_vars] = df_out.loc[idx_tmp[i - 1], ls_vars]
            else:
                s_new = df_out.loc[idx_tmp[i], ls_vars]
                df_out.loc[idx_tmp[i], ls_vars] = s_tmp
                s_tmp = s_new
    return df_out


df_data = preprocessing_6(df_data)




# %%
# **************************************************
# *** Branch: SCORES COMPUTATION                 ***
# **************************************************

# Summarize preprocessed data
df_1 = df_data.drop(columns=['PERMNO', 'DATE', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FQTR',
                             'CONM', 'TIC', 'EXCHG', 'GSECTOR'])
df_summary_1 = fn.tab_summary(df_1)




# Create variables LTM (Last Twelve Months)
def get_LTM(df_data, ls_vars):
    df_out = df_data
    for var in tqdm(ls_vars, desc='LTM'):
        df_out[var + '_t_3'] = df_out[var].shift(periods=3 * 3)
        df_out[var + '_t_2'] = df_out[var].shift(periods=2 * 3)
        df_out[var + '_t_1'] = df_out[var].shift(periods=1 * 3)
        df_out['PERMNO_t_3'] = df_out['PERMNO'].shift(periods=3 * 3)

        ls_cols = [var + '_t_3', var + '_t_2', var + '_t_1', var]
        df_out[var + '_LTM'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t_3'], df_out[ls_cols].sum(axis=1, skipna=False), np.nan)
        df_out = df_out.drop(columns=[var + '_t_3', var + '_t_2', var + '_t_1', 'PERMNO_t_3'])

    return df_out

df_data = get_LTM(df_data, ls_vars=['COGSQ', 'DPQ', 'NIQ', 'PIQ', 'REQ', 'REVTQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ'])


# Create additional variables
def preprocessing_6(df_data):
    df_out = df_data

    # Value
    df_out['ME'] = df_out['PRCCM'] * df_out['SHROUT']
    df_out['BE'] = df_out['ATQ'] - df_out['LTQ']  # Book value of Equity = Total Assets - Total Liabilities
    df_out['CF_LTM'] = df_out['NIQ_LTM'] + df_out['DPQ_LTM'] - df_out['WCAPCHQ_LTM'] - df_out['CAPXQ_LTM']  # CF = NI + D&A - dWC - CAPX
    df_out['BE/ME'] = df_out['BE'] / df_out['ME']  # Book-to-Market Equity
    df_out['E/P'] = (df_out['NIQ_LTM'] / df_out['SHROUT']) / df_out['PRCCM']  # Earning-to-Price
    df_out['CF/P'] = (df_out['CF_LTM'] / df_out['SHROUT']) / df_out['PRCCM']  # Cash Flow-to-Price

    # Profitability
    df_out['GPOA'] = (df_out['REVTQ_LTM'] - df_out['COGSQ_LTM']) / df_out['ATQ']
    df_out['ROE'] = df_out['NIQ_LTM'] / df_out['BE']
    df_out['ROA'] = df_out['NIQ_LTM'] / df_out['ATQ']
    df_out['CFOA'] = df_out['CF_LTM'] / df_out['ATQ']
    df_out['GMAR'] = (df_out['REVTQ_LTM'] - df_out['COGSQ_LTM']) / df_out['REVTQ_LTM']
    df_out['ACC'] = - (df_out['WCAPCHQ_LTM'] - df_out['DPQ_LTM']) / df_out['ATQ']

    df_out.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace inf with nan
    return df_out

df_data = preprocessing_6(df_data)



# Create diff. variables (nb_years interval)
def get_diff(df_data, ls_vars, nb_years):
    df_out = df_data
    for var in ls_vars:
        df_out[var + '_t'] = (-1) * df_out[var].shift(periods=(nb_years * 4 * 3))
        df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(nb_years * 4 * 3))
        ls_cols = [var + '_t', var]
        df_out['d_' + var] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].sum(axis=1, skipna=False), np.nan)
        df_out = df_out.drop(columns=[var + '_t', 'PERMNO_t'])

    return df_out

df_data = get_diff(df_data, ls_vars=['GPOA','ROE','ROA','CFOA','GMAR'], nb_years=5)





# Safety
df_data['LEV'] = (df_data['DLTTQ'] + df_data['DLCQ']) / df_data['ATQ']
df_data['AZSCORE'] = (1.2*df_data['WCAPQ'] + 1.4*df_data['REQ_LTM'] + 3.3*(df_data['PIQ_LTM'] + df_data['XINTQ_LTM']) + 0.6*df_data['ME'] + df_data['REVTQ_LTM']) / df_data['ATQ']
df_data.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace inf with nan

# Checkpoint data
df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
# %%
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)

# Beta & Volatility
with warnings.catch_warnings():
    warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

    n=5
    for i in range(0,n*12):
        df_data['TRT1M' + 't_' + str(i)] = df_data['TRT1M'].shift(periods=i)
    for i in range(0, n * 12):
        df_data['SPRTRN' + 't_' + str(i)] = df_data['SPRTRN'].shift(periods=i)



    df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n * 4 * 3 - 1)


    col_list_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(0,n*12)]
    col_list_SPRTRN = ['SPRTRN' + 't_' + str(i) for i in range(0,n*12)]


    df_data['TRT1M_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_TRT1M].mean(axis=1, skipna=False), np.nan) # Check the PERMNO
    df_data['SPRTRN_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_SPRTRN].mean(axis=1, skipna=False), np.nan) # Check the PERMNO

    for i in range(0,n*12):
        df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'TRT1M_mean']].sum(axis=1, skipna=False)

    for i in range(0, n * 12):
        df_data['SPRTRN' + 't_' + str(i)] = df_data[['SPRTRN' + 't_' + str(i), 'TRT1M_mean']].sum(axis=1, skipna=False)

    for i in range(0, n * 12):
        df_data['Prod_TRT1M_SPRTRN' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'SPRTRN' + 't_' + str(i)]].product(axis=1, skipna=False)


    col_list_Cov_TRT1M_SPRTRN = ['Prod_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0,n*12)]

    df_data['Cov_TRT1M_SPRTRN'] = df_data[col_list_Cov_TRT1M_SPRTRN].sum(axis=1, skipna=False) / (len(range(0, n * 12)) - 1)


    df_data['TRT1M_Var'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[col_list_TRT1M].var(axis=1, skipna=False), np.nan)
    df_data['SPRTRN_Var'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[col_list_SPRTRN].var(axis=1, skipna=False), np.nan)

    df_data['Beta'] = df_data['Cov_TRT1M_SPRTRN'] / df_data['SPRTRN_Var']


    df_data = df_data.drop(columns=['TRT1M' + 't_' + str(i) for i in range(0,n*12)])
    df_data = df_data.drop(columns=['SPRTRN' + 't_' + str(i) for i in range(0,n*12)])
    df_data = df_data.drop(columns=['Prod_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0,n*12)])
    df_data = df_data.drop(columns=['TRT1M_mean','SPRTRN_mean','Cov_TRT1M_SPRTRN','PERMNO_t'])


# Next Month & Next Quarter Returns

df_data['NTRT1M'] = df_data['TRT1M'].shift(periods=(-1))
df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=(-1))
df_data['NTRT1M'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data['NTRT1M'],  np.nan)
df_data['NTRT1M'] = df_data['NTRT1M'].fillna(0)

for i in range(1,4):
    df_data['TRT1M_t' + str(i)] = 1 + df_data['TRT1M'].shift(periods=(-i))

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=(-3))

ls_cols = ['TRT1M_t' + str(i) for i in range(1,4)]

df_data['NTRT1Q'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[ls_cols].product(axis=1, skipna=False) - 1 ,  np.nan)
df_data['NTRT1Q'] = df_data['NTRT1Q'].fillna(0)

df_data = df_data.drop(columns=['TRT1M_t' + str(i) for i in range(1,4)])
df_data = df_data.drop(columns=['PERMNO_t'])


# %%

# Create data dictionary
dic_data = {}
ls_dates = sorted(df_data['DATE'].unique().tolist())
ls_lens = []

for date in tqdm(ls_dates):
    df_tmp = df_data[df_data['DATE'] == date]
    df_tmp = df_tmp.dropna(how='any')
    dic_data[date] = df_tmp
    ls_lens += [len(df_tmp)]


'''
min_dvol = 100
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 100]
'''
dic_test = dic_data[list(dic_data.keys())[72]]
dic_test = dic_test[dic_test['DVOL'] >= 40]

dic_test_2 = dic_data[list(dic_data.keys())[360]]
dic_test_2 = dic_test_2[dic_test_2['DVOL'] >= 40]

#for i in dic_data:
#df['max_rank'] = df['Number_legs'].rank(method='max')

dic_test['BE/ME_rank'] = dic_test.loc['BE/ME'].rank(method='max',ascending=False)
dict_test_3 = dic_test[['BE/ME_r,['BE/ME']]


'''
df_data['ATQ_s'] = df_data['ATQ'].shift(periods=(3))
df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=(3))
df_data['ATQ_s'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data['ATQ_s'],  np.nan)
df_data = df_data[['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'ATQ','ATQ_s']]
'''


df_data['NTRT1M'] = df_data['NTRT1M'].fillna(0)



# %%
# **************************************************
# *** Branch: COMMENTS                           ***
# **************************************************

