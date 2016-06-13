
import os.path
import time


def date_str_cmp(s1, s2):
    day1 = int(s1.split("-")[4])
    day2 = int(s2.split("-")[4])
    return cmp(day1, day2)


def get_subdirs(a_dir):
        return [name for name in os.listdir(a_dir)
                if os.path.isdir(os.path.join(a_dir, name))]
