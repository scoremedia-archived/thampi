"""
Create a Machine Learning Prediction Server on AWS Lambda.
"""
from setuptools import find_packages, setup

dependencies = ['click', 'cloudpickle', 'zappa==0.45.1', 'Flask==0.12.4', 'docker']

setup(
    name='thampi',
    version='0.1.0',
    url='https://github.com/scoremedia/thampi',
    license='BSD',
    author='theScore Inc.',
    author_email='oss@thescore.com',
    description='Create a Machine Learning Prediction Server on AWS Lambda.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'thampi = thampi.cli.cli:main',
        ],
    },
    classifiers=[
        # As from http://pypi.python.org/pypi?%3Aaction=list_classifiers
        # 'Development Status :: 1 - Planning',
        # 'Development Status :: 2 - Pre-Alpha',
        # 'Development Status :: 3 - Alpha',
        'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        # 'Development Status :: 6 - Mature',
        # 'Development Status :: 7 - Inactive',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
