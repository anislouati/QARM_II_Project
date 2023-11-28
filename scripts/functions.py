# Import packages
from pathlib import Path


# %%
# **************************************************
# *** Branch: DATA MANAGEMENT                    ***
# **************************************************

# Project directories paths (README: modify if necessary!)
paths = {'main': Path.cwd()}
paths.update({'data': Path.joinpath(paths.get('main'), 'data'),
              'output': Path.joinpath(paths.get('main'), 'output'),
              'scripts': Path.joinpath(paths.get('main'), 'scripts')})
