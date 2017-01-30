import zipfile
from zipfile import ZipFile
import os
import shutil

d = {} # словарь
f = open('text.txt', 'r', encoding='utf8')

# Заполнение словаря
for line in f:
    k = line.replace("\n","").split(None, 1)
    d[k[0]] = k[1]

f.close()

print(d)


#fname = 'ex1/zadanie-1---mashinnaya-arifmetika_20170130-235632.zip'
fname = 'ex2/zadanie-2---kvadratnoe-uravnenie_20170131-002923.zip'
path, fname = os.path.split(fname)
os.chdir(path)

###import pdb; pdb.set_trace()

# Проверка на zip
print(zipfile.is_zipfile(fname))

# Открыть архив для чтения и распоковать
z = ZipFile(fname, 'r')
z.extractall()
z.close()

#Список имен файлов
sps = os.listdir(path=os.getcwd())

#Смена директории
###os.chdir(fname)

for i in range (len(sps)):
    # Проверка является ли файл .py или .ipynb
    if (sps[i].find(".py") != -1)or(sps[i].find(".ipynb") != -1):
        for key in d:
            if (sps[i].find(key) != -1):
                dirnew = os.getcwd() + '/' + str(key) + '/' + sps[i]
                dirold = os.getcwd() + '/' + sps[i]
                os.renames(dirold, dirnew)

                

