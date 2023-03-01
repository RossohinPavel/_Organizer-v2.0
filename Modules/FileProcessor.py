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
    __slots__ = 'object_list', 'order_name'

    def __init__(self, order_dict):
        self.order_name = order_dict['NAME']
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
        for obj in self.object_list:
            edition = obj.name
            for file in obj.processing_run():
                yield self.order_name, edition, file


class Edition:
    __slots__ = 'path', 'name', 'index', 'file_stg', 'proc_stg', 'cover_list', 'constant_list', 'variables_list'

    def __init__(self, path, name, index, file_stg, proc_stg=None):
        self.path = path
        self.name = name
        self.index = index
        self.file_stg = file_stg
        self.proc_stg = proc_stg
        self.cover_list = None
        self.constant_list = None
        self.variables_list = None

    def get_file_list(self):
        pass

    def get_file_len(self):
        return 0

    def get_new_dirs(self):
        return []

    def processing_run(self):
        return []

    def get_covers(self):
        path = f'{self.path}/{self.name}'
        for catalog in os.listdir(path):
            if catalog in ('Constant', 'Variable'):
                for file in os.listdir(f'{path}/{catalog}'):
                    if re.fullmatch(r'cover_(?:\d{3}|\d{,3}_pcs|\d{3}-\d{,3}_pcs)\.jpg', file):
                        yield f'{path}/{catalog}', file

    def get_constant_pages(self):
        path = f'{self.path}/{self.name}'
        for catalog in os.listdir(path):
            if catalog == 'Constant':
                for file in os.listdir(f'{path}/{catalog}'):
                    if re.fullmatch(r'\d{3}_\d{,3}_pcs\.jpg', file):
                        yield f'{path}/{catalog}', file

    def get_variable_pages(self):
        path = f'{self.path}/{self.name}'
        for catalog in os.listdir(path):
            if catalog == 'Variable':
                for file in os.listdir(f'{path}/{catalog}'):
                    if re.fullmatch(r'\d{3}__\d{3}\.jpg', file):
                        yield f'{path}/{catalog}', file

    def get_ex_pages(self, covers_include=False):
        path = f'{self.path}/{self.name}'
        for catalog in os.listdir(path):
            if re.fullmatch(r'\d{3}(-\d{,3}_pcs)?', catalog):
                lst = []
                for file in os.listdir(f'{path}/{catalog}'):
                    if re.fullmatch(r'\d{3}__\d{3}(-\d{,3}_pcs)?\.jpg', file):
                        lst.append((f'{path}/{catalog}', file))
                    if covers_include and re.fullmatch(r'cover_\d{3}(-\d{,3}_pcs)?\.jpg', file):
                        lst.append((f'{path}/{catalog}', file))
                yield tuple(lst)

    @staticmethod
    def cover_processing(src_p, src_n, dst_p, dst_n, **kwargs):
        with Image.open(f'{src_p}/{src_n}') as cover_image:
            cover_image.load()
        draw = ImageDraw.Draw(cover_image)
        rec_x = cover_image.width
        rec_y = cover_image.height
        print(kwargs)
        if kwargs.get('stroke', False):     # Прорисовка обводки
            draw.rectangle((0, 0, rec_x, rec_y), outline=kwargs['stroke_color'], width=kwargs['stroke_size'])
        # # Направляющие для обычных книг
        # gl_color = kwargs['gl_color'] if 'gl_color' in kwargs else '#000000'
        # gl_size = kwargs['gl_size'] if 'gl_size' in kwargs else 4
        # gl_spine = kwargs['gl_spine'] if 'gl_spine' in kwargs else 0
        # file_name = kwargs['file_name'] if 'file_name' in kwargs else '0.jpg'
        # if gl_spine > 0 and kwargs['luxe'] is False:
        #     draw.line((gl_spine, 0, gl_spine, 90), fill=gl_color, width=gl_size)
        #     draw.line((rec_x - gl_spine, 0, rec_x - gl_spine, 90), fill=gl_color, width=gl_size)
        #     draw.line((gl_spine, rec_y, gl_spine, rec_y - 90), fill=gl_color, width=gl_size)
        #     draw.line((rec_x - gl_spine, rec_y, rec_x - gl_spine, rec_y - 90), fill=gl_color, width=gl_size)
        # # Направляющие для Люкс книг
        # if gl_spine > 0 and kwargs['luxe'] is True:
        #     draw.line((gl_spine, 0, gl_spine, rec_y), fill=gl_color, width=gl_size)
        #     draw.line((gl_spine + 590, 0, gl_spine + 590, 60), fill=gl_color, width=gl_size)
        #     draw.line((rec_x - gl_spine - 590, 0, rec_x - gl_spine - 590, 60), fill=gl_color, width=gl_size)
        #     draw.line((gl_spine + 590, rec_y, gl_spine + 590, rec_y - 60), fill=gl_color, width=gl_size)
        #     draw.line((rec_x - gl_spine - 590, rec_y, rec_x - gl_spine - 590, rec_y - 60), fill=gl_color, width=gl_size)
        #     draw.line((rec_x - gl_spine, 0, rec_x - gl_spine, rec_y), fill=gl_color, width=gl_size)
        # # Бек принт
        # if 'back_print' in kwargs:
        #     # Рисуем задник для бекпринта
        #     new_name = kwargs['back_print']
        #     back_print = Image.new('RGB', (len(new_name) * 21, 50), 'white')
        #     # Определяем объект для текста
        #     draw_text = ImageDraw.Draw(back_print)
        #     # Получаем шрифт
        #     font = ImageFont.truetype("Data\\Settings\\Roboto-Regular.ttf", size=40)
        #     # Рисуем текст на заднике
        #     draw_text.text((20, 0), text=new_name, font=font, fill="black")
        #     # Поворачиваем задник
        #     rotated_back_print = back_print.rotate(90, expand=True)
        #     # Получаем размеры бекпринта
        #     bp_x = back_print.width
        #     bp_y = back_print.height
        #     # Вставляем бэкпринт на исходное изображение
        #     bp_pos_x = rec_x - kwargs['gl_spine'] + 10 if 'gl_spine' in kwargs else int(rec_x / 2) + 10
        #     cover_image.paste(back_print, (bp_pos_x, rec_y - bp_y))
        #     cover_image.paste(rotated_back_print, (rec_x - bp_y, int((rec_y / 2) - (bp_x / 2))))
        cover_image.save(f'{dst_p}/{dst_n}', quality='keep', dpi=(300, 300))

    @staticmethod
    def journal_decoding(file_list, dst_p):
        file_list_len = len(file_list)
        if not len(file_list) % 2 == 0:
            return
        count = 0
        yield f'br{str(count).rjust(3, "0")}.jpg'
        shutil.copy2(f'{file_list[-1][0]}/{file_list[-1][-1]}', f'{dst_p}/br{str(count).rjust(3, "0")}.jpg')
        count += 1
        for i in range((file_list_len-1) // 2):
            uneven_spread = file_list[i]
            even_spread = file_list[file_list_len-2-i]
            with Image.open(f'{uneven_spread[0]}/{uneven_spread[1]}') as uneven_spread:
                uneven_spread.load()
            with Image.open(f'{even_spread[0]}/{even_spread[1]}') as even_spread:
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
        shutil.copy2(f'{file_list[msi][0]}/{file_list[msi][-1]}', f'{dst_p}/br{str(count).rjust(3, "0")}.jpg')

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
            l_side = Image.new('RGB', (spread_img.width // 2 + left_ind + overlap, spread_img.height + top_ind), 'white')
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

    @staticmethod
    def mm_to_pixel(value: int) -> int:
        return int(value * 11.88)



class FotobookEdition(Edition):
    def get_file_list(self):
        self.cover_list = tuple(self.get_covers())
        self.constant_list = tuple(self.get_constant_pages())
        self.variables_list = tuple(self.get_variable_pages())

    def get_file_len(self):
        return len(self.cover_list) + len(self.constant_list) + len(self.variables_list)

    def get_new_dirs(self):
        lst = [f'{self.path}/_TO_PRINT/{self.name}/{self.file_stg["cover_canal"]}']
        if self.constant_list:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/{self.file_stg["page_canal"]}_Constant')
        if self.variables_list:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/{self.file_stg["page_canal"]}_Variable')
        return tuple(lst)

    def processing_run(self):
        print(self.proc_stg)
        cover_canal, page_canal = self.file_stg["cover_canal"], self.file_stg["page_canal"]
        option = {"б/у": 'bu', "с/у": 'cu', "с/у1.2": 'cu1_2'}[self.file_stg["book_option"]]
        book_type = self.file_stg['book_type']
        rename = self.proc_stg['rename']
        for src_path, src_file in self.cover_list:
            yield src_file
            c_name = f'{self.index}{option}__{src_file}' if rename else src_file
            if book_type in ('Кожаная обложка', 'Планшет'):
                shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/{cover_canal}/{c_name}')
            else:
                self.cover_processing('src', 'p_dst', 'name', **self.file_stg, **self.proc_stg)
        for src_path, src_file in self.constant_list:
            yield src_file
            p_name = f'{self.index}{option}__{src_file}' if rename else src_file
            shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/{page_canal}_Constant/{p_name}')
        for src_path, src_file in self.variables_list:
            yield src_file
            p_name = f'{self.index}{option}__{src_file}' if rename else src_file
            shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/{page_canal}_Variable/{p_name}')


class PolibookEdition(Edition):
    def get_file_list(self):
        self.cover_list = tuple(self.get_covers())
        self.constant_list = tuple(self.get_constant_pages())
        self.variables_list = tuple(self.get_variable_pages())

    def get_file_len(self):
        return len(self.cover_list) + len(self.constant_list) + len(self.variables_list)

    def get_new_dirs(self):
        lst = [f'{self.path}/_TO_PRINT/{self.name}/Covers']
        if self.constant_list:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/Constant')
        if self.variables_list:
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/Variable')
        return tuple(lst)

    def processing_run(self):
        option = {"б/у": 'бу', "с/у": 'су', "с/у1.2": 'су1_2'}[self.file_stg["book_option"]]
        book_type = self.file_stg['book_type']
        rename = self.proc_stg['rename']
        for src_path, src_file in self.cover_list:
            yield src_file
            c_name = f'{self.index}{option}__{src_file}' if rename else src_file
            if book_type in ('Кожаная обложка', 'Планшет'):
                shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/Covers/{c_name}')
            else:
                self.cover_processing('src', 'p_dst', 'name', **self.file_stg, **self.proc_stg)
        for src_path, src_file in self.constant_list:
            yield src_file
            p_name = f'{self.index}{option}__{src_file}' if rename else src_file
            shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/Constant/{p_name}')
        for src_path, src_file in self.variables_list:
            yield src_file
            p_name = f'{self.index}{option}__{src_file}' if rename else src_file
            shutil.copy2(f'{src_path}/{src_file}', f'{self.path}/_TO_PRINT/{self.name}/Variable/{p_name}')


class AlbumEdition(Edition):
    def get_file_list(self):
        self.cover_list = tuple(self.get_covers())
        if self.file_stg['combination'] == 'В_О':
            self.variables_list = tuple(self.get_constant_pages()),
            self.constant_list = self.variables_list[0][0][1].split('_')[1]
        else:
            self.variables_list = tuple(self.get_ex_pages())

    def get_file_len(self):
        file_len = len(self.cover_list) + sum(len(x) for x in self.variables_list)
        if self.file_stg['dc_break']:
            file_len += len(self.variables_list)
        return file_len

    def get_new_dirs(self):
        cover_dir = f'{self.path}/_TO_PRINT/{self.name}/Covers',
        lst = []
        for ex in self.variables_list:
            pages_len = f'{len(ex)}p_'
            copies = f'-{self.constant_list}_pcs' if self.file_stg['combination'] == 'В_О' else ''
            old_name = ex[0][0].split('/')[-1] if self.file_stg['combination'] != 'В_О' else '001'
            lst.append(f'{self.path}/_TO_PRINT/{self.name}/{pages_len}{old_name}{copies}')
        return cover_dir + tuple(lst)

    def processing_run(self):
        rename, gl_need = self.proc_stg['rename'], self.proc_stg['guideline']
        cover_path = f'{self.path}/_TO_PRINT/{self.name}/Covers'
        for src_path, src_file in self.cover_list:
            yield src_file
            c_name = f'{self.index}_{src_file}' if rename else src_file
            if not gl_need:
                shutil.copy2(f'{src_path}/{src_file}', f'{cover_path}/{c_name}')
            else:
                self.cover_processing(src_path, src_file, cover_path, c_name, **self.file_stg, **self.proc_stg)
        for ex in self.variables_list:
            pages_len = f'{len(ex)}p_'
            copies = f'-{self.constant_list}_pcs' if self.file_stg['combination'] == 'В_О' else ''
            old_name = ex[0][0].split('/')[-1] if self.file_stg['combination'] != 'В_О' else '001'
            new_path = f'{self.path}/_TO_PRINT/{self.name}/{pages_len}{old_name}{copies}'
            text = f'{self.path[-6:]} - {self.name[:20]} - {old_name}'
            if self.file_stg['dc_break']:
                for file in self.break_decoding(ex, new_path, text, **self.file_stg):
                    yield file
            else:
                for file in self.album_decoding(ex, new_path, text, **self.file_stg):
                    yield file



class JournalEdition(Edition):
    def get_file_list(self):
        self.variables_list = tuple(self.get_ex_pages(True))

    def get_file_len(self):
        return sum(len(x) for x in self.variables_list)

    def get_new_dirs(self):
        return tuple(f'{self.path}/_TO_PRINT/{self.name}/{ex[0][0].split("/")[-1]}' for ex in self.variables_list)

    def processing_run(self):
        for ex in self.variables_list:
            for file in self.journal_decoding(ex, f'{self.path}/_TO_PRINT/{self.name}/{ex[0][0].split("/")[-1]}'):
                yield file


class CanvasEdition(Edition):

    def get_file_list(self):
        self.cover_list = []
        for path, cover in self.get_covers():
            if re.fullmatch(r'cover_\d{3}\.jpg', cover):
                self.cover_list.append((path, cover))
            if re.fullmatch(r'cover_\d{,3}_pcs\.jpg', cover):
                for mult in range(int(cover.split('_')[1])):
                    self.cover_list.append((path, cover))
            if re.fullmatch(r'cover_\d{3}-\d{,3}_pcs\.jpg', cover):
                for mult in range(int(re.split(r'[-_]', cover)[2])):
                    self.cover_list.append((path, cover))

    def get_file_len(self):
        return len(self.cover_list)

    def get_new_dirs(self):
        return f'{self.path}/_TO_PRINT',

    def processing_run(self):
        canvas_pattern = r'\d{6} холст .{5,11} натяжка в короб\s?\d*\.jpg'
        to_print_len = sum(1 for x in os.listdir(f'{self.path}/_TO_PRINT') if re.search(canvas_pattern, x))
        kwargs = {'stroke': True, 'stroke_size': 355, 'stroke_color': '#ffffff'}
        canvas_format = self.file_stg["book_format"]
        for ind, value in enumerate(self.cover_list):
            path, file = value
            yield file
            count = ind + to_print_len
            count = ' ' + str(count) if count > 0 else ''
            name = f'{self.path[-6:]} холст {canvas_format} натяжка в короб{count}.jpg'
            self.cover_processing(path, file, f'{self.path}/_TO_PRINT', name, **kwargs)
