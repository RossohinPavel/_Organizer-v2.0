import pickle


with open('../Configs/library.pcl', 'rb') as file:
    print(pickle.load(file))