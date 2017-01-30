from __future__ import division, print_function, absolute_import
import argparse
import zipfile
import os

def fill_namedict(fname='text.txt'):
    # Заполнение словаря имен
    d = {}
    with open(fname, 'r', encoding='utf8') as f: 
        for line in f:
            k = line.replace("\n","").split(None, 1)
            d[k[0]] = k[1]
    return d


def unpack(zip_fname, name_dict):
    """Unpack the zip archive into per-student folders
    """

    # XXX: relative paths etc
    path, fname = os.path.split(zip_fname)
    os.chdir(path)

    if not zipfile.is_zipfile(fname):
        raise ValueError("%s is not a zip file" % fname)

    # Открыть архив для чтения и распоковать
    with zipfile.ZipFile(fname, 'r') as z:
        z.extractall()

    # Список имен файлов
    sps = os.listdir(path=os.getcwd())

    for fname in sps:
        # Проверка является ли файл .py или .ipynb
        if (fname.find(".py") != -1)or(fname.find(".ipynb") != -1):
            for key in name_dict:
                if key in fname:
                    dirnew = os.path.join(os.getcwd(), str(key), fname)
                    dirold = os.path.join(os.getcwd(), fname)
                    os.renames(dirold, dirnew)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("path",
                        help="Path to the zip file from LMS.")
    args = parser.parse_args()

    # fill the name map & unpack
    d = fill_namedict()
    unpack(args.path, d)
