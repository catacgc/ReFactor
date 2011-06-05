import re

class ContentFilter(object):
    '''
    Filter a Finder by files content based on regular expressions
    Example:
        >> finder = Finder('/some/path').extension('php')
        >> filter = ContentFilter(finder).only(r'namespace Some\\Namesapce;')
        >> print list(filter)
        
    '''
    
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


