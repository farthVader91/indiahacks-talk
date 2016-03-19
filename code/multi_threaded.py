import timeit
import os
from PIL import Image
from Queue import Queue
from urllib import urlretrieve
import requests
import sys
import threading

client_id = os.getenv('IMGUR_CLIENT_ID', None)
assert client_id is not None, "IMGUR_CLIENT_ID not set!"

headers = {
    'Authorization': 'Client-ID {}'.format(client_id),
    'content-type': 'application/json'
}

thumbnails_dir = os.path.abspath('var')

outfile = 'collage.jpeg'
clg = Image.new("RGB", (256, 256))

max_workers = 4

link_queue = Queue()
fpath_queue = Queue()

urls = ['http://i.imgur.com/wnqXEPv.jpg',
        'http://i.imgur.com/Qwp65mn.jpg',
        'http://i.imgur.com/6okdWJu.jpg',
        'http://i.imgur.com/7RR2bIS.jpg']

def download_image(link):
    filename = link.rsplit('/', 1)[1]
    path = os.path.join(thumbnails_dir, filename)
    urlretrieve(link, filename=path)

def create_thumbnail_dir():
    if not os.path.isdir(thumbnails_dir):
        os.makedirs(thumbnails_dir)

def resize_image(infile, size=(128, 128)):
    im = Image.open(infile)
    im.resize(size)
    return im

class DownloadWorker(threading.Thread):
    def __init__(self, *args):
        super(DownloadWorker, self).__init__()
        self.in_queue = link_queue

    def run(self):
        while True:
            job = self.in_queue.get()
            download_image(job)
            self.in_queue.task_done()

def iter_images():
    for dirpath, _, filenames in os.walk(thumbnails_dir):
        for filename in filenames:
            yield os.path.join(dirpath, filename)

def process_image(path, dim):
    img = resize_image(path)
    clg.paste(img, dim)

def main():
    create_thumbnail_dir()
    downloaders = map(DownloadWorker, range(max_workers))
    for dld in downloaders:
        dld.daemon = True
        dld.start()
    start = timeit.default_timer()
    for url in urls:
        link_queue.put(url)
    link_queue.join()
    elapsed = timeit.default_timer() - start
    print 'downloading took %.2f seconds' % elapsed
    left, upper, count = 0, 0, 1
    for image_p in iter_images():
        process_image(image_p, (left, upper))
        left += 128
        if not count % 2:
            left = 0
            upper += 128
            if count == 4:
                clg.save(outfile, 'JPEG')
        count += 1


if __name__ == '__main__':
    main()