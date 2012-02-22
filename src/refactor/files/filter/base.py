import re
import os

class ExtensionFilter(object):
    
    def __init__(self, extensions=[]):
        self.extensions = extensions
        
    def check(self, file):
        if not self.extensions:
            return True
        extension = os.path.splitext(file.get_path())[1]
        return extension[1:] in self.extensions

class ContentFilter(object):
    '''
    Filter a Finder by files content based on regular expressions
    Example:
        >> filter = ContentFilter(r'namespace Some\\Namespace;')
        >> finder = Finder('/some/path').extension('php').add_filter(filter)
        >> print list(finder)
        
    '''
    
    def __init__(self, content_pattern):
        self.content_pattern = re.compile(content_pattern)

    def check(self, file):
        if not self.content_pattern:
            return True
        if self.content_pattern.search(file.get_content()):
            return True
        
        return False


