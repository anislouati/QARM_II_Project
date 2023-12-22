# Import packages
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from scripts.functions import Portfolio
from scripts.functions import paths
from tqdm import tqdm
import pandas as pd
import pickle
import scripts.functions as fn
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
                        'ZS_PROF', 'ZS_GWTH', 'ZS_SAF',
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


# Load data
with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'rb') as file:
    dic_data = pickle.load(file)
with open(Path.joinpath(paths.get('output'), 'tables', 'df_ports_chars.pkl'), 'rb') as file:
    df_ports_chars = pickle.load(file)


# %%
# *** Branch: Presentation ***


# Sector average counts
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=20, w_meth_long='EW', pct_long=120,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50, ind_const='I', reb_freq='M')
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)
df_sec_avg_counts = port.get_df_sec_avg_counts()
df_sec_avg_counts.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format('df_sec_avg_counts')), index=False)

# Plot zscores (stock picking)
fn.plot_zscores(date=datetime(2022, 12, 31), ls_zscores=['ZS_VAL', 'ZS_QLT'], leg='L')
fn.plot_zscores(date=datetime(2022, 12, 31), ls_zscores=['ZS_PROF', 'ZS_GWTH', 'ZS_SAF'], leg='L')

# Portfolios selection
ls_keys = ['VAL_1', 'QLT_1', 'VQ_1', 'VAL_2', 'QLT_2', 'VQ_2', 'VAL_3', 'QLT_3', 'VQ_3',
           'BEST_11', 'VQAM_1', 'BEST_12', 'VQAM_2', 'BEST_13', 'VQAM_3',
           'BEST_21', 'BEST_G1', 'BEST_22', 'BEST_G2', 'BEST_23', 'BEST_G3']
ls_values = [812, 1620, 3240, 818, 1626, 3246, 830, 1638, 4070,
             3240, 5580, 1626, 5676, 4070, 5688,
             3240, 3780, 1626, 3786, 4070, 3888]
dic_selected_ports = dict(zip(ls_keys, ls_values))
dic_sigs = {'VAL': 'ZS_VAL', 'QLT': 'ZS_QLT', 'VQ': 'ZS_VAL_QLT', 'VQAM': 'ZS_VAL_QLT_AMOM'}

# All ports exports
ls_ports = []
for i in range(len(ls_keys)):
    s_tmp = df_ports_chars.iloc[dic_selected_ports[ls_keys[i]]]
    port = Portfolio(dic_data=dic_data, sig_long=dic_sigs[s_tmp['L_SIG']], n_asts_long=s_tmp['L_N_ASTS'], w_meth_long=s_tmp['L_W_METH'], pct_long=s_tmp['L_PCT'],
                     sig_short=dic_sigs[s_tmp['S_SIG']], n_asts_short=s_tmp['S_N_ASTS'], w_meth_short=s_tmp['S_W_METH'], pct_short=s_tmp['S_PCT'],
                     ind_const=s_tmp['IND_CONST'], reb_freq=s_tmp['REB_FREQ'], tc_bps=20)
    ls_ports.append(port)

# Export tables
df_ports_stats = fn.tab_ports_stats(ls_ports, 'df_ports_stats')
df_ports_perfs = fn.tab_ports_perfs(ls_ports, 'df_ports_perfs')

# Turnover analysis

# Best portfolio without transactions cost: VQAM_25_EW_300_QLT_15_EW_200_I_1000_50_M
port_1 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='EW', pct_long=300,
                   sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=200,
                   ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=0, spr_bps=0)
port_1_TC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='EW', pct_long=300,
                      sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=200,
                      ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=0)
port_1_TC_BC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='EW', pct_long=300,
                         sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=200,
                         ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=50)

# Best portfolio with transaction costs: VQ_25_EW_300_QLT_20_EW_200_I_M
port_2 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                   sig_short='ZS_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                   ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=0, spr_bps=0)
port_2_TC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                      sig_short='ZS_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                      ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=0)
port_2_TC_BC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                         sig_short='ZS_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                         ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=50)

# Export tables
ls_ports = [port_1, port_1_TC, port_1_TC_BC, port_2, port_2_TC, port_2_TC_BC]
df_ports_stats = fn.tab_ports_stats(ls_ports, 'df_ports_TO_analysis_stats')
df_ports_perfs = fn.tab_ports_perfs(ls_ports, 'df_ports_TO_analysis_perfs')


# %%
# *** Branch: Report ***


# 100/100 portfolio analysis (market-neutral)
ls_sigs = ['ZS_VAL', 'ZS_QLT', 'ZS_VAL_QLT', 'ZS_VAL_QLT_AMOM']
ls_w_meth = ['EW', 'MN', 'RP']

df_port_analysis
dic_tmp = {}
for w_meth in ls_w_meth:
    dic_tmp_1 = {}
    for sig in ls_sigs:
        port = Portfolio(dic_data=dic_data, sig_long=sig, n_asts_long=25, w_meth_long=w_meth, pct_long=100,
                         sig_short=sig, n_asts_short=25, w_meth_short=w_meth, pct_short=100,
                         ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=0)
        df_port_chars = port.tab_port_chars()
        df_port_chars = df_port_chars[['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'MAX_DD_PRD', 'AVG_TO']]
        dic_tmp_1[sig] = df_port_chars
    df_tmp_1 = pd.concat(dic_tmp_1, axis=0).T
    dic_tmp_0[w_meth] = df_tmp_1
df_tmp_0 = pd.concat(dic_tmp_0, axis=1).T
df_tmp_0 = df_tmp_0.droplevel(2, axis=0)
df_tmp_0.to_latex(Path.joinpath(paths.get('tables'), '{}.tex'.format('stats_100')), float_format='%.4f')

# Results analysis
fn.exp_res_analysis(pct_long_short=(100, 100))
fn.exp_res_analysis(pct_long_short=(130, 30))
fn.exp_res_analysis(pct_long_short=(120, 50))
fn.exp_res_analysis(pct_long_short=(300, 200))

# Transaction costs analysis
fn.exp_TC_analysis(pct_long_short=(100, 100))
fn.exp_TC_analysis(pct_long_short=(130, 30))
fn.exp_TC_analysis(pct_long_short=(120, 50))
fn.exp_TC_analysis(pct_long_short=(300, 200))

# Sensitivity analysis
fn.exp_sens_analysis(pct_long_short=(100, 100))
fn.exp_sens_analysis(pct_long_short=(130, 30))
fn.exp_sens_analysis(pct_long_short=(120, 50))
fn.exp_sens_analysis(pct_long_short=(300, 200))




# %%
# DO NOT MODIFY ABOVE!



test = fn.get_port_stats_graph(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=120,
                               sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                               ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=50)

# Berkshire Hathaway comp
df_stock_perfs, df_stock_stats = fn.get_stats_stock(PERMNO=17778)
df_stock_perfs.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format('df_ports_BRK.B_perfs')))
df_stock_stats.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format('df_ports_BRK.B_stats')))










