import timeit
import os
import grequests

client_id = os.getenv('IMGUR_CLIENT_ID', None)
assert client_id is not None, "IMGUR_CLIENT_ID not set!"

headers = {
    'Authorization': 'Client-ID {}'.format(client_id),
    'content-type': 'application/json'
}

thumbnails_dir = os.path.abspath('var')
if not os.path.isdir(thumbnails_dir):
    os.makedirs(thumbnails_dir)

urls = ['http://i.imgur.com/wnqXEPv.jpg',
        'http://i.imgur.com/Qwp65mn.jpg',
        'http://i.imgur.com/6okdWJu.jpg',
        'http://i.imgur.com/7RR2bIS.jpg']

def main():
    rs = (grequests.get(url, headers=headers) for url in urls)
    start = timeit.default_timer()
    respones = grequests.map(rs)
    elapsed = timeit.default_timer() - start
    print 'downloading took %.2f seconds' % elapsed
    for resp in respones:
        filename = resp.url.rsplit('/', 1)[1]
        path = os.path.join(thumbnails_dir, filename)
        with open(path, 'wb') as target:
            target.write(resp.content)

if __name__ == '__main__':
    main()