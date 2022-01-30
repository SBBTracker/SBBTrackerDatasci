from setuptools import setup, find_packages

with open('requirements.txt') as f:
    ls = f.read().splitlines()
    required = list()
    for i in ls:
        if not i.strip().startswith('#'):
            if i.startswith('git'):
                i = 'sbbbattlesim@' + i
            required.append(i)

setup(
    name='sbbtracker-datasci',
    version='0.0.1',
    description='A toolkit for analyzing SBBTracker data',
    author='Ilyas Aricanli',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=required,
    zip_safe=False,
    entry_points = {
        'console_scripts': ['sbbtracker-download=sbbtracker_datasci.download:download_data'],
    }
)

