"""
LedgerLang AST Node definitions
"""

class Node:
    pass

class ProgramNode(Node):
    def __init__(self, statements):
        self.statements = statements
    def __repr__(self):
        return f'Program({self.statements})'

class VarDeclNode(Node):
    """ACCOUNT x = expr  |  RATE x = expr  |  VAR x = expr"""
    def __init__(self, kind, name, expr, line):
        self.kind = kind   # 'ACCOUNT' | 'RATE' | 'VAR'
        self.name = name
        self.expr = expr
        self.line = line
    def __repr__(self):
        return f'VarDecl({self.kind} {self.name} = {self.expr})'

class PortfolioDeclNode(Node):
    """PORTFOLIO name = [expr, expr, ...]"""
    def __init__(self, name, elements, line):
        self.name     = name
        self.elements = elements
        self.line     = line
    def __repr__(self):
        return f'Portfolio({self.name} = {self.elements})'

class AssignNode(Node):
    def __init__(self, name, expr, line):
        self.name = name
        self.expr = expr
        self.line = line
    def __repr__(self):
        return f'Assign({self.name} = {self.expr})'

class ComputeNode(Node):
    """COMPUTE name = expr"""
    def __init__(self, name, expr, line):
        self.name = name
        self.expr = expr
        self.line = line
    def __repr__(self):
        return f'Compute({self.name} = {self.expr})'

class IfNode(Node):
    def __init__(self, condition, then_body, else_body, line):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body  # may be None
        self.line      = line
    def __repr__(self):
        return f'If({self.condition}, then={self.then_body}, else={self.else_body})'

class RepeatNode(Node):
    def __init__(self, count, body, line):
        self.count = count
        self.body  = body
        self.line  = line
    def __repr__(self):
        return f'Repeat({self.count}, {self.body})'

class ShowNode(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line
    def __repr__(self):
        return f'Show({self.expr})'

class WarnNode(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line
    def __repr__(self):
        return f'Warn({self.expr})'

class ReportNode(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line
    def __repr__(self):
        return f'Report({self.expr})'

# ── Expressions ──────────────────────────────────────────────

class BinOpNode(Node):
    def __init__(self, left, op, right, line):
        self.left  = left
        self.op    = op
        self.right = right
        self.line  = line
    def __repr__(self):
        return f'BinOp({self.left} {self.op} {self.right})'

class UnaryOpNode(Node):
    def __init__(self, op, operand, line):
        self.op      = op
        self.operand = operand
        self.line    = line
    def __repr__(self):
        return f'UnaryOp({self.op}{self.operand})'

class NumberNode(Node):
    def __init__(self, value, line):
        self.value = value
        self.line  = line
    def __repr__(self):
        return f'Num({self.value})'

class StringNode(Node):
    def __init__(self, value, line):
        self.value = value
        self.line  = line
    def __repr__(self):
        return f'Str({repr(self.value)})'

class BoolNode(Node):
    def __init__(self, value, line):
        self.value = value
        self.line  = line
    def __repr__(self):
        return f'Bool({self.value})'

class IdentifierNode(Node):
    def __init__(self, name, line):
        self.name = name
        self.line = line
    def __repr__(self):
        return f'Id({self.name})'

class IndexNode(Node):
    """portfolio[index]"""
    def __init__(self, name, index, line):
        self.name  = name
        self.index = index
        self.line  = line
    def __repr__(self):
        return f'Index({self.name}[{self.index}])'
