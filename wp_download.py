# -*- coding: utf-8 -*-
""" Downloads wallpapers in full resolution from 
http://www.australiangeographic.com.au and store it to local storage
(see local_path variable). """


import urllib2, logging
from bs4 import BeautifulSoup

site_prefix = 'http://www.australiangeographic.com.au'
url_gallery = site_prefix + '/journal/wallpaper/'
path_to_file = '/home/nedr/Изображения/wp/au/temp/'

def getimg(url, file_name):
    """ Open wallpaper's page, find url of hi-res picture
    in <div id="content"> --> children <p><a>. 
    Get URL from <a href="...">. """
    # where to save downloaded wallpapers
    logging.debug('opening %s', url)
    soup = BeautifulSoup(urllib2.urlopen(url))
    try:
        # finding url of original wallpaper
        img_url = soup.find("div", id="content").p.a.get('href')
        logging.debug(u'url of img: %s', img_url)
        logging.debug('gonna write to %s', path_to_file + file_name)
        if not __debug__:
            logging.info('downloading %s to %s', img_url, file_name)
            download(img_url, path_to_file + file_name)
    except urllib2.URLError:
        logging.error('URLError while parsing %s', url)
    return

def download(url, dest):
    """Download file from url and save it as dest. """
    try:
        wallpaper_net = urllib2.urlopen(url)
        content = wallpaper_net.read()
        with open(dest,'wb') as wallpaper_file:
            wallpaper_file.write(content)
    except urllib2.URLError:
        logging.error('ERLError while saving img from %s', url)
    except IOError:
        logging.error('IOError while saving %s in %s', url, dest)
    else:
        wallpaper_net.close
    return
    

if __debug__: 
    logging.basicConfig(level = logging.DEBUG)
else:
    logging.basicConfig(level = logging.INFO)
links = 0
soup = BeautifulSoup(urllib2.urlopen(url_gallery))
# gonna find links to wallpaper's pages
# at first we'll find table cell (<td>) with tumbnail of wallpaper
for image_block in soup.find('table').find_all('td'):
    # finding link to wallpaper page in table cell 
    link_str = image_block.find('a').get('href')
    # if url of page is not absolute, make that
    if not link_str.startswith('http'):
        link_str = 'http://www.australiangeographic.com.au' + link_str
    # descriprion of image we will use as a name of file
    img_name = [string for string in image_block.find_all('p')[1].strings]
    getimg(link_str, img_name[0] + '.jpg')
    links += 1

logging.info('links to img pages found: %d', links)


