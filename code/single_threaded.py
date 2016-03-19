import timeit
import os
import sys
import requests
from urllib import urlretrieve
from PIL import Image

client_id = os.getenv('IMGUR_CLIENT_ID', None)
assert client_id is not None, "IMGUR_CLIENT_ID not set!"
headers = {
    'Authorization': 'Client-ID {}'.format(client_id),
    'content-type': 'application/json'
}
clg = Image.new("RGB", (256, 256))
outfile = 'collage.jpeg'

urls = ['http://i.imgur.com/wnqXEPv.jpg',
        'http://i.imgur.com/Qwp65mn.jpg',
        'http://i.imgur.com/6okdWJu.jpg',
        'http://i.imgur.com/7RR2bIS.jpg']

def make_collage():
    data_dir = os.path.abspath('var')
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
    left, upper, count = 0, 0, 1
    total_time = 0
    for url in urls:
        start = timeit.default_timer()
        path = urlretrieve(url)[0]
        total_time += timeit.default_timer() - start
        im = Image.open(path)
        im.resize((128, 128))
        clg.paste(im, (left, upper))
        left += 128
        count += 1
        if not count % 2:
            left = 0
            upper += 128
    print 'downloading took %.2f seconds' % total_time
    clg.save(outfile, 'JPEG')

def main():
    make_collage()

if __name__ == '__main__':
    main()