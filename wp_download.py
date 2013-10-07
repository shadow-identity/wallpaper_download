#!/bin/python
# -*- coding: utf-8 -*-
"""Download wallpapers from www.australiangeographic.com.au
Positional argument:
path -- pathname of destination wallpapers directory

Optional argument:
-v, --verbose -- affects both log file and stdout
-r, --rewrite -- rewrite existing file (else skip them)

Output:
- Image files saves into path directory. They have addition information
  about site and author (if exist) in Exif.Image.Copyright field.
- Log to stdout

"""
#TODO: add thumbnail to exif?
#TODO: using context manager

import urllib2
import logging
import argparse
from os.path import abspath, exists
from os import mkdir
from urllib2 import URLError

import lxml.html
from socks import HTTPError


class Image():
    """Class containing attributes and methods assigned with image

    Attributes
    self.preview_url -- url of preview page
    self.image_url -- url of full image
    self.author -- author of image
    self.name -- full name of image (will be file name)
    self.extension -- file extension of image
    self.filename -- full name destination image file
    self.error -- non-critical errors flag

    """

    def __init__(self):
        self.error = False

    def get_data_from_gallery(self, image):
        """Get useful information about image from gallery, save it in attrs

        Arguments:
        image -- ElementTree object containing values

        """
        try:
            self.preview_url = image[0][0].attrib['href']
        except IndexError:
            # Can't get url of preview page -> skip it
            return error_parsing_gallery
        if image[1] is not None:
            description = image[1]
        else:
            #Subelement does not exist - get name from filename and gtfo
            self.name = self.preview_url.rsplit('/', 1)[-1].rsplit('.')[0]
            self.author = 'Not present'
            return
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
            self.name = self.preview_url.rsplit('/', 1)[-1].rsplit('.')[0]

        #Author is always in last but one element
        if description[len(description) - 2] is not None:
            self.author = description[len(description) - 2].text
        else:
            self.author = 'Failed to get author'
        logging.debug('%-50s %-20s %s'
                      % (self.name, self.author, self.preview_url))

    def get_original_image_url(self):
        """Get information from preview page, save it in attributes."""

        try:
            self.image_url = open_url(
                self.preview_url, '//*[@id="content"]/p/a')[0].attrib['href']
        except IndexError:
            self.error = True
            return
            # get file extension of image from it's url
        if self.image_url is not None:
            self.extension = '.' + self.image_url.rpartition('.')[2]

    def save_image(self):
        """Get path to save, download file and save it to destination."""
        self.filename = args.path + self.name + self.extension
        if exists(self.filename) and args.rewrite:
            image_file = open_url(self.image_url)

            if image_file is not None:
                try:
                    with open(self.filename, 'wb') as wallpaper_file:
                        wallpaper_file.write(image_file)
                except IOError:
                    logging.error('IOError while saving %s', self.filename)
                    self.error = True
                else:
                    logging.debug('recorded %s' % self.filename)
            else:
                self.error = True
        else:
            logging.debug('skipping existing file %s' % self.filename)

    def edit_exif(self):
        """Manipulations with exif (adding copyright)."""
        from pyexiv2.metadata import ImageMetadata
        from pyexiv2.exif import ExifValueError, ExifTag

        info_to_exif = ('File was downloaded from gallery {0}. \n'
                        'URL of image: {1} \n'
                        'Author: {2}'.format(
            url, self.image_url, self.author))
        try:
            metadata = ImageMetadata(self.filename)
            metadata.read()
            if 'Exif.Image.Copyright' in metadata:
                info_to_exif = metadata['Exif.Image.Copyright'].value + '\n' + info_to_exif
            metadata['Exif.Image.Copyright'] = info_to_exif
            metadata.write()
        except ExifValueError, info:
            logging.debug('error parsing Exit. %s' % info)
            self.error = True
        except ExifTag, info:
            logging.debug('error saving Exif. %s' % info)
            self.error = True
        except IOError, info:
            logging.debug('%s' % info)
            self.error = True


def open_url(url, xpath=None, criticality=False):
    """Returns content of url or tree by xpath (if given).
    If criticality = 1, program stops
    """
    try:
        content = urllib2.urlopen(url).read()
        if xpath is not None:
            doc = lxml.html.document_fromstring(content)
            if doc.make_links_absolute(site_prefix):
                doc = doc.make_links_absolute(site_prefix)
            tree = doc.xpath(xpath)
            return tree
        else:
            return content
    except HTTPError, info:
        if criticality == 1:
            logging.critical('Critical HTTP error %s' % info)
            exit(1)
        else:
            logging.error('HTTP error %s' % info)
    except URLError, info:
        if criticality == 1:
            logging.critical('Critical error while loading url. %s' % info)
            exit(1)
        else:
            logging.error('Error while loading %s' % info)
    except IndexError, info:
        if criticality:
            logging.critical('HTML structure error in %s. \n %s' % (url, info))
            exit(1)
        else:
            logging.error('%s' % info)


url = 'http://www.australiangeographic.com.au/journal/wallpaper'
site_prefix = 'http://www.australiangeographic.com.au'
error_parsing_gallery = 'error while parsing gallery'
error_saving_file = 'error while downloading or saving image'

#Parse command line arguments
parser = argparse.ArgumentParser(
    description='Download wallpapers from %(url)s BSD license. \
    Source: https://bitbucket.org/ambush_k3/wp_download or \
    https://github.com/shadow-identity/wallpaper_download' % locals())
parser.add_argument('path', help='path to save wallpapers')
parser.add_argument('-v', '--verbose', help='increase output verbosity',
                    action='store_true')
parser.add_argument('-r', '--rewrite', help='rewrite existing files', action='store_true')
args = parser.parse_args()

#Configure logger
if args.verbose:
    logging.basicConfig(format='[LINE:%(lineno)-3d]# ' \
                               '%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG)
    hello_message = 'Started. Arguments: %s' % args
else:
    logging.basicConfig(format='%(asctime)s %(message)s ', level=logging.INFO)
    hello_message = 'Started. Arguments: %s' % args

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

images_table = open_url(url, '//*[@id="content"]/table/tr/td/div', True)
number_images = len(images_table)
error_counter = 0

for (counter, image) in enumerate(images_table, start=1):
    page = Image()
    if page.get_data_from_gallery(image) == error_parsing_gallery:
        error_counter += 1
        continue
    if page.preview_url is None:
        error_counter += 1
        continue
    page.get_original_image_url()
    if page.image_url is None or page.error:
        error_counter += 1
        continue
    page.save_image()
    if page.error:
        error_counter += 1
        continue
    page.edit_exif()
    if page.error:
        error_counter += 1
        continue
    logging.debug((page.error, page.filename, page.extension,
                   page.image_url))

if error_counter != 0:
    errors = number_images - error_counter
    logging.info('There was %(errors)s '
                 'of %(number_images)s images is not parsed.' % locals())
else:
    logging.info('All of %(number_images)s images was successfully saved'
                 % locals())
