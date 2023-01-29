import pickle


SETTINGS = {'autolog': False,
            'log_check_depth': 10,
            'order_main_dir': '',
            'fotoprint_temp_dir': '',
            'stroke_size': 4,
            'stroke_color': '#000000',
            'guideline_size': 4,
            'guideline_color': '#000000',
            'roddom_main_dir': '',
}


with open('settings.pcl', 'wb') as file:
    pickle.dump(SETTINGS, file)