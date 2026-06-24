"""
LedgerLang Compiler - Main Driver
Usage:
    python compiler.py <source_file>
    python compiler.py <source_file> --debug
    python compiler.py <source_file> --save
"""

import sys, os, argparse
from lexer    import Lexer
from parser   import Parser
from icg      import ICG
from codegen  import CodeGenerator

BANNER = """
╔══════════════════════════════════════════════════╗
║         LedgerLang Compiler  v1.0                ║
║   A Financial Domain Specific Language           ║
╚══════════════════════════════════════════════════╝"""

def section(title):
    print(f'\n{"─"*52}\n  {title}\n{"─"*52}')

def make_listing(source_lines, all_errors):
    err_map = {}
    for e in all_errors:
        parts = e.split(':', 1)
        try:
            ln = int(parts[0].replace('Line','').strip())
        except ValueError:
            ln = 0
        err_map.setdefault(ln, []).append(e)
    out = []
    for i, line in enumerate(source_lines, 1):
        out.append(f'{i:4d} | {line}')
        for msg in err_map.get(i, []):
            out.append(f'     >>> ERROR: {msg}')
    for msg in err_map.get(0, []):
        out.append(f'     >>> ERROR: {msg}')
    return '\n'.join(out)

def compile_source(source, debug=False):
    source_lines = source.splitlines()
    all_errors   = []
    print(BANNER)

    # ── Stage 1: Lexer ────────────────────────────────────────
    section('STAGE 1 — LEXICAL ANALYSIS')
    lexer = Lexer(source)
    tokens, lex_errors = lexer.tokenize()
    all_errors.extend(lex_errors)
    if debug:
        print('\nTokens:')
        for t in tokens: print(f'  {t}')
    if lex_errors:
        print('\nLexer errors:')
        for e in lex_errors: print(f'  {e}')
    else:
        print(f'  ✓ {len(tokens)-1} tokens, no errors.')

    # ── Stage 2: Parser ───────────────────────────────────────
    section('STAGE 2 — SYNTAX ANALYSIS (PARSING)')
    parser = Parser(tokens)
    ast, parse_errors = parser.parse()
    all_errors.extend(parse_errors)
    if debug:
        print('\nAST:')
        for s in ast.statements: print(f'  {s}')
    if parse_errors:
        print('\nParser errors:')
        for e in parse_errors: print(f'  {e}')
    else:
        print(f'  ✓ AST: {len(ast.statements)} top-level statements, no errors.')

    # ── Stage 3: ICG ──────────────────────────────────────────
    section('STAGE 3 — INTERMEDIATE CODE (THREE-ADDRESS CODE)')
    icg = ICG()
    tac, icg_errors = icg.generate(ast)
    all_errors.extend(icg_errors)
    if tac:
        print('\nThree-Address Code:')
        for idx, instr in enumerate(tac, 1):
            print(f'  {idx:3d}:  {instr}')
    if icg_errors:
        print('\nICG errors:')
        for e in icg_errors: print(f'  {e}')
    else:
        print(f'\n  ✓ {len(tac)} TAC instructions, no errors.')

    # ── Listing File ──────────────────────────────────────────
    section('LISTING FILE')
    print(make_listing(source_lines, all_errors))

    # ── Stage 4: Code Generation ──────────────────────────────
    if all_errors:
        section('STAGE 4 — CODE GENERATION')
        print(f'\n  ✗ Skipped — {len(all_errors)} error(s) found above.')
        return None, ast

    section('STAGE 4 — CODE GENERATION (Python target)')
    codegen = CodeGenerator(ast)
    code = codegen.generate()
    print('\nGenerated Python:')
    for line in code.splitlines():
        print(f'  {line}')
    return code, ast

def run_code(code):
    section('EXECUTION OUTPUT')
    try:
        exec(compile(code, '<ledgerlang>', 'exec'), {})
    except Exception as e:
        print(f'  Runtime error: {e}')

def main():
    ap = argparse.ArgumentParser(description='LedgerLang Compiler')
    ap.add_argument('source')
    ap.add_argument('--debug', action='store_true')
    ap.add_argument('--save',  action='store_true')
    args = ap.parse_args()

    if not os.path.exists(args.source):
        print(f'Error: file not found: {args.source}'); sys.exit(1)

    with open(args.source) as f:
        source = f.read()

    code, _ = compile_source(source, args.debug)
    if code:
        if args.save:
            out = args.source.replace('.ledger', '_generated.py')
            with open(out, 'w') as f: f.write(code)
            print(f'\n  Saved to: {out}')
        run_code(code)

if __name__ == '__main__':
    main()
