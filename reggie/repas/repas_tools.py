# ==================================================================================================================================
# Copyright (c) 2017 - 2018 Stephen Copplestone
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
import os
import sys
import fileinput
from timeit import default_timer as timer
import logging
import subprocess

# import reggie source code
# use reggie2.0 functions by adding the path
import reggie.tools as tools
from reggie.combinations import getCombinations
from reggie.combinations import readKeyValueFile
from reggie.combinations import isKeyOf
from reggie.externalcommand import ExternalCommand


class bcolors:
    """Color and font style definitions for changing output appearance"""

    # Reset (user after applying a color to return to normal coloring)
    # fmt: off
    ENDC   ='\033[0m'

    # Regular Colors
    BLACK  ='\033[0;30m'
    RED    ='\033[0;31m'
    GREEN  ='\033[0;32m'
    YELLOW ='\033[0;33m'
    BLUE   ='\033[0;34m'
    PURPLE ='\033[0;35m'
    CYAN   ='\033[0;36m'
    WHITE  ='\033[0;37m'

    # Text Style
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    # fmt: on


class Case(ExternalCommand):
    def __init__(self, cwd, command, names_file, names2_file, parameter_file):
        ExternalCommand.__init__(self)
        # fmt: off
        self.target_directory = cwd
        self.nErrors          = 0
        self.command          = command
        self.failed           = False
        # fmt: on

        self.names_file = os.path.join(cwd, names_file)
        # check if file exists
        if not os.path.exists(self.names_file):
            print(tools.red(f"parameter_rename.ini file not found under: '{self.names_file}'"))
            sys.exit(1)

        self.names2_file = os.path.join(cwd, names2_file)
        # check if file exists
        if not os.path.exists(self.names2_file):
            print(tools.red(f"parameter_change.ini file not found under: '{self.names2_file}'"))
            sys.exit(1)

        self.parameter_file = os.path.join(cwd, parameter_file)
        # check if file exists
        if not os.path.exists(self.parameter_file):
            print(tools.red(f"parameter.ini file not found under: '{self.parameter_file}'"))
            sys.exit(1)

        # display used files
        print("Using the following input files")
        print("parameter_rename.ini".ljust(25), " = [", self.names_file, "]")
        print("parameter_change.ini".ljust(25), " = [", self.names2_file, "]")
        print("parameter.ini       ".ljust(25), " = [", self.parameter_file, "]")
        print('=' * 132)

    def create(self, combi, digits):
        # copy original parameter.ini file to backup parameter_backup.ini file
        subprocess.check_call(f"cp {self.parameter_file} parameter_backup.ini")

        # create temorary parameter_tmp.ini file which will be edited
        tmp_file_name = "parameter_tmp.ini"
        subprocess.check_call(f"cp {self.parameter_file} {tmp_file_name}")  # mv parameter file to tmp file

        # check each line; if a changable parameter is found, set the current key/value pair in the combi
        with fileinput.input('parameter_tmp.ini', inplace=True) as f:
            for line in f:
                line_written = False
                for key, value in combi.items():
                    if digits[key] >= 0 and line.startswith(key):
                        print(f"{key} = {value}")
                        line_written = True
                if not line_written:
                    print(line.strip())

        # copy temorary parameter_tmp.ini to original file
        subprocess.check_call(f"mv {tmp_file_name} {self.parameter_file}")  # mv tmp file to parameter file

    def names(self):
        # read combinations in 'parameter.ini' for renaming the results
        combis, _ = getCombinations(self.parameter_file, CheckForMultipleKeys=True)

        # set "suffix"
        logging.getLogger('logger').debug("")
        logging.getLogger('logger').debug("")
        logging.getLogger('logger').debug(tools.yellow('=' * 132))
        logging.getLogger('logger').debug("Creating output name:")
        if not os.path.exists(self.names_file):
            print(tools.red(f"parameter_rename.ini file not found under: '{self.names_file}'"))
            sys.exit(1)
        options_names, _, _ = readKeyValueFile(self.names_file)
        suffix = ''
        for option in options_names:
            logging.getLogger('logger').debug(f"option.name={option.name!s}")
            found, _ = isKeyOf(combis[0], option.name)
            if found:
                logging.getLogger('logger').debug(str(option.name) + " = " + tools.blue(str(found)) + f" ({combis[0][option.name]})")
                suffix += "_" + str(option.values[0]) + f"{combis[0][option.name]}"
            else:
                print(str(option.name) + " = " + tools.red(str(found)) + " (NOT FOUND!)")

        print(f"Name=[{tools.red(suffix)}]")
        logging.getLogger('logger').debug(tools.yellow('=' * 132))
        logging.getLogger('logger').debug("")
        logging.getLogger('logger').debug("")

        self.suffix = suffix
        self.prefix = suffix[1:] + "_"

    def run(self, i):
        try:
            s = f"cmd={self.command}"
            if self.execute_cmd(self.command, self.target_directory, string_info=s) != 0:  # use uncolored string for cmake
                self.failed = True
        except Exception:  # this fails, if the supplied command line is corrupted
            print(tools.red("Failed"))
            self.failed = True

        # if self fails, add error to number of errors
        if self.failed:
            self.nErrors += 1

        # move the std.out file
        old_std = os.path.join(self.target_directory, 'std.out')
        new_std = os.path.join(self.target_directory, f'std-{i:04d}')
        if os.path.exists(os.path.abspath(old_std)):  # check if file exists
            os.rename(old_std, new_std)

        # move the err.out file
        old_err = os.path.join(self.target_directory, 'std.err')
        new_err = os.path.join(self.target_directory, f'std-{i:04d}.err')
        if os.path.exists(os.path.abspath(old_err)):  # check if file exists
            os.rename(old_err, new_err)

    def save_data(self):
        # 0.0 set output folder structure
        output_path = "output_dir/standalone/examples/cmd_0001"
        if os.path.exists(output_path):
            self.results_main = "results/"
            if not os.path.exists(self.results_main):
                tools.create_folder(self.results_main)

        # 1.0 save data from output_dir/standalone/examples/cmd_0001
        try:
            for folder in os.listdir(output_path):
                folder_path = os.path.join(output_path, folder)
                if not os.path.isdir(folder_path):
                    continue
                for file in os.listdir(folder_path):
                    # create results sub-directory if it is non-existent
                    self.results_sub = f"results/{folder}" + self.suffix
                    if not os.path.exists(self.results_sub):
                        tools.create_folder(self.results_sub)
                    file_path = os.path.join(folder_path, file)

                    # save files with different endings
                    ext = [".csv", ".pdf", ".txt", "parameter.ini", "std.out"]
                    #  ".m2ts", ".mkv", ".mov", ".mp4", ".mpg", ".mpeg", \
                    #  ".rm", ".swf", ".vob", ".wmv"]
                    if file.endswith(tuple(ext)):
                        subprocess.check_call("cp " + file_path + " " + self.results_sub + "/.")
        except Exception as ex:
            print("save_data: cannote store any data because (some) output was not created")
            print('Error: ' + str(ex))

        # 1.1 save convergence data from output_dir/standalone/examples/cmd_0001
        try:
            for file in os.listdir(output_path):
                if file.endswith(".pdf"):
                    try:
                        if file.index('order') != -1:
                            # order = file[file.index('order') + 5 : -4]  # get string from 'order' + 5 to the end, but remove last 4 character ".pdf"
                            # new_name = "L2"+self.suffix+"_order%s.pdf" % order # add suffix to name
                            new_name = self.prefix + file
                    except Exception:
                        new_name = "L2" + self.suffix + ".pdf"
                    subprocess.check_call("cp output_dir/standalone/examples/cmd_0001/" + file + " " + self.results_main + new_name)  # move file to upper most path

                if file.endswith(".csv"):
                    try:
                        if file.index('order') != -1:
                            # order = file[file.index('order') + 5 : -4]  # get string from 'order' + 5 to the end, but remove last 4 character ".pdf"
                            # new_name = "L2"+self.suffix+"_order%s.csv" % order # add suffix to name
                            new_name = self.prefix + file
                    except Exception:
                        new_name = "L2" + self.suffix + ".csv"
                    subprocess.check_call("cp output_dir/standalone/examples/cmd_0001/" + file + " " + self.results_main + new_name)  # move file to upper most path
        except Exception as ex:
            print("save_data: cannote store convergence data because (some) output was not created")
            print('Error: ' + str(ex))


def finalize(start, run_errors):
    """Display if repas was successful or not and return the number of errors that were encountered"""
    if run_errors > 0:
        print(bcolors.RED + 132 * '=')
        print("repas tool  FAILED!", end=' ')  # skip linebreak
        return_code = 1
    else:
        print(bcolors.BLUE + 132 * '=')
        print("repas tool  successful!", end=' ')  # skip linebreak
        return_code = 0

    if start > 0:  # only calculate run time and display output when start > 0
        end = timer()
        print("in [%2.2f sec]" % (end - start))
    else:
        print()

    print(f"Number of run     errors: {run_errors:d}")

    print('=' * 132 + bcolors.ENDC)
    sys.exit(return_code)
