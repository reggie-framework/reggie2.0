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

from reggie import tools


class OutputDirectory:
    output_dir = "output_dir"

    def __init__(self, parent, name, number=-1, mkdir=True):
        self.number = number
        self.parent = parent

        # set parent directory for subfolder creation
        parent_dir = self.parent.target_directory if self.parent else OutputDirectory.output_dir

        # numbering of directory (if a number is supplied)
        if number >= 0:
            self.target_directory = os.path.join(parent_dir, f"{name:s}_{number:04d}")
        else:
            self.target_directory = os.path.join(parent_dir, name)

        # create directory if it is non-existent
        if mkdir:
            tools.create_folder(self.target_directory)
