import shutil
import os
import re


def make_dirs(pathname):
    os.makedirs(pathname, exist_ok=True)


def copy_file(src, dst):
    shutil.copy2(src, dst)


def get_constant_files(path):
    """Метод возвращает tuple из изображений, которые соответствую изображениям в папке Constant"""
    lst = []
    if 'Constant' in os.listdir(path):
        lst = os.listdir(f'{path}/Constant')
    return tuple(name for name in lst if re.fullmatch(r'(\d+|cover)_\d+_pcs\.jpg', name))


class OrderBuckup:
    pass