import multiprocessing
import time
import pickle


AUTOLOG = True


def func1(q):
    q.put(True)
    for i in range(3):
        print('func1')
        time.sleep(5)
    q.put(False)



def func2(q):
    while q.get():
        q.put(True)
        print('succes')
        time.sleep(3)
    print('end func2')



if __name__ == '__main__':
    q = multiprocessing.Queue()
    proc1 = multiprocessing.Process(target=func1, args=(q, ))
    proc2 = multiprocessing.Process(target=func2, args=(q, ))

    proc1.start()
    proc2.start()

    proc1.join()
    proc2.join()