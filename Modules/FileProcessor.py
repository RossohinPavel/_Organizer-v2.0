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
    __slots__ = 'path', 'order_name', 'contents', 'type_of_proc', 'dir_list', 'file_list'

    def __init__(self, order_dict):
        self.path = order_dict['PATH']
        self.order_name = order_dict['NAME']
        self.type_of_proc = order_dict['TYPE']
        self.contents = tuple(order_dict['CONTENTS'].keys())
        self.dir_list = set()
        self.file_list = []

    def get_file_list(self):
        order_path = f'{self.path}/{self.order_name}'
        for name in self.contents:
            if self.type_of_proc == 'ALL':
                self.__get_all_files(order_path, name)
            if self.type_of_proc == 'CCV':
                self.__get_ccv_files(order_path, name)
            if self.type_of_proc == 'EX':
                self.__get_ex_files(order_path, name)

    def __get_all_files(self, path, content_name):
        file_list = []
        for root, dirs, files in os.walk(f'{path}/{content_name}'):
            for file in files:
                catalog = os.path.relpath(f'{root}', path)
                self.dir_list.add(catalog)
                file_list.append((catalog, file))
        self.file_list.append(tuple(file_list))

    def __get_ccv_files(self, path, content_name):
        file_list = []
        if content_name != 'PHOTO':
            content_path = f'{path}/{content_name}'
            for catalog in os.listdir(content_path):
                if catalog in ('Covers', 'Variable', 'Constant'):
                    self.dir_list.add(f'{content_name}/{catalog}')
                if catalog == 'Covers':
                    for name in os.listdir(f'{content_path}/{catalog}'):
                        file_list.append((f'{content_name}/{catalog}', name))
                if catalog in ('Constant', 'Variable'):
                    for name in os.listdir(f'{content_path}/{catalog}'):
                        if re.fullmatch(r'\d{3}_(?:_\d{3}|\d{,3}_pcs)\.jpg', name):
                            file_list.append((f'{content_name}/{catalog}', name))
        else:
            for root, dirs, files in os.walk(f'{path}/{content_name}/_ALL'):
                for file in files:
                    catalog = os.path.relpath(root, path)
                    self.dir_list.add(catalog)
                    file_list.append((catalog, file))
        self.file_list.append(tuple(file_list))

    def __get_ex_files(self, path, content_name):
        file_list = []
        if content_name != 'PHOTO':
            content_path = f'{path}/{content_name}'
            for ex in os.listdir(content_path):
                if re.fullmatch(r'\d{3}(-\d{,3}_pcs)?', ex):
                    self.dir_list.add(f'{content_name}/{ex}')
                    for file in os.listdir(f'{content_path}/{ex}'):
                        if re.fullmatch(r'(?:\d{3}_|cover)_\d{3}(-\d{,3}_pcs)?\.jpg', file):
                            file_list.append((f'{content_name}/{ex}', file))
        else:
            for name in os.listdir(f'{path}/{content_name}'):
                if name != '_ALL':
                    for root, dirs, files in os.walk(f'{path}/{content_name}/{name}'):
                        for file in files:
                            catalog = os.path.relpath(root, path)
                            self.dir_list.add(catalog)
                            file_list.append((catalog, file))
        self.file_list.append(tuple(file_list))

    def get_file_len(self) -> int:
        return sum(len(x) for x in self.file_list)

    def make_dirs(self):
        dst = f'{self.path}/{self.order_name}/_TO_PRINT'
        for name in sorted(self.dir_list, key=len):
            os.makedirs(f'{dst}/{name}', exist_ok=True)

    def processing_run(self):
        src = f'{self.path}/{self.order_name}'
        contents_len = len(self.contents)
        for i, v in enumerate(self.contents):
            for f_path, f_name in self.file_list[i]:
                yield self.order_name, f'{contents_len}/{i+1} -- {v}', f_name
                shutil.copy2(f'{src}/{f_path}/{f_name}', f'{src}/_TO_PRINT/{f_path}/{f_name}')
