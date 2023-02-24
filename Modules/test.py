import pickle
import os


for log in os.listdir('../Logs'):
    with open(f'../Logs/{log}', 'rb') as file:
        print(pickle.load(file))