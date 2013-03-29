# -*- coding: utf-8 -*-
"""Download wallpapers from www.australiangeographic.com.au
Positional argument:
path -- pathname of destination wallpapers directory

Optional arguments:
-v, --verbose -- affects both log file and stdout

Output:
- Image files saves into path directory with addition information about site
  and author (if exist) in Exif.Image.Copyright field.
- Log to stdout
- Log file wp_download.log (more detailed than log in stdout)

"""
#TODO: add exceptions
#TODO: add thumbnail to exif?
#TODO: counter of images in gallery and saved images

import urllib
import urllib2
import lxml.html
import logging
import argparse
from os.path import abspath, exists
from os import mkdir
from urllib2 import URLError
from socks import HTTPError
from lxml.html import make_links_absolute


class Image():
    """Class containing attributes and methods assigned with image

    Attributes
    self.prewiev_url -- url of prewiev page
    self.image_url -- url of full image
    self.author -- author of image
    self.name -- full name of image (will be file name)
    self.extention -- file extention of image
    self.filename -- full name destination image file

    """

    def get_data_from_gallery(self, image):
        """Get useful information about image from gallery, save it in attrs

        Arguments:
        image -- ElementTree object containing values

        """
        try:
            self.prewiev_url = image[0][0].attrib['href']
            description = image[1]
            self.name = ''
            if description.text is not None:
                self.name = description.text
            # hack: usually element 'description' contains 4 tags (br, br,
            # em, br). If more, name is in 2- (or more) strings (and tags) of
            # description. Get it from additional <em> and after it and <br />
            if len(description) > 3:
                for element in description[:-2]:
                    if element.tag == 'em' and element.text is not None:
                        self.name = self.name + element.text
                        if element.tail is not None:
                            self.name = self.name + element.tail
                    elif element.tag == 'br' and element.tail is not None:
                        self.name = self.name + element.tail
            self.name = self.name.strip()
            # self.name cant include trailing ' ' or \n. Remove it from url
            if self.name == '':
                self.name = self.prewiev_url.rsplit('/', 1)[-1].rsplit('.')[0]

            #Author is always in last but one element
            if description[len(description) - 2] is not None:
                self.author = description[len(description) - 2].text
            else:
                self.author = 'Failed to get author'

        except IndexError:
                return error_parsing_gallery

        #logging.debug('%-40s %s' % (self.name, self.author))

    def get_original_image_url(self):
        """Get information from prewiev page, save it in attributes."""
        prewiev_html = urllib2.urlopen(self.prewiev_url).read()
        prewiev_doc = lxml.html.document_fromstring(prewiev_html)
        self.image_url = prewiev_doc.xpath(
                        '//*[@id="content"]/p/a')[0].attrib['href']
        # getting file extention of image from it's url
        self.extention = '.' + self.image_url.rpartition('.')[2]

    def save_image(self):
        """Get path to save, download file and save it to destination."""
        """try:"""

        #Calculate full filepath, download image, write it to disk
        self.filename = args.path + self.name + self.extention
        image_pointer = urllib2.urlopen(self.image_url)
        image = image_pointer.read()
        with open(self.filename, 'wb') as wallpaper_file:
            wallpaper_file.write(image)
        """except urllib2.URLError:
            logging.error('ERLError while saving img from %s', url)
        except IOError:
            logging.error('IOError while saving %s in %s', url, dest)
        else:"""
        image_pointer.close

    def edit_exif(self):
        """Manipulations with exif (adding copyright)."""
        import pyexiv2
        info_to_exif = ('File was downloaded from gallery {0}. \n'
                        'URL of image: {1} \n'
                        'Author: {2}'.format(
                                url, self.image_url, self.author))
        metadata = pyexiv2.ImageMetadata(self.filename)
        metadata.read()
        if 'Exif.Image.Copyright' in metadata:
            info_to_exif = metadata['Exif.Image.Copyright'].value + '\n' \
                           + info_to_exif
        metadata['Exif.Image.Copyright'] = info_to_exif
        metadata.write()


url = 'http://www.australiangeographic.com.au/journal/wallpaper'
site_prefix = 'http://www.australiangeographic.com.au'
error_parsing_gallery = 'error while parsing gallery'

#Parse command line arguments
parser = argparse.ArgumentParser(description=
    'Download wallpapers from %(url)s'
    'BSD license. Source: https://bitbucket.org/ambush_k3/wp_download'
    % locals())
parser.add_argument('-v', '--verbose',
    help='increase output verbosity', action='store_true')
parser.add_argument('path', help='path to save wallpapers')
args = parser.parse_args()

#Configure logger
if __debug__ or args.verbose:
    logging.basicConfig(format='%(asctime)s, %(message)s', level=logging.DEBUG)
    hello_message = 'Started. Arguments: %s' % args
else:
    #TODO: add message type
    logging.basicConfig(level=logging.INFO)

logging.info(hello_message)

#Is given path valid?
if not abspath(args.path):
    logging.error('Path must be absolute!')
    exit(1)
if not (args.path.endswith('/') or args.path.endswith('\\')):
    logging.debug('Fixing path %s' % args.path)
    from sys import platform as _platform
    if _platform.startswith("linux") or _platform == "darwin":
        args.path += '/'
    elif _platform == "win32" or "cygwin":
        args.path += '\\'
    logging.debug('Fixed path: %s' % args.path)

#Is given path exist? If not - create it
if not exists(args.path):
    try:
        mkdir(args.path)
    except OSError:
        logging.critical('Error creating %s. \
                       If path is correct, check access rights' % args.path)
        exit(1)
    else:
        logging.info('Created destination path: %s' % args.path)

try:
    html = urllib2.urlopen(url).read()
    doc = lxml.html.document_fromstring(html)
    if doc.make_links_absolute(site_prefix):
            doc = doc.make_links_absolute(site_prefix)
    images_table = doc.xpath('//*[@id="content"]/table/tr/td/div')
except HTTPError, ex:
    print ex
    logging.critical('HTTP error %s' % ex)
    exit(1)
except URLError, ex:
    print ex
    logging.critical('Error loading gallery %s' % ex)
    exit(1)
number_images = len(images_table)
counter = 0
error_page = []
error_counter = 0
for (counter, image) in enumerate(images_table, start=1):
    page = Image()
    if page.get_data_from_gallery(image) == error_parsing_gallery:
        error_page.append(counter)
        error_counter += 1
        continue
    # FIXME: revert to normal state
    if 'ffgfg' in page.name:
        page.get_original_image_url()
        page.save_image()
        page.edit_exif()

if error_counter != 0:
    errors = number_images - error_counter
    logging.info('There was %(errors)s '
                 'of %(number_images)s images is not parsed. \
                  Error pages: %(error_page)s' % locals())
else:
    logging.info('All of %(number_images)s images was successfully saved' 
                 % locals())
    