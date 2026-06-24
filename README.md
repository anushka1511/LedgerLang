# LedgerLang Compiler

A compiler for **LedgerLang**, a Domain-Specific Language (DSL) designed for financial computations, portfolio analysis, and accounting-oriented workflows. The project demonstrates compiler design concepts including lexical analysis, parsing, AST construction, intermediate code generation, and target code generation.

## Language Features

| Feature | Syntax |
|---|---|
| Variable declaration | `ACCOUNT x = 100` / `RATE r = 0.05` / `VAR n = 10` |
| Computation | `COMPUTE net = savings * (1 - tax)` |
| Assignment | `x = x + 1` |
| Arrays (portfolios) | `PORTFOLIO prices = [100, 200, 150]` |
| Array access | `prices[0]` |
| If / Else | `IF x > 10 THEN ... ELSE ... END` |
| Loop | `REPEAT 12 TIMES ... END` |
| Output | `SHOW x` / `WARN "message"` / `REPORT "message"` |
| Comments | `# this is a comment` |
| Operators | `+  -  *  /  ==  !=  <  >  <=  >=  AND  OR  NOT` |

## Compiler Pipeline

```
Source (.ledger)
    │
    ▼
[Stage 1] Lexical Analyzer  →  Token stream
    │
    ▼
[Stage 2] Parser            →  Abstract Syntax Tree (AST)
    │
    ▼
[Stage 3] ICG               →  Three-Address Code (TAC)
    │
    ▼
[Stage 4] Code Generator    →  Executable Python code
```

## Requirements

- Python 3.10+
- No external dependencies required
## Usage

```bash
python compiler.py sample1.ledger          # compile and run
python compiler.py sample1.ledger --debug  # show all stage details
python compiler.py sample1.ledger --save   # save generated Python file
```

## Example Program

```
# Personal Finance Calculator
ACCOUNT savings = 5000
ACCOUNT loan    = 20000
RATE    tax     = 0.15
RATE    interest = 0.04

COMPUTE net = savings - (savings * tax)

IF loan > 10000 THEN
    WARN "High debt detected"
ELSE
    REPORT "Debt under control"
END

REPEAT 12 TIMES
    savings = savings + (savings * interest)
END

REPORT "Savings after 1 year:"
SHOW savings
```

## File Structure

```
ledgerlang/
├── compiler.py      # Main driver — runs the full pipeline
├── lexer.py         # Stage 1: Lexical Analyzer
├── parser.py        # Stage 2: Recursive Descent Parser
├── ast_nodes.py     # AST node definitions
├── icg.py           # Stage 3: Intermediate Code Generator (TAC)
├── codegen.py       # Stage 4: Python Code Generator
├── sample1.ledger   # Personal finance example
├── sample2.ledger   # Portfolio analysis example
└── sample3_errors.ledger  # Error handling demonstration
```

## Error Handling

- Errors are reported with line numbers
- The compiler continues analysis even after errors (error recovery)
- Code generation is skipped if any errors are present
- A listing file is always produced showing source lines interleaved with errors
