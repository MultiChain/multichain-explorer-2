# -*- coding: utf-8 -*-

# MultiChain Explorer 2 (c) Coin Sciences Ltd
# All rights reserved under BSD 3-clause license


import sys
import os
import datetime
import json
import cfg
import struct
import signal
import string


def file_read_char(f):
    return ord(f.read(1))

def file_read_int32(f):
    return struct.unpack('i', f.read(4))[0]

def str_to_int8(data):
    return ord(data)

def bytes_to_int32(data):
    return struct.unpack('i', data)[0]

def bytes_to_int64(data):
    return struct.unpack('q', data)[0]

def bytes_to_hex(data):
    toHex = lambda x:''.join(format(c, '02x') for c in x)
    return toHex(data)

def print_error(msg):
    sys.stderr.write(msg + "\n")

def full_dir_name(dir_name):
    return str(dir_name).replace("~",os.path.expanduser("~")).rstrip("/") + "/";

def file_dir_name(file_name):
    return os.path.dirname(os.path.realpath(str(file_name).replace("~",os.path.expanduser("~")))).rstrip("/") + "/";

def file_file_name(file_name):
    return os.path.split(file_name)[1];

def log_write(data):
    return file_write(cfg.log_file,str(datetime.datetime.now()) + " " + str(data) + "\n",True)

def log_error(data):
    return log_write("ERROR: " + str(data))

def check_directory(dir_name):
    try:
        os.mkdir(dir_name)
    except:
        pass
    if not os.path.exists(dir_name):
        return False
    return True
    
def directory_exists(dir_name):
    if not os.path.exists(dir_name):
        return False
    return True    

def remove_file(file_name):
    try:
        os.remove(file_name)
    except:
        pass

def file_write(filename,data,append=False):
    mode="w"
    if append:
        mode="a"
    f = open(filename, mode)
    f.write(str(data))
    f.close
    return True

def file_read(filename):
    result=None
    if os.path.isfile(filename):
        f = open(filename, "r")
        result=f.read()
        f.close
    return result

def file_exists(filename):
    return os.path.isfile(filename)

def is_process_running(process_id):
    try:
        os.kill(process_id, 0)
        return True
    except OSError:
        return False

def kill_process(process_id):
    try:
        os.kill(process_id, signal.SIGKILL)
        return True
    except OSError:
        return False

def get_pid():
    return os.getpid()

def become_daemon():
    try:
        pid = os.fork()
    except OSError as e:
        print_error(e)
        os._exit(1)

    if pid == 0:
        os.setsid()

        try:
            pid = os.fork()
        except OSError as e:
            print_error(e)
            os._exit(1)

        if (pid == 0):
            os.chdir(file_dir_name(__file__))
            os.umask(0)
        else:
            os._exit(0)
    else:
        os._exit(0)

def read_file_ptr(config):
    current_ptr=file_read(config['ptr'])
    ptr = (0, 0)
    if current_ptr is not None:
        ptr_dict=json.loads(current_ptr)
        ptr=(ptr_dict["file"],ptr_dict["offset"])
        
    return ptr

def write_file_ptr(config,ptr):
    remove_file(config['ptr'])
    ptr_dict={"file":ptr[0],"offset":ptr[1]}
    return file_write(config['ptr'],json.dumps(ptr_dict))

def is_true(value):
    val=str(value).lower()
    if val == 'on':
        return True
    if val == 'yes':
        return True
    if val == 'true':
        return True
    return False

def is_printable(s):
    """
    Return True if the string is ASCII (with punctuation) and printable
    :param s:
    :return:
    """
    for c in s:
        if c not in string.printable:
            return False
    return True

