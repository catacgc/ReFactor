import re

class Context(object):
    '''
    This class is an Abstract base class for Context objects
    A Context is used to limit the scope of a refactoring operation
    When a text is applied over a Context object through the cut method, the Context
    object must return the new content and set the interval that delimits the new content 
    from the original content 
    
    '''
    def __init__(self):
        self.start = None
        self.end = None
    
    def cut(self, content):
        raise Exception('Implement the get_context method in child class')
    
    def get_interval(self):
        if self.start == None or self.end == None:
            return None
        
        return (self.start, self.end)
    
    def __and__(self, context):
        return AndContext(self, context)
    
    def __or__(self, context):
        return OrContext(self, context)
    
class AndContext(Context):
    
    def __init__(self, left, right):
        Context.__init__(self)
        self.left = left
        self.right = right
        
    def cut(self, content):
        left = self.left.cut(content)
        if not left:
            return None
        
        right = self.right.cut(left)
        if not right:
            return None
        
        self.start = self.left.start
        self.end = self.start + self.right.end
        return right
    
    def __repr__(self):
        return '%r and %r' % (self.left, self.right)
    
class OrContext(Context):
    
    def __init__(self, left, right):
        Context.__init__(self)
        self.left = left
        self.right = right
        
    def cut(self, content):
        left = self.left.cut(content)
        if left:
            self.start = self.left.start
            self.end = self.left.end
            return left
        
        right = self.right.cut(content)
        if right:
            self.start = self.right.start
            self.end = self.right.end
            return right
        
        return None
        
    def __repr__(self):
        return '%r or %r' % (self.left, self.right)

class After(Context):
    
    def __init__(self, context_pattern, group=0):
        Context.__init__(self)
        
        self.group = group
        self.pattern = re.compile(context_pattern, re.MULTILINE)
        self.raw_pattern = context_pattern
    
    def cut(self, content):
        m = self.pattern.search(content)
        if not m:
            return
        
        self.start = m.end(self.group)
        self.end = len(content)
        
        return content[self.start:self.end]
    
    def __repr__(self):
        return 'After<%s> [%d,%d]' % (self.raw_pattern, self.start, self.end)

class Before(Context):
    
    def __init__(self, context_pattern, group=0):
        Context.__init__(self)
        
        self.group = group
        self.pattern = re.compile(context_pattern, re.MULTILINE)
        self.raw_pattern = context_pattern
    
    def cut(self, content):
        m = self.pattern.search(content)
        if not m:
            return
        
        self.start = 0
        self.end = m.start(self.group)
        
        return content[self.start:self.end]
    
    def __repr__(self):
        return 'Before<%s> [%d,%d]' % (self.raw_pattern, self.start, self.end)
    
class Identity(Context):
    
    def __init__(self):
        Context.__init__(self)
        self.start = 0
        
    def cut(self, content):
        self.end = len(content) 
        return content
    
class AfterLine(Context):
    
    def cut(self, content):
        found = False
        context = []
        self.start = 0
        
        for line in content.split():
            self.start += len(line)
            if self.pattern.match(line):
                found = True
                break
            
        if not found:
            self.start = None
            return
            
        self.end = len(content) 
        return "\n".join(context)
    
class BeforeLine(Context):
        
    def cut(self, content):
        context = []
        self.start = 0
        
        for line in content.split():
            if self.pattern.match(line):
                break
            context.append(line)
        
        return "\n".join(context)
    
    
