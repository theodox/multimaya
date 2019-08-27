import subprocess
import inspect
import tempfile
import traceback
import os
import ast
import sys

from mayapy import mayapy_executable

SCRIPT_TEMPLATE = '''# multimaya launcher shim
import os
import sys
import traceback

__keep__ = {keep_script}

if __name__ == '__main__':
    try:
        import {modname}
        {modname}.{funcname}()
    except:
        with open("{filename}.crash", "wt") as handle:
            traceback.print_exc(None, handle)
        sys.exit(-1)

    if not __keep__:
        os.remove("{filename}")
    sys.exit(0)
'''


def generate_wrapper(func, filename, keep_script=False):
    """
    Generates a minimal import-and-execute wrapper around <func>,
    which is assumed to be a no-argument callable

    if 'keep_script' is True, don't delete the temp file after the run;
    otherwise try to delete it after a successful run
    """

    modulename = inspect.getmodule(func).__name__
    return SCRIPT_TEMPLATE.format(
        modname=modulename,
        funcname=func.__name__,
        filename=filename.replace('\\', '/'),
        keep_script=keep_script
    )


def function_to_script(func):
    """
    save a launcher script for <func> to a temporary file;
    return the name of the temporary file
    """
    with tempfile.NamedTemporaryFile(mode='wt', delete=False, suffix='.py') as filehandle:
        script_text = generate_wrapper(func, filehandle.name)

        filehandle.write(script_text)

    return filehandle.name


def launch_mayapy(func):

    script = function_to_script(func)
    arguments = [mayapy_executable(), script]
    env = os.environ.copy()
    env['PYTHONPATH'] = ";".join(sys.path)
    print subprocess.check_output(arguments, env=env)
    print script


# test - remove
if __name__ == '__main__':
    import examples.test as t
    launch_mayapy(t.blah)
