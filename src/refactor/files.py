import os
import re

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
        self._extensions = None
    
    def extension(self, *args):
        '''
        Filter files by the given extensions 
        @return: Finder
        '''
        self._extensions = args
        return self
        
    def exclude(self, *args):
        self._excluded = [re.compile(arg) for arg in args]
        return self
        
    def include(self, *args):
        self._included = [re.compile(arg) for arg in args]
        return self
    
    def is_valid(self, path):
        return  self._match_extension(path) \
                and not self._is_excluded(path) \
                and self._is_included(path)
    
    def _match_extension(self, path):
        if not self._extensions:
            return True
        extension = os.path.splitext(path)[1]
        return extension[1:] in self._extensions
        
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
        return len([1 for file in self])
    
    def __iter__(self):
        for root, subdirs, files in os.walk(self._path):
            for filename in files:
                path = root + '/' + filename
                
                if self.is_valid(path):
                    yield path
                    
        self._finished = True
    
    def __repr__(self):
        return "Finder(path=%s,extensions=%r,include=%r,exclude=%r)" % \
            (self._path, ",".join(self._extensions), self._included, self._excluded)
    

class ContentFilter(object):
    
    def __init__(self, files_list):
        self._finder = files_list
        self._exclude_patterns = []
        self._include_patterns = []
        
    def only(self, content_pattern):
        self._include_patterns.append(re.compile(content_pattern))
        return self
    
    def without(self, content_pattern):
        self._exclude_patterns.append(re.compile(content_pattern))
        return self
    

    def _is_allowed(self, filename):
        if not self._include_patterns:
            return True
        with open(filename, 'r') as f:
            content = f.read()
            for _re in self._include_patterns:
                if _re.search(content):
                    return True
        return False
    
    def _is_restricted(self, filename):
        if not self._exclude_patterns:
            return False
        with open(filename, 'r') as f:
            content = f.read()
            for _re in self._exclude_patterns:
                if _re.search(content):
                    return True
        return False
             
    
    def is_valid(self, filename):
        return self._is_allowed(filename) and not self._is_restricted(filename)
    
    
    def __iter__(self):
        for filename in self._finder:
            if self.is_valid(filename):
                yield filename
                
    def __len__(self):
        return len([1 for filename in self])


