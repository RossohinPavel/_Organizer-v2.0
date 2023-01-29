import pickle


with open('../Configs/settings.pcl', 'wb') as file:
    pickle.dump({'roddom_main_dir': '', 'fotoprint_temp_dir': ''}, file)


