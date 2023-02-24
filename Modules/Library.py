class Product:
    """__CATEGORY - список используемых категорий продуктов в программе"""
    CATEGORY = ('photobook', 'layflat', 'journal', 'album', 'photofolder', 'photocanvas', 'SRAprint', 'sub')

    RUS_NAMES = ('Фотокниги на фотобумаге', 'Полиграфические фотокниги Layflat', 'Полиграфические журналы',
                 'Полиграфические альбомы, PUR, FlexBind', 'Фотопапки', 'Фотохолсты', 'Полиграфическая фотопечать',
                 'Субпродукты')

    """__LOCAL_OPTION - список всех опций, которыми можно описать продукт"""
    __LOCAL_OPTION = ('book_format', 'book_option', 'lamination', 'page_print_mat', 'cover_carton', 'book_type',
                      'cover_canal', 'page_canal', 'gl_value', 'gl_length', 'dc_overlap', 'dc_top_indent',
                      'dc_left_indent', 'dc_break')

    __DESCRIPTION = {'photobook': (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
                     'layflat': (0, 1, 2, 3, 4, 5, 8, 9),
                     'journal': (0, 3),
                     'album': (0, 2, 3, 4, 5, 8, 9, 10, 11, 12, 13),
                     'photofolder': (0, 2, 3, 4),
                     'photocanvas': (0,),
                     'SRAprint': (),
                     'sub': ()}

    SEGMENT = ('Премиум', 'Тираж')

    SHORT_NAME = ("КС", "Люкс", "кКожа", "ФБ", "ППК", "КК", "ПС", "кМикс", "пМикс", "ПК", "ПА", "ПУР", "Дуо",
                  "Дуо гор", "Трио", "Журнал", "+полигр фото", '+холсты')

    BOOK_FORMAT = ("10x10", "15x15", "15x20в", "20x15г", "20x20", "20x30в", "30x20г", "25x25", "30x30", "40x30г",
                   "30x40в", '30x45', '40x40', '50x50', '60x40', '50x75', '60x60', '60x90', '80x80', '120x80')

    BOOK_OPTION = ("б/у", "с/у", "с/у1.2")

    LAMINATION = ('гля', 'мат')

    COVER_PRINT_MAT = ("Omela 500", "Omela 700", "Raflatac 500", "Raflatac 700", "Sappi SRA3", "Sappi 320x620",
                       "UPM SRA4 170", "UPM SRA4 150", "UPM SRA4 250", "UPM SRA3 170", "UPM SRA3 250",
                       "Fuji CA Matte 152x204", "Fuji CA Matte 203x305", "Fuji CA Matte 152x304",
                       "Fuji CA Matte 203x406", "Fuji CA Matte 203x500", "Fuji CA Matte 254x400",
                       "Fuji CA Matte 254x500", "Fuji CA Matte 254x700", "Fuji CA Matte 305x610",
                       "Fuji CA Matte 152x370", "Fuji CA Matte 203x470", "Fuji CA Matte 203x570",
                       "Fuji CA Matte 254x470", "Fuji CA Matte 254x620", "Fuji CA Matte 254x770",
                       "Fuji CA Matte 305x675", 'CottonCanvas')

    PAGE_PRINT_MAT = ("Raflatac 500", "Raflatac 700", "Sappi SRA3", "Sappi 320x620",
                      "UPM SRA4 170", "UPM SRA4 150", "UPM SRA3 170", "UPM SRA3 250",
                      "Fuji CA Matte 300x102", "Fuji CA Matte 152x304", "Fuji CA Matte 152x406",
                      "Fuji CA Matte 203x305", "Fuji CA Matte 203x400", "Fuji CA Matte 305x402",
                      "Fuji CA Matte 203x600", "Fuji CA Matte 254x512", "Fuji CA Matte 305x610",
                      "Fuji CA Matte 305x810", "Flex Bind 330x330", "Flex Bind 330x457")

    COVER_CARTON = ("145х153", "145x205", "193x153", "193x205", "193x300", "293x205", "248x255", "293x300",
                    "153x205", "200x153", "200x205", "200x300", "200x300 2.0", "300x205", "255x255", "300x300")

    BOOK_TYPE_TEXT = {'Фотокниги на фотобумаге': ('Книга', 'Люкс', 'Кожаный корешок', 'Кожаная обложка', 'Планшет'),
                      'Полиграфические фотокниги Layflat': ('Книга', 'Планшет'),
                      'Полиграфические альбомы, PUR, FlexBind': ('Книга',)}

    COVER_CANAL = ('160', '161', '162', '163', '164', '165', '166', '214', '205', '245', '243', '240', '242',
                   '266', '36', '204', 'POLI', 'ORAJET')

    PAGE_CANAL = ('201', '214', '203', '204', '205', '207', '275', '274', '276', '271')

    @classmethod
    def get_product_descr(cls, product_type: str) -> dict:
        category = cls.CATEGORY[cls.RUS_NAMES.index(product_type)]
        main_dsc = {'segment': '', 'category': category, 'short_name': '', 'cover_print_mat': ''}
        local_desc = {cls.__LOCAL_OPTION[k]: '' for k in cls.__DESCRIPTION[category]}
        main_dsc.update(local_desc)
        return main_dsc

    @classmethod
    def book_option(cls, value=None):
        return cls.BOOK_OPTION

    @classmethod
    def lamination(cls, value=None):
        return cls.LAMINATION

    @classmethod
    def book_type(cls, value=None):
        return cls.BOOK_TYPE_TEXT[value]
