# Import packages
from datetime import datetime
from operator import attrgetter
from pathlib import Path
from scipy.optimize import minimize
from scripts.functions import paths
from tqdm import tqdm
import numpy as np
import pandas as pd
import pickle
import scripts.functions as fn
import warnings

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

# # Checkpoint data
# df_fundamentals_quarterly.to_pickle(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'))
# df_security_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'))
# df_stock_monthly.to_pickle(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_fundamentals_quarterly.pkl'), 'rb') as f:
    df_fundamentals_quarterly = pickle.load(f)
with open(Path.joinpath(paths.get('data'), 'df_security_monthly.pkl'), 'rb') as f:
    df_security_monthly = pickle.load(f)
with open(Path.joinpath(paths.get('data'), 'df_stock_monthly.pkl'), 'rb') as f:
    df_stock_monthly = pickle.load(f)

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

# Checkpoint data
# df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data_1.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data_1.pkl'), 'rb') as f:
    df_data = pickle.load(f)

# ATTENTION: accounting data published in Q_t is available (out-of-sample) for investment decisions in Q_t_1
# Push forward fundamentals (out-of-sample)
df_data = fn.preprocessing_6(df_data)

# Create additional variables (fundamental metrics)
df_data = fn.preprocessing_7(df_data)

# Checkpoint data
# df_data.to_pickle(Path.joinpath(paths.get('data'), 'df_data_2.pkl'))
with open(Path.joinpath(paths.get('data'), 'df_data_2.pkl'), 'rb') as f:
    df_data = pickle.load(f)


# %%
# **************************************************
# *** Branch: PORTFOLIO CONSTRUCTION             ***
# **************************************************

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

# Create data dictionary
dic_data = {}
ls_dates = sorted(df_data['DATE'].unique().tolist())

for date in tqdm(ls_dates, desc='Data dictionary'):
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
    dic_data[date] = df_tmp




# TODO: save data dictionary as json
# %%


class Portfolio:
    def __init__(self, dic_data, sig_long, n_asts_long, w_meth_long,
                 sig_short, n_asts_short, w_meth_short, ind_const, reb_freq, min_short_me, max_short_cl):
        self.dic_data = dic_data
        self.sig_long = sig_long
        self.n_asts_long = n_asts_long
        self.w_meth_long = w_meth_long
        self.sig_short = sig_short
        self.n_asts_short = n_asts_short
        self.w_meth_short = w_meth_short
        self.ind_const = ind_const
        self.reb_freq = reb_freq
        self.min_short_me = min_short_me
        self.max_short_cl = max_short_cl

        self.dic_sigs = {'ZS_VAL': 'VAL', 'ZS_QLT': 'QLT', 'ZS_MOM_1': 'MOM1', 'ZS_MOM_2': 'MOM2', 'ZS_RMOM_1': 'RMOM',
                         'ZS_VAL_QLT': 'VQ', 'ZS_VAL_QLT_MOM_1': 'VQM1', 'ZS_VAL_QLT_MOM_2': 'VQM2', 'ZS_VAL_QLT_RMOM': 'VQRM', 'ZS_VAL_QLT_ARMOM': 'VQARM'}
        self.port_name = '_'.join([self.dic_sigs[sig_long], str(int(n_asts_long)), w_meth_long,
                                   self.dic_sigs[sig_short], str(int(n_asts_short)), w_meth_short,
                                   ind_const, str(int(min_short_me)), str(int(max_short_cl * 100)), reb_freq])

    def get_ls_asts(self, df_data, leg):
        # Min market cap to avoid short small caps
        # Max cumulative loss to avoid short if already big loss

        ls_asts = []
        ls_secs = df_data['GSECTOR'].unique().tolist()

        if self.ind_const == 'I':
            dic_asts = {}
            for sec in ls_secs:
                df_tmp = df_data.loc[df_data['GSECTOR'] == sec, ['PERMNO', 'ME', 'CTRT1M_1', self.sig_long, self.sig_short]]
                if leg == 'L':
                    df_tmp = df_tmp.sort_values(by=[self.sig_long], ascending=False)
                    dic_asts[sec] = df_tmp['PERMNO'].tolist()
                elif leg == 'S':
                    df_tmp = df_tmp.sort_values(by=[self.sig_short], ascending=True)
                    df_tmp = df_tmp[(df_tmp['ME'] >= self.min_short_me) & (df_tmp['CTRT1M_1'] >= -self.max_short_cl)]
                    dic_asts[sec] = df_tmp['PERMNO'].tolist()
                if len(dic_asts[sec]) < np.ceil((max(self.n_asts_long, self.n_asts_short) * 2) / len(ls_secs)):  # Remove too small sectors
                    del dic_asts[sec]
            dic_asts = dict(sorted(dic_asts.items(), key=lambda x: len(x[1]), reverse=True))  # Sort by sector size

            ls_secs = list(dic_asts.keys())
            if leg == 'L':
                i = 0
                while len(ls_asts) < self.n_asts_long:
                    s = 0
                    while (len(ls_asts) < self.n_asts_long) and (s < len(ls_secs)):
                        ls_asts += [dic_asts[ls_secs[s]][i]]
                        s += 1
                    i += 1
            elif leg == 'S':
                i = 0
                while len(ls_asts) < self.n_asts_short:
                    s = 0
                    while (len(ls_asts) < self.n_asts_short) and (s < len(ls_secs)):
                        ls_asts += [dic_asts[ls_secs[s]][i]]
                        s += 1
                    i += 1

        elif self.ind_const == 'NI':
            df_tmp = df_data[['PERMNO', 'ME', 'CTRT1M_1', self.sig_long, self.sig_short]]
            if leg == 'L':
                ls_asts = df_tmp.loc[df_tmp[self.sig_long].nlargest(self.n_asts_long).index, 'PERMNO'].tolist()
            elif leg == 'S':
                df_tmp = df_tmp[(df_tmp['ME'] >= self.min_short_me) & (df_tmp['CTRT1M_1'] >= -self.max_short_cl)]
                ls_asts = df_tmp.loc[df_tmp[self.sig_short].nsmallest(self.n_asts_short).index, 'PERMNO'].tolist()

        ls_asts = sorted(ls_asts)  # Sort PERMNO
        return ls_asts

    def get_s_port_w(self, df_data, leg, w_meth):
        s_port_w = pd.Series(dtype='float64')
        ls_asts = self.get_ls_asts(df_data, leg)
        n_asts = len(ls_asts)

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
            df_rtns = pd.DataFrame(df_data.loc[df_data['PERMNO'].isin(ls_asts), 'LS_PTRT1M'].tolist()).T  # Previous returns
            df_rtns.columns = ls_asts
            df_covmat = df_rtns.cov()
            a_covmat = np.array(df_covmat * 12)  # Annualized from monthly data

            # Useful functions
            def get_port_var(w):
                return w.T @ a_covmat @ w

            def cons1(w):
                return np.sum(w) - 1

            # Optimization
            x0 = np.ones(n_asts) / n_asts
            bnds = [(0.005, 1) for i in range(n_asts)]  # Long-only, min 0.5% per asset
            cons = {'type': 'eq', 'fun': cons1}
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore', category=RuntimeWarning)
                result = minimize(fun=get_port_var, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

            # Return output
            if not result.success:  # Assumption: if optimization unsuccessful, use equal weighting (at this date)
                s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')
            else:
                s_port_w = pd.Series(result.x, index=ls_asts, dtype='float64')

        # Market neutral (zero beta)
        elif w_meth == 'MN':
            # Initialization
            s_betas = df_data.loc[df_data['PERMNO'].isin(ls_asts), 'BETA'].rename(None)
            a_betas = np.array(s_betas)

            # Useful functions
            def get_port_beta(w):
                return w.T @ a_betas

            def obj_fun(w):
                diff = (get_port_beta(w) - 1) ** 2
                return diff  # Minimize to have Beta_P = 1 (Beta_L - Beta_S = 1 - 1 = 0)

            def cons1(w):
                return np.sum(w) - 1

            # Optimization
            x0 = np.ones(n_asts) / n_asts
            bnds = [(0.005, 1) for i in range(n_asts)]  # Long-only, min 0.5% per asset
            cons = {'type': 'eq', 'fun': cons1}
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore', category=RuntimeWarning)
                result = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

            # Return output
            if not result.success:
                s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')
            else:
                s_port_w = pd.Series(result.x, index=ls_asts, dtype='float64')

        # Risk parity (equally-weighted risk contributions)
        elif w_meth == 'RP':
            # Initialization
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

            def cons1(w):
                return np.sum(w) - 1

            # Optimization
            x0 = np.ones(n_asts) / n_asts
            bnds = [(0.005, 1) for i in range(n_asts)]  # Long-only, min 0.5% per asset
            cons = {'type': 'eq', 'fun': cons1}
            with warnings.catch_warnings():
                warnings.filterwarnings(action='ignore', category=RuntimeWarning)
                result = minimize(fun=obj_fun, x0=x0, method='SLSQP', bounds=bnds, constraints=cons, tol=1e-12, options={'maxiter': 1000})

            # Return output
            if not result.success:
                s_port_w = pd.Series((1 / n_asts), index=ls_asts, dtype='float64')
            else:
                s_port_w = pd.Series(result.x, index=ls_asts, dtype='float64')
        return s_port_w

    def tab_port_perf(self):
        dic_cols = {'DATE': 'datetime64[ns]', 'PORT_VAL': 'float64', 'PORT_L': 'float64', 'PORT_S': 'float64', 'PORT_RTN': 'float64',
                    'L_VAL': 'float64', 'L_RTN': 'float64', 'LS_L_ASTS': 'object', 'LS_L_W': 'object', 'LS_L_POS': 'object', 'LS_L_RTNS': 'object',
                    'S_VAL': 'float64', 'S_RTN': 'float64', 'LS_S_ASTS': 'object', 'LS_S_W': 'object', 'LS_S_POS': 'object', 'LS_S_RTNS': 'object'}
        df_port_perf = pd.DataFrame(columns=list(dic_cols.keys())).astype(dtype=dic_cols)
        ls_dates = list(self.dic_data.keys())

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
        df_port_perf.loc[0, ['PORT_VAL', 'L_VAL', 'S_VAL']] = 100

        # Iteration over rebalancing dates
        for i in tqdm(range(len(ls_reb_dates)), desc=self.port_name):
            # Data at rebalancing date
            df_tmp = self.dic_data[ls_reb_dates[i]]
            pos_tmp = (n_dates * i)

            # Long leg
            s_long_w = self.get_s_port_w(df_tmp, leg='L', w_meth=self.w_meth_long)
            ls_long_asts = s_long_w.index.tolist()
            df_port_perf.at[pos_tmp, 'LS_L_W'] = s_long_w.tolist()
            df_port_perf.at[pos_tmp, 'LS_L_POS'] = (s_long_w * df_port_perf.loc[pos_tmp, 'L_VAL']).tolist()
            df_long_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_long_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
            df_long_rtns.columns = ls_long_asts

            # Short leg
            s_short_w = self.get_s_port_w(df_tmp, leg='S', w_meth=self.w_meth_short)
            ls_short_asts = s_short_w.index.tolist()
            df_port_perf.at[pos_tmp, 'LS_S_W'] = s_short_w.tolist()
            df_port_perf.at[pos_tmp, 'LS_S_POS'] = (s_short_w * df_port_perf.loc[pos_tmp, 'S_VAL']).tolist()
            df_short_rtns = pd.DataFrame(df_tmp.loc[df_tmp['PERMNO'].isin(ls_short_asts), 'LS_NTRT1M'].tolist()).T  # Next returns
            df_short_rtns.columns = ls_short_asts

            # Carry forward position in rebalancing period
            for j in range(1, (n_dates + 1)):
                pos_tmp = (n_dates * i) + j
                df_port_perf.loc[pos_tmp, 'DATE'] = ls_dates[pos_tmp]

                # Long leg
                df_port_perf.at[pos_tmp, 'LS_L_ASTS'] = ls_long_asts
                a_long_rtns = np.array(df_long_rtns.loc[j - 1])
                df_port_perf.at[pos_tmp, 'LS_L_RTNS'] = a_long_rtns.tolist()
                df_port_perf.loc[pos_tmp, 'L_RTN'] = (np.array(df_port_perf.loc[(pos_tmp - 1), 'LS_L_W']) * a_long_rtns).sum()
                df_port_perf.at[pos_tmp, 'LS_L_POS'] = (np.array(df_port_perf.loc[(pos_tmp - 1), 'LS_L_POS']) * (1 + a_long_rtns)).tolist()
                df_port_perf.loc[pos_tmp, 'L_VAL'] = np.array(df_port_perf.loc[pos_tmp, 'LS_L_POS']).sum()
                df_port_perf.at[pos_tmp, 'LS_L_W'] = (np.array(df_port_perf.at[pos_tmp, 'LS_L_POS']) / df_port_perf.loc[pos_tmp, 'L_VAL']).tolist()

                # Short leg
                df_port_perf.at[pos_tmp, 'LS_S_ASTS'] = ls_short_asts
                a_short_rtns = (1) * np.array(df_short_rtns.loc[j - 1])  # Take the negative (short position, approx.)
                df_port_perf.at[pos_tmp, 'LS_S_RTNS'] = a_short_rtns.tolist()
                df_port_perf.loc[pos_tmp, 'S_RTN'] = (np.array(df_port_perf.loc[(pos_tmp - 1), 'LS_S_W']) * a_short_rtns).sum()
                df_port_perf.at[pos_tmp, 'LS_S_POS'] = (np.array(df_port_perf.loc[(pos_tmp - 1), 'LS_S_POS']) * (1 + a_short_rtns)).tolist()
                df_port_perf.loc[pos_tmp, 'S_VAL'] = np.array(df_port_perf.loc[pos_tmp, 'LS_S_POS']).sum()
                df_port_perf.at[pos_tmp, 'LS_S_W'] = (np.array(df_port_perf.at[pos_tmp, 'LS_S_POS']) / df_port_perf.loc[pos_tmp, 'S_VAL']).tolist()

                # Portfolio (L/S)
                # TODO: redo with L/S rebalancing, include long bias ==> 130/30
                df_port_perf.loc[pos_tmp, 'PORT_RTN'] = (df_port_perf.loc[pos_tmp, 'L_RTN'] - df_port_perf.loc[pos_tmp, 'S_RTN']) / 2
                df_port_perf.loc[pos_tmp, 'PORT_VAL'] = df_port_perf.loc[(pos_tmp - 1), 'PORT_VAL'] * (1 + df_port_perf.loc[pos_tmp, 'PORT_RTN'])
        return df_port_perf

    # TODO: get_port_chars





port = Portfolio(dic_data=dic_data, sig_long='ZS_VAL', n_asts_long=25, w_meth_long='EW',
                 sig_short='ZS_QLT', n_asts_short=10, w_meth_short='EW', ind_const='I', min_short_me=1000, max_short_cl=0.4, reb_freq='Q')

zzz = port.tab_port_perf()
port.port_name





# %%

ls_lens = [len(dic_data[date]) for date in list(dic_data.keys())]
df_tmp = dic_data[ls_dates[0]]
ls_asts = get_ls_asts(df_tmp, indicator='ZS_VAL', n_asts=25, ind_const='NI', leg='S')
zzz = df_tmp[df_tmp['PERMNO'].isin(ls_asts)]


# df_VAL_25_I_EW_Q_L
# Weighting: EW, VW, MV, RP, MN
# Ind_const: True, False
# Indicator (ZS): VAL, QLT, VAL_QLT, VAL_QLT_MOM
# Rebalancing: quarterly (Q), yearly (Y)
# Performance: Mean, Vol, SR, MaxDD, FF5 (alpha, betas), Calamar, Turnover, Normalized Hierfindahl Index or Gini



