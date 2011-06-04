'''
Created on May 27, 2011

@author: catalin
'''
import unittest
from refactor.files import Finder, ContentFilter

class FinderTest(unittest.TestCase):
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
        self.assertEqual(list(finder), ['./filetest/file1.php'])

class ContentFilterTest(unittest.TestCase): 
    def test_only(self):
        filter = ContentFilter(Finder('./filetest'))
        self.assertEqual(3, len(filter))
        
        filter.only(r'namespace Mach\\')
        self.assertEqual(1, len(filter))
        self.assertEqual(list(filter), ['./filetest/file1.php'])
        
    def test_without(self):
        filter = ContentFilter(Finder('./filetest'))
        filter.without(r'namespace Mach\\')
        self.assertEqual(2, len(filter))
        
        
        
if __name__ == "__main__":
    unittest.main()
    