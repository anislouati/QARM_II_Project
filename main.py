# Import packages
from datetime import datetime
from itertools import product
from operator import attrgetter
from pathlib import Path
from scipy.optimize import minimize, OptimizeResult
from scripts.functions import Portfolio
from scripts.functions import paths
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle
import scripts.functions as fn
import statsmodels.api as sm
import time
import warnings
import matplotlib.pyplot as plt
import seaborn as sns

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
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************



port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='MN', pct_long=300,
                 sig_short='ZS_VAL_QLT_AMOM', n_asts_short=25, w_meth_short='MN', pct_short=200,
                 ind_const='NI', reb_freq='Y', min_short_me=1000, max_short_cl=0.4, tc_bps=20)
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)



# TODO: check results
with open(Path.joinpath(paths.get('output'), 'df_ports_chars.pkl'), 'rb') as file:
    df_ports_chars = pickle.load(file)







# %%
# Illustrations
df_sec_avg_counts = fn.get_df_sec_avg_counts(dic_data)







# %%
# **************************************************
# *** Branch: PORTFOLIO ANALYSIS                 ***
# **************************************************

port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_VAL_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=0)
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)



test = dic_data['df_facs_data']


def perf_output():
    return


for i in range(len(df_port_perf)):
    if i == 0:
        df_port_perf.loc[i, ['L_NAV']] = 100
        df_port_perf.loc[i, ['S_NAV']] = 100
    else:
        df_port_perf.loc[i, ['L_NAV']] = np.array(df_port_perf.loc[i - 1, ['L_NAV']])[0] * (1 + np.array(df_port_perf.loc[i, ['L_RTNS']])[0])
        df_port_perf.loc[i, ['S_NAV']] = np.array(df_port_perf.loc[i - 1, ['S_NAV']])[0] * (1 + np.array(df_port_perf.loc[i, ['S_RTNS']])[0])

df_tpm = df_port_perf.set_index('DATE')

# Plot portfolio performances
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
#ax.set_title('Portfolios Performances', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(df_tpm['PORT_NAV'],
        label='PORT_NAV' + ' (L = ' + str(port.pct_long) + ', S = ' + str(port.pct_short) + ', C = ' + str(100 - (port.pct_long - port.pct_short)) + ')',
        color='red', lw=3)
ax.plot(df_tpm['L_NAV'], label='L_NAV' + ' (' + str(port.sig_long) + ', ' + str(port.n_asts_long) + ', ' + str(port.w_meth_long) + ', ' + str(port.ind_const) + ', ' + str(port.reb_freq) + ')', color='green', lw=3)
ax.plot(df_tpm['S_NAV'], label='S_NAV' + ' (' + str(port.sig_short) + ', ' + str(port.n_asts_short) + ', ' + str(port.w_meth_short) + ', ' + str(port.ind_const) + ', ' + str(port.reb_freq) + ')', color='blue', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('figures'), 'port_perfs_' + port.port_name + '.png'))
plt.close()


# %%




port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_VAL_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5)

df_port_perf = port.tab_port_perf()

dic_asts_data = dic_data['dic_asts_data']
ls_dates = list(dic_asts_data.keys())
df_tmp = dic_asts_data[ls_dates[-1]]


def get_df_sec_avg_counts(dic_data):
    dic_asts_data = dic_data['dic_asts_data']
    ls_dates = list(dic_asts_data.keys())
    dic_GICS = {bytes('10', 'utf-8'): 'Energy', bytes('15', 'utf-8'): 'Materials', bytes('20', 'utf-8'): 'Industrials',
                bytes('25', 'utf-8'): 'Consumer Discretionary', bytes('30', 'utf-8'): 'Consumer Stables', bytes('35', 'utf-8'): 'Health Care',
                bytes('40', 'utf-8'): 'Financials', bytes('45', 'utf-8'): 'Information Technology', bytes('50', 'utf-8'): 'Communication Services',
                bytes('55', 'utf-8'): 'Utilities', bytes('60', 'utf-8'): 'Real Estate'}

    ls_dfs = []
    for i in range(len(ls_dates)):
        s_tmp_1 = pd.Series([np.nan for i in range(len(list(dic_GICS.keys())))], index=sorted(list(dic_GICS.keys())))
        s_tmp_2 = dic_asts_data[ls_dates[i]]['GSECTOR'].value_counts().rename(None)
        for sec in s_tmp_2.index.tolist():
            s_tmp_1[sec] = s_tmp_2[sec]
            s_tmp_1 = s_tmp_1.rename(ls_dates[i])
        ls_dfs += [pd.DataFrame(s_tmp_1).transpose()]

    df_sec_counts = pd.concat(ls_dfs, axis=0).fillna(0)
    df_sec_counts = df_sec_counts.reset_index(drop=False, names=['DATE'])
    df_sec_counts['YEAR'] = df_sec_counts['DATE'].dt.year.astype(float)
    df_sec_avg_counts = df_sec_counts.groupby('YEAR')[list(dic_GICS.keys())].mean()
    df_sec_avg_counts = df_sec_avg_counts.rename(columns=dic_GICS)
    return df_sec_avg_counts

# %%%

import plotly.graph_objs as go
import plotly.offline as pyo
import pandas as pd
import numpy as np

with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'rb') as file:
    dic_data = pickle.load(file)

def plot_zscores(dic_data, date, ls_zscores, leg):
    dic_asts_data = dic_data['dic_asts_data']
    df_zscores = dic_asts_data[date]
    df_zscores = df_zscores[['PERMNO', 'CONM', 'TIC'] + ls_zscores]
    ls_permnos = df_zscores['PERMNO'].unique().tolist()
    df_zscores['ZS_INT'] = df_zscores[ls_zscores].mean(axis=1, skipna=False)

    ascending = False
    if leg == 'L':
        ascending = False
    elif leg == 'S':
        ascending = True

    n_asts = 50
    dic_s_zscores = {}
    for i in range(len(ls_zscores)):
        dic_s_zscores[i] = pd.Series(list(df_zscores[ls_zscores[i]]), index=ls_permnos, dtype='float64').nlargest(n_asts).sort_values(ascending=ascending)
    dic_s_zscores[len(ls_zscores)] = pd.Series(list(df_zscores['ZS_INT']), index=ls_permnos, dtype='float64').nlargest(n_asts).sort_values(ascending=ascending)

    if len(ls_zscores) == 2:
        ls_asts_0 = sorted(dic_s_zscores[0].index.tolist())  # ZS_0
        ls_asts_1 = sorted(dic_s_zscores[1].index.tolist())  # ZS_1
        ls_asts_2 = sorted(dic_s_zscores[2].index.tolist())  # ZS_INT

        ls_asts_3 = [ast for ast in ls_asts_0 if ast not in ls_asts_2]  # Only ZS_0
        ls_asts_4 = [ast for ast in ls_asts_1 if ast not in ls_asts_2]  # Only ZS_1
        ls_asts_5 = [ast for ast in ls_permnos if (ast not in ls_asts_0) and (ast not in ls_asts_1) and (ast not in ls_asts_2)]  # All other

        # Create scatter plot traces
        trace_0 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_2), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_2), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='green'), name='All Points')
        trace_1 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='red'), name='All Points')
        trace_2 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='blue'), name='All Points')
        trace_3 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[1]],
                             mode='markers', marker=dict(size=8, color='black'), name='All Points')

        # Create layout
        layout = go.Layout(title='Interactive Scatter Plot with Highlighted Points',
                           xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'))

        # Create figure with both traces
        fig = go.Figure(data=[trace_0, trace_1, trace_2, trace_3], layout=layout)

        # Save plot as an HTML file
        pyo.plot(fig, filename='scatter_plot_highlighted.html')

plot_zscores(dic_data, date=datetime(2000, 12, 31), ls_zscores=['ZS_VAL', 'ZS_QLT'], leg='L')

# %%







np.random.seed(0)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100)

data = {'x': x, 'y': y}
df = pd.DataFrame(data)

# Create scatter plot trace
trace = go.Scatter(x=df['x'], y=df['y'], mode='markers', marker=dict(size=8, color='blue'), name='Scatter Plot')

# Create layout
layout = go.Layout(title='Interactive Scatter Plot', xaxis=dict(title='X-axis'), yaxis=dict(title='Y-axis'))

# Create figure
fig = go.Figure(data=[trace], layout=layout)

# Save plot as an HTML file
pyo.plot(fig, filename='scatter_plot.html')




# Sample data for a 3D scatter plot
np.random.seed(0)
x = np.random.randn(100)
y = 2 * x + np.random.randn(100)
z = 3 * x - y + np.random.randn(100)  # Adding a third dimension 'z'

data = {'x': x, 'y': y, 'z': z}  # Including 'z' in the data
df = pd.DataFrame(data)

# Create 3D scatter plot trace
trace = go.Scatter3d(x=df['x'], y=df['y'], z=df['z'], mode='markers',
                      marker=dict(size=8, color='blue'), name='Scatter Plot')

# Create layout for 3D plot
layout = go.Layout(title='Interactive 3D Scatter Plot', scene=dict(xaxis=dict(title='X-axis'),
                                                                  yaxis=dict(title='Y-axis'),
                                                                  zaxis=dict(title='Z-axis')))

# Create figure
fig = go.Figure(data=[trace], layout=layout)

# Save 3D plot as an HTML file
pyo.plot(fig, filename='scatter_3d_plot.html')
