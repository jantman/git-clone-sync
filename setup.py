from setuptools import setup, find_packages
from sys import version_info
from gitclonesync import VERSION

with open('README.rst') as file:
    long_description = file.read()

with open('CHANGES.rst') as file:
    long_description += '\n' + file.read()

requires = [
    'GitPython>=0.3.2.1',
    'githup3.py>=0.8.2',
]

classifiers = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Information Technology',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Natural Language :: English',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 2 :: Only',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Topic :: Software Development :: Version Control',
    'Topic :: Utilities',
]

setup(
    name='gitclonesync',
    version=VERSION,
    author='Jason Antman',
    author_email='jason@jasonantman.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'git_clone_sync = gitclonesync.clonesyncer:cli_entry',
            'set_github_remote = gitclonesync.githubclone:cli_entry',
        ],
    },
    url='http://github.com/jantman/git-clone-sync/',
    license='GPLv3+',
    description='Script to keep git clones in sync with origin and upstream',
    long_description=long_description,
    install_requires=requires,
    keywords="git clone cron",
    classifiers=classifiers
)
