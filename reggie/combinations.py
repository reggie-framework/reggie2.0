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
import os
import sys
import re
import logging
import collections

from reggie import tools


class Option:
    """Create an option object with a "name" and "values" similar to dict"""

    def __init__(self, name, values):
        self.name = name
        self.values = values


def splitValues(s):
    """Split string of values at ',' but not inside brackets, since a value can be an array, which is written as '(/ a, b, c /)'"""
    # This is done with a regular expression. Explanation:
    #   ,       : matches comma ','
    #   \s*     : match 0 or more whitespaces (actually not necessary, since we already removed all whitespaces)
    #   (?!...) : matches if ... doesn't match next.
    #   [^()]*  : matches all characters, except '(' or ')', 0 or more times
    #   \)      : matches closing bracket ')', the backslash is the escape-character
    return re.split(r',\s*(?![^()]*\))', s)


def isKeyOf(a, key_IN):
    """Check if the dictionary 'a' contains a key 'key_IN'"""
    found = False
    number = 0
    for key in a:
        if key == key_IN:
            number += 1
            found = True
    return found, number


def isSubset(a, b):
    """Check if the dictionary 'a' is a subset of the dictionary 'b'"""
    try:
        # build list of booleans, that contains for every key in 'a', if a[key] == b[key]
        tmp = [a[key] == b[key] for key in a]
    except KeyError:  # if a key of 'a' is not in 'b'
        return False
    return all(tmp)  # return True if all elements of tmp are True


def anyIsSubset(alist, b):
    """Check if any element 'a' of the list 'alist' is a subset of the dictionary 'b'"""
    tmp = [isSubset(a, b) for a in alist]  # build a list of booleans, that contains for every 'a' in alist if 'a' is a subset of 'b'
    return any(tmp)  # return True, if any 'a' of alist is a subset of 'b'


def readValueFromFile(filename, key):
    # fmt: off
    # Read the value of a single key from a file. Workflow:
    # 1.  Read file line by line:
    # 1.1   ignore exclusion (if line starts with 'exclude:')
    # 1.2   ignore noCrossCombination (if line starts with 'nocrosscombination:')
    # 1.3   get option and its values from line, if the key is the same as the key passed to the routine, break and return the matching value
    found = os.path.exists(filename)  # check if directory exists
    if not found:
        # raise getCombinationException(filename) # file not found
        raise Exception(tools.red(f"getCombination failed. file '{filename}' not found."))

    # 1. read options and exclusions from the file
    currentValue = None
    with open(filename) as f:
        for line in f:                          # iterate over all lines of the file
            line = re.sub(r"\s+", "", line)                 # remove all whitespaces ("\s" is the whitespac symbol)
            line = re.sub(r"\\s", " ", line)                # add new whitespaces for all occurrances of "\s" in the string ("\s" is NOT the whitespace symbol here)
            line = tools.exclude_comments_from_line(line)   # remove comments

            if line:                                        # exclude_comments_from_line returns None if line is commented out and returns line (without trailing comments) if not
                # 1.1 read an exclusion
                if line.lower().startswith('exclude:'):
                    continue  # ignore exclusion

                # 1.2 read a noCrossCombination
                if line.lower().startswith('nocrosscombination:'):
                    continue  # ignore noCrossCombination

                # 1.3 read a option and its possible values
                if '=' in line:
                    (currentKey, currentValue) = line.split('=', 1)  # split line at '='
                    if key.lower() == currentKey.lower():  # check if the key matches the one passed to the routine
                        break  # if so, break from the for loop
                    continue  # better luck in the next line
    # fmt: on
    return currentValue


def readKeyValueFile(filename):
    # fmt: off
    # General workflow:
    # 1.  Read file line by line:
    # 1.1   get exclusion from line (if line starts with 'exclude:')
    # 1.2   get noCrossCombination from line (if line starts with 'nocrosscombination:')
    # 1.3   get option and its values from line ( option=value1 [,value2 [,value3 ...]] )
    found = os.path.exists(filename)  # check if directory exists
    if not found :
        #  Raise getCombinationException(filename) # file not found
        raise Exception(tools.red(f"getCombination failed. file '{filename}' not found."))

    options = []                               # list of all options
    exclusions = []                            # list of all exclusions
    noCrossCombinations = []                   # list of all noCrossCombinations

    # 1. read options and exclusions from the file
    with open(filename) as f :
        for line in f :                             # iterate over all lines of the file
            line = re.sub(r"\s+", "", line)                     # remove all whitespaces ("\s" is the whitespac symbol)
            line = re.sub(r"\\s", " ", line)                    # add new whitespaces for all occurrances of "\s" in the string ("\s" is NOT the whitespace symbol here)
            line = tools.exclude_comments_from_line(line)       # remove comments

            if line:                                            # exclude_comments_from_line returns None if line is commented out and returns line (without trailing comments) if not
                # 1.1 read an exclusion
                if line.lower().startswith('exclude:') :
                    line = line.split(':', 1)[1]         # remove everything before ':''
                    ex = {}                              # new dictionary for the exclusion
                    for key_value in splitValues(line):  # split at ',' (but not inside brackets) and iterate over key-value-pairs
                        (key, value) = key_value.split('=')
                        ex[key] = value                  # save key and its value in the exclusion-dictionary

                    exclusions.append(ex)                # append exclusion to the list of all exclusions
                    continue                             # reading of exclusion finished -> go on with next line

                # 1.2 read a noCrossCombination
                if line.lower().startswith('nocrosscombination:') :
                    line = line.split(':', 1)[1]                    # remove everything before ':''
                    noCrossCombination = line.split(',')            # list of keys, that should not be cross combined
                    noCrossCombinations.append(noCrossCombination)  # append noCrossCombination to the list of all noCrossCombinations
                    continue                                        # reading of noCrossCombination finished -> go on with next line

                # 1.3 read a option and its possible values
                if '=' in line :
                    # Catch special variables
                    # DEFVAR=(INT):i0 = 1, 2
                    if "DEFVAR" in line and ("INT" in line or "REAL" in line) :
                        splitline = line.split('=', 2)
                        key       = "=".join(splitline[:2])
                        values    = splitline[2]
                    else:
                        (key, values) = line.split('=', 1)     # split line at '='
                    option = Option(key, splitValues(values))  # generate new Option with a list of values (splitted at ',' but not inside brackets)
                    options.append(option)                     # append option to options list, where
                    continue                                   # reading of option finished -> go on with next line
                # fmt: on

    options.sort(key=lambda option: len(option.values), reverse=True)  # sort list in order to have the most varying option at the beginning

    return options, exclusions, noCrossCombinations


def getCombinations(filename, CheckForMultipleKeys=False, OverrideOptionKey=None, OverrideOptionValue=None, MaxCores=0):
    # 1. get the key-value list from file
    # 1.1   get exclusion from line (if line starts with 'exclude:')
    # 1.2   get noCrossCombination from line (if line starts with 'nocrosscombination:')
    # 1.3   get option and it values from line ( option=value1 [,value2 [,value3 ...]] )
    options, exclusions, noCrossCombinations = readKeyValueFile(filename)

    # 1.4   Check if a options[].values (key in the dict) is to be overridden (removes all other occurrences too!)
    if OverrideOptionKey and OverrideOptionValue:
        print(tools.yellow(f"Setting all options for: {OverrideOptionKey}=[{OverrideOptionValue}]"))

        # find the key/value pair in the options and replace the key/value + re-sort the list
        option_not_found = True
        for i in range(len(options)):
            if options[i].name == OverrideOptionKey:
                options[i].values = [OverrideOptionValue]
                option_not_found = False
        if option_not_found:
            raise Exception(tools.red(f"Trying to set {OverrideOptionKey} = [{OverrideOptionValue}], but {OverrideOptionKey} was not found in the list."))

        options.sort(key=lambda option: len(option.values), reverse=True)  # sort list in order to have the most varying option at the beginning

    # Avoid performing multiple tests, where the number of cores will be limited to MaxCores(only set in the call from getCommand_Lines)
    if MaxCores > 0:
        # loop over all the options
        for i in range(len(options)):
            # find the MPI option
            if options[i].name == 'MPI':
                counter = 0
                # loop over the values
                for j in range(len(options[i].values)):
                    # determine number of cores above the MPICH limit
                    if int(options[i].values[j]) >= MaxCores:
                        counter += 1
                        # add an exclusion for the second and subsequent occurrences
                        if counter > 1:
                            ex = {options[i].name: options[i].values[j]}
                            exclusions.append(ex)

    # 2.  Compute combinations:
    # 2.1   count total number of all combinations
    # 2.2   build only the valid combinations (that do NOT match any exclusion)
    # 2. compute combinations
    # 2.1 count total number of possible combinations without the exclusions
    combinations = []  # list of all VALID combinations

    NumOfCombinationsTotal = 1
    # Test if any name has more than one value which would lead to at least 2 combinations, for sanity check later
    only_one_combination = False
    if not any((len(option.values) > 1) for option in options):
        only_one_combination = True
    for option in options:
        # Sanity check for names that have only one value, but are used in noCrossCombinations (if there is more than one combination)
        if not only_one_combination:
            for noCrossCombination in noCrossCombinations:
                if option.name in noCrossCombination and len(option.values) < 2:
                    print(
                        tools.red(
                            f'{option.name} has not more than one value ({option.values}), but is also included in noCrossCombinations,'
                            f'which could lead to some combinations which are not tested! Please add more values or remove {option.name} from noCrossCombinations.'
                        )
                    )
                    sys.exit(1)
        option.base = NumOfCombinationsTotal  # save total  number of combinations of all options before this option
        NumOfCombinationsTotal = NumOfCombinationsTotal * len(option.values)

    logging.getLogger('logger').debug(f"  Total number of combinations for '{filename:s}' = {NumOfCombinationsTotal:d}")

    # Maximum number of combinations BEFORE removing the invalid ones (if this value is to be further increased,
    # maybe think about re-writing the code and remove invalid combinations from the start)
    maxCombinations = int(1e5)

    if NumOfCombinationsTotal > maxCombinations:
        raise Exception(tools.red(f"{NumOfCombinationsTotal} is more than {maxCombinations} combinations in parameter.ini which is not allowed!"))

    digits = None
    # 2.2 build all valid combinations (all that do not match any exclusion)
    for i in range(NumOfCombinationsTotal):  # iterate index 'i' over NumOfCombinationsTotal
        combination = collections.OrderedDict()
        digits = collections.OrderedDict()
        # build i-th combination by adding all options with their name and a certain value
        for option in options:
            # compute index in the list of values of the option
            # Explanation with Example:
            #   Assume you are reading the following file:
            #       opt1 = black,white
            #       opt2 = a,b,c
            #       opt3 = cat,dog,bird,snake
            #       opt4 = car,train
            #   Then you get 2*3*4*2 = 48 combinations in total. Let us imagine the options (opt1, opt2, ...)
            #   as digits in a crazy number system, where opt1 is the digit with the lowest value and
            #   opt4 with the highest value. Since we have different number of values for every digit, the base
            #   of each digit is not as in a standard number system like the decimal a series of powers 10^0, 10^1, 10^2, ...
            #   In our example we get the following bases for the options:
            #       base of opt1 = 1   (first digit has base 1 in every number system)
            #       base of opt2 = 2   (since opt1 has two   values, we get a 2 here)
            #       base of opt3 = 6   (since opt2 has three values and base=2, we get 2*3=6.  This is the number of combinations of opt1 and opt2)
            #       base of opt4 = 24  (since opt3 has four  values and base=6, we get 6*4=24. This is the number of combinations of opt1, opt2 and opt3)
            #   Luckily we already stored the base while counting the number of all combinations before.
            #   We now can compute the index in the list of values of an option (which is the value of the respective digit in our crazy number system)
            #   by dividing the index i (which is a number in our crazy number system) by the base and modulo the number of values of the option.
            j = (i / option.base) % len(option.values)
            digits[option.name] = int(j)

        for option in options:
            if CheckForMultipleKeys:
                # check if the same parameter name (e.g. 'BoundaryName') occurs more than once in the list and
                # move multiple occurrences to a separate key/value where the value is a list of all occurrences
                # this must be done, because dicts cannot have the same key name more than once (it is a dictionary)
                found, number = isKeyOf(combination, option.name)
                if found:
                    new_key = "MULTIPLE_KEY:" + option.name
                    logging.getLogger('logger').info(
                        tools.yellow(str(option.name))
                        + " is already in list (found "
                        + str(number)
                        + " times). "
                        + "Adding new key/value as "
                        + tools.yellow(new_key)
                        + " with value="
                        + option.values[digits[option.name]]
                    )
                    # create list for value in key/value pair for the new re-named option "MULTIPLE_KEY+X"
                    combination.setdefault(new_key, []).append(option.values[digits[option.name]])
                    digits[new_key] = -100  # default value for special key
                else:
                    combination[option.name] = option.values[digits[option.name]]
            else:
                combination[option.name] = option.values[digits[option.name]]

        # check if the combination is valid (does not match any exclusion)
        if anyIsSubset(exclusions, combination):
            continue  # if any exclusion matches the combination, the combination is invalid => cycle and do not add to list of valid combinations

        # check if option is marked with "noCrossCombinations", these are not to be permutated
        skip = False
        for noCrossCombination in noCrossCombinations:
            # Check if the parameter exists in the list
            if digits.get(noCrossCombination[0], None) is None:
                print(tools.red(f"nocrosscombination [{noCrossCombination[0]}] not found in list of parameters given in [{filename}].\nOnly parameters that are read can be considered for nocrosscombination."))
                sys.exit(1)

            # Check all noCrossCombinations and skip them is they already were added to the list
            if not all(digits[key] == digits[noCrossCombination[0]] for key in noCrossCombination):
                skip = True
                break

        # Don't add combination if it was marked skip=True
        if skip:
            continue

        # add valid combination
        combinations.append(combination)

    logging.getLogger('logger').debug(f"  Number of valid combinations = {len(combinations):d}")
    return combinations, digits


def writeCombinationsToFile(combinations, path):
    # write one set of parameters to a file, e.g., parameter.ini
    with open(path, 'w') as f:
        for key, value in combinations.items():
            # check if multiple parameters with the exact same name are used within parameter.ini (examples are BoundaryName or RefState)
            if "MULTIPLE_KEY:" in key:
                f.write(f"  ! {key}={value}\n")  # write comment into file
                # write all multiple occurring values of the multiple key without "MULTIPLE_KEY:" to file
                f.writelines(f"{key[13:]}={item}\n" for item in value)  # write key/value into file
            else:
                # for parameters with value 'crosscombinations' in the key-value pair, replace it with the value from 'crosscombinations'
                #
                # example: N                 = crosscombinations
                #          N_Geo             = crosscombinations
                #          crosscombinations = 1,2,3,4,5
                #
                # this results in using 1,2,3,4,5 for both "N" and "NGeo" (as an example)
                if value == 'crosscombinations':
                    f.write("{}={}\n".format(key, combinations.get('crosscombinations')))
                else:
                    f.write(f"{key}={value}\n")


# class getCombinationException(Exception) : # Exception for missing files, e.g., command_line.ini
# def __init__(self, filename):
# self.filename = filename
# def __str__(self):
# return tools.printr("getCombination failed. file '%s' not found." % (self.filename))
