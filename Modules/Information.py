class StickerInfo:
    __slots__ = 'order_name', 'order_dict', 'lib_dict'

    def __init__(self, order_name, order_dict, lib_dict):
        self.order_name = order_name
        self.order_dict = order_dict
        self.lib_dict = lib_dict

    def forming_line(self, name, counts, types) -> tuple:
        if types is None:
            return 'body', name
        if types == 'PHOTO':
            return 'suff', '+фото'
        lib = self.lib_dict[types]
        if lib['category'] in ('photocanvas', 'SRAprint', 'sub'):
            return 'suff', lib['short_name']
        info = (lib['short_name'],
                lib['book_format'] if lib['short_name'] not in ("кМикс", "пМикс", "Дуо", "Дуо гор", "Трио") else '',
                counts[2], lib.get('book_option', ''), lib.get('lamination', ''),
                f'-- {counts[3]}' if counts[3] is not None else '',
                '\nкож кор' if lib.get('book_type', False) == 'Кожаный корешок' else '')
        return 'body', ' '.join(name for name in info if name)

    def main(self) -> str:
        body = []
        suff = set()
        for key, value in self.order_dict.items():
            order_info = self.forming_line(key, *value)
            if order_info[0] == 'body':
                body.append(order_info[1])
            else:
                suff.add(order_info[1])
        return '\n'.join(body + list(suff))


class ProductInfo:
    __slots__ = 'date_gen', 'library', 'book_lst', 'photo', 'undetected'

    def __init__(self, date_gen, library):
        self.date_gen = date_gen
        self.library = library
        self.book_lst = []
        self.photo = {}
        self.undetected = {}
        self.__init()

    def get_info(self):
        return self.book_lst, self.photo, self.undetected

    def __init(self):
        for order in (v for day in self.date_gen for k, v in day.items() if k != 'PATH'):
            for edition_name, edition_specs in order.items():
                counters, product_name = edition_specs
                if product_name == 'PHOTO':
                    self.__update_photo_dct(counters)
                elif product_name not in ('PHOTO', None):
                    self.__product_analyse(counters, product_name)
                else:
                    self.__update_undetected_dct(edition_name, counters)

    def __update_photo_dct(self, dct):
        for k, v in dct.items():
            self.photo[k] = self.photo.get(k, 0) + v

    def __update_undetected_dct(self, name, counter):
        self.undetected[name] = self.undetected.get(name, 0) + counter[0]

    def __product_analyse(self, counters, p_name):
        lib_record = self.library.get(p_name)
        if lib_record['segment'] == 'Премиум':
            if lib_record['category'] == 'photocanvas':
                self.__create_photocanvas_record(counters, p_name, lib_record)
        if lib_record['segment'] == 'Тираж':
            pass

    def __create_record(self, category, sub_cat, pr_name, pr_count, mat_lst):
        rec = {'category': category, 'sub_cat': sub_cat, 'pr_name': pr_name, 'pr_count': pr_count, 'mat_lst': mat_lst}
        self.book_lst.append(rec)

    def __create_photocanvas_record(self, counters, p_name, lib_record):
        x, y = map(lambda q: (int(q) + 10) / 100, lib_record['book_format'][:5].split('x'))
        mat_dct = {lib_record['cover_print_mat']: round(x * y * counters[0], 4)}
        self.__create_record('Премиум', 'Остальное', p_name, counters[0], mat_dct)