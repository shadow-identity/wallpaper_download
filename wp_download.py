# -*- coding: utf-8 -*-
""" Downloads wallpapers in full resolution from 
http://www.australiangeographic.com.au and store it to local storage
(see local_path variable). """


import urllib2, logging
from bs4 import BeautifulSoup

logging.basicConfig(level = logging.DEBUG) 

debug = True

def getimg(url, debug=False):
    """ Open wallpaper's page, find url of hires picture
    in <div id="content"> --> children <p><a>. 
    Get URL from <a href="...">. """
    # where to save downloaded wallpapers
    local_path = '/home/nedr/Изображения/wp/au/'
    logging.debug('opening %s' % url)
    soup = BeautifulSoup(urllib2.urlopen(url))
    try:
        img_url = soup.find("div", id="content").p.a.get('href')
        logging.debug(u'url of img: %s' % img_url)
        logging.debug(img_url[img_url.rfind('/') + 1:])
        logging.debug('/home/nedr/progs/test/wallpapers' 
                      + img_url[img_url.rfind('/'):])
        if not debug:
            download(img_url, local_path
                     + img_url[img_url.rfind('/'):])
    except urllib2.URLError:
        logging.error('URLError while parsing %s' % url)
    return


def download(url, dest):
    """Download file from url and save it as dest. """
    try:
        s = urllib2.urlopen(url)
        content = s.read()
        with open(dest,'wb') as d:
            d.write(content)
    except urllib2.URLError:
        logging.error('ERLError while saving img from %s' % url)
    except IOError:
        logging.error('IOError while saving %s in %s' % (url, dest))
    finally:
        s.close()
    return
    

def main():
    links = 0
    site_prefix = 'http://www.australiangeographic.com.au'
    url_gallery = site_prefix + '/journal/wallpaper/'
    soup = BeautifulSoup(urllib2.urlopen(url_gallery))
    # gonna find links to wallpaper's pages
    for link in soup.find('table').find_all('a'):
        link_str = link.get('href')
        # if url is not absolute
        if not link_str.startswith('http'):
            link_str = 'http://www.australiangeographic.com.au' + link_str
        getimg(link_str, debug)
        links += 1

    logging.info('links to img pages found: %d' % (links))


if debug:
    #getimg('http://www.australiangeographic.com.au/journal/images-of-australia-coneflower.htm', debug)
    main()
else:
    main()