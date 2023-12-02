# Import packages
from pathlib import Path
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
ls_selected_cols_1 = ['GVKEY', 'LPERMNO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'ACTQ', 'ATQ',
                      'CEQQ', 'CHEQ', 'COGSQ', 'CSTKQ', 'DLCQ', 'DLTTQ', 'DPQ', 'EPSFXQ', 'LCTQ', 'LTQ',
                      'MIBTQ', 'NIQ', 'PIQ', 'PSTKQ', 'REQ', 'REVTQ', 'TXPQ', 'WCAPQ', 'CAPXY', 'FQTR', 'XINTQ']
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

df_fundamentals_quarterly['XINTQ'] = df_fundamentals_quarterly['XINTQ'].fillna(0) # Fill the na with 0 for the interest expense variable


# Merge datasets
df_fundamentals_quarterly['KEYQ'] = df_fundamentals_quarterly['PERMNO'].astype(str) + '_' + df_fundamentals_quarterly['YEAR'].astype(str) + '_' + df_fundamentals_quarterly['QTR'].astype(str)
df_security_monthly['KEYQ'] = df_security_monthly['PERMNO'].astype(str) + '_' + df_security_monthly['YEAR'].astype(str) + '_' + df_security_monthly['QTR'].astype(str)
df_security_monthly = df_security_monthly.drop(columns=['GVKEY', 'PERMNO', 'DATADATE', 'YEAR', 'QTR'])
df_tmp = pd.merge(df_fundamentals_quarterly, df_security_monthly, on='KEYQ', how='inner')

df_tmp['KEYM'] = df_tmp['PERMNO'].astype(str) + '_' + df_tmp['YEAR'].astype(str) + '_' + df_tmp['MTH'].astype(str)
df_stock_monthly['KEYM'] = df_stock_monthly['PERMNO'].astype(str) + '_' + df_stock_monthly['YEAR'].astype(str) + '_' + df_stock_monthly['MTH'].astype(str)
df_stock_monthly = df_stock_monthly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH'])
df_data = pd.merge(df_tmp, df_stock_monthly, on='KEYM', how='inner')



# Checkpoint data
df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as f:
    df_data = pickle.load(f)


# Modify/Create variables
s_mean_cshoq = df_data.groupby('KEYQ')['CSHOQ'].mean()
df_tmp = pd.DataFrame(s_mean_cshoq).reset_index(drop=False)


df_data['TRT1M'] = df_data['TRT1M'] / 100  # Expressed in percentage points
df_data['VOL'] = df_data['VOL'] * 100  # Expressed in hundreds shares (monthly data)
df_data['DVOL'] = df_data['PRCCM'] * df_data['VOL'] / (10**6)  # Dollar volume expressed in millions
df_data['SPRDPCT'] = (df_data['ASK'] - df_data['BID']) / df_data['ASK']  # Percentage bid-ask spread

# Filter out illiquid stocks
min_dvol = 100
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 100]
ls_permnos = df_tmp['PERMNO'].unique().tolist()

# Filter out illiquid stocks
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df = pd.DataFrame(s_max_dvols)
df = df[df['DVOL'] >= 100000000]
ls_gvkeys = df.index.to_list()

print('hello')
# Sort final data
# df_data = df_data.reindex(columns=())
df_data = df_data.sort_values(by=['PERMNO', 'DATADATE'], ascending=[True, True]).reset_index(drop=True)

# Summarize data
df_1 = df_data.drop(columns=['GVKEY', 'PERMNO', 'DATADATE', 'CONM', 'TIC', 'GSECTOR', 'LOC'])
df_summary_1 = fn.tab_summary(df_1)
print('world')

# Missing values management [...]

# TODO: value variables
# TODO: common shares outstanding fill
# TODO: create market equity (ME)








# %%
# **************************************************
# ***           Score Computations               ***
# **************************************************

df_data['BE'] = df_data['ATQ'] - df_data['LTQ']   # Book value of Equity = Total Asset - Total Liabilities

# *** Value Score ***



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

df_data['g_GPOA'] = df_data['GPOA']
df_data['g_ROE'] = df_data['ROE']
df_data['g_ROA'] = df_data['ROA']
df_data['g_CFOA'] = df_data['CFOA']
df_data['g_GMAR'] = df_data['GMAR']
df_data['g_ACC'] = df_data['ACC']


j = 0
n = 5
idx_tmp = df_fundamentals_quarterly.index
for i in tqdm(idx_tmp):

    if j < n*4:
        df_data.loc[i, 'g_GPOA'] = None

    if j >= n*4:
        if df_fundamentals_quarterly.loc[i, 'PERMNO'] == df_fundamentals_quarterly.loc[idx_tmp[j-1], 'PERMNO']:
            df_fundamentals_quarterly.loc[i, 'g_GPOA'] = (df_fundamentals_quarterly.loc[i, 'GPOA'] - df_fundamentals_quarterly.loc[idx_tmp[j-n*4], 'GPOA']) / df_fundamentals_quarterly.loc[idx_tmp[j-n*4], 'GPOA']
        else:
            df_fundamentals_quarterly.loc[i, 'g_GPOA'] = None

    j += 1


# Safety

df_data['LEV'] = (df_data['DLTTQ'] + df_data['DLCQ']) / df_data['ATQ']

df_data['AZSCORE'] = (1.2*df_data['WCAPQ'] + 1.4*df_data['REQ'] + 3.3*(df_data['PIQ'] + df_data['XINTQ']) + 0.6*df_data['ME'] + df_data['REVTQ']) / df_data['ATQ']



# %%
# **************************************************
# *** Branch: Comments                           ***
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

ls_selected_cols_1_test = ['GVKEY', 'LPERMNO', 'LPERMCO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'REVTY', 'OANCFY', 'CAPXY', 'FQTR','XINTQ', 'XINTY' , 'INTPNY', 'NIITY', 'FINXINTQ']
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
