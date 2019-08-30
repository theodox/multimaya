import sys
import maya
import maya.standalone
import multiprocessing

def blah(*args):
    maya.standalone.initialize()
    import maya.cmds as cmds
    print sys.path
    print 'blah'
    print multiprocessing.current_process()
    return args[0] * -1


def fah(arg):
    maya.standalone.initialize()
    import maya.cmds as cmds
    return cmds.ls()