import os
import shutil
import subprocess


def remove_save_dir(dir_path):
    if os.path.exists(dir_path):
            shutil.rmtree(dir_path)


def run(command, wait=True):
    p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if wait:
        p.wait()
    return p