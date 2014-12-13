"""
This file is used to collect images from a given plain text file containing images URLs in each line.
It can be used via command line, or pragmatically import the CollectImage class eo execute it.
To see command line help execute:
$ python image_collector.py --help

Written by Ahmed Gamal A. Ali
"""

__author__ = 'Ahmed Gamal A. Ali'

from PIL import Image
import errno
from sys import argv
import os
from urlparse import urlparse
import logging

import requests
from requests.adapters import HTTPAdapter
import requests.adapters as req_ad

requests.adapters.DEFAULT_RETRIES = 5


class CollectImages():
    def __init__(self, image_file, save_dir, create=False):
        """
        The class constructor that execute everything.
        By initiating this class with the valid arguments, the images are going to be collected and stored to the\
         directory given to the initiator.

        :param image_file: The path to the plain text file containing the images URLs
        :param save_dir: The path to the directory where the images and log file will be saved
        :param create: A bool value, if True, the save directory will be created if it doesn't exists.
        :return: None
        """
        self.valid_urls = []
        self.invalid_urls = []
        self.image_file = image_file
        self.save_dir = save_dir
        self.create_save_dir = create
        # validating given parameters
        self.validate_params()
        # Validating urls in file.
        self.validate_urls()
        logging.getLogger('').handlers = []
        logging.basicConfig(filename=os.path.join(self.save_dir, 'Log.log'), filemode="w", level=logging.INFO)
        logging.info('''This is the output for downloading images found in file: %s
Valid URLs found: %d
Invalid URLs found: %d
Images are saved in %s
''' % (self.image_file, len(self.valid_urls), len(self.invalid_urls), os.path.join(self.save_dir, 'images/')))
        # setting counter to append to image name to avoid overriding images with the same name.
        self.counter = 0
        for url in self.valid_urls:
            self.counter += 1
            self.download_file(url)

    def validate_params(self):
        """
        Validates the given paths either they exist or not. It raises OSError if the following cases:
        1. The given images file does not exists.
        2. The given save directory does not exists and create option is False.
        3. Permission denied for the given save directory.
        :return: None
        """
        if not os.path.exists(self.image_file):
            raise OSError("File %s Not Found" % self.image_file)
        if not os.path.exists(self.save_dir) and not self.create_save_dir:
            raise OSError("Save Directory not found, Please create it or give allow the create parameter")
        elif not os.path.exists(os.path.join(self.save_dir, 'images/')) and self.create_save_dir:
            try:
                os.makedirs(os.path.join(self.save_dir, 'images/'))
            except OSError as exc:
                if exc.errno == errno.EEXIST and os.path.isdir(self.save_dir):
                    logging.warning("Save directory already exists, images might be overridden or\
                     merged with already existing files.")
                else:
                    raise

    def validate_urls(self):
        """
        Validates the given images file looking for at least one valid URL in the file.
        :except "Images File is empty" in case of empty images file.
        :except "No Valid URLs Found" in case no urls are in the file.
        :return: None
        """
        img_file = open(self.image_file, 'r')
        urls = img_file.readlines()
        img_file.close()
        if len(urls) == 0:
            raise Exception("Images File is Empty")
        urls = list(set(urls))
        for img_url in urls:
            # replacing spaces with the equivalent URL encode %20
            img_url = img_url.strip().replace(' ', '%20')
            parsed_url = urlparse(img_url)
            # checking valid protocol, and host existence
            if (parsed_url.scheme == 'https' or
                parsed_url.scheme == 'http' or
                parsed_url.scheme == 'ftps' or
                parsed_url.scheme == 'ftp') \
                    and parsed_url.netloc != '':
                self.valid_urls.append(img_url)
            else:
                self.invalid_urls.append(img_url)
        if len(self.valid_urls) == 0:
            raise Exception("No Valid URLs Found")

    def download_file(self, url):
        """
        Downloads the image from the given URL to the save directory.
        All actions are logged in a Log file in the save directory.

        :param url: Image URL to be downloaded.
        :return: None
        """
        local_filename = str(self.counter) + "_" + url.split('/')[-1].split("?")[0]
        try:
            # simulating browser header to avoid 502 HTTP bad gateway error
            header = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36\
                 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8,ar;q=0.6,ms;q=0.4',
                'Cache-Control': 'max-age=   0',
                'Connection': 'keep-alive'}
            req_ad.DEFAULT_RETRIES = 5
            s = requests.Session()
            s.mount(url, HTTPAdapter(max_retries=5))
            r = s.get(url, headers=header, stream=True)
            if r.status_code == requests.codes.ok:
                with open(os.path.join(self.save_dir, 'images', local_filename), 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024):
                        if chunk:  # filter out keep-alive new chunks
                            f.write(chunk)
                            f.flush()
                f.close()
                self.verify_image(os.path.join(self.save_dir, 'images', local_filename))
                logging.info("URL: %s saved to %s" % (url, os.path.join(self.save_dir, 'images', local_filename)))
            else:
                self.counter -= 1
                logging.error("URL: %s not found" % url)
        except Exception, e:
            # removing corrupted file if saved.
            if os.path.exists(os.path.join(self.save_dir, 'images', local_filename)):
                os.remove(os.path.join(self.save_dir, 'images', local_filename))
            self.counter -= 1
            logging.error("URL: %s couldn't be saved. Returned with the following exception: %s" % (url, str(e)))
        return local_filename

    @staticmethod
    def verify_image(img_path):
        """
        Verify that the saved file is a valid image. If not, it will be deleted by the caller method.
        :param img_path: Path to the downloaded image.
        :raise exception if the file is corrupted or not an image.
        :return: None
        """
        image = Image.open(img_path)
        image.verify()


def print_help():
    """
    Prints the help file content.
    :return: None
    """
    f = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'help.txt'))
    print f.read()
    f.close()


def extract_args(args):
    """
    Extract arguments and either print the proper output on the screen or start the download process.
    :param args: List of arguments given to the application from command line.
    :return: None
    """
    if '-h' in args or '--help' in args:
        print_help()
        exit()
    if len(args) < 3:
        print "Please insert valid arguments."
        print_help()
        exit()
    images = None
    save_dir = None
    create = False
    for arg in args:
        if arg.startswith("--images") and '=' in arg:
            images = arg.split("=")[1]
        if arg.startswith("--save_dir") and '=' in arg:
            save_dir = arg.split("=")[1]
        if arg == '--create':
            create = True

    if images is None or save_dir is None:
        print "Please insert valid arguments."
        print_help()
        exit()
    CollectImages(image_file=images, save_dir=save_dir, create=create)


if __name__ == '__main__':
    extract_args(argv)
