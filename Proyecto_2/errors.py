from typing import List
from collections import namedtuple
from lexer import Token

SyntaxErrorInfo = namedtuple("SyntaxErrorInfo", ["line", "col", "found_lexeme", "expected_list", "message"])

READABLE = {
    'COLON': ':',
    'COMMA': ',',
    'DOT': '.',
    'LPAR': '(',
    'RPAR': ')',
    'LBRACK': '[',
    'RBRACK': ']',
    'LBRACE': '{',
    'RBRACE': '}',
    'ASSIGN': '=',
    'NEWLINE': 'NEWLINE',
    'INDENT': 'INDENT',
    'DEDENT': 'DEDENT',
    'EOF': 'EOF',
    'ID': 'identifier',
    'INT': 'integer',
    'FLOAT': 'float',
    'STRING': 'string',
    'BINOP': 'operator',
}

def readable_of_terminal(term: str) -> str:
    if term in READABLE:
        return READABLE[term]
    if term.startswith('KEYWORD_'):
        return term.split('KEYWORD_', 1)[1]
    return term

def expected_list_to_strings(expected_terms: List[str]) -> List[str]:
    return [readable_of_terminal(t) for t in expected_terms]

def format_token_error(token: Token, expected_terms: List[str]) -> str:
    lex = token.lexeme.replace('"', '\\"')
    expected_readable = expected_list_to_strings(expected_terms)
    expected_fmt = ', '.join(f'"{e}"' for e in expected_readable)
    return f'<{token.line}, {token.col}> Error sintactico: se encontro: "{lex}"; se esperaba: {expected_fmt}.'

def format_indentation_error(token: Token) -> str:
    return f'<{token.line}, {token.col}>Error sintactico: falla de indentacion'

def build_expected_from_table(nonterminal: str, table: dict) -> List[str]:
    expected = sorted({ term for (A, term) in table.keys() if A == nonterminal })
    if not expected:
        expected = ['EOF']
    return expected

def to_syntax_error_info(token: Token, expected_terms: List[str], indent_error: bool = False) -> SyntaxErrorInfo:
    if indent_error:
        msg = format_indentation_error(token)
    else:
        msg = format_token_error(token, expected_terms)
    readable_expected = expected_list_to_strings(expected_terms)
    return SyntaxErrorInfo(token.line, token.col, token.lexeme, readable_expected, msg)