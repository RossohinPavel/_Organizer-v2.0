class Product:
    __slots__ = 'product_name', 'short_name'

    def __init__(self, product_name, short_name):
        self.product_name = product_name
        self.short_name = short_name


class FotoBook(Product):
    __slots__ = ('product_name', 'short_name', 'book_format', 'book_option', 'cover_print_material',
                 'page_print_material', 'cover_carton_format', 'cover_canal', 'page_canal', 'guideline')

    def __init__(self, product_name, short_name, book_format, book_option,
                 cover_print_material, page_print_material, cover_carton_format,
                 cover_canal, page_canal, guideline):
        super().__init__(product_name, short_name)
        self.book_format = book_format
        self.book_option = book_option
        self.cover_print_material = cover_print_material
        self.page_print_material = page_print_material
        self.cover_carton_format = cover_carton_format
        self.cover_canal = cover_canal
        self.page_canal = page_canal
        self.guideline = guideline



a = FotoBook(1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
print(a.__dict__)