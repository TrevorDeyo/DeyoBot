# Starting the stopwatch
import time
start_time = time.time()

# function that prints with program execution time elasped added at the beginning
def print_time(string):
    global start_time
    elasped_time = int((time.time() - start_time) * 1000)
    print(f"{elasped_time}ms: {string}")

# imports
import os
print_time("import os done")
from git import Repo
print_time("from git import Repo done")

# Created Repo obj
repo = Repo(os.getcwd())
print_time("created Repo object using os.getcwd()")

# connect to the remote repository on github
origin = repo.remote()
print_time("connected to the remote repository on github")

# import datetime & drop microseconds
import datetime
print_time("Imported datetime & dropped microseconds")
yyyy_mm_dd_hh_mm_ss_ms = datetime.datetime.now()
yyyy_mm_dd_hh_mm_ss = yyyy_mm_dd_hh_mm_ss_ms.replace(microsecond=0)

# commit local changes using datename as name
repo.index.commit(str(yyyy_mm_dd_hh_mm_ss))
print_time("committed local changes using datename as name")

# push changes to github
origin.push()
print_time("Repository commits pushed to github")