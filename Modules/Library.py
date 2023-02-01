class Product:
    __PRODUCT_DESCRIPTION = {"Фотокнига Стандарт": {'product_name': '', 'short_name': '', 'book_format': '',
                                                    'book_option': '', 'lamination': '',
                                                    'cover_print_mat': '', 'page_print_mat': '', 'cover_carton': '',
                                                    'cover_canal': '', 'page_canal': '', 'gl_value': 0, 'gl_length': 0},
                             "Фотокнига ЛЮКС": {'product_name': '', 'short_name': '', 'book_format': '',
                                                'book_option': '', 'lamination': '', 'is_luxe': True,
                                                'cover_print_mat': '', 'page_print_mat': '', 'cover_carton': '',
                                                'cover_canal': '', 'page_canal': '', 'gl_value': 0, 'gl_length': 0},
                             "Фотокнига Классик": {'product_name': '', 'short_name': '', 'book_format': '',
                                                   'book_option': '', 'lamination': '',
                                                   'cover_print_mat': '', 'page_print_mat': '', 'cover_carton': '',
                                                   'cover_canal': '', 'page_canal': '', 'gl_value': 0, 'gl_length': 0},
                             "Фотопланшет Стандарт": {'product_name': '', 'short_name': '', 'book_format': '',
                                                      'book_option': '', 'lamination': '', 'is_tablet': True,
                                                      'cover_print_mat': '', 'page_print_mat': '', 'cover_carton': '',
                                                      'cover_canal': '', 'page_canal': ''},
                             "Фотокнига Flex Bind": {'product_name': '', 'short_name': '', 'book_format': '',
                                                     'lamination': '', 'cover_print_mat': '', 'page_print_mat': '',
                                                     'cover_carton': '', 'gl_value': 0, 'gl_length': 0, 'dc_overlap': 0,
                                                     'dc_top_indent': 0, 'dc_left_indent': 0, 'dc_break': False},
                             "Layflat": {'product_name': '', 'short_name': '', 'book_format': '', 'book_option': '',
                                         'lamination': '', 'cover_print_mat': '', 'page_print_mat': '',
                                         'cover_carton': '', 'gl_value': 0, 'gl_length': 0, 'is_tablet': False},
                             "Фотоальбом полиграфический": {'product_name': '', 'short_name': '', 'book_format': '',
                                                            'lamination': '', 'cover_print_mat': '',
                                                            'page_print_mat': '', 'cover_carton': '', 'gl_value': 0,
                                                            'gl_length': 0, 'dc_overlap': 0, 'dc_top_indent': 0,
                                                            'dc_left_indent': 0},
                             "Фотоальбом PUR": {'product_name': '', 'short_name': '', 'book_format': '',
                                                'lamination': '', 'cover_print_mat': '', 'page_print_mat': '',
                                                'cover_carton': '', 'gl_value': 0, 'gl_length': 0, 'dc_overlap': 0,
                                                'dc_top_indent': 0, 'dc_left_indent': 0},
                             "Фотожурнал": {'product_name': '', 'short_name': '', 'book_format': '',
                                            'cover_print_mat': '', 'page_print_mat': ''},
                             "Фотопапка": {'product_name': '', 'short_name': '', 'book_format': '', 'lamination': '',
                                           'cover_print_mat': '', 'page_print_mat': '', 'cover_carton': ''},
                             "Фотопечать SRA": {'product_name': '', 'short_name': '', 'cover_print_mat': ''},
                             "Субпродукты": {'product_name': '', 'short_name': '', 'cover_print_mat': ''}
                             }

    __SHORT_NAME_LIST = ("КС", "Люкс", "кКожа", "ФБ", "ППК", "КК", "ПС", "кМикс", "пМикс", "ПК", "ПА", "ПУР", "Дуо",
                         "Дуо гор", "Трио", "Журнал", "+полигр фото")

    __BOOK_FORMAT_LIST = ("10x10", "15x15", "15x20в", "20x15г", "20x20", "20x30в", "30x20г", "25x25", "30x30", "40x30г",
                          "30x40в")

    __BOOK_OPTION_LIST = ("б/у", "с/у", "с/у1.2")

    __LAMINATION = ('гля', 'мат')

    __COVER_PRINT_MAT = ("Omela 500", "Omela 700", "Raflatac 500", "Raflatac 700", "Sappi SRA3", "Sappi 320x620",
                         "UPM SRA4 170", "UPM SRA4 150", "UPM SRA4 250", "UPM SRA3 170", "UPM SRA3 250",
                         "Fuji CA Matte 152x204", "Fuji CA Matte 203x305", "Fuji CA Matte 152x304",
                         "Fuji CA Matte 203x406", "Fuji CA Matte 203x500", "Fuji CA Matte 254x400",
                         "Fuji CA Matte 254x500", "Fuji CA Matte 254x700", "Fuji CA Matte 305x610",
                         "Fuji CA Matte 152x370", "Fuji CA Matte 203x470", "Fuji CA Matte 203x570",
                         "Fuji CA Matte 254x470", "Fuji CA Matte 254x620", "Fuji CA Matte 254x770",
                         "Fuji CA Matte 305x675")

    __PAGE_PRINT_MAT = ("Raflatac 500", "Raflatac 700", "Sappi SRA3", "Sappi 320x620",
                        "UPM SRA4 170", "UPM SRA4 150", "UPM SRA3 170", "UPM SRA3 250",
                        "Fuji CA Matte 300x102", "Fuji CA Matte 152x304", "Fuji CA Matte 152x406",
                        "Fuji CA Matte 203x305", "Fuji CA Matte 203x400", "Fuji CA Matte 305x402",
                        "Fuji CA Matte 203x600", "Fuji CA Matte 254x512", "Fuji CA Matte 305x610",
                        "Fuji CA Matte 305x810", "Flex Bind 330x330", "Flex Bind 330x457")

    __COVER_CARTON_LIST = ("145х153", "145x205", "193x153", "193x205", "193x300", "293x205", "248x255", "293x300",
                           "153x205", "200x153", "200x205", "200x300", "200x300 2.0", "300x205", "255x255", "300x300")

    __COVER_CANAL_LIST = ('160', '161', '162', '163', '164', '165', '166', '214', '205', '245', '243', '240', '242',
                          '266', '36', '204', 'POLI', 'ORAJET')

    __PAGE_CANAL_LIST = ('201', '214', '203', '204', '205', '207', '275', '274', '276', '271')

    @classmethod
    def product_type(cls) -> tuple:
        return tuple(cls.__PRODUCT_DESCRIPTION.keys())

    @classmethod
    def short_name_list(cls) -> tuple:
        return cls.__SHORT_NAME_LIST

    @classmethod
    def book_format_list(cls) -> tuple:
        return cls.__BOOK_FORMAT_LIST

    @classmethod
    def book_option_list(cls) -> tuple:
        return cls.__BOOK_OPTION_LIST

    @classmethod
    def lamination(cls) -> tuple:
        return cls.__LAMINATION

    @classmethod
    def cover_print_mat(cls) -> tuple:
        return cls.__COVER_PRINT_MAT

    @classmethod
    def page_print_mat(cls) -> tuple:
        return cls.__PAGE_PRINT_MAT

    @classmethod
    def cover_carton_list(cls) -> tuple:
        return cls.__COVER_CARTON_LIST

    @classmethod
    def cover_canal_list(cls) -> tuple:
        return cls.__COVER_CANAL_LIST

    @classmethod
    def page_canal_list(cls) -> tuple:
        return cls.__PAGE_CANAL_LIST

    @classmethod
    def get_product_descr(cls, product_type) -> dict:
        return cls.__PRODUCT_DESCRIPTION[product_type]