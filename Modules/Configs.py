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
