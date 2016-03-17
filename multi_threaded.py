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

thumbnails_dir = os.path.abspath('thumbnails')

url_fmt = 'https://api.imgur.com/3/gallery/hot/viral/{}.json'

def iter_gallery_urls(repeat=5):
    for i in xrange(repeat):
        yield url_fmt.format(i)

def iter_jpeg_urls(url):
    resp = requests.get(url, headers=headers)
    result = resp.json()
    for item in result['data']:
        _type = item.get('type')
        if _type and _type == 'image/jpeg':
            yield item['link']

def download_image(link):
    print "downloading", link
    filename = link.rsplit('/', 1)[1]
    path = os.path.join(thumbnails_dir, filename)
    urlretrieve(link, filename=path)
    print 'finished dlding'

def create_thumbnail_dir():
    if not os.path.isdir(thumbnails_dir):
        os.makedirs(thumbnails_dir)

def resize_image(infile, size=(128, 128)):
    im = Image.open(infile)
    im.resize(size)
    return im

outfile = 'collage.jpeg'
clg = Image.new("RGB", (512, 512))

max_workers = 10


link_queue = Queue()
fpath_queue = Queue()
import logging


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

if __name__ == '__main__':
    create_thumbnail_dir()
    downloaders = map(DownloadWorker, range(max_workers))
    for dld in downloaders:
        dld.daemon = True
        dld.start()
    """
    processors = map(ImageProcessor, range(max_workers))
    for proc in processors:
        proc.daemon = True
        proc.start()
    """
    added_count = 0
    for url in iter_gallery_urls(10):
        for link in iter_jpeg_urls(url):
            link_queue.put(link)
            added_count += 1
            if added_count == 16:
                break
        else:
            continue
        break
    link_queue.join()
    left, upper, count = 0, 0, 1
    for image_p in iter_images():
        process_image(image_p, (left, upper))
        print "added to collage"
        left += 128
        if not count % 4:
            left = 0
            upper += 128
            if count == 16:
                clg.save(outfile, 'JPEG')
        count += 1
