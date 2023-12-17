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

# Sector average counts
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=130,
                 sig_short='ZS_VAL_QLT', n_asts_short=25, w_meth_short='EW', pct_short=30, ind_const='I', reb_freq='M')
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


# Export ports navs
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['VAL_1', 'QLT_1', 'VQ_1'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_1')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['VAL_2', 'QLT_2', 'VQ_2'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_2')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['VAL_3', 'QLT_3', 'VQ_3'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_3')

fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_11', 'VQAM_1'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_4')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_12', 'VQAM_2'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_5')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_13', 'VQAM_3'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_6')

fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_21', 'BEST_G1'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_7')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_22', 'BEST_G2'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_8')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_23', 'BEST_G3'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_9')

# Export ports stats
ls_stats = ['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'MAX_DD_PRD', 'AVG_TO',
            'ANN_ALPHA', 't_ALPHA', 'B_MKTRF', 't_MKTRF', 'B_SMB', 't_SMB', 'B_HML', 't_HML', 'R_SQUARED']
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['VAL_1', 'QLT_1', 'VQ_1'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_1')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['VAL_2', 'QLT_2', 'VQ_2'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_2')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['VAL_3', 'QLT_3', 'VQ_3'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_3')

fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_11', 'VQAM_1'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_4')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_12', 'VQAM_2'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_5')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_13', 'VQAM_3'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_6')

fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_21', 'BEST_G1'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_7')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_22', 'BEST_G2'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_8')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_23', 'BEST_G3'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_9')


# %%

def tab_sens_analysis(pct_long_short, file_name=None):
    with open(Path.joinpath(paths.get('tables'), 'df_ports_chars.pkl'), 'rb') as file:
        df_pc = pickle.load(file)
    df_pc = df_pc.loc[(df_pc['L_PCT'] == pct_long_short[0]) & (df_pc['S_PCT'] == pct_long_short[1])]

    df_sens_analysis = pd.DataFrame()
    ls_sigs = ['VAL', 'QLT', 'VQ', 'VQAM']
    df_pc_top = df_pc.loc[(df_pc['PORT_NAV'].min() > 0)].sort_values(by=['SHARPE'], ascending=False).head(200)

    i = 0
    for leg in ['L', 'S']:
        for sig in ls_sigs:
            df_sens_analysis.loc[i, 'SIG'] = leg + '_' + sig
            df_sens_analysis.loc[i, 'TOP_COUNT'] = len(df_pc_top.loc[(df_pc_top['L_SIG'] == sig)])
            df_sens_analysis.loc[i, 'DEF_COUNT'] = len(df_pc.loc[(df_pc['L_SIG'] == sig) & (df_pc['PORT_NAV'].min() < 0)])
            i += 1



    '''
    for sig in ls_sigs:
        df_sens_analysis.loc['T_L_{}'.format(sig), 'COUNT'] = len(df_pc_top.loc[df_pc_top['L_SIG'] == sig])
        df_sens_analysis.loc['T_L_{}'.format(sig), 'AVG_SHARPE'] = df_pc_top.loc[df_pc_top['L_SIG'] == sig, 'SHARPE'].mean()
        df_sens_analysis.loc['T_L_{}'.format(sig), 'AVG_MAX_DD'] = df_pc_top.loc[df_pc_top['L_SIG'] == sig, 'MAX_DD'].mean()

    for sig in ls_sigs:
        df_sens_analysis.loc['T_S_{}'.format(sig), 'COUNT'] = len(df_pc_top.loc[df_pc_top['S_SIG'] == sig])
        df_sens_analysis.loc['T_S_{}'.format(sig), 'AVG_SHARPE'] = df_pc_top.loc[df_pc_top['S_SIG'] == sig, 'SHARPE'].mean()
        df_sens_analysis.loc['T_S_{}'.format(sig), 'AVG_MAX_DD'] = df_pc_top.loc[df_pc_top['S_SIG'] == sig, 'MAX_DD'].mean()

    for sig in ls_sigs:
        df_sens_analysis.loc['B_L_{}'.format(sig), 'COUNT'] = len(df_pc_btm.loc[df_pc_btm['L_SIG'] == sig])
        df_sens_analysis.loc['B_L_{}'.format(sig), 'AVG_SHARPE'] = df_pc_btm.loc[df_pc_btm['L_SIG'] == sig, 'SHARPE'].mean()
        df_sens_analysis.loc['B_L_{}'.format(sig), 'AVG_MAX_DD'] = df_pc_btm.loc[df_pc_btm['L_SIG'] == sig, 'MAX_DD'].mean()

    for sig in ls_sigs:
        df_sens_analysis.loc['B_S_{}'.format(sig), 'COUNT'] = len(df_pc_btm.loc[df_pc_btm['S_SIG'] == sig])
        df_sens_analysis.loc['B_S_{}'.format(sig), 'AVG_SHARPE'] = df_pc_btm.loc[df_pc_btm['S_SIG'] == sig, 'SHARPE'].mean()
        df_sens_analysis.loc['B_S_{}'.format(sig), 'AVG_MAX_DD'] = df_pc_btm.loc[df_pc_btm['S_SIG'] == sig, 'MAX_DD'].mean()

    df_sens_analysis = df_sens_analysis.reset_index(drop=False)
    df_sens_analysis = df_sens_analysis.rename(columns={'index': 'SIG'})

    for sig in ['T_L', 'T_S', 'B_L', 'B_S']:
        total_count = df_sens_analysis.loc[df_sens_analysis['SIG'].str.contains(sig), 'COUNT'].sum()
        df_sens_analysis.loc[df_sens_analysis['SIG'].str.contains(sig), 'PCT'] = df_sens_analysis.loc[df_sens_analysis['SIG'].str.contains(sig), 'COUNT'] / total_count

    df_sens_analysis = df_sens_analysis[['SIG', 'COUNT', 'PCT', 'AVG_SHARPE', 'AVG_MAX_DD']]
    '''
    print(df_sens_analysis)


tab_sens_analysis(pct_long_short=(130, 30))

# %%
# TODO : Put in function
'''
port_1 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                   sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                   ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5, tc_bps=0, spr_bps=0, b_cost=False)
df_port_perf_1 = port_1.tab_port_perf()

port_2 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                   sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                   ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=0, b_cost=False)
df_port_perf_2 = port_2.tab_port_perf()

port_3 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                   sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                   ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5, tc_bps=0, spr_bps=50, b_cost=True)
df_port_perf_3 = port_3.tab_port_perf()


for i in range(len(df_port_perf_1)):
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
# ax.set_title('Portfolios Performances', size=28)
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
# ax.set_title('Portfolios Performances', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(df_tpm_1['PORT_NAV'], label='PORT_NAV' + ' (L = ' + str(port_1.pct_long) + ', S = ' + str(port_1.pct_short) + ', C = ' + str(100 - (port_1.pct_long - port_1.pct_short)) + ')', lw=3)
ax.plot(df_tpm_2['PORT_NAV'], label='PORT_NAV_TC' + ' (L = ' + str(port_2.pct_long) + ', S = ' + str(port_2.pct_short) + ', C = ' + str(100 - (port_2.pct_long - port_2.pct_short)) + ')', lw=3)
ax.plot(df_tpm_3['PORT_NAV'], label='PORT_NAV_TC_BC' + ' (L = ' + str(port_3.pct_long) + ', S = ' + str(port_3.pct_short) + ', C = ' + str(100 - (port_3.pct_long - port_3.pct_short)) + ')', lw=3)
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
# ax.set_title('Portfolios Performances', size=28)
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

# Table stats long vs short
df_port_chars_1 = port_1.tab_port_chars(output_perf=False)
df_port_chars_1_L = df_port_chars_1[['L_ANN_MEAN', 'L_ANN_VOL', 'L_SHARPE', 'L_MAX_DD', 'L_CALMAR', 'L_AVG_TO', 'L_NORM_HI']]
df_port_chars_1_L = df_port_chars_1_L.rename(columns={'L_ANN_MEAN': 'ANN_MEAN', 'L_ANN_VOL': 'ANN_VOL', 'L_SHARPE': 'SHARPE', 'L_MAX_DD': 'MAX_DD', 'L_CALMAR': 'CALMAR', 'L_AVG_TO': 'AVG_TO', 'L_NORM_HI': 'NORM_HI'})
df_port_chars_1_S = df_port_chars_1[['S_ANN_MEAN', 'S_ANN_VOL', 'S_SHARPE', 'S_MAX_DD', 'S_CALMAR', 'S_AVG_TO', 'S_NORM_HI']]
df_port_chars_1_S = df_port_chars_1_S.rename(columns={'S_ANN_MEAN': 'ANN_MEAN', 'S_ANN_VOL': 'ANN_VOL', 'S_SHARPE': 'SHARPE', 'S_MAX_DD': 'MAX_DD', 'S_CALMAR': 'CALMAR', 'S_AVG_TO': 'AVG_TO', 'S_NORM_HI': 'NORM_HI'})

df_port_chars_2 = port_2.tab_port_chars(output_perf=False)
df_port_chars_2_L = df_port_chars_2[['L_ANN_MEAN', 'L_ANN_VOL', 'L_SHARPE', 'L_MAX_DD', 'L_CALMAR', 'L_AVG_TO', 'L_NORM_HI']]
df_port_chars_2_L = df_port_chars_2_L.rename(columns={'L_ANN_MEAN': 'ANN_MEAN', 'L_ANN_VOL': 'ANN_VOL', 'L_SHARPE': 'SHARPE', 'L_MAX_DD': 'MAX_DD', 'L_CALMAR': 'CALMAR', 'L_AVG_TO': 'AVG_TO', 'L_NORM_HI': 'NORM_HI'})
df_port_chars_2_S = df_port_chars_2[['S_ANN_MEAN', 'S_ANN_VOL', 'S_SHARPE', 'S_MAX_DD', 'S_CALMAR', 'S_AVG_TO', 'S_NORM_HI']]
df_port_chars_2_S = df_port_chars_2_S.rename(columns={'S_ANN_MEAN': 'ANN_MEAN', 'S_ANN_VOL': 'ANN_VOL', 'S_SHARPE': 'SHARPE', 'S_MAX_DD': 'MAX_DD', 'S_CALMAR': 'CALMAR', 'S_AVG_TO': 'AVG_TO', 'S_NORM_HI': 'NORM_HI'})

dic_port_chars_L = {'L': df_port_chars_1_L, 'L_TC': df_port_chars_2_L}
df_port_chars_L = pd.concat(dic_port_chars_L, axis=0).T
dic_port_chars_S = {'S': df_port_chars_1_S, 'S_TC': df_port_chars_2_S}
df_port_chars_S = pd.concat(dic_port_chars_S, axis=0).T
dic_port_chars = {'L': df_port_chars_L, 'S': df_port_chars_S}
df_port_chars = pd.concat(dic_port_chars, axis=1).T
df_port_chars = df_port_chars.droplevel(2, axis=0)
df_port_chars.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format('stats_L_S_' + port_1.port_name)))

# Table  stats LS vs LA
df_port_chars_1 = port_1.tab_port_chars(output_perf=False)
df_port_chars_1_LS = df_port_chars_1[['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'CALMAR', 'AVG_TO']]
df_port_chars_1_L = df_port_chars_1[['L_ANN_MEAN', 'L_ANN_VOL', 'L_SHARPE', 'L_MAX_DD', 'L_CALMAR', 'L_AVG_TO']]
df_port_chars_1_L = df_port_chars_1_L.rename(columns={'L_ANN_MEAN': 'ANN_MEAN', 'L_ANN_VOL': 'ANN_VOL', 'L_SHARPE': 'SHARPE', 'L_MAX_DD': 'MAX_DD', 'L_CALMAR': 'CALMAR', 'L_AVG_TO': 'AVG_TO'})
df_port_chars_2 = port_2.tab_port_chars(output_perf=False)
df_port_chars_2_LS = df_port_chars_1[['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'CALMAR', 'AVG_TO']]
df_port_chars_2_L = df_port_chars_2[['L_ANN_MEAN', 'L_ANN_VOL', 'L_SHARPE', 'L_MAX_DD', 'L_CALMAR', 'L_AVG_TO']]
df_port_chars_2_L = df_port_chars_2_L.rename(columns={'L_ANN_MEAN': 'ANN_MEAN', 'L_ANN_VOL': 'ANN_VOL', 'L_SHARPE': 'SHARPE', 'L_MAX_DD': 'MAX_DD', 'L_CALMAR': 'CALMAR', 'L_AVG_TO': 'AVG_TO'})
df_port_chars_3 = port_3.tab_port_chars(output_perf=False)
df_port_chars_3_LS = df_port_chars_1[['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'CALMAR', 'AVG_TO']]

dic_port_chars_LS = {'LS': df_port_chars_1_LS, 'LS_TC': df_port_chars_2_LS, 'LS_TC_BC': df_port_chars_3_LS}
df_port_chars_LS = pd.concat(dic_port_chars_LS, axis=0).T
dic_port_chars_L = {'L': df_port_chars_1_L, 'L_TC': df_port_chars_2_L}
df_port_chars_L = pd.concat(dic_port_chars_L, axis=0).T
dic_port_chars = {'LS': df_port_chars_LS, 'L': df_port_chars_L}
df_port_chars = pd.concat(dic_port_chars, axis=1).T
df_port_chars = df_port_chars.droplevel(2, axis=0).T
df_port_chars.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format('stats_LS_LA_' + port_1.port_name)))
'''

# Portfolios stats
def tab_port_stats(list_port,file_name):
    dic_ports_stats = {}
    j = 1
    for i in list_port:
        df_port_chars = i.tab_port_chars(output_perf=False)
        df_port_stats = df_port_chars[['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'MAX_DD_PRD', 'AVG_TO',
                                       'ANN_ALPHA', 't_ALPHA', 'B_MKTRF', 't_MKTRF', 'B_SMB', 't_SMB', 'B_HML', 't_HML', 'B_UMD', 't_UMD', 'R_SQUARED',
                                       'L_SIG', 'L_N_ASTS', 'L_W_METH', 'L_PCT', 'S_SIG', 'S_N_ASTS', 'S_W_METH', 'S_PCT', 'IND_CONST', 'REB_FREQ', 'PORT_NAV_T']]
        dic_ports_stats[str(j) + '_' + i.port_name] = df_port_stats
        j += 1
    df_ports_stats = pd.concat(dic_ports_stats, axis=0).droplevel(1, axis=0)
    df_ports_stats.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format(file_name)))

    return df_ports_stats

# Port selections
with open(Path.joinpath(paths.get('output'), 'tables', 'df_ports_chars_3.pkl'), 'rb') as file:
    df_ports_chars = pickle.load(file)

ls_keys = ['VAL_1', 'QLT_1', 'VQ_1', 'VAL_2', 'QLT_2', 'VQ_2', 'VAL_3', 'QLT_3', 'VQ_3',
           'BEST_11', 'VQAM_11', 'BEST_12', 'VQAM_12', 'BEST_13', 'VQAM_13',
           'BEST_21', 'BEST_G1', 'BEST_22', 'BEST_G2', 'BEST_23', 'BEST_G3']
ls_values = [812, 1620, 3240, 818, 1626, 3246, 830, 1638, 4070,
             3240, 5580, 1626, 5676, 4070, 5688,
             3240, 3780, 1626, 3786, 4070, 3888]
dic_sigs = {'VAL': 'ZS_VAL', 'QLT': 'ZS_QLT', 'VQ': 'ZS_VAL_QLT', 'VQAM': 'ZS_VAL_QLT_AMOM'}

# Export port stats
ls_keys_1 = ls_keys
ls_values_1 = ls_values
dic_selected_ports = dict(zip(ls_keys_1, ls_values_1))

list_port = []
for i in range(len(ls_keys_1)):
    s_tmp = df_ports_chars.iloc[dic_selected_ports[ls_keys_1[i]]]
    port = Portfolio(dic_data=dic_data, sig_long=dic_sigs[s_tmp['L_SIG']], n_asts_long=s_tmp['L_N_ASTS'], w_meth_long=s_tmp['L_W_METH'], pct_long=s_tmp['L_PCT'],
                     sig_short=dic_sigs[s_tmp['S_SIG']], n_asts_short=s_tmp['S_N_ASTS'], w_meth_short=s_tmp['S_W_METH'], pct_short=s_tmp['S_PCT'],
                     ind_const=s_tmp['IND_CONST'], reb_freq=s_tmp['REB_FREQ'], tc_bps=20)
    list_port.append(port)
    print(port.port_name)

df_ports_stats = tab_port_stats(list_port,'df_ports_stats')


# Transaction cost analysis
ls_keys_1 = ['BEST_G1', 'BEST_G2', 'BEST_G3']
ls_values_1 = [3780, 3786, 3888]
dic_selected_ports = dict(zip(ls_keys_1, ls_values_1))

list_port = []
for i in range(len(ls_keys_1)):
    s_tmp = df_ports_chars.iloc[dic_selected_ports[ls_keys_1[i]]]
    port = Portfolio(dic_data=dic_data, sig_long=dic_sigs[s_tmp['L_SIG']], n_asts_long=s_tmp['L_N_ASTS'], w_meth_long=s_tmp['L_W_METH'], pct_long=s_tmp['L_PCT'],
                     sig_short=dic_sigs[s_tmp['S_SIG']], n_asts_short=s_tmp['S_N_ASTS'], w_meth_short=s_tmp['S_W_METH'], pct_short=s_tmp['S_PCT'],
                     ind_const=s_tmp['IND_CONST'], reb_freq=s_tmp['REB_FREQ'], tc_bps=0)
    list_port.append(port)
    port = Portfolio(dic_data=dic_data, sig_long=dic_sigs[s_tmp['L_SIG']], n_asts_long=s_tmp['L_N_ASTS'], w_meth_long=s_tmp['L_W_METH'], pct_long=s_tmp['L_PCT'],
                     sig_short=dic_sigs[s_tmp['S_SIG']], n_asts_short=s_tmp['S_N_ASTS'], w_meth_short=s_tmp['S_W_METH'], pct_short=s_tmp['S_PCT'],
                     ind_const=s_tmp['IND_CONST'], reb_freq=s_tmp['REB_FREQ'], tc_bps=20)
    list_port.append(port)
    port = Portfolio(dic_data=dic_data, sig_long=dic_sigs[s_tmp['L_SIG']], n_asts_long=s_tmp['L_N_ASTS'], w_meth_long=s_tmp['L_W_METH'], pct_long=s_tmp['L_PCT'],
                     sig_short=dic_sigs[s_tmp['S_SIG']], n_asts_short=s_tmp['S_N_ASTS'], w_meth_short=s_tmp['S_W_METH'], pct_short=s_tmp['S_PCT'],
                     ind_const=s_tmp['IND_CONST'], reb_freq=s_tmp['REB_FREQ'], tc_bps=20, spr_bps=50)
    list_port.append(port)
    print(port.port_name)

df_ports_stats = tab_port_stats(list_port,'df_ports_BEST_G_TC_stats')

def tab_perf_export(list_port,file_name):
    dic_ports_stats = {}
    j = 1
    for i in list_port:
        df_port_perf = i.tab_port_perf().set_index('DATE')['PORT_NAV']
        dic_ports_stats[str(j) + '_' + i.port_name] = df_port_perf
        j += 1
    df_ports_perf = pd.concat(dic_ports_stats, axis=1)
    df_ports_perf.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format(file_name)))
    return df_ports_perf

df_ports_perf = tab_perf_export(list_port,'df_ports_BEST_G_TC_perfs')



# Turnover analysis

# Best portfolio without transactions cost: VQAM_25_EW_300_QLT_15_EW_200_I_1000_50_M
port_1 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5,tc_bps=0, spr_bps=0)

port_1_TC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0)

port_1_TC_BC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=50)

# Best portfolio with transaction costs: VQ_25_EW_300_QLT_20_EW_200_I_M
port_2 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5,tc_bps=0, spr_bps=0)

port_2_TC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0)

port_2_TC_BC = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=50)

list_port = [port_1, port_1_TC, port_1_TC_BC, port_2, port_2_TC, port_2_TC_BC]
df_ports_stats = tab_port_stats(list_port,'df_ports_TO_analysis_stats')
df_ports_perf = tab_perf_export(list_port,'df_ports_TO_analysis_perfs')