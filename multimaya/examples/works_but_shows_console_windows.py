import sys
import time
import os
import multiprocessing


def worker():
    """worker function"""
    for n in range(5):
        print "waiting" + "." * n
        time.sleep(1)


if __name__ == '__main__':

    sys.executable = sys.executable.replace("maya.exe", "mayapy.exe")
    sys.exec_prefix = os.path.dirname(sys.executable)
    multiprocessing.set_executable(sys.executable)
    multiprocessing.freeze_support()
    jobs = []
    for i in range(5):
        p = multiprocessing.Process(target=worker)
        jobs.append(p)
        p.start()
        jobs.append(p)
    for j in jobs:
        j.join()
    print "done"
