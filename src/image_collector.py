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
        '''

        :param image_file:
        :param save_dir:
        :param create:
        :return:
        '''
        self.valid_urls = []
        self.invalid_urls = []
        self.image_file = image_file
        self.save_dir = save_dir
        self.create_save_dir = create
        self.validate_params()
        self.validate_urls()
        # open(os.path.join(self.save_dir, 'Log.log'), 'a').close()
        logging.getLogger('').handlers = []
        logging.basicConfig(filename=os.path.join(self.save_dir, 'Log.log'), filemode="w", level=logging.INFO)
        logging.info('''This is the output for dowloading images found in file: %s
Valid URLs found: %d
Invalid URLs found: %d
Images are saved in %s
''' % (
            self.image_file, len(self.valid_urls), len(self.invalid_urls), os.path.join(self.save_dir, 'images/')))
        self.counter = 0
        for url in self.valid_urls:
            self.counter += 1
            self.download_file(url)


    def validate_params(self):
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
        img_file = open(self.image_file, 'r')
        urls = img_file.readlines()
        img_file.close()
        if len(urls) == 0:
            raise Exception("Images File is Empty")
        urls = list(set(urls))
        for img_url in urls:
            img_url = img_url.strip().replace(' ', '%20')
            parsed_url = urlparse(img_url)
            if (parsed_url.scheme == 'https' or
                        parsed_url.scheme == 'http' or
                        parsed_url.scheme == 'ftps' or
                        parsed_url.scheme == 'ftp') and parsed_url.netloc != '':
                self.valid_urls.append(img_url)
            else:
                self.invalid_urls.append(img_url)
        if len(self.valid_urls) == 0:
            raise Exception("No Valid URLs Found")

    def download_file(self, url):
        local_filename = str(self.counter) + "_" + url.split('/')[-1].split("?")[0]
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8,ar;q=0.6,ms;q=0.4',
                'Cache-Control': 'max-age=   0',
                'Connection': 'keep-alive'}
            req_ad.DEFAULT_RETRIES = 1
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
                logging.info("URL: %s saved to %s" % (url, os.path.join(self.save_dir, 'images', local_filename) ))
            else:
                self.counter -= 1
                logging.error("URL: %s not found" % url)
        except Exception, e:
            if os.path.exists(os.path.join(self.save_dir, 'images', local_filename)):
                os.remove(os.path.join(self.save_dir, 'images', local_filename))
            self.counter -= 1
            logging.error("URL: %s couldn't be saved. Returned with the following exception: %s" % (url, str(e)))
        return local_filename

    # @staticmethod
    # def url_exists(url):
    #     req_ad.DEFAULT_RETRIES = 1
    #     s = requests.Session()
    #     s.mount(url, HTTPAdapter(max_retries=1))
    #     header = {
    #         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    #         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    #         'Accept-Encoding': 'gzip, deflate, sdch',
    #         'Accept-Language': 'en-US,en;q=0.8,ar;q=0.6,ms;q=0.4',
    #         'Cache-Control': 'max-age=   0',
    #         'Connection': 'keep-alive'}
    #
    #     r = s.head(url, headers=header)
    #     # print dir(r.cookies)
    #     # print r.cookies.get_dict()
    #     # print r.text
    #     # r.clear_session_cookies()
    #     print url
    #     print r.status_code
    #     print "===="
    #     valid = r.status_code == requests.codes.ok
    #     return valid, r.cookies.get_dict()

    @staticmethod
    def verify_image(img_path):
        image = Image.open(img_path)
        image.verify()


def extract_argumanets(args):
    if len(args) < 3:
        print "Please insert valid arguments."
        # open(os.)
        # for arg in args:
        # i


def main(args):
    extract_argumanets(args)


if __name__ == '__main__':
    main(argv)
