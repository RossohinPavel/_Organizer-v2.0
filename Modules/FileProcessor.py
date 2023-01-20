import shutil
import os


def make_dirs(pathname):
    os.makedirs(pathname, exist_ok=True)


def copy_file(src, dst):
    shutil.copy2(src, dst)