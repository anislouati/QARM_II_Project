# Import packages
from pathlib import Path
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
    ls_permnos = df_out['PERMNO'].unique().tolist()

    df_dates = pd.DataFrame({'DATE': pd.Series(df_out['DATE'].unique().tolist())})  # Assumption: df_data['DATE'] contains all monthly dates
    df_dates['YEAR'] = df_dates['DATE'].dt.year.astype(float)
    df_dates['MTH'] = df_dates['DATE'].dt.month.astype(float)
    df_dates = df_dates.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

    # Fill missing dates with nans
    ls_dfs = []
    for permno in tqdm(ls_permnos, desc='Preprocessing (4)'):
        s_tmp = df_out[df_out['PERMNO'] == permno]['DATE']
        dt_start, dt_end = s_tmp.min(), s_tmp.max()
        pos_start = df_dates.index[(df_dates['YEAR'] == dt_start.year) & (df_dates['MTH'] == dt_start.month)].tolist()[0]
        pos_end = df_dates.index[(df_dates['YEAR'] == dt_end.year) & (df_dates['MTH'] == dt_end.month)].tolist()[0]

        df_tmp = df_dates.loc[pos_start:pos_end, ['DATE']]
        df_tmp['PERMNO'] = permno
        df_tmp = preprocessing_1(df_tmp)
        df_tmp = df_tmp[['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM']]
        df_tmp = df_tmp[~df_tmp['KEYM'].isin(df_out[df_out['PERMNO'] == permno]['KEYM'])]  # Exclude obs present in dataset
        ls_dfs += [df_tmp]

    ls_dfs = [df_out] + ls_dfs
    df_out = pd.concat(ls_dfs, axis=0, ignore_index=True)
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
    df_out['TRT1M'] = df_out['TRT1M'] / 100  # Total return expressed as float (before: percentage points)
    df_out['VOL'] = df_out['VOL'] * 100  # Volume expressed in units (before: hundreds shares, monthly data)
    df_out['SHROUT'] = df_out['SHROUT'] / 1000  # Shares outstanding expressed in mil.
    df_out['DVOL'] = (df_out['PRCCM'] * df_out['VOL']) / (10 ** 6)  # Dollar volume expressed in mil.
    df_out['SPRDPCT'] = (df_out['ASK'] - df_out['BID']) / df_out['ASK']  # Bid-Ask spread expressed as float

    return df_out


def tab_summary(df_data):
    df_summary = pd.DataFrame({'Count': df_data.count(),  # Count of non-missing values
                               'Missing Pct': (df_data.isna().sum() / len(df_data)),  # Missing values as percentage
                               'Min': df_data.min(),
                               'Mean': df_data.mean(),
                               'Median': df_data.median(),
                               'Max': df_data.max()})
    return df_summary








