from collections import namedtuple
import string

Token = namedtuple("Token", ["type", "lexeme", "line", "col"])

class LexerError(Exception):
    pass

KEYWORDS = {
    "def", "if", "else", "elif", "while", "for",
    "return", "pass", "break", "continue", "in",
    "and", "or", "not", "True", "False", "None"
}

MULTI_CHAR_TOKENS = {
    "OP": ["**", "+", "-", "*", "/", "%"],
    "CMP": ["==", "!=", "<=", ">="],
    "ASSIGN": ["="],
    "SINGLE": [
        "!", "<", ">", ":", ",", ".", "(", ")", "[", "]", "{", "}"
    ]
}

SINGLE_CHAR_MAP = {
    ":": "COLON", ",": "COMMA", ".": "DOT", "(": "LPAR", ")": "RPAR",
    "[": "LBRACK", "]": "RBRACK", "{": "LBRACE", "}": "RBRACE",
    "<": "CMP", ">": "CMP", "!": "CMP",
    "+": "OP", "-": "OP", "*": "OP", "/": "OP", "%": "OP",
    "=": "ASSIGN"
}

ID_START_CHARS = string.ascii_letters + "_"
ID_CONTINUE_CHARS = string.ascii_letters + string.digits + "_"

def _match_identifier_or_keyword(text):
    if not text or text[0] not in ID_START_CHARS:
        return None, 0

    length = 1
    while length < len(text) and text[length] in ID_CONTINUE_CHARS:
        length += 1

    lexeme = text[:length]
    typ = "KEYWORD" if lexeme in KEYWORDS else "ID"
    return typ, lexeme

def _match_number(text):
    if not text or text[0] not in string.digits:
        return None, 0

    has_dot = False
    length = 0
    while length < len(text) and text[length] in string.digits:
        length += 1

    if length < len(text) and text[length] == '.':
        if length + 1 < len(text) and text[length + 1] in string.digits:
            has_dot = True
            length += 1
            while length < len(text) and text[length] in string.digits:
                length += 1
        elif length + 1 == len(text) or text[length+1] not in ID_CONTINUE_CHARS:
             pass
        else:
             pass

    if has_dot:
        return "FLOAT", text[:length]
    else:
        return "INT", text[:length]

def _match_string(text):
    if not text or text[0] not in ('\'', '\"'):
        return None, 0

    quote_char = text[0]
    length = 1
    escaped = False

    while length < len(text):
        char = text[length]
        if escaped:
            escaped = False
        elif char == '\\':
            escaped = True
        elif char == quote_char:
            return "STRING", text[:length + 1]
        
        length += 1

    return None, 0

def _match_symbol(text):
    if not text:
        return None, 0

    all_multi_tokens = sorted([
        ('**', 'OP'), ('==', 'CMP'), ('!=', 'CMP'), ('<=', 'CMP'), ('>=', 'CMP'), 
        ('+', 'OP'), ('-', 'OP'), ('*', 'OP'), ('/', 'OP'), ('%', 'OP'),
        ('=', 'ASSIGN'), ('<', 'CMP'), ('>', 'CMP'),
        (':', 'COLON'), (',', 'COMMA'), ('.', 'DOT'),
        ('(', 'LPAR'), (')', 'RPAR'), ('[', 'LBRACK'), (']', 'RBRACK'),
        ('{', 'LBRACE'), ('}', 'RBRACE')
    ], key=lambda x: len(x[0]), reverse=True)

    for lexeme_test, typ_test in all_multi_tokens:
        if text.startswith(lexeme_test):
            return typ_test, lexeme_test

    return None, 0


def _get_next_token(line_text, pos):
    start_pos = pos
    while start_pos < len(line_text) and line_text[start_pos] in ' \t':
        start_pos += 1

    if start_pos == len(line_text):
        return None, None, start_pos

    current_text = line_text[start_pos:]

    typ, lexeme = _match_string(current_text)
    if typ:
        return typ, lexeme, start_pos + len(lexeme)

    if current_text.startswith('#'):
        return "COMMENT", current_text, len(line_text)

    typ, lexeme = _match_identifier_or_keyword(current_text)
    if typ:
        return typ, lexeme, start_pos + len(lexeme)

    typ, lexeme = _match_number(current_text)
    if typ:
        return typ, lexeme, start_pos + len(lexeme)

    typ, lexeme = _match_symbol(current_text)
    if typ:
        return typ, lexeme, start_pos + len(lexeme)

    return "MISMATCH", current_text[0], start_pos + 1


def tokenize(source):
    source = source.replace('\r\n', '\n').replace('\r', '\n')
    tokens = []
    indent_stack = [0]
    lines = source.splitlines(True)
    line_no = 0

    for raw_line in lines:
        line_no += 1
        if raw_line.strip() == "":
            tokens.append(Token("NEWLINE", "\\n", line_no, 1))
            continue

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
        
        line_text_after_indent = raw_line[col - 1:]

        if line_text_after_indent.lstrip().startswith("#"):
            comment_end_col = len(raw_line.rstrip('\n')) + 1
            tokens.append(Token("NEWLINE", "\\n", line_no, comment_end_col))
            continue
        
        if leading > indent_stack[-1]:
            indent_stack.append(leading)
            tokens.append(Token("INDENT", "<INDENT>", line_no, 1))
        else:
            while leading < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(Token("DEDENT", "<DEDENT>", line_no, col))
            if leading != indent_stack[-1]:
                raise LexerError(f"Error de sangría en línea {line_no}. Nivel actual: {leading}, Esperado: {indent_stack[-1]}")
        
        pos = col - 1
        line_text = raw_line.rstrip("\n")

        while pos < len(line_text):
            typ, lexeme, next_pos = _get_next_token(line_text, pos)
            
            if pos < next_pos and all(c in ' \t' for c in line_text[pos:next_pos]):
                pos = next_pos
                continue

            if typ is None:
                break
            
            token_col = pos + 1

            if typ == "COMMENT":
                pos = len(line_text)
                continue
            elif typ == "MISMATCH":
                 raise LexerError(f"Carácter ilegal {lexeme!r} en línea {line_no} col {token_col}")
            else:
                tokens.append(Token(typ, lexeme, line_no, token_col))
            
            pos = next_pos

        tokens.append(Token("NEWLINE", "\\n", line_no, len(line_text) + 1))

    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "<DEDENT>", line_no + 1, 1))

    tokens.append(Token("EOF", "<EOF>", line_no + 1, 1))
    return tokens