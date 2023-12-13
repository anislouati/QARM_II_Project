# Import packages
# from scripts.functions import Portfolio
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from scipy.optimize import minimize, OptimizeResult
from scripts.functions import paths
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle
import scripts.functions as fn
import statsmodels.api as sm
import warnings

# Project settings
pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 10)

# Warnings management
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings(action='ignore', category=RuntimeWarning)


# %%
# **************************************************
# *** Branch: DATA MANAGEMENT                    ***
# **************************************************

# Import raw data
df_fundamentals_quarterly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_fundamentals_quarterly.sas7bdat'))
df_security_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_compustat_merged_security_monthly.sas7bdat'))
df_stock_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'crsp_security_files_monthly_stock.sas7bdat'))
df_factors_monthly = pd.read_sas(Path.joinpath(paths.get('data'), 'factors_monthly.sas7bdat'))

# Filter selected cols
ls_selected_cols_1 = ['LPERMNO', 'DATADATE',
                      'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC',
                      'ATQ', 'COGSQ', 'CSHOQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ',
                      'REVTQ', 'WCAPQ', 'XINTQ', 'CAPXY']
df_fundamentals_quarterly = df_fundamentals_quarterly[ls_selected_cols_1]
df_fundamentals_quarterly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_2 = ['LPERMNO', 'DATADATE', 'PRCCM', 'TRT1M']
df_security_monthly = df_security_monthly[ls_selected_cols_2]
df_security_monthly.rename(columns={'LPERMNO': 'PERMNO', 'DATADATE': 'DATE'}, inplace=True)

ls_selected_cols_3 = ['PERMNO', 'DATE', 'BID', 'ASK', 'VOL', 'SPRTRN']
df_stock_monthly = df_stock_monthly[ls_selected_cols_3]

ls_selected_cols_4 = ['DATEFF', 'RF', 'MKTRF', 'SMB', 'HML']
df_factors_monthly = df_factors_monthly[ls_selected_cols_4]

# Create keys/identifiers (KEYQ, KEYM)
df_fundamentals_quarterly = fn.preprocessing_1(df_fundamentals_quarterly)
df_security_monthly = fn.preprocessing_1(df_security_monthly)
df_stock_monthly = fn.preprocessing_1(df_stock_monthly)

# Filter raw dates (min_year-max_year)
min_year = 1980
max_year = 2022
df_fundamentals_quarterly = df_fundamentals_quarterly[(df_fundamentals_quarterly['YEAR'] >= min_year) & (df_fundamentals_quarterly['YEAR'] <= max_year)]
df_security_monthly = df_security_monthly[(df_security_monthly['YEAR'] >= min_year) & (df_security_monthly['YEAR'] <= max_year)]
df_stock_monthly = df_stock_monthly[(df_stock_monthly['YEAR'] >= min_year) & (df_stock_monthly['YEAR'] <= max_year)]

# Filter stock exchanges (11: NYSE, 12: AMEX, 14: NASDAQ-NMS)
df_fundamentals_quarterly = df_fundamentals_quarterly[df_fundamentals_quarterly['EXCHG'].isin([11, 12, 14])]
ls_permnos = df_fundamentals_quarterly['PERMNO'].unique().tolist()
df_security_monthly = df_security_monthly[df_security_monthly['PERMNO'].isin(ls_permnos)]
df_stock_monthly = df_stock_monthly[df_stock_monthly['PERMNO'].isin(ls_permnos)]

# Sort data and reset index
df_fundamentals_quarterly = df_fundamentals_quarterly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
df_security_monthly = df_security_monthly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
df_stock_monthly = df_stock_monthly.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Drop faulty FQTR and duplicates
df_fundamentals_quarterly = fn.preprocessing_2(df_fundamentals_quarterly)
df_security_monthly = fn.preprocessing_3(df_security_monthly)
df_stock_monthly = fn.preprocessing_3(df_stock_monthly)

# Save data (uncomment)
# with open(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'), 'wb') as file:
#     pickle.dump(df_fundamentals_quarterly, file)
# with open(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'), 'wb') as file:
#     pickle.dump(df_security_monthly, file)
# with open(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'), 'wb') as file:
#     pickle.dump(df_stock_monthly, file)
# Load data
with open(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'), 'rb') as file:
    df_fundamentals_quarterly = pickle.load(file)
with open(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'), 'rb') as file:
    df_security_monthly = pickle.load(file)
with open(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'), 'rb') as file:
    df_stock_monthly = pickle.load(file)

# Merge datasets
df_fundamentals_quarterly = df_fundamentals_quarterly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYM'])
df_tmp = pd.merge(df_fundamentals_quarterly, df_security_monthly, on='KEYQ', how='inner')

df_stock_monthly = df_stock_monthly.drop(columns=['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ'])
df_data = pd.merge(df_stock_monthly, df_tmp, on='KEYM', how='inner')

# Fill missing dates with nans (by stock)
df_data = fn.preprocessing_4(df_data)
ls_selected_cols = ['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED',
                    'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC',
                    'ATQ', 'COGSQ', 'CSHOQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ',
                    'REVTQ', 'WCAPQ', 'XINTQ', 'CAPXY',
                    'PRCCM', 'TRT1M', 'BID', 'ASK', 'VOL', 'SPRTRN']
df_data = df_data[ls_selected_cols]
df_data = df_data.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# Check filled data (by stock)
delta_months = (df_data.groupby('PERMNO')['DATE'].max().dt.to_period('M') - df_data.groupby('PERMNO')['DATE'].min().dt.to_period('M')).apply(attrgetter('n')) + 1
months_count = df_data.groupby('PERMNO')['DATE'].count()
pd_delta_months = pd.DataFrame()
pd_delta_months['Number of months'] = delta_months
pd_delta_months['Count of months'] = months_count
pd_delta_months['Check'] = delta_months - months_count
s_tmp = pd_delta_months['Check'].value_counts()
print('Assets in dataset: {}'.format(len(df_data['PERMNO'].unique().tolist())))
print('Assets with filled data: {}'.format(s_tmp[0]))

# Create/Modify variables
df_data = fn.preprocessing_5(df_data)
ls_selected_cols = ['PERMNO', 'DATE', 'YEAR', 'QTR', 'MTH', 'KEYQ', 'KEYM', 'FILLED',
                    'FQTR', 'CONM', 'TIC', 'EXCHG', 'GSECTOR', 'LOC',
                    'ATQ', 'COGSQ', 'CSHOQ', 'DLCQ', 'DLTTQ', 'DPQ', 'LTQ', 'NIQ', 'PIQ', 'REQ',
                    'REVTQ', 'WCAPQ', 'WCAPCHQ', 'XINTQ', 'CAPXQ', 'PRCCQ',
                    'PRCCM', 'TRT1M', 'BID', 'ASK', 'SPRDPCT', 'VOL', 'DVOL', 'SPRTRN']
df_data = df_data[ls_selected_cols]
df_data = df_data.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)

# ATTENTION: accounting data published in Q_t is available (out-of-sample) for investment decisions in Q_t_1
# Push forward fundamentals (out-of-sample)
df_data = fn.preprocessing_6(df_data)

# Create additional variables (fundamental metrics)
df_data = fn.preprocessing_7(df_data)

# Filter clean dates (31/12/min_year-31/12/max_year)
min_year = 1994
max_year = 2022
df_data = df_data[(df_data['DATE'] >= datetime(min_year, 12, 31)) &
                  (df_data['DATE'] <= datetime(max_year, 12, 31))]

# Filter out excluded sectors (40: Financials)
'''
n_asts_1 = len(df_data['PERMNO'].unique().tolist())
df_data = df_data[df_data['GSECTOR'] != bytes('40', 'utf-8')]
n_asts_2 = len(df_data['PERMNO'].unique().tolist())
print('Assets before filter: {}'.format(n_asts_1))
print('Assets after filter: {}'.format(n_asts_2))
'''

# Sync dates (EOM) for factors data
ls_dates = sorted(df_data['DATE'].unique().tolist())
ls_year_mth = [(str(date.year) + '_' + str(date.month)) for date in ls_dates]
dic_dates = dict(zip(ls_year_mth, ls_dates))
for i in range(len(df_factors_monthly)):
    date = df_factors_monthly.loc[i, 'DATEFF']
    year_mth = str(date.year) + '_' + str(date.month)
    if year_mth in list(dic_dates.keys()):
        df_factors_monthly.loc[i, 'DATE_NEW'] = dic_dates[year_mth]
df_factors_monthly = df_factors_monthly[~pd.isnull(df_factors_monthly['DATE_NEW'])].drop(columns=['DATEFF'])
ls_selected_cols = ['DATE_NEW', 'RF', 'MKTRF', 'SMB', 'HML']
df_factors_monthly = df_factors_monthly[ls_selected_cols]
df_factors_monthly.rename(columns={'DATE_NEW': 'DATE'}, inplace=True)
df_factors_monthly = df_factors_monthly.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

# Save data (uncomment)
# with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'wb') as file:
#     pickle.dump(df_data, file)
# with open(Path.joinpath(paths.get('data'), 'df_factors_monthly.pkl'), 'wb') as file:
#     pickle.dump(df_factors_monthly, file)
# Load data
with open(Path.joinpath(paths.get('data'), 'df_data.pkl'), 'rb') as file:
    df_data = pickle.load(file)
with open(Path.joinpath(paths.get('data'), 'df_factors_monthly.pkl'), 'rb') as file:
    df_factors_monthly = pickle.load(file)

# Create data dictionary
dic_asts_data = {}
ls_dates = sorted(df_data['DATE'].unique().tolist())
for date in tqdm(ls_dates, desc='Assets data dictionary'):
    df_tmp = df_data[df_data['DATE'] == date]
    df_tmp = df_tmp.dropna(how='any')  # Remark: we drop all rows with at least one nan (by date)

    min_dvol = 25  # Minimum dollar volume (mil., monthly)
    min_me = 250  # Minimum market cap (mil.)
    df_tmp = df_tmp[(df_tmp['DVOL'] >= min_dvol) & (df_tmp['ME'] >= min_me)]
    df_tmp = fn.get_ZS(df_tmp)

    ls_selected_cols = ['PERMNO', 'DATE', 'CONM', 'TIC', 'EXCHG', 'GSECTOR',
                        'PRCCM', 'TRT1M', 'SPRDPCT', 'DVOL', 'SPRTRN', 'ME',
                        'VOL_TRT1M', 'VOL_SPRTRN', 'BETA',
                        'CTRT1M_1', 'LS_PTRT1M', 'LS_NTRT1M',
                        'ZS_VAL', 'ZS_QLT', 'ZS_MOM_1', 'ZS_MOM_2', 'ZS_RMOM_1',
                        'ZS_VAL_QLT', 'ZS_VAL_QLT_MOM_1', 'ZS_VAL_QLT_MOM_2', 'ZS_VAL_QLT_RMOM', 'ZS_VAL_QLT_ARMOM']
    df_tmp = df_tmp[ls_selected_cols]
    df_tmp = df_tmp.sort_values(by=['PERMNO', 'DATE'], ascending=[True, True]).reset_index(drop=True)
    dic_asts_data[date] = df_tmp
dic_data = {'dic_asts_data': dic_asts_data, 'df_facs_data': df_factors_monthly}

# Save data (uncomment)
# with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'wb') as file:
#     pickle.dump(dic_data, file)
# Load data
with open(Path.joinpath(paths.get('data'), 'dic_data.pkl'), 'rb') as file:
    dic_data = pickle.load(file)


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
        dic_cols = {'DATE': 'datetime64[ns]', 'PORT_C': 'float64', 'PORT_L': 'float64', 'PORT_S': 'float64', 'PORT_NAV': 'float64', 'PORT_RTNS': 'float64',
                    'L_RTNS': 'float64', 'L_POS': 'object', 'L_WT': 'object', 'L_TO': 'float64', 'L_ASTS_RTNS': 'object',
                    'S_RTNS': 'float64', 'S_POS': 'object', 'S_WT': 'object', 'S_TO': 'float64', 'S_ASTS_RTNS': 'object'}
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
            if ls_reb_dates[i] != ls_dates[0]:  # Initial allocation already done
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

            # Turnover (after rebalancing)
            if ls_reb_dates[i] != ls_dates[0]:  # No turnover at initial allocation
                df_port_perf.loc[pos_tmp, 'L_TO'] = get_turnover(df_port_perf, pos_tmp, leg='L')
                df_port_perf.loc[pos_tmp, 'S_TO'] = get_turnover(df_port_perf, pos_tmp, leg='S')

            # Carry forward position in rebalancing period
            for j in range(1, (n_dates + 1)):
                pos_tmp = (n_dates * i) + j
                df_port_perf.loc[pos_tmp, 'DATE'] = ls_dates[pos_tmp]

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

                # Turnover
                df_port_perf.loc[pos_tmp, 'L_TO'] = get_turnover(df_port_perf, pos_tmp, leg='L')
                df_port_perf.loc[pos_tmp, 'S_TO'] = get_turnover(df_port_perf, pos_tmp, leg='S')

                # Portfolio (L/S)
                df_port_perf.loc[pos_tmp, 'PORT_C'] = df_port_perf.loc[(pos_tmp - 1), 'PORT_C']  # Assumption: no interest on cash (possible to use risk-free rate)
                df_port_perf.loc[pos_tmp, 'PORT_NAV'] = df_port_perf.loc[pos_tmp, 'PORT_C'] + df_port_perf.loc[pos_tmp, 'PORT_L'] - df_port_perf.loc[pos_tmp, 'PORT_S']
                df_port_perf.loc[pos_tmp, 'PORT_RTNS'] = (df_port_perf.loc[pos_tmp, 'PORT_NAV'] / df_port_perf.loc[(pos_tmp - 1), 'PORT_NAV']) - 1
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
            with open(Path.joinpath(paths.get('output'), 'ports', (self.port_name + '.pkl')), 'wb') as file:
                pickle.dump(df_port_perf, file)

        # Merge factors data
        df_port_perf = pd.merge(df_port_perf, self.df_facs_data, on='DATE', how='inner')
        df_port_perf = df_port_perf.sort_values(by=['DATE'], ascending=[True]).reset_index(drop=True)

        # Initialization
        df_port_chars = pd.DataFrame()
        s_port_rtns = pd.Series(df_port_perf.loc[1:, 'PORT_RTNS'].tolist(), index=df_port_perf.loc[1:, 'DATE'].tolist(), dtype='float64').rename(None)
        s_port_losses = (-1) * s_port_rtns
        df_drawdown = get_drawdown(s_port_rtns)
        s_max_drawdown = df_drawdown.iloc[df_drawdown['DD'].idxmin()]
        X = sm.add_constant(df_port_perf.loc[1:, ['MKTRF', 'SMB', 'HML']])
        model = sm.OLS((df_port_perf.loc[1:, 'PORT_RTNS'] - df_port_perf.loc[1:, 'RF']), X).fit()

        # Performance analysis
        df_port_chars.loc[0, 'PORT_NAME'] = self.port_name
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
        df_port_chars.loc[0, 'LEV'] = df_port_perf.iloc[-1]['PORT_S'] / df_port_perf.iloc[-1]['PORT_NAV']
        df_port_chars.loc[0, 'L_AVG_TO'] = df_port_perf.loc[1:, 'L_TO'].mean()
        df_port_chars.loc[0, 'S_AVG_TO'] = df_port_perf.loc[1:, 'S_TO'].mean()
        df_port_chars.loc[0, 'L_NORM_HI'] = get_norm_herfindahl_idx(np.array(list(df_port_perf.iloc[-1]['L_WT'].values())))
        df_port_chars.loc[0, 'S_NORM_HI'] = get_norm_herfindahl_idx(np.array(list(df_port_perf.iloc[-1]['S_WT'].values())))
        return df_port_chars







# TODO: get_port_chars
# TODO: grid search
# Performance: Mean, Vol, SR, MaxDD, FF5 (alpha, betas), Calamar, Turnover, Normalized Hierfindahl Index or Gini

port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL_QLT', n_asts_long=25, w_meth_long='MN', pct_long=130,
                 sig_short='ZS_MOM_2', n_asts_short=25, w_meth_short='MN', pct_short=30,
                 ind_const='NI', reb_freq='Q', min_short_me=1000, max_short_cl=0.4)


df_port_chars = port.tab_port_chars(output_perf=True)





# %%









ls = port.get_ls_asts(df_tmp, leg='L')
df_tmp.loc[df_tmp['PERMNO'].isin(ls), 'GSECTOR'].value_counts()
df_tmp = dic_data[ls_dates[0]]
s_port_w = port.get_s_port_w(df_tmp, leg='L', w_meth='RP')
ls_lens = [len(dic_data[date]) for date in list(dic_data.keys())]
ls_asts = get_ls_asts(df_tmp, indicator='ZS_VAL', n_asts=25, ind_const='NI', leg='S')
zzz = df_tmp[df_tmp['PERMNO'].isin(ls_asts)]








