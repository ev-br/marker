from __future__ import division, print_function, absolute_import
import argparse
import zipfile
import os

def fill_namedict(fname='name_map.txt'):
    # Заполнение словаря имен
    d = {}
    with open(fname, 'r', encoding='utf8') as f: 
        for line in f:
            if line.startswith("#"):
                continue
            k = line.replace("\n","").split(None, 1)
            d[k[0]] = k[1]
    return d


class Student(object):
    """Basic info: name, lms_id, list number.

    Also may hold the marking results (mark, log etc)
    """
    def __init__(self, lms_id, name=None, list_num=None):
        self.lms_id = lms_id
        self._name = name
        self._list_num = list_num

    @property
    def name(self):
        if self._name is not None:
            return self._name
        else:
            return self.lms_id

    @property
    def list_num(self):
        if self._list_num is not None:
            return int(self._list_num)
        else:
            return -1


def fill_cohort(name_dict_fname="name_map.txt",
                num_dict_fname="number_map.txt"):
    """Construct the dict of {lms_id: Student(...)}
    """
    name_dict = fill_namedict(name_dict_fname)
    num_dict = fill_namedict(num_dict_fname)

    cohort = {}
    for lms_id in name_dict:
        student = Student(lms_id=lms_id,
                          name=name_dict[lms_id],
                          list_num=num_dict[lms_id])
        cohort.update({lms_id: student})
    return cohort


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
