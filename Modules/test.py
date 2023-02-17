import re


file_list = ('009__001.jpg', 'cover_009.jpg', '010__001-2_pcs.jpg', 'cover_010-2_pcs.jpg')


for name in file_list:
    if re.fullmatch(r'(?:\d{3}_|cover)_\d{3}(-\d{,3}_pcs)?\.jpg', name):
        print(name)
