#!/usr/bin/env python

'''
 Copyright (c) 2013, Lawrence Livermore National Security, LLC.
 Produced at the Lawrence Livermore National Laboratory (cf, DISCLAIMER).
 Written by Charles Heizer <heizer1 at llnl.gov>.
 LLNL-CODE-636469 All rights reserved.
 
 This file is part of MacPatch, a program for installing and patching
 software.
 
 MacPatch is free software; you can redistribute it and/or modify it under
 the terms of the GNU General Public License (as published by the Free
 Software Foundation) version 2, dated June 1991.
 
 MacPatch is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the IMPLIED WARRANTY OF MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE. See the terms and conditions of the GNU General Public
 License for more details.
 
 You should have received a copy of the GNU General Public License along
 with MacPatch; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
'''

import pip
import zipfile

_pre_ = [
    "pip",
    "setuptools"
]

_all_ = [
    'argparse>=1.3.0',
    'requests>=2.7.0',
    'biplist>=0.9',
    'wheel>=0.24.0',
    'six>=1.9.0',
    'python-dateutil>=2.4.2',
]

srcDir = "/opt/MacPatch/Server/conf/src"
mysql = srcDir + "/mysql-connector-python-2.1.3"

linux = ['python-crontab>=1.9.3']
darwin = ["mysql-connector-python-rf>=2.1.3"]

def installAlt(package):
    # Debugging
    # pip.main(["install", "--pre", "--upgrade", "--no-index",
    #         "--find-links=.", package, "--log-file", "log.txt", "-vv"])
    pip.main(["install", "--no-index", "--find-links=.", package])

def install(packages):
    for package in packages:
        pip.main(["install", "--upgrade", "--trusted-host", "pypi.python.org", package])

if __name__ == '__main__':

    from sys import platform

    install(_pre_)
    install(_all_) 
    
    if platform.startswith('linux'):
        install(linux)

    if platform.startswith('darwin'): # MacOS
        install(darwin)
        installAlt(cryptoPKG)