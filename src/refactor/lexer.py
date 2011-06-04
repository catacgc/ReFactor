import re
from pygments.lexer import RegexLexer, bygroups, using, this
from pygments.util import get_bool_opt, get_list_opt
from pygments.token import *

class PhpLexer(RegexLexer):

    name = 'PHP'
    aliases = ['php', 'php3', 'php4', 'php5']
    filenames = ['*.php', '*.php[345]']
    mimetypes = ['text/x-php']

    flags = re.IGNORECASE | re.DOTALL | re.MULTILINE
    tokens = {
        'root': [
            (r'<\?(php)?', Comment.Preproc, 'php'),
            (r'[^<]+', Other),
            (r'<', Other)
        ],
        'php': [
            (r'\?>', Comment.Preproc, '#pop'),
            (r'<<<(\'?)([a-zA-Z_][a-zA-Z0-9_]*)\1\n.*?\n\2\;?\n', String),
            (r'\s+', Text),
            (r'#.*?\n', Comment.Single),
            (r'//.*?\n', Comment.Single),
            # put the empty comment here, it is otherwise seen as
            # the start of a docstring
            (r'/\*\*/', Comment.Multiline),
            (r'/\*\*.*?\*/', String.Doc),
            (r'/\*.*?\*/', Comment.Multiline),
            (r'(->|::)(\s*)([a-zA-Z_][a-zA-Z0-9_]*)', bygroups(Operator, Text, Name.Attribute)),
            (r'[~!%^&*+=|:.<>/?@-]+', Operator),
            (r'[\[\]{}();,]+', Punctuation),
            (r'(namespace)(\s+)', bygroups(Keyword, Text), 'namespacename'),
            (r'(use)(\s+)', bygroups(Keyword, Text), 'uselist'),
            (r'(class)(\s+)', bygroups(Keyword, Text), 'classdef'),
            (r'(function)(\s*)(?=\()', bygroups(Keyword, Text)),
            (r'(function)(\s+)(&?)(\s*)', bygroups(Keyword, Text, Operator, Text), 'functionname'),
            (r'(const)(\s+)([a-zA-Z_][a-zA-Z0-9_]*)', bygroups(Keyword, Text, Name.Constant)),
            (r'(new)(\s+)([\\a-zA-Z0-9_]*)', bygroups(Keyword, Text, Name.Class)),
            (r'(and|E_PARSE|old_function|E_ERROR|or|as|E_WARNING|parent|'
             r'eval|PHP_OS|break|exit|case|PHP_VERSION|cfunction|'
             r'FALSE|print|for|require|continue|foreach|require_once|'
             r'declare|return|default|static|do|switch|die|stdClass|'
             r'echo|else|TRUE|elseif|var|empty|if|xor|enddeclare|include|'
             r'virtual|endfor|include_once|while|endforeach|global|__FILE__|'
             r'endif|list|__LINE__|endswitch|new|__sleep|endwhile|not|'
             r'array|__wakeup|E_ALL|NULL|final|php_user_filter|'
             r'implements|public|private|protected|abstract|clone|try|'
             r'catch|throw|this)\b', Keyword),
            ('(true|false|null)\b', Keyword.Constant),
            (r'\$\{\$+[a-zA-Z_][a-zA-Z0-9_]*\}', Name.Variable),
            (r'\$+[a-zA-Z_][a-zA-Z0-9_]*', Name.Variable),
            (r'[\\a-zA-Z_][\\a-zA-Z0-9_]*', Name.Other),
            (r'(\d+\.\d*|\d*\.\d+)([eE][+-]?[0-9]+)?', Number.Float),
            (r'\d+[eE][+-]?[0-9]+', Number.Float),
            (r'0[0-7]+', Number.Oct),
            (r'0[xX][a-fA-F0-9]+', Number.Hex),
            (r'\d+', Number.Integer),
            (r"'([^'\\]*(?:\\.[^'\\]*)*)'", String.Single),
            (r'`([^`\\]*(?:\\.[^`\\]*)*)`', String.Backtick),
            (r'"', String.Double, 'string'),
        ],
        'namespacename' : [
            (r'[a-zA-Z_][\\a-zA-Z0-9_]*', Name.Namespace, '#pop')
        ],
        'uselist' : [
            (r'\s+', Text),
            (r',', Punctuation),
            (r';', Punctuation, '#pop'),
            (r'[\\a-zA-Z0-9_]*', Name.Use)
        ],
        'classdef': [
            (r'\{', Punctuation, '#pop'),
            (r',', Punctuation),
            (r'\s+', Text),
            (r'(extends)(\s+)([\\a-zA-Z0-9_]*)', bygroups(Keyword, Text, Name.Class.Parent)),
            (r'implements', Keyword, 'interfacelist'),
            (r'[a-zA-Z_][\\a-zA-Z0-9_]*', Name.Class),
        ],
        'interfacelist': [
            (r'\s+', Text),
            (r',', Punctuation),
            (r'\{', Punctuation, 'php'),
            (r'[\\a-zA-Z0-9_]*', Name.Interface)
        ],
        'functionname': [
            (r'[a-zA-Z_][a-zA-Z0-9_]*', Name.Function, '#pop')
        ],
        'string': [
            (r'"', String.Double, '#pop'),
            (r'[^{$"\\]+', String.Double),
            (r'\\([nrt\"$\\]|[0-7]{1,3}|x[0-9A-Fa-f]{1,2})', String.Escape),
            (r'\$[a-zA-Z_][a-zA-Z0-9_]*(\[\S+\]|->[a-zA-Z_][a-zA-Z0-9_]*)?',
             String.Interpol),
            (r'(\{\$\{)(.*?)(\}\})',
             bygroups(String.Interpol, using(this, _startinline=True),
                      String.Interpol)),
            (r'(\{)(\$.*?)(\})',
             bygroups(String.Interpol, using(this, _startinline=True),
                      String.Interpol)),
            (r'(\$\{)(\S+)(\})',
             bygroups(String.Interpol, Name.Variable, String.Interpol)),
            (r'[${\\]+', String.Double)
        ],
    }

    def __init__(self, **options):
        self.funcnamehighlighting = get_bool_opt(
            options, 'funcnamehighlighting', True)
        self.disabledmodules = get_list_opt(
            options, 'disabledmodules', ['unknown'])
        self.startinline = get_bool_opt(options, 'startinline', False)

        # private option argument for the lexer itself
        if '_startinline' in options:
            self.startinline = options.pop('_startinline')

        # collect activated functions in a set
        self._functions = set()
        if self.funcnamehighlighting:
            from pygments.lexers._phpbuiltins import MODULES
            for key, value in MODULES.iteritems():
                if key not in self.disabledmodules:
                    self._functions.update(value)
        RegexLexer.__init__(self, **options)

    def get_tokens_unprocessed(self, text):
        stack = ['root']
        if self.startinline:
            stack.append('php')
        for index, token, value in \
            RegexLexer.get_tokens_unprocessed(self, text, stack):
            if token is Name.Other:
                if value in self._functions:
                    yield index, Name.Builtin, value
                    continue
            yield index, token, value
            