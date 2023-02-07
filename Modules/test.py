import pickle


with open('../Configs/library.pcl', 'rb') as file:
    for k, v in pickle.load(file).items():
        print(k)
        print(v)