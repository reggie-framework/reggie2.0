# ==================================================================================================================================
# Copyright (c) 2017 - 2018 Stephen Copplestone and Matthias Sonntag
#
# This file is part of reggie2.0 (gitlab.com/reggie2.0/reggie2.0). reggie2.0 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# reggie2.0 is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License v3.0 for more details.
#
# You should have received a copy of the GNU General Public License along with reggie2.0. If not, see <http://www.gnu.org/licenses/>.
# ==================================================================================================================================
from timeit import default_timer as timer
import logging
from reggie import tools
from reggie import check
from reggie import args_parser
from reggie import summary
import sys

"""
General workflow:
1.  get the command line arguments 'args' and all valid build combinations in the check directory from 'builds.ini'
2.  set the logger 'log' with the debug level from 'args' to determine the level of logging which displays output to the user
3.  perform the regression check by a) building executables
                                    b) running the code
                                    c) performing the defined analyzes
4.  display the summary table with information for each build, run and analysis step
5.  display if regression check was successful or not and return the corresponding error code
"""


def main():
    # Local imports ----------------------------------------
    from reggie.common.common_vars import Common

    # ------------------------------------------------------
    print('')
    print(tools.red(r'       oooooooo      ====================') + tools.yellow(r'=====================================') + tools.green(r'====================      oooooooo       '))
    print(tools.red(r'    ooo   oo   ooo      _____    ______  ') + tools.yellow(r'  _____    _____   _____   ______    ') + tools.green(r' ___         ___       ooo   oo   ooo    '))
    print(tools.red(r'   oo     oo     oo    |  __ \  |  ____| ') + tools.yellow(r' / ____|  / ____| |_   _| |  ____|   ') + tools.green(r'|__ \       / _ \     oo     oo     oo   '))
    print(tools.red(r'  oo      oo      oo   | |__) | | |__    ') + tools.yellow(r'| |  __  | |  __    | |   | |__      ') + tools.green(r'   ) |     | | | |   oo      oo      oo  '))
    print(tools.red(r'  oo     oooo     oo   |  _  /  |  __|   ') + tools.yellow(r'| | |_ | | | |_ |   | |   |  __|     ') + tools.green(r'  / /      | | | |   oo     oooo     oo  '))
    print(tools.red(r'  oo    oooooo    oo   | | \ \  | |____  ') + tools.yellow(r'| |__| | | |__| |  _| |_  | |____    ') + tools.green(r' / /_   _  | |_| |   oo    oooooo    oo  '))
    print(tools.red(r'   oo oo  oo  oo oo    |_|  \_\ |______| ') + tools.yellow(r' \_____|  \_____| |_____| |______|   ') + tools.green(r'|____| (_)  \___/     oo oo  oo  oo oo   '))
    print(tools.red(r'    ooo   oo   ooo                       ') + tools.yellow(r'                                     ') + tools.green(r'                       ooo   oo   ooo    '))
    print(tools.red(r'       oooooooo      ====================') + tools.yellow(r'=====================================') + tools.green(r'====================      oooooooo       '))
    print('')

    start = timer()
    print(sys.version_info)

    common = Common()
    program = common.program
    version = common.version
    commit = common.commit
    print(f'{program} version {version}' + (f' [commit {commit}]' if commit else ''))

    # 1.  get the command line arguments 'args' and all valid build combinations in the check directory from 'builds.ini'
    args, builds = args_parser.getArgsAndBuilds()

    # 2.  set the logger 'log' with the debug level from 'args' to determine the level of logging which displays output to the user
    tools.setup_logger(args.debug)
    log = logging.getLogger('logger')

    # 3.  perform the regression check by a) building executables
    #                                     b) running the code
    #                                     c) performing the defined analyzes
    check.PerformCheck().main(start, builds, args, log)

    # 4.  display the summary table with information for each build, run and analysis step
    summary.SummaryOfErrors(builds, args)

    # 5.  display if regression check was successful or not and return the corresponding error code
    summary.finalize(start, 0, check.Run.total_errors, check.ExternalRun.total_errors, check.Analyze.total_errors, check.Analyze.total_infos)


if __name__ == '__main__':
    main()
