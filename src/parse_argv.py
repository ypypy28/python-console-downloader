import os
import argparse


def validate_speed(line: str) -> int:
    try:
        return int(line)
    except ValueError:
        suf = line[-1]
        if suf == 'k':
            return int(line[:-1])*1024
        elif suf == 'm':
            return int(line[:-1])*1024*1024
        else:
            print("You've entered wron suffix for speed\n"
                  "Try use k for kilobytes or m for megabytes"
                  "or write speed in bytes without any suffix")
            exit()


def validate_dir(path_to_dir: str) -> str:
    if not os.path.isdir(path_to_dir):
        os.mkdir(path_to_dir)
    return path_to_dir


def validate_file(path_to_file: str) -> str:
    try:
        f = open(path_to_file, 'r')
    except IOError:
        print(("ERROR: can't open file {0}"
               " (does it exist?)").format(path_to_file))
        exit()
    else:
        f.close()
        return path_to_file


def get_args() -> dict:
    parser = argparse.ArgumentParser(description="Download files \
                                                  from links from a file")
    parser.add_argument('-f',
                        type=validate_file,
                        nargs=1,
                        required=True,
                        help="путь к файлу со списком ссылок")

    parser.add_argument('-o',
                        type=validate_dir,
                        nargs=1,
                        required=True,
                        help="путь к папке, где сохранять файлы")
    parser.add_argument('-n',
                        type=int,
                        nargs=1,
                        required=True,
                        help="количество одновременно \
                              качающих потоков (1,2,3,4...)")

    parser.add_argument('-l',
                        type=validate_speed,
                        nargs=1,
                        required=True,
                        help="общее ограничение на скорость скачивания,\
                              для всех потоков")
    args = parser.parse_args()
    return vars(args)
