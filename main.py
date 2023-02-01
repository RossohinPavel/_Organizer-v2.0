"""Органайзер. Версия 2_0"""
import tkinter as tk
from tkinter import filedialog as tkfd
from tkinter import colorchooser as tkcc
from tkinter.ttk import Progressbar
from tkinter.ttk import Combobox
import Modules.Configs as Conf
import Modules.Roddom as Roddom
import Modules.FileProcessor as FileProc
import Modules.Library as Lib


class CellLabel(tk.Frame):
    """Конструктор для ячеек с названиями"""

    def __init__(self, label_color='red', label_text='Название лейбла', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = tk.Label(self, text=label_text, bg=label_color, width=270)
        self.label.pack()


class CellOneButton(tk.Frame):
    """Конструктор для одиночных кнопок"""

    def __init__(self, func_name='Название кнопки', func=None, pd_x=0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(width=270)
        self.button = tk.Button(self, text=func_name, relief=tk.FLAT, fg="#eee", bg="#454545", command=func, padx=pd_x)
        self.button.pack(pady=3)


class ChildWindow(tk.Toplevel):
    """Конструктор для дочерних окон"""

    def __init__(self, parent_root):
        self.parent_root = parent_root
        super().__init__(master=parent_root)
        self.style = {'relief': tk.FLAT, 'fg': "#eee", 'bg': "#454545"}

    def to_parent_center(self):
        """Центрирование относительно родительского окна"""
        self.update_idletasks()
        parent_width = self.parent_root.winfo_width()  # Получаем размер родительского окна
        parent_height = self.parent_root.winfo_height()
        parent_place_x = self.parent_root.winfo_x()  # Получаем положение родительского окна
        parent_place_y = self.parent_root.winfo_y()
        child_width = self.winfo_width()  # Размер дочернего окна
        child_height = self.winfo_height()
        place_x = ((parent_width - child_width) // 2) + parent_place_x
        place_y = ((parent_height - child_height) // 2) + parent_place_y
        self.geometry(f"+{place_x}+{place_y}")

    def focus(self):
        """Перехват фокуса и блокирование родительского окна"""
        self.grab_set()
        self.focus_set()
        self.wait_window()


class RoddomWindow(ChildWindow):
    """Окно Роддома"""

    def __init__(self, parent_root):
        super().__init__(parent_root)
        # Получаем настройки из конфигов
        self.settings = Conf.read_pcl('settings')
        # Основные настройки окна
        self.title('Роддом')
        self.geometry('260x237')
        self.resizable(False, False)
        self.to_parent_center()
        # Переменные, которые используют виджеты
        self.order_exist = None
        self.directory_info = tk.StringVar(self, self.settings['roddom_main_dir'])
        self.order_calc_info = None
        self.text_res_enable = tk.IntVar(self, value=1)
        self.mrk_form_enable = tk.IntVar(self, value=0)
        # Вызов отрисовки основных виджетов
        self.show_directory_widget()
        self.info_frame = tk.Frame(self, width=260, height=80)
        self.info_frame.pack()
        self.show_cb_frame()
        self.show_buttons_widget()
        # Фокусировка окна
        self.focus()

    def show_directory_widget(self):
        """Функция отрисовки фрейма с информацией, где храняться заказы роддома"""
        frame = tk.Frame(self, width=260, height=50)
        dir_status_label = tk.Label(frame, text='Папка, куда сохраняются заказы Роддом\'а')
        dir_status_label.place(x=0, y=0)
        dir_update_button = tk.Button(frame, textvariable=self.directory_info, command=self.update_directory,
                                      width=35, **self.style)
        dir_update_button.place(x=3, y=20)
        separator = tk.Canvas(frame, width=260, height=1, bg='black')
        separator.place()
        frame.pack()

    def update_directory(self):
        """Функция смены папки размещения заказов роддома"""
        new_path = tkfd.askdirectory()
        if new_path:
            self.directory_info.set(new_path)
            self.settings['roddom_main_dir'] = new_path
            Conf.write_pcl('settings', self.settings)

    def show_cb_frame(self):
        """Функция отрисовки Checkbutton - настроек обработки заказов роддома"""
        frame = tk.Frame(self, width=260, height=50)
        separator = tk.Canvas(frame, width=260, height=1, bg='black')
        separator.place(x=0, y=0)
        text_res_cb = tk.Checkbutton(frame, text='Сохранять результаты в sum.txt', variable=self.text_res_enable)
        text_res_cb.place(x=3, y=3)
        mrk_form_cb = tk.Checkbutton(frame, text='Формировать .mrk файл', variable=self.mrk_form_enable)
        mrk_form_cb.place(x=3, y=23)
        frame.pack()

    def show_buttons_widget(self):
        """Функция отрисовки кнопок, для взаимодействия с заказом"""
        frame = tk.Frame(self, width=260, height=60)
        button1 = tk.Button(frame, text='Посчитать заказ', command=self.init_calc, **self.style)
        button1.place(x=3, y=0)
        button2 = tk.Button(frame, text='Скопировать инф', command=self.info_to_clipboard, **self.style)
        button2.place(x=3, y=28)
        button3 = tk.Button(frame, text='Отправить в печать', command=self.to_print, **self.style)
        button3.place(y=28, x=138)
        frame.pack()

    def init_calc(self):
        """Функция вызова метода подсчета из заказа - объекта Роддома"""
        order = tkfd.askdirectory(initialdir=self.directory_info.get())
        if not order:
            return
        self.order_exist = Roddom.RoddomOrder(order, bool(self.text_res_enable.get()), bool(self.mrk_form_enable.get()))
        self.order_calc_info = str(self.order_exist)
        self.show_order_info(self.order_calc_info)
        self.info_to_clipboard()

    def info_to_clipboard(self):
        """Функция, которая заносит информацию о пути и дате заказа в будфер обмена"""
        tk.Tk.clipboard_clear(self)
        tk.Tk.clipboard_append(self, self.order_calc_info)

    def info_frame_clear(self):
        """Функция очистки info_frame"""
        for widget in self.info_frame.winfo_children():
            widget.destroy()

    def show_order_info(self, text):
        """Функция отрисовки подсчитанной информации"""
        self.info_frame_clear()
        label = tk.Label(self.info_frame, text=text, font=12)
        label.place(x=0, y=0)

    def button_disabler(self):
        """Функция, которая выключает взаимодействие с кнопками"""
        for i in self.winfo_children():
            if type(i) == tk.Frame:
                for j in i.winfo_children():
                    if type(j) == tk.Button and j._name != '!button2':
                        j.config(state="disabled")

    def button_enabler(self):
        """Функция, которая включает взаимодействие с кнопками"""
        for i in self.winfo_children():
            if type(i) == tk.Frame:
                for j in i.winfo_children():
                    if type(j) == tk.Button and j._name != '!button2':
                        j.config(state="normal")

    def to_print(self):
        """Функция отправки в печать. Отображает на экране информацию о коопировани и вызывает методы копирования"""
        if not self.order_exist:
            return
        path = tkfd.askdirectory(initialdir=self.settings['fotoprint_temp_dir'])
        if not path:
            return
        self.order_calc_info = f'{path}\n\nРоддом\n\n{self.order_exist.order_name}'
        self.info_to_clipboard()
        self.info_frame_clear()
        self.button_disabler()
        operation_label = tk.Label(self.info_frame, text='Создаю Каталоги')
        operation_label.place(x=0, y=0)
        file_label = tk.Label(self.info_frame, text='Вторая строчка')
        file_label.place(x=0, y=15)
        progressbar = Progressbar(self.info_frame, orient=tk.HORIZONTAL, mode="determinate", length=254)
        progressbar.place(x=3, y=40)
        for i in self.order_exist.get_directory_list():
            FileProc.make_dirs(f'{path}/{i}')
        file_lst = self.order_exist.get_file_list()
        file_len = len(file_lst)
        progressbar['maximum'] = file_len
        progressbar['value'] = 0
        operation_label.config(text='Копирую файлы')
        for name in file_lst:
            FileProc.copy_file(f'{self.directory_info.get()}/{name}', f'{path}/{name}')
            progressbar['value'] += 1
            file_label.config(text=f'{progressbar["value"]}/{file_len} -- {name.split("/")[-1]}')
            self.update()
        operation_label.config(text='Завершено')
        file_label.config(text='')
        self.button_enabler()
        self.order_exist = None


class SettingsWindow(ChildWindow):
    def __init__(self, main_window):
        super().__init__(main_window)
        self.settings = Conf.read_pcl('settings')
        self.title('Настройки')
        self.show_autolog_widget()
        self.show_log_check_depth_widget()
        self.show_cover_processing_settings('Цвет обводки', 'stroke_color', 'Толщина обводки', 'stroke_size')
        self.show_cover_processing_settings('Цвет направляющих', 'guideline_color', 'Толщина направляющих',
                                            'guideline_size')
        self.show_directory_widget('Диск оператора фотопечати', 'fotoprint_temp_dir')
        self.show_directory_widget('Папка для сохранения заказов', 'order_main_dir')
        self.to_parent_center()
        self.focus()

    def show_autolog_widget(self):
        def update_label_info():
            autolog_label.config(text='Автолог: Активен' if self.settings['autolog'] else 'Автолог: Отключен')
            autolog_init_bt.config(text='Отключить' if self.settings['autolog'] else 'Включить')

        def init_autolog():
            value = not self.settings['autolog']
            self.settings['autolog'] = value
            update_label_info()
            Conf.write_pcl('settings', self.settings)

        frame = tk.Frame(self, width=260, height=30)
        autolog_label = tk.Label(frame)
        autolog_label.place(x=0, y=4)
        autolog_init_bt = tk.Button(frame, **self.style, command=init_autolog)
        autolog_init_bt.place(x=130, y=2)
        update_label_info()
        separator = tk.Canvas(frame, width=260, height=1, bg='black')
        separator.place(x=0, y=27)
        frame.pack()

    def show_log_check_depth_widget(self):
        def update_text_value():
            label.config(text=f'Глубина проверки лога - {self.settings["log_check_depth"]} заказов')

        def update_depth_value():
            value = entry_var.get()
            if value.isdigit():
                self.settings['log_check_depth'] = int(value)
                Conf.write_pcl('settings', self.settings)
            update_text_value()
            entry.delete(0, tk.END)

        frame = tk.Frame(self, width=260, height=51)
        label = tk.Label(frame)
        label.place(x=1, y=1)
        update_text_value()
        entry_var = tk.StringVar(frame)
        entry = tk.Entry(frame, width=10, textvariable=entry_var)
        entry.place(x=40, y=26)
        update_button = tk.Button(frame, text='Задать', **self.style, command=update_depth_value)
        update_button.place(x=120, y=22)
        separator = tk.Canvas(frame, width=260, height=1, bg='black')
        separator.place(x=0, y=47)
        frame.pack()

    def show_cover_processing_settings(self, color_text, color_stg_key, size_text, size_stg_key):
        def update_color():
            color = tkcc.askcolor()
            if color:
                self.settings[color_stg_key] = color[1]
                Conf.write_pcl('settings', self.settings)
            color_btn.config(bg=self.settings[color_stg_key])

        def update_size_label():
            size_label.config(text=f'{size_text}: {self.settings[size_stg_key]} пикселей')

        def update_size(val):
            self.settings[size_stg_key] = int(val)
            Conf.write_pcl('settings', self.settings)
            update_size_label()

        frame = tk.Frame(self, width=260, height=73)
        label = tk.Label(frame, text=color_text)
        label.place(x=1, y=3)
        color_btn = tk.Button(frame, relief=tk.FLAT, width=12, bg=self.settings[color_stg_key], command=update_color)
        color_btn.place(x=125, y=0)

        size_label = tk.Label(frame)
        size_label.place(x=1, y=26)
        scale = tk.Scale(frame, orient=tk.HORIZONTAL, from_=1, to=10, length=255, showvalue=False, command=update_size)
        scale.place(x=0, y=48)
        scale.set(self.settings[size_stg_key])
        update_size_label()

        separator = tk.Canvas(frame, width=260, height=1, bg='black')
        separator.place(x=0, y=68)
        frame.pack()

    def show_directory_widget(self, text, settings_key):
        def update_directory():
            path = tkfd.askdirectory()
            if path:
                text_var.set(path)
                self.settings[settings_key] = path
                Conf.write_pcl('settings', self.settings)

        frame = tk.Frame(self, width=260, height=50)
        text_var = tk.StringVar(frame, value=self.settings[settings_key])
        dir_status_label = tk.Label(frame, text=text)
        dir_status_label.place(x=0, y=0)
        dir_update_button = tk.Button(frame, textvariable=text_var, command=update_directory, width=35, **self.style)
        dir_update_button.place(x=3, y=20)
        separator = tk.Canvas(frame, width=260, height=1, bg='black')
        separator.place(x=0, y=45)
        frame.pack()


class LibraryWindow(ChildWindow):
    """Конструктор для окон библиотеки"""

    def __init__(self, parent_root):
        super().__init__(parent_root)
        # Переменные, которые заполняются в зависимости от выбранного окна и выбранного действия
        self.category_combobox = None  # Для отрисовки комбобокса категорий и сохранения его значений
        self.product_menus_frame = None  # Фрейм, на котором рисуются менюшки с выбором
        self.product_description = None  # Для хранения словаря с описанием категорий продукта и типов значений
        self.full_name_variable = None  # Текстовая переменная для Entry полного имени продукта
        self.short_name_cb = None  # Комбобокс с выбором короткого имени
        self.book_format_cb = None  # Комбобокс с выбором формата
        self.book_option_cb = None  # Комбобокс с выбором опций сборки
        self.book_lamination_cb = None  # Комбобокс для ламинации
        self.cover_print_mat_cb = None  # Комбобокс с печатным материалом обложки
        self.page_print_mat_cb = None  # Кобобокс с печатным материалом разворотов
        self.is_tablet_chb_var = None       # Переменная CheckButton проверка на планшет
        self.gl_value_var = None        # Переменная для Entry значения направяющих
        self.gl_length_var = None       # Переменная для Entry длинны направляющих
        self.cover_canal_cb = None      # Комбобокс с выбором канала обложки
        self.dc_overlap_var = None      # Переменная для Entry значения нахлеста для раскодировки
        self.dc_top_indent_var = None   # Переменная для Entry значения отступа сверху
        self.dc_left_indent_var = None  # Переменная для Entry значения отступа слева

    def show_category_frame(self, cb_bind_func):
        """Функция для обображения фрейма категорий. Инициализирует комбобокс с нужным Событием."""
        frame = tk.Frame(self, width=500, height=51)
        label = tk.Label(frame, text='Выберите категорию')
        label.place(x=200, y=1)
        self.category_combobox = Combobox(frame, state="readonly", width=40, values=Lib.ProductFactory.product_type())
        self.category_combobox.bind('<<ComboboxSelected>>', cb_bind_func)
        self.category_combobox.place(x=130, y=25)
        separator = tk.Canvas(frame,  width=496, height=1, bg='black')
        separator.place(x=0, y=46)
        frame.pack()

    def show_product_menus(self):
        """Функция для отрисовки фрейма менюшек выбора значений"""
        self.product_menus_frame = tk.Frame(self, width=500, height=330)
        self.product_menus_frame.pack()

    def show_saved_names_frame(self):
        """Функция для отрисовки фрейма с отображением сохраненных имен"""
        frame = tk.Frame(self, width=500, height=50, bg='violet')
        frame.pack()

    def show_buttons(self):
        """Функция для отрисовки кнопок"""
        frame = tk.Frame(self, width=500, height=30, bg='green')
        frame.pack()

    def product_menus_frame_clearing(self):
        """Очистка меню-виджета от ненужных фреймов"""
        for widget in self.product_menus_frame.winfo_children():
            widget.destroy()

    def set_product_description(self, value):
        self.product_description = Lib.ProductFactory.get_product_descr(value)

    def __show_full_name_frame(self):
        full_name_label = tk.Label(self.product_menus_frame, text='Введите полное имя продукта')
        full_name_label.place(x=2, y=0)
        self.full_name_variable = tk.StringVar()
        full_name_entry = tk.Entry(self.product_menus_frame, width=39)
        full_name_entry.place(x=2, y=20)

    def __show_short_name_frame(self):
        short_name_label = tk.Label(self.product_menus_frame, text="Выберите короткое имя")
        short_name_label.place(x=2, y=41)
        self.short_name_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                      values=Lib.ProductFactory.short_name_list())
        self.short_name_cb.place(x=2, y=61)

    def __show_book_format_frame(self):
        book_format_label = tk.Label(self.product_menus_frame, text="Выберите формат книги")
        book_format_label.place(x=2, y=82)
        self.book_format_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                       values=Lib.ProductFactory.book_format_list())
        self.book_format_cb.place(x=2, y=102)

    def __show_book_option_frame(self):
        book_option_label = tk.Label(self.product_menus_frame, text="Выберите опции сборки книги")
        book_option_label.place(x=2, y=123)
        self.book_option_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                       values=Lib.ProductFactory.book_option_list())
        self.book_option_cb.place(x=2, y=143)

    def __show_lamination_frame(self):
        book_lamination_label = tk.Label(self.product_menus_frame, text='Выберите ламинацию для продукта')
        book_lamination_label.place(x=2, y=164)
        self.book_lamination_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                           values=Lib.ProductFactory.lamination())
        self.book_lamination_cb.place(x=2, y=184)

    def __show_cover_print_mat_frame(self):
        cover_print_mat_lbl = tk.Label(self.product_menus_frame, text="Выберите печатный материал обложки")
        cover_print_mat_lbl.place(x=250, y=0)
        self.cover_print_mat_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                           values=Lib.ProductFactory.cover_print_mat())
        self.cover_print_mat_cb.place(x=250, y=20)

    def __show_cover_carton_frame(self):
        cover_carton_format_lbl = tk.Label(self.product_menus_frame, text="Выберите картонку для обложки")
        cover_carton_format_lbl.place(x=250, y=41)
        self.cover_carton_format_combo = Combobox(self.product_menus_frame, width=36, state="readonly",
                                                  values=Lib.ProductFactory.cover_carton_list())
        self.cover_carton_format_combo.place(x=250, y=61)

    def __show_page_print_mat_frame(self):
        page_print_mat_lbl = tk.Label(self.product_menus_frame, text="Выберите печатный материал разворотов")
        page_print_mat_lbl.place(x=250, y=82)
        self.page_print_mat_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                          values=Lib.ProductFactory.page_print_mat())
        self.page_print_mat_cb.place(x=250, y=102)

    def __show_tablet_check_frame(self):
        self.is_tablet_chb_var = tk.IntVar(self.product_menus_frame)
        self.is_tablet_chb_var.set(int(self.product_description['is_tablet']))
        is_tablet_chb = tk.Checkbutton(self.product_menus_frame, text='Книга является планшетом',
                                       variable=self.is_tablet_chb_var)
        is_tablet_chb.place(x=250, y=160)

    def __show_guideline_value_frame(self):
        guideline_value_label = tk.Label(self.product_menus_frame, text="Введите значение в мм для направляющих")
        guideline_value_label.place(x=2, y=210)
        self.gl_value_var = tk.StringVar(self.product_menus_frame)
        guideline_value_entry = tk.Entry(self.product_menus_frame, width=39, textvariable=self.gl_value_var)
        guideline_value_entry.place(x=2, y=230)

    def __show_guideline_length_frame(self):
        guideline_length_label = tk.Label(self.product_menus_frame, text="Введите длинну в мм для направляющих")
        guideline_length_label.place(x=2, y=251)
        self.gl_length_var = tk.StringVar(self.product_menus_frame)
        guideline_length_entry = tk.Entry(self.product_menus_frame, width=39, textvariable=self.gl_length_var)
        guideline_length_entry.place(x=2, y=271)
    
    def __show_cover_canal_frame(self):
        cover_canal_label = tk.Label(self.product_menus_frame, text="Выберите 'канал' для обложки")
        cover_canal_label.place(x=250, y=210)
        self.cover_canal_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                       values=Lib.ProductFactory.cover_canal_list())
        self.cover_canal_cb.place(x=250, y=230)

    def __show_page_canal_frame(self):
        cover_canal_label = tk.Label(self.product_menus_frame, text="Выберите 'канал' для разворотов")
        cover_canal_label.place(x=250, y=251)
        self.cover_canal_cb = Combobox(self.product_menus_frame, width=36, state="readonly",
                                       values=Lib.ProductFactory.page_canal_list())
        self.cover_canal_cb.place(x=250, y=271)

    def __show_decoding_overlap_frame(self):
        decoding_overlap_label = tk.Label(self.product_menus_frame, text="НАХЛЕСТ для переплета в мм")
        decoding_overlap_label.place(x=250, y=210)
        self.dc_overlap_var = tk.StringVar(self.product_menus_frame)
        decoding_overlap_entry = tk.Entry(self.product_menus_frame, width=39, textvariable=self.dc_overlap_var)
        decoding_overlap_entry.place(x=250, y=230)

    def __show_decoding_top_indent_frame(self):
        decoding_top_indent_label = tk.Label(self.product_menus_frame, text="Введите значение отступа СВЕРХУ в мм")
        decoding_top_indent_label.place(x=250, y=251)
        self.dc_top_indent_var = tk.StringVar(self.product_menus_frame)
        decoding_top_indent_entry = tk.Entry(self.product_menus_frame, width=39, textvariable=self.dc_top_indent_var)
        decoding_top_indent_entry.place(x=250, y=271)

    def __show_decoding_left_indent_frame(self):
        decoding_left_indent_label = tk.Label(self.product_menus_frame, text="Введите значение отступа СЛЕВА в мм")
        decoding_left_indent_label.place(x=250, y=291)
        self.dc_left_indent_var = tk.StringVar(self.product_menus_frame)
        decoding_left_indent_entry = tk.Entry(self.product_menus_frame, width=39, textvariable=self.dc_left_indent_var)
        decoding_left_indent_entry.place(x=250, y=311)

    def init_menu_lines(self):
        """Отображает менюшки на self.product_menus_frame согласно выбранному продукту"""
        frames = {'product_name': lambda: self.__show_full_name_frame(),
                  'short_name': lambda: self.__show_short_name_frame(),
                  'book_format': lambda: self.__show_book_format_frame(),
                  'book_option': lambda: self.__show_book_option_frame(),
                  'lamination': lambda: self.__show_lamination_frame(),
                  'cover_print_mat': lambda: self.__show_cover_print_mat_frame(),
                  'cover_carton': lambda: self.__show_cover_carton_frame(),
                  'page_print_mat': lambda: self.__show_page_print_mat_frame(),
                  'is_tablet': lambda: self.__show_tablet_check_frame(),
                  'gl_value': lambda: self.__show_guideline_value_frame(),
                  'gl_length': lambda: self.__show_guideline_length_frame(),
                  'cover_canal': lambda: self.__show_cover_canal_frame(),
                  'page_canal': lambda: self.__show_page_canal_frame(),
                  'dc_overlap': lambda: self.__show_decoding_overlap_frame(),
                  'dc_top_indent': lambda: self.__show_decoding_top_indent_frame(),
                  'dc_left_indent': lambda: self.__show_decoding_left_indent_frame()}
        for key in self.product_description.keys():
            value = frames.get(key)
            if value:
                value()
        separator = tk.Canvas(self.product_menus_frame, width=496, height=1, bg='black')
        separator.place(x=0, y=207)


class AddToLibWindow(LibraryWindow):
    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.title('Добавление продукта')
        self.show_category_frame(self.add_event)
        self.show_product_menus()
        self.show_buttons()

    def add_event(self, event=None):
        self.product_menus_frame_clearing()
        self.set_product_description(self.category_combobox.get())
        self.init_menu_lines()


class ChangeLibWindow(LibraryWindow):
    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.title('Измeнение продукта')
        self.show_category_frame()
        self.show_saved_names_frame()
        self.show_product_menus()
        self.show_buttons()


class DeleteFromLibWindow(LibraryWindow):
    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.title('Удаление продукта')
        self.show_category_frame()
        self.show_saved_names_frame()
        self.show_buttons()


def init_cells():
    def init_roddom_window(): RoddomWindow(root)

    fotoprint_label = CellLabel(master=root, label_color='pale green1', label_text='Фотопечать')
    fotoprint_label.pack()
    roddom_cell = CellOneButton(master=root, func_name='Роддом', func=init_roddom_window, pd_x=50)
    roddom_cell.pack()


def show_menus():
    def init_settings_window(): SettingsWindow(root)

    def init_add_to_lib_window(): AddToLibWindow(root)

    def init_change_lib_window(): ChangeLibWindow(root)

    def init_delete_from_lib_window(): DeleteFromLibWindow(root)

    settings_menu = tk.Menu(tearoff=0)
    settings_menu.add_command(label="Общие настройки", command=init_settings_window)

    library_menu = tk.Menu(tearoff=0)
    library_menu.add_command(label='Добавить продукт', command=init_add_to_lib_window)
    library_menu.add_command(label='Изменить продукт', command=init_change_lib_window)
    library_menu.add_command(label='Удалить продукт', command=init_delete_from_lib_window)

    main_menu = tk.Menu()
    main_menu.add_cascade(label="Настройки", menu=settings_menu)
    main_menu.add_cascade(label='Библиотека', menu=library_menu)
    root.config(menu=main_menu)


def set_main_graph_settings():
    width, height = 270, 540
    root.geometry(f'{width}x{height}+'
                  f'{(root.winfo_screenwidth() - width) // 2}+'
                  f'{(root.winfo_screenheight() - height) // 2}')
    root.resizable(False, False)


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Органайзер 2.0 BETA')
    set_main_graph_settings()
    show_menus()
    init_cells()
    root.mainloop()
