import argparse
import sys
import os
import subprocess
import traceback

parser = argparse.ArgumentParser(description="CMake driver for Trilinos");

parser.add_argument('--opt', action='store_true', default=True)
parser.add_argument('--mpi',  action='store_true', default=False)
parser.add_argument('--public',  action='store_true', default=True)
parser.add_argument('--static',  action='store_true', default=False)
parser.add_argument('--noexplicit',  action='store_true', default=True)
parser.add_argument('--ordType',  action='store', default='int',
                    choices=("int", "long", "long int", "long long"))
parser.add_argument('--prefix', action='store', default='${PWD}')
parser.add_argument('--src', action='store', default='${HOME}/Code/TTUTrilinos')
parser.add_argument('--mac', action='store_true', default=False)
parser.add_argument('--dryrun', action='store_true', default=False)


args = parser.parse_args()

if args.opt==True:
    buildType="RELEASE"
else:
    buildType="DEBUG"

if args.mpi==True:
    enableMPI="ON"
else:
    enableMPI="OFF"

if args.noexplicit==True:
    useExplicitTemplates="OFF"
else:
    useExplicitTemplates="ON"

if args.static==True:
    buildShared="OFF"
else:
    buildShared="ON"


# oddball settings for Katharine's mac.
if args.mac==True:
    ldflags=""
    suf = "dylib"
    cc = "gcc-mp-7"
    cxx = "g++-mp-7"
    fc = "gfortran-mp-7"
    lapackLibPath="/opt/local/lib/lapack"
    hdf5LibPath="/opt/local/lib"
    netcdfLibPath="/opt/local/lib"
    lapackIncPath="/opt/local/include/lapack"
    hdf5IncPath="/opt/local/include"
    netcdfIncPath="/opt/local/include"
    #xlib = "/usr/X11R6/lib/libX11.dylib"
    xlib = "/opt/X11/lib/libX11.dylib"
else: # Settings for a Ubuntu 20.04 machine with packages
    # installed by apt-get.
    ldflags="-Wl,--no-undefined"
    suf = "so"
    cc="gcc"
    cxx="g++"
    fc="gfortran"
    lapackLibPath="/usr/lib/x86_64-linux-gnu"
    hdf5LibPath="/usr/lib/x86_64-linux-gnu"
    netcdfLibPath="/usr/lib/x86_64-linux-gnu"
    lapackIncPath="/usr/include"
    hdf5IncPath="/usr/include"
    netcdfIncPath="/usr/include"
    xlib = "/usr/lib/x86_64-linux-gnu/libX11.so"
if args.mpi==True:
    cc = "mpicc"
    cxx="mpicxx"
    fc="mpif90"

cxxFlags="'-std=c++11 -fPIC -O3 -funroll-all-loops -finline-functions -DEPETRA_LAPACK3'"
cFlags=""
fFlags=""



cmakeOpts = {    "CMAKE_BUILD_TYPE" : ("STRING", buildType),
                "BUILD_SHARED_LIBS" : ("BOOL", buildShared),
                "CMAKE_C_COMPILER" : ("STRING", cc),
                "CMAKE_CXX_COMPILER" : ("STRING", cxx),
                "CMAKE_Fortran_COMPILER" : ("STRING",fc),
                "CMAKE_CXX_FLAGS" : ("STRING", cxxFlags),
		"CMAKE_SHARED_LINKER_FLAGS" : ("STRING", ldflags),
                "CMAKE_C_FLAGS" : ("STRING", cFlags),
                "CMAKE_Fortran_FLAGS" : ("STRING", fFlags),
                 "CMAKE_MACOSX_RPATH" : ("STRING", "TRUE"),
                 "CMAKE_INSTALL_RPATH" : ("FILEPATH", args.prefix+"/lib"),
                 "CMAKE_INSTALL_NAME_DIR" : ("FILEPATH", args.prefix+"/lib"),
                 "TPL_ENABLE_MPI" : ("BOOL", enableMPI),
                 "TPL_ENABLE_Netcdf" : ("BOOL", "TRUE"),
                 "TPL_ENABLE_Matio" : ("BOOL", "FALSE"),
                 "TPL_HDF5_LIBRARIES" : ("STRING", "%s/libhdf5.%s" % (hdf5LibPath, suf)),
                 "TPL_X11_LIBRARIES" : ("STRING", xlib),
                 "TPL_BLAS_LIBRARIES" : ("STRING", "%s/libblas.%s" % (lapackLibPath, suf)),
                 "TPL_LAPACK_LIBRARIES" : ("STRING", "%s/liblapack.%s" % (lapackLibPath, suf)),
                 "TPL_BLAS_LIBRARY_DIR" : ("FILEPATH", "%s" % lapackLibPath),
                 "TPL_LAPACK_LIBRARY_DIR" : ("FILEPATH", "%s" % lapackLibPath),
                 "TPL_BLAS_INCLUDE_DIRS" : ("FILEPATH", "%s" % lapackIncPath),
                 "TPL_LAPACK_INCLUDE_DIRS" : ("FILEPATH", "%s" % lapackIncPath),
                 "TPL_Netcdf_LIBRARIES" : ("STRING", "%s/libnetcdf.%s" % (netcdfLibPath, suf)),
                 "TPL_Netcdf_LIBRARY_DIRS" : ("FILEPATH", "%s" % netcdfLibPath),
                 "TPL_Netcdf_INCLUDE_DIRS" : ("FILEPATH", "%s" % netcdfIncPath),
                 "Trilinos_EXTRA_LINK_FLAGS" : ("STRING", "-lgfortran -lm -lpthreads"),
                 "Trilinos_ASSERT_MISSING_PACKAGES" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_SHADOW_WARNINGS" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_ALL_OPTIONAL_PACKAGES" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_SECONDARY_STABLE_CODE" : ("BOOL", "ON"),
                 "Trilinos_ENABLE_CHECKED_STL" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_TESTS" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_EXAMPLES" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_EXPLICIT_INSTANTIATION" : ("BOOL", useExplicitTemplates),
                 "Trilinos_ENABLE_Sundance" : ("BOOL", "ON"),
                 "Trilinos_ENABLE_SEACAS" : ("BOOL", "ON"),
                 "Trilinos_ENABLE_Sacado" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_Stokhos" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_Gtest" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_Zoltan" : ("BOOL", enableMPI),
                 "Sundance_ENABLE_TESTS" : ("BOOL", "ON"),
                 "Sundance_ENABLE_EXAMPLES" : ("BOOL", "ON"),
                 "Stokhos_ENABLE_TESTS" : ("BOOL", "OFF"),
                 "Zoltan_ENABLE_TESTS" : ("BOOL", "OFF"),
                 "SEACAS_ENABLE_TESTS" : ("BOOL", "OFF"),
                 "SEACASExodus_ENABLE_MPI" : ("BOOL", "OFF"),
                 "EpetraExt_USING_HDF5" : ("BOOL", "OFF"),
                 "Trilinos_ENABLE_SEACASNemslice" : ("BOOL", "ON"),
                 "Trilinos_ENABLE_SEACASSVDI" : ("BOOL", "ON"),
                 "Trilinos_ENABLE_SEACASChaco" : ("BOOL", "ON"),
                 "Trilinos_ENABLE_SEACASEpu" : ("BOOL", "ON"),
                 "Stokhos_ENABLE_EXAMPLES" : ("BOOL", "OFF"),
                 "Sundance_ENABLE_Python" : ("BOOL", "OFF"),
                 "Sundance_ENABLE_SEACAS" : ("BOOL", "ON"),
                 "Teuchos_ORDINAL_TYPE" : ("STRING", args.ordType),
                 "NOX_ENABLE_LOCA" : ("BOOL", "OFF"),
                 "Trilinos_SKIP_FORTRANCINTERFACE_VERIFY_TEST" : ("BOOL", "TRUE"),
                 "CMAKE_INSTALL_PREFIX" : ("FILEPATH", args.prefix)
}

cmd = 'cmake'
for key in cmakeOpts.keys():
    val = cmakeOpts[key];
    cmd = cmd + " -D%s:%s=%s" % (key,  val[0], val[1])

cmd = cmd + ' ' + args.src


if args.dryrun==True:
    print("arguments are: ", args)
    print("command is: ", cmd)
    sys.exit()
else:
    print(args.src)
    os.system(cmd)
