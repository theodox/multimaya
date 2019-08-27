import sys
import os


def maya_executable():
    """return the maya executable for this maya or mayapy"""
    process_path = sys.executable
    maya_dir = os.path.dirname(process_path)

    if os.name == 'nt':
        return os.path.join(maya_dir, 'maya.exe')
    else:
        # todo: OSX/Linux support
        raise NotImplemented()


def mayapy_executable():
    """return the mayapy executable for this maya or mayapy"""
    process_path = sys.executable
    maya_dir = os.path.dirname(process_path)

    if os.name == 'nt':
        return os.path.join(maya_dir, 'mayapy.exe')
    else:
        # todo: OSX/Linux support
        raise NotImplemented()


def in_mayapy():
    if os.name == 'nt':
        return os.path.join(maya_dir, 'mayapy.exe')
    else:
        # todo: OSX/Linux support
        raise NotImplemented()
