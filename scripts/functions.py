# Import packages
from pathlib import Path
from scipy.optimize import minimize, OptimizeResult
from tqdm import tqdm
import numpy as np
import pandas as pd

# Project directories paths (README: modify if necessary!)
paths = {'main': Path.cwd()}
paths.update({'data': Path.joinpath(paths.get('main'), 'data')})
paths.update({'output': Path.joinpath(paths.get('main'), 'output')})
paths.update({'scripts': Path.joinpath(paths.get('main'), 'scripts')})


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
    n_lags_1 = 12  # Long-term (n_lags months)
    for i in range(0, n_lags_1):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_1 - 1))
    ls_cols = ['TRT1M_t' + str(i) for i in range(0, n_lags_1)]
    df_out['CTRT1M_1'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)  # Cumulative total returns

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(0, n_lags_1)])
    df_out = df_out.drop(columns=['PERMNO_t'])

    n_lags_2 = 3  # Short-term
    for i in range(0, n_lags_2):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_2 - 1))
    ls_cols = ['TRT1M_t' + str(i) for i in range(0, n_lags_2)]
    df_out['CTRT1M_2'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(0, n_lags_2)])
    df_out = df_out.drop(columns=['PERMNO_t'])
    print('- Momentum: DONE')

    # Reverse momentum
    df_out['NCTRT1M_1'] = (-1) * df_out['CTRT1M_1']  # Take the negative (zscore)

    n_lags_3 = 3  # Short-term
    n_lags_4 = 12  # Long-term
    for i in range(n_lags_3, n_lags_4):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_4 - 1))
    ls_cols = ['TRT1M_t' + str(i) for i in range(n_lags_3, n_lags_4)]
    df_out['NCTRT1M_2'] = (-1) * np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)  # Take the negative (zscore)

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(n_lags_3, n_lags_4)])
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
               'CTRT1M_1', 'CTRT1M_2', 'NCTRT1M_1', 'NCTRT1M_2']

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
    ls_cols = [('ZS_' + var) for var in ['CTRT1M_1']]
    df_out['ZS_MOM_1'] = df_out[ls_cols].mean(axis=1, skipna=False)
    ls_cols = [('ZS_' + var) for var in ['CTRT1M_2']]
    df_out['ZS_MOM_2'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Reverse momentum
    ls_cols = [('ZS_' + var) for var in ['NCTRT1M_1']]
    df_out['ZS_RMOM_1'] = df_out[ls_cols].mean(axis=1, skipna=False)
    ls_cols = [('ZS_' + var) for var in ['NCTRT1M_2']]
    df_out['ZS_RMOM_2'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Adjusted reverse momentum
    ls_cols = [('ZS_' + var) for var in ['MOM_2', 'RMOM_2']]
    df_out['ZS_ARMOM'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value and Quality
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT']]
    df_out['ZS_VAL_QLT'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value, Quality and Momentum (long-term)
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'MOM_1']]
    df_out['ZS_VAL_QLT_MOM_1'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value, Quality and Momentum (short-term)
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'MOM_2']]
    df_out['ZS_VAL_QLT_MOM_2'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value, Quality and Reverse momentum (long-term)
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'RMOM_1']]
    df_out['ZS_VAL_QLT_RMOM'] = df_out[ls_cols].mean(axis=1, skipna=False)

    # Value, Quality and Adjusted reverse momentum
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'ARMOM']]
    df_out['ZS_VAL_QLT_ARMOM'] = df_out[ls_cols].mean(axis=1, skipna=False)
    return df_out


# %%
# **************************************************
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************


class Portfolio:
    def __init__(self, dic_data, sig_long, n_asts_long, w_meth_long, pct_long,
                 sig_short, n_asts_short, w_meth_short, pct_short,
                 ind_const, reb_freq, min_short_me, max_short_cl):
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
        self.dic_asts_data = dic_data['dic_asts_data']
        self.df_facs_data = dic_data['df_facs_data']
        self.dic_sigs = {'ZS_VAL': 'VAL', 'ZS_QLT': 'QLT', 'ZS_MOM_1': 'MOM1', 'ZS_MOM_2': 'MOM2', 'ZS_RMOM_1': 'RMOM',
                         'ZS_VAL_QLT': 'VQ', 'ZS_VAL_QLT_MOM_1': 'VQM1', 'ZS_VAL_QLT_MOM_2': 'VQM2', 'ZS_VAL_QLT_RMOM': 'VQRM', 'ZS_VAL_QLT_ARMOM': 'VQARM'}
        self.port_name = '_'.join([self.dic_sigs[sig_long], str(int(n_asts_long)), w_meth_long, str(int(pct_long)),
                                   self.dic_sigs[sig_short], str(int(n_asts_short)), w_meth_short, str(int(pct_short)),
                                   ind_const, str(int(min_short_me)), str(int(max_short_cl * 100)), reb_freq])

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
            res = minimize(fun=get_port_var, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

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
            res = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

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
            res = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

        # Return output
        if opt_prob:
            if not res.success:
                s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')  # Assumption: if optimization fails (at this date), use equal weighting
            else:
                s_port_w = pd.Series(res.x, index=ls_asts, dtype='float64')
        return s_port_w

    def tab_port_perf(self):
        dic_cols = {'DATE': 'datetime64[ns]', 'PORT_C': 'float64', 'PORT_L': 'float64', 'PORT_S': 'float64', 'PORT_NAV': 'float64', 'PORT_RTN': 'float64',
                    'L_RTN': 'float64', 'L_POS': 'object', 'L_WT': 'object', 'L_RTNS': 'object',
                    'S_RTN': 'float64', 'S_POS': 'object', 'S_WT': 'object', 'S_RTNS': 'object'}
        df_port_perf = pd.DataFrame(columns=list(dic_cols.keys())).astype(dtype=dic_cols)
        ls_dates = list(self.dic_asts_data.keys())

        # Number of (EOM) dates in rebalancing period
        n_dates = 0
        if self.reb_freq == 'M':
            n_dates = 1
        elif self.reb_freq == 'Q':
            n_dates = 3
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

        # Iteration over rebalancing dates
        for i in tqdm(range(len(ls_reb_dates)), desc=self.port_name):
            df_tmp = self.dic_asts_data[ls_reb_dates[i]]
            pos_tmp = (n_dates * i)

            # Long/Short rebalancing
            if ls_reb_dates[i] != ls_dates[0]:
                # Liquidate positions
                df_port_perf.loc[pos_tmp, 'PORT_C'] += df_port_perf.loc[pos_tmp, 'PORT_L']
                df_port_perf.loc[pos_tmp, 'PORT_L'] = 0
                df_port_perf.loc[pos_tmp, 'PORT_C'] -= df_port_perf.loc[pos_tmp, 'PORT_S']
                df_port_perf.loc[pos_tmp, 'PORT_S'] = 0
                # Open new positions
                df_port_perf.loc[pos_tmp, 'PORT_C'] -= (self.pct_long / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_L'] += (self.pct_long / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_C'] += (self.pct_short / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']
                df_port_perf.loc[pos_tmp, 'PORT_S'] += (self.pct_short / 100) * df_port_perf.loc[pos_tmp, 'PORT_NAV']

            # Long leg
            s_long_w = self.get_s_port_w(df_tmp, leg='L', w_meth=self.w_meth_long)
            ls_long_asts = s_long_w.index.tolist()
            df_long_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_long_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
            df_long_rtns.columns = ls_long_asts
            df_port_perf.at[pos_tmp, 'L_POS'] = dict(zip(ls_long_asts, (s_long_w * df_port_perf.loc[pos_tmp, 'PORT_L']).tolist()))
            df_port_perf.at[pos_tmp, 'L_WT'] = dict(zip(ls_long_asts, s_long_w.tolist()))

            # Short leg
            s_short_w = self.get_s_port_w(df_tmp, leg='S', w_meth=self.w_meth_short)
            ls_short_asts = s_short_w.index.tolist()
            df_short_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_short_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
            df_short_rtns.columns = ls_short_asts
            df_port_perf.at[pos_tmp, 'S_POS'] = dict(zip(ls_short_asts, (s_short_w * df_port_perf.loc[pos_tmp, 'PORT_S']).tolist()))
            df_port_perf.at[pos_tmp, 'S_WT'] = dict(zip(ls_short_asts, s_short_w.tolist()))

            # Carry forward position in rebalancing period
            for j in range(1, (n_dates + 1)):
                pos_tmp = (n_dates * i) + j
                df_port_perf.loc[pos_tmp, 'DATE'] = ls_dates[pos_tmp]

                # Long leg
                a_long_rtns = np.array(df_long_rtns.loc[j - 1])
                df_port_perf.at[pos_tmp, 'L_RTNS'] = dict(zip(ls_long_asts, a_long_rtns.tolist()))
                df_port_perf.loc[pos_tmp, 'L_RTN'] = (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'L_WT'].values())) * a_long_rtns).sum()
                df_port_perf.at[pos_tmp, 'L_POS'] = dict(zip(ls_long_asts, (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'L_POS'].values())) * (1 + a_long_rtns)).tolist()))
                df_port_perf.loc[pos_tmp, 'PORT_L'] = np.array(list(df_port_perf.loc[pos_tmp, 'L_POS'].values())).sum()
                df_port_perf.at[pos_tmp, 'L_WT'] = dict(zip(ls_long_asts, (np.array(list(df_port_perf.at[pos_tmp, 'L_POS'].values())) / df_port_perf.loc[pos_tmp, 'PORT_L']).tolist()))

                # Short leg
                a_short_rtns = np.array(df_short_rtns.loc[j - 1])
                df_port_perf.at[pos_tmp, 'S_RTNS'] = dict(zip(ls_short_asts, a_short_rtns.tolist()))
                df_port_perf.loc[pos_tmp, 'S_RTN'] = (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'S_WT'].values())) * a_short_rtns).sum()
                df_port_perf.at[pos_tmp, 'S_POS'] = dict(zip(ls_short_asts, (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'S_POS'].values())) * (1 + a_short_rtns)).tolist()))
                df_port_perf.loc[pos_tmp, 'PORT_S'] = np.array(list(df_port_perf.loc[pos_tmp, 'S_POS'].values())).sum()
                df_port_perf.at[pos_tmp, 'S_WT'] = dict(zip(ls_short_asts, (np.array(list(df_port_perf.at[pos_tmp, 'S_POS'].values())) / df_port_perf.loc[pos_tmp, 'PORT_S']).tolist()))

                # Portfolio (L/S)
                df_port_perf.loc[pos_tmp, 'PORT_C'] = df_port_perf.loc[(pos_tmp - 1), 'PORT_C']  # Assumption: no interest on cash (possible to use risk-free rate)
                df_port_perf.loc[pos_tmp, 'PORT_NAV'] = df_port_perf.loc[pos_tmp, 'PORT_C'] + df_port_perf.loc[pos_tmp, 'PORT_L'] - df_port_perf.loc[pos_tmp, 'PORT_S']
                df_port_perf.loc[pos_tmp, 'PORT_RTN'] = (df_port_perf.loc[pos_tmp, 'PORT_NAV'] / df_port_perf.loc[(pos_tmp - 1), 'PORT_NAV']) - 1
        return df_port_perf

    def get_s_port_chars(self, output_perf=False):

        print(output_perf)



'''
def tab_port_chars(name, s_port_rtns, interval, theta=0.99):
    s_port_losses = (-1) * s_port_rtns
    VaR_uncond = get_VaR_uncond(s_port_losses, theta)
    ES_uncond = get_ES_uncond(s_port_losses, theta)
    df_drawdown = get_drawdown(s_port_rtns)
    max_drawdown = df_drawdown.iloc[df_drawdown['drawdown'].idxmin()]
    max_drawdown_period = max_drawdown['start'].strftime('%Y-%m-%d') + ' - ' + max_drawdown['end'].strftime('%Y-%m-%d')

    df_port_chars = pd.DataFrame(index=[name])
    df_port_chars['Annualized average return'] = s_port_rtns.mean() * get_factor(interval)
    df_port_chars['Annualized volatility'] = np.sqrt(s_port_rtns.var() * get_factor(interval))
    df_port_chars['Minimum return'] = s_port_rtns.min()
    df_port_chars['Maximum return'] = s_port_rtns.max()
    df_port_chars['Max Drawdown'] = (-1) * max_drawdown['drawdown']  # Express in terms of loss (negative return)
    df_port_chars['Max Drawdown Period'] = max_drawdown_period
    df_port_chars['VaR @' + str(int(theta * 100)) + '%'] = VaR_uncond
    df_port_chars['ES @' + str(int(theta * 100)) + '%'] = ES_uncond

    return df_port_chars
'''




