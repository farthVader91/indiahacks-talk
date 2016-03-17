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
    return urlretrieve(link)[0]

def create_thumbnail_dir():
    if not os.path.isdir(thumbnails_dir):
        os.makedirs(thumbnails_dir)

def resize_image(infile, size=(128, 128)):
    im = Image.open(infile)
    im.resize(size)
    return im

outfile = 'collage.jpeg'
clg = Image.new("RGB", (512, 512))


if __name__ == '__main__':
    create_thumbnail_dir()
    left, upper, count = 0, 0, 1
    for url in iter_gallery_urls(10):
        for link in iter_jpeg_urls(url):
            path = download_image(link)
            thumbnail = resize_image(path)
            clg.paste(thumbnail, (left, upper))
            print "added to collage"
            left += 128
            count += 1
            if not count % 4:
                left = 0
                upper += 128
                if count == 16:
                    clg.save(outfile, 'JPEG')
                    break
        else:
            continue
        break
    else:
        print "insufficient images"
