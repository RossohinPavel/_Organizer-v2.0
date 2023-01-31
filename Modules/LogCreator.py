import Modules.Configs as Conf
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
        print(self.content_count, self.name)

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
                paper_format, mpcr = form[5:].split('--')
                name = f'{paper_type.get(paper, "Fuji ???")} {paper_format}'
                photo_dct[name] = photo_dct.get(name, 0) + len(os.listdir(f'{path}/{paper}/{form}')) * int(mpcr)
        return photo_dct

    def book_count(self, name) -> dict:
        """Основной метод для подсчета изображений в книгах"""
        pass


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
