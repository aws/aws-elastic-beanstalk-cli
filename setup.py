# For more details on how to operate this file, check
# https://w.amazon.com/index.php/Python/Brazil
import re
from setuptools import setup, find_packages, Command
from glob import glob
from brazilpython.setup_utilities import find_data_files, add_command_by_name

# declare your scripts:
# scripts in bin/ with a shebang containing python will be
# recognized automatically
scripts = []
for fname in glob('bin/*'):
    with open(fname, 'r') as fh:
        if re.search(r'^#!.*python', fh.readline()):
            scripts.append(fname)

# if you have any python modules (.py files instead of dir/__init__.py
# packages) list them here:
py_modules = []

# Add data files from the configuration/ directory, if it exists. By
# default this is equivalent to has_configuration = true in your package
# Config
data_files = find_data_files('configuration/', '*', prefix='')

# add custom commands here:
cmdclass = {}

# you should not need to modify anything below, unless you need to build
# C extensions

args = dict(
    name='EB-CLI',
    version='1.0',
    # declare your packages
    packages=find_packages('lib'),
    # declare your scripts
    scripts=scripts,
    # declare custom commads
    cmdclass=cmdclass,
    package_dir={'': 'lib'},
    data_files=data_files,
    options={
        # make sure the right shebang is set for the scripts
        'build_scripts': {
            'executable': '/apollo/sbin/envroot "$ENVROOT/bin/python"',
            },
        },
    )

add_command_by_name('flake8', args)
add_command_by_name('build_sphinx', args)

if py_modules:
    args['py_modules'] = py_modules

setup(**args)
