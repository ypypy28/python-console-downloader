import queue
import threading
import urllib.request
import time
from parse_argv import get_args


def download_file(url, name, dirname, speed):
    try:
        r = urllib.request.urlopen(url)
    except (urllib.error.URLError, ValueError):
        print("ОШИБКА: ссылка {0} не рабочая.".format(url))
        return None

    with open("{0}/{1}".format(dirname, name), "wb") as f:
        dl = 0
        full_size = 0
        CHUNK_SIZE = 1024  # 1kb
        start = time.time()
        chunk = r.read(CHUNK_SIZE)
        while chunk:
            f.write(chunk)
            f.flush()
            dl += CHUNK_SIZE
            if dl >= speed:
                dl = 0
                end = time.time()
                d = end - start
                if d < 1:
                    time.sleep(1-d)
                    start = time.time()
            full_size += len(chunk)
            chunk = r.read(CHUNK_SIZE)
    return full_size


# making queue from urls in file
def get_queue(urls_file) -> queue.Queue:
    q = queue.Queue(maxsize=0)
    with open(urls_file, 'r') as f:
        for line in f:
            q.put(line.strip().split(' '))
    return q


def worker(q, dirname, speed):
    while True:
        item = q.get()

        # condition to stop working
        if item is None:
            break

        start = time.time()
        downloaded = download_file(item[0], item[1], dirname, speed)
        end = time.time()
        if downloaded is not None:
            print("Файл {0} скачан за {1} сек. Размер {2} bytes"
                  .format(item[1], round(end-start, 2), downloaded))
        else:
            print("Файл {0} не скачан".format(item[1]))
        q.task_done()


def make_business(q, num_threads, download_speed, dir_to_save) -> int:

    threads = []

    for _ in range(num_threads):
        # create a new thread target it to a job, args should be list (,)
        thread = threading.Thread(target=worker,
                                  args=(q, dir_to_save, download_speed))
        thread.start()
        threads.append(thread)

    # block all items in queue until they will be done
    q.join()

    for _ in range(num_threads):
        q.put(None)

    for thread in threads:
        thread.join(timeout=2)


def main():
    args = get_args()

    # print(args)
    URLS_FILE = args['f'][0]
    num_threads = args['n'][0]
    download_speed = args['l'][0]
    dir_to_save = args['o'][0]

    queue_of_url_name = get_queue(URLS_FILE)
    total_links = queue_of_url_name.qsize()
    print("Найдено {0} ссылок".format(total_links))

    # when number of links is less than threads, we dont need extra threads
    num_threads = num_threads if total_links >= num_threads else total_links
    download_speed = round(download_speed/num_threads)

    make_business(queue_of_url_name, num_threads, download_speed, dir_to_save)


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    print("Время работы программы: {0:.3} сек.".format(end_time - start_time))
