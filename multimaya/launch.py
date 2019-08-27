import subprocess
import inspect
import tempfile
import os
import ast
import sys

from maya import maya_executable, mayapy_executable

SCRIPT_TEMPLATE = '''# multimaya launcher shim
import os
import {modname}
if __name__ == '__main__':
    {init}
    try:
        {funcname}()
        sys.exit(0)
    except:
        sys.exit(-1)
'''


def generate_wrapper(func, initialize=True, ):
    """
    Generates a minimal import-and-execute wrapper around <func>,
    which is assumed to be a no-argument callable
    """

    init = ''
    if initialize:
        init = 'import maya.standalone; maya.standalone.initialize()'

    modulename = inspect.getmodule(func).__name__
    return SCRIPT_TEMPLATE.format(modname=modulename, init=init, funcname=func.__name__)


def function_to_script(func, initialize=True, post_delete=True):

    with tempfile.NamedTemporaryFile(mode='wt', delete=False, suffix='.py') as filehandle:
        script_text = generate_wrapper(func)
        if post_delete:
            script_text += '    finally:\r\n'
            script_text += '        os.remove("{}")\r\n'.format(filehandle.name.replace("\\", "/"))

        filehandle.write(script_text)

    return filehandle.name


def launch_mayapy(func):

    script = function_to_script(func)
    arguments = [mayapy_executable(), script]
    subprocess.check_call(arguments, env={"PYTHONPATH": ";".join(sys.path)})

# test - remove
if __name__ == '__main__':
    import examples.test as t
    launch_mayapy(t.blah)
