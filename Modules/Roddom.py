import re
import os
import Modules.Configs as Conf


class RoddomFormat:
    """Класс для описания отдельных фото"""
    __slots__ = 'sub_name', 'photo_lst', 'page_format', 'main_path', 'mrk_exist'

    @staticmethod
    def main(main_path, form):
        path = f'{main_path}/{form}'
        for i in os.listdir(path):
            if i.endswith('.jpg'):
                yield i

    @staticmethod
    def get_mrk_header() -> list:
        lst = ['[HDR]',
               'GEN REV = 01.00',
               'GEN CRT = "NORITSU KOKI" -01.00',
               'GEN DTM = 1899:12:30:00:00:00',
               'USR NAM = ""',
               'USR TEL = ""',
               'VUQ RGN = BGN',
               'VUQ VNM = "NORITSU KOKI" -ATR "QSSPrint"',
               'VUQ VER = 01.00',
               'GEN INP = "OTHER"',
               'VUQ RGN = END'
               ]
        return lst

    @staticmethod
    def get_mrk_job_cell(num, path, name, name_wo_format, sub, page_format) -> list:
        lst = ['',
               '[JOB]',
               f'PRT PID = {num}',
               'PRT TYP=STD',
               'PRT QTY = 1',
               'IMG FMT = EXIF2 -J',
               f'<IMG SRC = "./{path}">',
               f'IMG FLD = {name}',
               'VUQ RGN = BGN',
               'VUQ VNM = "NORITSU KOKI" -ATR "QSSPrint"',
               'VUQ VER = 01.00',
               f'PRT CVP1 = 1 -STR "{name_wo_format}  {num}"',
               f'PRT CVP2 = 1 -STR "{sub}__{page_format}  www.fotoknigioptom.ru"',
               'VUQ RGN = END'
               ]
        return lst

    def __init__(self, main_path, page_format, sub_name):
        self.photo_lst = tuple(self.main(main_path, page_format))
        self.main_path = main_path
        self.sub_name = sub_name
        self.page_format = page_format
        self.mrk_exist = None

    def create_mrk(self):
        mrk = self.get_mrk_header()
        for i in range(1, len(self.photo_lst)+1):
            num = str(i).rjust(3, '0')
            name = self.photo_lst[i-1]
            name_wo_format = name[:-4]
            path = f'{self.page_format}/{name}'
            mrk.extend(self.get_mrk_job_cell(num, path, name, name_wo_format, self.sub_name, self.page_format))
        mrk_name = f'{self.sub_name}__{self.page_format}__gloss.mrk'
        self.mrk_exist = mrk_name
        Conf.write_txt_from_list(f'{self.main_path}/{mrk_name}', mrk)

    def __str__(self):
        return self.page_format

    def __len__(self):
        return len(self.photo_lst)


class RoddomSub:
    """Класс для управления отдельной выпиской"""
    __slots__ = 'sub', 'format_lst'

    def __init__(self, main_path, sub):
        self.sub = sub
        self.format_lst = tuple(self.main(main_path, sub))

    @staticmethod
    def main(main_path, sub):
        path = f'{main_path}/{sub}'
        for form in os.listdir(path):
            if re.fullmatch(r'15x21|21x30|9x15', form):
                yield RoddomFormat(path, form, sub)

    def __str__(self):
        return self.sub


class RoddomOrder:
    """Класс для подсчета и управления одиночным заказом роддома"""
    __slots__ = 'sub_lst', 'order_name', 'total_sum'

    def __init__(self, path, txt=False, mrc=False):
        self.order_name = path.split('/')[-1]
        self.sub_lst = tuple(RoddomSub(path, x) for x in os.listdir(path) if os.path.isdir(f'{path}/{x}'))
        self.total_sum = self.get_total_sum(mrc)
        if txt:
            Conf.write_txt(f'{path}/{self.order_name} - sum.txt', str(self))

    def __str__(self):
        return self.get_order_string_info()

    def get_order_string_info(self) -> str:
        string = self.order_name + '\n' + ' ' * 4
        string += '\n    '.join(f'{str(k).ljust(5, " ")} - {v}' for k, v in self.total_sum.items())
        return string

    def get_total_sum(self, mrc) -> dict:
        dct = {}
        for sub in self.sub_lst:
            for form in sub.format_lst:
                key = str(form)
                if not dct.get(key):
                    dct[key] = 0
                dct[key] += len(form)
                if mrc:
                    form.create_mrk()
        return {k: dct[k] for k in sorted(dct.keys(), key=len)}

    def get_directory_list(self) -> tuple:
        return tuple(f'{self.order_name}/{sub}/{form}' for sub in self.sub_lst for form in sub.format_lst)

    def get_file_list(self) -> tuple:
        def generator():
            for sub in self.sub_lst:
                for form in sub.format_lst:
                    if form.mrk_exist:
                        yield f'{self.order_name}/{sub}/{form.mrk_exist}'
                    for page in form.photo_lst:
                        yield f'{self.order_name}/{sub}/{form}/{page}'
        return tuple(x for x in generator())
