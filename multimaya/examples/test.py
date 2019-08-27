import sys
import maya
import maya.standalone

def blah():
    maya.standalone.initialize()
    import maya.cmds as cmds
    print cmds.ls()
    print sys.path
    print 'blah'
    raise SystemExit(0)