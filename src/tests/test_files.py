'''
Created on May 27, 2011

@author: catalin
'''
import unittest
from refactor import *
from refactor.files.context import *

def dir():
    import os
    return os.path.dirname(__file__)

class FinderTest(unittest.TestCase):
    def test_finder(self):
        finder = Finder(dir() + '/filetest')
        self.assertEqual(3, len(finder), len(finder))
        
    def test_finder_include(self):
        finder = Finder(dir() + '/filetest').include('\.js$')
        self.assertEqual(1, len(finder))
        
    def test_finder_exclude(self):
        finder = Finder(dir() + '/filetest').exclude('html|php$')
        self.assertEqual(1, len(finder))
        
    def test_both(self):
        finder = Finder(dir() + '/filetest').include('file[1,2]').exclude('html$')
        self.assertEqual(1, len(finder))
        
    def test_extension(self):
        finder = Finder(dir() + '/filetest').extension('php', 'html').exclude('html')
        self.assertEqual(1, len(finder))
    
    def test_returned_path(self):
        finder = Finder(dir() + '/filetest').extension('php')
        files = list(finder)
        self.assertEqual(files[0].get_path(), dir() + '/filetest/file1.php')

class ContentFilterTest(unittest.TestCase): 
    def test_only(self):
        filter = Finder(dir() + '/filetest').filter(ContentFilter(r'namespace Mach\\'))
        self.assertEqual(1, len(filter))
        files = list(filter)
        self.assertEqual(files[0].get_path(), dir() + '/filetest/file1.php')

class ContextTest(unittest.TestCase):
    def test_context_cut(self):
        context = After(r'class ')
        newcontext = context.cut('namespace SomeNamespace\n\nuse AnotherNamespace\n\nclass SomeClass extends')
        self.assertEquals('SomeClass extends', newcontext)
        
    def test_context_and(self):
        context = After('1 ') & Before(' and 3')
        cut = context.cut('after 1 is 2 and 3')
        self.assertEquals('is 2', cut)
        self.assertEqual((8, 12), context.get_interval())
        self.assertEquals('is 2', 'after 1 is 2 and 3'[context.get_interval()[0] : context.get_interval()[1]])
        
    def test_context_or(self):
        context = After('1 ') | Before(' is 2')
        cut = context.cut('after 0 is 2 and 3')
        self.assertEquals('after 0', cut)
        self.assertEqual((0, 7), context.get_interval())
        
        context = After('1 ') | Before(' is 2')
        cut = context.cut('after 0 and 3')
        self.assertFalse(cut)
        
    def test_complex_logic(self):
        context = (After('1') | After('2')) & (Before('3') & Before('4'))
        cut = context.cut(' 2 1 - 4 3')
        self.assertEqual(' - ', cut)
        self.assertEqual(cut, ' 2 1 - 4 3'[context.get_interval()[0] : context.get_interval()[1]])
        
    def test_null_interval(self):
        context = After("1") | Before("2")
        cut = context.cut("2 is before 1")
        self.assertFalse(cut)
        self.assertFalse(context.get_interval())
        
    def test_source(self):
        context = After(r'namespace')
        
if __name__ == "__main__":
    unittest.main()
    
