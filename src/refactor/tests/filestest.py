'''
Created on May 27, 2011

@author: catalin
'''
import unittest
from refactor.files import Finder


class FilesTest(unittest.TestCase):
    def test_finder(self):
        finder = Finder('./filetest')
        self.assertEqual(3, len(finder), len(finder))
        
    def test_finder_include(self):
        finder = Finder('./filetest').include('\.js$')
        self.assertEqual(1, len(finder))
        
    def test_finder_exclude(self):
        finder = Finder('./filetest').exclude('html|php$')
        self.assertEqual(1, len(finder))
        
    def test_both(self):
        finder = Finder('./filetest').include('file[1,2]').exclude('html$')
        self.assertEqual(1, len(finder))
        
    def test_extension(self):
        finder = Finder('./filetest').extension('php', 'html').exclude('html')
        self.assertEqual(1, len(finder))
    
    def test_returned_path(self):
        finder = Finder('./filetest').extension('php')
        print finder
        
if __name__ == "__main__":
    unittest.main()