import pickle


class SomeClass:
    __ATTR = 'test'

    @classmethod
    def some_func(cls):
        return 'test'


with open('test.pcl', 'wb') as file:
    pickle.dump(SomeClass(), file)