import pickle

LIBRARY = {}


with open('library.pcl', 'wb') as file:
    pickle.dump(LIBRARY, file)