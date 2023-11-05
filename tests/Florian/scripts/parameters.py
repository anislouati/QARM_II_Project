from pathlib import Path

# Project directories paths
paths = {'main': Path.cwd()}

paths.update({'data': Path.joinpath(paths.get('main'), 'data'),
              'output': Path.joinpath(paths.get('main'), 'output'),
              'scripts': Path.joinpath(paths.get('main'), 'scripts')})


# Florian directories paths
paths_florian = {'main': Path.joinpath(Path.cwd(), 'tests\Florian')}

paths_florian.update({'output': Path.joinpath(paths_florian.get('main'), 'output'),
              'scripts': Path.joinpath(paths_florian.get('main'), 'scripts')})

