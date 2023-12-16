# Import packages
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from scripts.functions import Portfolio
from scripts.functions import paths
from tqdm import tqdm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import scripts.functions as fn
import seaborn as sns
import warnings

# Project settings
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)

# Warnings management
warnings.filterwarnings(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


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

ls_selected_cols_4 = ['DATEFF', 'RF', 'MKTRF', 'SMB', 'HML', 'UMD']
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
# df_fundamentals_quarterly.to_pickle(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'))
# df_security_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'))
# df_stock_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'))
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
ls_selected_cols = ['DATE_NEW', 'RF', 'MKTRF', 'SMB', 'HML', 'UMD']
df_factors_monthly = df_factors_monthly[ls_selected_cols]
df_factors_monthly.rename(columns={'DATE_NEW': 'DATE'}, inplace=True)
df_factors_monthly = df_factors_monthly.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

# Save data (uncomment)
# df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
# df_factors_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_factors_monthly.pkl'))
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
                        'ZS_VAL', 'ZS_QLT', 'ZS_MOM', 'ZS_RMOM', 'ZS_AMOM',
                        'ZS_VAL_QLT', 'ZS_VAL_QLT_MOM', 'ZS_VAL_QLT_AMOM']
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
# *** Branch: PORTFOLIO ANALYSIS                 ***
# **************************************************

# Instance of portfolio
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_VAL_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200, ind_const='I', reb_freq='M')
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)

# Sector average counts
df_sec_avg_counts = port.get_df_sec_avg_counts()

# TODO: check results
with open(Path.joinpath(paths.get('output'), 'tables', 'df_ports_chars_2.pkl'), 'rb') as file:
    df_ports_chars = pickle.load(file)
df_ports_chars.to_excel(Path.joinpath(paths.get('output'), 'excels', 'df_ports_chars_2.xlsx'), index=True)

# %%

port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=0, spr_bps=50, b_cost=True)
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)

test = dic_data['df_facs_data']

def perf_output():
    return


port_1 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=0, spr_bps=0, b_cost=False)

df_port_perf_1 = port_1.tab_port_perf()

port_2 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0, b_cost=False)

df_port_perf_2 = port_2.tab_port_perf()

port_3 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=0, spr_bps=50, b_cost=True)

df_port_perf_3 = port_3.tab_port_perf()

for i in range(len(df_port_perf)):
    if i == 0:
        df_port_perf_1.loc[i, ['L_NAV']] = 100
        df_port_perf_1.loc[i, ['S_NAV']] = 100
        df_port_perf_2.loc[i, ['L_NAV']] = 100
        df_port_perf_2.loc[i, ['S_NAV']] = 100

        df_port_perf_1.loc[i, ['LA_NAV']] = 100
        df_port_perf_2.loc[i, ['LA_NAV']] = 100
        df_port_perf_3.loc[i, ['LA_NAV']] = 100

    else:
        df_port_perf_1.loc[i, ['L_NAV']] = np.array(df_port_perf_1.loc[i - 1, ['L_NAV']])[0] * (1 + np.array(df_port_perf_1.loc[i, ['L_RTNS']])[0])
        df_port_perf_1.loc[i, ['S_NAV']] = np.array(df_port_perf_1.loc[i - 1, ['S_NAV']])[0] * (1 + np.array(df_port_perf_1.loc[i, ['S_RTNS']])[0])
        df_port_perf_2.loc[i, ['L_NAV']] = np.array(df_port_perf_2.loc[i - 1, ['L_NAV']])[0] * (1 + np.array(df_port_perf_2.loc[i, ['L_RTNS']])[0])
        df_port_perf_2.loc[i, ['S_NAV']] = np.array(df_port_perf_2.loc[i - 1, ['S_NAV']])[0] * (1 + np.array(df_port_perf_2.loc[i, ['S_RTNS']])[0])

        df_port_perf_1.loc[i, ['LA_NAV']] = np.array(df_port_perf_1.loc[i - 1, ['LA_NAV']])[0] * (1 + np.array(df_port_perf_1.loc[i, ['LA_RTNS']])[0])
        df_port_perf_2.loc[i, ['LA_NAV']] = np.array(df_port_perf_2.loc[i - 1, ['LA_NAV']])[0] * (1 + np.array(df_port_perf_2.loc[i, ['LA_RTNS']])[0])
        df_port_perf_3.loc[i, ['LA_NAV']] = np.array(df_port_perf_3.loc[i - 1, ['LA_NAV']])[0] * (1 + np.array(df_port_perf_3.loc[i, ['LA_RTNS']])[0])

df_tpm_1 = df_port_perf_1.set_index('DATE')
df_tpm_2 = df_port_perf_2.set_index('DATE')
df_tpm_3 = df_port_perf_3.set_index('DATE')

# Plot long vs short performances
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
#ax.set_title('Portfolios Performances', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(df_tpm_1['L_NAV'], label='L_NAV' + ' (' + str(port_1.sig_long) + ', ' + str(port_1.n_asts_long) + ', ' + str(port_1.w_meth_long) + ', ' + str(port_1.ind_const) + ', ' + str(port_1.reb_freq) + ')', lw=3)
ax.plot(df_tpm_1['S_NAV'], label='S_NAV' + ' (' + str(port_1.sig_short) + ', ' + str(port_1.n_asts_short) + ', ' + str(port_1.w_meth_short) + ', ' + str(port_1.ind_const) + ', ' + str(port_1.reb_freq) + ')', lw=3)
ax.plot(df_tpm_2['L_NAV'], label='L_NAV_TC' + ' (' + str(port_2.sig_long) + ', ' + str(port_2.n_asts_long) + ', ' + str(port_2.w_meth_long) + ', ' + str(port_2.ind_const) + ', ' + str(port_2.reb_freq) + ')', lw=3)
ax.plot(df_tpm_2['S_NAV'], label='S_NAV_TC' + ' (' + str(port_2.sig_short) + ', ' + str(port_2.n_asts_short) + ', ' + str(port_2.w_meth_short) + ', ' + str(port_2.ind_const) + ', ' + str(port_2.reb_freq) + ')', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('figures'), 'port_perfs_L_vs_S' + port_1.port_name + '.png'))
plt.close()

# Plot portfolio performances
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
#ax.set_title('Portfolios Performances', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(df_tpm_1['PORT_NAV'], label='PORT_NAV' + ' (L = ' + str(port_1.pct_long) + ', S = ' + str(port_1.pct_short) + ', C = ' + str(100 - (port_1.pct_long - port_1.pct_short)) + ')', lw=3)
ax.plot(df_tpm_2['PORT_NAV'], label='PORT_NAV_TC' + ' (L = ' + str(port_2.pct_long) + ', S = ' + str(port_2.pct_short) + ', C = ' + str(100 - (port_2.pct_long - port_2.pct_short)) + ')', lw=3)
ax.plot(df_tpm_3['PORT_NAV'], label='PORT_NAV_TC_BC' + ' (L = ' + str(port_3.pct_long) + ', S = ' + str(port_3.pct_short) + ', C = ' + str(100 - (port_3.pct_long - port.pct_short)) + ')', lw=3)
ax.plot(df_tpm_1['LA_NAV'], label='LA_NAV' + ' (' + str(port_1.sig_long) + ', ' + str(port_1.n_asts_long) + ', ' + str(port_1.w_meth_long) + ', ' + str(port_1.ind_const) + ', ' + str(port_1.reb_freq) + ')', lw=3)
ax.plot(df_tpm_2['LA_NAV'], label='LA_NAV_TC' + ' (' + str(port_2.sig_long) + ', ' + str(port_2.n_asts_long) + ', ' + str(port_2.w_meth_long) + ', ' + str(port_2.ind_const) + ', ' + str(port_2.reb_freq) + ')', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('figures'), 'port_perfs_LS_vs_LA' + port_1.port_name + '.png'))
plt.close()

# Plot portfolio performances
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
#ax.set_title('Portfolios Performances', size=28)
ax.axhline(y=0, color='black', ls='--', lw=1)
ax.plot(df_tpm_1['PORT_NAV'], label='PORT_NAV' + ' (L = ' + str(port_1.pct_long) + ', S = ' + str(port_1.pct_short) + ', C = ' + str(100 - (port_1.pct_long - port_1.pct_short)) + ')', lw=3)
ax.plot(df_tpm_1['PORT_L'], label='PORT_L', lw=3)
ax.plot((-1) * df_tpm_1['PORT_S'], label='PORT_S', lw=3)
ax.plot(df_tpm_1['PORT_C'], label='PORT_C', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('figures'), 'port_perfs_NAV' + port_1.port_name + '.png'))
plt.close()

df_port_chars_1 = port_1.tab_port_chars(output_perf=False)
df_port_chars_1_L = df_port_chars_1[['L_ANN_MEAN', 'L_ANN_VOL', 'L_SHARPE', 'L_MAX_DD', 'L_CALMAR', 'L_AVG_TO', 'L_NORM_HI']]
df_port_chars_1_S = df_port_chars_1[['S_ANN_MEAN', 'S_ANN_VOL', 'S_SHARPE', 'S_MAX_DD', 'S_CALMAR', 'S_AVG_TO', 'S_NORM_HI']]


df_port_chars_2 = port_1.tab_port_chars(output_perf=False)
df_port_chars_2_L = df_port_chars_2[['L_ANN_MEAN', 'L_ANN_VOL', 'L_SHARPE', 'L_MAX_DD', 'L_CALMAR', 'L_AVG_TO', 'L_NORM_HI']]
df_port_chars_2_S = df_port_chars_2[['S_ANN_MEAN', 'S_ANN_VOL', 'S_SHARPE', 'S_MAX_DD', 'S_CALMAR', 'S_AVG_TO', 'S_NORM_HI']]

dic_df_port_chars_1_L ={'L': df_port_chars_1_L, 'L_TC': df_port_chars_1_L}
dic_df_port_chars_1_S ={'L': df_port_chars_1_S, 'S_TC': df_port_chars_2_S}

dic_df_port_chars_1 = {'L':dic_df_port_chars_1_L, 'S':dic_df_port_chars_1_S}


