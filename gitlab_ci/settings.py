# ==================================================================================================================================
# Copyright (c) 2017 - 2018 Stephen Copplestone
#
# This file is part of reggie (github.com/reggie-framework/reggie). reggie is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3
# of the License, or (at your option) any later version.
#
# reggie is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License v3.0 for more details.
#
# You should have received a copy of the GNU General Public License along with reggie. If not, see <http://www.gnu.org/licenses/>.
# ==================================================================================================================================
import os
import sys


def init():
    absolute_reggie_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if not os.path.exists(absolute_reggie_path):
        print(f"Reggie repository not found under: '{absolute_reggie_path}'")
        sys.exit(1)
