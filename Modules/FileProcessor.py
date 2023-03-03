import shutil
import os
import re

from PIL import Image, ImageDraw, ImageFont


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
    __slots__ = 'object_list', 'order_name', 'path'

    def __init__(self, order_dict):
        self.order_name = order_dict['NAME']
        self.path = order_dict["PATH"]
        self.object_list = self.get_obj_list(order_dict)

    @staticmethod
    def get_obj_list(order_dict: dict) -> list:
        lst = []
        path = f'{order_dict["PATH"]}/{order_dict["NAME"]}'
        for ind, val in enumerate(order_dict['CONTENTS'].items(), 1):
            content, value = val
            if value['category'] == 'photobook':
                lst.append(FotobookEdition(path, content, ind, value, order_dict['PROC_STG']['photobook']))
            if value['category'] == 'layflat':
                lst.append(PolibookEdition(path, content, ind, value, order_dict['PROC_STG']['layflat']))
            if value['category'] == 'album':
                lst.append(AlbumEdition(path, content, ind, value, order_dict['PROC_STG']['album']))
            if value['category'] == 'journal':
                lst.append(JournalEdition(path, content, ind, value))
            if value['category'] == 'photocanvas':
                lst.append(CanvasEdition(path, content, ind, value))
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
        self.__mrk_deleting()
        for obj in self.object_list:
            edition = obj.name
            for file in obj.processing_run():
                yield self.order_name, edition, file

    def __mrk_deleting(self):
        for element in os.listdir(f'{self.path}/{self.order_name}/_TO_PRINT'):
            if re.fullmatch(r'\d{,3}\.mrk', element):
                os.remove(f'{self.path}/{self.order_name}/_TO_PRINT/{element}')


class Exemplar:
    __slots__ = 'name', 'img_list', 'comp_list'

    def __init__(self, name, img_list, comp_list):
        self.name = name
        self.img_list = img_list
        self.comp_list = comp_list

    def __len__(self):
        return len(self.img_list) - 1

    def get_cover(self):
        return self.img_list[-1]

    def get_pages(self):
        return self.img_list[:-1]

    def get_var_pages(self):
        return tuple(self.img_list[i] for i in range(len(self.img_list) - 1) if self.comp_list[i] == 'v')


class Edition:
    __slots__ = 'path', 'name', 'index', 'file_stg', 'proc_stg', 'cover_lst', 'const_lst', 'var_lst', 'reserved'
    DIR_PAT = r'\d{3}(-\d{,3}_pcs)?'
    VAR_IMG_PAT = r'(?:\d{3}_|cover)_\d{3}(-\d{,3}_pcs)?\.jpg'
    CONST_IMG_PAT = r''
    VAR_COV_PAT = r'cover_\d{3}(-\d{,3}_pcs)?\.jpg'
    CONST_COV_PAT = r'cover_\d{,3}_pcs\.jpg'
    VAR_P_PAT = r''
    CONST_P_PAT = r'\d{3}_\d{,3}_pcs\.jpg'

    @staticmethod
    def mm_to_pixel(value: int) -> int:
        return int(value * 11.808)

    def __init__(self, path, name, index, file_stg, proc_stg=None):
        self.path = path
        self.name = name
        self.index = index
        self.file_stg = file_stg
        self.proc_stg = proc_stg
        self.cover_lst = None
        self.const_lst = None
        self.var_lst = None
        self.reserved = None

    def get_file_list(self):
        path = f'{self.path}/{self.name}'
        var_img = tuple(x for x in self.__get_variables())
        for ex_dir in (x for x in os.listdir(path) if re.fullmatch(self.DIR_PAT, x)):
            img_list = tuple(x for x in os.listdir(f'{path}/{ex_dir}') if re.fullmatch(self.VAR_IMG_PAT, x))
            comp_list = tuple('v' if x in var_img else 'c' for x in img_list)
            yield Exemplar(ex_dir, img_list, comp_list)

    def get_file_len(self):
        return 0

    def get_new_dirs(self):
        return []

    def processing_run(self):
        return []

    def __get_variables(self):
        path = f'{self.path}/{self.name}'
        for var_dir in (x for x in os.listdir(path) if x == 'Variable'):
            yield from (x for x in os.listdir(f'{path}/{var_dir}') if re.fullmatch(self.VAR_IMG_PAT, x))

    def get_constant_img(self, pattern: str):
        path = f'{self.path}/{self.name}'
        for const_dir in (x for x in os.listdir(path) if x == 'Constant'):
            yield from (x for x in os.listdir(f'{path}/{const_dir}') if re.fullmatch(pattern, x))

    def get_book_file_list(self, ex_obj):
        combination = self.file_stg['combination']
        path = f'{self.path}/{self.name}'
        if combination == 'Копии' or combination is None:
            ex = ex_obj[0]
            ex_path, ex_len = f'{path}/{ex.name}', len(ex)
            self.cover_lst = (ex_path, ex.get_cover(), ex_len),
            self.var_lst = tuple((ex_path, img, ex_len) for img in ex.get_pages())
        if combination in ('В_О', 'О_О', 'Индивидуально'):
            self.const_lst = tuple((f'{path}/Constant', img) for img in self.get_constant_img(self.CONST_P_PAT))
        if combination == 'В_О':
            const_len = len(self.const_lst)
            self.cover_lst = tuple((f'{path}/{ex.name}', ex.get_cover(), const_len) for ex in ex_obj)
        if combination == 'О_О':
            max_spn = max(len(ex) for ex in ex_obj)
            self.var_lst = tuple((f'{path}/{ex.name}', img, len(ex)) for ex in ex_obj for img in ex.get_var_pages())
            self.cover_lst = tuple((f'{path}/Constant', x, max_spn) for x in self.get_constant_img(self.CONST_COV_PAT))
        if combination == 'Индивидуально':
            self.var_lst = tuple((f'{path}/{ex.name}', img, len(ex)) for ex in ex_obj for img in ex.get_var_pages())
            self.cover_lst = tuple((f'{path}/{ex.name}', ex.get_cover(), len(ex)) for ex in ex_obj)

    @staticmethod
    def cover_processing(src_p, src_n, dst_p, dst_n, **kwargs):
        with Image.open(f'{src_p}/{src_n}') as cover_image:
            cover_image.load()
        draw = ImageDraw.Draw(cover_image)  # Инициализация объекта для рисования
        rec_x, rec_y = cover_image.width, cover_image.height    # Получаем размер обложки
        gl_color = kwargs.get('guideline_color', '#000000')     # Инициализация общих переменных
        gl_size = kwargs.get('guideline_size', 4)
        gl_spine = Edition.mm_to_pixel(kwargs.get('gl_value', 0))   # Сразу переводим в пиксели
        gl_length = Edition.mm_to_pixel(kwargs.get('gl_length', 0))
        if kwargs.get('stroke', False):     # Прорисовка обводки
            draw.rectangle((0, 0, rec_x, rec_y), outline=kwargs['stroke_color'], width=kwargs['stroke_size'])
        if kwargs.get('guideline', False) and kwargs.get('book_type', False) in ('Книга', 'Люкс'):  # Направляющие
            draw.line((gl_spine, 0, gl_spine, gl_length), fill=gl_color, width=gl_size)
            draw.line((rec_x - gl_spine, 0, rec_x - gl_spine, gl_length), fill=gl_color, width=gl_size)
            draw.line((gl_spine, rec_y, gl_spine, rec_y - gl_length), fill=gl_color, width=gl_size)
            draw.line((rec_x - gl_spine, rec_y, rec_x - gl_spine, rec_y - gl_length), fill=gl_color, width=gl_size)
        if kwargs.get('guideline', False) and kwargs.get('book_type', False) == 'Люкс':     # Направляющие для Люкс
            draw.line((gl_spine - 590, 0, gl_spine - 590, rec_y), fill=gl_color, width=gl_size)
            draw.line((rec_x - gl_spine + 590, 0, rec_x - gl_spine + 590, rec_y), fill=gl_color, width=gl_size)
        if kwargs.get('guideline', False) and kwargs.get('book_type', False) == 'Кожаный корешок':
            draw.line((rec_x // 2 - 1, 0, rec_x // 2 - 1, rec_y), fill=gl_color, width=gl_size)
        if kwargs.get('add backprint', False):
            new_name = kwargs['bp_text']
            back_print = Image.new('RGB', (len(new_name) * 21, 50), 'white')  # Рисуем задник для бекпринта
            draw_text = ImageDraw.Draw(back_print)  # Определяем объект для текста
            draw_text.text((20, 0), text=new_name, font=ImageFont.truetype("arial.ttf", 40), fill="black")   # Текст
            rotated_back_print = back_print.rotate(90, expand=True)     # Поворачиваем задник
            bp_x, bp_y = back_print.width, back_print.height    # Получаем размеры бекпринта
            bp_pos_x = rec_x - gl_spine # Вставляем бэкпринт на исходное изображение
            cover_image.paste(back_print, (bp_pos_x, rec_y - bp_y))
            cover_image.paste(rotated_back_print, (rec_x - bp_y, int((rec_y / 2) - (bp_x / 2))))
        cover_image.save(f'{dst_p}/{dst_n}', quality='keep', dpi=(300, 300))



class FotobookEdition(Edition):
    def get_file_list(self):
        self.get_book_file_list(tuple(super().get_file_list()))

    def get_file_len(self):
        return sum(len(lst) for lst in (self.cover_lst, self.const_lst, self.var_lst) if lst)

    def get_new_dirs(self):
        lst = [f'{self.path}/_TO_PRINT/{self.name}/{self.file_stg["cover_canal"]}']
        if self.const_lst:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/{self.file_stg["page_canal"]}_Constant')
        if self.var_lst:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/{self.file_stg["page_canal"]}_Variable')
        return tuple(lst)

    def processing_run(self):
        self.reserved = {}
        option = {"б/у": 'bu', "с/у": 'cu', "с/у1.2": 'cu1_2'}[self.file_stg["book_option"]]
        book_type = self.file_stg['book_type']
        rename = self.proc_stg['rename']
        cover_canal, page_canal = self.file_stg["cover_canal"], self.file_stg["page_canal"]
        cov_path = f'{self.path}/_TO_PRINT/{self.name}/{cover_canal}'
        order_name = self.path.split('/')[-1]
        for src_path, src_file, ex_len in self.cover_lst:
            yield src_file
            c_name = f'{self.index}_{src_file[:-4]}_{ex_len}{option}.jpg' if rename else src_file
            if book_type in ('Кожаная обложка', 'Планшет'):
                shutil.copy2(f'{src_path}/{src_file}', f'{cov_path}/{c_name}')
            else:
                bp = {}
                if self.proc_stg.get('add backprint', False):
                    bp = {'bp_text': f'{order_name} - {c_name}'}
                self.cover_processing(src_path, src_file, cov_path, c_name, **self.file_stg, **self.proc_stg, **bp)
                self.reserved.setdefault(cover_canal, []).append((f'{self.name}/{cover_canal}', c_name))
        if self.const_lst:
            const_path = f'{self.path}/_TO_PRINT/{self.name}/{page_canal}_Constant'
            for src_path, src_file in self.const_lst:
                yield src_file
                p_name = f'{self.index}_{src_file[:-4]}_{option}.jpg' if rename else src_file
                shutil.copy2(f'{src_path}/{src_file}', f'{const_path}/{p_name}')
                self.reserved.setdefault(page_canal, []).append((page_canal, f'{self.name}/{page_canal}_Constant', p_name))
        if self.var_lst:
            var_path = f'{self.path}/_TO_PRINT/{self.name}/{page_canal}_Variable'
            for src_path, src_file, ex_len in self.var_lst:
                yield src_file
                p_name = f'{self.index}_{src_file[:-4]}_{ex_len}{option}.jpg' if rename else src_file
                shutil.copy2(f'{src_path}/{src_file}', f'{var_path}/{p_name}')
                self.reserved.setdefault(page_canal, []).append((page_canal, f'{self.name}/{page_canal}_Variable', p_name))
        # if self.proc_stg['generate .mrk']:
        #     self.create_mrk()

    def create_mrk(self):
        file_list = os.listdir(f'{self.path}/_TO_PRINT')
        cover_canal = self.file_stg['cover_canal']
        if cover_canal not in ('POLI', 'ORAJET'):
            with open(f'{self.path}/_TO_PRINT/{cover_canal}.mrk', 'a') as file:
                if f'{cover_canal}.mrk' not in file_list:
                    file.writelines(x + '\n' for x in self.get_mrk_header())
        self.get_mrk_file_list()

    @staticmethod
    def get_mrk_header():
        header = ('[HDR]', 'GEN REV = 01.00', 'GEN CRT = "NORITSU KOKI" -01.00', 'GEN DTM = 1899:12:30:00:00:00',
                  'USR NAM = ""', 'USR TEL = ""', 'VUQ RGN = BGN', 'VUQ VNM = "NORITSU KOKI" -ATR "QSSPrint"',
                  'VUQ VER = 01.00', 'GEN INP = "OTHER"', 'VUQ RGN = END')
        return header

    @staticmethod
    def get_mrk_body(num, qty, path, name, order_name, edition):
        body = ('', '[JOB]', f'PRT PID = {num}', 'PRT TYP=STD', f'PRT QTY = {qty}', 'IMG FMT = EXIF2 -J',
                f'<IMG SRC = "./{path}">', f'IMG FLD = {name}', 'VUQ RGN = BGN',
                'VUQ VNM = "NORITSU KOKI" -ATR "QSSPrint"', 'VUQ VER = 01.00',
                f'PRT CVP1 = 1 -STR "{order_name}  {edition}"',
                f'PRT CVP2 = 1 -STR "{name}  {num}  www.fotoknigioptom.ru"', 'VUQ RGN = END')
        return body

    def get_mrk_file_list(self):
        order_name = self.path.split('/')[-1]
        print(order_name)
        for canal, lst in self.reserved.items():
            for i, val in enumerate(lst, 1):
                rel_path, img = val
                if re.fullmatch(r'(?:cover|\d{3}_)_\d{3}\.jpg', img):
                    pass
                    # yield self.get_mrk_body(i, 1, rel_path, img, order_name, self.index)
                if re.fullmatch(r'(?:cover|\d{3}_)_\d{3}-\d{,3}_pcs\.jpg', img):
                    print(img)




class PolibookEdition(Edition):
    def get_file_list(self):
        self.get_book_file_list(tuple(super().get_file_list()))

    def get_file_len(self):
        return sum(len(lst) for lst in (self.cover_lst, self.const_lst, self.var_lst) if lst)

    def get_new_dirs(self):
        lst = [f'{self.path}/_TO_PRINT/{self.name}/Covers']
        if self.const_lst:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/Constant')
        if self.var_lst:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/Variable')
        return tuple(lst)

    def processing_run(self):
        option = {"б/у": 'бу', "с/у": 'су', "с/у1.2": 'су1_2'}[self.file_stg["book_option"]]
        book_type = self.file_stg['book_type']
        rename = self.proc_stg['rename']
        cover_path = f'{self.path}/_TO_PRINT/{self.name}/Covers'
        for src_path, src_file, ex_len in self.cover_lst:
            yield src_file
            c_name = f'{self.index}_{src_file[:-4]}_{ex_len}{option}.jpg' if rename else src_file
            if book_type in ('Кожаная обложка', 'Планшет'):
                shutil.copy2(f'{src_path}/{src_file}', f'{cover_path}/{c_name}')
            else:
                self.cover_processing(src_path, src_file, cover_path, c_name, **self.file_stg, **self.proc_stg)
        if self.const_lst:
            for src_path, src_file in self.const_lst:
                yield src_file
                p_name = f'{self.index}_{src_file[:-4]}_{option}.jpg' if rename else src_file
                shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/Constant/{p_name}')
        if self.var_lst:
            for src_path, src_file, ex_len in self.var_lst:
                yield src_file
                p_name = f'{self.index}_{src_file[:-4]}_{ex_len}{option}.jpg' if rename else src_file
                shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/Variable/{p_name}')


class AlbumEdition(Edition):
    def get_file_list(self):
        self.get_album_file_list(tuple(super().get_file_list()))

    def get_album_file_list(self, ex_obj):
        combination = self.file_stg['combination']
        path = f'{self.path}/{self.name}'
        if combination == 'О_О':
            max_spn = max(len(ex) for ex in ex_obj)
            self.cover_lst = tuple((f'{path}/Constant', x, max_spn) for x in self.get_constant_img(self.CONST_COV_PAT))
        else:
            self.cover_lst = tuple((f'{path}/{ex.name}', ex.get_cover(), len(ex)) for ex in ex_obj)
        if combination == 'В_О':
            ex = ex_obj[0]
            self.var_lst = tuple((f'{path}/{ex.name}', img) for img in ex.get_pages()),
        else:
            self.var_lst = tuple(tuple((f'{path}/{ex.name}', img) for img in ex.get_pages()) for ex in ex_obj)

    def get_file_len(self):
        file_len = len(self.cover_lst) + sum(len(x) for x in self.var_lst)
        if self.file_stg['dc_break']:
            file_len += len(self.var_lst)
        return file_len

    def get_new_dirs(self):
        cover_dir = f'{self.path}/_TO_PRINT/{self.name}/Covers',
        lst = tuple(f'{self.path}/_TO_PRINT/{self.name}/{len(ex)}p_{ex[0][0].split("/")[-1]}' for ex in self.var_lst)
        return cover_dir + lst

    def processing_run(self):
        rename, gl_need = self.proc_stg['rename'], self.proc_stg['guideline']
        cover_path = f'{self.path}/_TO_PRINT/{self.name}/Covers'
        for src_path, src_file, ex_len in self.cover_lst:
            yield src_file
            c_name = f'{self.index}_{src_file[:-4]}_{ex_len}p.jpg' if rename else src_file
            if gl_need:
                self.cover_processing(src_path, src_file, cover_path, c_name, **self.file_stg, **self.proc_stg)
            else:
                shutil.copy2(f'{src_path}/{src_file}', f'{cover_path}/{c_name}')
        for ex in self.var_lst:
            pages_len = f'{len(ex)}p_'
            old_name = ex[0][0].split('/')[-1]
            new_path = f'{self.path}/_TO_PRINT/{self.name}/{pages_len}{old_name}'
            text = f'{self.path[-6:]} - {self.name[:20]} - {old_name}'
            if self.file_stg['dc_break']:
                for file in self.break_decoding(ex, new_path, text, **self.file_stg):
                    yield file
            else:
                for file in self.album_decoding(ex, new_path, text, **self.file_stg):
                    yield file

    @staticmethod
    def album_decoding(file_list, dst_p, text, **kwargs):
        pages_count = 1
        white_image = Image.new('RGB', (2400, 2400), 'white')
        top_white_image = white_image.copy()
        draw_text = ImageDraw.Draw(top_white_image)
        draw_text.text((235, 2125), text=text, fill="#9a9a9a", font=ImageFont.truetype("arial.ttf", 80))
        top_white_image.save(f'{dst_p}/page{pages_count}.jpg', quality=100, dpi=(300, 300))
        top_white_image.close()
        overlap = Edition.mm_to_pixel(kwargs['dc_overlap'])
        top_ind = Edition.mm_to_pixel(kwargs['dc_top_indent'])
        left_ind = Edition.mm_to_pixel(kwargs['dc_left_indent'])
        for path, page in file_list:
            yield page
            with Image.open(f'{path}/{page}') as spread_img:
                spread_img.load()
            l_side = spread_img.crop((0, 0, spread_img.width // 2 + overlap, spread_img.height))
            r_side = spread_img.crop((spread_img.width // 2 - overlap, 0, spread_img.width, spread_img.height))
            spread_img.close()
            if left_ind > 0 or top_ind > 0:
                new_l_side = Image.new('RGB', (l_side.width + left_ind, l_side.height + top_ind), 'white')
                new_l_side.paste(l_side, (0, top_ind))
                l_side.close()
                l_side = new_l_side
                new_r_side = Image.new('RGB', (r_side.width + left_ind, r_side.height + top_ind), 'white')
                new_r_side.paste(r_side, (left_ind, top_ind))
                r_side.close()
                r_side = new_r_side
            pages_count += 2
            l_side.save(f'{dst_p}/page{pages_count - 1}.jpg', quality=100, dpi=(300, 300))
            r_side.save(f'{dst_p}/page{pages_count}.jpg', quality=100, dpi=(300, 300))
            l_side.close()
            r_side.close()
        white_image.save(f'{dst_p}/page{pages_count + 1}.jpg', quality=100, dpi=(300, 300))
        white_image.close()

    @staticmethod
    def break_decoding(file_list, dst_p, text, **kwargs):
        pages_list = []
        white_image = Image.new('RGB', (2400, 2400), 'white')
        draw_text = ImageDraw.Draw(white_image)
        draw_text.text((235, 2125), text=text, fill="#9a9a9a", font=ImageFont.truetype("arial.ttf", 80))
        pages_list.append(white_image)
        overlap = Edition.mm_to_pixel(kwargs['dc_overlap'])
        top_ind = Edition.mm_to_pixel(kwargs['dc_top_indent'])
        left_ind = Edition.mm_to_pixel(kwargs['dc_left_indent'])
        for path, page in file_list:
            yield f'Creating objects {page}'
            with Image.open(f'{path}/{page}') as spread_img:
                spread_img.load()
            l_crop = spread_img.crop((0, 0, spread_img.width // 2 + overlap, spread_img.height))
            r_crop = spread_img.crop((spread_img.width // 2 - overlap, 0, spread_img.width, spread_img.height))
            spread_img.close()
            l_side = Image.new('RGB', (spread_img.width // 2 + left_ind + overlap, spread_img.height + top_ind),
                               'white')
            r_side = l_side.copy()
            l_side.paste(l_crop, (0, top_ind))
            l_crop.close()
            pages_list.append(l_side)
            r_side.paste(r_crop, (left_ind, top_ind))
            r_crop.close()
            pages_list.append(r_side)
        pages_list.append(Image.new('RGB', (2400, 2400), 'white'))
        yield f'Saving decoded pages'
        middle = len(pages_list) // 2
        for i in range(middle):
            fb_page = Image.new('RGB', (3780, 5398), 'white')
            top_img, bottom_img = pages_list[i], pages_list[middle + i]
            if i % 2 == 0:
                fb_page.paste(top_img, (0, 0))
                fb_page.paste(bottom_img, (0, 2763))
            else:
                fb_page.paste(top_img, (3780 - top_img.width, 0))
                fb_page.paste(bottom_img, (3780 - top_img.width, 2763))
            top_img.close()
            bottom_img.close()
            fb_page.save(f'{dst_p}/page{i + 1}.jpg', quality=100, dpi=(300, 300))
            fb_page.close()


class JournalEdition(Edition):
    def get_file_list(self):
        self.var_lst = tuple(super().get_file_list())

    def get_file_len(self):
        return sum(len(ex) + 1 for ex in self.var_lst)

    def get_new_dirs(self):
        return tuple(f'{self.path}/_TO_PRINT/{self.name}/{ex.name}' for ex in self.var_lst)

    def processing_run(self):
        path = f'{self.path}/{self.name}'
        for ex in self.var_lst:
            ex_path = f'{path}/{ex.name}'
            dst_path = f'{self.path}/_TO_PRINT/{self.name}/{ex.name}'
            for file in self.journal_decoding(ex_path, ex.img_list, dst_path):
                yield file

    @staticmethod
    def journal_decoding(src_p, file_list, dst_p):
        file_list_len = len(file_list)
        if not file_list_len % 2 == 0:
            return
        count = 0
        yield f'br{str(count).rjust(3, "0")}.jpg'
        shutil.copy2(f'{src_p}/{file_list[-1]}', f'{dst_p}/br{str(count).rjust(3, "0")}.jpg')
        count += 1
        for i in range((file_list_len-1) // 2):
            uneven_spread = file_list[i]
            even_spread = file_list[file_list_len-2-i]
            with Image.open(f'{src_p}/{uneven_spread}') as uneven_spread:
                uneven_spread.load()
            with Image.open(f'{src_p}/{even_spread}') as even_spread:
                even_spread.load()
            uneven_spread_crop = uneven_spread.crop((0, 0, uneven_spread.width // 2, uneven_spread.height))
            spread_to_save = even_spread.copy()
            spread_to_save.paste(uneven_spread_crop)
            yield f'br{str(count).rjust(3, "0")}.jpg'
            spread_to_save.save(f'{dst_p}/br{str(count).rjust(3, "0")}.jpg', quality=100, dpi=(300, 300))
            uneven_spread_crop.close()
            count += 1
            even_spread_crop = even_spread.crop((0, 0, even_spread.width // 2, even_spread.height))
            spread_to_save = uneven_spread.copy()
            spread_to_save.paste(even_spread_crop)
            yield f'br{str(count).rjust(3, "0")}.jpg'
            spread_to_save.save(f'{dst_p}/br{str(count).rjust(3, "0")}.jpg', quality=100, dpi=(300, 300))
            even_spread_crop.close()
            count += 1
            even_spread.close()
            uneven_spread.close()
        yield f'br{str(count).rjust(3, "0")}.jpg'
        msi = file_list_len // 2 - 1
        shutil.copy2(f'{src_p}/{file_list[msi]}', f'{dst_p}/br{str(count).rjust(3, "0")}.jpg')


class CanvasEdition(Edition):

    def get_file_list(self):
        self.cover_lst = tuple(self.get_canvas_covers(super().get_file_list()))

    def get_canvas_covers(self, ex_obj):
        for ex in ex_obj:
            path = f'{self.path}/{self.name}/{ex.name}'
            cover = ex.get_cover()
            if re.fullmatch(r'cover_\d{3}\.jpg', cover):
                yield path, cover
            if re.fullmatch(r'cover_\d{3}-\d{,3}_pcs\.jpg', cover):
                for mult in range(int(re.split(r'[-_]', cover)[2])):
                    yield path, cover

    def get_file_len(self):
        return len(self.cover_lst)

    def get_new_dirs(self):
        return f'{self.path}/_TO_PRINT',

    def processing_run(self):
        canvas_pattern = r'\d{6} холст .{5,11} натяжка в короб\s?\d*\.jpg'
        to_print_len = sum(1 for x in os.listdir(f'{self.path}/_TO_PRINT') if re.search(canvas_pattern, x))
        kwargs = {'stroke': True, 'stroke_size': 355, 'stroke_color': '#ffffff'}
        canvas_format = self.file_stg["book_format"]
        for ind, value in enumerate(self.cover_lst):
            path, file = value
            yield file
            count = ind + to_print_len
            count = ' ' + str(count) if count > 0 else ''
            name = f'{self.path[-6:]} холст {canvas_format} натяжка в короб{count}.jpg'
            self.cover_processing(path, file, f'{self.path}/_TO_PRINT', name, **kwargs)
