# lexer.py
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

class LexerError(Exception):
    pass

# Keywords and token types
KEYWORDS = {
    "def", "if", "else", "elif", "while", "for",
    "return", "pass", "break", "continue", "in",
    "and", "or", "not", "True", "False", "None"
}

# Single- and multi-character operators/delimiters (order matters for regex)
TOKEN_SPECIFICATION = [
    ("NEWLINE",      r"\n"),                         # line endings (handled specially)
    ("SKIP",         r"[ \t]+"),                     # spaces and tabs (handled for indentation)
    ("COMMENT",      r"\#.*"),                       # comment
    ("STRING",       r"('([^'\\]|\\.)*'|\"([^\"\\]|\\.)*\")"),  # simple string literals
    ("FLOAT",        r"\d+\.\d+"),                   # float number
    ("INT",          r"\d+"),                        # integer number
    ("OP",           r"\+|\-|\*|\/|\%|\*\*"),        # arithmetic operators
    ("CMP",          r"==|!=|<=|>=|<|>"),            # comparison
    ("ASSIGN",       r"="),                          # assignment
    ("COLON",        r":"),                          # :
    ("COMMA",        r","),                          # ,
    ("DOT",          r"\."),                         # .
    ("LPAR",         r"\("),                         # (
    ("RPAR",         r"\)"),                         # )
    ("LBRACK",       r"\["),                         # [
    ("RBRACK",       r"\]"),                         # ]
    ("LBRACE",       r"\{"),                         # {
    ("RBRACE",       r"\}"),                         # }
    ("ID",           r"[A-Za-z_][A-Za-z0-9_]*"),     # identifiers
    ("MISMATCH",     r"."),                          # any other character
]

MASTER_REGEX = re.compile("|".join("(?P<%s>%s)" % pair for pair in TOKEN_SPECIFICATION))

def tokenize(source):
    """
    Tokenize the given Python-like source string.

    Returns a list of Token(type, lexeme, line, col), including INDENT/DEDENT/NEWLINE/EOF tokens.

    Raises LexerError on illegal characters or mismatched indentation.
    """
    tokens = []
    indent_stack = [0]  # stack of indentation levels (counts of spaces)
    lines = source.splitlines(True)  # keep line endings
    line_no = 0

    for raw_line in lines:
        line_no += 1
        # If the line is only a newline, produce NEWLINE and continue
        if raw_line.strip() == "":
            # Even blank lines must produce a NEWLINE token but do not affect indentation
            tokens.append(Token("NEWLINE", "\\n", line_no, 1))
            continue

        # Compute indentation (count of spaces, tabs are treated as 4 spaces here)
        leading = 0
        col = 1
        for ch in raw_line:
            if ch == " ":
                leading += 1
                col += 1
            elif ch == "\t":
                leading += 4
                col += 1
            else:
                break

        # If the line after stripping leading whitespace starts with comment, treat as NEWLINE (no indent change)
        stripped_after_indent = raw_line.lstrip(" \t")
        if stripped_after_indent.startswith("#"):
            tokens.append(Token("NEWLINE", "\\n", line_no, col))
            continue

        # INDENT / DEDENT handling
        if leading > indent_stack[-1]:
            indent_stack.append(leading)
            tokens.append(Token("INDENT", "<INDENT>", line_no, 1))
        else:
            while leading < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(Token("DEDENT", "<DEDENT>", line_no, col))
            if leading != indent_stack[-1]:
                raise LexerError(f"Indentation error at line {line_no}")

        # Now tokenize the rest of the line
        pos = 0
        line_text = raw_line.rstrip("\n")
        while pos < len(line_text):
            match = MASTER_REGEX.match(line_text, pos)
            if not match:
                raise LexerError(f"Unexpected character at line {line_no} col {pos+1}")
            kind = match.lastgroup
            lexeme = match.group(kind)
            start = match.start()
            token_col = start + 1  # 1-based column within the line

            if kind == "NEWLINE":
                # Shouldn't match because we stripped newline; just break
                pos = match.end()
                break
            elif kind == "SKIP" or kind == "COMMENT":
                # advance position but do not emit token
                pos = match.end()
                continue
            elif kind == "ID":
                typ = "KEYWORD" if lexeme in KEYWORDS else "ID"
                tokens.append(Token(typ, lexeme, line_no, token_col))
            elif kind == "STRING":
                tokens.append(Token("STRING", lexeme, line_no, token_col))
            elif kind == "FLOAT":
                tokens.append(Token("FLOAT", lexeme, line_no, token_col))
            elif kind == "INT":
                tokens.append(Token("INT", lexeme, line_no, token_col))
            elif kind == "OP":
                tokens.append(Token("OP", lexeme, line_no, token_col))
            elif kind == "CMP":
                tokens.append(Token("CMP", lexeme, line_no, token_col))
            elif kind == "ASSIGN":
                tokens.append(Token("ASSIGN", lexeme, line_no, token_col))
            elif kind in {"COLON","COMMA","DOT","LPAR","RPAR","LBRACK","RBRACK","LBRACE","RBRACE"}:
                tokens.append(Token(kind, lexeme, line_no, token_col))
            elif kind == "MISMATCH":
                raise LexerError(f"Illegal character {lexeme!r} at line {line_no} col {token_col}")
            else:
                # fallback - should not happen
                tokens.append(Token(kind, lexeme, line_no, token_col))
            pos = match.end()

        # At the end of a logical line, emit NEWLINE
        tokens.append(Token("NEWLINE", "\\n", line_no, len(line_text) + 1))

    # After all lines, unwind remaining indents
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "<DEDENT>", line_no + 1, 1))

    # EOF token
    tokens.append(Token("EOF", "<EOF>", line_no + 1, 1))
    return tokens

# Quick manual test when executed as script (not exhaustive)
if __name__ == "__main__":
    src = """def foo(x):
    if x > 0:
        return x + 1
    else:
        return 0
"""
    try:
        toks = tokenize(src)
        for t in toks:
            print(t)
    except LexerError as e:
        print("LexerError:", e)
