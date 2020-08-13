#############################################################################
#
# This script installs development utilities, compilers, and libraries needed
# to build the TTU version of Trilinos and the XTemp thermal analyzer.
#
#############################################################################
import argparse
import sys
import os
import subprocess
import traceback

if os.getuid()!=0:
    print('This script must be run using sudo')
    sys.exit(-1)

if os.uname()[0] != 'Linux':
    print('This script is Linux-specific. Oops.')
    sys.exit(-1)


parser = argparse.ArgumentParser(description="Setup of development tools");
parser.add_argument('--dryrun', action='store_true', default=False)

args = parser.parse_args()

for f in ('m4', 'git', 'cmake', 'gcc', 'g++', 'gfortran', 'libssl-dev',
    'openssh-client, openssh-server', 'liblapack3', 'liblapack-dev',
    'libblas3', 'libblas-dev', 'libx11-dev', 'gcc-8', 'g++-8',
    'gfortran-8', 'libgsl-dev', 'netcdf-bin', 'libnetcdf-dev', 'swig'):

    cmd = 'apt-get -y install %s' % f

    if args.dryrun==True:
        os.system('echo %s' % cmd)
    else:
        os.system(cmd)
