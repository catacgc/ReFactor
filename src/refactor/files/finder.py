import os
import re
from filter.base import *

class File(object):
    
    def __init__(self, path):
        self.path = path
        self.content = None
        
    def get_path(self):
        return self.path
        
    def get_content(self):
        if self.content != None:
            return self.content
        
        f = open(self.path)
        self.content = f.read()
        f.close()
        
        return self.content
    
    def __repr__(self):
        return 'File<%s>' % self.path
    
class Finder(object):
    '''
    This class scans files from given path and filters them by extension, 
    or include/exclude regular expressions
    
    @author: Catalin Costache <catalin.g.costache@gmail.com>
    
    Example:
    >> finder = Finder('/some/path') \
    >>        .extension('js', 'html') \
    >>        .exclude(r'\.svn|hg|git') \
    >>        .include(r'/app|library') \
    >> print len(finder)
    >> print list(finder)
    >> for filename in finder:
    >>     print filemame
    
    '''

    def __init__(self, path):
        '''
        Creates a new Finder
        @param path: the reference path where to start looking for files 
        '''
        self._path = path
        self._finished = False
        self._excluded = None
        self._included = None
        self._filters = []
    
    def extension(self, *args):
        '''
        Filter files by the given extensions 
        @return: Finder
        '''
        self.filter(ExtensionFilter(args))
        return self
    
    def filter(self, filter):
        self._filters.append(filter)
        return self
    
    def exclude(self, *args):
        self._excluded = [re.compile(arg) for arg in args]
        return self
        
    def include(self, *args):
        self._included = [re.compile(arg) for arg in args]
        return self
    
    def is_valid(self, path):
        return  not self._is_excluded(path) \
                and self._is_included(path)
    
    def _match_filters(self, fileobject):
        for filter in self._filters:
            if not filter.check(fileobject):
                return False
            
        return True
        
    def _is_excluded(self, path):
        if not self._excluded:
            return False
        for _re in self._excluded:
            if _re.search(path):
                return True
        return False
    
    def _is_included(self, path):
        if not self._included:
            return True
        for _re in self._included:
            if _re.search(path):
                return True 
        return False
    
    def __len__(self):
        return len([1 for filename in self])
    
    def __iter__(self):
        for root, subdirs, files in os.walk(self._path):
            for filename in files:
                path = root + '/' + filename
                
                
                if self.is_valid(path):
                    f = File(path)
                    if self._match_filters(f):
                        yield f
                    
        self._finished = True
    
    def __repr__(self):
        return "Finder(path=%s)" % self._path
    