__author__ = 'Ahmed Gamal A. Ali'
import os
import shutil
import subprocess


def remove_save_dir(dir_path):
    """
    Removing the save directory contents if available.
    :param dir_path: path to the directory to be removed
    :return: None
    """
    if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


def run(command, wait=True):
    """
    Execute command line.
    :param command: The command line to be executed.
    :param wait: Bool value. If True, the program will be blocked until the execution is returned.
    If False, it will start the process as a background process
    :return: instance of subprocess.Popen
    """
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if wait:
        p.wait()
    return p