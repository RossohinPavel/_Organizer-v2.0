import Modules.Configs as Conf
from collections import Counter
import os
import re


class Order:
    __slots__ = 'path', 'creation_date', 'name', 'content', 'content_count', 'content_type'

    def __init__(self, path, name):
        self.path = path
        self.creation_date = path.split('/')[-1]
        self.name = name
        self.content = self.get_order_content()
        self.content_type = self.get_content_type()
        self.content_count = self.get_content_count()
        print(self.name, self.content_type, self.content_count)

    def get_order_content(self) -> tuple:
        """Метод для формирования содержимого заказа. Также проверяет на то, что не включены технические папки."""
        exclusions = ('_TO_PRINT', 'TO_PRINT', '_ЕЩ_ЗКШТЕ')
        path = f'{self.path}/{self.name}'
        return tuple(name for name in os.listdir(path) if name not in exclusions and os.path.isdir(f'{path}/{name}'))

    def get_content_type(self) -> tuple:
        """Метод для определения типа продукта. Формирует записи в виде
        (Базовый тип (для определения обработки), тип продукта). Если не удалось, то к записывается None"""
        return None

    def get_content_count(self) -> tuple:
        """Метод для подсчета количества изображений в тираже. Формирует 2 разные записи (для фото и для книг)
        Для фото - (бумага и формат - суммарное количество).
        Для книг - (общее количество обложек, общее количество разворотов, комплексный счетчик, тип совмещения)"""
        return tuple(self.book_count(name) if name != 'PHOTO' else self.photo_count() for name in self.content)

    def photo_count(self) -> dict:
        """Метод для подсчета фотографий в заказе, которые загружаются в отдельную папку PHOTO"""
        path = f'{self.path}/{self.name}/PHOTO/_ALL/Фотопечать'
        paper_type = {'Глянцевая': 'Fuji Gl', 'Матовая': 'Fuji Mt'}
        photo_dct = {}
        for paper in os.listdir(path):
            for form in os.listdir(f'{path}/{paper}'):
                paper_format, multiplier = form[5:].split('--')
                name = f'{paper_type.get(paper, "Fuji ???")} {paper_format}'
                photo_dct[name] = photo_dct.get(name, 0) + len(os.listdir(f'{path}/{paper}/{form}')) * int(multiplier)
        return photo_dct

    def book_count(self, product_name) -> tuple:
        """Основной метод для подсчета изображений в книгах. Также определяет тип совмещения.
        Возвращает значения в следующем порядке:
        (Общее кол-во обложек, общее кол-во разворотов, комплексный счетчик, порядок совмещения обложек и блоков)"""
        path = f'{self.path}/{self.name}/{product_name}'
        ex_list = []
        const_list = []
        for catalog in os.listdir(path):
            catalog_path = f'{path}/{catalog}'
            if re.fullmatch(r'\d{3}', catalog):
                pic_length = len([x for x in os.listdir(catalog_path) if re.fullmatch(r'\d{3}__\d{3}\.jpg', x)])
                ex_list.append(pic_length if pic_length else 1)
                continue
            if re.fullmatch(r'\d{3}-\d+_pcs', catalog):
                multiplier = int(re.split('[-_]', catalog)[1])
                pic_length = len([x for x in os.listdir(catalog_path) if re.fullmatch(r'\d{3}__\d{3}-\d+_pcs\.jpg', x)])
                ex_list.extend([pic_length if pic_length else 1]*multiplier)
                continue
            if catalog == 'Constant':
                const_list.extend([x for x in os.listdir(catalog_path) if re.fullmatch(r'(\d+|cover)_\d+_pcs\.jpg', x)])
        cover_count = len(ex_list)
        page_count = sum(ex_list)
        return cover_count, page_count, self.get_complex_count(ex_list), self.get_combination(cover_count, page_count, const_list)

    @staticmethod
    def get_complex_count(ex_list) -> str:
        """Метод для формирования комплексного счетчика"""
        return ' '.join(f'{v}/{k}' for k, v in sorted(Counter(ex_list).items(), key=lambda x: (x[1], x[0])))

    @staticmethod
    def get_combination(cover_count, page_count, const_list):
        """Метод для определения типа совмещения обложек и блоков. Для одиночной книги возвращаем None"""
        if cover_count != 1:
            cover_exist = False
            const_page_count = 0
            for name in const_list:
                if re.fullmatch(r'cover_\d+_pcs\.jpg', name):
                    cover_exist = True
                if re.fullmatch(r'\d\d\d_\d+_pcs\.jpg', name):
                    const_page_count += int(name.split('_')[1])
            if cover_exist and const_page_count == page_count:
                return "Копии"
            if cover_exist:
                return 'О_О'
            if const_page_count == page_count:
                return 'В_О'
            return 'Индивидуально'



def get_settings():
    """Функия получения настроек для формирования лога"""
    settings = Conf.read_pcl_for_test('settings')
    return settings['order_main_dir'], settings['log_check_depth']


def get_daydir_tuple(path) -> tuple:
    """
    Функция для получения списка папок - дней, в которых расположены заказы. Дополнительно проверяем на 23 год и старше.
    :param path: Корневой каталог, куда загружаются заказы
    :return: Кортеж, элементы которого - абсолютные пути до этой папки.
    """
    return tuple(f'{path}/{day}' for day in os.listdir(path) if re.fullmatch(r'\d{3}[3-9]-\d{2}-\d{2}', day))


def get_orderdir_tuple(path) -> tuple:
    """
    Функция для получения списков заказов
    :param path: Корневой каталог - день, когда загружен заказ
    :return: Кортеж имен папок - заказов
    """
    return tuple(name for name in os.listdir(path) if re.fullmatch(r'\d{6}', name))


def main():
    order_main_dir, log_check_depth = get_settings()      # Получаем необходимые настройки для работы
    for day in reversed(get_daydir_tuple(order_main_dir)):       # Проходим по дням в обратном порядке
        for name in reversed(get_orderdir_tuple(day)):
            order = Order(day, name)



if __name__ == '__main__':
    main()
