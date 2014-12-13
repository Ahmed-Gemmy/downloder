import os

from tests.utils import run


__author__ = 'Ahmed Gamal A. Ali'
import unittest


class ImagesCollectorCommandLineTest(unittest.TestCase):
    def setUp(self):
        self.script_path = os.path.join('/'.join(os.path.abspath(__file__).split("/")[:-2]), 'src',
                                        'image_collector.py')
        self.files_path = os.path.join('/'.join(os.path.abspath(__file__).split("/")[:-1]), 'fixtures')

    def test_no_arguments(self):
        p = run("python " + self.script_path)
        std_out = p.stdout.read()
        self.assertIn("Please insert valid arguments", std_out)
        self.assertIn("Options:", std_out)

    def test_help_argument(self):
        p = run("python " + self.script_path + " -h")
        std_out = p.stdout.read()
        self.assertNotIn("Please insert valid arguments", std_out)
        self.assertIn("Options:", std_out)
        p = run("python " + self.script_path + " --help")
        std_out = p.stdout.read()
        self.assertNotIn("Please insert valid arguments", std_out)
        self.assertIn("Options:", std_out)

    def test_missing_argument(self):
        p = run("python " + self.script_path + " --images=" + os.path.join(self.files_path, 'empty.txt'))
        std_out = p.stdout.read()
        self.assertIn("Please insert valid arguments", std_out)
        self.assertIn("Options:", std_out)
        p = run("python " + self.script_path + " --save_dir=/tmp/save_dir")
        std_out = p.stdout.read()
        self.assertIn("Please insert valid arguments", std_out)
        self.assertIn("Options:", std_out)

    def test_empty_file_argument(self):
        p = run("python " + self.script_path + " --save_dir=/tmp/save_dir --images=" + os.path.join(self.files_path, 'empty.txt'))
        std_out = p.stdout.read()
        std_err = p.stderr.read()
        self.assertIn("Exception: Images File is Empty", std_err)
        self.assertEqual("", std_out)

    def test_save_dir_not_found(self):
        p = run("python " + self.script_path + " --save_dir=/not_found_dir --images=" + os.path.join(self.files_path, 'all_valid.txt'))
        std_out = p.stdout.read()
        std_err = p.stderr.read()
        self.assertIn("OSError: Save Directory not found", std_err)
        self.assertEqual("", std_out)

    def test_save_dir_permission_denied(self):
        p = run("python " + self.script_path + " --create --save_dir=/not_found_dir --images=" + os.path.join(self.files_path, 'all_valid.txt'))
        std_out = p.stdout.read()
        std_err = p.stderr.read()
        self.assertIn("Permission denied", std_err)
        self.assertEqual("", std_out)

    def test_all_valid(self):
        p = run("python " + self.script_path + " --create --save_dir=/tmp/out_dir --images=" + os.path.join(self.files_path, 'all_valid.txt'))
        std_out = p.stdout.read()
        std_err = p.stderr.read()
        print std_out
        print "="
        print std_err
        print "=="
