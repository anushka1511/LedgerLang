"""
LedgerLang Intermediate Code Generator
Produces Three-Address Code (TAC) from the AST.
"""

from ast_nodes import *


class ICGError(Exception):
    def __init__(self, message, line):
        super().__init__(message)
        self.line = line


class ICG:
    def __init__(self):
        self.instructions = []   # list of TAC strings
        self.temp_count   = 0
        self.label_count  = 0
        self.errors       = []
        self.symbol_table = {}   # name -> type hint

    def new_temp(self):
        self.temp_count += 1
        return f't{self.temp_count}'

    def new_label(self):
        self.label_count += 1
        return f'L{self.label_count}'

    def emit(self, instr):
        self.instructions.append(instr)

    # ── Entry point ──────────────────────────────────────────

    def generate(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                try:
                    self.gen_stmt(stmt)
                except ICGError as e:
                    self.errors.append(f'Line {e.line}: {e}')
        return self.instructions, self.errors

    # ── Statements ───────────────────────────────────────────

    def gen_stmt(self, node):
        if isinstance(node, (VarDeclNode, ComputeNode)):
            t = self.gen_expr(node.expr)
            self.emit(f'{node.name} = {t}')
            self.symbol_table[node.name] = 'var'

        elif isinstance(node, AssignNode):
            t = self.gen_expr(node.expr)
            self.emit(f'{node.name} = {t}')

        elif isinstance(node, PortfolioDeclNode):
            for i, elem in enumerate(node.elements):
                t = self.gen_expr(elem)
                self.emit(f'{node.name}[{i}] = {t}')
            self.symbol_table[node.name] = 'array'

        elif isinstance(node, IfNode):
            self.gen_if(node)

        elif isinstance(node, RepeatNode):
            self.gen_repeat(node)

        elif isinstance(node, ShowNode):
            t = self.gen_expr(node.expr)
            self.emit(f'SHOW {t}')

        elif isinstance(node, WarnNode):
            t = self.gen_expr(node.expr)
            self.emit(f'WARN {t}')

        elif isinstance(node, ReportNode):
            t = self.gen_expr(node.expr)
            self.emit(f'REPORT {t}')

        else:
            raise ICGError(f'Unknown statement node: {type(node).__name__}', 0)

    def gen_if(self, node):
        cond   = self.gen_expr(node.condition)
        l_else = self.new_label()
        l_end  = self.new_label()

        self.emit(f'IF_FALSE {cond} GOTO {l_else}')
        for stmt in node.then_body:
            self.gen_stmt(stmt)
        if node.else_body:
            self.emit(f'GOTO {l_end}')
        self.emit(f'{l_else}:')
        if node.else_body:
            for stmt in node.else_body:
                self.gen_stmt(stmt)
            self.emit(f'{l_end}:')

    def gen_repeat(self, node):
        count_temp = self.gen_expr(node.count)
        loop_var   = self.new_temp()
        l_start    = self.new_label()
        l_end      = self.new_label()

        self.emit(f'{loop_var} = 0')
        self.emit(f'{l_start}:')
        cmp_temp = self.new_temp()
        self.emit(f'{cmp_temp} = {loop_var} < {count_temp}')
        self.emit(f'IF_FALSE {cmp_temp} GOTO {l_end}')
        for stmt in node.body:
            self.gen_stmt(stmt)
        self.emit(f'{loop_var} = {loop_var} + 1')
        self.emit(f'GOTO {l_start}')
        self.emit(f'{l_end}:')

    # ── Expressions ──────────────────────────────────────────

    def gen_expr(self, node):
        if isinstance(node, NumberNode):
            return str(node.value)

        if isinstance(node, StringNode):
            return f'"{node.value}"'

        if isinstance(node, BoolNode):
            return '1' if node.value else '0'

        if isinstance(node, IdentifierNode):
            return node.name

        if isinstance(node, IndexNode):
            idx = self.gen_expr(node.index)
            t   = self.new_temp()
            self.emit(f'{t} = {node.name}[{idx}]')
            return t

        if isinstance(node, BinOpNode):
            left  = self.gen_expr(node.left)
            right = self.gen_expr(node.right)
            t     = self.new_temp()
            self.emit(f'{t} = {left} {node.op} {right}')
            return t

        if isinstance(node, UnaryOpNode):
            operand = self.gen_expr(node.operand)
            t       = self.new_temp()
            self.emit(f'{t} = {node.op} {operand}')
            return t

        raise ICGError(f'Unknown expression node: {type(node).__name__}', 0)
