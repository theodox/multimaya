import subprocess
import inspect
import tempfile
import traceback
import os
import sys
import types
import multiprocessing
import pickle

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


PROC_TEMPLATE = '''# multimaya launcher shim
import os
import sys
import traceback
import multiprocessing

__keep__ = {keep_script}


sys.executable = sys.executable.replace("maya.exe", "mayapy.exe")
sys.exec_prefix = os.path.dirname(sys.executable)
multiprocessing.set_executable(sys.executable)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        import {modname}
        proc = multiprocessing.Process(target={modname}.{funcname}, args={args}, kwargs={kwargs})
        proc.start()
        proc.join()
        print ("DONE")
    except:
        with open("{filename}.crash", "wt") as handle:
            traceback.print_exc(None, handle)
        sys.exit(-1)

    if not __keep__:
        os.remove("{filename}")
    sys.exit(0)
'''


def generate_proc(func, filename, keep_script, *args, **kwargs):

    modulename = inspect.getmodule(func).__name__

    return PROC_TEMPLATE.format(
        modname=modulename,
        funcname=func.__name__,
        filename=filename.replace('\\', '/'),
        args=args,
        kwargs=kwargs,
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


def function_to_proc(func, *args, **kwargs):
    """
    save a multiprocessing-compatible script to a te
    """
    with tempfile.NamedTemporaryFile(mode='wt', delete=False, suffix='.py') as filehandle:
        script_text = generate_proc(func, filehandle.name, True, *args, **kwargs)
        filehandle.write(script_text)

    return filehandle.name


def launch_mayapy(func):

    script = function_to_script(func)
    arguments = [mayapy_executable(), script]
    env = os.environ.copy()
    env['PYTHONPATH'] = ";".join(sys.path)
    print subprocess.check_output(arguments, env=env)
    print script


def mayapy_process(func, *args, **kwargs):
    proc = function_to_proc(func, *args, **kwargs)
    arguments = [mayapy_executable(), proc]
    env = os.environ.copy()
    env['PYTHONPATH'] = ";".join(sys.path)
    print subprocess.check_output(arguments, env=env)
    print proc


POOL_TEMPLATE = '''# multimaya launcher shim
import os
import sys
import traceback
import multiprocessing
import pickle
import {modname}

__keep__ = {keep_script}

sys.executable = sys.executable.replace("maya.exe", "mayapy.exe")
sys.exec_prefix = os.path.dirname(sys.executable)
multiprocessing.set_executable(sys.executable)

def pool_func(arg):
    return {modname}.{funcname}(arg)

if __name__ == '__main__':
    multiprocessing.freeze_support()
    try:
        pool = multiprocessing.Pool({poolsize})
        print pickle.dumps(pool.map(pool_func, {arglist}))  
    except:
        with open("{filename}.crash", "wt") as handle:
            traceback.print_exc(None, handle)
        sys.exit(-1)

    if not __keep__:
        os.remove("{filename}")
    sys.exit(0)
'''


def generate_pool(func, filename, keep_script, *arglist, **kwargs):

    poolsize = kwargs.get('processes', 4)
    modulename = inspect.getmodule(func).__name__

    return POOL_TEMPLATE.format(
        modname=modulename,
        funcname=func.__name__,
        filename=filename.replace('\\', '/'),
        arglist=arglist,
        poolsize=poolsize,
        keep_script=keep_script
    )


def function_to_pool(func, *arglist, **kwargs):
    with tempfile.NamedTemporaryFile(mode='wt', delete=False, suffix='.py') as filehandle:
        script_text = generate_pool(func, filehandle.name, True, *arglist, **kwargs)
        filehandle.write(script_text)
    return filehandle.name


def mayapy_pool(func, *args, **kwargs):
    proc = function_to_pool(func, *args, processes=4)
    arguments = [mayapy_executable(), proc]
    env = os.environ.copy()
    env['PYTHONPATH'] = ";".join((str(i) for i in sys.path))
    result = subprocess.check_output(arguments, env=env)
    return pickle.loads(result[:-2], encoding='utf-8')


