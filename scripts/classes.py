# Import packages
from pathlib import Path
import numpy as np
import pandas as pd


# %%
# **************************************************
# *** Branch: Paths                              ***
# **************************************************

# Project directories paths
paths = {'main': Path.cwd()}

paths.update({'data': Path.joinpath(paths.get('main'), 'data'),
              'output': Path.joinpath(paths.get('main'), 'output'),
              'scripts': Path.joinpath(paths.get('main'), 'scripts')})


# %%
# **************************************************
# *** Branch: Data Management                    ***
# **************************************************

