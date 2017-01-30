from __future__ import division, print_function, absolute_import
import zipfile
import os

# Заполнение словаря имен
d = {}
with open('text.txt', 'r', encoding='utf8') as f: 
    for line in f:
        k = line.replace("\n","").split(None, 1)
        d[k[0]] = k[1]

#fname = 'ex1/zadanie-1---mashinnaya-arifmetika_20170130-235632.zip'
fname = 'ex2/zadanie-2---kvadratnoe-uravnenie_20170131-002923.zip'
path, fname = os.path.split(fname)
os.chdir(path)

# Проверка на zip
print(zipfile.is_zipfile(fname))

# Открыть архив для чтения и распоковать
with zipfile.ZipFile(fname, 'r') as z:
    z.extractall()

# Список имен файлов
sps = os.listdir(path=os.getcwd())

for i in range (len(sps)):
    # Проверка является ли файл .py или .ipynb
    if (sps[i].find(".py") != -1)or(sps[i].find(".ipynb") != -1):
        for key in d:
            if (sps[i].find(key) != -1):
                dirnew = os.getcwd() + '/' + str(key) + '/' + sps[i]
                dirold = os.getcwd() + '/' + sps[i]
                os.renames(dirold, dirnew)

