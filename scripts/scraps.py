
# %%
# *** Commented Out ***

"""
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
"""

'''
df_fundamentals_quarterly_test = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))
ls_selected_cols_1_test = ['GVKEY', 'LPERMNO', 'LPERMCO', 'DATADATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC', 'REVTY', 'OANCFY', 'CAPXY', 'FQTR','DILADQ']
df_fundamentals_quarterly_test_1 = df_fundamentals_quarterly_test[ls_selected_cols_1_test]
df_fundamentals_quarterly_test_6 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('GOOGL', 'utf-8')]
df_fundamentals_quarterly_test_7 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('AAPL', 'utf-8')]
df_fundamentals_quarterly_test_8 = df_fundamentals_quarterly_test_1.loc[df_fundamentals_quarterly_test_1['TIC'] == bytes('WMT', 'utf-8')]
'''

'''
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

'''
# Preprocess data ()
def preprocess_4(df_data):
    df_out = df_data
    ls_permnos = df_out['PERMNO'].unique().tolist()

    df_dates = pd.DataFrame(pd.date_range(start=datetime(1989, 1, 1), end=datetime(2023, 12, 31), freq='BM').rename('DATE'))
    df_dates['YEAR'] = df_dates['DATE'].dt.year.astype(float)
    df_dates['QTR'] = df_dates['DATE'].dt.quarter.astype(float)
    df_dates['MTH'] = df_dates['DATE'].dt.month.astype(float)

    dic_dfs = {}
    for permno in tqdm(ls_permnos):
        s_dates = df_out[df_out['PERMNO'] == permno]['DATE']
        dt_start, dt_end = s_dates.min(), s_dates.max()
        pos_start = df_dates.index[(df_dates['YEAR'] == dt_start.year) & (df_dates['MTH'] == dt_start.month)].tolist()[0]
        pos_end = df_dates.index[(df_dates['YEAR'] == dt_end.year) & (df_dates['MTH'] == dt_end.month)].tolist()[0]

        df_tmp = df_dates.loc[pos_start:pos_end, ['DATE']]
        df_tmp['PERMNO'] = permno
        df_tmp = fn.preprocessing_1(df_tmp)
        df_tmp = df_tmp[['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM']]
        dic_dfs[permno] = df_tmp

    return dic_dfs

dic_dfs = preprocess_4(df_data)

df_test = pd.DataFrame.from_dict(dic_dfs, orient='index')

# Check FQTR pattern
j = 0
idx_tmp = df_fundamentals_quarterly.index
list_check_FQTR = []
for i in tqdm(idx_tmp):
    if j != 0:
        if df_fundamentals_quarterly.loc[i, 'PERMNO'] == df_fundamentals_quarterly.loc[idx_tmp[j - 1], 'PERMNO']:
            if df_fundamentals_quarterly.loc[i, 'FQTR'] == 1:
                if df_fundamentals_quarterly.loc[i, 'FQTR'] - df_fundamentals_quarterly.loc[idx_tmp[j - 1], 'FQTR'] != -3:
                    list_check_FQTR.append(idx_tmp[j])
                    #print(idx_tmp[j])
            if df_fundamentals_quarterly.loc[i, 'FQTR'] in [2,3,4]:
                if df_fundamentals_quarterly.loc[i, 'FQTR'] - df_fundamentals_quarterly.loc[idx_tmp[j - 1], 'FQTR'] != 1:
                    list_check_FQTR.append(idx_tmp[j])
                    #print(idx_tmp[j])
    j = j + 1
ls = list(set(df_fundamentals_quarterly.loc[list_check_FQTR, 'PERMNO'].to_list()))
'''

'''
j = 0
idx_tmp = df_data.index
df_data['LTM_REVTQ'] = df_data['REVTQ']
for i in tqdm(idx_tmp):
    if j < (3 * 3):
        df_data.loc[i,'LTM_REVTQ'] == None
    if j >=(3 * 3):
        if df_data.loc[i, 'PERMNO'] == df_data.loc[idx_tmp[j - (3 * 3)], 'PERMNO']:
            df_data.loc[i, 'LTM_REVTQ'] = pd.array([df_data.loc[idx_tmp[j - (3 * 3)], 'REVTQ'],
                                               df_data.loc[idx_tmp[j - (2 * 3)], 'REVTQ'],
                                               df_data.loc[idx_tmp[j - (1 * 3)], 'REVTQ'],
                                               df_data.loc[idx_tmp[j - (0 * 3)], 'REVTQ']]).sum(skipna= False)
        else:
            df_data.loc[i, 'LTM_REVTQ'] == None

    j = j+1
'''

'''
#pd.array([1,2,None]).sum(skipna= False)
df_data_test_4 = df_data.loc[df_data['TIC'] == bytes('AAPL', 'utf-8')]
df_data_test_5 = df_data_test_4[['PERMNO','FQTR','YEAR','QTR','MTH','REVTQ','REVTQ_LTM','NIQ', 'NIQ_LTM']]
'''

'''
s_mean_cshoq = df_data.groupby('KEYQ')['CSHOQ'].mean()
df_tmp = pd.DataFrame(s_mean_cshoq).reset_index(drop=False)
df_tmp.rename(columns={'CSHOQ': 'CSHOQ_NEW'}, inplace=True)
df_data = pd.merge(df_tmp, df_data, on='KEYQ', how='inner')
df_data['CSHOQ'] = df_data['CSHOQ_NEW']
df_data = df_data.drop(columns=['CSHOQ_NEW'])
'''

'''
df_data['ME'] = df_data['PRCCM'] * df_data['CSHOQ']
df_data['BE'] = df_data['ATQ'] - df_data['LTQ']   # Book value of Equity = Total Asset - Total Liabilities
df_data['BE/ME'] = df_data['BE'] / df_data['ME'] # book-to-market equity
df_data['E/P'] = (df_data['NIQ'] / df_data['CSHOQ']) / df_data['PRCCM'] # earning-to-price
df_data['CF/P'] = ((df_data['NIQ'] + df_data['DPQ'] - df_data['WCAPCHQ'] - df_data['CAPXQ']) / df_data['CSHOQ']) / df_data['PRCCM'] # cash flow-to-price
'''

'''
df_data['GPOA'] = (df_data['REVTQ'] - df_data['COGSQ']) / df_data['ATQ']
df_data['ROE'] = df_data['NIQ'] / df_data['BE']
df_data['ROA'] = df_data['NIQ'] / df_data['ATQ']
df_data['CFOA'] = (df_data['NIQ'] + df_data['DPQ'] - df_data['WCAPCHQ'] - df_data['CAPXQ']) / df_data['ATQ']
df_data['GMAR'] = (df_data['REVTQ'] - df_data['COGSQ']) / df_data['REVTQ']
df_data['ACC'] = - (df_data['WCAPCHQ'] - df_data['DPQ']) / df_data['ATQ']
'''

'''
zzz = df_data[['DATADATE', 'PERMNO','YEAR','QTR', 'GPOA', 'g_GPOA']]
df_data.iloc[0][['DATADATE', 'PERMNO','YEAR','QTR']]
df_data.iloc[0 + n*4*3+1][['DATADATE', 'PERMNO','YEAR','QTR']]
'''