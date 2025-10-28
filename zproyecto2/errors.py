# errors.py
from typing import List
from collections import namedtuple
from lexer import Token

# Estructura simple para devolver información de error si se prefiere manipularla
SyntaxErrorInfo = namedtuple("SyntaxErrorInfo", ["line", "col", "found_lexeme", "expected_list", "message"])

# Mapa legible para representar terminales de la gramática en mensajes de usuario
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
    """
    Devuelve una representación legible del símbolo de la gramática.
    Si es un KEYWORD_XXX devuelve 'xxx'.
    Si no se encuentra en el mapa, devuelve el mismo término.
    """
    if term in READABLE:
        return READABLE[term]
    if term.startswith('KEYWORD_'):
        return term.split('KEYWORD_', 1)[1]
    return term

def expected_list_to_strings(expected_terms: List[str]) -> List[str]:
    """
    Convierte una lista de términos gramaticales (por ejemplo 'KEYWORD_if', 'COMMA')
    a la lista de cadenas legibles que aparecerán dentro de las comillas dobles
    en el mensaje 'se esperaba: "t1", "t2", ...'.
    """
    return [readable_of_terminal(t) for t in expected_terms]

def format_token_error(token: Token, expected_terms: List[str]) -> str:
    """
    Formatea el error sintáctico cuando el parser recibe un token no esperado.
    Salida exacta:
    <linea, col> Error sintactico: se encontro: "<lexema>"; se esperaba: "t1", "t2", ...
    Donde t1,t2 son las representaciones legibles de los términos esperados.
    """
    lex = token.lexeme.replace('"', '\\"')
    expected_readable = expected_list_to_strings(expected_terms)
    expected_fmt = ', '.join(f'"{e}"' for e in expected_readable)
    return f'<{token.line}, {token.col}> Error sintactico: se encontro: "{lex}"; se esperaba: {expected_fmt}.'

def format_indentation_error(token: Token) -> str:
    """
    Formato concreto para errores de indentación:
    <linea, col>Error sintactico: falla de indentacion
    (observa que en el enunciado el ejemplo no tiene espacio después de la coma
    en algunos casos; aquí respetamos el formato solicitado.)
    """
    return f'<{token.line}, {token.col}>Error sintactico: falla de indentacion'

def build_expected_from_table(nonterminal: str, table: dict) -> List[str]:
    """
    Dado un no terminal y la tabla predictiva (keys: (A, terminal) -> production),
    devuelve la lista de terminales (no legibles) que el parser puede usar como
    'esperados'. La conversión a texto legible la hace format_token_error.
    """
    expected = sorted({ term for (A, term) in table.keys() if A == nonterminal })
    # Si no hay entradas, devolvemos EOF como expectativa por defecto
    if not expected:
        expected = ['EOF']
    return expected

def to_syntax_error_info(token: Token, expected_terms: List[str], indent_error: bool = False) -> SyntaxErrorInfo:
    """
    Construye un SyntaxErrorInfo con mensaje renderizado; útil si se quiere
    devolver la estructura además del string formateado.
    """
    if indent_error:
        msg = format_indentation_error(token)
    else:
        msg = format_token_error(token, expected_terms)
    readable_expected = expected_list_to_strings(expected_terms)
    return SyntaxErrorInfo(token.line, token.col, token.lexeme, readable_expected, msg)
