import pickle


with open('../Configs/settings.pcl', 'rb') as file:
    print(pickle.load(file))