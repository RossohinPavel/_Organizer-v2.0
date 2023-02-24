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
                file_list.append((catalog, catalog, file))
        self.file_list.append(file_list)

    def __get_ccv_files(self, path, content_name):
        file_list = []
        if content_name != 'PHOTO':
            content_path = f'{path}/{content_name}'
            for catalog in os.listdir(content_path):
                if catalog in ('Constant', 'Variable'):
                    working_dir = f'{content_name}/{catalog}'
                    for name in os.listdir(f'{content_path}/{catalog}'):
                        if re.fullmatch(r'\d{3}_(?:_\d{3}|\d{,3}_pcs)\.jpg', name):
                            self.dir_list.add(working_dir)
                            file_list.append((working_dir, working_dir, name))
                        if re.fullmatch(r'cover_(?:\d{3}|\d{,3}_pcs)\.jpg', name):
                            self.dir_list.add(f'{content_name}/Covers')
                            file_list.append((working_dir, f'{content_name}/Covers', name))
        else:
            for root, dirs, files in os.walk(f'{path}/{content_name}/_ALL'):
                for file in files:
                    catalog = os.path.relpath(root, path)
                    self.dir_list.add(catalog)
                    file_list.append((catalog, catalog, file))
        self.file_list.append(file_list)

    def __get_ex_files(self, path, content_name):
        file_list = []
        if content_name != 'PHOTO':
            content_path = f'{path}/{content_name}'
            for ex in os.listdir(content_path):
                if re.fullmatch(r'\d{3}(-\d{,3}_pcs)?', ex):
                    working_dir = f'{content_name}/{ex}'
                    self.dir_list.add(working_dir)
                    for file in os.listdir(f'{content_path}/{ex}'):
                        if re.fullmatch(r'(?:\d{3}_|cover)_\d{3}(-\d{,3}_pcs)?\.jpg', file):
                            file_list.append((working_dir, working_dir, file))
        else:
            for name in os.listdir(f'{path}/{content_name}'):
                if name != '_ALL':
                    for root, dirs, files in os.walk(f'{path}/{content_name}/{name}'):
                        for file in files:
                            catalog = os.path.relpath(root, path)
                            self.dir_list.add(catalog)
                            file_list.append((catalog, catalog, file))
        self.file_list.append(file_list)

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
            for f_src, f_dst, f_name in self.file_list[i]:
                yield self.order_name, f'{contents_len}/{i+1} -- {v}', f_name
                shutil.copy2(f'{src}/{f_src}/{f_name}', f'{src}/_TO_PRINT/{f_dst}/{f_name}')


class OrderSmartProcessor:
    __slots__ = 'object_list', 'order_name'

    def __init__(self, order_dict):
        self.order_name = order_dict['NAME']
        self.object_list = self.get_obj_list(order_dict)

    @staticmethod
    def get_obj_list(order_dict: dict) -> list:
        lst = []
        path = f'{order_dict["PATH"]}/{order_dict["NAME"]}'
        for content, value in order_dict['CONTENTS'].items():
            if value['category'] == 'photobook':
                lst.append(FotobookEdition(path, content, value, order_dict['PROC_STG']['photobook']))
            if value['category'] == 'layflat':
                lst.append(PolibookEdition(path, content, value, order_dict['PROC_STG']['layflat']))
            if value['category'] == 'album':
                lst.append(AlbumEdition(path, content, value, order_dict['PROC_STG']['album']))
            if value['category'] == 'journal':
                lst.append(JournalEdition(path, content, value))
            if value['category'] == 'photocanvas':
                lst.append(CanvasEdition(path, content, value))
        return lst

    def get_file_list(self):
        for obj in self.object_list:
            obj.get_file_list()

    def get_file_len(self):
        return sum(obj.get_file_len() for obj in self.object_list)

    def make_dirs(self):
        for path in set(y for x in self.object_list for y in x.get_new_dirs()):
            os.makedirs(path, exist_ok=True)

    def processing_run(self):
        pass


class Edition:
    __slots__ = 'path', 'name', 'file_stg', 'proc_stg', 'cover_list', 'pages_list'

    def __init__(self, path, name, file_stg, proc_stg=None):
        self.path = path
        self.name = name
        self.file_stg = file_stg
        self.proc_stg = proc_stg
        self.cover_list = None
        self.pages_list = None

    def get_file_list(self):
        pass

    def get_file_len(self):
        return 0

    def get_new_dirs(self):
        return []

    def get_covers(self):
        path = f'{self.path}/{self.name}'
        for catalog in os.listdir(path):
            if catalog in ('Constant', 'Variable'):
                for file in os.listdir(f'{path}/{catalog}'):
                    if re.fullmatch(r'cover_(?:\d{3}|\d{,3}_pcs|\d{3}-\d{,3}_pcs)\.jpg', file):
                        yield f'{path}/{catalog}', file


class FotobookEdition(Edition):
    pass


class PolibookEdition(Edition):
    pass


class AlbumEdition(Edition):
    pass


class JournalEdition(Edition):
    pass


class CanvasEdition(Edition):

    def get_file_list(self):
        self.cover_list = tuple(self.get_covers())

    def get_file_len(self):
        counter = 0
        for path, name in self.cover_list:
            if re.fullmatch(r'cover_\d{3}\.jpg', name):
                counter += 1
            if re.fullmatch(r'cover_\d{,3}_pcs\.jpg', name):
                counter += int(name.split('_')[1])
            if re.fullmatch(r'cover_\d{3}-\d{,3}_pcs\.jpg', name):
                counter += int(re.split(r'[-_]', name)[2])
        return counter

    def get_new_dirs(self):
        return f'{self.path}/_TO_PRINT',
