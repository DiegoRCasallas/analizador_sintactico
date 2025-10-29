from collections import deque
import grammar as Gmod
import table as Tmod
from lexer import Token

EPS = 'ε'
MARCA_FIN = '$'

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

def token_a_terminal(token):
    tipo = token.tipo
    lex = token.lexema
    if tipo == 'KEYWORD':
        return f"KEYWORD_{lex}"
    if tipo == 'OP' or tipo == 'CMP':
        return 'BINOP'
    return tipo

def legible_de_terminal(terminal):
    if terminal in LEGIBLE:
        return LEGIBLE[terminal]
    if terminal.startswith('KEYWORD_'):
        return terminal.split('KEYWORD_', 1)[1]
    return terminal

def formatear_error_token(token, lista_esperados):
    if lista_esperados == ['INDENTATION_ERROR']:
        return f"<{token.linea}, {token.col}>Error sintactico: falla de indentacion"
    lex = token.lexema.replace('"', '\\"')
    esperados_fmt = ', '.join(f'"{e}"' for e in lista_esperados)
    return f'<{token.linea}, {token.col}> Error sintactico: se encontro: "{lex}"; se esperaba: {esperados_fmt}.'

def recopilar_esperados_para_no_terminal(no_terminal, tabla):
    terminales_esperados = Tmod.terminales_esperados_para_no_terminal(no_terminal, tabla)
    legibles = [legible_de_terminal(t) for t in terminales_esperados]
    return legibles if legibles else [legible_de_terminal('EOF')]

def analizar(tokens, tabla, gramatica, simbolo_inicial, depuracion=False):
    from collections import deque

    pila = deque()
    pila.append('EOF')
    pila.append(simbolo_inicial)

    cursor = 0
    n = len(tokens)
    if n == 0:
        return False, '<0, 0> Error sintactico: se encontro: ""; se esperaba: "EOF".'

    if tokens[-1].tipo != 'EOF':
        tokens = tokens + [Token('EOF', '<EOF>', tokens[-1].linea, tokens[-1].col + 1)]
        n += 1

    producciones_aplicadas = []

    while pila:
        tope = pila.pop()
        actual = tokens[cursor]
        terminal_actual = token_a_terminal(actual)

        if depuracion:
            print(f"[DEPURACION] pila_tope={tope}  actual=({cursor}){actual.tipo}:{actual.lexema}  terminal_actual={terminal_actual}")

        if tope == EPS:
            continue

        if tope not in gramatica:
            if tope == terminal_actual:
                cursor += 1
                if tope == 'EOF':
                    return True, "El analisis sintactico ha finalizado exitosamente.", producciones_aplicadas
                continue
            else:
                esperados = [legible_de_terminal(tope)]
                mensaje = formatear_error_token(actual, esperados)
                return False, mensaje, []
        else:
            clave = (tope, terminal_actual)
            prod = tabla.get(clave)
            if prod is None:
                esperados = Tmod.terminales_esperados_para_no_terminal(tope, tabla)
                esperados_legibles = [legible_de_terminal(t) for t in esperados] or [legible_de_terminal('EOF')]
                mensaje = formatear_error_token(actual, esperados_legibles)
                return False, mensaje, []
            producciones_aplicadas.append((tope, prod))
            for simb in reversed(prod):
                if simb != EPS:
                    pila.append(simb)

        if cursor >= n:
            ultimo = tokens[-1]
            return False, formatear_error_token(ultimo, [legible_de_terminal('EOF')]), []

    if cursor < n and tokens[cursor].tipo == 'EOF':
        return True, "El analisis sintactico ha finalizado exitosamente.", producciones_aplicadas
    if cursor >= n:
        return True, "El analisis sintactico ha finalizado exitosamente.", producciones_aplicadas

    actual = tokens[cursor]
    return False, formatear_error_token(actual, [legible_de_terminal('EOF')]), []



if __name__ == "__main__":
    from lexer import tokenizar, ErrorLexer
    import table as T
    import grammar as G

    fuente = """def foo(x):
    if x > 0:
        return x + 1
    else:
        return 0
"""
    try:
        toks = tokenizar(fuente)
    except ErrorLexer as e:
        print("ErrorLexer:", e)
        raise

    try:
        tabla_pred, FIRST, FOLLOW, SELECT = T.construir_tabla_predictiva(G.gramatica, G.SIMBOLO_INICIAL)
    except Exception as e:
        print("Error al construir tabla predictiva:", e)
        raise

    ok, mensaje = analizar(toks, tabla_pred, G.normalizar_gramatica_para_ll1(G.gramatica), G.SIMBOLO_INICIAL)
    print(mensaje)