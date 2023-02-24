


main_dct = {'1': 1, '2': {'21': 21, '22': 22}}
children = main_dct['2']
children.update({'23': 23})
print(main_dct)
