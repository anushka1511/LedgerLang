"""
LedgerLang Parser - Recursive Descent Parser
Builds an AST from the token stream produced by the Lexer.
"""

from lexer import (TT_KEYWORD, TT_IDENTIFIER, TT_INTEGER, TT_FLOAT,
                   TT_STRING, TT_OP, TT_ASSIGN, TT_LPAREN, TT_RPAREN,
                   TT_LBRACKET, TT_RBRACKET, TT_COMMA, TT_NEWLINE, TT_EOF)
from ast_nodes import *


class ParseError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line


class Parser:
    def __init__(self, tokens):
        # Strip newlines for easier parsing (we keep line info in tokens)
        self.tokens = [t for t in tokens if t.type != TT_NEWLINE]
        self.pos    = 0
        self.errors = []

    # ── Helpers ──────────────────────────────────────────────

    def current(self):
        return self.tokens[self.pos]

    def peek(self, offset=1):
        p = self.pos + offset
        if p < len(self.tokens):
            return self.tokens[p]
        return self.tokens[-1]  # EOF

    def advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def expect(self, type_, value=None):
        tok = self.current()
        if tok.type != type_:
            raise ParseError(
                f"Expected {type_} but got {tok.type} ({repr(tok.value)})", tok.line)
        if value is not None and tok.value != value:
            raise ParseError(
                f"Expected {repr(value)} but got {repr(tok.value)}", tok.line)
        return self.advance()

    def match(self, type_, value=None):
        tok = self.current()
        if tok.type != type_:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def skip_to_next_statement(self):
        """Error recovery: skip tokens until a statement-starting keyword or EOF."""
        starters = {'ACCOUNT','RATE','VAR','COMPUTE','IF','REPEAT',
                    'SHOW','WARN','REPORT','PORTFOLIO','END','ELSE'}
        # Always advance at least one token to prevent infinite loops
        if self.current().type != TT_EOF:
            self.advance()
        while self.current().type != TT_EOF:
            if self.current().type == TT_KEYWORD and self.current().value in starters:
                break
            self.advance()

    # ── Top-level ────────────────────────────────────────────

    def parse(self):
        statements = []
        while self.current().type != TT_EOF:
            try:
                stmt = self.parse_statement()
                if stmt:
                    statements.append(stmt)
            except ParseError as e:
                self.errors.append(f'Line {e.line}: {e}')
                self.skip_to_next_statement()
        return ProgramNode(statements), self.errors

    # ── Statements ───────────────────────────────────────────

    def parse_statement(self):
        tok = self.current()

        if tok.type == TT_KEYWORD:
            if tok.value in ('ACCOUNT', 'RATE', 'VAR'):
                return self.parse_var_decl()
            if tok.value == 'PORTFOLIO':
                return self.parse_portfolio_decl()
            if tok.value == 'COMPUTE':
                return self.parse_compute()
            if tok.value == 'IF':
                return self.parse_if()
            if tok.value == 'REPEAT':
                return self.parse_repeat()
            if tok.value == 'SHOW':
                return self.parse_output('SHOW')
            if tok.value == 'WARN':
                return self.parse_output('WARN')
            if tok.value == 'REPORT':
                return self.parse_output('REPORT')

        if tok.type == TT_IDENTIFIER:
            return self.parse_assignment()

        raise ParseError(f'Unexpected token {repr(tok.value)}', tok.line)

    def parse_var_decl(self):
        kind_tok = self.advance()        # ACCOUNT | RATE | VAR
        name_tok = self.expect(TT_IDENTIFIER)
        self.expect(TT_ASSIGN)
        expr = self.parse_expression()
        return VarDeclNode(kind_tok.value, name_tok.value, expr, kind_tok.line)

    def parse_portfolio_decl(self):
        line = self.current().line
        self.advance()                   # PORTFOLIO
        name_tok = self.expect(TT_IDENTIFIER)
        self.expect(TT_ASSIGN)
        self.expect(TT_LBRACKET)
        elements = []
        if not self.match(TT_RBRACKET):
            elements.append(self.parse_expression())
            while self.match(TT_COMMA):
                self.advance()
                elements.append(self.parse_expression())
        self.expect(TT_RBRACKET)
        return PortfolioDeclNode(name_tok.value, elements, line)

    def parse_compute(self):
        line = self.current().line
        self.advance()                   # COMPUTE
        name_tok = self.expect(TT_IDENTIFIER)
        self.expect(TT_ASSIGN)
        expr = self.parse_expression()
        return ComputeNode(name_tok.value, expr, line)

    def parse_assignment(self):
        name_tok = self.advance()        # identifier
        self.expect(TT_ASSIGN)
        expr = self.parse_expression()
        return AssignNode(name_tok.value, expr, name_tok.line)

    def parse_if(self):
        line = self.current().line
        self.advance()                   # IF
        condition = self.parse_expression()
        self.expect(TT_KEYWORD, 'THEN')
        then_body = self.parse_body()
        else_body = None
        if self.match(TT_KEYWORD, 'ELSE'):
            self.advance()
            else_body = self.parse_body()
        self.expect(TT_KEYWORD, 'END')
        return IfNode(condition, then_body, else_body, line)

    def parse_repeat(self):
        line = self.current().line
        self.advance()                   # REPEAT
        count = self.parse_expression()
        self.expect(TT_KEYWORD, 'TIMES')
        body = self.parse_body()
        self.expect(TT_KEYWORD, 'END')
        return RepeatNode(count, body, line)

    def parse_output(self, kind):
        line = self.current().line
        self.advance()                   # SHOW | WARN | REPORT
        expr = self.parse_expression()
        if kind == 'SHOW':
            return ShowNode(expr, line)
        if kind == 'WARN':
            return WarnNode(expr, line)
        return ReportNode(expr, line)

    def parse_body(self):
        """Parse statements until ELSE / END / EOF."""
        stmts = []
        while self.current().type != TT_EOF:
            if self.match(TT_KEYWORD, 'END') or self.match(TT_KEYWORD, 'ELSE'):
                break
            try:
                stmt = self.parse_statement()
                if stmt:
                    stmts.append(stmt)
            except ParseError as e:
                self.errors.append(f'Line {e.line}: {e}')
                self.skip_to_next_statement()
        return stmts

    # ── Expressions (recursive descent) ──────────────────────
    # Precedence (low → high):
    #   OR  →  AND  →  NOT  →  comparison  →  add/sub  →  mul/div  →  unary  →  primary

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.match(TT_KEYWORD, 'OR'):
            op = self.advance().value
            right = self.parse_and()
            left = BinOpNode(left, op, right, self.current().line)
        return left

    def parse_and(self):
        left = self.parse_not()
        while self.match(TT_KEYWORD, 'AND'):
            op = self.advance().value
            right = self.parse_not()
            left = BinOpNode(left, op, right, self.current().line)
        return left

    def parse_not(self):
        if self.match(TT_KEYWORD, 'NOT'):
            line = self.current().line
            self.advance()
            operand = self.parse_not()
            return UnaryOpNode('NOT', operand, line)
        return self.parse_comparison()

    def parse_comparison(self):
        left = self.parse_additive()
        comp_ops = {'==', '!=', '<', '>', '<=', '>='}
        while self.match(TT_OP) and self.current().value in comp_ops:
            op = self.advance().value
            right = self.parse_additive()
            left = BinOpNode(left, op, right, self.current().line)
        return left

    def parse_additive(self):
        left = self.parse_multiplicative()
        while self.match(TT_OP) and self.current().value in ('+', '-'):
            op = self.advance().value
            right = self.parse_multiplicative()
            left = BinOpNode(left, op, right, self.current().line)
        return left

    def parse_multiplicative(self):
        left = self.parse_unary()
        while self.match(TT_OP) and self.current().value in ('*', '/'):
            op = self.advance().value
            right = self.parse_unary()
            left = BinOpNode(left, op, right, self.current().line)
        return left

    def parse_unary(self):
        if self.match(TT_OP, '-'):
            line = self.current().line
            self.advance()
            operand = self.parse_unary()
            return UnaryOpNode('-', operand, line)
        return self.parse_primary()

    def parse_primary(self):
        tok = self.current()

        # Parenthesised expression
        if tok.type == TT_LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TT_RPAREN)
            return expr

        # Number literals
        if tok.type in (TT_INTEGER, TT_FLOAT):
            self.advance()
            return NumberNode(tok.value, tok.line)

        # String literal
        if tok.type == TT_STRING:
            self.advance()
            return StringNode(tok.value, tok.line)

        # Boolean literals
        if tok.type == TT_KEYWORD and tok.value in ('TRUE', 'FALSE'):
            self.advance()
            return BoolNode(tok.value == 'TRUE', tok.line)

        # Identifier or array index
        if tok.type == TT_IDENTIFIER:
            self.advance()
            if self.match(TT_LBRACKET):
                self.advance()
                index = self.parse_expression()
                self.expect(TT_RBRACKET)
                return IndexNode(tok.value, index, tok.line)
            return IdentifierNode(tok.value, tok.line)

        raise ParseError(f'Unexpected token in expression: {repr(tok.value)}', tok.line)
