import sys
import time
import os
import multiprocessing
import maya.standalone
import maya.cmds as cmds

def worker(cmd):
    """worker function"""
    maya.standalone.initialize()
    do = getattr(maya.cmds, cmd)
    for n in range(10):
        do()

    return cmds.ls(type='mesh')

if __name__ == '__main__':
    try:
        maya.standalone.initialize()
    except:
        pass
    sys.executable = sys.executable.replace("maya.exe", "mayapy.exe")
    sys.exec_prefix = os.path.dirname(sys.executable)
    multiprocessing.set_executable(sys.executable)
    multiprocessing.freeze_support()
   
    p  = multiprocessing.Pool(4)
    print  p.map(worker, ['polyPlane', 'polySphere', 'polyCube'])
    