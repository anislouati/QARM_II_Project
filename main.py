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
                      'ACTQ', 'ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ', 'LCTQ', 'LTQ', 'NIQ',
                      'PIQ', 'REQ', 'REVTQ', 'WCAPQ', 'XINTQ', 'CAPXY']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]
df_fundamentals_quarterly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_2 = ['LPERMNO', 'DATADATE', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]
df_security_monthly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_3 = ['PERMNO', 'DATE', 'BID', 'ASK', 'VOL', 'SHROUT', 'SPRTRN']
df_stock_monthly = df_stock_monthly[ls_selected_cols_3]



# Checkpoint data
df_fundamentals_quarterly.to_pickle(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'))
df_security_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'))
df_stock_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'), 'rb') as f:
    df_fundamentals_quarterly = pickle.load(f)
with open(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'), 'rb') as f:
    df_security_monthly = pickle.load(f)
with open(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'), 'rb') as f:
    df_stock_monthly = pickle.load(f)









# Preprocess data (add keys/identifiers)
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

# Preprocess data (drop faulty FQTR and duplicates)
df_fundamentals_quarterly = fn.preprocessing_2(df_fundamentals_quarterly)
df_security_monthly = fn.preprocessing_3(df_security_monthly)
df_stock_monthly = fn.preprocessing_3(df_stock_monthly)



# Merge datasets
df_fundamentals_quarterly = df_fundamentals_quarterly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYM'])
df_tmp = pd.merge(df_fundamentals_quarterly, df_security_monthly, on='KEYQ', how='inner')

df_stock_monthly = df_stock_monthly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ'])
df_data = pd.merge(df_stock_monthly, df_tmp, on='KEYM', how='inner')

# Preprocess data (fill missing dates with nans)
df_data = fn.preprocessing_4(df_data)
ls_selected_cols = ['PERMNO', 'DATE', 'FQTR', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM',
                    'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'ACTQ', 'ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ',
                    'EPSFXQ', 'LCTQ', 'LTQ', 'NIQ', 'PIQ', 'REQ', 'REVTQ', 'WCAPQ', 'XINTQ', 'CAPXY',
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
ls_selected_cols = ['PERMNO', 'DATE', 'FQTR', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM',
                    'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'ACTQ', 'ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ',
                    'EPSFXQ', 'LCTQ', 'LTQ', 'NIQ', 'PIQ', 'REQ', 'REVTQ', 'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ',
                    'PRCCM', 'TRT1M', 'BID', 'ASK', 'SPRDPCT', 'VOL', 'DVOL', 'SHROUT', 'SPRTRN']
df_data = df_data[ls_selected_cols]
df_data = df_data.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Filter out illiquid stocks (max dollar volume (monthly) < $100mil.)
min_dvol = 100
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 100]
ls_permnos = df_tmp['PERMNO'].unique().tolist()
df_data = df_data[df_data['PERMNO'].isin(ls_permnos)]

# Checkpoint data
df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)

# Summarize preprocessed data
df_1 = df_data.drop(columns=['PERMNO', 'DATE', 'FQTR', 'QTR', 'MTH', 'KEYQ', 'KEYM',
                             'CONM', 'TIC', 'EXCHG', 'GSECTOR'])
df_summary_1 = fn.tab_summary(df_1)

print(df_data['SPRTRN'].unique().tolist())

# Create data dictionary
dic_data = {}
ls_dates = sorted(df_data['DATE'].unique().tolist())
ls_lens = []

for date in tqdm(ls_dates):
    df_tmp = df_data[df_data['DATE'] == date]
    df_tmp = df_tmp.dropna(how='any')
    dic_data[date] = df_tmp
    ls_lens += [len(df_tmp)]



# %%
# **************************************************
# *** Branch: SCORE COMPUTATIONS                 ***
# **************************************************

def get_LTM(variables,df):
    for v in variables:
        df[v + '_t_3'] = df[v].shift(periods=3 * 3)
        df[v + '_t_2'] = df[v].shift(periods=2 * 3)
        df[v + '_t_1'] = df[v].shift(periods=1 * 3)
        df['PERMNO_t_3'] = df['PERMNO'].shift(periods=3 * 3)

        col_list = [v + '_t_3', v + '_t_2', v + '_t_1', v]

        df[v + '_LTM'] = np.where(df['PERMNO'] == df['PERMNO_t_3'], df[col_list].sum(axis=1, skipna=False), np.nan)

        df = df.drop(columns=[v + '_t_3', v + '_t_2', v + '_t_1', 'PERMNO_t_3'])

    return df

df_data = get_LTM(['REVTQ', 'NIQ', 'COGSQ', 'DPQ', 'WCAPCHQ', 'CAPXQ', 'REQ', 'PIQ', 'XINTQ'],df_data)


# *** Value Score ***
df_data['ME'] = df_data['PRCCM'] * df_data['SHROUT']
df_data['BE'] = df_data['ATQ'] - df_data['LTQ']   # Book value of Equity = Total Asset - Total Liabilities
df_data['BE/ME'] = df_data['BE'] / df_data['ME']  # Book-to-Market equity
df_data['E/P'] = (df_data['NIQ_LTM'] / df_data['SHROUT']) / df_data['PRCCM']  # Earning-to-Price
df_data['CF/P'] = ((df_data['NIQ_LTM'] + df_data['DPQ_LTM'] - df_data['WCAPCHQ_LTM'] - df_data['CAPXQ_LTM']) / df_data['SHROUT']) / df_data['PRCCM']  # Cash Flow-to-Price


# *** Quality Score ***

# Profitability
df_data['GPOA'] = (df_data['REVTQ_LTM'] - df_data['COGSQ_LTM']) / df_data['ATQ']
df_data['ROE'] = df_data['NIQ_LTM'] / df_data['BE']
df_data['ROA'] = df_data['NIQ_LTM'] / df_data['ATQ']
df_data['CFOA'] = (df_data['NIQ_LTM'] + df_data['DPQ_LTM'] - df_data['WCAPCHQ_LTM'] - df_data['CAPXQ_LTM']) / df_data['ATQ']
df_data['GMAR'] = (df_data['REVTQ_LTM'] - df_data['COGSQ_LTM']) / df_data['REVTQ_LTM']
df_data['ACC'] = - (df_data['WCAPCHQ_LTM'] - df_data['DPQ_LTM']) / df_data['ATQ']

df_data.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace inf with nan


'''
df_data_test = df_data.loc[df_data['TIC'] == bytes('AAPL', 'utf-8')]
'''

# Growth

def get_growth(variables, n, df):
    for v in variables:
        df[v + '_t'] = -df[v].shift(periods=n * 4 * 3)

        df['PERMNO_t'] = df['PERMNO'].shift(periods=n * 4 * 3)

        col_list = [v + '_t', v]

        df['d_' + v] = np.where(df['PERMNO'] == df['PERMNO_t'], df[col_list].sum(axis=1, skipna=False), np.nan)

        df = df.drop(columns=[v + '_t', 'PERMNO_t'])

    return df

df_data = get_growth(variables= ['GPOA','ROE','ROA','CFOA','GMAR'], n=5, df=df_data)


'''
zzz = df_data[['DATE', 'PERMNO', 'QTR', 'GPOA', 'd_GPOA', 'ROE','d_ROE', 'ROA', 'd_ROA', 'CFOA', 'd_CFOA','GMAR', 'd_GMAR']]
zzz_test = zzz.loc[df_data['TIC'] == bytes('AAPL', 'utf-8')]
'''


# Safety
df_data['LEV'] = (df_data['DLTTQ'] + df_data['DLCQ']) / df_data['ATQ']
df_data['AZSCORE'] = (1.2*df_data['WCAPQ'] + 1.4*df_data['REQ_LTM'] + 3.3*(df_data['PIQ_LTM'] + df_data['XINTQ_LTM']) + 0.6*df_data['ME'] + df_data['REVTQ_LTM']) / df_data['ATQ']

df_data.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace inf with nan

# Checkpoint data
df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
# %%
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)

# Beta

n=5
for i in range(0,n*12+1):
    df_data['TRT1M' + 't_' + str(i)] = df_data['TRT1M'].shift(periods=i)
for i in range(0, n * 12 + 1):
    df_data['SPRTRN' + 't_' + str(i)] = df_data['SPRTRN'].shift(periods=i)

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n * 4 * 3)


col_list_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(0,n*12+1)]
col_list_SPRTRN = ['SPRTRN' + 't_' + str(i) for i in range(0,n*12+1)]


df_data['TRT1M_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_TRT1M].mean(axis=1, skipna=False), np.nan) # Check the PERMNO
df_data['SPRTRN_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_SPRTRN].mean(axis=1, skipna=False), np.nan) # Check the PERMNO

for i in range(0,n*12+1):
    df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'TRT1M_mean']].sum(axis=1, skipna=False)

for i in range(0, n * 12 + 1):
    df_data['SPRTRN' + 't_' + str(i)] = df_data['SPRTRN'].shift(periods=i)



for i in range(0, n * 12 + 1):
    df_data['Prod_TRT1M_SPRTRN' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'SPRTRN' + 't_' + str(i)]].product(axis=1, skipna=False)


col_list_Cov_TRT1M_SPRTRN= ['Prod_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0,n*12+1)]

df_data['Cov_TRT1M_SPRTRN'] = df_data[col_list_Cov_TRT1M_SPRTRN].sum(axis=1, skipna=False) / (len(range(0, n * 12 + 1)) - 1)


df_data['TRT1M_Var'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[col_list_TRT1M].var(axis=1, skipna=False), np.nan)
df_data['SPRTRN_Var'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[col_list_SPRTRN].var(axis=1, skipna=False), np.nan)

df_data['Beta'] = df_data['Cov_TRT1M_SPRTRN'] / df_data['SPRTRN_Var']


df_data = df_data.drop(columns=['TRT1M' + 't_' + str(i) for i in range(0,n*12+1)])
df_data = df_data.drop(columns=['SPRTRN' + 't_' + str(i) for i in range(0,n*12+1)])
df_data = df_data.drop(columns=['Prod_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0,n*12+1)])
df_data = df_data.drop(columns=['TRT1M_mean','SPRTRN_mean','Cov_TRT1M_SPRTRN','PERMNO_t'])



#df_data['SPRTRN_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[['TRT1M'+'t_' + str(i) for i in range(1,n*12+1)]].mean(), np.nan)

'''
#df_data['TRT1M_list'] = 'None'
#df_data = pd.concat([df_data['TRT1M'+'t_' + str(i)] for i in range(1,n*12+1)]).sort_index().values.tolist()
#df_data['TRT1M_list'] = [df_data['TRT1M'+'t_' + str(i)] for i in range(1,n*12+1)]

# Rename the concatenated column and drop the original columns
df = pd.concat([df, concatenated_cols['Name_Age_Country']], axis=1)
df = df.rename(columns={'Name_Age_Country': 'Name|Age|Country'})
df = df.drop(columns=['Name', 'Age', 'Country'])


if df_data['PERMNO'] == df_data['PERMNO_t']:


col_list = [v + '_t', v]

df['d_' + v] = np.where(df['PERMNO'] == df['PERMNO_t'], df[col_list].sum(axis=1, skipna=False), np.nan)

df = df.drop(columns=[v + '_t', 'PERMNO_t'])
'''


# %%
# **************************************************
# *** Branch: COMMENTS                           ***
# **************************************************

'''
def get_LTM(variables):
    j = 0
    idx_tmp = df_data.index
    for v in variables:
        df_data[v + '_LTM'] = df_data[v]
    for i in tqdm(idx_tmp):
        for v in variables:
            if j < (3 * 3):
                df_data.loc[i, v + '_LTM'] = None
            if j >= (3 * 3):
                if df_data.loc[i, 'PERMNO'] == df_data.loc[idx_tmp[j - (3 * 3)], 'PERMNO']:
                    df_data.loc[i, v + '_LTM'] = pd.array([df_data.loc[idx_tmp[j - (3 * 3)], v],
                                                            df_data.loc[idx_tmp[j - (2 * 3)], v],
                                                            df_data.loc[idx_tmp[j - (1 * 3)], v],
                                                            df_data.loc[idx_tmp[j - (0 * 3)], v]]).sum(skipna=False)
                else:
                    df_data.loc[i, v + '_LTM'] = None

        j = j + 1

get_LTM(['REVTQ'])
#get_LTM(['REVTQ', 'NIQ', 'COGSQ', 'DPQ', 'WCAPCHQ', 'CAPXQ', 'REQ', 'PIQ', 'XINTQ'])

def get_LTM_2():
    return


#df_data['REVTQ_LTM_2'] = np.nan
df_data['REVTQ_t_3'] = df_data['REVTQ'].shift(periods=3*3)
df_data['REVTQ_t_2'] = df_data['REVTQ'].shift(periods=2 * 3)
df_data['REVTQ_t_1'] = df_data['REVTQ'].shift(periods=1 * 3)
df_data['PERMNO_t_3'] = df_data['PERMNO'].shift(periods=3*3)

col_list = ['REVTQ_t_3', 'REVTQ_t_2', 'REVTQ_t_1','REVTQ']


if df_data['PERMNO'] == df_data['PERMNO_t_3']:
    return

#np.where(df['Courses'] == 'Spark', 1000, 2000)
#df_data['REVTQ_LTM_2'] = df[col_list].sum(axis=1, skipna=False)

df_data['REVTQ_LTM_2'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t_3'], df_data[col_list].sum(axis=1, skipna=False), np.nan)

test_LTM = df_data['REVTQ_LTM'].fillna(-1000000000) == df_data['REVTQ_LTM_2'].fillna(-1000000000)
print(len(test_LTM))
print(test_LTM.sum())
'''

'''
# Growth
df_data['d_GPOA'] = df_data['GPOA']
df_data['d_ROE'] = df_data['ROE']
df_data['d_ROA'] = df_data['ROA']
df_data['d_CFOA'] = df_data['CFOA']
df_data['d_GMAR'] = df_data['GMAR']

j = 0
n = 5
idx_tmp = df_data.index
for i in tqdm(idx_tmp):

    if j < (n*4*3):
        df_data.loc[i, 'd_GPOA'] = None
        df_data.loc[i, 'd_ROE'] = None
        df_data.loc[i, 'd_ROA'] = None
        df_data.loc[i, 'd_CFOA'] = None
        df_data.loc[i, 'd_GMAR'] = None

    if j >= (n*4*3):
        if df_data.loc[i, 'PERMNO'] == df_data.loc[idx_tmp[j-(n*4*3)], 'PERMNO']:
            df_data.loc[i, 'd_GPOA'] = (df_data.loc[i, 'GPOA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'GPOA'])
            df_data.loc[i, 'd_ROE'] = (df_data.loc[i, 'ROE'] - df_data.loc[idx_tmp[j-(n*4*3)], 'ROE'])
            df_data.loc[i, 'd_ROA'] = (df_data.loc[i, 'ROA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'ROA'])
            df_data.loc[i, 'd_CFOA'] = (df_data.loc[i, 'CFOA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'CFOA'])
            df_data.loc[i, 'd_GMAR'] = (df_data.loc[i, 'GMAR'] - df_data.loc[idx_tmp[j-(n*4*3)], 'GMAR'])

        else:
            df_data.loc[i, 'd_GPOA'] = None
            df_data.loc[i, 'd_ROE'] = None
            df_data.loc[i, 'd_ROA'] = None
            df_data.loc[i, 'd_CFOA'] = None
            df_data.loc[i, 'd_GMAR'] = None

    j += 1

n = 5

df_data['GPOA_t'] = -df_data['GPOA'].shift(periods=n* 4 * 3)

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n* 4 * 3)

col_list = ['GPOA_t', 'GPOA']

df_data['d_GPOA_2'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[col_list].sum(axis=1, skipna=False), np.nan)

df_data = df_data.drop(columns=['GPOA_t', 'PERMNO_t'])

test_LTM = df_data['d_GPOA'].fillna(-1000000000) == df_data['d_GPOA_2'].fillna(-1000000000)
print(len(test_LTM))
print(test_LTM.sum())
'''

'''
n=5
for i in range(1,n*12+1):
    df_data['TRT1M' + 't_' + str(i)] = df_data['TRT1M'].shift(periods=i)
for i in range(1, n * 12 + 1):
    df_data['SPRTRN' + 't_' + str(i)] = df_data['SPRTRN'].shift(periods=i)

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n * 4 * 3)

col_list_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(1,n*12+1)]
col_list_TRT1M.append('TRT1M')

col_list_SPRTRN = ['SPRTRN' + 't_' + str(i) for i in range(1,n*12+1)]
col_list_SPRTRN.append('SPRTRN')

df_data['TRT1M_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_TRT1M].mean(axis=1, skipna=False), np.nan) # Check the PERMNO
df_data['SPRTRN_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_SPRTRN].mean(axis=1, skipna=False), np.nan) # Check the PERMNO

for i in range(1,n*12+1):
    df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'TRT1M_mean']].sum(axis=1, skipna=False)

for i in range(1, n * 12 + 1):
    df_data['SPRTRN' + 't_' + str(i)] = df_data['SPRTRN'].shift(periods=i)

for i in range(1, n * 12 + 1):
    df_data['Prod_TRT1M_SPRTRN' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'SPRTRN' + 't_' + str(i)]].product(axis=1, skipna=False)

col_list_Cov_TRT1M_SPRTRN= ['TRT1M' + 't_' + str(i) for i in range(1,n*12+1)]
col_list_Cov_TRT1M_SPRTRN.append('TRT1M')

df_data['Cov_TRT1M_SPRTRN'] =

'''
