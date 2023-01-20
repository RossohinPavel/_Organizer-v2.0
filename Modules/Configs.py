import json


def read_json_config(name) -> dict:
    with open(f"Configs/{name}.json", "r") as file:
        return json.load(file)


def write_json_config(name, value):
    with open(f"Configs/{name}.json", "w") as write_file:
        json.dump(value, write_file, indent=4, ensure_ascii=False)


def write_txt(path, string):
    with open(path, 'w') as file:
        file.write(string)


def write_txt_from_list(path, lst):
    generator = (x + '\n' for x in lst)
    with open(path, 'w') as file:
        file.writelines(generator)
