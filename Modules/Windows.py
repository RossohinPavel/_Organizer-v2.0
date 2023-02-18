import re
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox as tkmb
from tkinter import filedialog as tkfd
from tkinter import colorchooser as tkcc

import Modules.Configs as Conf
import Modules.Roddom as Roddom
import Modules.FileProcessor as FileProc
import Modules.Library as Lib
import Modules.LogCreator as Log
import Modules.Information as Inf


class Window(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_cells()
        self.show_menus()
        self.set_main_graph_settings()

    def init_cells(self):
        def init_roddom_window(): RoddomWindow(self)

        def init_log(): Log.main()

        def init_sticgen(): StickerGenWindow(self)

        def init_smart_proc_window(): SmartProcWindow(self)

        def init_backup_window(): BackUpWindow(self)

        info_cell_label = CellLabel(master=self, label_text='Работа с заказами', label_color='#ed95b7')
        info_cell_label.pack()
        info_cell = CellTwoButton(master=self, bt_l_name='Обновить БД', bt_r_name='СтикГен',
                                  bt_l_func=init_log, bt_r_func=init_sticgen)
        info_cell.pack()
        smart_proc_label = CellLabel(master=self, label_color='dark salmon', label_text='Умная обработка')
        smart_proc_label.pack()
        smart_button = CellOneButton(master=self, func_name='Подготовка к печати', pd_x=10, func=init_smart_proc_window)
        smart_button.pack()
        bup_label = CellLabel(master=self, label_color='#adc6ed', label_text='Бакап файлов заказа')
        bup_label.pack()
        bup_button = CellOneButton(master=self, func_name='Подготовка к печати', pd_x=10, func=init_backup_window)
        bup_button.pack()
        fotoprint_label = CellLabel(master=self, label_color='pale green1', label_text='Фотопечать')
        fotoprint_label.pack()
        roddom_cell = CellOneButton(master=self, func_name='Роддом', func=init_roddom_window, pd_x=50)
        roddom_cell.pack()

    def set_main_graph_settings(self):
        self.title('Органайзер 2_0 BETA')
        width, height = 270, 240
        self.geometry(f'{width}x{height}+'
                      f'{(self.winfo_screenwidth() - width) // 2}+'
                      f'{(self.winfo_screenheight() - height) // 2}')
        self.resizable(False, False)

    def show_menus(self):
        def init_settings_window(): SettingsWindow(self)

        def init_add_to_lib_window(): AddToLibWindow(self)

        def init_change_lib_window(): ChangeLibWindow(self)

        def init_delete_from_lib_window(): DeleteFromLibWindow(self)

        settings_menu = tk.Menu(tearoff=0)
        settings_menu.add_command(label="Общие настройки", command=init_settings_window)

        library_menu = tk.Menu(tearoff=0)
        library_menu.add_command(label='Добавить продукт', command=init_add_to_lib_window)
        library_menu.add_command(label='Изменить продукт', command=init_change_lib_window)
        library_menu.add_command(label='Удалить продукт', command=init_delete_from_lib_window)

        main_menu = tk.Menu()
        main_menu.add_cascade(label="Настройки", menu=settings_menu)
        main_menu.add_cascade(label='Библиотека', menu=library_menu)
        self.config(menu=main_menu)


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


class CellTwoButton(tk.Frame):
    """Конструктор для парных кнопок"""

    def __init__(self, bt_l_name='Название кнопки', bt_l_func=None, bt_r_name='Название кнопки', bt_r_func=None,
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config(width=270)
        self.l_button = tk.Button(self, text=bt_l_name, command=bt_l_func, relief=tk.FLAT, fg="#eee", bg="#454545")
        self.l_button.pack(side='left', ipadx=20, padx=10, pady=3)
        self.r_button = tk.Button(self, text=bt_r_name, command=bt_r_func, relief=tk.FLAT, fg="#eee", bg="#454545")
        self.r_button.pack(side='right', ipadx=20, padx=10, pady=3)


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
        text_res_cb = ttk.Checkbutton(frame, text='Сохранять результаты в sum.txt', variable=self.text_res_enable)
        text_res_cb.place(x=3, y=3)
        mrk_form_cb = ttk.Checkbutton(frame, text='Формировать .mrk файл', variable=self.mrk_form_enable)
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
        progressbar = ttk.Progressbar(self.info_frame, orient=tk.HORIZONTAL, mode="determinate", length=254)
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
        self.resizable(False, False)
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
    __FRAMES = {'short_name': ('combo', 'Выберите короткое имя', 2, 41),
                'book_format': ('combo', 'Выберите формат книги', 2, 82),
                'book_option': ('radio', 'Выберите опции сборки книги', 2, 123),
                'lamination': ('radio', 'Выберите ламинацию для продукта', 2, 164),
                'cover_print_mat': ('combo', 'Выберите печатный материал обложки', 250, 0),
                'cover_carton': ('combo', 'Выберите картонку для обложки', 250, 41),
                'page_print_mat': ('combo', 'Выберите печатный материал разворотов', 250, 82),
                'dc_break': ('check', 'Раскодировка с дублированием', 270, 180),
                'book_type': ('radio', 'Выберите тип обложки', 250, 123),
                'gl_value': ('entry', "Введите значение в мм для направляющих", 2, 210),
                'gl_length': ('entry', 'Введите длинну направляющих в мм', 2, 251),
                'cover_canal': ('combo', "Выберите 'канал' обложки", 250, 210),
                'page_canal': ('combo', "Выберите 'канал' разворотов", 250, 251),
                'dc_overlap': ('entry', 'НАХЛЕСТ для переплета в мм', 250, 210),
                'dc_top_indent': ('entry', 'Введите значение отступа СВЕРХУ в мм', 250, 251),
                'dc_left_indent': ('entry', 'Введите значение отступа СЛЕВА в мм', 250, 291)
                }

    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.product_description = None  # Для хранения словаря с описанием категорий продукта и типов значений
        self.library_dct = Conf.read_pcl('library')  # Словарь с сохраненными именами
        # Переменные, которые заполняются в зависимости от выбранного окна и выбранного действия
        self.category_combobox = None  # Для отрисовки комбобокса категорий и сохранения его значений
        self.names_combobox = None  # Для отрисовки комбобокса с сохраненными именами продуктов
        self.product_menus_frame = None  # Фрейм, на котором рисуются менюшки с выбором
        self.resizable(False, False)

    def show_category_frame(self, cb_bind_func):
        """Функция для обображения фрейма категорий. Инициализирует комбобокс с нужным Событием."""
        frame = tk.Frame(self, width=500, height=51)
        label = tk.Label(frame, text='Выберите категорию')
        label.place(x=200, y=1)
        self.category_combobox = ttk.Combobox(frame, state="readonly", width=40, values=Lib.Product.product_type())
        self.category_combobox.bind('<<ComboboxSelected>>', cb_bind_func)
        self.category_combobox.place(x=130, y=25)
        separator = tk.Canvas(frame, width=496, height=1, bg='black')
        separator.place(x=0, y=46)
        frame.pack()

    def show_saved_names_frame(self, cb_bind_func):
        """Функция для отрисовки фрейма с отображением сохраненных имен"""
        frame = tk.Frame(self, width=500, height=50)
        label = tk.Label(frame, text='Выберите продукт')
        label.place(x=200, y=1)
        self.names_combobox = ttk.Combobox(frame, state="readonly", width=40)
        self.names_combobox.bind('<<ComboboxSelected>>', cb_bind_func)
        self.names_combobox.place(x=130, y=25)
        separator = tk.Canvas(frame, width=496, height=1, bg='black')
        separator.place(x=0, y=46)
        frame.pack()

    def show_product_menus(self):
        """Функция для отрисовки фрейма менюшек выбора значений"""
        self.product_menus_frame = tk.Frame(self, width=500, height=330)
        self.product_menus_frame.pack()

    def show_buttons(self, text, command):
        """Функция для отрисовки кнопок"""
        frame = tk.Frame(self, width=500, height=30)
        frame.pack()
        button = tk.Button(frame, **self.style, text=text, width=30, command=command)
        button.place(x=140, y=2)

    def product_menus_frame_clearing(self):
        """Очистка меню-виджета от ненужных фреймов"""
        for widget in self.product_menus_frame.winfo_children():
            widget.destroy()

    def __show_entry_frame(self, text, txt_var_name, x, y):
        """Конструктор фрейма для отрисовки Entry виджета"""
        text_label = tk.Label(self.product_menus_frame, text=text)
        text_label.place(x=x, y=y)
        self.__dict__[txt_var_name] = tk.StringVar(self.product_menus_frame)
        entry = tk.Entry(self.product_menus_frame, width=39, textvariable=self.__dict__[txt_var_name])
        entry.place(x=x, y=y + 20)

    def __show_combobox_frame(self, text, cb_var, cb_val, x, y):
        """Конструктор фрейма для отрисовки Комбобокс виджета"""
        text_label = tk.Label(self.product_menus_frame, text=text)
        text_label.place(x=x, y=y)
        self.__dict__[cb_var] = ttk.Combobox(self.product_menus_frame, width=36, state="readonly", values=cb_val)
        self.__dict__[cb_var].place(x=x, y=y + 20)

    def __show_check_frame(self, text, var, x, y):
        """Конструктор для отрисовки чек фреймов"""
        self.__dict__[var] = tk.BooleanVar(self.product_menus_frame)
        self.__dict__[var].set(True)
        check_btn = tk.Checkbutton(self.product_menus_frame, text=text, variable=self.__dict__[var])
        check_btn.place(x=x, y=y)

    def __show_radio_frame(self, text, radio_var, radio_val, x, y):
        text_label = tk.Label(self.product_menus_frame, text=text)
        text_label.place(x=x, y=y)
        self.__dict__[radio_var] = tk.StringVar(self.product_menus_frame, value=radio_val[0])
        indents = ((0, 20), (50, 20), (100, 20))
        if radio_var == '_book_type':
            indents = ((0, 20), (0, 40), (80, 20), (80, 40))
        for i, name in enumerate(radio_val):
            i_x, i_y = indents[i]
            x_pos, y_pos = x + i_x, y + i_y
            radio = ttk.Radiobutton(self.product_menus_frame, text=name, value=name, variable=self.__dict__[radio_var])
            radio.place(x=x_pos, y=y_pos)

    def init_menu_lines(self):
        """Отображает менюшки на self.product_menus_frame согласно выбранному продукту"""
        setattr(self, '_product_name', None)
        self.__show_entry_frame('Введите полное имя продукта', '_product_name', 2, 0)
        book_type = self.category_combobox.get()
        for key in self.product_description:
            frame = self.__FRAMES.get(key)
            var = f'_{key}'
            tip, text, x, y = frame
            setattr(self, var, None)
            if tip == 'entry':
                self.__show_entry_frame(text, var, x, y)
            if tip == 'combo':
                self.__show_combobox_frame(text, var, getattr(Lib.Product, key)(), x, y)
            if tip == 'check':
                self.__show_check_frame(text, var, x, y)
            if tip == 'radio':
                self.__show_radio_frame(text, var, getattr(Lib.Product, key)(book_type), x, y)
        separator = tk.Canvas(self.product_menus_frame, width=496, height=1, bg='black')
        separator.place(x=0, y=207)

    def get_values_from_menus(self):
        """Получение введенных значений"""
        category = self.category_combobox.get()
        if not category:
            return
        full_name = getattr(self, '_product_name').get()
        values = {'category': category}
        for key in self.product_description:
            value = self.__dict__[f'_{key}'].get()
            if key in ('gl_value', 'gl_length', 'dc_overlap', 'dc_top_indent', 'dc_left_indent'):
                value = int(value) if value.isdigit() else 0
            if value or key in ('dc_break', 'gl_value', 'gl_length', 'dc_overlap', 'dc_top_indent', 'dc_left_indent'):
                values[key] = value
        if len(values) - 1 != len(self.product_description) or not full_name:
            return
        return {full_name: values}

    def clear_menus_entered_values(self):
        """Установка значений в комбобоксах и энтри на пустые"""
        self.__dict__['_product_name'].set('')
        for key in self.product_description:
            if self.__FRAMES.get(key)[0] in ('combo', 'entry'):
                self.__dict__[f'_{key}'].set('')

    def set_values_to_enter_menus(self, name):
        """Установка значений в комбобоксах и энтри на сохраненные"""
        self.__dict__['_product_name'].set(name)
        product_dict = self.library_dct[name]
        for key in self.product_description:
            self.__dict__[f'_{key}'].set(product_dict[key])

    def save_library(self):
        """Пишем в Либу"""
        Conf.write_pcl('library', self.library_dct)


class AddToLibWindow(LibraryWindow):
    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.title('Добавление продукта')
        self.show_category_frame(self.category_event)
        self.show_product_menus()
        self.show_buttons('Сохранить продукт в библиотеке', self.add_button)
        self.to_parent_center()
        self.focus()

    def category_event(self, event=None):
        self.product_menus_frame_clearing()
        self.product_description = Lib.Product.get_product_descr(self.category_combobox.get())
        self.init_menu_lines()

    def add_button(self):
        dct = self.get_values_from_menus()
        if dct:
            self.library_dct.update(dct)
            self.clear_menus_entered_values()
            self.save_library()
            tkmb.showinfo(title='Добавление продукта', message='Продукт успешно добавлен в библиотеку')


class ChangeLibWindow(LibraryWindow):
    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.title('Измeнение продукта')
        self.show_category_frame(self.category_event)
        self.show_saved_names_frame(self.names_event)
        self.show_product_menus()
        self.show_buttons('Обновить значения', self.change_button)
        self.to_parent_center()
        self.focus()

    def category_event(self, event=None):
        self.names_combobox.set('')
        category = self.category_combobox.get()
        self.names_combobox.config(values=tuple(k for k, v in self.library_dct.items() if v['category'] == category))
        self.product_menus_frame_clearing()

    def names_event(self, event=None):
        name = self.names_combobox.get()
        if name:
            self.product_menus_frame_clearing()
            self.product_description = Lib.Product.get_product_descr(self.category_combobox.get())
            self.init_menu_lines()
            self.set_values_to_enter_menus(name)

    def change_button(self):
        dct = self.get_values_from_menus()
        if dct:
            self.library_dct.update(dct)
            self.clear_menus_entered_values()
            self.save_library()
            self.names_combobox.set('')
            tkmb.showinfo(title='Изменение продукта', message='Значения продукта успешно обновлены')


class DeleteFromLibWindow(LibraryWindow):
    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.title('Удаление продукта')
        self.show_category_frame(self.category_event)
        self.show_saved_names_frame(None)
        self.show_buttons('Удалить продукт из библиотеки', self.del_button)
        self.to_parent_center()
        self.focus()

    def category_event(self, event=None):
        self.names_combobox.set('')
        category = self.category_combobox.get()
        self.names_combobox.config(values=tuple(k for k, v in self.library_dct.items() if v['category'] == category))

    def del_button(self):
        product_to_del = self.names_combobox.get()
        if product_to_del:
            self.library_dct.pop(product_to_del)
            self.save_library()
            self.names_combobox.set('')
            self.category_event()
            tkmb.showinfo(title='Удаление продукта', message='Продукт удален из библиотеки')


class StickerGenWindow(ChildWindow):
    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.title('Генерация наклеек')
        self.order_name = tk.StringVar()
        self.order_info = tk.StringVar()
        self.library_dct = Conf.read_pcl('library')
        self.show_order_entry_frame()
        self.show_order_info_frame()
        self.show_buttons_frame()
        self.resizable(False, False)
        self.to_parent_center()
        self.grab_set()
        self.wait_window()

    def show_order_entry_frame(self):
        frame = tk.Frame(master=self, height=52, width=300)
        label = tk.Label(frame, text='Введите номер заказа')
        label.place(x=86, y=1)
        entry = tk.Entry(frame, textvariable=self.order_name)
        entry.place(x=55, y=27)
        entry.bind('<Return>', self.get_order_info)
        entry.focus_set()
        button = tk.Button(frame, text='Получить', **self.style, command=self.get_order_info)
        button.place(x=185, y=24)
        frame.pack()

    def get_order_info(self, event=None):
        order_name = self.order_name.get()
        for log_dict in Conf.read_pcl_log_for_processing():
            if order_name in log_dict:
                self.order_info.set(Inf.StickerInfo(order_name, log_dict[order_name], self.library_dct).main())
                break
        self.order_name.set('')
        self.to_clipboard()

    def show_order_info_frame(self):
        frame = tk.Frame(self, width=300, height=200)
        frame.pack()
        label = tk.Label(frame, justify=tk.LEFT, textvariable=self.order_info)
        label.place(x=1, y=1)

    def show_buttons_frame(self):
        frame = tk.Frame(self, width=300, height=28)
        button1 = tk.Button(frame, text='Скопировать в буфер', **self.style, command=self.to_clipboard)
        button1.place(x=1, y=1)
        button2 = tk.Button(frame, text='Закрыть', **self.style, command=self.destroy)
        button2.place(x=242, y=1)
        frame.pack()

    def to_clipboard(self):
        self.clipboard_clear()
        self.clipboard_append(self.order_info.get())


class ProcessingWindow(ChildWindow):
    """Конструктор для окон обработчика заказов"""

    def __init__(self, parent_root):
        super().__init__(parent_root)
        self.order_name_label = None  # Общие переменные для вывода информации
        self.order_name_entry_var = tk.StringVar(self)
        self.order_exist = None
        self.init_local_variables()  # Инициализируем локальные переменные
        self.processing_info = None
        self.processing_pb = None
        self.__main()

    def init_local_variables(self):
        pass

    def reset_settings_to_default(self):
        pass

    def show_main_frame(self):
        pass

    def get_order_settings(self) -> dict:
        pass

    def __main(self):
        self.config(border=1, relief='solid')
        self.bind('<Control-Return>', self.init_proc)
        self.order_name_entry_widget()
        self.order_name_label = ttk.Label(master=self, text='Для запуска обработчика введите номер заказа')
        self.order_name_label.pack()
        self.show_main_frame()
        self.buttons_frame()
        self.overrideredirect(True)
        self.to_parent_center()

    def order_name_entry_widget(self):
        frame = tk.Frame(master=self, width=300, height=30)
        label = ttk.Label(master=frame, text='Введите номер заказа:')
        label.place(x=20, y=4)
        entry = ttk.Entry(master=frame, width=10, textvariable=self.order_name_entry_var)
        entry.bind("<Return>", self.get_order_dict)
        entry.bind('<Control-Return>', self.init_proc)
        entry.focus_set()
        entry.place(x=150, y=4)
        button = tk.Button(master=frame, **self.style, text='Ввод', padx=10, command=self.get_order_dict)
        button.place(x=220, y=1)
        canvas = tk.Canvas(master=frame, width=296, height=1, bg='black')
        canvas.place(x=0, y=26)
        frame.pack()

    def get_order_dict(self, event=None):
        order_name = self.order_name_entry_var.get()
        self.order_exist = None
        if re.fullmatch(r'\d{6}', order_name):
            for day_dict in Conf.read_pcl_log_for_processing():
                if order_name in day_dict:
                    self.order_exist = {'PATH': day_dict['PATH'], 'NAME': order_name, 'CONTENTS': day_dict[order_name]}
                    break
        if self.order_exist:
            self.order_name_label.config(text=f'Обработка заказа: {order_name}')
        else:
            self.order_name_label.config(text='Для запуска обработчика введите номер заказа')
        self.order_name_entry_var.set('')
        self.reset_settings_to_default()

    def buttons_frame(self):
        frame = tk.Frame(master=self, width=300, height=33)
        canvas = tk.Canvas(master=frame, width=296, height=1, bg='black')
        canvas.place(x=0, y=0)
        run_button = tk.Button(master=frame, **self.style, text='Запустить', padx=5, command=self.init_proc)
        run_button.place(x=1, y=5)
        close_button = tk.Button(master=frame, **self.style, text='Выход', command=self.stop_func, padx=5)
        close_button.place(x=245, y=5)
        frame.pack()

    def stop_func(self):
        try:
            self.destroy()
        except:
            pass

    def show_progress_widget(self):
        for name in self.winfo_children():
            name.destroy()
        self.geometry('300x105')
        self.to_parent_center()
        self.processing_info = ttk.Label(self,
                                         text='Номер заказа\nКоличество и название тиража\nНомер и название файла')
        self.processing_info.place(x=1, y=1)
        self.processing_pb = ttk.Progressbar(self, mode="determinate", length=296)
        self.processing_pb.place(x=1, y=51)
        self.close_button = tk.Button(self, text='Остановить', **self.style, command=self.stop_func)
        self.close_button.place(x=221, y=75)

    def init_proc(self, event=None):
        if not self.order_exist:
            return
        order_settings = self.get_order_settings()
        self.show_progress_widget()
        self.processing_info.config(text='Формирую задачу')
        order_obj = None
        if type(self) == BackUpWindow:
            order_obj = FileProc.OrderBuckup(order_settings)
        if type(self) == SmartProcWindow:
            return
        order_obj.get_file_list()
        total_count = order_obj.get_file_len()
        counter = 0
        self.processing_pb['maximum'] = total_count
        self.processing_pb['value'] = 0
        self.processing_info.config(text='Создаю каталоги')
        order_obj.make_dirs()
        self.update()
        for order, content, file in order_obj.processing_run():
            counter += 1
            self.processing_pb['value'] += 1
            self.processing_info.config(text=f'{order}\n{content}\n{total_count}/{counter} -- {file}')
            self.update()
        self.destroy()


class SmartProcWindow(ProcessingWindow):
    def __init__(self, parent_root):
        self.settings_dict = {}
        super().__init__(parent_root)
        self.grab_set()
        self.wait_window()

    def type_line_widget(self, book_type, text, frame_height, check_option):
        self.settings_dict[book_type] = {}
        frame = tk.Frame(master=self, width=300, height=frame_height)
        label = ttk.Label(master=frame, text=text)
        label.place(x=0, y=0)
        combobox = ttk.Combobox(frame, width=45, state="readonly")
        combobox.place(x=4, y=20)
        coords = ((20, 41), (150, 41), (20, 61), (150, 61), (20, 81))
        self.settings_dict[book_type].update({'label': label})
        self.settings_dict[book_type].update({'combobox': combobox})
        if check_option:
            self.settings_dict[book_type]['checkbutton'] = {}
            for i, v in enumerate(check_option):
                pos_x, pos_y = coords[i]
                frame.__dict__[v] = tk.BooleanVar(frame)
                frame.__dict__[v].set(False)
                check_btn = ttk.Checkbutton(frame, text=v, variable=frame.__dict__[v])
                check_btn.place(x=pos_x, y=pos_y)
                self.settings_dict[book_type]['checkbutton'].update({v: (check_btn, frame.__dict__[v])})
        frame.pack()

    def show_undetected_edition_frame(self):
        self.settings_dict['undetected'] = {}
        label = ttk.Label(self, text='Список нераспознанных тиражей')
        label.pack()
        combobox = ttk.Combobox(self, width=45)
        combobox.pack()
        self.settings_dict['undetected'].update({'label': label, 'combobox': combobox})

    def disable_info_widgets(self):
        for vals in self.settings_dict.values():
            vals['label'].config(state=tk.DISABLED)
            vals['combobox'].config(state=tk.DISABLED)
            vals['combobox'].set('')
            cbuns = vals.get('checkbutton', '')
            if cbuns:
                for widget, var in cbuns.values():
                    widget.config(state=tk.DISABLED)
                    var.set(False)

    def enable_info_widgets(self, order_dct):
        for key, value in order_dct.items():
            widgets = self.settings_dict[key]
            widgets['label'].config(state=tk.NORMAL)
            widgets['combobox'].config(state='readonly', values=value)
            cbuns = widgets.get('checkbutton', '')
            if cbuns:
                for name, tup in cbuns.items():
                    tup[0].config(state=tk.NORMAL)
                    if key == 'fotobook' and name in ('Обводка', 'Направляющие', 'Формировать .mrk') or key in ('polibook', 'albums'):
                        tup[1].set(True)

    def show_main_frame(self):
        self.type_line_widget('fotobook', 'Книги на Фотобумаге -- Раскидывание по каналам', 100,
                              ('Обводка', 'Переименование', 'Направляющие', 'Добавить Бек-Принт', 'Формировать .mrk'))
        self.type_line_widget('polibook', "Layflat'ы -- Извлечение Спец-Папок", 61, ('Направляющие', 'Переименование'))
        self.type_line_widget('albums', "Альбомы, PUR, FlexBind'ы -- Раскодировка", 61,
                              ('Направляющие', 'Переименование'))
        self.type_line_widget('journals', 'Журналы -- Раскодировка', 41, None)
        self.show_undetected_edition_frame()
        self.disable_info_widgets()

    def get_order_dict(self, event=None):
        super().get_order_dict()
        self.disable_info_widgets()
        if not self.order_exist:
            return
        combination = {"Фотокнига Премиум": 'fotobook', "Фотокнига выпускника": 'fotobook', 'Layflat': 'polibook',
                       'Фотокнига Flex Bind': 'albums', 'Альбом и PUR': 'albums', 'Фотожурнал': 'journals'}
        book_dict = {}
        for name, values in self.order_exist['CONTENTS'].items():
            book_type = values[1]
            if book_type is not None:
                book_type = book_type[1]
            if book_type in combination:
                book_dict.setdefault(combination[book_type], []).append(name)
            if book_type not in combination and book_type != 'PHOTO':
                book_dict.setdefault('undetected', []).append(name)
        self.enable_info_widgets(book_dict)
        print(self.settings_dict)


class BackUpWindow(ProcessingWindow):
    def __init__(self, parent_root):
        self.order_list_radio = None
        self.order_list_cb = None
        self.order_type_radio = None
        super().__init__(parent_root)
        self.grab_set()
        self.wait_window()

    def init_local_variables(self):
        self.order_list_radio = tk.StringVar(self)
        self.order_type_radio = tk.StringVar(self)
        self.reset_settings_to_default()

    def show_main_frame(self):
        frame = tk.Frame(self, width=300, height=75)
        order_list_radio1 = ttk.Radiobutton(master=frame, text='Бакапнуть все', command=self.order_list_radio_switcher,
                                            value='ALL', variable=self.order_list_radio)
        order_list_radio1.place(x=1, y=2)
        order_list_radio2 = ttk.Radiobutton(master=frame, text='Выбранный тираж',
                                            command=self.order_list_radio_switcher,
                                            value='CHOSEN', variable=self.order_list_radio)
        order_list_radio2.place(x=155, y=2)
        self.order_list_cb = ttk.Combobox(master=frame, state=tk.DISABLED, width=46)
        self.order_list_cb.place(x=1, y=26)
        type_radio1 = ttk.Radiobutton(master=frame, text='Все файлы',
                                      value='ALL', variable=self.order_type_radio)
        type_radio1.place(x=1, y=51)
        type_radio2 = ttk.Radiobutton(master=frame, text='Спец-папки',
                                      value='CCV', variable=self.order_type_radio)
        type_radio2.place(x=108, y=51)
        type_radio3 = ttk.Radiobutton(master=frame, text='Экзепляры',
                                      value='EX', variable=self.order_type_radio)
        type_radio3.place(x=216, y=51)
        frame.pack()

    def reset_settings_to_default(self):
        self.order_list_radio.set('ALL')
        self.order_type_radio.set('CCV')
        if self.order_list_cb:
            self.order_list_cb.config(state=tk.DISABLED)

    def order_list_radio_switcher(self):
        order_list = self.order_list_radio.get()
        if order_list == 'ALL':
            self.order_list_cb.config(state=tk.DISABLED)
        if order_list == 'CHOSEN':
            if self.order_exist:
                self.order_list_cb.config(values=tuple(self.order_exist['CONTENTS'].keys()))
            self.order_list_cb.config(state="readonly")

    def get_order_settings(self) -> dict:
        if self.order_list_radio.get() == 'CHOSEN':
            chosen_order = self.order_list_cb.get()
            if chosen_order:
                self.order_exist['CONTENTS'] = {chosen_order: self.order_exist['CONTENTS'][chosen_order]}
        self.order_exist.update({'TYPE': self.order_type_radio.get()})
        return self.order_exist
