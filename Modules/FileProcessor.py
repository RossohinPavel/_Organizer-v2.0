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

    def __init__(self, order_dict, library, common_stg):
        print(order_dict)
        self.order_name = order_dict['NAME']
        self.object_list = tuple(self.__get_object_list(order_dict, library, common_stg))


    @staticmethod
    def __get_object_list(order_dict, library, common_stg):
        common_stg = {k: common_stg[k] for k in ('stroke_size', 'stroke_color', 'guideline_size', 'guideline_color')}
        for key, value in order_dict['CONTENTS'].items():
            counts, edition_type = value
            if edition_type is None or edition_type[1] == 'PHOTO':
                continue
            book_type, edition_type = edition_type
            obj, proc_stg = None, None
            if edition_type in ('Фотокнига Премиум', 'Фотокнига выпускника'):
                obj = FotobookEdition
                proc_stg = order_dict['TYPE']['fotobook']
            if edition_type in ('Фотокнига Flex Bind', 'Альбом и PUR'):
                obj = AlbumEdition
                proc_stg = order_dict['TYPE']['albums']
            if edition_type == 'Layflat':
                obj = PolibookEdition
                proc_stg = order_dict['TYPE']['polibook']
            if edition_type == 'Фотожурнал':
                obj = JournalEdition
                proc_stg = {}
            path = f'{order_dict["PATH"]}/{order_dict["NAME"]}'
            file_stg = library[book_type]
            file_stg.update(common_stg)
            yield obj(path, key, proc_stg, file_stg)


class Edition:
    __slots__ = 'path', 'name', 'proc_stg', 'file_stg'

    def __init__(self, path, name, proc_stg, file_stg):
        self.path = path
        self.name = name
        self.proc_stg = proc_stg
        self.file_stg = file_stg


class FotobookEdition(Edition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class PolibookEdition(Edition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class AlbumEdition(Edition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class JournalEdition(Edition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CanvasEdition(Edition):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)