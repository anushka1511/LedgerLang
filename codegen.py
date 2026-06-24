"""
LedgerLang Code Generator
Generates executable Python directly from the AST.
"""

from ast_nodes import *


class CodeGenerator:
    def __init__(self, ast):
        self.ast    = ast
        self.output = []
        self.indent = 0

    def emit(self, line=''):
        if line == '':
            self.output.append('')
        else:
            self.output.append('    ' * self.indent + line)

    def generate(self):
        self.emit('# ── LedgerLang Generated Code ──────────────────────────')
        self.emit('import sys')
        self.emit('')
        self.emit('def ledger_show(val):')
        self.indent += 1
        self.emit('print(f"[SHOW]   {val}")')
        self.indent -= 1
        self.emit('')
        self.emit('def ledger_warn(val):')
        self.indent += 1
        self.emit('print(f"[WARN]   {val}")')
        self.indent -= 1
        self.emit('')
        self.emit('def ledger_report(val):')
        self.indent += 1
        self.emit('print(f"[REPORT] {val}")')
        self.indent -= 1
        self.emit('')
        self.emit('# ── Runtime ─────────────────────────────────────────────')
        self.emit('')

        for stmt in self.ast.statements:
            self.gen_stmt(stmt)

        return '\n'.join(self.output)

    def gen_stmt(self, node):
        if isinstance(node, (VarDeclNode, ComputeNode)):
            self.emit(f'{node.name} = {self.gen_expr(node.expr)}')

        elif isinstance(node, AssignNode):
            self.emit(f'{node.name} = {self.gen_expr(node.expr)}')

        elif isinstance(node, PortfolioDeclNode):
            elems = ', '.join(self.gen_expr(e) for e in node.elements)
            self.emit(f'{node.name} = [{elems}]')

        elif isinstance(node, IfNode):
            self.emit(f'if {self.gen_expr(node.condition)}:')
            self.indent += 1
            for s in node.then_body:
                self.gen_stmt(s)
            if not node.then_body:
                self.emit('pass')
            self.indent -= 1
            if node.else_body:
                self.emit('else:')
                self.indent += 1
                for s in node.else_body:
                    self.gen_stmt(s)
                self.indent -= 1

        elif isinstance(node, RepeatNode):
            count = self.gen_expr(node.count)
            self.emit(f'for _i in range({count}):')
            self.indent += 1
            for s in node.body:
                self.gen_stmt(s)
            if not node.body:
                self.emit('pass')
            self.indent -= 1

        elif isinstance(node, ShowNode):
            self.emit(f'ledger_show({self.gen_expr(node.expr)})')

        elif isinstance(node, WarnNode):
            self.emit(f'ledger_warn({self.gen_expr(node.expr)})')

        elif isinstance(node, ReportNode):
            self.emit(f'ledger_report({self.gen_expr(node.expr)})')

    def gen_expr(self, node):
        if isinstance(node, NumberNode):
            return str(node.value)
        if isinstance(node, StringNode):
            return f'"{node.value}"'
        if isinstance(node, BoolNode):
            return 'True' if node.value else 'False'
        if isinstance(node, IdentifierNode):
            return node.name
        if isinstance(node, IndexNode):
            return f'{node.name}[{self.gen_expr(node.index)}]'
        if isinstance(node, BinOpNode):
            op = node.op
            if op == 'AND': op = 'and'
            if op == 'OR':  op = 'or'
            return f'({self.gen_expr(node.left)} {op} {self.gen_expr(node.right)})'
        if isinstance(node, UnaryOpNode):
            op = 'not ' if node.op == 'NOT' else node.op
            return f'({op}{self.gen_expr(node.operand)})'
        return '0'
