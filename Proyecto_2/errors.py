from typing import List
from collections import namedtuple
from lexer import Token

InformacionErrorSintactico = namedtuple("InformacionErrorSintactico", ["linea", "col", "lexema_encontrado", "lista_esperados", "mensaje"])

LEGIBLE = {
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
    'NEWLINE': 'NUEVALINEA',
    'INDENT': 'INDENTACION',
    'DEDENT': 'DEDENTACION',
    'EOF': 'EOF',
    'ID': 'identificador',
    'INT': 'entero',
    'FLOAT': 'flotante',
    'STRING': 'cadena',
    'BINOP': 'operador',
}

def legible_de_terminal(terminal: str) -> str:
    if terminal in LEGIBLE:
        return LEGIBLE[terminal]
    if terminal.startswith('KEYWORD_'):
        return terminal.split('KEYWORD_', 1)[1]
    return terminal

def lista_esperados_a_cadenas(terminales_esperados: List[str]) -> List[str]:
    return [legible_de_terminal(t) for t in terminales_esperados]

def formatear_error_token(token: Token, terminales_esperados: List[str]) -> str:
    lex = token.lexeme.replace('"', '\\"')
    esperados_legibles = lista_esperados_a_cadenas(terminales_esperados)
    esperados_fmt = ', '.join(f'"{e}"' for e in esperados_legibles)
    return f'<{token.line}, {token.col}> Error sintactico: se encontro: "{lex}"; se esperaba: {esperados_fmt}.'

def formatear_error_indentacion(token: Token) -> str:
    return f'<{token.line}, {token.col}>Error sintactico: falla de indentacion'

def construir_esperados_desde_tabla(no_terminal: str, tabla: dict) -> List[str]:
    esperados = sorted({ terminal for (A, terminal) in tabla.keys() if A == no_terminal })
    if not esperados:
        esperados = ['EOF']
    return esperados

def a_informacion_error_sintactico(token: Token, terminales_esperados: List[str], error_indentacion: bool = False) -> InformacionErrorSintactico:
    if error_indentacion:
        mensaje = formatear_error_indentacion(token)
    else:
        mensaje = formatear_error_token(token, terminales_esperados)
    esperados_legibles = lista_esperados_a_cadenas(terminales_esperados)
    return InformacionErrorSintactico(token.line, token.col, token.lexeme, esperados_legibles, mensaje)