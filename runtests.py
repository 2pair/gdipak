import subprocess
from os import path

tests_script = path.join(".","tests","tests.py")
subprocess.call("python3 -m pytest " + tests_script, shell=True)