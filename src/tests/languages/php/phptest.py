'''
Created on May 27, 2011

@author: catalin
'''
import unittest
from refactor.language.php import *
from refactor import *


class PhpTest(unittest.TestCase):
    
    def testRenameMethod(self):
#        for file in Finder('./sources'):
#            for method in file.get(PhpMethodCall('loadConfig')):
#                if method.caller() not in ['$cfg', '$config', 'config', 'cfg']:
#                    continue
#                method.rename('load')
#                method.arguments[1] = '$x'
#                pass
#                
        lexer = PhpLexer()
        with open('sources/Cache.php') as f:
            tokens = lexer.get_tokens_unprocessed("".join(f.readlines()))
            for token in tokens:
                print token
            


if __name__ == "__main__":
    unittest.main()