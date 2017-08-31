#    OpenSBLI: An automatic code generator for solving differential equations.
#    Copyright (C) 2016 Satya P. Jammy, Christian T. Jacobs, Neil D. Sandham

#    This file is part of OpenSBLI.

#    OpenSBLI is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    OpenSBLI is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with OpenSBLI.  If not, see <http://www.gnu.org/licenses/>.

import os, os.path
import sys
import subprocess
import shutil

base_name = "mms"

N = 5 # Total number of simulations to perform

for degree in range(2, 13, 2):
    for i in range(0, N):
        # Form the directory name (and create the directory itself) where all files related to simulation 'i' will be kept.
        directory_name = base_name + "_%d_%d" % (degree, i)
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
        
        # Copy over the template mms.py simulation setup file.
        shutil.copy("src/mms.py", directory_name + "/mms.py")
        
        # The number of points will double each time.
        number_of_points = 4*(2**i)
        
        # Replace the number of points and the simulation name in the setup file.
        with open(directory_name + "/mms.py.new", "w") as new:
            with open(directory_name + "/mms.py", "r") as old:
                for line in old:
                    new.write(line.replace('NUMBER_OF_POINTS', str(number_of_points)).replace('SIMULATION_NAME', "\"%s\"" % directory_name).replace('DEGREE', "%s" % degree))
        shutil.move(directory_name + "/mms.py.new", directory_name + "/mms.py")

        # Generate the code
        exit_code = subprocess.call("cd %s; python mms.py" % (directory_name), shell=True)
        if(exit_code != 0):
            print("Something went wrong when generating the code for simulation %d." % i)
            sys.exit(1)
            
        # Copy over the Makefile and substitute in the correct simulation name.
        shutil.copy("src/Makefile", directory_name + "/%s_opsc_code/Makefile" % directory_name)
        with open(directory_name + "/%s_opsc_code/Makefile.new" % directory_name, "w") as new:
            with open(directory_name + "/%s_opsc_code/Makefile" % directory_name, "r") as old:
                for line in old:
                    new.write(line.replace('mms', str(directory_name)))
        shutil.move(directory_name + "/%s_opsc_code/Makefile.new" % directory_name, directory_name + "/%s_opsc_code/Makefile" % directory_name)
        
        # Run the simulation
        exit_code = subprocess.call("cd %s/%s_opsc_code; make %s_seq; ./%s_seq" % (directory_name, directory_name, directory_name, directory_name), shell=True)
