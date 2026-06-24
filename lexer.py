"""
LedgerLang Lexer - Tokenizes LedgerLang source code
"""

import re

# Token types
TT_KEYWORD    = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_INTEGER    = 'INTEGER'
TT_FLOAT      = 'FLOAT'
TT_STRING     = 'STRING'
TT_OP         = 'OP'
TT_ASSIGN     = 'ASSIGN'
TT_LPAREN     = 'LPAREN'
TT_RPAREN     = 'RPAREN'
TT_LBRACKET   = 'LBRACKET'
TT_RBRACKET   = 'RBRACKET'
TT_COMMA      = 'COMMA'
TT_NEWLINE    = 'NEWLINE'
TT_EOF        = 'EOF'

KEYWORDS = {
    'ACCOUNT', 'RATE', 'VAR', 'COMPUTE',
    'IF', 'THEN', 'ELSE', 'END',
    'REPEAT', 'TIMES',
    'SHOW', 'WARN', 'REPORT',
    'PORTFOLIO', 'AND', 'OR', 'NOT',
    'TRUE', 'FALSE'
}

OPERATORS = ['>=', '<=', '!=', '==', '>', '<', '+', '-', '*', '/']

class Token:
    def __init__(self, type_, value, line):
        self.type  = type_
        self.value = value
        self.line  = line

    def __repr__(self):
        return f'Token({self.type}, {repr(self.value)}, line={self.line})'


class LexerError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos    = 0
        self.line   = 1
        self.tokens = []
        self.errors = []

    def current(self):
        if self.pos < len(self.source):
            return self.source[self.pos]
        return None

    def peek(self, offset=1):
        p = self.pos + offset
        if p < len(self.source):
            return self.source[p]
        return None

    def advance(self):
        ch = self.source[self.pos]
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def skip_whitespace(self):
        while self.current() in (' ', '\t', '\r'):
            self.advance()

    def skip_comment(self):
        # Comments start with #
        while self.current() is not None and self.current() != '\n':
            self.advance()

    def read_string(self):
        line = self.line
        self.advance()  # skip opening quote
        s = ''
        while self.current() is not None and self.current() != '"':
            if self.current() == '\n':
                self.errors.append(f'Line {line}: Unterminated string literal')
                break
            s += self.advance()
        if self.current() == '"':
            self.advance()  # skip closing quote
        else:
            self.errors.append(f'Line {line}: Unterminated string literal')
        return Token(TT_STRING, s, line)

    def read_number(self):
        line = self.line
        num  = ''
        is_float = False
        while self.current() is not None and (self.current().isdigit() or self.current() == '.'):
            if self.current() == '.':
                if is_float:
                    self.errors.append(f'Line {line}: Invalid number format')
                    break
                is_float = True
            num += self.advance()
        if is_float:
            return Token(TT_FLOAT, float(num), line)
        return Token(TT_INTEGER, int(num), line)

    def read_identifier_or_keyword(self):
        line = self.line
        word = ''
        while self.current() is not None and (self.current().isalnum() or self.current() == '_'):
            word += self.advance()
        upper = word.upper()
        if upper in KEYWORDS:
            return Token(TT_KEYWORD, upper, line)
        return Token(TT_IDENTIFIER, word, line)

    def read_operator(self):
        line = self.line
        # Try two-char operators first
        two = self.source[self.pos:self.pos+2]
        if two in OPERATORS:
            self.pos += 2
            return Token(TT_OP, two, line)
        one = self.current()
        if one in [o for o in OPERATORS if len(o) == 1]:
            self.advance()
            return Token(TT_OP, one, line)
        return None

    def tokenize(self):
        while self.pos < len(self.source):
            self.skip_whitespace()
            ch = self.current()

            if ch is None:
                break

            # Comment
            if ch == '#':
                self.skip_comment()
                continue

            # Newline
            if ch == '\n':
                self.tokens.append(Token(TT_NEWLINE, '\\n', self.line))
                self.advance()
                continue

            # String
            if ch == '"':
                self.tokens.append(self.read_string())
                continue

            # Number
            if ch.isdigit():
                self.tokens.append(self.read_number())
                continue

            # Identifier or keyword
            if ch.isalpha() or ch == '_':
                self.tokens.append(self.read_identifier_or_keyword())
                continue

            # Assignment
            if ch == '=' and self.peek() != '=':
                self.tokens.append(Token(TT_ASSIGN, '=', self.line))
                self.advance()
                continue

            # Operators
            op_token = self.read_operator()
            if op_token:
                self.tokens.append(op_token)
                continue

            # Punctuation
            if ch == '(':
                self.tokens.append(Token(TT_LPAREN, '(', self.line))
                self.advance()
                continue
            if ch == ')':
                self.tokens.append(Token(TT_RPAREN, ')', self.line))
                self.advance()
                continue
            if ch == '[':
                self.tokens.append(Token(TT_LBRACKET, '[', self.line))
                self.advance()
                continue
            if ch == ']':
                self.tokens.append(Token(TT_RBRACKET, ']', self.line))
                self.advance()
                continue
            if ch == ',':
                self.tokens.append(Token(TT_COMMA, ',', self.line))
                self.advance()
                continue

            # Unknown character
            self.errors.append(f'Line {self.line}: Unknown character {repr(ch)}')
            self.advance()

        self.tokens.append(Token(TT_EOF, None, self.line))
        return self.tokens, self.errors
