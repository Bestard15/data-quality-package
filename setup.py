from setuptools import setup, find_packages

setup(
    name='data_quality_auditor',
    version='0.2.0',
    packages=find_packages(where=''),
    install_requires=[
        'pandas',
        'PyYAML',
        'click'
    ],
    entry_points={
        'console_scripts': [
            'audit_data=scripts.main:main',
        ],
    },
    include_package_data=True,
    package_data={'': ['rules.yml']},
    description='Auditor automático de calidad de datos',
    author='Juan',
    author_email='tu.email@updata.link',
)
