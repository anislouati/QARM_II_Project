# Import packages
from pathlib import Path
from scripts.functions import paths
import pandas as pd
import scripts.functions as fn
from tqdm import tqdm

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
ls_selected_cols_1 = ['GVKEY', 'LPERMNO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'ACTQ', 'ATQ',
                      'CEQQ', 'CHEQ', 'COGSQ', 'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ', 'LCTQ', 'LTQ',
                      'MIBTQ', 'NIQ', 'PIQ', 'PSTKQ', 'REQ', 'REVTQ', 'TXPQ', 'WCAPQ', 'CAPXY']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]
df_fundamentals_quarterly.rename(columns={'LPERMNO': 'PERMNO'}, inplace=True)

ls_selected_cols_2 = ['GVKEY', 'LPERMNO', 'DATADATE', 'CSHOQ', 'CSHTRM', 'PRCCM', 'TRT1M']
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
df_fundamentals_quarterly = df_fundamentals_quarterly[df_fundamentals_quarterly['EXCHG'].isin([11., 12., 14.])]
ls_permnos = df_fundamentals_quarterly['PERMNO'].unique().tolist()
df_security_monthly = df_security_monthly[df_security_monthly['PERMNO'].isin(ls_permnos)]
df_stock_monthly = df_stock_monthly[df_stock_monthly['PERMNO'].isin(ls_permnos)]

# Sort data and reset index
df_fundamentals_quarterly = df_fundamentals_quarterly.sort_values(by=['PERMNO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)
df_security_monthly = df_security_monthly.sort_values(by=['PERMNO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)
df_stock_monthly = df_stock_monthly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Compute additional variables [1]
df_fundamentals_quarterly['CAPXQ'] = df_fundamentals_quarterly['CAPXY']
df_fundamentals_quarterly['WCAPCHQ'] = df_fundamentals_quarterly['WCAPQ']  # D_WC





j = 0
idx_tmp = df_fundamentals_quarterly.index
for i in tqdm(idx_tmp):
    # CAPXQ
    if j == 0:
        if df_fundamentals_quarterly.loc[i, 'QTR'] != 4:
            df_fundamentals_quarterly.loc[i, 'CAPXQ'] = None

    if j != 0:
        if df_fundamentals_quarterly.loc[i, 'QTR'] != 4:
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
df_fundamentals_quarterly['MERGEKEY'] = df_fundamentals_quarterly['PERMNO'].astype(str) + '_' + df_fundamentals_quarterly['YEAR'].astype(str) + '_' + df_fundamentals_quarterly['QTR'].astype(str)
df_security_monthly['MERGEKEY'] = df_security_monthly['PERMNO'].astype(str) + '_' + df_security_monthly['YEAR'].astype(str) + '_' + df_security_monthly['QTR'].astype(str)
df_security_monthly = df_security_monthly.drop(columns=['GVKEY', 'PERMNO', 'DATADATE', 'YEAR', 'QTR'])
df_tmp = pd.merge(df_fundamentals_quarterly, df_security_monthly, on='MERGEKEY', how='inner')
df_tmp = df_tmp.drop(columns=['MERGEKEY'])

df_tmp['MERGEKEY'] = df_tmp['PERMNO'].astype(str) + '_' + df_tmp['YEAR'].astype(str) + '_' + df_tmp['MTH'].astype(str)
df_stock_monthly['MERGEKEY'] = df_stock_monthly['PERMNO'].astype(str) + '_' + df_stock_monthly['YEAR'].astype(str) + '_' + df_stock_monthly['MTH'].astype(str)
df_stock_monthly = df_stock_monthly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH'])
df_data = pd.merge(df_tmp, df_stock_monthly, on='MERGEKEY', how='inner')
df_data = df_data.drop(columns=['MERGEKEY'])













# Compute additional variables [2]
df_data['VOL'] = df_data['VOL']*100
df_data['MID'] = (df_data['ASK'] + df_data['BID']) / 2
df_data['SPREADPCT'] = (df_data['ASK'] - df_data['BID']) / df_data['ASK']
df_data['DVOL'] = df_data['MID'] * df_data['VOL']



# Filter out illiquid stocks
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df = pd.DataFrame(s_max_dvols)
df = df[df['DVOL'] >= 100000000]
ls_gvkeys = df.index.to_list()

# Filter out illiquid stocks
s_max_dvols = df_stock_monthly.groupby('PERMCO')['DVOL'].max()
df = pd.DataFrame(s_max_dvols)
df = df[df['DolVol'] >= 100000000]
ls_gvkeys = df.index.to_list()


# Sort final data
# df_data = df_data.reindex(columns=())
df_data = df_data.sort_values(by=['PERMNO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)

# Summarize data
df_1 = df_data.drop(columns=['GVKEY', 'PERMNO', 'DATADATE', 'CONM', 'TIC', 'GSECTOR', 'LOC'])
df_summary_1 = fn.tab_summary(df_1)






# %%


'''
df_security_monthly_test = df_security_monthly.loc[df_security_monthly['PERMCO'] == 45483]
df_stock_monthly_test = df_stock_monthly.loc[df_stock_monthly['PERMCO'] == 45483]
df_fundamentals_quarterly_test_3 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('GOOGL', 'utf-8')]
df_fundamentals_quarterly_test_4 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('GOOG', 'utf-8')]
df_fundamentals_quarterly_test_2 = df_fundamentals_quarterly.groupby(by=['TIC']).groups.keys()
print(df_security_monthly['PERMCO'].nunique())
print(df_security_monthly['PERMNO'].nunique())
'''



# Missing values management [...]


# %%
# **************************************************
# ***           Score Computations               ***
# **************************************************

# *** Value Score ***

'''
df_fundamentals_quarterly_test_0 = df_fundamentals_quarterly.loc[df_fundamentals_quarterly['TIC'] == bytes('AAPL', 'utf-8')]

df_fundamentals_quarterly_test = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))

ls_selected_cols_1_test = ['GVKEY', 'LPERMNO', 'LPERMCO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'REVTY', 'OANCFY', 'CAPXY']
df_fundamentals_quarterly_test_1 = df_fundamentals_quarterly_test[ls_selected_cols_1_test]

df_fundamentals_quarterly_test_2 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('AAPL', 'utf-8')]

# NB: yearly variable
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
