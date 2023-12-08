# Import packages
from pathlib import Path
from tqdm import tqdm
import numpy as np
import pandas as pd
import warnings

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

        j += 1

    df_out['XINTQ'] = df_out['XINTQ'].fillna(0)  # Assumption: fill missing values with 0 (interest expense)
    df_out.loc[df_out['FILLED'], 'XINTQ'] = np.nan  # Put nan if row has been filled
    df_out['TRT1M'] = df_out['TRT1M'] / 100  # Total return expressed as float (before: percentage points)
    df_out['VOL'] = df_out['VOL'] * 100  # Volume expressed in units (before: hundreds shares, monthly data)
    df_out['SHROUT'] = df_out['SHROUT'] / 1000  # Shares outstanding expressed in mil.
    df_out['DVOL'] = (df_out['PRCCM'] * df_out['VOL']) / (10 ** 6)  # Dollar volume expressed in mil.
    df_out['SPRDPCT'] = (df_out['ASK'] - df_out['BID']) / df_out['ASK']  # Bid-Ask spread expressed as float
    return df_out


def preprocessing_6(df_data):
    df_out = df_data
    df_out = df_out.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=3)
    ls_vars = ['ATQ', 'COGSQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ', 'REVTQ',
               'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ']

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

    # New variables
    df_out['LTM_CF'] = df_out['LTM_NIQ'] + df_out['LTM_DPQ'] - df_out['LTM_WCAPCHQ'] - df_out['LTM_CAPXQ']  # CF = NI + D&A - dWC - CAPX
    df_out['ME'] = df_out['PRCCM'] * df_out['SHROUT']
    df_out['BE'] = df_out['ATQ'] - df_out['LTQ']  # Book value of Equity = Total Assets - Total Liabilities

    # Value
    df_out['BE/ME'] = df_out['BE'] / df_out['ME']  # Book-to-Market Equity
    df_out['E/P'] = (df_out['LTM_NIQ'] / df_out['SHROUT']) / df_out['PRCCM']  # Earning-to-Price
    df_out['CF/P'] = (df_out['LTM_CF'] / df_out['SHROUT']) / df_out['PRCCM']  # Cash Flow-to-Price

    # Quality: Profitability
    df_out['GPOA'] = (df_out['LTM_REVTQ'] - df_out['LTM_COGSQ']) / df_out['ATQ']
    df_out['ROE'] = df_out['LTM_NIQ'] / df_out['BE']
    df_out['ROA'] = df_out['LTM_NIQ'] / df_out['ATQ']
    df_out['CFOA'] = df_out['LTM_CF'] / df_out['ATQ']
    df_out['GMAR'] = (df_out['LTM_REVTQ'] - df_out['LTM_COGSQ']) / df_out['LTM_REVTQ']
    df_out['ACC'] = - (df_out['LTM_WCAPCHQ'] - df_out['LTM_DPQ']) / df_out['ATQ']

    # Quality: Growth
    df_out.replace([np.inf, -np.inf], np.nan, inplace=True)  # Avoid to have runtime error (sum inf number)
    df_out = get_diff(df_out, ls_vars=['GPOA', 'ROE', 'ROA', 'CFOA', 'GMAR'], n=5)  # Create diff. variables (n years interval)

    # Quality: Safety
    df_out['LEV'] = (-1) * (df_out['DLTTQ'] + df_out['DLCQ']) / df_out['ATQ']  # Take the negative (zscore computation)
    df_out['AZSCORE'] = ((1.2 * df_out['WCAPQ']) + (1.4 * df_out['LTM_REQ']) + (3.3 * (df_out['LTM_PIQ'] + df_out['LTM_XINTQ'])) + (0.6 * df_out['ME']) + df_out['LTM_REVTQ']) / df_out['ATQ']
    df_out.replace([np.inf, -np.inf], np.nan, inplace=True)  # Replace inf with nan

    # Beta and Volatility (benchmark: S&P 500 Composite Index)
    with warnings.catch_warnings():
        warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

        n = 5
        for i in range(0, n * 12):
            df_out['TRT1M' + 't_' + str(i)] = df_out['TRT1M'].shift(periods=i)
        for i in range(0, n * 12):
            df_out['SPRTRN' + 't_' + str(i)] = df_out['SPRTRN'].shift(periods=i)

        df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=n * 4 * 3 - 1)  # Take n*12 months taking the current months: first date n*12 - 1
        ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(0, n * 12)]
        ls_cols_SPRTRN = ['SPRTRN' + 't_' + str(i) for i in range(0, n * 12)]

        # Compute (-1)* mean return over the last n*12 months
        df_out['M_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], -df_out[ls_cols_TRT1M].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO
        df_out['M_SPRTRN'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], -df_out[ls_cols_SPRTRN].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO

        # Compute return + (-1) * mean return
        for i in range(0, n * 12):
            df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)
        for i in range(0, n * 12):
            df_out['SPRTRN' + 't_' + str(i)] = df_out[['SPRTRN' + 't_' + str(i), 'M_SPRTRN']].sum(axis=1, skipna=False)

        # Compute product of (TRT1M - mean TRT1M) * (SPRTRN - mean SPRTRN)
        for i in range(0, n * 12):
            df_out['PROD_TRT1M_SPRTRN' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'SPRTRN' + 't_' + str(i)]].product(axis=1, skipna=False)

        # Compute COV(TRT1M, SPRTRN) over the last n*12 months
        ls_cols_COV_TRT1M_SPRTRN = ['PROD_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0, n * 12)]
        df_out['COV_TRT1M_SPRTRN'] = df_out[ls_cols_COV_TRT1M_SPRTRN].sum(axis=1, skipna=False) / (len(range(0, n * 12)) - 1)

        # Compute Var over the last n*12 months (Var(return - mean return) = Var(return))
        df_out['VAR_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols_TRT1M].var(axis=1, skipna=False), np.nan)
        df_out['VAR_SPRTRN'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols_SPRTRN].var(axis=1, skipna=False), np.nan)

        # Compute BETA over the last n*12 months
        df_out['BETA'] = df_out['COV_TRT1M_SPRTRN'] / df_out['VAR_SPRTRN']
        df_out['NBETA'] = (-1) * df_out['BETA']  # Take the negative (zscore computation)

        df_out = df_out.drop(columns=['TRT1M' + 't_' + str(i) for i in range(0, n * 12)])
        df_out = df_out.drop(columns=['SPRTRN' + 't_' + str(i) for i in range(0, n * 12)])
        df_out = df_out.drop(columns=['PROD_TRT1M_SPRTRN' + 't_' + str(i) for i in range(0, n * 12)])
        df_out = df_out.drop(columns=['M_TRT1M', 'M_SPRTRN', 'COV_TRT1M_SPRTRN', 'PERMNO_t'])

        # Create variable with list of returns over the last n years

        for i in range(n * 12 - 1, -1, -1):
            df_out['TRT1M' + 't_' + str(i)] = df_out['TRT1M'].shift(periods=i)

        df_out['PERMNO_t'] = df_out['PERMNO'].shift(
            periods=n * 4 * 3 - 1)  # Take n*12 months taking the current months: first date n*12 - 1
        ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n * 12 - 1, -1, -1)]

        # Compute (-1)* mean return over the last n*12 months
        df_out['M_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols_TRT1M].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO

        # Compute return + (-1) * mean return
        for i in range(n * 12 - 1, -1, -1):
            df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

        df_out['M_TRT1M'] = -df_out['M_TRT1M']

        for i in range(n * 12 - 1, -1, -1):
            df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

        ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n * 12 - 1, -1, -1)]
        df_out['LS_TRT1M'] = df_out[ls_cols_TRT1M].values.tolist()

        df_out = df_out.drop(columns=['TRT1M' + 't_' + str(i) for i in range(n * 12 - 1, -1, -1)])
        df_out = df_out.drop(columns=['M_TRT1M', 'PERMNO_t'])


    # Next Month Returns
    df_out['NTRT1M'] = df_out['TRT1M'].shift(periods=(-1))
    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-1))
    df_out['NTRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out['NTRT1M'], np.nan)
    df_out['NTRT1M'] = df_out['NTRT1M'].fillna(0)
    df_out.loc[df_out['FILLED'], 'NTRT1M'] = np.nan

    # Next Quarter
    # Create the list next quarter
    for i in range(1, 4):
        df_out['TRT1M_t' + str(i)] = df_out['TRT1M'].shift(periods=(-i))

    ls_cols = ['TRT1M_t' + str(i) for i in range(1, 4)]

    for i in range(1, 4):
        df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-i))
        df_out['TRT1M_t' + str(i)] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out['TRT1M_t' + str(i)], np.nan)

    for i in range(1, 4):
        df_out['TRT1M_t' + str(i)] = df_out['TRT1M_t' + str(i)].fillna(0)


    df_out['LS_NTRT1Q'] = df_out[ls_cols].values.tolist()
    df_out.loc[df_out['FILLED'], 'LS_NTRT1Q'] = np.nan

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(1, 4)])
    df_out = df_out.drop(columns=['PERMNO_t'])


    # Create the variable next quarter cumulative return
    for i in range(1, 4):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=(-i))

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-3))
    ls_cols = ['TRT1M_t' + str(i) for i in range(1, 4)]


    df_out['NTRT1Q'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)
    df_out['NTRT1Q'] = df_out['NTRT1Q'].fillna(0)
    df_out.loc[df_out['FILLED'], 'NTRT1Q'] = np.nan

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(1, 4)])
    df_out = df_out.drop(columns=['PERMNO_t'])


    # Next Year
    # Create the list next year
    for i in range(1, 12+1):
        df_out['TRT1M_t' + str(i)] = df_out['TRT1M'].shift(periods=(-i))

    ls_cols = ['TRT1M_t' + str(i) for i in range(1, 12+1)]

    for i in range(1, 12+1):
        df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-i))
        df_out['TRT1M_t' + str(i)] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out['TRT1M_t' + str(i)], np.nan)

    for i in range(1, 12+1):
        df_out['TRT1M_t' + str(i)] = df_out['TRT1M_t' + str(i)].fillna(0)

    df_out['LS_NTRT1Y'] = df_out[ls_cols].values.tolist()
    df_out.loc[df_out['FILLED'], 'LS_NTRT1Q'] = np.nan

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(1, 12+1)])
    df_out = df_out.drop(columns=['PERMNO_t'])


    # Create the variable next year cumulative return
    for i in range(1, 12+1):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=(-i))

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-12))
    ls_cols = ['TRT1M_t' + str(i) for i in range(1, 12+1)]
    df_out['NTRT1Y'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)
    df_out['NTRT1Y'] = df_out['NTRT1Y'].fillna(0)
    df_out.loc[df_out['FILLED'], 'NTRT1Y'] = np.nan

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(1, 12+1)])
    df_out = df_out.drop(columns=['PERMNO_t'])

    # Momentum
    n_lags = 6
    for i in range(0, n_lags):
        df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags - 1))
    ls_cols = ['TRT1M_t' + str(i) for i in range(0, n_lags)]
    df_out['CTRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)  # Cumulative total returns (nb_lags

    df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(0, n_lags)])
    df_out = df_out.drop(columns=['PERMNO_t'])
    return df_out





# %%
# **************************************************
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************






