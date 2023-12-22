
# %%
# *** Commented Out ***

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

'''
min_dvol = 100
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 100]
'''

'''
df_data['ATQ_s'] = df_data['ATQ'].shift(periods=(3))
df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=(3))
df_data['ATQ_s'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data['ATQ_s'],  np.nan)
df_data = df_data[['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'ATQ','ATQ_s']]
'''

'''
min_dvol = 100
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 100]
'''

'''
#for i in dic_data:
#df['max_rank'] = df['Number_legs'].rank(method='max')

dic_test['BE/ME_rank'] = dic_test['BE/ME'].rank(method='max',ascending=False)
dict_test_3 = dic_test[['BE/ME_rank','BE/ME']]
'''

'''
def tab_summary(df_data):
    df_summary = pd.DataFrame({'Count': df_data.count(),  # Count of non-missing values
                               'Missing Pct': (df_data.isna().sum() / len(df_data)),  # Missing values as percentage
                               'Min': df_data.min(),
                               'Mean': df_data.mean(),
                               'Median': df_data.median(),
                               'Max': df_data.max()})
    return df_summary
'''

'''
# Filter out illiquid stocks (max dollar volume (monthly) < $100mil.)
min_dvol = 40
s_max_dvols = df_data.groupby('PERMNO')['DVOL'].max()
df_tmp = pd.DataFrame(s_max_dvols).reset_index(drop=False)
df_tmp = df_tmp[df_tmp['DVOL'] >= 40]
ls_permnos = df_tmp['PERMNO'].unique().tolist()
df_data = df_data[df_data['PERMNO'].isin(ls_permnos)]
'''

'''
dic_test = dic_data[list(dic_data.keys())[332]]
dic_test = dic_test[dic_test['DVOL'] >= 40]

dic_test_2 = dic_data[list(dic_data.keys())[360]]
dic_test_2 = dic_test_2[dic_test_2['DVOL'] >= 40]
'''

'''
df_out['M_TRT1M'] = - df_out['M_TRT1M']
for i in range(0, n * 12):
    df_out['TRT1M' + 't_' + str(i)] = df_out[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)
'''

'''
for i in range(0, n * 12):
    if i == 0:
        df_out['LS_TRT1M'] = df_out['TRT1M' + 't_' + str(i)].astype(str)
    else:
        df_out['LS_TRT1M'] = df_out['LS_TRT1M'] + ',' + df_out['TRT1M' + 't_' + str(i)].astype(str)
'''

'''
test_df.astype(str).agg(', '.join, axis=1)
np.array(your_list,dtype=float)
np.fromstring(df_out['LS_TRT1M'], dtype=float, sep=',')
np.array(df_out['LS_TRT1M'].split(','),dtype=float)
np.fromstring(df_out['LS_TRT1M'], dtype=float, sep=',')
df_out[ls_cols_TRT1M].apply(lambda row: row.tolist(), axis=1)
'''

'''
df_out['LS_TRT1M'] = df_out[ls_cols_TRT1M].astype(str).agg(','.join, axis=1)
print('Done')
df_out['LS_TRT1M'] = df_out['LS_TRT1M'].tolist()
'''

'''
df_out['LS_TRT1M'] = df_out[ls_cols_TRT1M].values.tolist()
'''

'''
n = 5
for i in range(n*12-1,-1,-1):
    df_data['TRT1M' + 't_' + str(i)] = df_data['TRT1M'].shift(periods=i)

df_data['PERMNO_t'] = df_data['PERMNO'].shift(periods=n * 4 * 3 - 1)  # Take n*12 months taking the current months: first date n*12 - 1
ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n*12-1,-1,-1)]

# Compute (-1)* mean return over the last n*12 months
df_data['M_TRT1M'] = np.where(df_data['PERMNO'] == df_data['PERMNO_t'], df_data[ls_cols_TRT1M].mean(axis=1, skipna=False), np.nan)  # Check the PERMNO

# Compute return + (-1) * mean return
for i in range(n*12-1,-1,-1):
    df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

df_data['M_TRT1M'] = -df_data['M_TRT1M']

for i in range(n*12-1,-1,-1):
    df_data['TRT1M' + 't_' + str(i)] = df_data[['TRT1M' + 't_' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

ls_cols_TRT1M = ['TRT1M' + 't_' + str(i) for i in range(n*12-1,-1,-1)]
df_data['LS_TRT1M'] = df_data[ls_cols_TRT1M].values.tolist()

df_out = df_data.drop(columns=['TRT1M' + 't_' + str(i) for i in range(n*12-1,-1,-1)])
'''

'''
for n in range(n*12-1,-1,-1):
  print(n)
'''

'''
zzz = df_data['LS_TRT1M'].iloc[62][0]
zzzz= pd.DataFrame(df_data['LS_TRT1M'].iloc[62])
'''

'''
x = pd.DataFrame(df_data['LS_TRT1M'].iloc[60])
'''

'''
for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out['TRT1M'].shift(periods=(-i))

df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-3))
ls_cols = ['TRT1M_t' + str(i) for i in range(1, 4)]


df_out['M_TRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'],df_out[ls_cols].mean(axis=1, skipna=True), np.nan)


for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out[['TRT1M_t' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)

df_out['M_TRT1M'] = -df_out['M_TRT1M']

for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out[['TRT1M_t' + str(i), 'M_TRT1M']].sum(axis=1, skipna=False)


for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out['TRT1M_t' + str(i)].fillna(0)


df_out['LS_NTRT1Q'] = df_out[ls_cols].values.tolist()
df_out.loc[df_out['FILLED'], 'LS_NTRT1Q'] = np.nan

df_out = df_out.drop(columns=['M_TRT1M'])
'''

'''
df_data_test = df_data[['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED', 'FQTR',
                    'CONM', 'TIC', 'EXCHG', 'GSECTOR','TRT1M','NTRT1M','NTRT1Q','NTRT1Y']]
'''

'''
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
'''

'''
if ind_const:
    ls_tmp = ls_asts
    ls_asts = []
    min_n_asts = n_asts // len(ls_secs)  # Integer division

    for sec in ls_secs:
        df_tmp = df_data[df_data['GSECTOR'] == sec]
        if leg == 'long':
            ls_asts += df_tmp.loc[df_tmp[indicator].nlargest(min_n_asts).index, 'PERMNO'].tolist()
        if leg == 'short':
            ls_asts += df_tmp.loc[df_tmp[indicator].nsmallest(min_n_asts).index, 'PERMNO'].tolist()

    i = 0
    while (i < len(ls_tmp)) and (len(ls_asts) < n_asts):
        if ls_tmp[i] in ls_asts:
            i += 1
        else:
            ls_asts += [ls_tmp[i]]
            i += 1
'''

'''
# Next month return
df_out['NTRT1M'] = df_out['TRT1M'].shift(periods=(-1))
df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-1))
df_out['NTRT1M'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out['NTRT1M'], np.nan)
df_out['NTRT1M'] = df_out['NTRT1M'].fillna(0)
df_out.loc[df_out['FILLED'], 'NTRT1M'] = np.nan
print('- Next month return: DONE')
'''

'''
# Next quarter returns (list)
for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out['TRT1M'].shift(periods=(-i))

ls_cols = ['TRT1M_t' + str(i) for i in range(1, 4)]

for i in range(1, 4):
    df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(-i))
    df_out['TRT1M_t' + str(i)] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out['TRT1M_t' + str(i)], np.nan)

for i in range(1, 4):
    df_out['TRT1M_t' + str(i)] = df_out['TRT1M_t' + str(i)].fillna(0)

df_out['LS_NTRT1M_1Q'] = df_out[ls_cols].values.tolist()
df_out.loc[df_out['FILLED'], 'LS_NTRT1M_1Q'] = np.nan

df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(1, 4)])
df_out = df_out.drop(columns=['PERMNO_t'])
print('- Next quarter returns: DONE')
'''

'''
df_tmp = dic_data[ls_dates[-1]]
ls_asts = get_ls_asts(df_tmp, n_asts=25, ind_const=True, indicator='ZS_VAL', leg='long')
zzz = df_tmp[df_tmp['PERMNO'].isin(ls_asts)]
'''

'''
for sig_long in ls_sigs:
    for n_asts_long in ls_n_asts:
        for w_meth_long in ls_w_meth:
            for sig_short in ls_sigs:
                for n_asts_short in ls_n_asts:
                    for w_meth_short in ls_w_meth:
                        for (pct_long, pct_short) in ls_pct_long_short:
                            for ind_const in ls_ind_const:
                                for reb_freq in ls_reb_freq:
                                    port = Portfolio(dic_data=dic_data, sig_long=sig_long, n_asts_long=n_asts_long, w_meth_long=w_meth_long, pct_long=pct_long,
                                                     sig_short=sig_short, n_asts_short=n_asts_short, w_meth_short=w_meth_short, pct_short=pct_short,
                                                     ind_const=ind_const, reb_freq=reb_freq, min_short_me=1000, max_short_cl=0.4)
                                    df_port_chars = port.tab_port_chars(output_perf=False)
                                    df_ports_chars = pd.concat([df_ports_chars, df_port_chars], axis=0, ignore_index=True)
'''

'''
# Momentum
n_lags_1 = 12  # Long-term (n_lags months)
for i in range(0, n_lags_1):
    df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_1 - 1))
ls_cols = ['TRT1M_t' + str(i) for i in range(0, n_lags_1)]
df_out['CTRT1M_1'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)  # Cumulative total returns

df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(0, n_lags_1)])
df_out = df_out.drop(columns=['PERMNO_t'])
'''

'''
n_lags_2 = 3  # Short-term
for i in range(0, n_lags_2):
    df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_2 - 1))
ls_cols = ['TRT1M_t' + str(i) for i in range(0, n_lags_2)]
df_out['CTRT1M_2'] = np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)

df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(0, n_lags_2)])
df_out = df_out.drop(columns=['PERMNO_t'])
'''

'''
df_out['NCTRT1M_1'] = (-1) * df_out['CTRT1M_1']  # Take the negative (zscore)
'''

'''
n_lags_3 = 3  # Short-term
n_lags_4 = 12  # Long-term
for i in range(n_lags_3, n_lags_4):
    df_out['TRT1M_t' + str(i)] = 1 + df_out['TRT1M'].shift(periods=i)

df_out['PERMNO_t'] = df_out['PERMNO'].shift(periods=(n_lags_4 - 1))
ls_cols = ['TRT1M_t' + str(i) for i in range(n_lags_3, n_lags_4)]
df_out['NCTRT1M_2'] = (-1) * np.where(df_out['PERMNO'] == df_out['PERMNO_t'], df_out[ls_cols].product(axis=1, skipna=False) - 1, np.nan)  # Take the negative (zscore)

df_out = df_out.drop(columns=['TRT1M_t' + str(i) for i in range(n_lags_3, n_lags_4)])
df_out = df_out.drop(columns=['PERMNO_t'])
'''

'''
    ls_cols = [('ZS_' + var) for var in ['CTRT1M_2']]
    df_out['ZS_MOM_2'] = df_out[ls_cols].mean(axis=1, skipna=False)
'''

'''
    ls_cols = [('ZS_' + var) for var in ['NCTRT1M_2']]
    df_out['ZS_RMOM_2'] = df_out[ls_cols].mean(axis=1, skipna=False)
'''

'''
    # Value, Quality and Momentum (short-term)
    ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'MOM_2']]
    df_out['ZS_VAL_QLT_MOM_2'] = df_out[ls_cols].mean(axis=1, skipna=False)
'''

'''
# Value, Quality and Reverse momentum
ls_cols = [('ZS_' + var) for var in ['VAL', 'QLT', 'RMOM']]
df_out['ZS_VAL_QLT_RMOM'] = df_out[ls_cols].mean(axis=1, skipna=False)
'''

#%%
# Test

'''
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_MOM_1', n_asts_long=20, w_meth_long='RP', pct_long=200,
                 sig_short='ZS_VAL_QLT_MOM_1', n_asts_short=20, w_meth_short='RP', pct_short=100,
                 ind_const='NI', reb_freq='Q', min_short_me=1000, max_short_cl=0.4)
df_2 = port.tab_port_chars(output_perf=False)





port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=100,
                 sig_short='ZS_VAL_QLT', n_asts_short=25, w_meth_short='EW', pct_short=100,
                 ind_const='NI', reb_freq='M', min_short_me=1000, max_short_cl=0.4)
df_3 = port.tab_port_chars(output_perf=False)

df_test = dic_data['dic_asts_data'][list(dic_data['dic_asts_data'].keys())[0]]
print(port.get_ls_asts(df_test,'L'))
print(port.get_ls_asts(df_test,'S'))

port = Portfolio(dic_data=dic_data, sig_long='ZS_QLT', n_asts_long=25, w_meth_long='EW', pct_long=100,
                 sig_short='ZS_VAL_QLT', n_asts_short=25, w_meth_short='EW', pct_short=100,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.4)
df_3 = port.tab_port_chars(output_perf=False)
df_4 = port.tab_port_perf()

df_test = dic_data['dic_asts_data'][list(dic_data['dic_asts_data'].keys())[0]]
print(port.get_ls_asts(df_test,'L'))
print(port.get_ls_asts(df_test,'S'))

print(port.get_s_port_w(df_test,'L','MN').sum())

'''

'''
s_port_w = pd.Series(dtype='float64')
ls_asts = port.get_ls_asts(df_test, 'L')
n_asts = len(ls_asts)
opt_prob = False

opt_prob = True
df_rtns = pd.DataFrame(df_test.loc[df_test['PERMNO'].isin(ls_asts), 'LS_PTRT1M'].tolist()).T  # Previous returns
df_rtns.columns = ls_asts
df_covmat = df_rtns.cov()
a_covmat = np.array(df_covmat * 12)  # Annualized from monthly data

df_test.loc[df_test['PERMNO'].isin(ls_asts), 'LS_PTRT1M'].iloc[0][-1]
# Useful functions
def get_port_var(w):
    return w.T @ a_covmat @ w


# Optimization
res = minimize(fun=get_port_var, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12,
               options={'maxiter': 1000})
'''
'''
# Initialization
dic_cols = {'DATE': 'datetime64[ns]', 'PORT_C': 'float64', 'PORT_L': 'float64', 'PORT_S': 'float64',
            'PORT_NAV': 'float64', 'PORT_RTNS': 'float64',
            'L_RTNS': 'float64', 'L_POS': 'object', 'L_WT': 'object', 'L_TO': 'float64', 'L_ASTS_RTNS': 'object',
            'S_RTNS': 'float64', 'S_POS': 'object', 'S_WT': 'object', 'S_TO': 'float64', 'S_ASTS_RTNS': 'object'}
df_port_perf = pd.DataFrame(columns=list(dic_cols.keys())).astype(dtype=dic_cols)
ls_dates = list(dic_data['dic_asts_data'].keys())

# Number of (EOM) dates in rebalancing period


n_dates = 1


# Rebalancing dates
ls_reb_dates = []
t = 0  # Include initial allocation date
while t < len(ls_dates):
    if (t % n_dates) == 0:
        ls_reb_dates += [ls_dates[t]]
    t += 1

zzz = pd.DataFrame(ls_reb_dates)

ls_reb_dates = ls_reb_dates[:-1]

pct_long = 100
pct_short = 100

# Initial allocation date
df_port_perf.loc[0, 'DATE'] = ls_dates[0]
df_port_perf.loc[0, ['PORT_L', 'PORT_S']] = 0
df_port_perf.loc[0, ['PORT_C', 'PORT_NAV']] = 100  # Initial equity (normalized)
df_port_perf.loc[0, 'PORT_C'] -= (pct_long / 100) * df_port_perf.loc[0, 'PORT_NAV']
df_port_perf.loc[0, 'PORT_L'] += (pct_long / 100) * df_port_perf.loc[0, 'PORT_NAV']  # Open long
df_port_perf.loc[0, 'PORT_C'] += (pct_short / 100) * df_port_perf.loc[0, 'PORT_NAV']
df_port_perf.loc[0, 'PORT_S'] += (pct_short / 100) * df_port_perf.loc[0, 'PORT_NAV']



s_long_w = port.get_s_port_w(df_test, leg='L', w_meth='EW')

ls_long_asts = s_long_w.index.tolist()


df_long_asts_rtns = pd.DataFrame(df_test.loc[df_test['PERMNO'].isin(ls_long_asts), 'LS_NTRT1M'].tolist()).T
df_long_asts_rtns.columns = ls_long_asts
'''


'''
df_port_perf.at[1, 'L_POS'] = dict(zip(ls_long_asts, (s_long_w * df_port_perf.loc[1, 'PORT_L']).tolist()))
df_port_perf.at[1, 'L_WT'] = dict(zip(ls_long_asts, s_long_w.tolist()))
'''
'''
for j in range(1,1):
    print(j)
# Dont' excute for the firts date
'''
'''
df_test = dic_data['dic_asts_data'][list(dic_data['dic_asts_data'].keys())[1]]

s_long_w = port.get_s_port_w(df_test, leg='L', w_meth='EW')

ls_long_asts = s_long_w.index.tolist()
'''
'''
pos_tmp = 2

# Long leg
a_long_asts_rtns = np.array(df_long_asts_rtns.loc[j - 1])
df_port_perf.at[pos_tmp, 'L_ASTS_RTNS'] = dict(zip(ls_long_asts, a_long_asts_rtns.tolist()))
df_port_perf.loc[pos_tmp, 'L_RTNS'] = (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'L_WT'].values())) * a_long_asts_rtns).sum()
df_port_perf.at[pos_tmp, 'L_POS'] = dict(zip(ls_long_asts, (np.array(list(df_port_perf.loc[(pos_tmp - 1), 'L_POS'].values())) * (1 + a_long_asts_rtns)).tolist()))
df_port_perf.loc[pos_tmp, 'PORT_L'] = np.array(list(df_port_perf.loc[pos_tmp, 'L_POS'].values())).sum()
df_port_perf.at[pos_tmp, 'L_WT'] = dict(zip(ls_long_asts, (np.array(list(df_port_perf.at[pos_tmp, 'L_POS'].values())) / df_port_perf.loc[pos_tmp, 'PORT_L']).tolist()))


leg = 'L'

dic_tmp = df_4.loc[(pos_tmp - 1), (leg + '_WT')]
s_w_t_1 = pd.Series(list(dic_tmp.values()), index=list(dic_tmp.keys()), dtype='float64').rename(None)

dic_tmp = df_4.loc[pos_tmp, (leg + '_ASTS_RTNS')]
s_r_t = pd.Series(list(dic_tmp.values()), index=list(dic_tmp.keys()), dtype='float64').rename(None)
s_w_t_1_a = s_w_t_1 * ((1 + s_r_t) / (1 + df_4.loc[pos_tmp, (leg + '_RTNS')]))

dic_tmp = df_4.loc[pos_tmp, (leg + '_WT')]
s_w_t = pd.Series(list(dic_tmp.values()), index=list(dic_tmp.keys()), dtype='float64').rename(None)

dic = {0: s_w_t_1_a, 1: s_w_t}
df = pd.DataFrame.from_dict(dic, orient='index').fillna(0).sort_index(axis=1)

(df.iloc[1] - df.iloc[0]).abs().sum()



port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=280,
                 sig_short='ZS_VAL_QLT', n_asts_short=25, w_meth_short='EW', pct_short=180,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.4)
df_5 = port.tab_port_perf()
df_6 = port.tab_port_chars()

'''
'''
ls_dates = list(dic_data['dic_asts_data'].keys())
df_tmp = dic_data['dic_asts_data'][ls_dates[0]]
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT_AMOM', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT_AMOM', n_asts_short=25, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.4)
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)
'''

'''
def get_df_port_chars(sig_long, sig_short, n_asts, w_meth, pct_long_short, ind_const, reb_freq):
    port = Portfolio(dic_data=dic_data, sig_long=sig_long, n_asts_long=n_asts, w_meth_long=w_meth, pct_long=pct_long_short[0],
                     sig_short=sig_short, n_asts_short=n_asts, w_meth_short=w_meth, pct_short=pct_long_short[1],
                     ind_const=ind_const, reb_freq=reb_freq, min_short_me=1000, max_short_cl=0.4)
    df_port_chars = port.tab_port_chars(output_perf=False)
    return df_port_chars

def process_combo(combo):
    sig_long, sig_short, n_asts, w_meth, pct_long_short, ind_const, reb_freq = combo
    return get_df_port_chars(sig_long=sig_long, sig_short=sig_short, n_asts=n_asts,
                             w_meth=w_meth, pct_long_short=pct_long_short, ind_const=ind_const, reb_freq=reb_freq)
'''

'''
i = 0
start_time = time.time()
for sig in ls_sigs:
    for n_asts in ls_n_asts:
        for w_meth in ls_w_meth:
            for (pct_long, pct_short) in ls_pct_long_short:
                for ind_const in ls_ind_const:
                    for reb_freq in ls_reb_freq:
                        port = Portfolio(dic_data=dic_data, sig_long=sig, n_asts_long=n_asts, w_meth_long=w_meth, pct_long=pct_long,
                                         sig_short=sig, n_asts_short=n_asts, w_meth_short=w_meth, pct_short=pct_short,
                                         ind_const=ind_const, reb_freq=reb_freq, min_short_me=1000, max_short_cl=0.4)
                        df_port_chars = port.tab_port_chars(output_perf=False)
                        df_ports_chars = pd.concat([df_ports_chars, df_port_chars], axis=0, ignore_index=True)
                        df_ports_chars.to_pickle(Path.joinpath(paths.get('output'), 'df_ports_chars.pkl'))
                        i += 1
                        print('Port {}/{}: DONE'.format(i, n_ports))
end_time = time.time()
print('Elapsed time: {} seconds'.format(end_time - start_time))
'''

'''
# Get parameters combos using itertools.product
ls_long_sigs = ['ZS_VAL', 'ZS_QLT', 'ZS_VAL_QLT', 'ZS_VAL_QLT_AMOM']
ls_short_sigs = ['ZS_VAL', 'ZS_QLT', 'ZS_VAL_QLT', 'ZS_VAL_QLT_AMOM']
ls_n_asts = [25]
ls_w_meth = ['EW', 'MN', 'RP']
ls_pct_long_short = [(130, 30), (120, 50), (100, 90), (200, 100), (300, 200)]
ls_ind_const = ['I', 'NI']
ls_reb_freq = ['M', 'Q', 'Y']
ls_combos = list(product(ls_long_sigs, ls_short_sigs, ls_n_asts, ls_w_meth, ls_pct_long_short, ls_ind_const, ls_reb_freq))

# Grid search
df_ports_chars = pd.DataFrame()
for i in tqdm(range(len(ls_combos))):
    combo = ls_combos[i]
    df_port_chars = fn.get_df_port_chars(dic_data, combo)
    df_ports_chars = pd.concat([df_ports_chars, df_port_chars], axis=0, ignore_index=True)
    df_ports_chars.to_pickle(Path.joinpath(paths.get('output'), 'df_ports_chars.pkl'))
'''

'''
def get_df_port_chars(dic_data, combo):

    port = Portfolio(dic_data=dic_data, sig_long=combo[0], n_asts_long=combo[2], w_meth_long=combo[3], pct_long=combo[4][0],
                     sig_short=combo[1], n_asts_short=combo[2], w_meth_short=combo[3], pct_short=combo[4][1],
                     ind_const=combo[5], reb_freq=combo[6], min_short_me=1000, max_short_cl=0.4)
    df_port_chars = port.tab_port_chars(output_perf=False)
    return df_port_chars
'''

'''
# Plot portfolio performances (OS)
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
ax.set_title('Portfolios Performances (OS, Init=100)', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(s_min_var_os_port_perf, label='Min-Var', color='red', lw=3)
ax.plot(s_value_w_os_port_perf, label='Val-Weight', color='green', lw=3)
ax.plot(s_equal_w_os_port_perf, label='Eq-Weight', color='blue', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('output'), 'Project1', 'P1_Q1.5_os_port_perfs.png'))
plt.close()
'''

'''
# Plot distribution of carbon intensity
sns.set(context='paper', style='ticks', font_scale=1.5)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
ax.set_title('Distribution of Carbon Intensity (Y=2021)', size=28)
sns.histplot(df_carb_int_1m.iloc[-1], bins=25, stat='density', kde=False, color='royalblue', edgecolor='white', alpha=0.8)
sns.kdeplot(df_carb_int_1m.iloc[-1], color='red', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.set_xlim(left=0)
ax.set_xlabel('Carbon Intensity', size=20)
ax.set_ylabel('Density', size=20)
ax.grid(axis='y', alpha=0.4)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('output'), 'Project1', 'P1_Q2.1_dist_carbon_intensity.png'))
plt.close()
'''

'''
# Compare the efficient frontier
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
fig.suptitle('Classic and Resampled Efficient Frontiers', size=28)
x_1 = df_sample_EF_plugin['std']
y_1 = df_sample_EF_plugin['mean']
ax.plot(x_1, y_1, linewidth=3)
x_2 = df_resampled_EF['std']
y_2 = df_resampled_EF['mean']
ax.plot(x_2, y_2, linewidth=3)
ax.tick_params(axis='both', labelsize=18)
ax.set_xlabel('Annualised standard deviation', size=20)
ax.set_ylabel('Annualised average return', size=20)
ax.legend(['Classic Efficient Frontier', 'Resampled Efficient Frontier'], fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('output'), 'Project1', 'P1_Q1.3_sample_vs_resampled_EF_Q=' + str(Q) + '.png'))
plt.close()
'''

'''
# Compare repartition of the weights in the efficient frontier for each expected return level
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 10), dpi=300)
fig.suptitle('Classic and Resampled Efficient Frontiers Weights', size=28)

ax1.stackplot(df_sample_EF_plugin['mean'], abs(df_sample_EF_plugin_w))
ax1.set_title('Classic Efficient Frontier Weights', size=24)
ax.tick_params(axis='both', labelsize=16)
ax1.set_xlabel('Annualised average return', size=20)
ax1.set_ylabel('Cumulative of weights absolute value', size=20)
ax1.set_xlim(0.1, 0.25)
ax1.set_ylim(0, 5)

ax2.stackplot(df_resampled_EF_w_p.T.index, abs(df_resampled_EF_w_p))
ax2.set_title('Resampled Efficient Frontier Weights', size=24)
ax.tick_params(axis='both', labelsize=16)
ax2.set_xlabel('Annualised average return', size=20)
ax2.set_ylabel('Cumulative of weights absolute value', size=20)
ax2.set_xlim(0.1, 0.25)
ax2.set_ylim(0, 5)

fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('output'), 'Project1', 'P1_Q1.3_sample_vs_resampled_EF_weights_Q=' + str(Q) + '.png'))
plt.close()
'''

'''
# Plot portfolios performances (IS)
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
ax.set_title('Portfolios Performances (IS, Init=100)', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(min_var_is_port_perf, label='Min-Var', color='red', lw=3)
ax.plot(value_w_is_port_perf, label='Val-Weight', color='green', lw=3)
ax.plot(equal_w_is_port_perf, label='Eq-Weight', color='blue', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('output'), 'Project1', 'P1_Q1.4_is_ports_perfs.png'))
plt.close()
'''

'''
# Plot min-var performances (OS, plugin vs. long-only)
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
ax.set_title('Min-Var Performances (OS, Init=100)', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(s_min_var_os_port_perf, label='Min-Var Plugin', color='red', lw=3)
ax.plot(s_min_var_os_lo_port_perf, label='Min-Var Long-Only', color='orange', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('output'), 'Project1', 'P1_Q1.6_min_var_os_ports_perfs.png'))
plt.close()
'''

'''
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

'''


'''
port_1 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0, b_cost=False)

port_2 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0, b_cost=False)

port_3 = Portfolio(dic_data=dic_data, sig_long='ZS_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0, b_cost=False)


zzz = port_1.tab_port_chars(output_perf=False).T


list_port = [port_1, port_2, port_3]
'''

'''
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=0, spr_bps=50, b_cost=True)
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)

test = dic_data['df_facs_data']
'''


'''    
# Turnover (after rebalancing)
if ls_reb_dates[i] != ls_dates[0]:  # No turnover at initial allocation
    df_port_perf.loc[pos_tmp, 'L_TO'] = get_turnover(df_port_perf, pos_tmp, leg='L')
    df_port_perf.loc[pos_tmp, 'S_TO'] = get_turnover(df_port_perf, pos_tmp, leg='S')
'''

'''
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_VAL_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5)
df_port_perf = port.tab_port_perf()

dic_asts_data = dic_data['dic_asts_data']
ls_dates = list(dic_asts_data.keys())
df_tmp = dic_asts_data[ls_dates[-1]]
'''

'''
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=300,
                 sig_short='ZS_VAL_QLT', n_asts_short=20, w_meth_short='EW', pct_short=200,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=0)
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)
'''

'''
def get_df_sec_avg_counts(dic_data):
    dic_asts_data = dic_data['dic_asts_data']
    ls_dates = list(dic_asts_data.keys())
    dic_GICS = {bytes('10', 'utf-8'): 'Energy', bytes('15', 'utf-8'): 'Materials', bytes('20', 'utf-8'): 'Industrials',
                bytes('25', 'utf-8'): 'Consumer Discretionary', bytes('30', 'utf-8'): 'Consumer Stables', bytes('35', 'utf-8'): 'Health Care',
                bytes('40', 'utf-8'): 'Financials', bytes('45', 'utf-8'): 'Information Technology', bytes('50', 'utf-8'): 'Communication Services',
                bytes('55', 'utf-8'): 'Utilities', bytes('60', 'utf-8'): 'Real Estate'}

    ls_dfs = []
    for i in range(len(ls_dates)):
        s_tmp_1 = pd.Series([np.nan for i in range(len(list(dic_GICS.keys())))], index=sorted(list(dic_GICS.keys())))
        s_tmp_2 = dic_asts_data[ls_dates[i]]['GSECTOR'].value_counts().rename(None)
        for sec in s_tmp_2.index.tolist():
            s_tmp_1[sec] = s_tmp_2[sec]
            s_tmp_1 = s_tmp_1.rename(ls_dates[i])
        ls_dfs += [pd.DataFrame(s_tmp_1).transpose()]

    df_sec_counts = pd.concat(ls_dfs, axis=0).fillna(0)
    df_sec_counts = df_sec_counts.reset_index(drop=False, names=['DATE'])
    df_sec_counts['YEAR'] = df_sec_counts['DATE'].dt.year.astype(float)
    df_sec_avg_counts = df_sec_counts.groupby('YEAR')[list(dic_GICS.keys())].mean()
    df_sec_avg_counts = df_sec_avg_counts.rename(columns=dic_GICS)
    return df_sec_avg_counts
'''

'''
for i in range(len(df_port_perf)):
    if i == 0:
        df_port_perf.loc[i, ['L_NAV']] = 100
        df_port_perf.loc[i, ['S_NAV']] = 100
    else:
        df_port_perf.loc[i, ['L_NAV']] = np.array(df_port_perf.loc[i - 1, ['L_NAV']])[0] * (1 + np.array(df_port_perf.loc[i, ['L_RTNS']])[0])
        df_port_perf.loc[i, ['S_NAV']] = np.array(df_port_perf.loc[i - 1, ['S_NAV']])[0] * (1 + np.array(df_port_perf.loc[i, ['S_RTNS']])[0])

df_tpm = df_port_perf.set_index('DATE')

# Plot portfolio performances
sns.set(context='paper', style='ticks', font_scale=1.0)
fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
#ax.set_title('Portfolios Performances', size=28)
ax.axhline(y=100, color='black', ls='--', lw=1)
ax.plot(df_tpm['PORT_NAV'],
        label='PORT_NAV' + ' (L = ' + str(port.pct_long) + ', S = ' + str(port.pct_short) + ', C = ' + str(100 - (port.pct_long - port.pct_short)) + ')',
        color='red', lw=3)
ax.plot(df_tpm['L_NAV'], label='L_NAV' + ' (' + str(port.sig_long) + ', ' + str(port.n_asts_long) + ', ' + str(port.w_meth_long) + ', ' + str(port.ind_const) + ', ' + str(port.reb_freq) + ')', color='green', lw=3)
ax.plot(df_tpm['S_NAV'], label='S_NAV' + ' (' + str(port.sig_short) + ', ' + str(port.n_asts_short) + ', ' + str(port.w_meth_short) + ', ' + str(port.ind_const) + ', ' + str(port.reb_freq) + ')', color='blue', lw=3)
ax.tick_params(axis='both', labelsize=18)
ax.legend(loc='upper left', fontsize=16)
fig.tight_layout()
plt.show()
fig.savefig(Path.joinpath(paths.get('figures'), 'port_perfs_long_vs_short' + port.port_name + '.png'))
plt.close()
'''

'''
annotations = []
for permno in ls_permnos:
    annotation = dict(x=df_zscores.loc[df_zscores['PERMNO'] == permno, ls_zscores[0]].values[0],
                      y=df_zscores.loc[df_zscores['PERMNO'] == permno, ls_zscores[1]].values[0],
                      xref='x', yref='y',
                      text=df_zscores.loc[df_zscores['PERMNO'] == permno, 'CONM'].values[0].decode('utf-8'),
                      showarrow=True, arrowhead=7, ax=0, ay=-40)
    annotations.append(annotation)
'''

'''
# 1) 120/50
i = 3
j = 6
ls_keys = ls_keys[i:j]
ls_values = ls_values[i:j]
dic_selected_ports = dict(zip(ls_keys, ls_values))

list_port = []
for i in range(len(ls_keys)):
    s_tmp = df_ports_chars.iloc[dic_selected_ports[ls_keys[i]]]
    port = Portfolio(dic_data=dic_data, sig_long=dic_sigs[s_tmp['L_SIG']], n_asts_long=s_tmp['L_N_ASTS'], w_meth_long=s_tmp['L_W_METH'], pct_long=s_tmp['L_PCT'],
                     sig_short=dic_sigs[s_tmp['S_SIG']], n_asts_short=s_tmp['S_N_ASTS'], w_meth_short=s_tmp['S_W_METH'], pct_short=s_tmp['S_PCT'],
                     ind_const=s_tmp['IND_CONST'], reb_freq=s_tmp['REB_FREQ'], tc_bps=20)
    list_port.append(port)
    print(port.port_name)

df_ports_stats = tab_port_stats(list_port,'port_stats_1_120_50')

# 1) 300/200
i = 6
j = 9
ls_keys = ls_keys[i:j]
ls_values = ls_values[i:j]
dic_selected_ports = dict(zip(ls_keys, ls_values))

list_port = []
for i in range(len(ls_keys)):
    s_tmp = df_ports_chars.iloc[dic_selected_ports[ls_keys[i]]]
    port = Portfolio(dic_data=dic_data, sig_long=dic_sigs[s_tmp['L_SIG']], n_asts_long=s_tmp['L_N_ASTS'], w_meth_long=s_tmp['L_W_METH'], pct_long=s_tmp['L_PCT'],
                     sig_short=dic_sigs[s_tmp['S_SIG']], n_asts_short=s_tmp['S_N_ASTS'], w_meth_short=s_tmp['S_W_METH'], pct_short=s_tmp['S_PCT'],
                     ind_const=s_tmp['IND_CONST'], reb_freq=s_tmp['REB_FREQ'], tc_bps=20)
    list_port.append(port)
    print(port.port_name)

df_ports_stats = tab_port_stats(list_port,'port_stats_1_300_200')
'''

'''
port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=0, spr_bps=50, b_cost=True)
df_port_perf = port.tab_port_perf()
df_port_chars = port.tab_port_chars(output_perf=False)

test = dic_data['df_facs_data']
'''

'''
port_1 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0, b_cost=False)

port_2 = Portfolio(dic_data=dic_data, sig_long='ZS_VAL', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0, b_cost=False)

port_3 = Portfolio(dic_data=dic_data, sig_long='ZS_QLT', n_asts_long=25, w_meth_long='EW', pct_long=150,
                 sig_short='ZS_VAL_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                 ind_const='I', reb_freq='Y', min_short_me=1000, max_short_cl=0.5,tc_bps=20, spr_bps=0, b_cost=False)


zzz = port_1.tab_port_chars(output_perf=False).T
list_port = [port_1, port_2, port_3]
'''

'''
# Export ports navs
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['VAL_1', 'QLT_1', 'VQ_1'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_1')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['VAL_2', 'QLT_2', 'VQ_2'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_2')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['VAL_3', 'QLT_3', 'VQ_3'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_3')

fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_11', 'VQAM_1'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_4')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_12', 'VQAM_2'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_5')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_13', 'VQAM_3'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_6')

fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_21', 'BEST_G1'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_7')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_22', 'BEST_G2'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_8')
fn.tab_ports_feats({key: dic_selected_ports[key] for key in ['BEST_23', 'BEST_G3'] if key in dic_selected_ports},
                   ls_feats=['PORT_NAV'], file_name='df_ports_navs_9')

# Export ports stats
ls_stats = ['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'MAX_DD_PRD', 'AVG_TO',
            'ANN_ALPHA', 't_ALPHA', 'B_MKTRF', 't_MKTRF', 'B_SMB', 't_SMB', 'B_HML', 't_HML', 'R_SQUARED']
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['VAL_1', 'QLT_1', 'VQ_1'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_1')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['VAL_2', 'QLT_2', 'VQ_2'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_2')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['VAL_3', 'QLT_3', 'VQ_3'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_3')

fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_11', 'VQAM_1'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_4')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_12', 'VQAM_2'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_5')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_13', 'VQAM_3'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_6')

fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_21', 'BEST_G1'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_7')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_22', 'BEST_G2'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_8')
fn.tab_ports_stats({key: dic_selected_ports[key] for key in ['BEST_23', 'BEST_G3'] if key in dic_selected_ports},
                   ls_stats=ls_stats, file_name='df_ports_stats_9')
'''

'''
def tab_perf_export(list_port,file_name):
    dic_ports_stats = {}
    j = 1
    for i in list_port:
        df_port_perf = i.tab_port_perf().set_index('DATE')['PORT_NAV']
        dic_ports_stats[str(j) + '_' + i.port_name] = df_port_perf
        j += 1
    df_ports_perf = pd.concat(dic_ports_stats, axis=1)
    df_ports_perf.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format(file_name)))
    return df_ports_perf
'''

'''
# Portfolios stats
def tab_port_stats(list_port,file_name):
    dic_ports_stats = {}
    j = 1
    for i in list_port:
        df_port_chars = i.tab_port_chars(output_perf=False)
        df_port_stats = df_port_chars[['ANN_MEAN', 'ANN_VOL', 'SHARPE', 'MAX_DD', 'MAX_DD_PRD', 'AVG_TO',
                                       'ANN_ALPHA', 't_ALPHA', 'B_MKTRF', 't_MKTRF', 'B_SMB', 't_SMB', 'B_HML', 't_HML', 'B_UMD', 't_UMD', 'R_SQUARED',
                                       'L_SIG', 'L_N_ASTS', 'L_W_METH', 'L_PCT', 'S_SIG', 'S_N_ASTS', 'S_W_METH', 'S_PCT', 'IND_CONST', 'REB_FREQ', 'PORT_NAV_T']]
        dic_ports_stats[str(j) + '_' + i.port_name] = df_port_stats
        j += 1
    df_ports_stats = pd.concat(dic_ports_stats, axis=0).droplevel(1, axis=0)
    df_ports_stats.to_excel(Path.joinpath(paths.get('tables'), '{}.xlsx'.format(file_name)))

    return df_ports_stats
'''

'''
# *** Transaction cost analysis ***
#df_data.loc[df_data['TIC'] == bytes('BRK.B', 'utf-8')]
#df_stock = df_data.loc[df_data['PERMNO'] == 17778]
'''

'''
port = Portfolio(dic_data=dic_data, sig_long='ZS_QLT', n_asts_long=20, w_meth_long='EW', pct_long=120,
                         sig_short='ZS_QLT', n_asts_short=15, w_meth_short='EW', pct_short=50,
                         ind_const='I', reb_freq='M', min_short_me=1000, max_short_cl=0.5, tc_bps=20, spr_bps=0)

#VQ_20.0_EW_120.0_VQ_15.0_EW_50.0_I_M

yyy =  port.tab_port_perf()
zzz = port.tab_port_chars()
'''

