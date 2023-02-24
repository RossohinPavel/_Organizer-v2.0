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
                f'-- {counts[3]}' if counts[3] is not None else '')
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
