"""Органайзер. Версия 2_0"""
import multiprocessing
import pickle
import time

import Modules.Windows as Win


def read_config_autolog():
    with open('Configs/settings.pcl', 'rb') as file:
        return pickle.load(file)['autolog']


def window_run(q):
    q.put(True)
    Win.Window().mainloop()
    q.put(False)


def log_run(q):
    flag = True
    while flag:
        count = 20 * 5
        Win.Log.main()
        print('Происходит автоматиченская запись лога')
        while flag and count > 0:
            q.put(True)
            time.sleep(3)
            count -= 1
            flag = q.get()



if __name__ == '__main__':
    if read_config_autolog():
        q = multiprocessing.Queue()
        proc1 = multiprocessing.Process(target=window_run, args=(q,))
        proc2 = multiprocessing.Process(target=log_run, args=(q,))
        proc1.start()
        proc2.start()
        proc1.join()
        proc2.join()
    else:
        Win.Window().mainloop()
