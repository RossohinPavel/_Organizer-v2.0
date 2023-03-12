import pickle


with open ('../Logs/2023-03-12.pcl', 'rb') as file:
    print(pickle.load(file))
