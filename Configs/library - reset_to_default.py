import pickle

LIBRARY = {
    "Фотокнига Стандарт": {},
    "Фотокнига ЛЮКС": {},
    "Фотокнига Классик": {},
    "Фотопланшет Стандарт": {},
    "Фотокнига Flex Bind": {},
    "Layflat": {},
    "Фотоальбом полиграфический": {},
    "Фотоальбом PUR": {},
    "Фотожурнал": {},
    "Фотопапка": {},
    "Фотопечать SRA": {},
    "Субпродукты": {}
}


with open('library.pcl', 'wb') as file:
    pickle.dump(LIBRARY, file)