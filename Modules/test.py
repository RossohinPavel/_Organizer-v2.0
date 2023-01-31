import os
import time


path = 'D:/тест/Book2/2023-01-30/301009/PHOTO/_ALL/Фотопечать'
paper_type = {'Глянцевая': 'Fuji Gloss', 'Матовая': 'Fuji Matt'}

start = time.time()
for i in range(50):
    dct = {}
    for paper in os.listdir(path):
        for form in os.listdir(f'{path}/{paper}'):
            paper_format, multiplicator = form[5:].split('--')
            page_len = 0
            for page in os.listdir(f'{path}/{paper}/{form}'):
                page_len += 1
            page_len *= int(multiplicator)
            dct.update({f'{paper_type[paper]} {paper_format}': page_len})
    # print(dct)

print('Методом тупого перебора -', time.time() - start)


start = time.time()
for i in range(50):
    dct = {}
    for paper in os.listdir(path):
        for form in os.listdir(f'{path}/{paper}'):
            paper_format, multiplicator = form[5:].split('--')
            name = f'{paper_type[paper]} {paper_format}'
            dct[name] = dct.get(name, 0) + len(os.listdir(f'{path}/{paper}/{form}')) * int(multiplicator)
    # print(dct)

print('Методом тупого перебора с len -', time.time() - start)

# start = time.time()
#
# for i in range(50):
#     k = lambda paper_type, page_format: paper_type[paper] + page_format[5:10]
#     v = lambda path, page_form:
#     dct = { for paper in os.listdir(path) for form in os.listdir(f'{path}/{paper}')}
#     for paper in os.listdir(path):
#         for form in os.listdir(f'{path}/{paper}'):
#             paper_format, multiplicator = form[5:].split('--')
#             page_len = len(os.listdir(f'{path}/{paper}/{form}'))
#             page_len *= int(multiplicator)
#             dct.update({paper_type[paper]: page_len})
#
#
# print('Методом генерации словари и доп функций', time.time() - start)