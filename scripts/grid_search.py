# Import packages
from itertools import product
from multiprocessing import Pool
from pathlib import Path
from scripts.functions import get_df_port_chars
from scripts.functions import paths
from tqdm import tqdm
import pandas as pd
import time
import warnings

# Warnings management
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)
warnings.filterwarnings(action='ignore', category=RuntimeWarning)


# %%

def main():
    ls_sigs_long = ['ZS_VAL', 'ZS_QLT', 'ZS_VAL_QLT', 'ZS_VAL_QLT_AMOM']
    ls_n_asts_long = [20, 25]
    ls_sigs_short = ['ZS_VAL', 'ZS_QLT', 'ZS_VAL_QLT', 'ZS_VAL_QLT_AMOM']
    ls_n_asts_short = [15, 20]
    ls_w_meth = ['EW', 'MN', 'RP']
    ls_pct_long_short = [(130, 30), (120, 50), (100, 100), (300, 200), (500, 400)]
    ls_ind_const = ['I', 'NI']
    ls_reb_freq = ['M', 'Q', 'Y']
    ls_combos = list(product(ls_sigs_long, ls_n_asts_long, ls_sigs_short, ls_n_asts_short,
                             ls_w_meth, ls_pct_long_short, ls_ind_const, ls_reb_freq))

    start_time = time.time()
    with Pool(processes=12) as pool:  # Multiprocessing
        results = list(tqdm(pool.imap(get_df_port_chars, ls_combos), total=len(ls_combos)))
    end_time = time.time()
    print('Elapsed time: {}s'.format(round(end_time - start_time, 0)))

    df_ports_chars = pd.concat(results, axis=0, ignore_index=True)
    df_ports_chars.to_pickle(Path.joinpath(paths.get('output'), 'df_ports_chars.pkl'))

if __name__ == "__main__":
    main()

