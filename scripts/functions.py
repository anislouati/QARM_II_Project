# Import packages
from pathlib import Path
import pandas as pd

# Project directories paths (README: modify if necessary!)
paths = {'main': Path.cwd()}
paths.update({'data': Path.joinpath(paths.get('main'), 'data'),
              'output': Path.joinpath(paths.get('main'), 'output'),
              'scripts': Path.joinpath(paths.get('main'), 'scripts')})


# %%
# **************************************************
# *** Branch: DATA MANAGEMENT                    ***
# **************************************************

def tab_summary(df_data):
    df_summary = pd.DataFrame({'Count': df_data.count(),  # Count of non-missing values
                               'Missing Pct': (df_data.isna().sum() / len(df_data)),  # Missing values as percentage
                               'Mean': df_data.mean(),
                               'Min': df_data.min(),
                               '25%': df_data.quantile([0.25]),
                               '50%': df_data.quantile([0.50]),
                               '75%': df_data.quantile([0.75]),
                               'Max': df_data.max()})
    return df_summary

