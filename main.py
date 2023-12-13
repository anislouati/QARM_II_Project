# Import packages
from scripts.functions import Portfolio
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from scipy.optimize import minimize, OptimizeResult
from scripts.functions import paths
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle
import scripts.functions as fn
import warnings
import time

# Project settings
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)

# Warnings management
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings(action='ignore', category=RuntimeWarning)


# %%
# **************************************************
# *** Branch: DATA MANAGEMENT                    ***
# **************************************************

# Import raw data
df_fundamentals_quarterly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))
df_security_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_security_monthly.sas7bdat'))
df_stock_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_security_files_monthly_stock.sas7bdat'))
df_factors_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'factors_monthly.sas7bdat'))

# Filter selected cols
ls_selected_cols_1 = ['LPERMNO', 'DATADATE',
                      'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC',
                      'ATQ', 'COGSQ', 'CSHOQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ',
                      'REVTQ', 'WCAPQ', 'XINTQ', 'CAPXY']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]
df_fundamentals_quarterly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_2 = ['LPERMNO', 'DATADATE', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]
df_security_monthly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_3 = ['PERMNO', 'DATE', 'BID', 'ASK', 'VOL', 'SPRTRN']
df_stock_monthly = df_stock_monthly[ls_selected_cols_3]

ls_selected_cols_4 = ['DATEFF', 'RF', 'MKTRF', 'SMB', 'HML']
df_factors_monthly = df_factors_monthly[ls_selected_cols_4]

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

# Save data (uncomment)
# with open(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'), 'wb') as file:
#     pickle.dump(df_fundamentals_quarterly, file)
# with open(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'), 'wb') as file:
#     pickle.dump(df_security_monthly, file)
# with open(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'), 'wb') as file:
#     pickle.dump(df_stock_monthly, file)
# Load data
with open(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'), 'rb') as file:
    df_fundamentals_quarterly = pickle.load(file)
with open(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'), 'rb') as file:
    df_security_monthly = pickle.load(file)
with open(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'), 'rb') as file:
    df_stock_monthly = pickle.load(file)

# Merge datasets
df_fundamentals_quarterly = df_fundamentals_quarterly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYM'])
df_tmp = pd.merge(df_fundamentals_quarterly, df_security_monthly, on='KEYQ', how='inner')

df_stock_monthly = df_stock_monthly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ'])
df_data = pd.merge(df_stock_monthly, df_tmp, on='KEYM', how='inner')

# Fill missing dates with nans (by stock)
df_data = fn.preprocessing_4(df_data)
ls_selected_cols = ['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED',
                    'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC',
                    'ATQ', 'COGSQ', 'CSHOQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ',
                    'REVTQ', 'WCAPQ', 'XINTQ', 'CAPXY',
                    'PRCCM', 'TRT1M', 'BID', 'ASK', 'VOL', 'SPRTRN']
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
print('Assets in dataset: {}'.format(len(df_data['PERMNO'].unique().tolist())))
print('Assets with filled data: {}'.format(s_tmp[0]))

# Create/Modify variables
df_data = fn.preprocessing_5(df_data)
ls_selected_cols = ['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED',
                    'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC',
                    'ATQ', 'COGSQ', 'CSHOQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ',
                    'REVTQ', 'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ', 'PRCCQ',
                    'PRCCM', 'TRT1M', 'BID', 'ASK', 'SPRDPCT', 'VOL', 'DVOL', 'SPRTRN']
df_data = df_data[ls_selected_cols]
df_data = df_data.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# ATTENTION: accounting data published in Q_t is available (out-of-sample) for investment decisions in Q_t_1
# Push forward fundamentals (out-of-sample)
df_data = fn.preprocessing_6(df_data)

# Create additional variables (fundamental metrics)
df_data = fn.preprocessing_7(df_data)

# Filter clean dates (31/12/min_year-31/12/max_year)
min_year = 1994
max_year = 2022
df_data = df_data[(df_data['DATE'] >= datetime(min_year, 12, 31)) &
                  (df_data['DATE'] <= datetime(max_year, 12, 31))]

# Filter out excluded sectors (40: Financials)
'''
n_asts_1 = len(df_data['PERMNO'].unique().tolist())
df_data = df_data[df_data['GSECTOR'] != bytes('40', 'utf-8')]
n_asts_2 = len(df_data['PERMNO'].unique().tolist())
print('Assets before filter: {}'.format(n_asts_1))
print('Assets after filter: {}'.format(n_asts_2))
'''

# Sync dates (EOM) for factors data
ls_dates = sorted(df_data['DATE'].unique().tolist())
ls_year_mth = [(str(date.year) + '_' + str(date.month)) for date in ls_dates]
dic_dates = dict(zip(ls_year_mth, ls_dates))
for i in range(len(df_factors_monthly)):
    date = df_factors_monthly.loc[i, 'DATEFF']
    year_mth = str(date.year) + '_' + str(date.month)
    if year_mth in list(dic_dates.keys()):
        df_factors_monthly.loc[i, 'DATE_NEW'] = dic_dates[year_mth]
df_factors_monthly = df_factors_monthly[~pd.isnull(df_factors_monthly['DATE_NEW'])].drop(columns=['DATEFF'])
ls_selected_cols = ['DATE_NEW', 'RF', 'MKTRF', 'SMB', 'HML']
df_factors_monthly = df_factors_monthly[ls_selected_cols]
df_factors_monthly.rename(columns={'DATE_NEW': 'DATE'}, inplace=True)
df_factors_monthly = df_factors_monthly.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

# Save data (uncomment)
# with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'wb') as file:
#     pickle.dump(df_data, file)
# with open(Path.joinpath(paths.get('data'), 'df_factors_monthly.pkl'), 'wb') as file:
#     pickle.dump(df_factors_monthly, file)
# Load data
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as file:
    df_data = pickle.load(file)
with open(Path.joinpath(paths.get('data'), 'df_factors_monthly.pkl'), 'rb') as file:
    df_factors_monthly = pickle.load(file)

# Create data dictionary
dic_asts_data = {}
ls_dates = sorted(df_data['DATE'].unique().tolist())
for date in tqdm(ls_dates, desc='Assets data dictionary'):
    df_tmp = df_data[df_data['DATE'] == date]
    df_tmp = df_tmp.dropna(how='any')  # Remark: we drop all rows with at least one nan (by date)

    min_dvol = 25  # Minimum dollar volume (mil., monthly)
    min_me = 250  # Minimum market cap (mil.)
    df_tmp = df_tmp[(df_tmp['DVOL'] >= min_dvol) & (df_tmp['ME'] >= min_me)]
    df_tmp = fn.get_ZS(df_tmp)

    ls_selected_cols = ['PERMNO', 'DATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR',
                        'PRCCM', 'TRT1M', 'SPRDPCT', 'DVOL', 'SPRTRN', 'ME',
                        'VOL_TRT1M', 'VOL_SPRTRN', 'BETA',
                        'CTRT1M_1', 'LS_PTRT1M', 'LS_NTRT1M',
                        'ZS_VAL', 'ZS_QLT', 'ZS_MOM_1', 'ZS_MOM_2', 'ZS_RMOM_1',
                        'ZS_VAL_QLT', 'ZS_VAL_QLT_MOM_1', 'ZS_VAL_QLT_MOM_2', 'ZS_VAL_QLT_RMOM', 'ZS_VAL_QLT_ARMOM']
    df_tmp = df_tmp[ls_selected_cols]
    df_tmp = df_tmp.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
    dic_asts_data[date] = df_tmp
dic_data = {'dic_asts_data': dic_asts_data, 'df_facs_data': df_factors_monthly}

# Save data (uncomment)
# with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'wb') as file:
#     pickle.dump(dic_data, file)
# Load data
with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'rb') as file:
    dic_data = pickle.load(file)


# %%
# **************************************************
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************

# Grid search
df_ports_chars = pd.DataFrame()
ls_sigs = ['ZS_VAL', 'ZS_QLT', 'ZS_VAL_QLT']  # V, Q, VQ, MOM
ls_n_asts = [15, 25]  # TODO: 25
ls_w_meth = ['EW', 'MV', 'MN', 'RP']  # EW MN RP MV
ls_pct_long_short = [(150, 50), (120, 50), (100, 90)]  # (130, 30) (150, 50) (120, 50) (130, 40) (100, 100) (100, 90)
ls_ind_const = ['I', 'NI']
ls_reb_freq = ['Q', 'Y']
n_ports = len(ls_sigs) * len(ls_n_asts) * len(ls_w_meth) * len(ls_pct_long_short) * len(ls_ind_const) * len(ls_reb_freq)

i = 0
start_time = time.time()
for sig in ls_sigs:
    for n_asts in ls_n_asts:
        for w_meth in ls_w_meth:
            for (pct_long, pct_short) in ls_pct_long_short:
                for ind_const in ls_ind_const:
                    for reb_freq in ls_reb_freq:
                        port = Portfolio(dic_data=dic_data, sig_long=sig, n_asts_long=n_asts, w_meth_long=w_meth, pct_long=pct_long,
                                         sig_short=sig, n_asts_short=n_asts, w_meth_short=w_meth, pct_short=pct_short,
                                         ind_const=ind_const, reb_freq=reb_freq, min_short_me=1000, max_short_cl=0.4)
                        df_port_chars = port.tab_port_chars(output_perf=False)
                        df_ports_chars = pd.concat([df_ports_chars, df_port_chars], axis=0, ignore_index=True)
                        with open(Path.joinpath(paths.get('output'), 'df_ports_chars.pkl'), 'wb') as file:
                            pickle.dump(df_ports_chars, file)
                        i += 1
                        print('Port {}/{}: DONE'.format(i, n_ports))
end_time = time.time()
print('Elapsed time: {} seconds'.format(end_time - start_time))

# Load data
with open(Path.joinpath(paths.get('output'), 'df_ports_chars.pkl'), 'rb') as file:
    df_ports_chars = pickle.load(file)




#%%
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_MOM_1', n_asts_long=25, w_meth_long='MN', pct_long=100,
                 sig_short='ZS_VAL_QLT_MOM_1', n_asts_short=25, w_meth_short='MN', pct_short=100,
                 ind_const='NI', reb_freq='M', min_short_me=1000, max_short_cl=0.4)
df_1 = port.tab_port_chars(output_perf=False)

port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_MOM_1', n_asts_long=20, w_meth_long='RP', pct_long=200,
                 sig_short='ZS_VAL_QLT_MOM_1', n_asts_short=20, w_meth_short='RP', pct_short=100,
                 ind_const='NI', reb_freq='Q', min_short_me=1000, max_short_cl=0.4)
df_2 = port.tab_port_chars(output_perf=False)



# %%

