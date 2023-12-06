
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

'''
def get_LTM(variables):
    j = 0
    idx_tmp = df_data.index
    for v in variables:
        df_data[v + '_LTM'] = df_data[v]
    for i in tqdm(idx_tmp):
        for v in variables:
            if j < (3 * 3):
                df_data.loc[i, v + '_LTM'] = None
            if j >= (3 * 3):
                if df_data.loc[i, 'PERMNO'] == df_data.loc[idx_tmp[j - (3 * 3)], 'PERMNO']:
                    df_data.loc[i, v + '_LTM'] = pd.array([df_data.loc[idx_tmp[j - (3 * 3)], v],
                                                            df_data.loc[idx_tmp[j - (2 * 3)], v],
                                                            df_data.loc[idx_tmp[j - (1 * 3)], v],
                                                            df_data.loc[idx_tmp[j - (0 * 3)], v]]).sum(skipna=False)
                else:
                    df_data.loc[i, v + '_LTM'] = None

        j = j + 1

get_LTM(['REVTQ'])
#get_LTM(['REVTQ', 'NIQ', 'COGSQ', 'DPQ', 'WCAPCHQ', 'CAPXQ', 'REQ', 'PIQ', 'XINTQ'])

def get_LTM_2():
    return


#df_data['REVTQ_LTM_2'] = np.nan
df_data['REVTQ_t_3'] = df_data['REVTQ'].shift(periods=3*3)
df_data['REVTQ_t_2'] = df_data['REVTQ'].shift(periods=2 * 3)
df_data['REVTQ_t_1'] = df_data['REVTQ'].shift(periods=1 * 3)
df_data['PERMNO_t_3'] = df_data['PERMNO'].shift(periods=3*3)

col_list = ['REVTQ_t_3', 'REVTQ_t_2', 'REVTQ_t_1','REVTQ']


if df_data['PERMNO'] == df_data['PERMNO_t_3']:
    return

#np.where(df['Courses'] == 'Spark', 1000, 2000)
#df_data['REVTQ_LTM_2'] = df[col_list].sum(axis=1, skipna=False)

df_data['REVTQ_LTM_2'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t_3'], df_data[col_list].sum(axis=1, skipna=False), np.nan)

test_LTM = df_data['REVTQ_LTM'].fillna(-1000000000) == df_data['REVTQ_LTM_2'].fillna(-1000000000)
print(len(test_LTM))
print(test_LTM.sum())
'''

'''
# Growth
df_data['d_GPOA'] = df_data['GPOA']
df_data['d_ROE'] = df_data['ROE']
df_data['d_ROA'] = df_data['ROA']
df_data['d_CFOA'] = df_data['CFOA']
df_data['d_GMAR'] = df_data['GMAR']

j = 0
n = 5
idx_tmp = df_data.index
for i in tqdm(idx_tmp):

    if j < (n*4*3):
        df_data.loc[i, 'd_GPOA'] = None
        df_data.loc[i, 'd_ROE'] = None
        df_data.loc[i, 'd_ROA'] = None
        df_data.loc[i, 'd_CFOA'] = None
        df_data.loc[i, 'd_GMAR'] = None

    if j >= (n*4*3):
        if df_data.loc[i, 'PERMNO'] == df_data.loc[idx_tmp[j-(n*4*3)], 'PERMNO']:
            df_data.loc[i, 'd_GPOA'] = (df_data.loc[i, 'GPOA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'GPOA'])
            df_data.loc[i, 'd_ROE'] = (df_data.loc[i, 'ROE'] - df_data.loc[idx_tmp[j-(n*4*3)], 'ROE'])
            df_data.loc[i, 'd_ROA'] = (df_data.loc[i, 'ROA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'ROA'])
            df_data.loc[i, 'd_CFOA'] = (df_data.loc[i, 'CFOA'] - df_data.loc[idx_tmp[j-(n*4*3)], 'CFOA'])
            df_data.loc[i, 'd_GMAR'] = (df_data.loc[i, 'GMAR'] - df_data.loc[idx_tmp[j-(n*4*3)], 'GMAR'])

        else:
            df_data.loc[i, 'd_GPOA'] = None
            df_data.loc[i, 'd_ROE'] = None
            df_data.loc[i, 'd_ROA'] = None
            df_data.loc[i, 'd_CFOA'] = None
            df_data.loc[i, 'd_GMAR'] = None

    j += 1

n = 5

df_data['GPOA_t'] = -df_data['GPOA'].shift(periods=n* 4 * 3)

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n* 4 * 3)

col_list = ['GPOA_t', 'GPOA']

df_data['d_GPOA_2'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[col_list].sum(axis=1, skipna=False), np.nan)

df_data = df_data.drop(columns=['GPOA_t', 'PERMNO_t'])

test_LTM = df_data['d_GPOA'].fillna(-1000000000) == df_data['d_GPOA_2'].fillna(-1000000000)
print(len(test_LTM))
print(test_LTM.sum())
'''

'''
zzz = df_data[['DATE', 'PERMNO', 'QTR', 'GPOA', 'd_GPOA', 'ROE','d_ROE', 'ROA', 'd_ROA', 'CFOA', 'd_CFOA','GMAR', 'd_GMAR']]
zzz_test = zzz.loc[df_data['TIC'] == bytes('AAPL', 'utf-8')]
'''

'''
n=5
for i in range(1,n*12+1):
    df_data['TRT1M' + 't_' + str(i)] = df_data['TRT1M'].shift(periods=i)
for i in range(1, n * 12 + 1):
    df_data['SPRTRN' + 't_' + str(i)] = df_data['SPRTRN'].shift(periods=i)

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n * 4 * 3)

col_list_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(1,n*12+1)]
col_list_TRT1M.append('TRT1M')

col_list_SPRTRN = ['SPRTRN' + 't_' + str(i) for i in range(1,n*12+1)]
col_list_SPRTRN.append('SPRTRN')

df_data['TRT1M_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_TRT1M].mean(axis=1, skipna=False), np.nan) # Check the PERMNO
df_data['SPRTRN_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], -df_data[col_list_SPRTRN].mean(axis=1, skipna=False), np.nan) # Check the PERMNO

for i in range(1,n*12+1):
    df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'TRT1M_mean']].sum(axis=1, skipna=False)

for i in range(1, n * 12 + 1):
    df_data['SPRTRN' + 't_' + str(i)] = df_data['SPRTRN'].shift(periods=i)

for i in range(1, n * 12 + 1):
    df_data['Prod_TRT1M_SPRTRN' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'SPRTRN' + 't_' + str(i)]].product(axis=1, skipna=False)

col_list_Cov_TRT1M_SPRTRN= ['TRT1M' + 't_' + str(i) for i in range(1,n*12+1)]
col_list_Cov_TRT1M_SPRTRN.append('TRT1M')

df_data['Cov_TRT1M_SPRTRN'] =
'''

'''
tmp = pd.DataFrame()
tmp['TRT1M' + 't_' + str(i)] = df_data['TRT1M'].shift(periods=i)
df_data = pd.concat([df_data, tmp], axis=1)
'''

'''
 #tmp =pd.DataFrame({'TRT1M' + 't_' + str(i): df_data['TRT1M'].shift(periods=i)})
df_data = pd.concat([df_data, pd.DataFrame({'TRT1M' + 't_' + str(i): df_data['TRT1M'].shift(periods=i)})], axis=1) 
'''

'''
zzz_test = df_data.loc[df_data['TIC'] == bytes('WMT', 'utf-8')]
'''

'''
#df_data['SPRTRN_mean'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[['TRT1M'+'t_' + str(i) for i in range(1,n*12+1)]].mean(), np.nan)


#df_data['TRT1M_list'] = 'None'
#df_data = pd.concat([df_data['TRT1M'+'t_' + str(i)] for i in range(1,n*12+1)]).sort_index().values.tolist()
#df_data['TRT1M_list'] = [df_data['TRT1M'+'t_' + str(i)] for i in range(1,n*12+1)]

# Rename the concatenated column and drop the original columns
df = pd.concat([df, concatenated_cols['Name_Age_Country']], axis=1)
df = df.rename(columns={'Name_Age_Country': 'Name|Age|Country'})
df = df.drop(columns=['Name', 'Age', 'Country'])


if df_data['PERMNO'] == df_data['PERMNO_t']:


col_list = [v + '_t', v]

df['d_' + v] = np.where(df['PERMNO'] == df['PERMNO_t'], df[col_list].sum(axis=1, skipna=False), np.nan)

df = df.drop(columns=[v + '_t', 'PERMNO_t'])
'''