# Import packages
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from scipy.optimize import minimize
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

# # Checkpoint data
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
# Push forward fundamentals (out-of-sample) ==> Example: info published on 31/03 (Q_t) available starting 30/04 (Q_t_1)
df_data = fn.preprocessing_6(df_data)

# Create additional variables (fundamental metrics)
df_data = fn.preprocessing_7(df_data)

# Checkpoint data
# df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)


# %%
# **************************************************
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************

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

# Create data dictionary
dic_data = {}
ls_dates = sorted(df_data['DATE'].unique().tolist())

for date in tqdm(ls_dates, desc='Data dictionary'):
    df_tmp = df_data[df_data['DATE'] == date]
    df_tmp = df_tmp.dropna(how='any')  # Remark: we drop all rows with at least one nan (by date)

    min_dvol = 25  # Minimum dollar volume (mil., monthly)
    min_me = 250  # Minimum market cap (mil.)
    df_tmp = df_tmp[(df_tmp['DVOL'] >= min_dvol) & (df_tmp['ME'] >= min_me)]
    df_tmp = fn.get_ZS(df_tmp)

    ls_selected_cols = ['PERMNO', 'DATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR',
                        'PRCCM', 'TRT1M', 'SPRDPCT', 'DVOL', 'SPRTRN', 'ME',
                        'VOL_TRT1M', 'VOL_SPRTRN', 'BETA',
                        'LS_PTRT1M', 'NTRT1M', 'LS_NTRT1M_1Q', 'LS_NTRT1M_1Y',
                        'ZS_VAL', 'ZS_PROF', 'ZS_GWTH', 'ZS_SAF', 'ZS_QLT', 'ZS_MOM', 'ZS_VAL_QLT', 'ZS_VAL_QLT_MOM']
    df_tmp = df_tmp[ls_selected_cols]
    df_tmp = df_tmp.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
    dic_data[date] = df_tmp


# %%
# Portfolio construction


def get_ls_asts(df_data, indicator, n_asts, ind_const, leg):
    if indicator not in ['ZS_VAL', 'ZS_QLT', 'ZS_MOM', 'ZS_VAL_QLT', 'ZS_VAL_QLT_MOM']:
        raise ValueError('Unsupported indicator, try: [\'ZS_VAL\', \'ZS_QLT\', \'ZS_MOM\', \'ZS_VAL_QLT\', \'ZS_VAL_QLT_MOM\']')
    if ind_const not in ['I', 'NI']:
        raise ValueError('Unsupported industry constraint, try: [\'I\', \'NI\']')
    if leg not in ['L', 'S']:
        raise ValueError('Unsupported leg type, try: [\'L\', \'S\']')

    ls_asts = []
    ls_secs = df_data['GSECTOR'].unique().tolist()

    if ind_const == 'I':
        dic_asts = {}
        for sec in ls_secs:
            df_tmp = df_data.loc[df_data['GSECTOR'] == sec, ['PERMNO', indicator]]
            if leg == 'L':
                dic_asts[sec] = df_tmp.sort_values(by=[indicator], ascending=False)['PERMNO'].tolist()
            elif leg == 'S':
                dic_asts[sec] = df_tmp.sort_values(by=[indicator], ascending=True)['PERMNO'].tolist()
            if len(dic_asts[sec]) < np.ceil((n_asts * 4) / len(ls_secs)):  # Remove too small sectors
                del dic_asts[sec]
        dic_asts = dict(sorted(dic_asts.items(), key=lambda x: len(x[1]), reverse=True))  # Sort by sector size

        ls_secs = list(dic_asts.keys())
        i = 0
        while len(ls_asts) < n_asts:
            s = 0
            while (len(ls_asts) < n_asts) and (s < len(ls_secs)):
                ls_asts += [dic_asts[ls_secs[s]][i]]
                s += 1
            i += 1

    elif ind_const == 'NI':
        if leg == 'L':
            ls_asts = df_data.loc[df_data[indicator].nlargest(n_asts).index, 'PERMNO'].tolist()
        elif leg == 'S':
            ls_asts = df_data.loc[df_data[indicator].nsmallest(n_asts).index, 'PERMNO'].tolist()

    ls_asts = sorted(ls_asts)  # Sort by PERMNO
    return ls_asts


def get_s_port_w(df_data, indicator, n_asts, ind_const, w_method, leg):
    if w_method not in ['EW', 'VW', 'MV', 'MN', 'RP']:
        raise ValueError('Unsupported weighting method, try: [\'EW\', \'VW\', \'MV\', \'MN\', \'RP\']')

    s_port_w = pd.Series(dtype='float64')
    ls_asts = get_ls_asts(df_data, indicator, n_asts, ind_const, leg)

    # Equal weighting
    if w_method == 'EW':
        s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')

    # Value weighting
    elif w_method == 'VW':
        s_me = df_data.loc[df_data['PERMNO'].isin(ls_asts), 'ME'].rename(None)
        s_port_w = pd.Series((s_me / s_me.sum()).values, index=ls_asts, dtype='float64')

    # Minimum variance
    elif w_method == 'MV':
        # Initialization
        df_rtns = pd.DataFrame(df_data.loc[df_data['PERMNO'].isin(ls_asts), 'LS_PTRT1M'].tolist()).T
        df_rtns.columns = ls_asts
        df_covmat = df_rtns.cov()
        a_covmat = np.array(df_covmat * 12)  # Annualized from monthly data

        # Useful functions
        def get_port_var(w):
            return w.T @ a_covmat @ w

        def cons1(w):
            return np.sum(w) - 1

        # Optimization
        x0 = np.ones(n_asts) / n_asts
        bnds = [(0.005, 1) for i in range(n_asts)]  # Long-only, min 0.5% per asset
        cons = {'type': 'eq', 'fun': cons1}
        with warnings.catch_warnings():
            warnings.filterwarnings(action='ignore', category=RuntimeWarning)
            result = minimize(fun=get_port_var, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

        # Return output
        if not result.success:  # Assumption: if optimization unsuccessful, use equal weighting (at this date)
            s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')
        else:
            s_port_w = pd.Series(result.x, index=ls_asts, dtype='float64')

    # Market neutral (zero beta)
    elif w_method == 'MN':
        # Initialization
        s_betas = df_data.loc[df_data['PERMNO'].isin(ls_asts), 'BETA'].rename(None)
        a_betas = np.array(s_betas)

        # Useful functions
        def get_port_beta(w):
            return w.T @ a_betas

        def obj_fun(w):
            diff = (get_port_beta(w) - 1) ** 2
            return diff  # Minimize to have Beta_P = 1 (Beta_L - Beta_S = 1 - 1 = 0)

        def cons1(w):
            return np.sum(w) - 1

        # Optimization
        x0 = np.ones(n_asts) / n_asts
        bnds = [(0.005, 1) for i in range(n_asts)]  # Long-only, min 0.5% per asset
        cons = {'type': 'eq', 'fun': cons1}
        with warnings.catch_warnings():
            warnings.filterwarnings(action='ignore', category=RuntimeWarning)
            result = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

        # Return output
        if not result.success:
            s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')
        else:
            s_port_w = pd.Series(result.x, index=ls_asts, dtype='float64')

    # Risk parity (equally-weighted risk contributions)
    elif w_method == 'RP':
        # Initialization
        df_rtns = pd.DataFrame(df_data.loc[df_data['PERMNO'].isin(ls_asts), 'LS_PTRT1M'].tolist()).T
        df_rtns.columns = ls_asts
        df_covmat = df_rtns.cov()
        a_covmat = np.array(df_covmat * 12)  # Annualized from monthly data

        # Useful functions
        def obj_fun(w):
            a_Sw = a_covmat @ w
            diff = 0
            for i in range(n_asts):
                for j in range(n_asts):
                    diff += ((w[i] * a_Sw[i]) - (w[j] * a_Sw[j])) ** 2
            return diff  # Minimize to have TRC_i = TRC_j ==> (w_i * MRC_i) = (w_j * MRC_j)

        def cons1(w):
            return np.sum(w) - 1

        # Optimization
        x0 = np.ones(n_asts) / n_asts
        bnds = [(0.005, 1) for i in range(n_asts)]  # Long-only, min 0.5% per asset
        cons = {'type': 'eq', 'fun': cons1}
        with warnings.catch_warnings():
            warnings.filterwarnings(action='ignore', category=RuntimeWarning)
            result = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

        # Return output
        if not result.success:
            s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')
        else:
            s_port_w = pd.Series(result.x, index=ls_asts, dtype='float64')
    return s_port_w



'''
for date in tqdm(ls_dates):
    df_tmp = dic_data[date]
    s_port_w = get_s_port_w(df_tmp, indicator='ZS_QLT', n_asts=25, ind_const='I', w_method='RP', leg='L')
'''


ls_lens = [len(dic_data[date]) for date in list(dic_data.keys())]
df_tmp = dic_data[ls_dates[0]]
ls_asts = get_ls_asts(df_tmp, indicator='ZS_VAL', n_asts=25, ind_const='I', leg='L')
zzz = df_tmp[df_tmp['PERMNO'].isin(ls_asts)]
print(zzz['GSECTOR'].value_counts())
s_port_w = get_s_port_w(df_tmp, indicator='ZS_QLT', n_asts=25, ind_const='I', w_method='RP', leg='L')



# TODO: tab_port_perf(df_data: , indicator, n_asts, ind_const, w_method, reb_freq)

def tab_port_perf(dic_data: dict, indicator: str, n_asts: int, ind_const: str, w_method: str, reb_freq: str):
    """
    Function to compute portfolio performance.

    :param dic_data: Dictionary containing data.
    :param indicator: Indicator for portfolio construction ('ZS_VAL', 'ZS_QLT', 'ZS_MOM', 'ZS_VAL_QLT', 'ZS_VAL_QLT_MOM').
    :param n_asts: Number of assets in each leg (L/S) of the portfolio.
    :param ind_const: Industry constraint ('I', 'NI').
    :param w_method: Weighting method for portfolio construction ('EW', 'VW', 'MV', 'MN', 'RP').
    :param reb_freq: Rebalancing frequency ('M', 'Q', 'Y').
    :return: Dataframe containing portfolio composition (L/S) and performance data.
    """

    if reb_freq not in ['M', 'Q', 'Y']:
        raise ValueError('Unsupported rebalancing frequency, try: [\'M\', \'Q\', \'Y\']')

    dic_cols = {'DATE': 'datetime64[ns]', 'PORT_VAL': 'float64', 'PORT_RTN': 'float64',
                'L_VAL': 'float64', 'L_RTN': 'float64', 'LS_L_ASTS': 'object', 'LS_L_W': 'object', 'LS_L_POS': 'object',
                'S_VAL': 'float64', 'S_RTN': 'float64', 'LS_S_ASTS': 'object', 'LS_S_W': 'object', 'LS_S_POS': 'object'}
    df_port_perf = pd.DataFrame(columns=list(dic_cols.keys())).astype(dtype=dic_cols)
    port_name = '_'.join([indicator[3:], str(int(n_asts)), ind_const, w_method, reb_freq])
    ls_dates = list(dic_data.keys())

    # Number of (EOM) dates in rebalancing period
    n_dates = 0
    if reb_freq == 'M':
        n_dates = 1
    elif reb_freq == 'Q':
        n_dates = 3
    elif reb_freq == 'Y':
        n_dates = 12

    # Rebalancing dates
    ls_reb_dates = []
    t = 0  # Include initial allocation date
    while t < len(ls_dates):
        if (t % n_dates) == 0:
            ls_reb_dates += [ls_dates[t]]
        t += 1
    ls_reb_dates = ls_reb_dates[:-1]  # Rebalance last time @T-1 (T: end period)

    # Initial allocation date
    df_port_perf.loc[0, 'DATE'] = ls_dates[0]
    df_port_perf.loc[0, ['PORT_VAL', 'L_VAL', 'S_VAL']] = 100

    # Iteration over rebalancing dates
    for i in tqdm(range(1), desc=port_name):
        df_tmp = dic_data[ls_reb_dates[i]]
        s_long_w = get_s_port_w(df_tmp, indicator, n_asts, ind_const, w_method, leg='L')
        df_port_perf.at[(n_dates * i), 'LS_L_ASTS'] = s_long_w.index.tolist()
        df_port_perf.at[(n_dates * i), 'LS_L_W'] = s_long_w.values.tolist()
        df_port_perf.at[(n_dates * i), 'LS_L_POS'] = (s_long_w * df_port_perf.loc[(n_dates * i), 'L_VAL']).tolist()

        s_short_w = get_s_port_w(df_tmp, indicator, n_asts, ind_const, w_method, leg='S')
        df_port_perf.at[(n_dates * i), 'LS_S_ASTS'] = s_short_w.index.tolist()
        df_port_perf.at[(n_dates * i), 'LS_S_W'] = s_short_w.values.tolist()
        df_port_perf.at[(n_dates * i), 'LS_S_POS'] = (s_short_w * df_port_perf.loc[(n_dates * i), 'S_VAL']).tolist()

        for j in range(n_dates):
            # TODO: carry forward, get next returns based on
            # TODO: look only at LS_NTR1M_1Y, remove other (look at 1, 3, 12 elements)
        # For next n_dates...





    return df_port_perf




s_port_w = get_s_port_w(df_tmp, indicator='ZS_QLT', n_asts=25, ind_const='I', w_method='RP', leg='L')

df.at[0, 'LS_L_POS'] = s_port_w.index.tolist()
print()
print(s_port_w.values.tolist() * 3)

zzz = tab_port_perf(dic_data, indicator='ZS_VAL', n_asts=25, ind_const='I', w_method='EW', reb_freq='M')

# %%






def tab_port_perf(df_rtns, df_port_w):
    df_rtns_2 = df_rtns.copy()  # Local copy, for in-scope modification
    df_rtns_2 = df_rtns_2[df_port_w.columns]  # Restrict to assets used in allocations
    wealth = 100
    dic_asset_perf = {}
    s_port_perf = pd.Series(dtype='float64')

    init_all_date = df_port_w.index[0]
    port_composition = pd.Series(df_port_w.loc[init_all_date] * wealth, dtype='float64')
    dic_asset_perf[init_all_date] = port_composition
    s_port_perf[init_all_date] = port_composition.sum()

    ls_reb_dates = df_port_w.index.tolist()[1:-1]  # NOTA: we rebalance last time @T-1 (T: last end of month date), last weights not included!
    ls_dates = [date for date in df_rtns_2.index if date > init_all_date]  # NOTA: we start loop at first day after initial allocation

    for date in ls_dates:
        r = np.array(df_rtns_2.loc[date] + 1)
        port_composition = port_composition * r
        dic_asset_perf[date] = port_composition
        s_port_perf[date] = port_composition.sum()
        wealth = port_composition.sum()
        if date in ls_reb_dates:
            port_composition = pd.Series(df_port_w.loc[date] * wealth)

    df_asset_perf = pd.DataFrame.from_dict(dic_asset_perf, orient='index').fillna(0).sort_index(axis=1)
    return df_asset_perf, s_port_perf






# TODO: tab_ports_chars(ls_dfs, )





# %%




# df_VAL_25_I_EW_Q_L
# Weighting: EW, VW, MV, RP, MN
# Ind_const: True, False
# Indicator (ZS): VAL, QLT, VAL_QLT, VAL_QLT_MOM
# Rebalancing: quarterly (Q), yearly (Y)
# Performance: Mean, Vol, SR, MaxDD, FF5 (alpha, betas), Calamar, Turnover, Normalized Hierfindahl Index or Gini




# %%
# **************************************************
# *** Branch: COMMENTS                           ***
# **************************************************


'''
df_tmp = dic_data[ls_dates[-1]]
ls_asts = get_ls_asts(df_tmp, n_asts=25, ind_const=True, indicator='ZS_VAL', leg='long')
zzz = df_tmp[df_tmp['PERMNO'].isin(ls_asts)]
'''