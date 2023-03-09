import os
import pickle


def write_txt(path, string):
    with open(path, 'w') as file:
        file.write(string)


def write_txt_from_list(path, lst):
    generator = (x + '\n' for x in lst)
    with open(path, 'w') as file:
        file.writelines(generator)


def write_pcl(name, value):
    with open(f'Configs/{name}.pcl', 'wb') as file:
        pickle.dump(value, file)


def read_pcl(name):
    with open(f'Configs/{name}.pcl', 'rb') as file:
        return pickle.load(file)


def write_pcl_log(name, value):
    with open(f'Logs/{name}.pcl', 'wb') as file:
        pickle.dump(value, file)


def read_pcl_log(name) -> dict:
    try:
        with open(f'Logs/{name}.pcl', 'rb') as file:
            return pickle.load(file)
    except FileNotFoundError:
        write_pcl_log(name, {})
        return {}


def read_pcl_log_for_processing():
    for logfile in reversed(os.listdir('Logs')):
        with open(f'Logs/{logfile}', 'rb') as file:
            yield pickle.load(file)


def get_logs_list() -> tuple:
    return tuple(os.listdir(f'Logs/'))


def read_chosen_pcl_log(date1, date2):
    for log in os.listdir('Logs'):
        if date1 <= log[:-4] <= date2:
            with open(f'Logs/{log}', 'rb') as file:
                yield pickle.load(file)
