# Import packages
from pathlib import Path
from scipy.optimize import minimize, OptimizeResult
from tqdm import tqdm
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pickle
import plotly.graph_objs as go
import plotly.offline as pyo
import seaborn as sns
import statsmodels.api as sm
import warnings

# Project directories paths (README: modify if necessary!)
paths = {'main': Path.cwd()}
paths.update({'data': Path.joinpath(paths.get('main'), 'data')})
paths.update({'output': Path.joinpath(paths.get('main'), 'output')})
paths.update({'scripts': Path.joinpath(paths.get('main'), 'scripts')})
paths.update({'figures': Path.joinpath(paths.get('output'), 'figures')})
paths.update({'tables': Path.joinpath(paths.get('output'), 'tables')})

# Warnings management
warnings.filterwarnings(action='ignore', category=RuntimeWarning)
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)


# %%
# **************************************************
# *** Branch: DATA MANAGEMENT                    ***
# **************************************************


def preprocessing_1(df_data):
    df_out = df_data
    df_out['YEAR'] = df_out['DATE'].dt.year.astype(float)
    df_out['QTR'] = df_out['DATE'].dt.quarter.astype(float)
    df_out['MTH'] = df_out['DATE'].dt.month.astype(float)
    df_out['KEYQ'] = df_out['PERMNO'].astype(str) + '_' + df_out['YEAR'].astype(str) + '_' + df_out['QTR'].astype(str)
    df_out['KEYM'] = df_out['PERMNO'].astype(str) + '_' + df_out['YEAR'].astype(str) + '_' + df_out['MTH'].astype(str)
    return df_out


def preprocessing_2(df_data):
    df_out = df_data
    idx_tmp = df_out.index
    ls_pos = []
    for i in tqdm(range(len(idx_tmp) - 1), desc='Preprocessing (2)'):
        if df_out.loc[idx_tmp[i], 'KEYQ'] == df_out.loc[idx_tmp[i + 1], 'KEYQ']:
            ls_pos += [i]

    ls_drops = []
    for j in ls_pos:
        ls_drops += [idx_tmp[j]]
        k = 1
        while (j - k >= 0) and (df_out.loc[idx_tmp[j - k], 'PERMNO'] == df_out.loc[idx_tmp[j], 'PERMNO']) and (df_out.loc[idx_tmp[j - k], 'FQTR'] != 4):
            ls_drops += [idx_tmp[j - k]]
            k += 1
        k = 1
        while (j + k <= len(idx_tmp) - 1) and (df_out.loc[idx_tmp[j + k], 'PERMNO'] == df_out.loc[idx_tmp[j], 'PERMNO']) and (df_out.loc[idx_tmp[j + k], 'FQTR'] != 1):
            ls_drops += [idx_tmp[j + k]]
            k += 1

    ls_drops = sorted(list(set(ls_drops)))  # Unique elements to be dropped
    df_out = df_out.drop(ls_drops)
    s_tmp = df_out['KEYQ'].value_counts()
    print('Original dataset size: {}'.format(len(df_data)))
    print('Rows deleted: {}'.format(len(ls_drops)))
    print('Preprocessed dataset size: {}'.format(len(df_out)))
    print('Unique keys (KEYQ): {}'.format(len(s_tmp[s_tmp == 1])))
    return df_out


def preprocessing_3(df_data):
    df_out = df_data
    idx_tmp = df_out.index
    ls_drops = []
    for i in tqdm(range(len(idx_tmp) - 1), desc='Preprocessing (3)'):
        if df_out.loc[idx_tmp[i], 'KEYM'] == df_out.loc[idx_tmp[i + 1], 'KEYM']:
            ls_drops += [idx_tmp[i]]  # Drop duplicate before ==> keep last

    df_out = df_out.drop(ls_drops)
    s_tmp = df_out['KEYM'].value_counts()
    print('Original dataset size: {}'.format(len(df_data)))
    print('Rows deleted: {}'.format(len(ls_drops)))
    print('Preprocessed dataset size: {}'.format(len(df_out)))
    print('Unique keys (KEYM): {}'.format(len(s_tmp[s_tmp == 1])))
    return df_out


def preprocessing_4(df_data):
    df_out = df_data
    df_out['FILLED'] = False  # Indicate if row has been filled
    ls_permnos = df_out['PERMNO'].unique().tolist()

    df_dates = pd.DataFrame({'DATE': pd.Series(df_out['DATE'].unique().tolist())})  # Assumption: df_data['DATE'] contains all monthly dates
    df_dates['YEAR'] = df_dates['DATE'].dt.year.astype(float)
    df_dates['MTH'] = df_dates['DATE'].dt.month.astype(float)
    df_dates = df_dates.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

    ls_dfs = []
    for permno in tqdm(ls_permnos, desc='Preprocessing (4)'):
        s_tmp = df_out[df_out['PERMNO'] == permno]['DATE']
        dt_start, dt_end = s_tmp.min(), s_tmp.max()
        pos_start = df_dates.index[(df_dates['YEAR'] == dt_start.year) & (df_dates['MTH'] == dt_start.month)].tolist()[0]
        pos_end = df_dates.index[(df_dates['YEAR'] == dt_end.year) & (df_dates['MTH'] == dt_end.month)].tolist()[0]

        df_tmp = df_dates.loc[pos_start:pos_end, ['DATE']]
        df_tmp['PERMNO'] = permno
        df_tmp['FILLED'] = True
        df_tmp = preprocessing_1(df_tmp)
        df_tmp = df_tmp[['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED']]
        df_tmp = df_tmp[~df_tmp['KEYM'].isin(df_out[df_out['PERMNO'] == permno]['KEYM'])]  # Exclude obs present in dataset
        ls_dfs += [df_tmp]

    ls_dfs = [df_out] + ls_dfs
    df_out = pd.concat(ls_dfs, axis=0, ignore_index=True)
    df_out['FILLED'] = df_out['FILLED'].astype(bool)
    return df_out


def preprocessing_5(df_data):
    df_out = df_data
    df_out['CAPXQ'] = df_out['CAPXY']
    df_out['WCAPCHQ'] = df_out['WCAPQ']
    df_out['PRCCQ'] = df_out['PRCCM']

    j = 0
    idx_tmp = df_out.index
    for i in tqdm(idx_tmp, desc='Preprocessing (5)'):
        # CAPXQ
        if j < (3 * 1):
            if df_out.loc[i, 'FQTR'] != 1:
                df_out.loc[i, 'CAPXQ'] = None

        if j >= 3:
            if df_out.loc[i, 'FQTR'] != 1:
                if df_out.loc[i, 'PERMNO'] == df_out.loc[idx_tmp[j - 3], 'PERMNO']:
                    df_out.loc[i, 'CAPXQ'] = df_out.loc[i, 'CAPXY'] - df_out.loc[idx_tmp[j - 3], 'CAPXY']
                else:
                    df_out.loc[i, 'CAPXQ'] = None

        # WCAPCHQ
        if j < 3:
            df_out.loc[i, 'WCAPCHQ'] = None

        if j >= 3:
            if df_out.loc[i, 'PERMNO'] == df_out.loc[idx_tmp[j - 3], 'PERMNO']:
                df_out.loc[i, 'WCAPCHQ'] = df_out.loc[i, 'WCAPQ'] - df_out.loc[idx_tmp[j - 3], 'WCAPQ']
            else:
                df_out.loc[i, 'WCAPCHQ'] = None

        # PRCCQ
        len_tpm = len(df_out) - 1
        if j != 0:
            if df_out.loc[idx_tmp[len_tpm - j], 'PERMNO'] == df_out.loc[idx_tmp[len_tpm - j + 1], 'PERMNO']:
                if df_out.loc[idx_tmp[len_tpm - j], 'FQTR'] == df_out.loc[idx_tmp[len_tpm - j + 1], 'FQTR']:
                    df_out.loc[idx_tmp[len_tpm - j], 'PRCCQ'] = df_out.loc[idx_tmp[len_tpm - j + 1], 'PRCCQ']

        j += 1

    df_out['XINTQ'] = df_out['XINTQ'].fillna(0)  # Assumption: fill missing values with 0 (interest expense)
    df_out.loc[df_out['FILLED'], 'XINTQ'] = np.nan  # Put nan if row has been filled
    df_out['TRT1M'] = df_out['TRT1M'] / 100  # Total return expressed as float (before: percentage points)
    df_out['VOL'] = df_out['VOL'] * 100  # Volume expressed in units (before: hundreds shares, monthly data)
    df_out['DVOL'] = (df_out['PRCCM'] * df_out['VOL']) / (10 ** 6)  # Dollar volume expressed in mil.
    df_out['SPRDPCT'] = (df_out['ASK'] - df_out['BID']) / df_out['ASK']  # Bid-Ask spread expressed as float
    return df_out


def preprocessing_6(df_data):
    df_out = df_data
    df_out = df_out.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=3)
    ls_vars = ['ATQ', 'COGSQ', 'CSHOQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ',
               'REVTQ', 'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ', 'PRCCQ']

    for var in tqdm(ls_vars, desc='Preprocessing (6)'):
        df_out[var] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[var].shift(periods=3), np.nan)
        df_out.loc[df_out['FILLED'], var] = np.nan

    df_out = df_out.drop(columns=['PERMNO_t'])
    return df_out


def get_LTM(df_data, ls_vars):
    df_out = df_data
    for var in tqdm(ls_vars, desc='LTM'):
        df_out[var + '_t_3'] = df_out[var].shift(periods=3 * 3)
        df_out[var + '_t_2'] = df_out[var].shift(periods=2 * 3)
        df_out[var + '_t_1'] = df_out[var].shift(periods=1 * 3)
        df_out['PERMNO_t_3'] = df_out['PERMNO'].shift(periods=3 * 3)

        ls_cols = [var + '_t_3', var + '_t_2', var + '_t_1', var]
        df_out['LTM_' + var] = np.where(df_out['PERMNO'] == df_out['PERMNO_t_3'], df_out[ls_cols].sum(axis=1, skipna=False), np.nan)
        df_out = df_out.drop(columns=[var + '_t_3', var + '_t_2', var + '_t_1', 'PERMNO_t_3'])
    return df_out


def get_diff(df_data, ls_vars, n):
    df_out = df_data
    for var in ls_vars:
        df_out[var + '_t'] = (-1) * df_out[var].shift(periods=(n * 4 * 3))
        df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n * 4 * 3))
        ls_cols = [var + '_t', var]
        df_out['D_' + var] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].sum(axis=1, skipna=False), np.nan)
        df_out = df_out.drop(columns=[var + '_t', 'PERMNO_t'])
    return df_out


def preprocessing_7(df_data):
    # Create variables LTM (Last Twelve Months)
    df_out = df_data
    df_out = get_LTM(df_out, ls_vars=['COGSQ', 'DPQ', 'NIQ', 'PIQ', 'REQ', 'REVTQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ'])
    print('Preprocessing (7):')

    # New variables
    df_out['LTM_CF'] = df_out['LTM_NIQ'] + df_out['LTM_DPQ'] - df_out['LTM_WCAPCHQ'] - df_out['LTM_CAPXQ']  # CF = NI + D&A - dWC - CAPX
    df_out['ME'] = df_out['PRCCQ'] * df_out['CSHOQ']
    df_out['BE'] = df_out['ATQ'] - df_out['LTQ']  # Book value of Equity = Total Assets - Total Liabilities
    print('- New variables: DONE')

    # Value
    df_out['BE/ME'] = df_out['BE'] / df_out['ME']  # Book-to-Market Equity
    df_out['E/P'] = (df_out['LTM_NIQ'] / df_out['CSHOQ']) / df_out['PRCCM']  # Earning-to-Price
    df_out['CF/P'] = (df_out['LTM_CF'] / df_out['CSHOQ']) / df_out['PRCCM']  # Cash Flow-to-Price
    print('- Value: DONE')

    # Profitability
    df_out['GPOA'] = (df_out['LTM_REVTQ'] - df_out['LTM_COGSQ']) / df_out['ATQ']
    df_out['ROE'] = df_out['LTM_NIQ'] / df_out['BE']
    df_out['ROA'] = df_out['LTM_NIQ'] / df_out['ATQ']
    df_out['CFOA'] = df_out['LTM_CF'] / df_out['ATQ']
    df_out['GMAR'] = (df_out['LTM_REVTQ'] - df_out['LTM_COGSQ']) / df_out['LTM_REVTQ']
    df_out['ACC'] = - (df_out['LTM_WCAPCHQ'] - df_out['LTM_DPQ']) / df_out['ATQ']
    print('- Profitability: DONE')

    # Growth
    df_out.replace([np.inf, -np.inf], np.nan, inplace=True)  # Avoid to have runtime error (sum inf number)
    df_out = get_diff(df_out, ls_vars=['GPOA', 'ROE', 'ROA', 'CFOA', 'GMAR'], n=5)  # Create diff. variables (n years interval)
    print('- Growth: DONE')

    # Safety
    df_out['LEV'] = (-1) * (df_out['DLTTQ'] + df_out['DLCQ']) / df_out['ATQ']  # Take the negative (zscore)
    df_out['AZSCORE'] = ((1.2 * df_out['WCAPQ']) + (1.4 * df_out['LTM_REQ']) + (3.3 * (df_out['LTM_PIQ'] + df_out['LTM_XINTQ'])) + (0.6 * df_out['ME']) + df_out['LTM_REVTQ']) / df_out['ATQ']
    df_out.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace inf with nan
    print('- Safety: DONE')

    # Beta and Volatility (benchmark: S&P 500 Composite Index)
    n = 5
    for i in range(0, n * 12):
        df_out['TRT1M' + 't_' + str(i)] = df_out['TRT1M'].shift(periods=i)
    for i in range(0, n * 12):
        df_out['SPRTRN' + 't_' + str(i)] = df_out['SPRTRN'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=n * 4 * 3 - 1)  # Take n*12 months taking the current months (first date: n*12 - 1)
    ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(0, n * 12)]
    ls_cols_SPRTRN = ['SPRTRN' + 't_' + str(i) for i in range(0, n * 12)]

    # Compute (-1)* mean return over the last n*12 months
    df_out['M_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], -df_out[ls_cols_TRT1M].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO
    df_out['M_SPRTRN'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], -df_out[ls_cols_SPRTRN].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO

    # Compute return + (-1)* mean return
    for i in range(0, n * 12):
        df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)
    for i in range(0, n * 12):
        df_out['SPRTRN' + 't_' + str(i)] = df_out[['SPRTRN' + 't_' + str(i), 'M_SPRTRN']].sum(axis=1, skipna=False)

    # Compute product of (TRT1M - mean TRT1M) * (SPRTRN - mean SPRTRN)
    for i in range(0, n * 12):
        df_out['PROD_TRT1M_SPRTRN' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'SPRTRN' + 't_' + str(i)]].product(axis=1, skipna=False)

    # Compute Cov(TRT1M, SPRTRN) over the last n*12 months
    ls_cols_COV_TRT1M_SPRTRN = ['PROD_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0, n * 12)]
    df_out['COV_TRT1M_SPRTRN'] = df_out[ls_cols_COV_TRT1M_SPRTRN].sum(axis=1, skipna=False) / (len(range(0, n * 12)) - 1)  # Unbiased estimator

    # Compute Vol over the last n*12 months (Vol(return - mean return) = Vol(return))
    df_out['VOL_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols_TRT1M].std(axis=1, skipna=False, ddof=1), np.nan)
    df_out['VOL_SPRTRN'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols_SPRTRN].std(axis=1, skipna=False, ddof=1), np.nan)
    df_out['VAR_SPRTRN'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols_SPRTRN].var(axis=1, skipna=False, ddof=1), np.nan)

    # Compute Beta over the last n*12 months
    df_out['BETA'] = df_out['COV_TRT1M_SPRTRN'] / df_out['VAR_SPRTRN']
    df_out['NBETA'] = (-1) * df_out['BETA']  # Take the negative (zscore)

    df_out = df_out.drop(columns=['TRT1M' + 't_' + str(i) for i in range(0, n * 12)])
    df_out = df_out.drop(columns=['SPRTRN' + 't_' + str(i) for i in range(0, n * 12)])
    df_out = df_out.drop(columns=['PROD_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0, n * 12)])
    df_out = df_out.drop(columns=['M_TRT1M', 'M_SPRTRN', 'COV_TRT1M_SPRTRN', 'VAR_SPRTRN', 'PERMNO_t'])
    print('- Beta and Volatility: DONE')

    # Previous monthly returns (n-years period)
    for i in range(n * 12 - 1, -1, -1):
        df_out['TRT1M' + 't_' + str(i)] = df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=n * 4 * 3 - 1)  # Take n*12 months taking the current months (first date: n*12 - 1)
    ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n * 12 - 1, -1, -1)]

    # Compute (-1)* mean return over the last n*12 months
    df_out['M_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols_TRT1M].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO

    # Compute return + (-1)* mean return
    for i in range(n * 12 - 1, -1, -1):
        df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

    df_out['M_TRT1M'] = -df_out['M_TRT1M']

    for i in range(n * 12 - 1, -1, -1):
        df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

    ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n * 12 - 1, -1, -1)]
    df_out['LS_PTRT1M'] = df_out[ls_cols_TRT1M].values.tolist()
    df_out.loc[df_out['FILLED'], 'LS_PTRT1M'] = np.nan

    df_out = df_out.drop(columns=['TRT1M' + 't_' + str(i) for i in range(n * 12 - 1, -1, -1)])
    df_out = df_out.drop(columns=['M_TRT1M', 'PERMNO_t'])
    print('- Previous monthly returns: DONE')

    # Momentum
    n_lags_1 = 0  # Short-term
    n_lags_2 = 12  # Long-term
    for i in range(n_lags_1, n_lags_2):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_2 - 1))
    ls_cols = ['TRT1M_t' + str(i) for i in range(n_lags_1, n_lags_2)]
    df_out['CTRT1M_1'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(n_lags_1, n_lags_2)])
    df_out = df_out.drop(columns=['PERMNO_t'])

    n_lags_1 = 1  # Short-term
    n_lags_2 = 12  # Long-term
    for i in range(n_lags_1, n_lags_2):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_2 - 1))
    ls_cols = ['TRT1M_t' + str(i) for i in range(n_lags_1, n_lags_2)]
    df_out['CTRT1M_2'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(n_lags_1, n_lags_2)])
    df_out = df_out.drop(columns=['PERMNO_t'])
    print('- Momentum: DONE')

    # Reverse momentum
    n_lags_1 = 0  # Short-term
    n_lags_2 = 1  # Long-term
    for i in range(n_lags_1, n_lags_2):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_2 - 1))
    ls_cols = ['TRT1M_t' + str(i) for i in range(n_lags_1, n_lags_2)]
    df_out['NCTRT1M'] = (-1) * np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)  # Take the negative (zscore)

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(n_lags_1, n_lags_2)])
    df_out = df_out.drop(columns=['PERMNO_t'])
    print('- Reverse momentum: DONE')

    # Next monthly returns (1-year period)
    for i in range(1, 12 + 1):
        df_out['TRT1M_t' + str(i)] = df_out['TRT1M'].shift(periods=(-i))

    ls_cols = ['TRT1M_t' + str(i) for i in range(1, 12 + 1)]

    for i in range(1, 12 + 1):
        df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-i))
        df_out['TRT1M_t' + str(i)] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out['TRT1M_t' + str(i)], np.nan)

    for i in range(1, 12 + 1):
        df_out['TRT1M_t' + str(i)] = df_out['TRT1M_t' + str(i)].fillna(0)

    df_out['LS_NTRT1M'] = df_out[ls_cols].values.tolist()
    df_out.loc[df_out['FILLED'], 'LS_NTRT1M'] = np.nan

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(1, 12 + 1)])
    df_out = df_out.drop(columns=['PERMNO_t'])
    print('- Next monthly returns: DONE')
    return df_out


def get_ZS(df_data):
    df_out = df_data
    ls_vars = ['BE/ME', 'E/P', 'CF/P',
               'GPOA', 'ROE', 'ROA', 'CFOA', 'GMAR', 'ACC',
               'D_GPOA', 'D_ROE', 'D_ROA', 'D_CFOA', 'D_GMAR',
               'LEV', 'AZSCORE', 'NBETA',
               'CTRT1M_2', 'NCTRT1M']

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
    ls_cols = [('ZS_' + var) for var in ['CTRT1M_2']]
    df_out['ZS_MOM'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Reverse momentum
    ls_cols = [('ZS_' + var) for var in ['NCTRT1M']]
    df_out['ZS_RMOM'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Adjusted momentum
    ls_cols = [('ZS_' + var) for var in ['MOM', 'RMOM']]
    df_out['ZS_AMOM'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value and Quality
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT']]
    df_out['ZS_VAL_QLT'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value, Quality and Momentum
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'MOM']]
    df_out['ZS_VAL_QLT_MOM'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value, Quality and Adjusted momentum
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'AMOM']]
    df_out['ZS_VAL_QLT_AMOM'] = df_out[ls_cols].mean(axis=1, skipna=False)
    return df_out


# %%
# **************************************************
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************

# COPY HERE
class Portfolio:
    def __init__(self, dic_data, sig_long, n_asts_long, w_meth_long, pct_long,
                 sig_short, n_asts_short, w_meth_short, pct_short,
                 ind_const, reb_freq, min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=0):
        self.dic_data = dic_data
        self.sig_long = sig_long
        self.n_asts_long = n_asts_long
        self.w_meth_long = w_meth_long
        self.pct_long = pct_long
        self.sig_short = sig_short
        self.n_asts_short = n_asts_short
        self.w_meth_short = w_meth_short
        self.pct_short = pct_short
        self.ind_const = ind_const
        self.reb_freq = reb_freq
        self.min_short_me = min_short_me
        self.max_short_cl = max_short_cl
        self.tc_bps = tc_bps
        self.spr_bps = spr_bps
        self.dic_asts_data = dic_data['dic_asts_data']
        self.ls_dates = list(self.dic_asts_data.keys())
        self.df_facs_data = dic_data['df_facs_data']
        self.dic_sigs = {'ZS_VAL': 'VAL', 'ZS_QLT': 'QLT', 'ZS_MOM': 'MOM', 'ZS_RMOM': 'RMOM', 'ZS_AMOM': 'AMOM',
                         'ZS_VAL_QLT': 'VQ', 'ZS_VAL_QLT_MOM': 'VQM', 'ZS_VAL_QLT_AMOM': 'VQAM'}
        self.dic_GICS = {bytes('10', 'utf-8'): 'Energy', bytes('15', 'utf-8'): 'Materials', bytes('20', 'utf-8'): 'Industrials',
                         bytes('25', 'utf-8'): 'Consumer Discretionary', bytes('30', 'utf-8'): 'Consumer Stables', bytes('35', 'utf-8'): 'Health Care',
                         bytes('40', 'utf-8'): 'Financials', bytes('45', 'utf-8'): 'Information Technology', bytes('50', 'utf-8'): 'Communication Services',
                         bytes('55', 'utf-8'): 'Utilities', bytes('60', 'utf-8'): 'Real Estate'}
        self.port_name = '_'.join([self.dic_sigs[sig_long], str(n_asts_long), w_meth_long, str(pct_long),
                                   self.dic_sigs[sig_short], str(n_asts_short), w_meth_short, str(pct_short), ind_const, reb_freq])

    def get_df_sec_avg_counts(self):
        ls_dfs = []
        for i in range(len(self.ls_dates)):
            s_tmp_1 = pd.Series([np.nan for i in range(len(list(self.dic_GICS.keys())))], index=sorted(list(self.dic_GICS.keys())))
            s_tmp_2 = self.dic_asts_data[self.ls_dates[i]]['GSECTOR'].value_counts().rename(None)
            for sec in s_tmp_2.index.tolist():
                s_tmp_1[sec] = s_tmp_2[sec]
                s_tmp_1 = s_tmp_1.rename(self.ls_dates[i])
            ls_dfs += [pd.DataFrame(s_tmp_1).transpose()]

        df_sec_counts = pd.concat(ls_dfs, axis=0).fillna(0)
        df_sec_counts = df_sec_counts.reset_index(drop=False, names=['DATE'])
        df_sec_counts['YEAR'] = df_sec_counts['DATE'].dt.year.astype(float)
        df_sec_avg_counts = df_sec_counts.groupby('YEAR')[list(self.dic_GICS.keys())].mean()
        df_sec_avg_counts = df_sec_avg_counts.rename(columns=self.dic_GICS)
        return df_sec_avg_counts

    def get_ls_asts(self, df_data, leg):
        # Min market cap to avoid short small caps
        # Max cumulative loss to avoid short if already big loss
        ls_asts = []
        n_asts = 0
        ls_secs = df_data['GSECTOR'].unique().tolist()
        df_tmp = pd.DataFrame()

        if leg == 'L':
            n_asts = self.n_asts_long
            df_tmp = df_data[['PERMNO', 'GSECTOR', 'ME', 'CTRT1M_1', self.sig_long]]
        elif leg == 'S':
            n_asts = self.n_asts_short
            df_tmp = df_data[['PERMNO', 'GSECTOR', 'ME', 'CTRT1M_1', self.sig_short]]

        if self.ind_const == 'I':
            dic_asts = {}
            for sec in ls_secs:
                df_tmp_sec = df_tmp[df_tmp['GSECTOR'] == sec]
                if leg == 'L':
                    df_tmp_sec = df_tmp_sec.sort_values(by=[self.sig_long], ascending=False)
                    dic_asts[sec] = df_tmp_sec['PERMNO'].tolist()
                elif leg == 'S':
                    df_tmp_sec = df_tmp_sec.sort_values(by=[self.sig_short], ascending=True)
                    df_tmp_sec = df_tmp_sec[(df_tmp_sec['ME'] >= self.min_short_me) & (df_tmp_sec['CTRT1M_1'] >= -self.max_short_cl)]
                    dic_asts[sec] = df_tmp_sec['PERMNO'].tolist()
                if len(dic_asts[sec]) < np.ceil((max(self.n_asts_long, self.n_asts_short) * 2) / len(ls_secs)):  # Remove too small sectors
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

        elif self.ind_const == 'NI':
            if leg == 'L':
                ls_asts = df_tmp.loc[df_tmp[self.sig_long].nlargest(n_asts).index, 'PERMNO'].tolist()
            elif leg == 'S':
                df_tmp = df_tmp[(df_tmp['ME'] >= self.min_short_me) & (df_tmp['CTRT1M_1'] >= -self.max_short_cl)]
                ls_asts = df_tmp.loc[df_tmp[self.sig_short].nsmallest(n_asts).index, 'PERMNO'].tolist()

        ls_asts = sorted(ls_asts)  # Sort PERMNO
        return ls_asts

    def get_s_port_w(self, df_data, leg, w_meth):
        s_port_w = pd.Series(dtype='float64')
        ls_asts = self.get_ls_asts(df_data, leg)
        n_asts = len(ls_asts)
        opt_prob = False

        # Optimization constraints
        def cons1(w):
            return np.sum(w) - 1

        # Optimization settings
        x0 = np.ones(n_asts) / n_asts
        bnds = [(0.005, 1) for i in range(n_asts)]  # Long-only, min 0.5% per asset
        cons = {'type': 'eq', 'fun': cons1}
        res = OptimizeResult()

        # Equal weighting
        if w_meth == 'EW':
            s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')

        # Value weighting
        elif w_meth == 'VW':
            s_me = df_data.loc[df_data['PERMNO'].isin(ls_asts), 'ME'].rename(None)
            s_port_w = pd.Series((s_me / s_me.sum()).values, index=ls_asts, dtype='float64')

        # Minimum variance
        elif w_meth == 'MV':
            # Initialization
            opt_prob = True
            df_rtns = pd.DataFrame(df_data.loc[df_data['PERMNO'].isin(ls_asts), 'LS_PTRT1M'].tolist()).T  # Previous returns
            df_rtns.columns = ls_asts
            df_covmat = df_rtns.cov()
            a_covmat = np.array(df_covmat * 12)  # Annualized from monthly data

            # Useful functions
            def get_port_var(w):
                return w.T @ a_covmat @ w

            # Optimization
            res = minimize(fun=get_port_var, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-6, options={'maxiter': 500})

        # Market neutral (zero beta)
        elif w_meth == 'MN':
            # Initialization
            opt_prob = True
            s_betas = df_data.loc[df_data['PERMNO'].isin(ls_asts), 'BETA'].rename(None)
            a_betas = np.array(s_betas)

            # Useful functions
            def get_port_beta(w):
                return w.T @ a_betas

            def obj_fun(w):
                diff = (get_port_beta(w) - 1) ** 2
                return diff  # Minimize to have Beta_P = 1 (Beta_L - Beta_S = 1 - 1 = 0)

            # Optimization
            res = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-6, options={'maxiter': 500})

        # Risk parity (equally-weighted risk contributions)
        elif w_meth == 'RP':
            # Initialization
            opt_prob = True
            df_rtns = pd.DataFrame(df_data.loc[df_data['PERMNO'].isin(ls_asts), 'LS_PTRT1M'].tolist()).T  # Previous returns
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

            # Optimization
            res = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-6, options={'maxiter': 500})

        # Return output
        if opt_prob:
            if not res.success:
                s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')  # Assumption: if optimization fails (at this date), use equal weighting
            else:
                s_port_w = pd.Series(res.x, index=ls_asts, dtype='float64')
        return s_port_w

    def tab_port_perf(self):
        # Useful functions
        def get_turnover(df_port_perf, pos_tmp, leg):
            dic_tmp = df_port_perf.loc[(pos_tmp - 1), (leg + '_WT')]
            s_w_t_1 = pd.Series(list(dic_tmp.values()), index=list(dic_tmp.keys()), dtype='float64').rename(None)

            dic_tmp = df_port_perf.loc[pos_tmp, (leg + '_ASTS_RTNS')]
            s_r_t = pd.Series(list(dic_tmp.values()), index=list(dic_tmp.keys()), dtype='float64').rename(None)
            s_w_t_1_a = s_w_t_1 * ((1 + s_r_t) / (1 + df_port_perf.loc[pos_tmp, (leg + '_RTNS')]))

            dic_tmp = df_port_perf.loc[pos_tmp, (leg + '_WT')]
            s_w_t = pd.Series(list(dic_tmp.values()), index=list(dic_tmp.keys()), dtype='float64').rename(None)

            dic = {0: s_w_t_1_a, 1: s_w_t}
            df = pd.DataFrame.from_dict(dic, orient='index').fillna(0).sort_index(axis=1)
            return (df.iloc[1] - df.iloc[0]).abs().sum()

        # Initialization
        dic_cols = {'DATE': 'datetime64[ns]', 'PORT_C': 'float64', 'PORT_L': 'float64',
                    'PORT_S': 'float64', 'PORT_NAV': 'float64', 'PORT_LEV': 'float64', 'PORT_RTNS': 'float64',
                    'L_RTNS': 'float64', 'L_POS': 'object', 'L_WT': 'object', 'L_TO': 'float64', 'L_TC': 'float64', 'L_ASTS_RTNS': 'object',
                    'S_RTNS': 'float64', 'S_POS': 'object', 'S_WT': 'object', 'S_TO': 'float64', 'S_TC': 'float64', 'S_ASTS_RTNS': 'object'}
        df_port_perf = pd.DataFrame(columns=list(dic_cols.keys())).astype(dtype=dic_cols)
        ls_dates = list(self.dic_asts_data.keys())
        df_long_asts_rtns = pd.DataFrame()
        ls_long_asts = []
        df_short_asts_rtns = pd.DataFrame()
        ls_short_asts = []

        # Number of (EOM) dates in rebalancing period
        n_dates = 0
        if self.reb_freq == 'M':
            n_dates = 1
        elif self.reb_freq == 'Q':
            n_dates = 3
        elif self.reb_freq == 'S':
            n_dates = 6
        elif self.reb_freq == 'Y':
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
        df_port_perf.loc[0, ['PORT_L', 'PORT_S']] = 0
        df_port_perf.loc[0, ['PORT_C', 'PORT_NAV']] = 100  # Initial equity (normalized)
        df_port_perf.loc[0, 'PORT_C'] -= (self.pct_long / 100) * df_port_perf.loc[0, 'PORT_NAV']
        df_port_perf.loc[0, 'PORT_L'] += (self.pct_long / 100) * df_port_perf.loc[0, 'PORT_NAV']  # Open long
        df_port_perf.loc[0, 'PORT_C'] += (self.pct_short / 100) * df_port_perf.loc[0, 'PORT_NAV']
        df_port_perf.loc[0, 'PORT_S'] += (self.pct_short / 100) * df_port_perf.loc[0, 'PORT_NAV']  # Open short
        df_port_perf.loc[0, 'PORT_LEV'] = df_port_perf.loc[0, 'PORT_S'] / df_port_perf.loc[0, 'PORT_NAV']  # Leverage (D/E)
        df_port_perf.loc[0, 'NET_EXP_PCT'] = (df_port_perf.loc[0, 'PORT_L'] - df_port_perf.loc[0, 'PORT_S']) / df_port_perf.loc[0, 'PORT_NAV']
        df_port_perf.loc[0, 'S_BC'] = 0

        # Iteration over rebalancing dates
        for i in tqdm(range(len(ls_reb_dates)), desc=self.port_name, disable=False):
            df_tmp = self.dic_asts_data[ls_reb_dates[i]]
            pos_tmp = (n_dates * i)

            if self.spr_bps != 0:
                df_tmp_2 = self.df_facs_data.set_index('DATE').loc[ls_reb_dates[i], 'RF']
                df_port_perf.loc[pos_tmp, 'RF'] = df_tmp_2

            if ls_reb_dates[i] == ls_dates[0]:
                # Long leg
                s_long_w = self.get_s_port_w(df_tmp, leg='L', w_meth=self.w_meth_long)
                ls_long_asts = s_long_w.index.tolist()
                df_long_asts_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_long_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
                df_long_asts_rtns.columns = ls_long_asts
                df_port_perf.at[pos_tmp, 'L_POS'] = dict(zip(ls_long_asts, (s_long_w * df_port_perf.loc[pos_tmp, 'PORT_L']).tolist()))
                df_port_perf.at[pos_tmp, 'L_WT'] = dict(zip(ls_long_asts, s_long_w.tolist()))

                # Short leg
                s_short_w = self.get_s_port_w(df_tmp, leg='S', w_meth=self.w_meth_short)
                ls_short_asts = s_short_w.index.tolist()
                df_short_asts_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_short_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
                df_short_asts_rtns.columns = ls_short_asts
                df_port_perf.at[pos_tmp, 'S_POS'] = dict(zip(ls_short_asts, (s_short_w * df_port_perf.loc[pos_tmp, 'PORT_S']).tolist()))
                df_port_perf.at[pos_tmp, 'S_WT'] = dict(zip(ls_short_asts, s_short_w.tolist()))

            # Long/Short rebalancing
            if ls_reb_dates[i] != ls_dates[0]:  # Initial allocation already done
                # Long leg
                s_long_w = self.get_s_port_w(df_tmp, leg='L', w_meth=self.w_meth_long)
                ls_long_asts = s_long_w.index.tolist()
                df_port_perf.at[pos_tmp, 'L_WT'] = dict(zip(ls_long_asts, s_long_w.tolist()))

                # Short leg
                s_short_w = self.get_s_port_w(df_tmp, leg='S', w_meth=self.w_meth_short)
                ls_short_asts = s_short_w.index.tolist()
                df_port_perf.at[pos_tmp, 'S_WT'] = dict(zip(ls_short_asts, s_short_w.tolist()))

                # Turnover (after rebalancing)
                df_port_perf.loc[pos_tmp, 'L_TO'] = get_turnover(df_port_perf, pos_tmp, leg='L')
                df_port_perf.loc[pos_tmp, 'S_TO'] = get_turnover(df_port_perf, pos_tmp, leg='S')

                # Transaction costs
                df_port_perf.loc[pos_tmp, 'L_TC'] = ((self.tc_bps / 10000) * df_port_perf.loc[pos_tmp, 'L_TO']) * df_port_perf.loc[pos_tmp, 'PORT_L']
                df_port_perf.loc[pos_tmp, 'S_TC'] = ((self.tc_bps / 10000) * df_port_perf.loc[pos_tmp, 'S_TO']) * df_port_perf.loc[pos_tmp, 'PORT_S']

                # Returns on legs after transactions costs
                df_port_perf.loc[pos_tmp, 'L_RTNS'] = (df_port_perf.loc[pos_tmp, 'PORT_L'] - df_port_perf.loc[pos_tmp, 'L_TC']) / df_port_perf.loc[pos_tmp - 1, 'PORT_L'] - 1
                df_port_perf.loc[pos_tmp, 'S_RTNS'] = (df_port_perf.loc[pos_tmp, 'PORT_S'] - df_port_perf.loc[pos_tmp, 'S_TC']) / df_port_perf.loc[pos_tmp - 1, 'PORT_S'] - 1

                # Liquidate positions
                df_port_perf.loc[pos_tmp, 'PORT_C'] += (df_port_perf.loc[pos_tmp, 'PORT_L'] - df_port_perf.loc[pos_tmp, 'L_TC'])
                df_port_perf.loc[pos_tmp, 'PORT_L'] = 0
                df_port_perf.loc[pos_tmp, 'PORT_C'] -= (df_port_perf.loc[pos_tmp, 'PORT_S'] + df_port_perf.loc[pos_tmp, 'S_TC'] + df_port_perf.loc[pos_tmp, 'S_BC'])
                df_port_perf.loc[pos_tmp, 'PORT_S'] = 0
                df_port_perf.loc[pos_tmp, 'PORT_NAV'] = df_port_perf.loc[pos_tmp, 'PORT_C']
                df_port_perf.loc[pos_tmp, 'S_BC'] = 0

                # Return on portfolio (L/S)
                df_port_perf.loc[pos_tmp, 'PORT_RTNS'] = (df_port_perf.loc[pos_tmp, 'PORT_NAV'] / df_port_perf.loc[(pos_tmp - 1), 'PORT_NAV']) - 1

                # Open new positions
                df_port_perf.loc[pos_tmp, 'PORT_C'] -= (self.pct_long / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_L'] += (self.pct_long / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_C'] += (self.pct_short / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_S'] += (self.pct_short / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_LEV'] = df_port_perf.loc[pos_tmp, 'PORT_S'] / df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'NET_EXP_PCT'] = (df_port_perf.loc[pos_tmp, 'PORT_L'] - df_port_perf.loc[pos_tmp, 'PORT_S']) / df_port_perf.loc[pos_tmp, 'PORT_NAV']

                # Legs after rebalancing
                df_port_perf.at[pos_tmp, 'L_POS'] = dict(zip(ls_long_asts, (s_long_w * df_port_perf.loc[pos_tmp, 'PORT_L']).tolist()))
                df_port_perf.at[pos_tmp, 'S_POS'] = dict(zip(ls_short_asts, (s_short_w * df_port_perf.loc[pos_tmp, 'PORT_S']).tolist()))

                # Legs next returns (needed for carry forward)
                df_long_asts_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_long_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
                df_long_asts_rtns.columns = ls_long_asts
                df_short_asts_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_short_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
                df_short_asts_rtns.columns = ls_short_asts

            # Carry forward position in rebalancing period
            for j in range(1, (n_dates + 1)):
                pos_tmp = (n_dates * i) + j
                df_port_perf.loc[pos_tmp, 'DATE'] = ls_dates[pos_tmp]

                # Short Borrowing cost
                if self.spr_bps != 0:
                    df_tmp_2 = self.df_facs_data.set_index('DATE').loc[ls_dates[pos_tmp], 'RF']
                    df_port_perf.loc[pos_tmp, 'RF'] = df_tmp_2
                    df_port_perf.loc[pos_tmp, 'S_BC'] = df_port_perf.loc[pos_tmp - 1, 'S_BC'] + df_port_perf.loc[(pos_tmp - 1), 'PORT_S'] * (df_port_perf.loc[(pos_tmp - 1), 'RF'] + (self.spr_bps / 12 / 10000))
                if self.spr_bps == 0:
                    df_port_perf.loc[pos_tmp, 'S_BC'] = 0

                # Long leg
                a_long_asts_rtns = np.array(df_long_asts_rtns.loc[j - 1])
                df_port_perf.at[pos_tmp, 'L_ASTS_RTNS'] = dict(zip(ls_long_asts, a_long_asts_rtns.tolist()))
                df_port_perf.loc[pos_tmp, 'L_RTNS'] = (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'L_WT'].values())) * a_long_asts_rtns).sum()
                df_port_perf.at[pos_tmp, 'L_POS'] = dict(zip(ls_long_asts, (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'L_POS'].values())) * (1 + a_long_asts_rtns)).tolist()))
                df_port_perf.loc[pos_tmp, 'PORT_L'] = np.array(list(df_port_perf.loc[pos_tmp, 'L_POS'].values())).sum()
                df_port_perf.at[pos_tmp, 'L_WT'] = dict(zip(ls_long_asts, (np.array(list(df_port_perf.at[pos_tmp, 'L_POS'].values())) / df_port_perf.loc[pos_tmp, 'PORT_L']).tolist()))

                # Short leg
                a_short_asts_rtns = np.array(df_short_asts_rtns.loc[j - 1])
                df_port_perf.at[pos_tmp, 'S_ASTS_RTNS'] = dict(zip(ls_short_asts, a_short_asts_rtns.tolist()))
                df_port_perf.loc[pos_tmp, 'S_RTNS'] = (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'S_WT'].values())) * a_short_asts_rtns).sum()
                df_port_perf.at[pos_tmp, 'S_POS'] = dict(zip(ls_short_asts, (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'S_POS'].values())) * (1 + a_short_asts_rtns)).tolist()))
                df_port_perf.loc[pos_tmp, 'PORT_S'] = np.array(list(df_port_perf.loc[pos_tmp, 'S_POS'].values())).sum()
                df_port_perf.at[pos_tmp, 'S_WT'] = dict(zip(ls_short_asts, (np.array(list(df_port_perf.at[pos_tmp, 'S_POS'].values())) / df_port_perf.loc[pos_tmp, 'PORT_S']).tolist()))

                # Portfolio (L/S)
                df_port_perf.loc[pos_tmp, 'PORT_C'] = df_port_perf.loc[(pos_tmp - 1), 'PORT_C']  # Assumption: no interest on cash (possible to use risk-free rate)
                df_port_perf.loc[pos_tmp, 'PORT_NAV'] = df_port_perf.loc[pos_tmp, 'PORT_C'] + df_port_perf.loc[pos_tmp, 'PORT_L'] - df_port_perf.loc[pos_tmp, 'PORT_S']
                df_port_perf.loc[pos_tmp, 'PORT_LEV'] = df_port_perf.loc[pos_tmp, 'PORT_S'] / df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_RTNS'] = (df_port_perf.loc[pos_tmp, 'PORT_NAV'] / df_port_perf.loc[(pos_tmp - 1), 'PORT_NAV']) - 1
                df_port_perf.loc[pos_tmp, 'NET_EXP_PCT'] = (df_port_perf.loc[pos_tmp, 'PORT_L'] - df_port_perf.loc[pos_tmp, 'PORT_S']) / df_port_perf.loc[pos_tmp, 'PORT_NAV']

        # Turnover zero on intermediary dates
        df_port_perf[['L_TO', 'L_TC', 'S_TO', 'S_TC']] = df_port_perf[['L_TO', 'L_TC', 'S_TO', 'S_TC']].fillna(0)

        # Merge risk-free rate data
        if self.spr_bps == 0:
            df_port_perf = pd.merge(df_port_perf, self.df_facs_data.drop(columns=['MKTRF', 'SMB', 'HML', 'UMD']), on='DATE', how='inner')
            df_port_perf = df_port_perf.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

        # Long leg adjusted for net exposure
        df_port_perf['LA_RTNS'] = (df_port_perf['NET_EXP_PCT'] * df_port_perf['L_RTNS']) + ((1 - df_port_perf['NET_EXP_PCT']) * df_port_perf['RF'])
        return df_port_perf

    def tab_port_chars(self, output_perf=False):
        # Useful functions
        def get_drawdown(s_port_rtns):
            max = 0
            dt_max = s_port_rtns.index[0]
            old_max = 0
            dt_old_max = s_port_rtns.index[0]
            df_drawdown = pd.DataFrame()
            s_min = pd.Series(dtype='float64')
            s_port_cum_rtns = pd.Series(np.cumprod(1 + np.array(s_port_rtns)), index=s_port_rtns.index)

            for i in s_port_cum_rtns.index:
                if s_port_cum_rtns[i] > max:
                    old_max = max
                    dt_old_max = dt_max
                    max = s_port_cum_rtns[i]
                    dt_max = i
                if max == s_port_cum_rtns[i]:
                    if not s_min.empty:
                        drawdown = s_min.min() / old_max - 1
                        df_drawdown_tmp = pd.DataFrame({'DD': [drawdown], 'START': [dt_old_max], 'END': [s_min.idxmin()]})
                        df_drawdown = pd.concat([df_drawdown, df_drawdown_tmp], ignore_index=True)
                        s_min = pd.Series(dtype='float64')
                if s_port_cum_rtns[i] < max:
                    s_min[i] = s_port_cum_rtns[i]
            return df_drawdown

        def get_norm_herfindahl_idx(a_port_w):
            n_asts = len(a_port_w)
            H = (a_port_w ** 2).sum()
            norm_H = (H - (1 / n_asts)) / (1 - (1 / n_asts))
            return norm_H

        # Portfolio performance
        df_port_perf = self.tab_port_perf()
        if output_perf:
            df_port_perf.to_pickle(Path.joinpath(paths.get('output'), 'ports', (self.port_name + '.pkl')))

        # Merge factors data
        df_port_perf = pd.merge(df_port_perf, self.df_facs_data.drop(columns=['RF']), on='DATE', how='inner')
        df_port_perf = df_port_perf.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

        # Initialization
        df_port_chars = pd.DataFrame()
        s_port_rtns = pd.Series(df_port_perf.loc[1:, 'PORT_RTNS'].tolist(), index=df_port_perf.loc[1:, 'DATE'].tolist(), dtype='float64').rename(None)
        s_port_losses = (-1) * s_port_rtns
        df_drawdown = get_drawdown(s_port_rtns)
        s_max_drawdown = df_drawdown.iloc[df_drawdown['DD'].idxmin()]
        X = sm.add_constant(df_port_perf.loc[1:, ['MKTRF', 'SMB', 'HML', 'UMD']])
        model = sm.OLS((df_port_perf.loc[1:, 'PORT_RTNS'] - df_port_perf.loc[1:, 'RF']), X).fit(cov_type='HC3')  # Heteroskedasticity-consistent estimator
        s_long_rtns = pd.Series(df_port_perf.loc[1:, 'L_RTNS'].tolist(), index=df_port_perf.loc[1:, 'DATE'].tolist(), dtype='float64').rename(None)
        s_short_rtns = pd.Series(df_port_perf.loc[1:, 'S_RTNS'].tolist(), index=df_port_perf.loc[1:, 'DATE'].tolist(), dtype='float64').rename(None)
        s_long_a_rtns = pd.Series(df_port_perf.loc[1:, 'LA_RTNS'].tolist(), index=df_port_perf.loc[1:, 'DATE'].tolist(), dtype='float64').rename(None)

        # Parameters combo
        df_port_chars.loc[0, 'NAME'] = self.port_name
        df_port_chars.loc[0, 'L_SIG'] = self.dic_sigs[self.sig_long]
        df_port_chars.loc[0, 'L_N_ASTS'] = self.n_asts_long
        df_port_chars.loc[0, 'L_W_METH'] = self.w_meth_long
        df_port_chars.loc[0, 'L_PCT'] = self.pct_long
        df_port_chars.loc[0, 'S_SIG'] = self.dic_sigs[self.sig_short]
        df_port_chars.loc[0, 'S_N_ASTS'] = self.n_asts_short
        df_port_chars.loc[0, 'S_W_METH'] = self.w_meth_short
        df_port_chars.loc[0, 'S_PCT'] = self.pct_short
        df_port_chars.loc[0, 'IND_CONST'] = self.ind_const
        df_port_chars.loc[0, 'REB_FREQ'] = self.reb_freq

        # Portfolio (L/S)
        df_port_chars.loc[0, 'PORT_NAV_T'] = df_port_perf.iloc[-1]['PORT_NAV']
        df_port_chars.loc[0, 'ANN_MEAN'] = s_port_rtns.mean() * 12
        df_port_chars.loc[0, 'ANN_VOL'] = np.sqrt(s_port_rtns.var() * 12)
        df_port_chars.loc[0, 'SHARPE'] = (df_port_chars.loc[0, 'ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'ANN_VOL']
        df_port_chars.loc[0, 'MIN_RTN'] = s_port_rtns.min()
        df_port_chars.loc[0, 'MIN_DATE'] = (s_port_rtns.idxmin()).strftime('%Y-%m')
        df_port_chars.loc[0, 'MAX_RTN'] = s_port_rtns.max()
        df_port_chars.loc[0, 'MAX_DATE'] = (s_port_rtns.idxmax()).strftime('%Y-%m')
        df_port_chars.loc[0, 'MAX_DD'] = (-1) * s_max_drawdown['DD']  # Expressed in terms of loss (negative return)
        df_port_chars.loc[0, 'MAX_DD_PRD'] = s_max_drawdown['START'].strftime('%Y-%m') + '_' + s_max_drawdown['END'].strftime('%Y-%m')
        df_port_chars.loc[0, 'CALMAR'] = (df_port_chars.loc[0, 'ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'MAX_DD']
        df_port_chars.loc[0, 'ANN_ALPHA'] = model.params.iloc[0] * 12
        df_port_chars.loc[0, 't_ALPHA'] = model.tvalues.iloc[0]
        df_port_chars.loc[0, 'B_MKTRF'] = model.params.iloc[1]
        df_port_chars.loc[0, 't_MKTRF'] = model.tvalues.iloc[1]
        df_port_chars.loc[0, 'B_SMB'] = model.params.iloc[2]
        df_port_chars.loc[0, 't_SMB'] = model.tvalues.iloc[2]
        df_port_chars.loc[0, 'B_HML'] = model.params.iloc[3]
        df_port_chars.loc[0, 't_HML'] = model.tvalues.iloc[3]
        df_port_chars.loc[0, 'B_UMD'] = model.params.iloc[4]
        df_port_chars.loc[0, 't_UMD'] = model.tvalues.iloc[4]
        df_port_chars.loc[0, 'R_SQUARED'] = model.rsquared
        df_port_chars.loc[0, 'AVG_LEV'] = df_port_perf.loc[1:, 'PORT_LEV'].mean()
        df_port_chars.loc[0, 'AVG_TO'] = df_port_perf.loc[1:, 'L_TO'].mean() * self.pct_long / 100 + df_port_perf.loc[1:, 'S_TO'].mean() * self.pct_short / 100

        # Long leg
        df_drawdown = get_drawdown(s_long_rtns)
        s_max_drawdown = df_drawdown.iloc[df_drawdown['DD'].idxmin()]
        df_port_chars.loc[0, 'PORT_L_T'] = df_port_perf.iloc[-1]['PORT_L']
        df_port_chars.loc[0, 'L_ANN_MEAN'] = s_long_rtns.mean() * 12
        df_port_chars.loc[0, 'L_ANN_VOL'] = np.sqrt(s_long_rtns.var() * 12)
        df_port_chars.loc[0, 'L_SHARPE'] = (df_port_chars.loc[0, 'L_ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'L_ANN_VOL']
        df_port_chars.loc[0, 'L_MAX_DD'] = (-1) * s_max_drawdown['DD']
        df_port_chars.loc[0, 'L_CALMAR'] = (df_port_chars.loc[0, 'L_ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'L_MAX_DD']
        df_port_chars.loc[0, 'L_AVG_TO'] = df_port_perf.loc[1:, 'L_TO'].mean()
        df_port_chars.loc[0, 'L_NORM_HI'] = get_norm_herfindahl_idx(np.array(list(df_port_perf.iloc[-1]['L_WT'].values())))

        # Short leg
        df_drawdown = get_drawdown(s_short_rtns)
        s_max_drawdown = df_drawdown.iloc[df_drawdown['DD'].idxmin()]
        df_port_chars.loc[0, 'PORT_S_T'] = df_port_perf.iloc[-1]['PORT_S']
        df_port_chars.loc[0, 'S_ANN_MEAN'] = s_short_rtns.mean() * 12
        df_port_chars.loc[0, 'S_ANN_VOL'] = np.sqrt(s_short_rtns.var() * 12)
        df_port_chars.loc[0, 'S_SHARPE'] = (df_port_chars.loc[0, 'S_ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'S_ANN_VOL']
        df_port_chars.loc[0, 'S_MAX_DD'] = (-1) * s_max_drawdown['DD']
        df_port_chars.loc[0, 'S_CALMAR'] = (df_port_chars.loc[0, 'S_ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'S_MAX_DD']
        df_port_chars.loc[0, 'S_AVG_TO'] = df_port_perf.loc[1:, 'S_TO'].mean()
        df_port_chars.loc[0, 'S_NORM_HI'] = get_norm_herfindahl_idx(np.array(list(df_port_perf.iloc[-1]['S_WT'].values())))

        # Long Adjusted
        df_drawdown = get_drawdown(s_long_a_rtns)
        s_max_drawdown = df_drawdown.iloc[df_drawdown['DD'].idxmin()]
        df_port_chars.loc[0, 'LA_ANN_MEAN'] = s_long_a_rtns.mean() * 12
        df_port_chars.loc[0, 'LA_ANN_VOL'] = np.sqrt(s_long_a_rtns.var() * 12)
        df_port_chars.loc[0, 'LA_SHARPE'] = (df_port_chars.loc[0, 'LA_ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'LA_ANN_VOL']
        df_port_chars.loc[0, 'LA_MAX_DD'] = (-1) * s_max_drawdown['DD']
        df_port_chars.loc[0, 'LA_CALMAR'] = (df_port_chars.loc[0, 'LA_ANN_MEAN'] - (df_port_perf.iloc[-1]['RF'] * 12)) / df_port_chars.loc[0, 'LA_MAX_DD']
        df_port_chars.loc[0, 'LA_AVG_TO'] = df_port_perf.loc[1:, 'L_TO'].mean() * (self.pct_long - self.pct_short)
        df_port_chars.loc[0, 'LA_NORM_HI'] = get_norm_herfindahl_idx(np.array(list(df_port_perf.iloc[-1]['L_WT'].values())))

        return df_port_chars


def get_df_port_chars(combo):
    with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'rb') as file:
        dic_data = pickle.load(file)
    port = Portfolio(dic_data, sig_long=combo[0], n_asts_long=combo[1], w_meth_long=combo[4], pct_long=combo[5][0],
                     sig_short=combo[2], n_asts_short=combo[3], w_meth_short=combo[4], pct_short=combo[5][1],
                     ind_const=combo[6], reb_freq=combo[7])
    df_port_chars = port.tab_port_chars(output_perf=False)
    return df_port_chars


# %%
# **************************************************
# *** Branch: PORTFOLIO ANALYSIS                 ***
# **************************************************


def plot_zscores(date, ls_zscores, leg):
    with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'rb') as file:
        dic_data = pickle.load(file)
    dic_asts_data = dic_data['dic_asts_data']
    df_zscores = dic_asts_data[date]
    df_zscores = df_zscores[['PERMNO', 'CONM', 'TIC'] + ls_zscores]
    ls_permnos = df_zscores['PERMNO'].unique().tolist()
    df_zscores['ZS_INT'] = df_zscores[ls_zscores].mean(axis=1, skipna=False)

    n_asts = 50
    dic_s_zscores = {}
    if leg == 'L':
        for i in range(len(ls_zscores)):
            dic_s_zscores[i] = pd.Series(list(df_zscores[ls_zscores[i]]), index=ls_permnos, dtype='float64').nlargest(n_asts).sort_values(ascending=False)
        dic_s_zscores[len(ls_zscores)] = pd.Series(list(df_zscores['ZS_INT']), index=ls_permnos, dtype='float64').nlargest(n_asts).sort_values(ascending=False)
    elif leg == 'S':
        for i in range(len(ls_zscores)):
            dic_s_zscores[i] = pd.Series(list(df_zscores[ls_zscores[i]]), index=ls_permnos, dtype='float64').nsmallest(n_asts).sort_values(ascending=True)
        dic_s_zscores[len(ls_zscores)] = pd.Series(list(df_zscores['ZS_INT']), index=ls_permnos, dtype='float64').nsmallest(n_asts).sort_values(ascending=True)

    if len(ls_zscores) == 2:
        ls_asts_0 = sorted(dic_s_zscores[0].index.tolist())  # ZS_0
        ls_asts_1 = sorted(dic_s_zscores[1].index.tolist())  # ZS_1
        ls_asts_2 = sorted(dic_s_zscores[2].index.tolist())  # ZS_INT

        ls_asts_3 = [ast for ast in ls_asts_0 if (ast not in ls_asts_2)]  # Only ZS_0
        ls_asts_4 = [ast for ast in ls_asts_1 if (ast not in ls_asts_2)]  # Only ZS_1
        ls_asts_5 = [ast for ast in ls_permnos if (ast not in ls_asts_0) and (ast not in ls_asts_1) and (ast not in ls_asts_2)]  # All other

        trace_0 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_2), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_2), ls_zscores[1]],
                             mode='markers', marker=dict(size=10, color='rgba(50,161,109,1.0)'),
                             name='Stocks in Integrated', hoverinfo='text',
                             hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_2), 'CONM'].tolist()])
        trace_1 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[1]],
                             mode='markers', marker=dict(size=10, color='rgba(52,147,250,1.0)'),
                             name='Stocks Only in {}'.format(ls_zscores[0][3:]), hoverinfo='text',
                             hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), 'CONM'].tolist()])
        trace_2 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[1]],
                             mode='markers', marker=dict(size=10, color='rgba(247,189,53,1.0)'),
                             name='Stocks Only in {}'.format(ls_zscores[1][3:]), hoverinfo='text',
                             hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), 'CONM'].tolist()])
        trace_3 = go.Scatter(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[0]],
                             y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[1]],
                             mode='markers', marker=dict(size=10, color='rgba(220,220,220,0.8)'),
                             name='All Other Stocks', hoverinfo='text',
                             hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), 'CONM'].tolist()])

        layout = go.Layout(
            title=dict(text='Stock Picking ({})'.format(date.strftime('%Y-%m-%d')), font=dict(size=28), x=0.5, y=0.95),
            xaxis=dict(
                title='ZScore {}'.format(ls_zscores[0][3:]),
                titlefont=dict(size=24),
                showline=False,
                linecolor='black',
                linewidth=2,
                zeroline=True,
                zerolinecolor='rgba(0,0,0,0.6)',
                zerolinewidth=2,
                gridcolor='rgba(183,203,254,0.3)',
                range=[-2.5, 2.5]
            ),
            yaxis=dict(
                title='ZScore {}'.format(ls_zscores[1][3:]),
                titlefont=dict(size=24),
                showline=False,
                linecolor='black',
                linewidth=2,
                zeroline=True,
                zerolinecolor='rgba(0,0,0,0.6)',
                zerolinewidth=2,
                gridcolor='rgba(183,203,254,0.3)',
                range=[-2.5, 2.5]
            ),
            legend=dict(font=dict(size=18)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(173,216,230,0.1)'
        )

        fig = go.Figure(data=[trace_0, trace_1, trace_2, trace_3], layout=layout)
        pyo.plot(fig, filename='output/figures/plot_zscores_2D.html')

    elif len(ls_zscores) == 3:
        ls_asts_0 = sorted(dic_s_zscores[0].index.tolist())  # ZS_0
        ls_asts_1 = sorted(dic_s_zscores[1].index.tolist())  # ZS_1
        ls_asts_2 = sorted(dic_s_zscores[2].index.tolist())  # ZS_2
        ls_asts_3 = sorted(dic_s_zscores[3].index.tolist())  # ZS_INT

        ls_asts_4 = [ast for ast in ls_asts_0 if (ast not in ls_asts_3)]  # Only ZS_0
        ls_asts_5 = [ast for ast in ls_asts_1 if (ast not in ls_asts_3)]  # Only ZS_1
        ls_asts_6 = [ast for ast in ls_asts_2 if (ast not in ls_asts_3)]  # Only ZS_2
        ls_asts_7 = [ast for ast in ls_permnos if (ast not in ls_asts_0) and (ast not in ls_asts_1) and (ast not in ls_asts_2) and (ast not in ls_asts_3)]  # All other

        trace_0 = go.Scatter3d(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[0]],
                               y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[1]],
                               z=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), ls_zscores[2]],
                               mode='markers', marker=dict(size=10, color='rgba(50,161,109,1.0)'),
                               name='Stocks in Integrated', hoverinfo='text',
                               hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_3), 'CONM'].tolist()])
        trace_1 = go.Scatter3d(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[0]],
                               y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[1]],
                               z=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), ls_zscores[2]],
                               mode='markers', marker=dict(size=10, color='rgba(52,147,250,1.0)'),
                               name='Stocks Only in {}'.format(ls_zscores[0][3:]), hoverinfo='text',
                               hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_4), 'CONM'].tolist()])
        trace_2 = go.Scatter3d(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[0]],
                               y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[1]],
                               z=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), ls_zscores[2]],
                               mode='markers', marker=dict(size=10, color='rgba(247,189,53,1.0)'),
                               name='Stocks Only in {}'.format(ls_zscores[1][3:]), hoverinfo='text',
                               hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_5), 'CONM'].tolist()])
        trace_3 = go.Scatter3d(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_6), ls_zscores[0]],
                               y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_6), ls_zscores[1]],
                               z=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_6), ls_zscores[2]],
                               mode='markers', marker=dict(size=10, color='rgba(155,32,176,1.0)'),
                               name='Stocks Only in {}'.format(ls_zscores[2][3:]), hoverinfo='text',
                               hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_6), 'CONM'].tolist()])
        trace_4 = go.Scatter3d(x=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_7), ls_zscores[0]],
                               y=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_7), ls_zscores[1]],
                               z=df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_7), ls_zscores[2]],
                               mode='markers', marker=dict(size=10, color='rgba(220,220,220,0.8)'),
                               name='All Other Stocks', hoverinfo='text',
                               hovertext=[b.decode('utf-8') for b in df_zscores.loc[df_zscores['PERMNO'].isin(ls_asts_7), 'CONM'].tolist()])

        layout = go.Layout(
            title=dict(text='Stock Picking ({})'.format(date.strftime('%Y-%m-%d')), font=dict(size=28), x=0.5, y=0.95),
            scene=dict(
                xaxis=dict(
                    title='ZScore {}'.format(ls_zscores[0][3:]),
                    titlefont=dict(size=24),
                    showline=False,
                    linecolor='black',
                    linewidth=2,
                    zeroline=True,
                    zerolinecolor='rgba(0,0,0,0.6)',
                    zerolinewidth=2,
                    gridcolor='rgba(183,203,254,0.3)',
                    range=[-2.5, 2.5]
                ),
                yaxis=dict(
                    title='ZScore {}'.format(ls_zscores[1][3:]),
                    titlefont=dict(size=24),
                    showline=False,
                    linecolor='black',
                    linewidth=2,
                    zeroline=True,
                    zerolinecolor='rgba(0,0,0,0.6)',
                    zerolinewidth=2,
                    gridcolor='rgba(183,203,254,0.3)',
                    range=[-2.5, 2.5]
                ),
                zaxis=dict(
                    title='ZScore {}'.format(ls_zscores[2][3:]),
                    titlefont=dict(size=24),
                    showline=False,
                    linecolor='black',
                    linewidth=2,
                    zeroline=True,
                    zerolinecolor='rgba(0,0,0,0.6)',
                    zerolinewidth=2,
                    gridcolor='rgba(183,203,254,0.3)',
                    range=[-2.5, 2.5]
                )
            ),
            legend=dict(font=dict(size=18)),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(173,216,230,0.1)'
        )

        fig = go.Figure(data=[trace_0, trace_1, trace_2, trace_3, trace_4], layout=layout)
        pyo.plot(fig, filename='output/figures/plot_zscores_3D.html')


def plot_line_chart(df, title='', xlabel='', ylabel='', figsize=(16, 9), legend_title='', file_path=''):
    # Initiate figure
    sns.set(context='paper', style='ticks', font_scale=1.0)
    fig, ax = plt.subplots(figsize=figsize, dpi=600)
    ax.set_title(title, fontsize=28)

    # Define the color palette
    palette = sns.color_palette('colorblind', n_colors=len(df.columns))

    # Compute the maximum value of each column and sort the values in descending order
    legend_order = df.max().sort_values(ascending=False).index.tolist()

    # Plot the line chart
    ax.axhline(y=1, color='black', ls='--', lw=1)
    sns.lineplot(data=df, ax=ax, linewidth=2, hue_order=legend_order, dashes=False, linestyle='solid', palette=palette)

    # X-axis settings
    ax.tick_params(axis='x', labelsize=18)
    ax.set_xlim()
    date_locator = mdates.YearLocator(2)
    date_formatter = mdates.DateFormatter('%Y')
    ax.xaxis.set_major_locator(date_locator)
    ax.xaxis.set_major_formatter(date_formatter)
    ax.set_xlabel(xlabel, fontsize=20)

    # Y-axis settings
    ax.tick_params(axis='y', labelsize=18)
    ax.set_ylim(0, ax.get_ylim()[1])
    ax.set_yticks(np.concatenate((np.delete(ax.get_yticks(), 0), [1])))
    ax.set_ylabel(ylabel, fontsize=20)

    # Customize the legend
    ax.legend(title=legend_title, fontsize=14, title_fontsize=16)

    # Remove the top and right spines
    sns.despine(top=True, right=True)

    # Show the plot
    fig.tight_layout()
    plt.show()
    fig.savefig(file_path)
    plt.close()