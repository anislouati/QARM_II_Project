# Import packages
from pathlib import Path

import numpy as np

from scripts.functions import paths
import pandas as pd
import scripts.functions as fn
from tqdm import tqdm
import pickle

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
ls_selected_cols_1 = ['LPERMNO', 'DATADATE', 'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC',
                      'ACTQ', 'ATQ', 'CEQQ', 'CHEQ', 'COGSQ', 'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ',
                      'LCTQ', 'LTQ', 'MIBTQ', 'NIQ', 'PIQ', 'PSTKQ', 'REQ', 'REVTQ', 'TXPQ', 'WCAPQ',
                      'XINTQ', 'CAPXY']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]
df_fundamentals_quarterly.rename(columns={'LPERMNO': 'PERMNO'}, inplace=True)

ls_selected_cols_2 = ['LPERMNO', 'DATADATE', 'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]
df_security_monthly.rename(columns={'LPERMNO': 'PERMNO'}, inplace=True)

ls_selected_cols_3 = ['PERMNO', 'DATE', 'BID', 'ASK', 'VOL']
df_stock_monthly = df_stock_monthly[ls_selected_cols_3]

# Create year, quarter and month cols
df_fundamentals_quarterly['YEAR'] = df_fundamentals_quarterly['DATADATE'].dt.year.astype(float)
df_fundamentals_quarterly['QTR'] = df_fundamentals_quarterly['DATADATE'].dt.quarter.astype(float)
ls_selected_cols_1 = df_fundamentals_quarterly.columns.to_list()

df_security_monthly['YEAR'] = df_security_monthly['DATADATE'].dt.year.astype(float)
df_security_monthly['QTR'] = df_security_monthly['DATADATE'].dt.quarter.astype(float)
df_security_monthly['MTH'] = df_security_monthly['DATADATE'].dt.month.astype(float)
ls_selected_cols_2 = df_security_monthly.columns.to_list()

df_stock_monthly['YEAR'] = df_stock_monthly['DATE'].dt.year.astype(float)
df_stock_monthly['QTR'] = df_stock_monthly['DATE'].dt.quarter.astype(float)
df_stock_monthly['MTH'] = df_stock_monthly['DATE'].dt.month.astype(float)
ls_selected_cols_3 = df_stock_monthly.columns.to_list()

# Filter dates (min_year-max_year)
min_year = 1990
max_year = 2023
df_fundamentals_quarterly = df_fundamentals_quarterly[(df_fundamentals_quarterly['YEAR'] >= min_year) & (df_fundamentals_quarterly['YEAR'] <= max_year)]
df_security_monthly = df_security_monthly[(df_security_monthly['YEAR'] >= min_year) & (df_security_monthly['YEAR'] <= max_year)]
df_stock_monthly = df_stock_monthly[(df_stock_monthly['YEAR'] >= min_year) & (df_stock_monthly['YEAR'] <= max_year)]

# Filter stock exchanges (11: NYSE, 12: AMEX, 14: NASDAQ-NMS)
df_fundamentals_quarterly = df_fundamentals_quarterly[df_fundamentals_quarterly['EXCHG'].isin([11, 12, 14])]
ls_permnos = df_fundamentals_quarterly['PERMNO'].unique().tolist()
df_security_monthly = df_security_monthly[df_security_monthly['PERMNO'].isin(ls_permnos)]
df_stock_monthly = df_stock_monthly[df_stock_monthly['PERMNO'].isin(ls_permnos)]

# Sort data and reset index
df_fundamentals_quarterly = df_fundamentals_quarterly.sort_values(by=['PERMNO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)
df_security_monthly = df_security_monthly.sort_values(by=['PERMNO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)
df_stock_monthly = df_stock_monthly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Create additional variables
df_fundamentals_quarterly['CAPXQ'] = df_fundamentals_quarterly['CAPXY']
df_fundamentals_quarterly['WCAPCHQ'] = df_fundamentals_quarterly['WCAPQ']

j = 0
idx_tmp = df_fundamentals_quarterly.index
for i in tqdm(idx_tmp):
    # CAPXQ
    if j == 0:
        if df_fundamentals_quarterly.loc[i, 'FQTR'] != 1:
            df_fundamentals_quarterly.loc[i, 'CAPXQ'] = None

    if j != 0:
        if df_fundamentals_quarterly.loc[i, 'FQTR'] != 1:
            if df_fundamentals_quarterly.loc[i, 'PERMNO'] == df_fundamentals_quarterly.loc[idx_tmp[j-1], 'PERMNO']:
                df_fundamentals_quarterly.loc[i, 'CAPXQ'] = df_fundamentals_quarterly.loc[i, 'CAPXY'] - df_fundamentals_quarterly.loc[idx_tmp[j-1], 'CAPXY']
            else:
                df_fundamentals_quarterly.loc[i, 'CAPXQ'] = None

    # WCAPCHQ
    if j == 0:
        df_fundamentals_quarterly.loc[i, 'WCAPCHQ'] = None

    if j != 0:
        if df_fundamentals_quarterly.loc[i, 'PERMNO'] == df_fundamentals_quarterly.loc[idx_tmp[j-1], 'PERMNO']:
            if df_fundamentals_quarterly.loc[i, 'YEAR'] == df_fundamentals_quarterly.loc[idx_tmp[j-1], 'YEAR']:
                if df_fundamentals_quarterly.loc[i, 'QTR'] - df_fundamentals_quarterly.loc[idx_tmp[j-1], 'QTR'] == 1:
                    df_fundamentals_quarterly.loc[i, 'WCAPCHQ'] = df_fundamentals_quarterly.loc[i, 'WCAPQ'] - df_fundamentals_quarterly.loc[idx_tmp[j-1], 'WCAPQ']

            elif df_fundamentals_quarterly.loc[i, 'YEAR'] - df_fundamentals_quarterly.loc[idx_tmp[j-1], 'YEAR'] == 1:
                if df_fundamentals_quarterly.loc[idx_tmp[j-1], 'QTR'] == 4:
                    df_fundamentals_quarterly.loc[i, 'WCAPCHQ'] = df_fundamentals_quarterly.loc[i, 'WCAPQ'] - df_fundamentals_quarterly.loc[idx_tmp[j-1], 'WCAPQ']

            else:
                df_fundamentals_quarterly.loc[i, 'WCAPCHQ'] = None
        else:
            df_fundamentals_quarterly.loc[i, 'WCAPCHQ'] = None

    j += 1

# Merge datasets
df_fundamentals_quarterly['KEYQ'] = df_fundamentals_quarterly['PERMNO'].astype(str) + '_' + df_fundamentals_quarterly['YEAR'].astype(str) + '_' + df_fundamentals_quarterly['QTR'].astype(str)
df_security_monthly['KEYQ'] = df_security_monthly['PERMNO'].astype(str) + '_' + df_security_monthly['YEAR'].astype(str) + '_' + df_security_monthly['QTR'].astype(str)
df_security_monthly = df_security_monthly.drop(columns=['PERMNO', 'DATADATE', 'YEAR', 'QTR'])
df_tmp = pd.merge(df_fundamentals_quarterly, df_security_monthly, on='KEYQ', how='inner')

df_tmp['KEYM'] = df_tmp['PERMNO'].astype(str) + '_' + df_tmp['YEAR'].astype(str) + '_' + df_tmp['MTH'].astype(str)
df_stock_monthly['KEYM'] = df_stock_monthly['PERMNO'].astype(str) + '_' + df_stock_monthly['YEAR'].astype(str) + '_' + df_stock_monthly['MTH'].astype(str)
df_stock_monthly = df_stock_monthly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH'])
df_data = pd.merge(df_tmp, df_stock_monthly, on='KEYM', how='inner')

# Modify/Create variables
s_mean_cshoq = df_data.groupby('KEYQ')['CSHOQ'].mean()
df_tmp = pd.DataFrame(s_mean_cshoq).reset_index(drop=False)
df_tmp.rename(columns={'CSHOQ': 'CSHOQ_NEW'}, inplace=True)
df_data = pd.merge(df_tmp, df_data, on='KEYQ', how='inner')
df_data['CSHOQ'] = df_data['CSHOQ_NEW']
df_data = df_data.drop(columns=['CSHOQ_NEW'])

df_data['XINTQ'] = df_data['XINTQ'].fillna(0)  # Fill missing values with 0 for the interest expense
df_data['TRT1M'] = df_data['TRT1M'] / 100  # Expressed in percentage points
df_data['VOL'] = df_data['VOL'] * 100  # Expressed in hundreds shares (monthly data)
df_data['DVOL'] = df_data['PRCCM'] * df_data['VOL'] / (10**6)  # Dollar volume expressed in millions
df_data['SPRDPCT'] = (df_data['ASK'] - df_data['BID']) / df_data['ASK']  # Percentage bid-ask spread

# Filter out illiquid stocks (max dollar volume < $100mil.)
min_dvol = 100
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 100]
ls_permnos = df_tmp['PERMNO'].unique().tolist()
df_data = df_data[df_data['PERMNO'].isin(ls_permnos)]

# Checkpoint data
ls_selected_cols = ['PERMNO', 'DATADATE', 'FQTR', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM',
                    'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'ACTQ', 'ATQ', 'CEQQ', 'CHEQ', 'COGSQ',
                    'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ', 'LCTQ', 'LTQ', 'MIBTQ', 'NIQ', 'PIQ',
                    'PSTKQ', 'REQ', 'REVTQ', 'TXPQ', 'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ',
                    'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M',
                    'BID', 'ASK', 'VOL', 'DVOL', 'SPRDPCT']
df_data = df_data[ls_selected_cols]
df_data.rename(columns={'DATADATE': 'DATE'}, inplace=True)
df_data = df_data.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)

# Summarize final data
df_1 = df_data.drop(columns=['PERMNO', 'DATE', 'FQTR', 'QTR', 'MTH', 'KEYQ', 'KEYM',
                             'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC'])
df_summary_1 = fn.tab_summary(df_1)

# Missing values management [...]
# TODO: value variables
# TODO: create market equity (ME)





# %%
# **************************************************
# *** Branch: SCORE COMPUTATIONS                 ***
# **************************************************

# %%
# *** Value Score ***

df_data['ME'] = df_data['PRCCM'] * df_data['CSHOQ']
df_data['BE'] = df_data['ATQ'] - df_data['LTQ']   # Book value of Equity = Total Asset - Total Liabilities

df_data['BE/ME'] = df_data['BE'] / df_data['ME'] # book-to-market equity

df_data['E/P'] = (df_data['NIQ'] / df_data['CSHOQ']) / df_data['PRCCM'] # earning-to-price

df_data['CF/P'] = ((df_data['NIQ'] + df_data['DPQ'] - df_data['WCAPCHQ'] - df_data['CAPXQ']) / df_data['CSHOQ']) / df_data['PRCCM'] # cash flow-to-price


# *** Quality Score ***

# Profitability

df_data['GPOA'] = (df_data['REVTQ'] - df_data['COGSQ']) / df_data['ATQ']
df_data['ROE'] = df_data['NIQ'] / df_data['BE']
df_data['ROA'] = df_data['NIQ'] / df_data['ATQ']
df_data['CFOA'] = (df_data['NIQ'] + df_data['DPQ'] - df_data['WCAPCHQ'] - df_data['CAPXQ']) / df_data['ATQ']
df_data['GMAR'] = (df_data['REVTQ'] - df_data['COGSQ']) / df_data['REVTQ']
df_data['ACC'] = - (df_data['WCAPCHQ'] - df_data['DPQ']) / df_data['ATQ']


# TODO : LTM function
j = 0
idx_tmp = df_data.index
df_data['LTM_REVTQ'] = df_data['REVTQ']
for i in tqdm(idx_tmp):
    if j < (4 * 3):
        df_data.loc[i,'LTM_REVTQ'] == None
    if j >=(4 * 3):
        if df_data.loc[i, 'PERMNO'] == df_data.loc[idx_tmp[j - (4 * 3)], 'PERMNO']:
            df_data.loc[i, 'LTM_REVTQ'] = pd.array([df_data.loc[idx_tmp[j - (4 * 3)], 'REVTQ'],
                                               df_data.loc[idx_tmp[j - (3 * 3)], 'REVTQ'],
                                               df_data.loc[idx_tmp[j - (2 * 3)], 'REVTQ'],
                                               df_data.loc[idx_tmp[j - (1 * 3)], 'REVTQ']]).sum(skipna= False)
        else:
            df_data.loc[i, 'LTM_REVTQ'] == None

    j = j+1

#pd.array([1,2,None]).sum(skipna= False)
df_data_test_4 = df_data.loc[df_data['TIC'] == bytes('AAPL', 'utf-8')]


# Growth
df_data['g_GPOA'] = df_data['GPOA']
df_data['g_ROE'] = df_data['ROE']
df_data['g_ROA'] = df_data['ROA']
df_data['g_CFOA'] = df_data['CFOA']
df_data['g_GMAR'] = df_data['GMAR']


j = 0
n = 5
idx_tmp = df_data.index
for i in tqdm(idx_tmp):

    if j < (n*4*3):
        df_data.loc[i, 'g_GPOA'] = None
        df_data.loc[i, 'g_ROE'] = None
        df_data.loc[i, 'g_ROA'] = None
        df_data.loc[i, 'g_CFOA'] = None
        df_data.loc[i, 'g_GMAR'] = None

    if j >= (n*4*3):
        if df_data.loc[i, 'PERMNO'] == df_data.loc[idx_tmp[j-(n*4*3)], 'PERMNO']:
            if df_data.loc[i, 'YEAR'] - df_data.loc[idx_tmp[j-(n*4*3)], 'YEAR'] == 5:
                if df_data.loc[i, 'QTR'] == df_data.loc[idx_tmp[j - (n*4*3)], 'QTR']:
                    df_data.loc[i, 'g_GPOA'] = (df_data.loc[i, 'GPOA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'GPOA']) / df_data.loc[idx_tmp[j-(n*4*3)], 'GPOA']
                    df_data.loc[i, 'g_ROE'] = (df_data.loc[i, 'ROE'] - df_data.loc[idx_tmp[j-(n*4*3)], 'ROE']) / df_data.loc[idx_tmp[j-(n*4*3)], 'ROE']
                    df_data.loc[i, 'g_ROA'] = (df_data.loc[i, 'ROA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'ROA']) / df_data.loc[idx_tmp[j-(n*4*3)], 'ROA']
                    df_data.loc[i, 'g_CFOA'] = (df_data.loc[i, 'CFOA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'CFOA']) / df_data.loc[idx_tmp[j-(n*4*3)], 'CFOA']
                    df_data.loc[i, 'g_GMAR'] = (df_data.loc[i, 'GMAR'] - df_data.loc[idx_tmp[j-(n*4*3)], 'GMAR']) / df_data.loc[idx_tmp[j-(n*4*3)], 'GMAR']

                else:
                    df_data.loc[i, 'g_GPOA'] = None
                    df_data.loc[i, 'g_ROE'] = None
                    df_data.loc[i, 'g_ROA'] = None
                    df_data.loc[i, 'g_CFOA'] = None
                    df_data.loc[i, 'g_GMAR'] = None
            else:
                df_data.loc[i, 'g_GPOA'] = None
                df_data.loc[i, 'g_ROE'] = None
                df_data.loc[i, 'g_ROA'] = None
                df_data.loc[i, 'g_CFOA'] = None
                df_data.loc[i, 'g_GMAR'] = None
        else:
            df_data.loc[i, 'g_GPOA'] = None
            df_data.loc[i, 'g_ROE'] = None
            df_data.loc[i, 'g_ROA'] = None
            df_data.loc[i, 'g_CFOA'] = None
            df_data.loc[i, 'g_GMAR'] = None

    j += 1

'''
zzz = df_data[['DATADATE', 'PERMNO','YEAR','QTR', 'GPOA', 'g_GPOA']]
df_data.iloc[0][['DATADATE', 'PERMNO','YEAR','QTR']]
df_data.iloc[0 + n*4*3+1][['DATADATE', 'PERMNO','YEAR','QTR']]
'''

# Safety

df_data['LEV'] = (df_data['DLTTQ'] + df_data['DLCQ']) / df_data['ATQ']

df_data['AZSCORE'] = (1.2*df_data['WCAPQ'] + 1.4*df_data['REQ'] + 3.3*(df_data['PIQ'] + df_data['XINTQ']) + 0.6*df_data['ME'] + df_data['REVTQ']) / df_data['ATQ']



# %%
# **************************************************
# *** Branch: COMMENTS                           ***
# **************************************************

'''
df_security_monthly_test = df_security_monthly.loc[df_security_monthly['PERMCO'] == 45483]
df_stock_monthly_test = df_stock_monthly.loc[df_stock_monthly['PERMCO'] == 45483]
df_fundamentals_quarterly_test_3 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('GOOGL', 'utf-8')]
df_fundamentals_quarterly_test_4 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('GOOG', 'utf-8')]
df_fundamentals_quarterly_test_2 = df_fundamentals_quarterly.groupby(by=['TIC']).groups.keys()
print(df_security_monthly['PERMCO'].nunique())
print(df_security_monthly['PERMNO'].nunique())

df_fundamentals_quarterly_test_3 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('GOOGL', 'utf-8')]
df_fundamentals_quarterly_test_4 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('AAPL', 'utf-8')]
df_fundamentals_quarterly_test_5 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('WMT', 'utf-8')]
'''

'''
df_fundamentals_quarterly_test = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))

ls_selected_cols_1_test = ['GVKEY', 'LPERMNO', 'LPERMCO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'REVTY', 'OANCFY', 'CAPXY', 'FQTR','DILADQ']
df_fundamentals_quarterly_test_1 = df_fundamentals_quarterly_test[ls_selected_cols_1_test]

df_fundamentals_quarterly_test_6 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('GOOGL', 'utf-8')]
df_fundamentals_quarterly_test_7 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('AAPL', 'utf-8')]
df_fundamentals_quarterly_test_8 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('WMT', 'utf-8')]
'''

'''

# %%
# **************************************************
# ***           Score Computations               ***
# **************************************************

# *** Value Score ***



df_fundamentals_quarterly_test_0 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('AAPL', 'utf-8')]

df_fundamentals_quarterly_test = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))

ls_selected_cols_1_test = ['GVKEY', 'LPERMNO', 'LPERMCO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'REVTY', 'OANCFY', 'CAPXY']
df_fundamentals_quarterly_test_1 = df_fundamentals_quarterly_test[ls_selected_cols_1_test]

df_fundamentals_quarterly_test_2 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('AAPL', 'utf-8')]

# NB: yearly variable
'''
'''
# *** Quality Score ***

# Profitability

df_data['BE'] = df_data['ATQ'] - df_data['LTQ']   # Book value of Equity = Total Asset - Total Liabilities

df_data['GPOA'] = (df_data['REVTQ'] - df_data['COGSQ']) / df_data['ATQ']

df_data['ROE'] = df_data['NIQ'] / df_data['BE']

df_data['ROA'] = df_data['NIQ'] / df_data['ATQ']

df_data['CFOA'] = (df_data['NIQ'] + df_data['DPQ'] - df_data['WCAPCHQ'] - df_data['CAPXQ']) / df_data['ATQ']

df_data['GMAR'] = (df_data['REVTQ'] - df_data['COGSQ']) / df_data['REVTQ']

df_data['ACC'] = - (df_data['WCAPCHQ'] - df_data['DPQ']) / df_data['ATQ']


# Growth




# Safety

df_data['LEV'] = (df_data['DLTTQ'] + df_data['DLCQ']) / df_data['ATQ']

df_data['AZSCORE'] = (1.2*df_data['WCAPQ'] + 1.4*df_data['REQ'] + 3.3*(df_data['PIQ'] + df_data['XINTQ']) + 0.6*df_data['ME'] + df_data['REVTQ']) / df_data['ATQ']

'''


'''
j = 0
n = 5
idx_tmp = df_data.index
for i in tqdm(idx_tmp):

    if j <= (n*4*3):
        df_data.loc[i, 'g_GPOA'] = None

    if j >= (n*4*3+1):
        #PERMNO_tpm = df_data.loc[i, 'PERMNO']
        #YEAR_tpm = df_data.loc[i, 'YEAR']
        #MTH_tpm = df_data.loc[i, 'MTH']

        GPOA = df_data.loc[i, 'GPOA']
        GPOA_t_5 = df_data[-62:i].loc[(df_data['PERMNO'] == df_data.loc[i, 'PERMNO']) & (df_data['YEAR'] == df_data.loc[i, 'YEAR'] - 5) & (df_data['MTH'] == df_data.loc[i, 'MTH'])]['GPOA']

    j += 1


PERMNO_tpm = df_data.loc[100, 'PERMNO']
YEAR_tpm = df_data.loc[100, 'YEAR']
MTH_tpm = df_data.loc[100, 'MTH']

yy = df_data.loc[(df_data['PERMNO'] == PERMNO_tpm) & (df_data['YEAR'] == YEAR_tpm) & (df_data['MTH'] == MTH_tpm)]['GPOA']
yyy = df_data.loc[(df_data['PERMNO'] == PERMNO_tpm) & (df_data['YEAR'] == YEAR_tpm - 5) & (df_data['MTH'] == MTH_tpm)]
'''